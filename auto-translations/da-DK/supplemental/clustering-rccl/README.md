<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversættelse.** Denne side er automatisk oversat fra engelsk og er ikke blevet gennemgået af et menneske. Den kan indeholde fejl, og visse instruktioner, kommandoer, downloads, produkttilgængelighed eller andet indhold kan variere afhængigt af sprog eller region. I tilfælde af uoverensstemmelse eller afvigelse er den oprindelige engelske version af playbook'en gældende og har forrang.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Clustering af to Ryzen™ AI Halos med RCCL

## Oversigt

Din Ryzen™ AI Halo er allerede i stand til at køre store sprogmodeller lokalt. Clustering tager dette et skridt videre ved at kombinere GPU-hukommelsen fra flere systemer over et lokalt netværk, hvilket giver dig adgang til endnu større modeller med stærkere ræsonnementsevner, bedre kodegenerering og dybere flersproget forståelse – helt på din egen hardware.

Denne playbook lærer dig, hvordan du clustrer to Ryzen AI Halo-systemer ved hjælp af RCCL (ROCm Communication Collectives Library) med vLLM og kører Qwen3.5-397B, en model med 397 milliarder parametre, på tværs af begge maskiner med ROCm-acceleration.

## Hvad du vil lære

- Hvordan man udvider VRAM-allokeringen på Ryzen AI Halo-systemer
- Opstart af vLLM med ROCm-understøttelse
- Konfiguration af RCCL til multi-node tensor-parallel inferens på tværs af to Ryzen AI Halo-systemer
- Kørsel af en model med 397 milliarder parametre på tværs af to netværksforbundne Ryzen AI Halo-systemer

## Forudsætninger

### Hardware

Denne playbook kræver to Ryzen AI Halo-enheder og én Ethernet-switch, forbundet i en stjernetopologi, hvor hver enhed er tilsluttet direkte til switchen.

| Komponent | Antal | Beskrivelse |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Compute-noder, der udgør clusteret |
| 10 Gbps Ethernet-switch | 1 | Central switch, der muliggør kommunikation mellem flere Ryzen AI Halo-noder (mindst 2 porte) |
| Ethernet-kabel | 2 | Forbinder hver Halo-enhed til switchen (Cat 7 eller højere anbefales) |

> **Bemærk**: Der kræves to Ethernet-switch-porte for at forbinde de to Ryzen AI Halo-enheder. En tredje port er nødvendig, hvis du tilgår modellen fra en separat klientmaskine i stedet for fra en af Halo-enhederne.

### Software
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fysisk Hardware-opsætning

> **Bemærk**: Udfør dette trin på både Maskine 1 og Maskine 2.

Forbind hver Ryzen AI Halo-enhed til Ethernet-switchen ved hjælp af et Cat 7-kabel (eller højere). Dette etablerer 10 Gbps-forbindelsen, der bruges til højhastighedskommunikation mellem noderne.

### 1. Bestem netværksgrænseflader

Find på hver maskine navnet på dens netværksgrænseflade, og noter det (det vil blive omtalt som `IFNAME` i resten af instruktionerne). Kør:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Dette udskriver grænsefladens navn direkte, for eksempel:

```bash
enp191s0
```

### 2. Bekræft netværkslinkets hastighed

