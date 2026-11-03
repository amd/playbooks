<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversettelse.** Denne siden ble automatisk oversatt fra engelsk og har ikke blitt gjennomgått av et menneske. Den kan inneholde feil, og enkelte instruksjoner, kommandoer, nedlastinger, produkttilgjengelighet eller annet innhold kan variere etter språk eller region. Ved eventuelle uoverensstemmelser eller avvik er den opprinnelige engelske versjonen av playbook-en gjeldende.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Klynging av to Ryzen™ AI Halo med RCCL

## Oversikt

Din Ryzen™ AI Halo er allerede i stand til å kjøre store språkmodeller lokalt. Klynging tar dette et steg videre ved å kombinere GPU-minnet til flere systemer over et lokalt nettverk, noe som gir deg tilgang til enda større modeller med sterkere resonnering, bedre kodegenerering og dypere flerspråklig forståelse, helt og holdent på din egen maskinvare.

Denne veiledningen lærer deg hvordan du klynger to Ryzen AI Halo-systemer ved hjelp av RCCL (ROCm Communication Collectives Library) med vLLM og kjører Qwen3.5-397B, en modell med 397 milliarder parametere, på tvers av begge maskinene med ROCm-akselerasjon.

## Hva du vil lære

- Hvordan utvide VRAM-tildelingen på Ryzen AI Halo-systemer
- Å starte vLLM med ROCm-støtte
- Konfigurering av RCCL for multi-node tensor-parallell inferens på tvers av to Ryzen AI Halo-systemer
- Kjøring av en modell med 397 milliarder parametere på tvers av to nettverkstilkoblede Ryzen AI Halo-systemer

## Forutsetninger

### Maskinvare

Denne veiledningen krever to Ryzen AI Halo-enheter og én Ethernet-svitsj, koblet sammen i en stjernetopologi der hver enhet er kablet direkte til svitsjen.

| Komponent | Antall | Beskrivelse |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Beregningsnoder som utgjør klyngen |
| 10Gbps Ethernet-svitsj | 1 | Sentral svitsj som muliggjør kommunikasjon mellom flere Ryzen AI Halo-noder (minst 2 porter) |
| Ethernet-kabel | 2 | Kobler hver Halo-enhet til svitsjen (Cat 7 eller høyere anbefales) |

> **Merk**: To Ethernet-svitsjporter kreves for å koble sammen de to Ryzen AI Halo-enhetene. En tredje port kreves dersom du får tilgang til modellen fra en separat klientmaskin i stedet for fra en av Halo-enhetene.

### Programvare
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fysisk oppsett av maskinvare

> **Merk**: Fullfør dette trinnet på både Maskin 1 og Maskin 2.

Koble hver Ryzen AI Halo-enhet til Ethernet-svitsjen med en Cat 7-kabel (eller høyere). Dette etablerer 10Gbps-forbindelsen som brukes for høyhastighetskommunikasjon mellom nodene.

### 1. Finn nettverksgrensesnitt

På hver maskin finner du navnet på nettverksgrensesnittet og noterer det ned (det vil bli referert til i resten av instruksjonene som `IFNAME`). Kjør:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Dette skriver ut grensesnittnavnet direkte, for eksempel:

```bash
enp191s0
```

### 2. Kontroller nettverkets linkhastigheter

