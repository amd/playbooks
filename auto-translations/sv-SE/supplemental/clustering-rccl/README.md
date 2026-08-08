<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinöversättning.** Den här sidan har automatiskt översatts från engelska och har inte granskats av en människa. Den kan innehålla fel, och vissa instruktioner, kommandon, nedladdningar, produkttillgänglighet eller annat innehåll kan variera beroende på språk eller region. Vid eventuella motsägelser eller avvikelser är det den ursprungliga engelska versionen av playbook som gäller och har företräde.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Klustring av två Ryzen™ AI Halo med RCCL

## Översikt

Din Ryzen™ AI Halo kan redan köra stora språkmodeller lokalt. Klustring tar detta ett steg längre genom att kombinera GPU-minnet från flera system över ett lokalt nätverk, vilket ger dig tillgång till ännu större modeller med starkare resonemang, bättre kodgenerering och djupare flerspråkig förståelse – helt på din egen hårdvara.

Denna spelbok lär dig hur du klustrar två Ryzen AI Halo-system med RCCL (ROCm Communication Collectives Library) tillsammans med vLLM och kör Qwen3.5-397B, en modell med 397 miljarder parametrar, över båda maskinerna med ROCm-acceleration.

## Vad du kommer att lära dig

- Hur du utökar VRAM-allokeringen på Ryzen AI Halo-system
- Att starta vLLM med ROCm-stöd
- Konfigurera RCCL för tensor-parallell inferens över flera noder mellan två Ryzen AI Halo-system
- Att köra en modell med 397 miljarder parametrar över två nätverksanslutna Ryzen AI Halo-system

## Förutsättningar

### Hårdvara

Denna spelbok kräver två Ryzen AI Halo-enheter och en Ethernet-switch, anslutna i en stjärntopologi där varje enhet är kopplad direkt till switchen.

| Komponent | Antal | Beskrivning |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Beräkningsnoder som utgör klustret |
| 10 Gbps Ethernet-switch | 1 | Central switch som möjliggör kommunikation mellan flera Ryzen AI Halo-noder (minst 2 portar) |
| Ethernet-kabel | 2 | Ansluter varje Halo-enhet till switchen (Cat 7 eller högre rekommenderas) |

> **Obs**: Två Ethernet-switchportar krävs för att ansluta de två Ryzen AI Halo-enheterna. En tredje port krävs om du kommer åt modellen från en separat klientmaskin istället för från en av Halo-enheterna.

### Programvara
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fysisk hårdvaruinstallation

> **Obs**: Slutför detta steg på både Maskin 1 och Maskin 2.

Anslut varje Ryzen AI Halo-enhet till Ethernet-switchen med en Cat 7-kabel (eller högre). Detta upprättar 10 Gbps-länken som används för höghastighetskommunikation mellan noderna.

### 1. Bestäm nätverksgränssnitt

På varje maskin, ta reda på namnet på dess nätverksgränssnitt och notera det (det kommer att kallas `IFNAME` i resten av instruktionerna). Kör:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Detta skriver ut gränssnittsnamnet direkt, till exempel:

```bash
enp191s0
```

### 2. Verifiera nätverkslänkens hastighet

