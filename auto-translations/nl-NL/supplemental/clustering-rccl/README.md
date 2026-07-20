<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Deze playbook gebruikt speciale tags die GitHub niet kan weergeven. Ga naar [amd.com/playbooks](https://amd.com/playbooks) om deze inhoud correct te bekijken.
<!-- @github-only:end -->

# Twee Ryzen™ AI Halo's clusteren met RCCL

## Overzicht

Uw Ryzen™ AI Halo is al in staat om grote taalmodellen lokaal uit te voeren. Clustering gaat een stap verder door het GPU-geheugen van meerdere systemen over een lokaal netwerk te combineren, waardoor u toegang krijgt tot nog grotere modellen met sterker redeneervermogen, betere codegeneratie en dieper meertalig begrip, volledig op uw eigen hardware.

Deze playbook leert u hoe u twee Ryzen AI Halo-systemen clustert met RCCL (ROCm Communication Collectives Library) met vLLM en Qwen3.5-397B uitvoert, een model met 397 miljard parameters, op beide machines met ROCm-versnelling.

## Wat u zult leren

- Hoe u de VRAM-toewijzing op Ryzen AI Halo-systemen uitbreidt
- vLLM starten met ondersteuning voor ROCm
- RCCL configureren voor multi-node tensor-parallelle inferentie tussen twee Ryzen AI Halo-systemen
- Een model met 397 miljard parameters uitvoeren op twee genetwerkte Ryzen AI Halo-systemen

## Vereisten

### Hardware

Voor deze playbook zijn twee Ryzen AI Halo-eenheden en één Ethernet-switch nodig, verbonden in een stertopologie waarbij elke eenheid rechtstreeks met de switch is bekabeld.

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

Verbind elke Ryzen AI Halo-eenheid met de Ethernet-switch met een Cat 7-kabel (of hoger). Dit stelt de 10Gbps-verbinding in die wordt gebruikt voor snelle communicatie tussen de nodes.

### 1. Netwerkinterfaces bepalen

Zoek op elke machine de naam van de netwerkinterface op en noteer deze (deze wordt in de rest van de instructies aangeduid als `IFNAME`). Voer uit:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Dit toont de interfacenaam direct, bijvoorbeeld:

```bash
enp191s0
```

### 2. Netwerklinksnelheden verifiëren

Controleer of de verbinding actief is en op volledige snelheid draait door de snelheid van uw interface te controleren:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Opmerking**: Vervang `<IFNAME>` door de interfacenaam uit de uitvoer van [1. Netwerkinterfaces bepalen](#1-determine-network-interfaces)

U zou een snelheid van `10000Mb/s` moeten zien:

```bash
	Speed: 10000Mb/s
```

> **Opmerking**: Als de snelheid lager is dan `10000Mb/s` of de verbinding niet tot stand komt, controleer dan de kabelverbinding en bevestig dat de switchpoort is ingesteld op 10Gbps. Sommige switches vereisen dat auto-negotiation wordt uitgeschakeld en de linksnelheid handmatig wordt ingesteld; raadpleeg de documentatie van uw switch.

## VRAM-toewijzing uitbreiden

> **Opmerking**: Voer deze stap uit op zowel Machine 1 als Machine 2.

### Geheugenconfiguratie voor het uitvoeren van grote modellen

Op Linux gebruikt ROCm een gedeelde systeemgeheugenpool, en deze pool is standaard geconfigureerd op de helft van het systeemgeheugen.

Deze hoeveelheid kan worden verhoogd door de instelling van de Translation Table Manager (TTM)-pagina van de kernel te wijzigen, met de volgende instructies. AMD raadt aan om de minimale toegewezen VRAM in de BIOS in te stellen (0,5 GB).

* Installeer de pipx-utility en voeg het pad voor door pipx geïnstalleerde wheels toe aan het zoekpad van het systeem.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installeer de amd-debug-tools wheel vanuit PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Voer de amd-ttm-tool uit om de huidige instellingen voor gedeeld geheugen op te vragen.
  ```bash
  amd-ttm
  ```

* Configureer de instellingen voor gedeeld geheugen opnieuw naar **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Start het systeem opnieuw op zodat de wijzigingen van kracht worden.

## vLLM-containerinitialisatie

> **Opmerking**: Voer deze stap uit op zowel Machine 1 als Machine 2.

Uw Ryzen AI Halo wordt geleverd met vLLM verpakt in een vooraf gebouwde container-image, die u uitvoert met Podman, een gratis en open source containertool.

### 1. De downloadmap voor het model aanmaken

Wanneer u het Qwen3.5-397B-model in deze playbook serveert, zal vLLM automatisch de modelgewichten naar uw systeem downloaden. Om ervoor te zorgen dat die gewichten toegankelijk zijn vanuit de container, maakt u eerst een modellenmap aan die de container kan mounten:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. De vLLM-container starten

Het onderstaande commando start de container en brengt u naar een interactieve shell. Het mount de zojuist aangemaakte modellenmap en geeft uw `IFNAME` door aan `NCCL_SOCKET_IFNAME` en `GLOO_SOCKET_IFNAME`, waarmee aan RCCL (de bibliotheek die vLLM gebruikt om GPU's binnen het cluster te coördineren) wordt aangegeven welke interface moet worden gebruikt.

Start de container met:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Opmerking**: Vervang `<IFNAME>` door de interfacenaam uit de uitvoer van [1. Netwerkinterfaces bepalen](#1-determine-network-interfaces)

## Het model uitvoeren op het cluster

vLLM gebruikt Ray om het cluster te orkestreren en RCCL om GPU-naar-GPU-communicatie tussen nodes af te handelen. Eén machine fungeert als de **head node** (Machine 1), die de inferentie coördineert. De andere sluit aan als een **worker node** (Machine 2), en draagt zijn GPU-geheugen en rekenkracht bij.

> **Opmerking**: Ray is een optionele afhankelijkheid voor vLLM en is alleen beschikbaar vanuit de vooraf geconfigureerde Podman-container.

Bij het opstarten verdeelt vLLM het model over beide nodes met behulp van tensor-parallellisme. Zodra het is geladen, verloopt de inferentie alsof deze op één enkele accelerator draait.

### Stap 1: De Ray head node starten (Machine 1)

Start op Machine 1 de Ray head node om het cluster te initialiseren:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **`<MACHINE_1_IP>` vinden**: Voer op Machine 1 `hostname -I | awk '{print $1}'` uit om het lokale IP-adres te vinden.
### Stap 2: Sluit je aan bij de cluster (Machine 2)

Verbind Machine 2 met de hoofdnode om de cluster te vormen:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **`<MACHINE_2_IP>` vinden**: Voer op Machine 2 `hostname -I | awk '{print $1}'` uit om het lokale IP-adres te vinden.

### Stap 3: Serveer het model (Machine 1)

Start op Machine 1 de vLLM-server. Dit downloadt automatisch het model en begint het te serveren via beide nodes:

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
|------|------|
| `--port` | Poort waarop de HTTP-API wordt aangeboden |
| `--host` | IP-adres waaraan de server wordt gekoppeld (`0.0.0.0` voor alle interfaces) |
| `--max-model-len` | Maximale contextlengte in tokens |
| `--gpu-memory-utilization` | Fractie van het GPU-geheugen die wordt toegewezen (0.0–1.0) |
| `--dtype` | Gegevenstype voor modelgewichten |
| `--tensor-parallel-size` | Aantal GPU's waarover het model wordt verdeeld (stel in op het totale aantal GPU's in de cluster) |
| `--distributed-executor-backend` | Backend voor uitvoering op meerdere nodes (`ray` voor clusterimplementaties) |
| `--enforce-eager` | Schakelt CUDA-graphcompilatie uit voor compatibiliteit |
| `--language-model-only` | Slaat het laden van hulponderdelen van het model over (bijv. vision encoder) |
| `--reasoning-parser` | Schakelt gestructureerde parsing van redeneeruitvoer voor het model in |

Raadpleeg voor volledig gebruik van de parameters de [vLLM-documentatie](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Toegang tot het model

vLLM biedt een OpenAI-compatibele API, zodat je elke compatibele client of interface met je cluster kunt verbinden. Een populaire optie is [Open WebUI](https://github.com/open-webui/open-webui), dat een browsergebaseerde chatinterface biedt.

Om Open WebUI te verbinden met je vLLM-eindpunt:

1. Open **Settings** > **Admin Panel** > **Connections**
2. Klik op de **+** bij **Manage OpenAI API Connections**
3. Stel het **Connection Type** in op **External**
4. Stel de **URL** in op `http://<MACHINE_1_IP>:7000/v1`
5. Selecteer bij **Auth** de optie **None** in de vervolgkeuzelijst
6. Laat **Model IDs** leeg om automatisch alle modellen van het eindpunt te ontdekken

> **`<MACHINE_1_IP>` vinden**: Voer op Machine 1 `hostname -I | awk '{print $1}'` uit om het lokale IP-adres te vinden. Als je Open WebUI vanaf Machine 1 zelf benadert, kun je `http://localhost:7000/v1` gebruiken.

![Verbindingsinstellingen van Open WebUI voor het vLLM-eindpunt](assets/openwebui-connection.png)

Selecteer na het verbinden het model in de vervolgkeuzelijst van Open WebUI en begin te chatten. Het model draait nu op beide Ryzen AI Halo-nodes:

![Chatten met Qwen3.5-397B in Open WebUI](assets/openwebui-chat.png)

## Volgende stappen

- **Verken andere modellen**: Ontdek nieuwe modellen op [Hugging Face](https://huggingface.co/models?&sort=trending) die passen binnen het gecombineerde GPU-geheugen van je cluster
- **Opschalen naar vier nodes**: Voeg twee extra Ryzen AI Halo-systemen toe als extra Ray-workers om modellen over nog meer GPU's te verdelen. Hiervoor is een Ethernet-switch met minstens vier poorten nodig, één per node. Volg [Stap 2: Sluit je aan bij de cluster](#step-2-join-the-cluster-machine-2) op elke extra worker en verhoog `--tensor-parallel-size` dienovereenkomstig
- **Probeer andere parallellisatiestrategieën**: vLLM ondersteunt [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) voor mixture-of-experts-modellen en [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) voor hogere doorvoer. Experimenteer met `--enable-expert-parallel` en `--data-parallel-size` om de beste configuratie voor jouw workload te vinden