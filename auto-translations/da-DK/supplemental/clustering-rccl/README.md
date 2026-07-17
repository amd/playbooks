<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Clustering af to Ryzen™ AI Halos med RCCL

## Oversigt

Din Ryzen™ AI Halo er allerede i stand til at køre store sprogmodeller lokalt. Clustering tager dette videre ved at kombinere GPU-hukommelsen fra flere systemer over et lokalt netværk, hvilket giver dig adgang til endnu større modeller med stærkere ræsonnering, bedre kodegenerering og dybere flersproget forståelse – alt sammen udelukkende på din egen hardware.

Dette playbook lærer dig, hvordan du klustrer to Ryzen AI Halo-systemer ved hjælp af RCCL (ROCm Communication Collectives Library) med vLLM og kører Qwen3.5-397B, en model med 397 milliarder parametre, på tværs af begge maskiner med ROCm-acceleration.

## Hvad du vil lære

- Sådan udvider du VRAM-allokeringen på Ryzen AI Halo-systemer
- Sådan starter du vLLM med ROCm-understøttelse
- Sådan konfigurerer du RCCL til multi-node tensor-parallel inferens på tværs af to Ryzen AI Halo-systemer
- Sådan kører du en model med 397 milliarder parametre på tværs af to netværksforbundne Ryzen AI Halo-systemer

## Forudsætninger

### Hardware

Dette playbook kræver to Ryzen AI Halo-enheder og én Ethernet-switch, forbundet i en stjerne-topologi, hvor hver enhed er kablet direkte til switchen.

| Komponent | Antal | Beskrivelse |
|-----------|-------|-------------|
| Ryzen AI Halo | 2 | Beregningsnoder, der udgør klusteret |
| 10Gbps Ethernet-switch | 1 | Central switch til at muliggøre multi-node Ryzen AI Halo-kommunikation (mindst 2 porte) |
| Ethernet-kabel | 2 | Forbinder hver Halo-enhed til switchen (Cat 7 eller højere anbefales) |

> **Bemærk**: To Ethernet-switch-porte er nødvendige for at forbinde de to Ryzen AI Halo-enheder. En tredje port er nødvendig, hvis du tilgår modellen fra en separat klientmaskine i stedet for fra en af Halo-enhederne.

### Software
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fysisk hardwareopsætning

> **Bemærk**: Gennemfør dette trin på både Maskine 1 og Maskine 2.

Forbind hver Ryzen AI Halo-enhed til Ethernet-switchen ved hjælp af et Cat 7-kabel (eller højere). Dette etablerer den 10Gbps-forbindelse, der bruges til højthastighedskommunikation mellem noderne.

### 1. Bestem netværksgrænseflader

På hver maskine skal du finde navnet på dens netværksgrænseflade og notere det (det vil blive refereret til i resten af instruktionerne som `IFNAME`). Kør:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Dette udskriver grænsefladenavnet direkte, for eksempel:

```bash
enp191s0
```

### 2. Verificer netværksforbindelseshastigheder