Bekreft at linken er aktiv og kjører på full hastighet ved å kontrollere hastigheten på grensesnittet:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Merk**: Erstatt `<IFNAME>` med grensesnittnavnet fra utdataene i [1. Finn nettverksgrensesnitt](#1-finn-nettverksgrensesnitt)

Du bør se en hastighet på `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Merk**: Hvis hastigheten er lavere enn `10000Mb/s`, eller hvis linken ikke kommer opp, kontroller kabeltilkoblingen og bekreft at svitsjporten er satt til 10Gbps. Enkelte svitsjer krever at auto-forhandling deaktiveres og at linkhastigheten settes manuelt; se dokumentasjonen for svitsjen din.

## Utvide VRAM-tildeling

> **Merk**: Fullfør dette trinnet på både Maskin 1 og Maskin 2.

### Minnekonfigurasjon for kjøring av store modeller

På Linux bruker ROCm en delt systemminnepool, og denne poolen er som standard konfigurert til halvparten av systemminnet.

Denne mengden kan økes ved å endre kjernens Translation Table Manager (TTM)-sideinnstilling, med følgende instruksjoner. AMD anbefaler at du setter det minste dedikerte VRAM-et i BIOS (0,5 GB).

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

* Rekonfigurer innstillingene for delt minne til **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Start systemet på nytt for at endringene skal tre i kraft.

## Initialisering av vLLM-container

> **Merk**: Fullfør dette trinnet på både Maskin 1 og Maskin 2.

Din Ryzen AI Halo leveres med vLLM pakket inne i et forhåndsbygget containerbilde, som du kjører med Podman, et gratis og åpen kildekode containerverktøy.

### 1. Opprett katalogen for modellnedlasting

Når du kjører Qwen3.5-397B-modellen i denne veiledningen, vil vLLM automatisk laste ned modellvektene til systemet ditt. For å sikre at disse vektene er tilgjengelige fra inne i containeren, oppretter du først en models-katalog som containeren kan montere:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Start vLLM-containeren

Kommandoen nedenfor starter containeren og gir deg et interaktivt skall. Den monterer models-katalogen du nettopp opprettet, og sender `IFNAME` til `NCCL_SOCKET_IFNAME` og `GLOO_SOCKET_IFNAME`, som forteller RCCL (biblioteket vLLM bruker for å koordinere GPU-er på tvers av klyngen) hvilket grensesnitt som skal brukes.

Start containeren med:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Merk**: Erstatt `<IFNAME>` med grensesnittnavnet fra utdataene i [1. Finn nettverksgrensesnitt](#1-finn-nettverksgrensesnitt)

## Kjøre modellen på klyngen

vLLM bruker Ray til å orkestrere klyngen og RCCL til å håndtere GPU-til-GPU-kommunikasjon på tvers av noder. Én maskin fungerer som **hodenode** (Maskin 1), som koordinerer inferens. Den andre blir med som en **arbeidernode** (Maskin 2), og bidrar med sitt GPU-minne og beregningskraft.

> **Merk**: Ray er en valgfri avhengighet for vLLM og er kun tilgjengelig fra innsiden av den forhåndskonfigurerte Podman-containeren.

Ved oppstart deler vLLM modellen på tvers av begge nodene ved hjelp av tensor-parallellisme. Når den er lastet inn, foregår inferens som om den kjører på én enkelt akselerator.

#### Forhindre Ray OOM-feil

Som standard overvåker Ray vertsminnet på hver node og avslutter den største prosessen når minnebruken overstiger 95 %. På din Ryzen™ AI Halo deler GPU-en og verten én felles minnepool, så innlasting av en modell kan utløse en `ray.exceptions.OutOfMemoryError` og drepe arbeiderprosessen.

For å forhindre dette vil vi eksportere `RAY_memory_monitor_refresh_ms=0` på hver maskin før vi starter og blir med i klyngen.
### Trinn 1: Start Ray-hovednoden (Maskin 1)

På Maskin 1 starter du Ray-hovednoden for å initialisere klyngen:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Finne `<MACHINE_1_IP>`**: På Maskin 1 kjører du `hostname -I | awk '{print $1}'` for å finne den lokale IP-adressen.

### Trinn 2: Bli med i klyngen (Maskin 2)

På Maskin 2 kobler du til hovednoden for å danne klyngen:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Finne `<MACHINE_2_IP>`**: På Maskin 2 kjører du `hostname -I | awk '{print $1}'` for å finne den lokale IP-adressen.

### Trinn 3: Server modellen (Maskin 1)

På Maskin 1 starter du vLLM-serveren. Dette vil automatisk laste ned modellen og begynne å servere den på tvers av begge nodene:

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
|------|---------|
| `--port` | Port for å servere HTTP-API-et på |
| `--host` | IP-adresse å binde serveren til (`0.0.0.0` for alle grensesnitt) |
| `--max-model-len` | Maksimal kontekstlengde i tokens |
| `--gpu-memory-utilization` | Andel av GPU-minne som skal tildeles (0.0–1.0) |
| `--dtype` | Datatype for modellvekter |
| `--tensor-parallel-size` | Antall GPU-er modellen skal deles på tvers av (sett til totalt antall GPU-er i klyngen) |
| `--distributed-executor-backend` | Backend for utførelse på flere noder (`ray` for klyngedistribusjoner) |
| `--enforce-eager` | Deaktiverer CUDA-graf-kompilering for kompatibilitet |
| `--language-model-only` | Hopper over lasting av hjelpekomponenter for modellen (f.eks. synsenkoder) |
| `--reasoning-parser` | Aktiverer strukturert tolkning av resonneringsutdata for modellen |

For fullstendig bruk av parametere, se [vLLM-dokumentasjonen](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Få tilgang til modellen

vLLM eksponerer et OpenAI-kompatibelt API, så du kan koble hvilken som helst kompatibel klient eller grensesnitt til klyngen din. Ett populært alternativ er [Open WebUI](https://github.com/open-webui/open-webui), som gir et nettleserbasert chattegrensesnitt.

Slik kobler du Open WebUI til vLLM-endepunktet ditt:

1. Åpne **Settings** > **Admin Panel** > **Connections**
2. Klikk på **+** ved **Manage OpenAI API Connections**
3. Sett **Connection Type** til **External**
4. Sett **URL** til `http://<MACHINE_1_IP>:7000/v1`
5. Under **Auth** velger du **None** fra nedtrekksmenyen
6. La **Model IDs** stå tomt for automatisk å oppdage alle modeller fra endepunktet

> **Finne `<MACHINE_1_IP>`**: På Maskin 1 kjører du `hostname -I | awk '{print $1}'` for å finne den lokale IP-adressen. Hvis du får tilgang til Open WebUI fra Maskin 1 selv, kan du bruke `http://localhost:7000/v1`.

![Tilkoblingsinnstillinger for Open WebUI mot vLLM-endepunktet](assets/openwebui-connection.png)

Når tilkoblingen er opprettet, velger du modellen fra modell-nedtrekksmenyen i Open WebUI og begynner å chatte. Modellen kjører nå på tvers av begge dine Ryzen AI Halo-noder:

![Chatting med Qwen3.5-397B i Open WebUI](assets/openwebui-chat.png)

## Neste steg

- **Utforsk andre modeller**: Oppdag nye modeller på [Hugging Face](https://huggingface.co/models?&sort=trending) som passer innenfor klyngens samlede GPU-minne
- **Skaler til fire noder**: Legg til to flere Ryzen AI Halo-systemer som ekstra Ray-arbeidsnoder for å dele modeller på tvers av enda flere GPU-er. Dette krever en Ethernet-svitsj med minst fire porter, én for hver node. Følg [Trinn 2: Bli med i klyngen](#step-2-join-the-cluster-machine-2) på hver ekstra arbeidsnode og øk `--tensor-parallel-size` deretter
- **Prøv andre parallelliseringsstrategier**: vLLM støtter [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) for mixture-of-experts-modeller og [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) for høyere gjennomstrømning. Eksperimenter med `--enable-expert-parallel` og `--data-parallel-size` for å finne den beste konfigurasjonen for arbeidsmengden din