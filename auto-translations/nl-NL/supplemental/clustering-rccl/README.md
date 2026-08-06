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

Uw Ryzen™ AI Halo is al in staat om lokaal grote taalmodellen uit te voeren. Clustering gaat hierin nog verder door het GPU-geheugen van meerdere systemen via een lokaal netwerk te combineren, waardoor u toegang krijgt tot nog grotere modellen met sterkere redenering, betere codegeneratie en dieper meertalig begrip, volledig op uw eigen hardware.

Deze playbook leert u hoe u twee Ryzen AI Halo-systemen clustert met RCCL (ROCm Communication Collectives Library) met vLLM en hoe u Qwen3.5-397B, een model met 397 miljard parameters, op beide machines uitvoert met ROCm-acceleratie.

## Wat u leert

- Hoe u de VRAM-toewijzing op Ryzen AI Halo-systemen uitbreidt
- vLLM starten met ROCm-ondersteuning
- RCCL configureren voor multi-node tensor-parallelle inferentie tussen twee Ryzen AI Halo-systemen
- Een model met 397 miljard parameters uitvoeren op twee Ryzen AI Halo-systemen in een netwerk

## Vereisten

### Hardware

Voor deze playbook zijn twee Ryzen AI Halo-eenheden en één Ethernet-switch nodig, aangesloten in een stertopologie waarbij elke eenheid rechtstreeks met de switch is verbonden.

| Onderdeel | Aantal | Beschrijving |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Compute-nodes die het cluster vormen |
| 10Gbps Ethernet-switch | 1 | Centrale switch om communicatie tussen meerdere Ryzen AI Halo-nodes mogelijk te maken (minimaal 2 poorten) |
| Ethernetkabel | 2 | Verbindt elke Halo-eenheid met de switch (Cat 7 of hoger aanbevolen) |

> **Opmerking**: Er zijn twee Ethernet-switchpoorten nodig om de twee Ryzen AI Halo-eenheden te verbinden. Een derde poort is nodig als u het model benadert vanaf een aparte clientmachine in plaats van vanaf een van de Halo-eenheden.

### Software
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fysieke hardware-installatie

> **Opmerking**: Voer deze stap uit op zowel Machine 1 als Machine 2.

Verbind elke Ryzen AI Halo-eenheid met de Ethernet-switch met een Cat 7-kabel (of hoger). Dit realiseert de 10Gbps-verbinding die wordt gebruikt voor snelle communicatie tussen de nodes.

### 1. Netwerkinterfaces bepalen

Zoek op elke machine de naam van de netwerkinterface en noteer deze (deze wordt in de rest van de instructies aangeduid als `IFNAME`). Voer uit:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Dit toont de naam van de interface direct, bijvoorbeeld:

```bash
enp191s0
```

### 2. Netwerklinksnelheden controleren