Bekræft, at forbindelsen er aktiv og kører med fuld hastighed, ved at kontrollere hastigheden på din grænseflade:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Bemærk**: Erstat `<IFNAME>` med grænsefladenavnet fra [1. Bestem netværksgrænseflader](#1-determine-network-interfaces)

Du bør se en hastighed på `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Bemærk**: Hvis hastigheden er lavere end `10000Mb/s`, eller forbindelsen ikke kommer op, skal du kontrollere kabelforbindelsen og bekræfte, at switchporten er indstillet til 10Gbps. Nogle switche kræver, at auto-forhandling deaktiveres, og at linkhastigheden indstilles manuelt; se dokumentationen til din switch.

## Udvidelse af VRAM-allokering

> **Bemærk**: Udfør dette trin på både Maskine 1 og Maskine 2.

### Hukommelseskonfiguration til kørsel af store modeller

På Linux benytter ROCm en delt systemhukommelsespulje, og denne pulje er som standard konfigureret til halvdelen af systemhukommelsen.

Denne mængde kan øges ved at ændre kernelens Translation Table Manager (TTM) sideindstilling, med følgende instruktioner. AMD anbefaler at indstille den minimale dedikerede VRAM i BIOS (0,5 GB).

* Installer pipx-værktøjet, og tilføj stien til pipx-installerede wheels til systemets søgesti.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installer amd-debug-tools wheel'en fra PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Kør amd-ttm-værktøjet for at forespørge de aktuelle indstillinger for delt hukommelse.
  ```bash
  amd-ttm
  ```

* Omkonfigurer indstillingerne for delt hukommelse til **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Genstart systemet, for at ændringerne træder i kraft.

## Initialisering af vLLM-container

> **Bemærk**: Udfør dette trin på både Maskine 1 og Maskine 2.

Din Ryzen AI Halo leveres med vLLM pakket inde i et prækompileret container-image, som du kører ved hjælp af Podman, et gratis open source-containerværktøj.

### 1. Opret download-mappe til modellen

Når du server Qwen3.5-397B-modellen i denne playbook, downloader vLLM automatisk modelvægtene til dit system. For at sikre, at disse vægte er tilgængelige inde fra containeren, skal du først oprette en models-mappe, som containeren kan montere:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Start vLLM-containeren

Kommandoen nedenfor starter containeren og bringer dig ind i en interaktiv shell. Den monterer den models-mappe, du lige har oprettet, og videregiver din `IFNAME` til `NCCL_SOCKET_IFNAME` og `GLOO_SOCKET_IFNAME`, hvilket fortæller RCCL (biblioteket vLLM bruger til at koordinere GPU'er på tværs af clusteret), hvilken grænseflade der skal bruges.

Start containeren med:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Bemærk**: Erstat `<IFNAME>` med grænsefladenavnet fra [1. Bestem netværksgrænseflader](#1-determine-network-interfaces)

## Kørsel af modellen på clusteret

vLLM bruger Ray til at orkestrere clusteret og RCCL til at håndtere GPU-til-GPU-kommunikation på tværs af noder. Én maskine fungerer som **head node** (Maskine 1) og koordinerer inferens. Den anden tilslutter sig som en **worker node** (Maskine 2) og bidrager med sin GPU-hukommelse og beregningskraft.

> **Bemærk**: Ray er en valgfri afhængighed for vLLM og er kun tilgængelig fra den forkonfigurerede Podman-container.

Ved opstart opdeler vLLM modellen på tværs af begge noder ved hjælp af tensor-parallelisme. Når den er indlæst, forløber inferens, som om den kørte på en enkelt accelerator.

### Trin 1: Start Ray head node (Maskine 1)

På Maskine 1 skal du starte Ray head node for at initialisere clusteret:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Find `<MACHINE_1_IP>`**: Kør `hostname -I | awk '{print $1}'` på Maskine 1 for at finde dens lokale IP-adresse.
### Trin 2: Tilslut til klyngen (Maskine 2)

På Maskine 2 skal du oprette forbindelse til hovednoden for at danne klyngen:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Find `<MACHINE_2_IP>`**: På Maskine 2 skal du køre `hostname -I | awk '{print $1}'` for at finde dens lokale IP-adresse.

### Trin 3: Server modellen (Maskine 1)

På Maskine 1 skal du starte vLLM-serveren. Dette vil automatisk downloade modellen og begynde at servere den på tværs af begge noder:

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

#### Parameterreference

| Flag | Formål |
|------|---------|
| `--port` | Port til at servere HTTP API'et på |
| `--host` | IP-adresse serveren skal bindes til (`0.0.0.0` for alle interfaces) |
| `--max-model-len` | Maksimal kontekstlængde i tokens |
| `--gpu-memory-utilization` | Andel af GPU-hukommelse, der skal allokeres (0.0–1.0) |
| `--dtype` | Datatype for modelvægte |
| `--tensor-parallel-size` | Antal GPU'er, modellen skal fordeles på (sæt til det samlede antal GPU'er i klyngen) |
| `--distributed-executor-backend` | Backend til eksekvering på tværs af flere noder (`ray` til klyngeimplementeringer) |
| `--enforce-eager` | Deaktiverer CUDA graph-kompilering af hensyn til kompatibilitet |
| `--language-model-only` | Springer indlæsning af hjælpemodelkomponenter over (f.eks. vision-encoder) |
| `--reasoning-parser` | Aktiverer struktureret parsing af ræsonneringsoutput for modellen |

For fuld dokumentation af parameterbrug, se [vLLM-dokumentationen](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Adgang til modellen

vLLM eksponerer et OpenAI-kompatibelt API, så du kan tilslutte enhver kompatibel klient eller grænseflade til din klynge. En populær mulighed er [Open WebUI](https://github.com/open-webui/open-webui), som tilbyder en browserbaseret chatgrænseflade.

Sådan tilslutter du Open WebUI til dit vLLM-endpoint:

1. Åbn **Settings** > **Admin Panel** > **Connections**
2. Klik på **+** ud for **Manage OpenAI API Connections**
3. Sæt **Connection Type** til **External**
4. Sæt **URL** til `http://<MACHINE_1_IP>:7000/v1`
5. Under **Auth** skal du vælge **None** i rullemenuen
6. Lad **Model IDs** stå tomt for automatisk at finde alle modeller fra endpointet

> **Find `<MACHINE_1_IP>`**: På Maskine 1 skal du køre `hostname -I | awk '{print $1}'` for at finde dens lokale IP-adresse. Hvis du tilgår Open WebUI fra Maskine 1 selv, kan du bruge `http://localhost:7000/v1`.

![Open WebUI-forbindelsesindstillinger for vLLM-endpointet](assets/openwebui-connection.png)

Når forbindelsen er oprettet, skal du vælge modellen fra modeldrop-down-menuen i Open WebUI og begynde at chatte. Modellen kører nu på tværs af begge dine Ryzen AI Halo-noder:

![Chat med Qwen3.5-397B i Open WebUI](assets/openwebui-chat.png)

## Næste skridt

- **Udforsk andre modeller**: Opdag nye modeller på [Hugging Face](https://huggingface.co/models?&sort=trending), der passer inden for din klynges samlede GPU-hukommelse
- **Skaler til fire noder**: Tilføj to yderligere Ryzen AI Halo-systemer som ekstra Ray-workere for at fordele modeller på endnu flere GPU'er. Dette kræver en Ethernet-switch med mindst fire porte, én til hver node. Følg [Trin 2: Tilslut til klyngen](#step-2-join-the-cluster-machine-2) på hver ekstra worker, og forøg `--tensor-parallel-size` tilsvarende
- **Prøv andre parallelismestrategier**: vLLM understøtter [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) til mixture-of-experts-modeller og [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) for højere gennemløb. Eksperimenter med `--enable-expert-parallel` og `--data-parallel-size` for at finde den bedste konfiguration til din arbejdsbyrde