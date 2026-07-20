<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Denne playbook bruger specielle tags, som GitHub ikke kan gengive. Besøg venligst [amd.com/playbooks](https://amd.com/playbooks) for at få vist dette indhold korrekt.
<!-- @github-only:end -->

# Sammenkobling af to Ryzen™ AI Halo-systemer med RCCL

## Oversigt

Din Ryzen™ AI Halo kan allerede køre store sprogmodeller lokalt. Ved at klynge flere systemer sammen går du et skridt videre og kombinerer GPU-hukommelsen fra flere systemer over et lokalt netværk, hvilket giver dig adgang til endnu større modeller med stærkere ræsonnement, bedre kodegenerering og dybere flersproget forståelse – helt på din egen hardware.

Denne playbook lærer dig, hvordan du sammenkobler to Ryzen AI Halo-systemer ved hjælp af RCCL (ROCm Communication Collectives Library) med vLLM og kører Qwen3.5-397B, en model med 397 milliarder parametre, på tværs af begge maskiner med ROCm-acceleration.

## Hvad du vil lære

- Hvordan du udvider VRAM-allokeringen på Ryzen AI Halo-systemer
- Opstart af vLLM med ROCm-understøttelse
- Konfiguration af RCCL til multi-node tensor-parallel inferens på tværs af to Ryzen AI Halo-systemer
- Kørsel af en model med 397 milliarder parametre på tværs af to netværksforbundne Ryzen AI Halo-systemer

## Forudsætninger

### Hardware

Denne playbook kræver to Ryzen AI Halo-enheder og én Ethernet-switch, forbundet i en stjernetopologi, hvor hver enhed er forbundet direkte til switchen.

| Komponent | Antal | Beskrivelse |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Compute-noder, der udgør klyngen |
| 10Gbps Ethernet-switch | 1 | Central switch, der muliggør kommunikation mellem flere Ryzen AI Halo-noder (mindst 2 porte) |
| Ethernet-kabel | 2 | Forbinder hver Halo-enhed til switchen (Cat 7 eller højere anbefales) |

> **Bemærk**: Der kræves to porte på Ethernet-switchen for at forbinde de to Ryzen AI Halo-enheder. Der kræves en tredje port, hvis du tilgår modellen fra en separat klientmaskine i stedet for fra en af Halo-enhederne.

### Software
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Opsætning af fysisk hardware

> **Bemærk**: Udfør dette trin på både Maskine 1 og Maskine 2.

Forbind hver Ryzen AI Halo-enhed til Ethernet-switchen med et Cat 7 (eller højere) kabel. Dette etablerer 10Gbps-forbindelsen, der bruges til højhastighedskommunikation mellem noderne.

### 1. Bestem netværksgrænseflader

På hver maskine skal du finde navnet på dens netværksgrænseflade og notere det (det vil blive omtalt som `IFNAME` i resten af instruktionerne). Kør:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Dette udskriver navnet på grænsefladen direkte, for eksempel:

```bash
enp191s0
```

### 2. Bekræft netværkets linkhastigheder

Bekræft, at forbindelsen er aktiv og kører med fuld hastighed, ved at tjekke hastigheden på din grænseflade:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Bemærk**: Erstat `<IFNAME>` med navnet på output-grænsefladen fra [1. Bestem netværksgrænseflader](#1-determine-network-interfaces)

Du bør se en hastighed på `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Bemærk**: Hvis hastigheden er lavere end `10000Mb/s`, eller forbindelsen ikke etableres, skal du kontrollere kabelforbindelsen og bekræfte, at switch-porten er indstillet til 10Gbps. Nogle switches kræver, at auto-negotiation deaktiveres, og at linkhastigheden indstilles manuelt; se dokumentationen til din switch.

## Udvidelse af VRAM-allokering

> **Bemærk**: Udfør dette trin på både Maskine 1 og Maskine 2.

### Hukommelseskonfiguration til kørsel af store modeller

På Linux bruger ROCm en delt systemhukommelsespulje, og denne pulje er som standard konfigureret til halvdelen af systemhukommelsen.

Denne mængde kan øges ved at ændre kernens Translation Table Manager (TTM)-sideindstilling ved hjælp af følgende instruktioner. AMD anbefaler at indstille den minimale dedikerede VRAM i BIOS (0,5 GB).

* Installer værktøjet pipx, og tilføj stien for pipx-installerede wheels til systemets søgesti.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installer amd-debug-tools-wheel'en fra PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Kør amd-ttm-værktøjet for at forespørge på de aktuelle indstillinger for delt hukommelse.
  ```bash
  amd-ttm
  ```

* Genkonfigurer indstillingerne for delt hukommelse til **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Genstart systemet, for at ændringerne træder i kraft.

## Initialisering af vLLM-container

> **Bemærk**: Udfør dette trin på både Maskine 1 og Maskine 2.

Din Ryzen AI Halo leveres med vLLM pakket inde i et præbygget container-image, som du kører ved hjælp af Podman, et gratis open source-containerværktøj.

### 1. Opret mappen til modeldownload

Når du serverer Qwen3.5-397B-modellen i denne playbook, vil vLLM automatisk downloade modelvægtene til dit system. For at sikre, at disse vægte er tilgængelige inde fra containeren, skal du først oprette en models-mappe, som containeren kan montere:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Start vLLM-containeren

Kommandoen nedenfor starter containeren og fører dig ind i en interaktiv shell. Den monterer den models-mappe, du lige har oprettet, og videregiver din `IFNAME` til `NCCL_SOCKET_IFNAME` og `GLOO_SOCKET_IFNAME`, hvilket fortæller RCCL (biblioteket, som vLLM bruger til at koordinere GPU'er på tværs af klyngen), hvilken grænseflade der skal bruges.

Start containeren med:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Bemærk**: Erstat `<IFNAME>` med navnet på output-grænsefladen fra [1. Bestem netværksgrænseflader](#1-determine-network-interfaces)

## Kørsel af modellen på klyngen

vLLM bruger Ray til at orkestrere klyngen og RCCL til at håndtere GPU-til-GPU-kommunikation på tværs af noder. Én maskine fungerer som **head-node** (Maskine 1), der koordinerer inferens. Den anden slutter sig til som **worker-node** (Maskine 2) og bidrager med sin GPU-hukommelse og beregningskraft.

> **Bemærk**: Ray er en valgfri afhængighed for vLLM og er kun tilgængelig fra inden for den prækonfigurerede Podman-container.

Ved opstart opdeler vLLM modellen på tværs af begge noder ved hjælp af tensor-parallelisme. Når den er indlæst, foregår inferens, som om den kørte på en enkelt accelerator.

### Trin 1: Start Ray head-noden (Maskine 1)

På Maskine 1 skal du starte Ray head-noden for at initialisere klyngen:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Sådan finder du `<MACHINE_1_IP>`**: Kør `hostname -I | awk '{print $1}'` på Maskine 1 for at finde dens lokale IP-adresse.
### Trin 2: Tilslut til klyngen (Maskine 2)

På Maskine 2 skal du oprette forbindelse til hovedknuden for at danne klyngen:

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
| `--port` | Port, som HTTP API'et skal serveres på |
| `--host` | IP-adresse, som serveren skal bindes til (`0.0.0.0` for alle interfaces) |
| `--max-model-len` | Maksimal kontekstlængde i tokens |
| `--gpu-memory-utilization` | Andel af GPU-hukommelse, der skal allokeres (0.0–1.0) |
| `--dtype` | Datatype for modellens vægte |
| `--tensor-parallel-size` | Antal GPU'er, som modellen skal fordeles på tværs af (sæt til det samlede antal GPU'er i klyngen) |
| `--distributed-executor-backend` | Backend til udførelse på tværs af flere noder (`ray` til klyngeimplementeringer) |
| `--enforce-eager` | Deaktiverer CUDA-graf-kompilering af hensyn til kompatibilitet |
| `--language-model-only` | Springer indlæsning af hjælpekomponenter til modellen over (f.eks. vision-encoder) |
| `--reasoning-parser` | Aktiverer struktureret parsing af ræsonneringsoutput for modellen |

For fuld gennemgang af parametre, se [vLLM-dokumentationen](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Tilgang til modellen

vLLM eksponerer et OpenAI-kompatibelt API, så du kan tilslutte enhver kompatibel klient eller grænseflade til din klynge. Ét populært valg er [Open WebUI](https://github.com/open-webui/open-webui), som tilbyder en browserbaseret chatgrænseflade.

Sådan tilslutter du Open WebUI til dit vLLM-endpoint:

1. Åbn **Indstillinger** > **Administrationspanel** > **Forbindelser**
2. Klik på **+** ved **Administrer OpenAI API-forbindelser**
3. Sæt **Forbindelsestype** til **Ekstern**
4. Sæt **URL** til `http://<MACHINE_1_IP>:7000/v1`
5. Under **Godkendelse** skal du vælge **Ingen** fra rullemenuen
6. Lad **Model-ID'er** stå tomt for automatisk at opdage alle modeller fra endpointet

> **Find `<MACHINE_1_IP>`**: På Maskine 1 skal du køre `hostname -I | awk '{print $1}'` for at finde dens lokale IP-adresse. Hvis du tilgår Open WebUI fra Maskine 1 selv, kan du bruge `http://localhost:7000/v1`.

![Open WebUI-forbindelsesindstillinger for vLLM-endpointet](assets/openwebui-connection.png)

Når forbindelsen er oprettet, skal du vælge modellen fra rullemenuen med modeller i Open WebUI og begynde at chatte. Modellen kører nu på tværs af begge dine Ryzen AI Halo-noder:

![Chat med Qwen3.5-397B i Open WebUI](assets/openwebui-chat.png)

## Næste trin

- **Udforsk andre modeller**: Find nye modeller på [Hugging Face](https://huggingface.co/models?&sort=trending), der passer inden for din klynges samlede GPU-hukommelse
- **Skalér til fire noder**: Tilføj to yderligere Ryzen AI Halo-systemer som ekstra Ray-workere for at fordele modeller på tværs af endnu flere GPU'er. Dette kræver en Ethernet-switch med mindst fire porte, én til hver node. Følg [Trin 2: Tilslut til klyngen](#step-2-join-the-cluster-machine-2) på hver ekstra worker og øg `--tensor-parallel-size` tilsvarende
- **Prøv andre parallelismestrategier**: vLLM understøtter [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) til mixture-of-experts-modeller og [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) for højere gennemløb. Eksperimentér med `--enable-expert-parallel` og `--data-parallel-size` for at finde den bedste konfiguration til din arbejdsbyrde