<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Klynging av to Ryzen™ AI Halo-er med RCCL

## Oversikt

Din Ryzen™ AI Halo er allerede i stand til å kjøre store språkmodeller lokalt. Klynging tar dette videre ved å kombinere GPU-minnet fra flere systemer over et lokalt nettverk, noe som gir deg tilgang til enda større modeller med sterkere resonnering, bedre kodegenerering og dypere flerspråklig forståelse – alt helt på din egen maskinvare.

Denne playbooken lærer deg hvordan du klynger to Ryzen AI Halo-systemer ved hjelp av RCCL (ROCm Communication Collectives Library) med vLLM og kjører Qwen3.5-397B, en modell med 397 milliarder parametere, på tvers av begge maskinene med ROCm-akselerasjon.

## Hva du vil lære

- Hvordan du utvider VRAM-allokeringen på Ryzen AI Halo-systemer
- Starte vLLM med ROCm-støtte
- Konfigurere RCCL for flernode tensor-parallell inferens på tvers av to Ryzen AI Halo-systemer
- Kjøre en modell med 397 milliarder parametere på tvers av to nettverkstilkoblede Ryzen AI Halo-systemer

## Forutsetninger

### Maskinvare

Denne playbooken krever to Ryzen AI Halo-enheter og én Ethernet-svitsj, koblet i en stjernetopologi der hver enhet er kablet direkte til svitsjen.

| Komponent | Antall | Beskrivelse |
|-----------|--------|-------------|
| Ryzen AI Halo | 2 | Beregningsnoder som utgjør klyngen |
| 10Gbps Ethernet-svitsj | 1 | Sentral svitsj for å muliggjøre kommunikasjon mellom Ryzen AI Halo-nodene (minst 2 porter) |
| Ethernet-kabel | 2 | Kobler hver Halo-enhet til svitsjen (Cat 7 eller høyere anbefales) |

> **Merk**: To Ethernet-svitsjeporter kreves for å koble de to Ryzen AI Halo-enhetene. En tredje port kreves hvis du får tilgang til modellen fra en separat klientmaskin i stedet for fra en av Halo-enhetene.

### Programvare
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fysisk maskinvareoppsett

> **Merk**: Fullfør dette trinnet på både Maskin 1 og Maskin 2.

Koble hver Ryzen AI Halo-enhet til Ethernet-svitsjen med en Cat 7-kabel (eller høyere). Dette etablerer 10Gbps-forbindelsen som brukes til høyhastighets kommunikasjon mellom nodene.

### 1. Finn nettverksgrensesnitt

På hver maskin finner du navnet på nettverksgrensesnittet og noterer det ned (det vil bli referert til i resten av instruksjonene som `IFNAME`). Kjør:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Dette skriver ut grensesnittnavnet direkte, for eksempel:

```bash
enp191s0
```

### 2. Verifiser nettverkslinkshastigheter

