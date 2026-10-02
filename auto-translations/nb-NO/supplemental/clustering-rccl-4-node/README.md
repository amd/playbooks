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

# Klyngedannelse av fire Ryzen™ AI Halo med RCCL

## Oversikt

Din Ryzen™ AI Halo er allerede i stand til å kjøre store språkmodeller lokalt. Klyngedannelse tar dette videre ved å kombinere GPU-minnet til flere systemer over et lokalt nettverk, noe som gir deg tilgang til enda større modeller med sterkere resonnering, bedre kodegenerering, og dypere flerspråklig forståelse, alt sammen på din egen maskinvare.

Denne oppskriftsboken lærer deg hvordan du klyngedanner fire Ryzen AI Halo-systemer ved hjelp av RCCL (ROCm Communication Collectives Library) med vLLM og kjører Qwen3.5-397B, en modell med 397 milliarder parametere, på tvers av alle fire maskinene med ROCm-akselerasjon.

## Hva du vil lære

- Hvordan utvide VRAM-tildelingen på Ryzen AI Halo-systemer
- Oppstart av vLLM med ROCm-støtte
- Konfigurering av RCCL for flernode tensor-parallell inferens på tvers av fire Ryzen AI Halo-systemer
- Kjøring av en modell med 397 milliarder parametere på tvers av fire nettverkstilkoblede Ryzen AI Halo-systemer

## Forutsetninger

### Maskinvare

Denne oppskriftsboken krever fire Ryzen AI Halo-enheter og én Ethernet-svitsj, koblet sammen i en stjernetopologi der hver enhet er koblet direkte til svitsjen.

| Komponent | Antall | Beskrivelse |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Beregningsnoder som danner klyngen |
| 10 Gbps Ethernet-svitsj | 1 | Sentral svitsj som muliggjør kommunikasjon mellom flere Ryzen AI Halo-noder (minst 4 porter) |
| Ethernet-kabel | 4 | Kobler hver Halo-enhet til svitsjen (Cat 7 eller høyere anbefales) |

> **Merk**: Fire Ethernet-svitsjporter er nødvendig for å koble til de fire Ryzen AI Halo-enhetene. En femte port er nødvendig hvis du får tilgang til modellen fra en separat klientmaskin i stedet for fra en av Halo-enhetene.

### Programvare
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fysisk maskinvareoppsett

> **Merk**: Fullfør dette trinnet på alle fire maskinene (Maskin 1 til og med Maskin 4).

Koble hver Ryzen AI Halo-enhet til Ethernet-svitsjen ved hjelp av en Cat 7-kabel (eller høyere). Dette etablerer 10 Gbps-forbindelsen som brukes for høyhastighetskommunikasjon mellom nodene.

### 1. Bestem nettverksgrensesnitt

På hver maskin finner du navnet på nettverksgrensesnittet og noterer det ned (det vil bli referert til i resten av instruksjonene som `IFNAME`). Kjør:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Dette skriver ut grensesnittnavnet direkte, for eksempel:

```bash
enp191s0
```

### 2. Bekreft nettverkslinjehastigheter

