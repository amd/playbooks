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

# Een cluster van vier Ryzen™ AI Halo-systemen bouwen met RCCL

## Overzicht

Uw Ryzen™ AI Halo is al in staat om grote taalmodellen lokaal uit te voeren. Clustering gaat hier nog een stap verder door het GPU-geheugen van meerdere systemen via een lokaal netwerk te combineren, waardoor u toegang krijgt tot nog grotere modellen met sterker redeneervermogen, betere codegeneratie en dieper meertalig begrip, volledig op uw eigen hardware.

Dit draaiboek leert u hoe u vier Ryzen AI Halo-systemen clustert met RCCL (ROCm Communication Collectives Library) in combinatie met vLLM, en hoe u Qwen3.5-397B, een model met 397 miljard parameters, uitvoert over alle vier de machines met ROCm-versnelling.

## Wat u gaat leren

- Hoe u de VRAM-toewijzing op Ryzen AI Halo-systemen uitbreidt
- Het starten van vLLM met ROCm-ondersteuning
- Het configureren van RCCL voor multi-node tensor-parallelle inferentie over vier Ryzen AI Halo-systemen
- Het uitvoeren van een model met 397 miljard parameters over vier genetwerkte Ryzen AI Halo-systemen

## Vereisten

### Hardware

Voor dit draaiboek zijn vier Ryzen AI Halo-eenheden en één Ethernet-switch vereist, verbonden in een stertopologie waarbij elke eenheid rechtstreeks met de switch is bekabeld.

| Onderdeel | Aantal | Beschrijving |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Reken-nodes die het cluster vormen |
| 10Gbps Ethernet-switch | 1 | Centrale switch die communicatie tussen meerdere Ryzen AI Halo-nodes mogelijk maakt (minimaal 4 poorten) |
| Ethernet-kabel | 4 | Verbindt elke Halo-eenheid met de switch (Cat 7 of hoger aanbevolen) |

> **Opmerking**: Er zijn vier Ethernet-switchpoorten nodig om de vier Ryzen AI Halo-eenheden aan te sluiten. Een vijfde poort is nodig als u het model vanaf een afzonderlijke clientmachine benadert in plaats van vanaf een van de Halo-eenheden.

### Software
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fysieke hardware-installatie

> **Opmerking**: Voer deze stap uit op alle vier de machines (Machine 1 tot en met Machine 4).

Verbind elke Ryzen AI Halo-eenheid met de Ethernet-switch met behulp van een Cat 7-kabel (of hoger). Dit zorgt voor de 10Gbps-verbinding die wordt gebruikt voor snelle communicatie tussen de nodes.

### 1. Netwerkinterfaces bepalen

Zoek op elke machine de naam van de netwerkinterface en noteer deze (in de rest van de instructies wordt hiernaar verwezen als `IFNAME`). Voer uit:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Dit toont direct de naam van de interface, bijvoorbeeld:

```bash
enp191s0
```

### 2. Netwerklinksnelheden controleren