Bekræft, at forbindelsen er aktiv og kører med fuld hastighed ved at kontrollere hastigheden på din grænseflade:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Bemærk**: Erstat `<IFNAME>` med det udskrevne grænsefladenavnet fra [1. Bestem netværksgrænseflader](#1-determine-network-interfaces)

Du bør se en hastighed på `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Bemærk**: Hvis hastigheden er lavere end `10000Mb/s`, eller forbindelsen ikke kommer op, skal du kontrollere kabelopkoblingen og bekræfte, at switch-porten er indstillet til 10Gbps. Nogle switches kræver, at auto-forhandling deaktiveres og forbindelseshastigheden indstilles manuelt; se din switches dokumentation.

## Udvidelse af VRAM-allokering

> **Bemærk**: Gennemfør dette trin på både Maskine 1 og Maskine 2.

### Hukommelseskonfiguration til kørsel af store modeller

På Linux anvender ROCm en delt systemhukommelsespulje, og denne pulje er som standard konfigureret til halvdelen af systemhukommelsen.

Denne mængde kan øges ved at ændre kernelens Translation Table Manager (TTM) side-indstilling med følgende instruktioner. AMD anbefaler at indstille den minimale dedikerede VRAM i BIOS (0,5 GB).

* Installer pipx-hjælpeprogrammet og tilføj stien til pipx-installerede wheels i systemets søgesti.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installer amd-debug-tools-wheelet fra PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Kør amd-ttm-værktøjet for at forespørge de aktuelle indstillinger for delt hukommelse.
  ```bash
  amd-ttm
  ```

* Rekonfigurer indstillingerne for delt hukommelse til **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Genstart systemet for at ændringerne træder i kraft.

## vLLM-containerinitialisering

> **Bemærk**: Gennemfør dette trin på både Maskine 1 og Maskine 2.

Din Ryzen AI Halo leveres med vLLM pakket inde i et færdigbygget container-image, som du kører ved hjælp af Podman, et gratis og open source container-værktøj.

### 1. Opret mappen til modeldownload

Når du serverer Qwen3.5-397B-modellen i dette playbook, vil vLLM automatisk downloade modelvægtene til dit system. For at sikre, at disse vægte er tilgængelige inde fra containeren, skal du først oprette en models-mappe, som containeren kan montere:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Start vLLM-containeren

Kommandoen nedenfor starter containeren og slipper dig ind i en interaktiv shell. Den monterer den models-mappe, du netop oprettede, og sender din `IFNAME` til `NCCL_SOCKET_IFNAME` og `GLOO_SOCKET_IFNAME`, hvilket fortæller RCCL (det bibliotek vLLM bruger til at koordinere GPU'er på tværs af klusteret), hvilken grænseflade der skal bruges.

Start containeren med:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Bemærk**: Erstat `<IFNAME>` med det udskrevne grænsefladenavnet fra [1. Bestem netværksgrænseflader](#1-determine-network-interfaces)

## Kørsel af modellen på klusteret

vLLM bruger Ray til at orkestrere klusteret og RCCL til at håndtere GPU-til-GPU-kommunikation på tværs af noder. Én maskine fungerer som **head node** (Maskine 1) og koordinerer inferens. Den anden tilslutter sig som **worker node** (Maskine 2) og bidrager med sin GPU-hukommelse og beregningskraft.

> **Bemærk**: Ray er en valgfri afhængighed for vLLM og er kun tilgængelig inde fra den forudkonfigurerede Podman-container.

Ved opstart opdeler vLLM modellen på tværs af begge noder ved hjælp af tensor-parallelisme. Når den er indlæst, forløber inferens, som om den kørte på en enkelt accelerator.

### Trin 1: Start Ray head node (Maskine 1)

På Maskine 1 skal du starte Ray head node for at initialisere klusteret:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Find `<MACHINE_1_IP>`**: På Maskine 1 skal du køre `hostname -I | awk '{print $1}'` for at finde dens lokale IP-adresse.

### Trin 2: Tilslut klusteret (Maskine 2)

På Maskine 2 skal du oprette forbindelse til head node for at danne klusteret:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Find `<MACHINE_2_IP>`**: På Maskine 2 skal du køre `hostname -I | awk '{print $1}'` for at finde dens lokale IP-adresse.

### Trin 3: Servér modellen (Maskine 1)

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
|------|--------|
| `--port` | Port til at servere HTTP API'en på |
| `--host` | IP-adresse at binde serveren til (`0.0.0.0` for alle grænseflader) |
| `--max-model-len` | Maksimal kontekstlængde i tokens |
| `--gpu-memory-utilization` | Andel af GPU-hukommelse der skal allokeres (0,0–1,0) |
| `--dtype` | Datatype for modelvægte |
| `--tensor-parallel-size` | Antal GPU'er til at opdele modellen på tværs af (indstilles til det samlede antal GPU'er i klusteret) |
| `--distributed-executor-backend` | Backend til multi-node-eksekvering (`ray` til klusterinstallationer) |
| `--enforce-eager` | Deaktiverer CUDA-grafkompilering for kompatibilitet |
| `--language-model-only` | Springer indlæsning af hjælpemodel-komponenter over (f.eks. vision encoder) |
| `--reasoning-parser` | Aktiverer struktureret ræsonneringsoutput-parsing for modellen |

For fuld parameterbrug, se [vLLM-dokumentationen](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Adgang til modellen

vLLM eksponerer en OpenAI-kompatibel API, så du kan forbinde enhver kompatibel klient eller grænseflade til dit kluster. En populær mulighed er [Open WebUI](https://github.com/open-webui/open-webui), som giver en browserbaseret chatgrænseflade.

Sådan forbinder du Open WebUI til dit vLLM-endpoint:

1. Åbn **Indstillinger** > **Adminpanel** > **Forbindelser**
2. Klik på **+** ved **Administrer OpenAI API-forbindelser**
3. Indstil **Forbindelsestype** til **Ekstern**
4. Indstil **URL** til `http://<MACHINE_1_IP>:7000/v1`
5. Under **Auth** skal du vælge **Ingen** fra rullemenuen
6. Lad **Model-ID'er** være tomme for automatisk at opdage alle modeller fra endpointet

> **Find `<MACHINE_1_IP>`**: På Maskine 1 skal du køre `hostname -I | awk '{print $1}'` for at finde dens lokale IP-adresse. Hvis du tilgår Open WebUI fra Maskine 1 selv, kan du bruge `http://localhost:7000/v1`.

![Open WebUI-forbindelsesindstillinger for vLLM-endpointet](assets/openwebui-connection.png)

Når du er forbundet, skal du vælge modellen fra model-rullemenuen i Open WebUI og begynde at chatte. Modellen kører nu på tværs af begge dine Ryzen AI Halo-noder:

![Chat med Qwen3.5-397B i Open WebUI](assets/openwebui-chat.png)

## Næste skridt

- **Udforsk andre modeller**: Opdag nye modeller på [Hugging Face](https://huggingface.co/models?&sort=trending), der passer inden for dit klusters kombinerede GPU-hukommelse
- **Skalér til fire noder**: Tilføj to yderligere Ryzen AI Halo-systemer som ekstra Ray-workers for at opdele modeller på tværs af endnu flere GPU'er. Dette kræver en Ethernet-switch med mindst fire porte, én til hver node. Følg [Trin 2: Tilslut klusteret](#step-2-join-the-cluster-machine-2) på hver ekstra worker og øg `--tensor-parallel-size` tilsvarende
- **Prøv andre parallelismestrategier**: vLLM understøtter [ekspert-parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) til mixture-of-experts-modeller og [data-parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) til højere gennemstrømning. Eksperimenter med `--enable-expert-parallel` og `--data-parallel-size` for at finde den bedste konfiguration til din arbejdsbyrde