Bekräfta att länken är aktiv och körs med full hastighet genom att kontrollera hastigheten för ditt gränssnitt:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Obs**: Ersätt `<IFNAME>` med utdatagränssnittsnamnet från [1. Bestäm nätverksgränssnitt](#1-determine-network-interfaces)

Du bör se en hastighet på `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Obs**: Om hastigheten är lägre än `10000Mb/s` eller länken inte kommer upp, kontrollera kabelanslutningen och bekräfta att switchporten är inställd på 10 Gbps. Vissa switchar kräver att auto-förhandling inaktiveras och att länkhastigheten ställs in manuellt; se din switch dokumentation.

## Utökning av VRAM-allokering

> **Obs**: Slutför detta steg på både Maskin 1 och Maskin 2.

### Minneskonfiguration för att köra stora modeller

På Linux använder ROCm en delad systemminnespool, och denna pool är som standard konfigurerad till hälften av systemminnet.

Denna mängd kan ökas genom att ändra kernelns Translation Table Manager (TTM)-sidinställning enligt följande instruktioner. AMD rekommenderar att ställa in det dedikerade minimum-VRAM i BIOS (0,5 GB).

* Installera pipx-verktyget och lägg till sökvägen för pipx-installerade wheels i systemets sökväg.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installera amd-debug-tools-wheelen från PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Kör amd-ttm-verktyget för att fråga efter de aktuella inställningarna för delat minne.
  ```bash
  amd-ttm
  ```

* Konfigurera om inställningarna för delat minne till **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Starta om systemet för att ändringarna ska träda i kraft.

## Initiering av vLLM-container

> **Obs**: Slutför detta steg på både Maskin 1 och Maskin 2.

Din Ryzen AI Halo levereras med vLLM paketerat inuti en förbyggd container-avbildning, som du kör med Podman, ett gratis och öppet källkodsverktyg för containrar.

### 1. Skapa katalogen för modellnedladdning

När du serverar Qwen3.5-397B-modellen i denna spelbok kommer vLLM automatiskt att ladda ner modellvikterna till ditt system. För att säkerställa att dessa vikter är åtkomliga inifrån containern, skapa först en modellkatalog som containern kan montera:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Starta vLLM-containern

Kommandot nedan startar containern och tar dig till ett interaktivt skal. Det monterar den modellkatalog du just skapade och skickar din `IFNAME` till `NCCL_SOCKET_IFNAME` och `GLOO_SOCKET_IFNAME`, vilket talar om för RCCL (biblioteket vLLM använder för att koordinera GPU:er över klustret) vilket gränssnitt som ska användas.

Starta containern med:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Obs**: Ersätt `<IFNAME>` med utdatagränssnittsnamnet från [1. Bestäm nätverksgränssnitt](#1-determine-network-interfaces)

## Att köra modellen på klustret

vLLM använder Ray för att orkestrera klustret och RCCL för att hantera GPU-till-GPU-kommunikation mellan noder. En maskin agerar som **huvudnod** (Maskin 1), som koordinerar inferensen. Den andra ansluter som en **arbetarnod** (Maskin 2) och bidrar med sitt GPU-minne och sin beräkningskraft.

> **Obs**: Ray är en valfri beroende för vLLM och är endast tillgängligt inifrån den förkonfigurerade Podman-containern.

Vid start delar vLLM upp modellen mellan båda noderna med hjälp av tensor-parallellism. När den väl är laddad fortsätter inferensen som om den kördes på en enda accelerator.

### Steg 1: Starta Ray-huvudnoden (Maskin 1)

På Maskin 1, starta Ray-huvudnoden för att initiera klustret:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Hitta `<MACHINE_1_IP>`**: På Maskin 1, kör `hostname -I | awk '{print $1}'` för att hitta dess lokala IP-adress.
### Steg 2: Anslut till klustret (Maskin 2)

På Maskin 2, anslut till huvudnoden för att bilda klustret:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Hitta `<MACHINE_2_IP>`**: Kör `hostname -I | awk '{print $1}'` på Maskin 2 för att hitta dess lokala IP-adress.

### Steg 3: Servera modellen (Maskin 1)

På Maskin 1, starta vLLM-servern. Detta laddar automatiskt ner modellen och börjar servera den över båda noderna:

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

#### Parameterreferens

| Flagga | Syfte |
|------|---------|
| `--port` | Port att servera HTTP-API:et på |
| `--host` | IP-adress att binda servern till (`0.0.0.0` för alla gränssnitt) |
| `--max-model-len` | Maximal kontextlängd i tokens |
| `--gpu-memory-utilization` | Andel GPU-minne att allokera (0.0–1.0) |
| `--dtype` | Datatyp för modellvikter |
| `--tensor-parallel-size` | Antal GPU:er att dela upp modellen över (ställ in på totalt antal GPU:er i klustret) |
| `--distributed-executor-backend` | Backend för exekvering över flera noder (`ray` för klusterdistributioner) |
| `--enforce-eager` | Inaktiverar CUDA-graf-kompilering för kompatibilitet |
| `--language-model-only` | Hoppar över laddning av hjälpkomponenter till modellen (t.ex. synkodare) |
| `--reasoning-parser` | Aktiverar strukturerad tolkning av resoneringsutdata för modellen |

För fullständig parameteranvändning, se [vLLM-dokumentationen](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Åtkomst till modellen

vLLM exponerar ett OpenAI-kompatibelt API, så du kan ansluta valfri kompatibel klient eller ett kompatibelt gränssnitt till ditt kluster. Ett populärt alternativ är [Open WebUI](https://github.com/open-webui/open-webui), som erbjuder ett webbläsarbaserat chattgränssnitt.

För att ansluta Open WebUI till din vLLM-slutpunkt:

1. Öppna **Settings** > **Admin Panel** > **Connections**
2. Klicka på **+** vid **Manage OpenAI API Connections**
3. Ställ in **Connection Type** till **External**
4. Ställ in **URL** till `http://<MACHINE_1_IP>:7000/v1`
5. Under **Auth**, välj **None** i listan
6. Lämna **Model IDs** tomt för att automatiskt upptäcka alla modeller från slutpunkten

> **Hitta `<MACHINE_1_IP>`**: Kör `hostname -I | awk '{print $1}'` på Maskin 1 för att hitta dess lokala IP-adress. Om du kommer åt Open WebUI från Maskin 1 själv kan du använda `http://localhost:7000/v1`.

![Open WebUI-anslutningsinställningar för vLLM-slutpunkten](assets/openwebui-connection.png)

När anslutningen är upprättad väljer du modellen från modellrullgardinsmenyn i Open WebUI och börjar chatta. Modellen körs nu över båda dina Ryzen AI Halo-noder:

![Chattar med Qwen3.5-397B i Open WebUI](assets/openwebui-chat.png)

## Nästa steg

- **Utforska andra modeller**: Upptäck nya modeller på [Hugging Face](https://huggingface.co/models?&sort=trending) som ryms inom ditt klusters sammanlagda GPU-minne
- **Skala upp till fyra noder**: Lägg till två ytterligare Ryzen AI Halo-system som ytterligare Ray-arbetare för att dela upp modeller över ännu fler GPU:er. Detta kräver en Ethernet-switch med minst fyra portar, en för varje nod. Följ [Steg 2: Anslut till klustret](#step-2-join-the-cluster-machine-2) på varje ytterligare arbetare och öka `--tensor-parallel-size` i enlighet med detta
- **Prova andra parallelliseringsstrategier**: vLLM stöder [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) för mixture-of-experts-modeller och [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) för högre genomströmning. Experimentera med `--enable-expert-parallel` och `--data-parallel-size` för att hitta den bästa konfigurationen för din arbetsbelastning