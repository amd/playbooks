<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Machinevertaling.** Deze pagina is automatisch vertaald vanuit het Engels en is niet door een mens gecontroleerd. Deze pagina kan fouten bevatten en bepaalde instructies, opdrachten, downloads, productbeschikbaarheid of andere inhoud kan per taal of regio verschillen. In geval van tegenstrijdigheid of discrepantie is de oorspronkelijke Engelse versie van de playbook doorslaggevend en prevaleert deze.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Twee Ryzen™ AI Halo's clusteren met RCCL

## Overzicht

Uw Ryzen™ AI Halo is al in staat om grote taalmodellen lokaal uit te voeren. Clustering gaat hier nog een stap verder door het GPU-geheugen van meerdere systemen via een lokaal netwerk te combineren, waardoor u toegang krijgt tot nog grotere modellen met sterker redeneervermogen, betere codegeneratie en dieper meertalig begrip, volledig op uw eigen hardware.

Deze playbook leert u hoe u twee Ryzen AI Halo-systemen clustert met RCCL (ROCm Communication Collectives Library) met vLLM en Qwen3.5-397B uitvoert, een model met 397 miljard parameters, op beide machines met ROCm-acceleratie.

## Wat u leert

- Hoe u de VRAM-toewijzing op Ryzen AI Halo-systemen kunt uitbreiden
- vLLM starten met ROCm-ondersteuning
- RCCL configureren voor multi-node tensor-parallelle inferentie op twee Ryzen AI Halo-systemen
- Een model met 397 miljard parameters uitvoeren op twee genetwerkte Ryzen AI Halo-systemen

## Vereisten

### Hardware

Voor deze playbook zijn twee Ryzen AI Halo-eenheden en één Ethernet-switch nodig, verbonden in een stertopologie waarbij elke eenheid rechtstreeks op de switch is aangesloten.

| Onderdeel | Aantal | Beschrijving |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Compute-nodes die het cluster vormen |
| 10Gbps Ethernet-switch | 1 | Centrale switch om communicatie tussen meerdere Ryzen AI Halo-nodes mogelijk te maken (minstens 2 poorten) |
| Ethernet-kabel | 2 | Verbindt elke Halo-eenheid met de switch (Cat 7 of hoger aanbevolen) |

> **Opmerking**: Er zijn twee Ethernet-switchpoorten nodig om de twee Ryzen AI Halo-eenheden te verbinden. Een derde poort is nodig als u het model benadert vanaf een aparte clientmachine in plaats van vanaf een van de Halo-eenheden.

### Software
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fysieke hardware-installatie

> **Opmerking**: Voer deze stap uit op zowel Machine 1 als Machine 2.

Sluit elke Ryzen AI Halo-eenheid aan op de Ethernet-switch met een Cat 7-kabel (of hoger). Dit brengt de 10Gbps-verbinding tot stand die wordt gebruikt voor snelle communicatie tussen de nodes.

### 1. Netwerkinterfaces bepalen

Zoek op elke machine de naam van de netwerkinterface en noteer deze (hierna aangeduid als `IFNAME` in de rest van de instructies). Voer uit:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Dit toont de naam van de interface direct, bijvoorbeeld:

```bash
enp191s0
```

### 2. Netwerklinksnelheden verifiëren

