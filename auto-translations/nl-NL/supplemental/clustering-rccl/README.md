<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Twee Ryzen™ AI Halos clusteren met RCCL

## Overzicht

Uw Ryzen™ AI Halo is al in staat om grote taalmodellen lokaal uit te voeren. Clustering gaat een stap verder door het GPU-geheugen van meerdere systemen via een lokaal netwerk te combineren, waardoor u toegang krijgt tot nog grotere modellen met sterkere redeneervaardigheden, betere codegeneratie en dieper meertalig begrip — allemaal volledig op uw eigen hardware.

Deze playbook leert u hoe u twee Ryzen AI Halo-systemen kunt clusteren met behulp van RCCL (ROCm Communication Collectives Library) met vLLM, en hoe u Qwen3.5-397B, een model met 397 miljard parameters, over beide machines kunt uitvoeren met ROCm-versnelling.

## Wat u leert

- Hoe u de VRAM-toewijzing op Ryzen AI Halo-systemen uitbreidt
- vLLM starten met ROCm-ondersteuning
- RCCL configureren voor multi-node tensor-parallelle inferentie over twee Ryzen AI Halo-systemen
- Een model met 397 miljard parameters uitvoeren over twee via een netwerk verbonden Ryzen AI Halo-systemen

## Vereisten

### Hardware

Deze playbook vereist twee Ryzen AI Halo-eenheden en één Ethernet-switch, verbonden in een steropologie waarbij elke eenheid rechtstreeks op de switch is aangesloten.

| Component | Aantal | Beschrijving |
|-----------|--------|--------------|
| Ryzen AI Halo | 2 | Rekenknooppunten die het cluster vormen |
| 10Gbps Ethernet-switch | 1 | Centrale switch voor communicatie tussen meerdere Ryzen AI Halo-knooppunten (minimaal 2 poorten) |
| Ethernetkabel | 2 | Verbindt elke Halo-eenheid met de switch (Cat 7 of hoger aanbevolen) |

> **Opmerking**: Er zijn twee Ethernet-switchpoorten nodig om de twee Ryzen AI Halo-eenheden te verbinden. Een derde poort is vereist als u het model benadert vanaf een afzonderlijke clientmachine in plaats van vanaf een van de Halo-eenheden.

### Software
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fysieke hardware-installatie

> **Opmerking**: Voer deze stap uit op zowel Machine 1 als Machine 2.

Verbind elke Ryzen AI Halo-eenheid met de Ethernet-switch via een Cat 7-kabel (of hoger). Dit legt de 10Gbps-verbinding aan die wordt gebruikt voor snelle communicatie tussen de knooppunten.

### 1. Netwerkinterfaces bepalen

Zoek op elke machine de naam van de netwerkinterface en noteer deze (in de rest van de instructies wordt hiernaar verwezen als `IFNAME`). Voer het volgende uit:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Dit geeft de interfacenaam direct weer, bijvoorbeeld:

```bash
enp191s0
```

### 2. Netwerkverbindingssnelheden verifiëren