Bekreft at forbindelsen er aktiv og kjører med full hastighet ved å sjekke hastigheten på grensesnittet ditt:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Merk**: Erstatt `<IFNAME>` med utgangsgrensesnittnavnet fra [1. Bestem nettverksgrensesnitt](#1-bestem-nettverksgrensesnitt)

Du bør se en hastighet på `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Merk**: Hvis hastigheten er lavere enn `10000Mb/s` eller forbindelsen ikke kommer opp, sjekk kabeltilkoblingen og bekreft at svitsjporten er satt til 10 Gbps. Enkelte svitsjer krever at auto-forhandling deaktiveres og at linjehastigheten settes manuelt; se dokumentasjonen for svitsjen din.

## Utvidelse av VRAM-tildeling

> **Merk**: Fullfør dette trinnet på alle fire maskinene (Maskin 1 til og med Maskin 4).

### Minnekonfigurasjon for kjøring av store modeller

På Linux bruker ROCm en delt systemminnepool, og denne poolen er som standard konfigurert til halvparten av systemminnet.

Denne mengden kan økes ved å endre kjernens Translation Table Manager (TTM)-sideinnstilling, med følgende instruksjoner. AMD anbefaler å angi minimum dedikert VRAM i BIOS (0,5 GB).

* Installer pipx-verktøyet og legg til stien for pipx-installerte wheels i systemets søkesti.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installer amd-debug-tools-wheelen fra PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Kjør amd-ttm-verktøyet for å spørre om de gjeldende innstillingene for delt minne.
  ```bash
  amd-ttm
  ```

* Omkonfigurer innstillingene for delt minne til **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Start systemet på nytt for at endringene skal tre i kraft.

## Initialisering av vLLM-containeren

> **Merk**: Fullfør dette trinnet på alle fire maskinene (Maskin 1 til og med Maskin 4).

Din Ryzen AI Halo leveres med vLLM pakket inne i et ferdigbygget containerbilde, som du kjører ved hjelp av Podman, et gratis og åpen kildekode-containerverktøy.

### 1. Opprett nedlastingsmappen for modellen

Når du betjener Qwen3.5-397B-modellen i denne oppskriftsboken, vil vLLM automatisk laste ned modellvektene til systemet ditt. For å sikre at disse vektene er tilgjengelige fra inne i containeren, oppretter du først en models-mappe som containeren kan montere:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Start vLLM-containeren

Kommandoen nedenfor starter containeren og tar deg inn i et interaktivt skall. Den monterer models-mappen du nettopp opprettet, og sender din `IFNAME` til `NCCL_SOCKET_IFNAME` og `GLOO_SOCKET_IFNAME`, som forteller RCCL (biblioteket vLLM bruker til å koordinere GPU-er på tvers av klyngen) hvilket grensesnitt som skal brukes.

Start containeren med:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Merk**: Erstatt `<IFNAME>` med utgangsgrensesnittnavnet fra [1. Bestem nettverksgrensesnitt](#1-bestem-nettverksgrensesnitt)

## Kjøre modellen på klyngen

vLLM bruker Ray til å orkestrere klyngen og RCCL til å håndtere GPU-til-GPU-kommunikasjon på tvers av noder. Én maskin fungerer som hodenode (Maskin 1), som koordinerer inferens. De tre andre deltar som arbeidernoder (Maskin 2, 3 og 4), og bidrar med sitt GPU-minne og sin beregningskraft.

> **Merk**: Ray er en valgfri avhengighet for vLLM og er kun tilgjengelig fra innsiden av den forhåndskonfigurerte Podman-containeren.

Ved oppstart deler vLLM modellen på tvers av alle fire nodene ved hjelp av tensor-parallellisme. Når den er lastet, foregår inferens som om den kjører på én enkelt akselerator.

#### Forhindre Ray OOM-feil

Som standard overvåker Ray vertsminnet på hver node og avslutter den største prosessen når minnebruken overstiger 95 %. På din Ryzen™ AI Halo deler GPU-en og verten én minnepool, så lasting av en modell kan utløse en `ray.exceptions.OutOfMemoryError` og avslutte arbeiderprosessen.

For å forhindre dette, vil vi eksportere `RAY_memory_monitor_refresh_ms=0` på hver maskin før vi starter og slutter oss til klyngen.
### Trinn 1: Start Ray-hovednoden (maskin 1)

På maskin 1 starter du Ray-hovednoden for å initialisere klyngen:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Finne `<MACHINE_1_IP>`**: Kjør `hostname -I | awk '{print $1}'` på maskin 1 for å finne den lokale IP-adressen.

### Trinn 2: Bli med i klyngen (maskin 2, 3 og 4)

På hver av maskin 2, 3 og 4 kobler du til hovednoden for å danne klyngen:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_N_IP> --num-gpus=1
```

> **Finne `<MACHINE_N_IP>`**: Kjør `hostname -I | awk '{print $1}'` på hver arbeidermaskin for å finne den lokale IP-adressen.

### Trinn 3: Server modellen (maskin 1)

På maskin 1 starter du vLLM-serveren. Dette vil automatisk laste ned modellen og begynne å servere den på tvers av alle de fire nodene:

```bash
vllm serve Qwen/Qwen3.5-397B-A17B-GPTQ-Int4 \
  --port 7000 \
  --host 0.0.0.0 \
  --max-model-len 131072 \
  --gpu-memory-utilization 0.8 \
  --dtype float16 \
  --tensor-parallel-size 4 \
  --distributed-executor-backend ray \
  --enforce-eager \
  --language-model-only \
  --reasoning-parser qwen3
```

#### Parameterreferanse

| Flagg | Formål |
|------|---------|
| `--port` | Port som HTTP-API-et skal serveres på |
| `--host` | IP-adresse å binde serveren til (`0.0.0.0` for alle grensesnitt) |
| `--max-model-len` | Maksimal kontekstlengde i tokens |
| `--gpu-memory-utilization` | Andel av GPU-minnet som skal tildeles (0,0–1,0) |
| `--dtype` | Datatype for modellvekter |
| `--tensor-parallel-size` | Antall GPU-er modellen skal fordeles på (sett til totalt antall GPU-er i klyngen) |
| `--distributed-executor-backend` | Backend for kjøring på tvers av flere noder (`ray` for klyngedistribusjoner) |
| `--enforce-eager` | Deaktiverer CUDA-grafkompilering for kompatibilitet |
| `--language-model-only` | Hopper over lasting av hjelpemodellkomponenter (f.eks. visuell koder) |
| `--reasoning-parser` | Aktiverer strukturert parsing av resonneringsoutput for modellen |

For fullstendig bruk av parametere, se [vLLM-dokumentasjonen](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Få tilgang til modellen

vLLM eksponerer et OpenAI-kompatibelt API, så du kan koble en hvilken som helst kompatibel klient eller grensesnitt til klyngen din. Ett populært alternativ er [Open WebUI](https://github.com/open-webui/open-webui), som tilbyr et nettleserbasert chattegrensesnitt.

Slik kobler du Open WebUI til vLLM-endepunktet ditt:

1. Åpne **Settings** > **Admin Panel** > **Connections**
2. Klikk på **+** ved **Manage OpenAI API Connections**
3. Sett **Connection Type** til **External**
4. Sett **URL** til `http://<MACHINE_1_IP>:7000/v1`
5. Under **Auth** velger du **None** fra nedtrekksmenyen
6. La **Model IDs** stå tom for automatisk å oppdage alle modeller fra endepunktet

> **Finne `<MACHINE_1_IP>`**: Kjør `hostname -I | awk '{print $1}'` på maskin 1 for å finne den lokale IP-adressen. Hvis du får tilgang til Open WebUI fra maskin 1 selv, kan du bruke `http://localhost:7000/v1`.

![Tilkoblingsinnstillinger for Open WebUI for vLLM-endepunktet](assets/openwebui-connection.png)

Når tilkoblingen er opprettet, velger du modellen fra modellnedtrekksmenyen i Open WebUI og begynner å chatte. Modellen kjører nå på tvers av alle de fire Ryzen AI Halo-nodene dine:

![Chatting med Qwen3.5-397B i Open WebUI](assets/openwebui-chat.png)

## Neste steg

- **Utforsk andre modeller**: Oppdag nye modeller på [Hugging Face](https://huggingface.co/models?&sort=trending) som passer innenfor klyngens samlede GPU-minne
- **Skaler forbi fire noder**: Legg til flere Ryzen AI Halo-systemer som ekstra Ray-arbeidere for å fordele modeller på enda flere GPU-er. Følg [Trinn 2: Bli med i klyngen](#step-2-join-the-cluster-machines-2-3-and-4) på hver ekstra arbeidermaskin, og øk `--tensor-parallel-size` tilsvarende
- **Prøv andre parallelliseringsstrategier**: vLLM støtter [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) for mixture-of-experts-modeller og [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) for høyere gjennomstrømning. Eksperimenter med `--enable-expert-parallel` og `--data-parallel-size` for å finne den beste konfigurasjonen for arbeidsbelastningen din