Controleer of de verbinding actief is en op volle snelheid draait door de snelheid van uw interface te controleren:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Opmerking**: Vervang `<IFNAME>` door de naam van de uitvoerinterface uit [1. Netwerkinterfaces bepalen](#1-determine-network-interfaces)

U zou een snelheid van `10000Mb/s` moeten zien:

```bash
	Speed: 10000Mb/s
```

> **Opmerking**: Als de snelheid lager is dan `10000Mb/s` of de verbinding niet tot stand komt, controleer dan de kabelaansluiting en bevestig dat de switchpoort is ingesteld op 10Gbps. Sommige switches vereisen dat auto-onderhandeling wordt uitgeschakeld en de linksnelheid handmatig wordt ingesteld; raadpleeg de documentatie van uw switch.

## VRAM-toewijzing uitbreiden

> **Opmerking**: Voer deze stap uit op zowel Machine 1 als Machine 2.

### Geheugenconfiguratie voor het uitvoeren van grote modellen

Op Linux maakt ROCm gebruik van een gedeelde systeemgeheugenpool, en deze pool is standaard geconfigureerd op de helft van het systeemgeheugen.

Deze hoeveelheid kan worden verhoogd door de pagina-instelling van de Translation Table Manager (TTM) van de kernel te wijzigen, volgens de onderstaande instructies. AMD raadt aan om het minimale toegewezen VRAM in te stellen in de BIOS (0,5 GB).

* Installeer de pipx-tool en voeg het pad voor door pipx geïnstalleerde wheels toe aan het zoekpad van het systeem.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installeer de amd-debug-tools wheel vanaf PyPI.
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

## Initialisatie van de vLLM-container

> **Opmerking**: Voer deze stap uit op zowel Machine 1 als Machine 2.

Uw Ryzen AI Halo wordt geleverd met vLLM verpakt in een vooraf gebouwde container-image, die u uitvoert met Podman, een gratis en open source containertool.

### 1. De downloadmap voor het model aanmaken

Wanneer u het Qwen3.5-397B-model in deze playbook serveert, zal vLLM automatisch de modelgewichten naar uw systeem downloaden. Om ervoor te zorgen dat deze gewichten toegankelijk zijn vanuit de container, maakt u eerst een modellenmap aan die de container kan koppelen (mounten):

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. De vLLM-container starten

Met de onderstaande opdracht start u de container en komt u in een interactieve shell terecht. Deze koppelt de zojuist aangemaakte modellenmap en geeft uw `IFNAME` door aan `NCCL_SOCKET_IFNAME` en `GLOO_SOCKET_IFNAME`, waarmee aan RCCL (de bibliotheek die vLLM gebruikt om GPU's binnen het cluster te coördineren) wordt aangegeven welke interface moet worden gebruikt.

Start de container met:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Opmerking**: Vervang `<IFNAME>` door de naam van de uitvoerinterface uit [1. Netwerkinterfaces bepalen](#1-determine-network-interfaces)

## Het model uitvoeren op het cluster

vLLM gebruikt Ray om het cluster te orkestreren en RCCL om GPU-naar-GPU-communicatie tussen nodes af te handelen. Eén machine fungeert als de **head node** (Machine 1), die de inferentie coördineert. De andere sluit aan als **worker node** (Machine 2) en levert zijn GPU-geheugen en rekenkracht.

> **Opmerking**: Ray is een optionele afhankelijkheid voor vLLM en is alleen beschikbaar binnen de vooraf geconfigureerde Podman-container.

Bij het opstarten verdeelt vLLM het model over beide nodes met behulp van tensor-parallellisme. Zodra het geladen is, verloopt de inferentie alsof deze op één enkele accelerator draait.

### Stap 1: De Ray-head node starten (Machine 1)

Start op Machine 1 de Ray-head node om het cluster te initialiseren:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **`<MACHINE_1_IP>` vinden**: Voer op Machine 1 `hostname -I | awk '{print $1}'` uit om het lokale IP-adres te vinden.
### Stap 2: Sluit u aan bij de cluster (Machine 2)

Verbind op Machine 2 met de hoofdnode om de cluster te vormen:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **`<MACHINE_2_IP>` vinden**: voer op Machine 2 `hostname -I | awk '{print $1}'` uit om het lokale IP-adres te vinden.

### Stap 3: Serveer het model (Machine 1)

Start op Machine 1 de vLLM-server. Dit downloadt automatisch het model en begint het te serveren over beide nodes:

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

#### Parameterreferentie

| Flag | Doel |
|------|---------|
| `--port` | Poort waarop de HTTP-API wordt aangeboden |
| `--host` | IP-adres waaraan de server wordt gekoppeld (`0.0.0.0` voor alle interfaces) |
| `--max-model-len` | Maximale contextlengte in tokens |
| `--gpu-memory-utilization` | Fractie van het GPU-geheugen dat wordt toegewezen (0.0–1.0) |
| `--dtype` | Datatype voor modelgewichten |
| `--tensor-parallel-size` | Aantal GPU's waarover het model wordt versplinterd (instellen op het totale aantal GPU's in de cluster) |
| `--distributed-executor-backend` | Backend voor uitvoering op meerdere nodes (`ray` voor clusterimplementaties) |
| `--enforce-eager` | Schakelt CUDA-graafcompilatie uit voor compatibiliteit |
| `--language-model-only` | Slaat het laden van hulpcomponenten van het model over (bijv. visie-encoder) |
| `--reasoning-parser` | Schakelt gestructureerde parsing van redeneeruitvoer voor het model in |

Raadpleeg voor volledig gebruik van de parameters de [vLLM-documentatie](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Toegang tot het model

vLLM biedt een OpenAI-compatibele API, zodat u elke compatibele client of interface met uw cluster kunt verbinden. Een populaire optie is [Open WebUI](https://github.com/open-webui/open-webui), dat een browsergebaseerde chatinterface biedt.

Zo verbindt u Open WebUI met uw vLLM-eindpunt:

1. Open **Settings** > **Admin Panel** > **Connections**
2. Klik op de **+** bij **Manage OpenAI API Connections**
3. Stel het **Connection Type** in op **External**
4. Stel de **URL** in op `http://<MACHINE_1_IP>:7000/v1`
5. Selecteer bij **Auth** **None** in de vervolgkeuzelijst
6. Laat **Model IDs** leeg om automatisch alle modellen van het eindpunt te ontdekken

> **`<MACHINE_1_IP>` vinden**: voer op Machine 1 `hostname -I | awk '{print $1}'` uit om het lokale IP-adres te vinden. Als u Open WebUI vanaf Machine 1 zelf benadert, kunt u `http://localhost:7000/v1` gebruiken.

![Verbindingsinstellingen van Open WebUI voor het vLLM-eindpunt](assets/openwebui-connection.png)

Selecteer na het verbinden het model in de vervolgkeuzelijst met modellen in Open WebUI en begin te chatten. Het model draait nu over beide van uw Ryzen AI Halo-nodes:

![Chatten met Qwen3.5-397B in Open WebUI](assets/openwebui-chat.png)

## Volgende stappen

- **Verken andere modellen**: ontdek nieuwe modellen op [Hugging Face](https://huggingface.co/models?&sort=trending) die passen binnen het gecombineerde GPU-geheugen van uw cluster
- **Schaal naar vier nodes**: voeg twee extra Ryzen AI Halo-systemen toe als aanvullende Ray-workers om modellen over nog meer GPU's te versplinteren. Hiervoor is een Ethernet-switch met ten minste vier poorten nodig, één per node. Volg [Stap 2: Sluit u aan bij de cluster](#step-2-join-the-cluster-machine-2) op elke extra worker en verhoog `--tensor-parallel-size` dienovereenkomstig
- **Probeer andere parallellisatiestrategieën**: vLLM ondersteunt [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) voor mixture-of-experts-modellen en [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) voor hogere doorvoer. Experimenteer met `--enable-expert-parallel` en `--data-parallel-size` om de beste configuratie voor uw workload te vinden