Bevestig dat de verbinding actief is en op volledige snelheid werkt door de snelheid van uw interface te controleren:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Opmerking**: Vervang `<IFNAME>` door de naam van de uitvoerinterface uit [1. Netwerkinterfaces bepalen](#1-determine-network-interfaces)

U zou een snelheid van `10000Mb/s` moeten zien:

```bash
	Speed: 10000Mb/s
```

> **Opmerking**: Als de snelheid lager is dan `10000Mb/s` of de verbinding niet tot stand komt, controleer dan de kabelverbinding en bevestig dat de switchpoort is ingesteld op 10Gbps. Sommige switches vereisen dat automatische onderhandeling wordt uitgeschakeld en de verbindingssnelheid handmatig wordt ingesteld; raadpleeg de documentatie van uw switch.

## VRAM-toewijzing uitbreiden

> **Opmerking**: Voer deze stap uit op zowel Machine 1 als Machine 2.

### Geheugenconfiguratie voor het uitvoeren van grote modellen

Op Linux maakt ROCm gebruik van een gedeelde systeemgeheugenpool, en deze pool is standaard geconfigureerd op de helft van het systeemgeheugen.

Dit bedrag kan worden verhoogd door de Translation Table Manager (TTM)-pagina-instelling van de kernel te wijzigen, met behulp van de volgende instructies. AMD raadt aan om het minimale toegewezen VRAM in het BIOS in te stellen (0,5 GB).

* Installeer het pipx-hulpprogramma en voeg het pad voor door pipx geïnstalleerde wheels toe aan het systeemzoekpad.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installeer het amd-debug-tools-wheel van PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Voer het amd-ttm-hulpprogramma uit om de huidige instellingen voor gedeeld geheugen op te vragen.
  ```bash
  amd-ttm
  ```

* Configureer de instellingen voor gedeeld geheugen opnieuw naar **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Start het systeem opnieuw op om de wijzigingen door te voeren.

## vLLM-containerinitialisatie

> **Opmerking**: Voer deze stap uit op zowel Machine 1 als Machine 2.

Uw Ryzen AI Halo wordt geleverd met vLLM verpakt in een vooraf gebouwde containerimage, die u uitvoert met Podman, een gratis en open source containertool.

### 1. De map voor het downloaden van modellen aanmaken

Wanneer u het Qwen3.5-397B-model in deze playbook serveert, zal vLLM de modelgewichten automatisch naar uw systeem downloaden. Om ervoor te zorgen dat die gewichten toegankelijk zijn vanuit de container, maakt u eerst een modellenmap aan die de container kan koppelen:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. De vLLM-container starten

De onderstaande opdracht start de container en brengt u in een interactieve shell. Het koppelt de modellenmap die u zojuist hebt aangemaakt en geeft uw `IFNAME` door aan `NCCL_SOCKET_IFNAME` en `GLOO_SOCKET_IFNAME`, waarmee RCCL (de bibliotheek die vLLM gebruikt om GPU's over het cluster te coördineren) wordt verteld welke interface gebruikt moet worden.

Start de container met:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Opmerking**: Vervang `<IFNAME>` door de naam van de uitvoerinterface uit [1. Netwerkinterfaces bepalen](#1-determine-network-interfaces)

## Het model uitvoeren op het cluster

vLLM gebruikt Ray om het cluster te orkestreren en RCCL om GPU-naar-GPU-communicatie tussen knooppunten af te handelen. Eén machine fungeert als het **hoofdknooppunt** (Machine 1) en coördineert de inferentie. De andere sluit aan als een **werkersknooppunt** (Machine 2) en draagt zijn GPU-geheugen en rekenkracht bij.

> **Opmerking**: Ray is een optionele afhankelijkheid voor vLLM en is alleen beschikbaar vanuit de vooraf geconfigureerde Podman-container.

Bij het opstarten verdeelt vLLM het model over beide knooppunten met behulp van tensorparallelisme. Zodra het model is geladen, verloopt de inferentie alsof het op één enkele versneller wordt uitgevoerd.

### Stap 1: Het Ray-hoofdknooppunt starten (Machine 1)

Start op Machine 1 het Ray-hoofdknooppunt om het cluster te initialiseren:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **`<MACHINE_1_IP>` vinden**: Voer op Machine 1 `hostname -I | awk '{print $1}'` uit om het lokale IP-adres te vinden.

### Stap 2: Deelnemen aan het cluster (Machine 2)

Maak op Machine 2 verbinding met het hoofdknooppunt om het cluster te vormen:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **`<MACHINE_2_IP>` vinden**: Voer op Machine 2 `hostname -I | awk '{print $1}'` uit om het lokale IP-adres te vinden.

### Stap 3: Het model serveren (Machine 1)

Start op Machine 1 de vLLM-server. Dit zal het model automatisch downloaden en beginnen het over beide knooppunten te serveren:

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

| Vlag | Doel |
|------|------|
| `--port` | Poort waarop de HTTP API wordt geserveerd |
| `--host` | IP-adres waaraan de server wordt gebonden (`0.0.0.0` voor alle interfaces) |
| `--max-model-len` | Maximale contextlengte in tokens |
| `--gpu-memory-utilization` | Fractie van het GPU-geheugen dat wordt toegewezen (0,0–1,0) |
| `--dtype` | Gegevenstype voor modelgewichten |
| `--tensor-parallel-size` | Aantal GPU's waarover het model wordt verdeeld (ingesteld op het totale aantal GPU's in het cluster) |
| `--distributed-executor-backend` | Backend voor uitvoering op meerdere knooppunten (`ray` voor clusterimplementaties) |
| `--enforce-eager` | Schakelt CUDA-grafiekcompilatie uit voor compatibiliteit |
| `--language-model-only` | Slaat het laden van hulpmodelcomponenten over (bijv. vision encoder) |
| `--reasoning-parser` | Schakelt gestructureerde redeneeruitvoerparsing in voor het model |

Raadpleeg de [vLLM-documentatie](https://docs.vllm.ai/en/latest/configuration/engine_args/) voor volledig parametergebruik.

## Toegang tot het model

vLLM biedt een OpenAI-compatibele API, zodat u elke compatibele client of interface op uw cluster kunt aansluiten. Een populaire optie is [Open WebUI](https://github.com/open-webui/open-webui), dat een browsergebaseerde chatinterface biedt.

Om Open WebUI te verbinden met uw vLLM-eindpunt:

1. Open **Instellingen** > **Beheerderspaneel** > **Verbindingen**
2. Klik op de **+** bij **OpenAI API-verbindingen beheren**
3. Stel het **Verbindingstype** in op **Extern**
4. Stel de **URL** in op `http://<MACHINE_1_IP>:7000/v1`
5. Selecteer onder **Auth** de optie **Geen** uit het vervolgkeuzemenu
6. Laat **Model-ID's** leeg om automatisch alle modellen van het eindpunt te ontdekken

> **`<MACHINE_1_IP>` vinden**: Voer op Machine 1 `hostname -I | awk '{print $1}'` uit om het lokale IP-adres te vinden. Als u Open WebUI benadert vanaf Machine 1 zelf, kunt u `http://localhost:7000/v1` gebruiken.

![Open WebUI-verbindingsinstellingen voor het vLLM-eindpunt](assets/openwebui-connection.png)

Zodra de verbinding is gemaakt, selecteert u het model in het modelvervolgkeuzemenu in Open WebUI en begint u te chatten. Het model wordt nu uitgevoerd over beide Ryzen AI Halo-knooppunten:

![Chatten met Qwen3.5-397B in Open WebUI](assets/openwebui-chat.png)

## Volgende stappen

- **Andere modellen verkennen**: Ontdek nieuwe modellen op [Hugging Face](https://huggingface.co/models?&sort=trending) die passen binnen het gecombineerde GPU-geheugen van uw cluster
- **Schalen naar vier knooppunten**: Voeg twee extra Ryzen AI Halo-systemen toe als aanvullende Ray-werkers om modellen over nog meer GPU's te verdelen. Dit vereist een Ethernet-switch met minimaal vier poorten, één voor elk knooppunt. Volg [Stap 2: Deelnemen aan het cluster](#step-2-join-the-cluster-machine-2) op elke extra werker en verhoog `--tensor-parallel-size` dienovereenkomstig
- **Andere parallelismestrategieën uitproberen**: vLLM ondersteunt [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) voor mixture-of-experts-modellen en [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) voor hogere doorvoer. Experimenteer met `--enable-expert-parallel` en `--data-parallel-size` om de beste configuratie voor uw workload te vinden