Bekreft at linken er aktiv og kjører med full hastighet ved å sjekke hastigheten på grensesnittet ditt:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Merk**: Erstatt `<IFNAME>` med grensesnittnavnet fra [1. Finn nettverksgrensesnitt](#1-determine-network-interfaces)

Du bør se en hastighet på `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Merk**: Hvis hastigheten er lavere enn `10000Mb/s` eller linken ikke kommer opp, sjekk kabelkoblingen og bekreft at svitsjeporten er satt til 10Gbps. Noen svitsjer krever at auto-forhandling deaktiveres og at linkshastigheten settes manuelt; se svitsjens dokumentasjon.

## Utvidelse av VRAM-allokering

> **Merk**: Fullfør dette trinnet på både Maskin 1 og Maskin 2.

### Minnekonfigurasjon for kjøring av store modeller

På Linux bruker ROCm en delt systemminnepulje, og denne puljen er som standard konfigurert til halvparten av systemminnet.

Dette beløpet kan økes ved å endre kjernens Translation Table Manager (TTM) sideinnstilling, med følgende instruksjoner. AMD anbefaler å sette minimum dedikert VRAM i BIOS (0,5 GB).

* Installer pipx-verktøyet og legg til stien for pipx-installerte wheels i systemets søkesti.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installer amd-debug-tools-wheelen fra PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Kjør amd-ttm-verktøyet for å spørre om gjeldende innstillinger for delt minne.
  ```bash
  amd-ttm
  ```

* Rekonfigurer innstillinger for delt minne til **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Start systemet på nytt for at endringene skal tre i kraft.

## Initialisering av vLLM-container

> **Merk**: Fullfør dette trinnet på både Maskin 1 og Maskin 2.

Din Ryzen AI Halo leveres med vLLM pakket inne i et forhåndsbygd containerimage, som du kjører ved hjelp av Podman, et gratis og åpen kildekode-containerverktøy.

### 1. Opprett katalogen for modellnedlasting

Når du serverer Qwen3.5-397B-modellen i denne playbooken, vil vLLM automatisk laste ned modellvektene til systemet ditt. For å sikre at disse vektene er tilgjengelige fra innsiden av containeren, oppretter du først en models-katalog som containeren kan montere:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Start vLLM-containeren

Kommandoen nedenfor starter containeren og slipper deg inn i et interaktivt skall. Den monterer models-katalogen du nettopp opprettet og sender din `IFNAME` til `NCCL_SOCKET_IFNAME` og `GLOO_SOCKET_IFNAME`, og forteller RCCL (biblioteket vLLM bruker til å koordinere GPU-er på tvers av klyngen) hvilket grensesnitt som skal brukes.

Start containeren med:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Merk**: Erstatt `<IFNAME>` med grensesnittnavnet fra [1. Finn nettverksgrensesnitt](#1-determine-network-interfaces)

## Kjøring av modellen på klyngen

vLLM bruker Ray til å orkestrere klyngen og RCCL til å håndtere GPU-til-GPU-kommunikasjon på tvers av noder. Én maskin fungerer som **hodenode** (Maskin 1) og koordinerer inferens. Den andre kobler seg til som en **arbeidernode** (Maskin 2) og bidrar med sitt GPU-minne og sin beregningskraft.

> **Merk**: Ray er en valgfri avhengighet for vLLM og er kun tilgjengelig fra innsiden av den forhåndskonfigurerte Podman-containeren.

Ved oppstart deler vLLM modellen på tvers av begge nodene ved hjelp av tensor-parallellisme. Når den er lastet, foregår inferens som om den kjøres på én enkelt akselerator.

### Trinn 1: Start Ray-hodenoden (Maskin 1)

På Maskin 1 starter du Ray-hodenoden for å initialisere klyngen:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Finne `<MACHINE_1_IP>`**: På Maskin 1 kjører du `hostname -I | awk '{print $1}'` for å finne den lokale IP-adressen.

### Trinn 2: Koble til klyngen (Maskin 2)

På Maskin 2 kobler du til hodenoden for å danne klyngen:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Finne `<MACHINE_2_IP>`**: På Maskin 2 kjører du `hostname -I | awk '{print $1}'` for å finne den lokale IP-adressen.

### Trinn 3: Server modellen (Maskin 1)

På Maskin 1 starter du vLLM-serveren. Dette vil automatisk laste ned modellen og begynne å serve den på tvers av begge nodene:

```bash
vllm serve Qwen/Qwen3.5-397B-A17B-GPTQ-Int4 \
  --port 7000 \
  --host 0.0.0.0 \
  --max-model-len 32768 \
  --gpu-memory-utilization 0.9 \
  --dtype float16 \
  --tensor-parallel-size 2 \
  --distributed-executor-backend ray \
  --enforce-eager \
  --language-model-only \
  --reasoning-parser qwen3
```

#### Parameterreferanse

| Flagg | Formål |
|-------|--------|
| `--port` | Port å serve HTTP API-et på |
| `--host` | IP-adresse å binde serveren til (`0.0.0.0` for alle grensesnitt) |
| `--max-model-len` | Maksimal kontekstlengde i tokens |
| `--gpu-memory-utilization` | Andel av GPU-minnet som skal allokeres (0,0–1,0) |
| `--dtype` | Datatype for modellvekter |
| `--tensor-parallel-size` | Antall GPU-er å dele modellen på (sett til totalt antall GPU-er i klyngen) |
| `--distributed-executor-backend` | Backend for flernode-kjøring (`ray` for klyngedistribusjoner) |
| `--enforce-eager` | Deaktiverer CUDA-grafkompilering for kompatibilitet |
| `--language-model-only` | Hopper over lasting av hjelpemodellkomponenter (f.eks. visuell enkoder) |
| `--reasoning-parser` | Aktiverer strukturert resonnerings-utdataparsing for modellen |

For full parameterbruk, se [vLLM-dokumentasjonen](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Tilgang til modellen

vLLM eksponerer et OpenAI-kompatibelt API, slik at du kan koble til en hvilken som helst kompatibel klient eller grensesnitt til klyngen din. Ett populært alternativ er [Open WebUI](https://github.com/open-webui/open-webui), som gir et nettleserbasert chat-grensesnitt.

For å koble Open WebUI til ditt vLLM-endepunkt:

1. Åpne **Innstillinger** > **Administrasjonspanel** > **Tilkoblinger**
2. Klikk på **+** ved **Administrer OpenAI API-tilkoblinger**
3. Sett **Tilkoblingstype** til **Ekstern**
4. Sett **URL** til `http://<MACHINE_1_IP>:7000/v1`
5. Under **Auth**, velg **Ingen** fra nedtrekksmenyen
6. La **Modell-ID-er** stå tomt for å automatisk oppdage alle modeller fra endepunktet

> **Finne `<MACHINE_1_IP>`**: På Maskin 1 kjører du `hostname -I | awk '{print $1}'` for å finne den lokale IP-adressen. Hvis du får tilgang til Open WebUI fra Maskin 1 selv, kan du bruke `http://localhost:7000/v1`.

![Open WebUI-tilkoblingsinnstillinger for vLLM-endepunktet](assets/openwebui-connection.png)

Når du er tilkoblet, velger du modellen fra modell-nedtrekksmenyen i Open WebUI og begynner å chatte. Modellen kjører nå på tvers av begge dine Ryzen AI Halo-noder:

![Chatter med Qwen3.5-397B i Open WebUI](assets/openwebui-chat.png)

## Neste steg

- **Utforsk andre modeller**: Oppdag nye modeller på [Hugging Face](https://huggingface.co/models?&sort=trending) som passer innenfor klyngens kombinerte GPU-minne
- **Skaler til fire noder**: Legg til to flere Ryzen AI Halo-systemer som ekstra Ray-arbeidere for å dele modeller på tvers av enda flere GPU-er. Dette krever en Ethernet-svitsj med minst fire porter, én for hver node. Følg [Trinn 2: Koble til klyngen](#step-2-join-the-cluster-machine-2) på hver ekstra arbeider og øk `--tensor-parallel-size` tilsvarende
- **Prøv andre parallellismestrategier**: vLLM støtter [ekspert-parallell](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) for mixture-of-experts-modeller og [data-parallell](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) for høyere gjennomstrømning. Eksperimenter med `--enable-expert-parallel` og `--data-parallel-size` for å finne den beste konfigurasjonen for din arbeidsbelastning