Controleer of de verbinding actief is en op volle snelheid draait door de snelheid van uw interface te controleren:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Opmerking**: Vervang `<IFNAME>` door de uitvoernaam van de interface uit [1. Netwerkinterfaces bepalen](#1-determine-network-interfaces)

U zou een snelheid van `10000Mb/s` moeten zien:

```bash
	Speed: 10000Mb/s
```

> **Opmerking**: Als de snelheid lager is dan `10000Mb/s` of de verbinding niet tot stand komt, controleer dan de kabelverbinding en bevestig dat de switchpoort is ingesteld op 10Gbps. Sommige switches vereisen dat auto-onderhandeling wordt uitgeschakeld en de linksnelheid handmatig wordt ingesteld; raadpleeg de documentatie van uw switch.

## VRAM-toewijzing uitbreiden

> **Opmerking**: Voer deze stap uit op alle vier de machines (Machine 1 tot en met Machine 4).

### Geheugenconfiguratie voor het uitvoeren van grote modellen

Op Linux maakt ROCm gebruik van een gedeelde systeemgeheugenpool, en deze pool is standaard geconfigureerd op de helft van het systeemgeheugen.

Deze hoeveelheid kan worden verhoogd door de pagina-instelling van de Translation Table Manager (TTM) van de kernel te wijzigen, aan de hand van de onderstaande instructies. AMD raadt aan om de minimale toegewezen VRAM in de BIOS in te stellen (0,5 GB).

* Installeer het pipx-hulpprogramma en voeg het pad voor door pipx geïnstalleerde wheels toe aan het systeemzoekpad.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installeer de amd-debug-tools wheel vanuit PyPI.
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

> **Opmerking**: Voer deze stap uit op alle vier de machines (Machine 1 tot en met Machine 4).

Uw Ryzen AI Halo wordt geleverd met vLLM verpakt in een vooraf gebouwde container-image, die u uitvoert met Podman, een gratis en open source containertool.

### 1. Maak de map voor het downloaden van modellen aan

Wanneer u het Qwen3.5-397B-model in dit draaiboek host, zal vLLM automatisch de modelgewichten naar uw systeem downloaden. Om ervoor te zorgen dat die gewichten vanuit de container toegankelijk zijn, maakt u eerst een models-map aan die door de container kan worden gekoppeld:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Start de vLLM-container

Met het onderstaande commando start u de container en komt u in een interactieve shell terecht. Hierbij wordt de zojuist aangemaakte models-map gekoppeld en wordt uw `IFNAME` doorgegeven aan `NCCL_SOCKET_IFNAME` en `GLOO_SOCKET_IFNAME`, waarmee aan RCCL (de bibliotheek die vLLM gebruikt om GPU's over het cluster te coördineren) wordt doorgegeven welke interface moet worden gebruikt.

Start de container met:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Opmerking**: Vervang `<IFNAME>` door de uitvoernaam van de interface uit [1. Netwerkinterfaces bepalen](#1-determine-network-interfaces)

## Het model uitvoeren op het cluster

vLLM gebruikt Ray om het cluster te orkestreren en RCCL om GPU-naar-GPU-communicatie tussen nodes af te handelen. Eén machine fungeert als de head node (Machine 1) en coördineert de inferentie. De andere drie sluiten aan als worker-nodes (Machines 2, 3 en 4) en dragen hun GPU-geheugen en rekenkracht bij.

> **Opmerking**: Ray is een optionele afhankelijkheid voor vLLM en is alleen beschikbaar vanuit de vooraf geconfigureerde Podman-container.

Bij het opstarten verdeelt vLLM het model over alle vier de nodes met behulp van tensor-parallellisme. Eenmaal geladen, verloopt de inferentie alsof deze op één enkele accelerator wordt uitgevoerd.

#### Ray OOM-fouten voorkomen

Standaard monitort Ray het hostgeheugen op elke node en beëindigt het het grootste proces wanneer het geheugengebruik boven 95% komt. Op uw Ryzen™ AI Halo delen de GPU en de host één geheugenpool, waardoor het laden van een model een `ray.exceptions.OutOfMemoryError` kan veroorzaken en het worker-proces kan beëindigen.

Om dit te voorkomen, exporteren we `RAY_memory_monitor_refresh_ms=0` op elke machine voordat we het cluster starten en eraan deelnemen.
### Stap 1: Start de Ray Head Node (Machine 1)

Start op Machine 1 de Ray head node om het cluster te initialiseren:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **`<MACHINE_1_IP>` vinden**: Voer op Machine 1 `hostname -I | awk '{print $1}'` uit om het lokale IP-adres te vinden.

### Stap 2: Sluit je aan bij het cluster (Machines 2, 3 en 4)

Maak op elk van Machines 2, 3 en 4 verbinding met de head node om het cluster te vormen:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_N_IP> --num-gpus=1
```

> **`<MACHINE_N_IP>` vinden**: Voer op elke workermachine `hostname -I | awk '{print $1}'` uit om het lokale IP-adres te vinden.

### Stap 3: Het model serveren (Machine 1)

Start op Machine 1 de vLLM-server. Dit zal automatisch het model downloaden en beginnen het te serveren op alle vier de nodes:

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

#### Parameteroverzicht

| Vlag | Doel |
|------|---------|
| `--port` | Poort waarop de HTTP-API wordt geserveerd |
| `--host` | IP-adres waaraan de server wordt gekoppeld (`0.0.0.0` voor alle interfaces) |
| `--max-model-len` | Maximale contextlengte in tokens |
| `--gpu-memory-utilization` | Fractie van het GPU-geheugen dat wordt toegewezen (0.0–1.0) |
| `--dtype` | Gegevenstype voor modelgewichten |
| `--tensor-parallel-size` | Aantal GPU's waarover het model wordt verdeeld (stel dit in op het totale aantal GPU's in het cluster) |
| `--distributed-executor-backend` | Backend voor multi-node uitvoering (`ray` voor clusterimplementaties) |
| `--enforce-eager` | Schakelt CUDA-graphcompilatie uit voor compatibiliteit |
| `--language-model-only` | Slaat het laden van hulpcomponenten van het model over (bijv. visuele encoder) |
| `--reasoning-parser` | Schakelt gestructureerde reasoning-outputparsing in voor het model |

Raadpleeg voor volledig gebruik van de parameters de [vLLM-documentatie](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Toegang krijgen tot het model

vLLM biedt een OpenAI-compatibele API, zodat je elke compatibele client of interface met je cluster kunt verbinden. Een populaire optie is [Open WebUI](https://github.com/open-webui/open-webui), dat een browsergebaseerde chatinterface biedt.

Zo verbind je Open WebUI met je vLLM-eindpunt:

1. Open **Instellingen** > **Beheerderspaneel** > **Verbindingen**
2. Klik op de **+** bij **OpenAI API-verbindingen beheren**
3. Stel het **Verbindingstype** in op **Extern**
4. Stel de **URL** in op `http://<MACHINE_1_IP>:7000/v1`
5. Selecteer bij **Auth** de optie **Geen** in de vervolgkeuzelijst
6. Laat **Model-ID's** leeg om automatisch alle modellen vanaf het eindpunt te detecteren

> **`<MACHINE_1_IP>` vinden**: Voer op Machine 1 `hostname -I | awk '{print $1}'` uit om het lokale IP-adres te vinden. Als je Open WebUI vanaf Machine 1 zelf benadert, kun je `http://localhost:7000/v1` gebruiken.

![Open WebUI-verbindingsinstellingen voor het vLLM-eindpunt](assets/openwebui-connection.png)

Zodra je verbonden bent, selecteer je het model in de vervolgkeuzelijst met modellen in Open WebUI en kun je beginnen met chatten. Het model draait nu op alle vier je Ryzen AI Halo-nodes:

![Chatten met Qwen3.5-397B in Open WebUI](assets/openwebui-chat.png)

## Volgende stappen

- **Ontdek andere modellen**: Verken nieuwe modellen op [Hugging Face](https://huggingface.co/models?&sort=trending) die binnen het gecombineerde GPU-geheugen van je cluster passen
- **Schaal verder dan vier nodes**: Voeg extra Ryzen AI Halo-systemen toe als aanvullende Ray-workers om modellen over nog meer GPU's te verdelen. Volg [Stap 2: Sluit je aan bij het cluster](#step-2-join-the-cluster-machines-2-3-and-4) op elke extra worker en verhoog `--tensor-parallel-size` dienovereenkomstig
- **Probeer andere parallellisatiestrategieën**: vLLM ondersteunt [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) voor mixture-of-experts-modellen en [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) voor hogere doorvoer. Experimenteer met `--enable-expert-parallel` en `--data-parallel-size` om de beste configuratie voor jouw workload te vinden