Controleer of de verbinding actief is en op volle snelheid draait door de snelheid van uw interface te controleren:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Opmerking**: Vervang `<IFNAME>` door de uitvoerinterfacenaam uit [1. Netwerkinterfaces bepalen](#1-determine-network-interfaces)

U zou een snelheid van `10000Mb/s` moeten zien:

```bash
	Speed: 10000Mb/s
```

> **Opmerking**: Als de snelheid lager is dan `10000Mb/s` of de verbinding niet tot stand komt, controleer dan de kabelverbinding en bevestig dat de switchpoort is ingesteld op 10Gbps. Sommige switches vereisen dat auto-onderhandeling wordt uitgeschakeld en de linksnelheid handmatig wordt ingesteld; raadpleeg de documentatie van uw switch.

## VRAM-toewijzing uitbreiden

> **Opmerking**: Voer deze stap uit op zowel Machine 1 als Machine 2.

### Geheugenconfiguratie voor het uitvoeren van grote modellen

Op Linux maakt ROCm gebruik van een gedeelde systeemgeheugenpool, en deze pool is standaard geconfigureerd op de helft van het systeemgeheugen.

Deze hoeveelheid kan worden verhoogd door de Translation Table Manager (TTM)-pagina-instelling van de kernel te wijzigen, volgens de onderstaande instructies. AMD raadt aan om het minimale toegewijde VRAM in te stellen in de BIOS (0,5 GB).

* Installeer het pipx-hulpprogramma en voeg het pad voor door pipx geïnstalleerde wheels toe aan het systeemzoekpad.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installeer de amd-debug-tools wheel vanaf PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Voer het amd-ttm-hulpprogramma uit om de huidige instellingen voor gedeeld geheugen op te vragen.
  ```bash
  amd-ttm
  ```

* Herconfigureer de instellingen voor gedeeld geheugen naar **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Start het systeem opnieuw op zodat de wijzigingen van kracht worden.

## Initialisatie van de vLLM-container

> **Opmerking**: Voer deze stap uit op zowel Machine 1 als Machine 2.

Uw Ryzen AI Halo wordt geleverd met vLLM verpakt in een vooraf gebouwde container-image, die u uitvoert met Podman, een gratis en opensource containerhulpprogramma.

### 1. Maak de map voor het downloaden van modellen aan

Wanneer u het Qwen3.5-397B-model in deze playbook host, zal vLLM automatisch de modelgewichten naar uw systeem downloaden. Om ervoor te zorgen dat deze gewichten toegankelijk zijn vanuit de container, maakt u eerst een modellenmap aan die de container kan koppelen:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Start de vLLM-container

Met de onderstaande opdracht start u de container en komt u in een interactieve shell terecht. Deze koppelt de zojuist aangemaakte modellenmap en geeft uw `IFNAME` door aan `NCCL_SOCKET_IFNAME` en `GLOO_SOCKET_IFNAME`, waarmee u aan RCCL (de bibliotheek die vLLM gebruikt om GPU's op het cluster te coördineren) aangeeft welke interface moet worden gebruikt.

Start de container met:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Opmerking**: Vervang `<IFNAME>` door de uitvoerinterfacenaam uit [1. Netwerkinterfaces bepalen](#1-determine-network-interfaces)

## Het model uitvoeren op het cluster

vLLM gebruikt Ray om het cluster te orkestreren en RCCL om de GPU-naar-GPU-communicatie tussen nodes af te handelen. Eén machine fungeert als de **head node** (Machine 1) en coördineert de inferentie. De andere sluit aan als **worker node** (Machine 2) en levert zijn GPU-geheugen en rekenkracht.

> **Opmerking**: Ray is een optionele afhankelijkheid voor vLLM en is alleen beschikbaar vanuit de vooraf geconfigureerde Podman-container.

Bij het opstarten verdeelt vLLM het model over beide nodes met behulp van tensor-parallelisme. Zodra het model is geladen, verloopt de inferentie alsof deze op één enkele accelerator draait.

#### Ray OOM-fouten voorkomen

Standaard bewaakt Ray het hostgeheugen op elke node en beëindigt het het grootste proces wanneer het geheugengebruik boven de 95% komt. Op uw Ryzen™ AI Halo delen de GPU en de host één geheugenpool, waardoor het laden van een model een `ray.exceptions.OutOfMemoryError` kan veroorzaken en het worker-proces kan beëindigen.

Om dit te voorkomen, exporteren we `RAY_memory_monitor_refresh_ms=0` op elke machine voordat we het cluster starten en eraan deelnemen.
### Stap 1: Start het Ray Head Node (Machine 1)

Start op Machine 1 het Ray head node om de cluster te initialiseren:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **`<MACHINE_1_IP>` vinden**: Voer op Machine 1 `hostname -I | awk '{print $1}'` uit om het lokale IP-adres te vinden.

### Stap 2: Sluit je aan bij de Cluster (Machine 2)

Maak op Machine 2 verbinding met het head node om de cluster te vormen:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **`<MACHINE_2_IP>` vinden**: Voer op Machine 2 `hostname -I | awk '{print $1}'` uit om het lokale IP-adres te vinden.

### Stap 3: Serveer het Model (Machine 1)

Start op Machine 1 de vLLM-server. Dit downloadt automatisch het model en begint het te serveren op beide nodes:

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

#### Parameteroverzicht

| Vlag | Doel |
|------|---------|
| `--port` | Poort waarop de HTTP API wordt geserveerd |
| `--host` | IP-adres waarop de server wordt gebonden (`0.0.0.0` voor alle interfaces) |
| `--max-model-len` | Maximale contextlengte in tokens |
| `--gpu-memory-utilization` | Fractie van het GPU-geheugen dat wordt toegewezen (0.0–1.0) |
| `--dtype` | Datatype voor modelgewichten |
| `--tensor-parallel-size` | Aantal GPU's waarover het model wordt gesharded (instellen op het totale aantal GPU's in de cluster) |
| `--distributed-executor-backend` | Backend voor uitvoering op meerdere nodes (`ray` voor cluster-implementaties) |
| `--enforce-eager` | Schakelt CUDA-graafcompilatie uit voor compatibiliteit |
| `--language-model-only` | Slaat het laden van aanvullende modelonderdelen over (bijv. vision encoder) |
| `--reasoning-parser` | Schakelt gestructureerde parsing van redeneeroutput voor het model in |

Raadpleeg voor volledig parametergebruik de [vLLM-documentatie](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Toegang tot het Model

vLLM stelt een OpenAI-compatibele API beschikbaar, zodat je elke compatibele client of interface met je cluster kunt verbinden. Een populaire optie is [Open WebUI](https://github.com/open-webui/open-webui), dat een browsergebaseerde chatinterface biedt.

Om Open WebUI te verbinden met je vLLM-eindpunt:

1. Open **Instellingen** > **Beheerderspaneel** > **Verbindingen**
2. Klik op de **+** bij **OpenAI API-verbindingen beheren**
3. Stel het **Verbindingstype** in op **Extern**
4. Stel de **URL** in op `http://<MACHINE_1_IP>:7000/v1`
5. Selecteer bij **Auth** de optie **Geen** in de vervolgkeuzelijst
6. Laat **Model-ID's** leeg om automatisch alle modellen van het eindpunt te detecteren

> **`<MACHINE_1_IP>` vinden**: Voer op Machine 1 `hostname -I | awk '{print $1}'` uit om het lokale IP-adres te vinden. Als je Open WebUI vanaf Machine 1 zelf benadert, kun je `http://localhost:7000/v1` gebruiken.

![Open WebUI-verbindingsinstellingen voor het vLLM-eindpunt](assets/openwebui-connection.png)

Zodra de verbinding tot stand is gebracht, selecteer je het model in de modelvervolgkeuzelijst in Open WebUI en kun je beginnen met chatten. Het model draait nu op beide Ryzen AI Halo-nodes van je cluster:

![Chatten met Qwen3.5-397B in Open WebUI](assets/openwebui-chat.png)

## Volgende Stappen

- **Verken andere modellen**: Ontdek nieuwe modellen op [Hugging Face](https://huggingface.co/models?&sort=trending) die passen binnen het gecombineerde GPU-geheugen van je cluster
- **Schaal naar vier nodes**: Voeg twee extra Ryzen AI Halo-systemen toe als bijkomende Ray-workers om modellen over nog meer GPU's te sharden. Dit vereist een Ethernet-switch met minstens vier poorten, één voor elk node. Volg [Stap 2: Sluit je aan bij de Cluster](#step-2-join-the-cluster-machine-2) op elke extra worker en verhoog `--tensor-parallel-size` dienovereenkomstig
- **Probeer andere parallellisatiestrategieën**: vLLM ondersteunt [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) voor mixture-of-experts-modellen en [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) voor hogere doorvoer. Experimenteer met `--enable-expert-parallel` en `--data-parallel-size` om de beste configuratie voor je workload te vinden