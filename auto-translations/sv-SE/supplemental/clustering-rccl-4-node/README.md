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

# Klustring av fyra Ryzen™ AI Halo med RCCL

## Översikt

Din Ryzen™ AI Halo kan redan köra stora språkmodeller lokalt. Klustring tar detta ett steg längre genom att kombinera GPU-minnet från flera system över ett lokalt nätverk, vilket ger dig tillgång till ännu större modeller med starkare resonemangsförmåga, bättre kodgenerering och djupare flerspråklig förståelse – helt och hållet på din egen hårdvara.

Den här playbooken lär dig hur du klustrar fyra Ryzen AI Halo-system med RCCL (ROCm Communication Collectives Library) tillsammans med vLLM och kör Qwen3.5-397B, en modell med 397 miljarder parametrar, över alla fyra maskinerna med ROCm-acceleration.

## Vad du kommer att lära dig

- Hur du utökar VRAM-tilldelningen på Ryzen AI Halo-system
- Att starta vLLM med ROCm-stöd
- Konfigurering av RCCL för multinod-tensorparallell inferens över fyra Ryzen AI Halo-system
- Att köra en modell med 397 miljarder parametrar över fyra nätverksanslutna Ryzen AI Halo-system

## Förutsättningar

### Hårdvara

Den här playbooken kräver fyra Ryzen AI Halo-enheter och en Ethernet-switch, anslutna i en stjärntopologi där varje enhet är kopplad direkt till switchen.

| Komponent | Antal | Beskrivning |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Beräkningsnoder som bildar klustret |
| 10 Gbps Ethernet-switch | 1 | Central switch för att möjliggöra kommunikation mellan flera Ryzen AI Halo-noder (minst 4 portar) |
| Ethernet-kabel | 4 | Ansluter varje Halo-enhet till switchen (Cat 7 eller högre rekommenderas) |

> **Obs**: Fyra portar på Ethernet-switchen krävs för att ansluta de fyra Ryzen AI Halo-enheterna. En femte port krävs om du kommer åt modellen från en separat klientmaskin istället för från en av Halo-enheterna.

### Programvara
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fysisk hårdvaruinstallation

> **Obs**: Slutför detta steg på alla fyra maskinerna (Maskin 1 till Maskin 4).

Anslut varje Ryzen AI Halo-enhet till Ethernet-switchen med en Cat 7-kabel (eller högre). Detta upprättar 10 Gbps-länken som används för höghastighetskommunikation mellan noderna.

### 1. Bestäm nätverksgränssnitt

Hitta på varje maskin namnet på dess nätverksgränssnitt och anteckna det (det kommer att hänvisas till i resten av instruktionerna som `IFNAME`). Kör:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Detta skriver ut gränssnittsnamnet direkt, till exempel:

```bash
enp191s0
```

### 2. Verifiera nätverkets länkhastigheter

Bekräfta att länken är aktiv och körs med full hastighet genom att kontrollera hastigheten för ditt gränssnitt:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Obs**: Ersätt `<IFNAME>` med gränssnittsnamnet från utdata i [1. Bestäm nätverksgränssnitt](#1-determine-network-interfaces)

Du bör se en hastighet på `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Obs**: Om hastigheten är lägre än `10000Mb/s` eller länken inte kommer upp, kontrollera kabelanslutningen och bekräfta att switchporten är inställd på 10 Gbps. Vissa switchar kräver att auto-förhandling inaktiveras och att länkhastigheten anges manuellt; se dokumentationen för din switch.

## Utökning av VRAM-tilldelning

> **Obs**: Slutför detta steg på alla fyra maskinerna (Maskin 1 till Maskin 4).

### Minneskonfiguration för att köra stora modeller

På Linux använder ROCm en delad systemminnespool, och denna pool är som standard konfigurerad till hälften av systemminnet.

Denna mängd kan ökas genom att ändra kärnans TTM-sidinställning (Translation Table Manager), enligt följande instruktioner. AMD rekommenderar att ange det minsta dedikerade VRAM-värdet i BIOS (0,5 GB).

* Installera pipx-verktyget och lägg till sökvägen för pipx-installerade wheels i systemets sökväg.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installera amd-debug-tools wheel från PyPI.
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

* Starta om systemet för att ändringarna ska börja gälla.

## Initiering av vLLM-containern

> **Obs**: Slutför detta steg på alla fyra maskinerna (Maskin 1 till Maskin 4).

Din Ryzen AI Halo levereras med vLLM paketerat i en förbyggd containeravbild, som du kör med Podman, ett gratis containerverktyg med öppen källkod.

### 1. Skapa katalogen för modellnedladdning

När du serverar Qwen3.5-397B-modellen i den här playbooken kommer vLLM automatiskt att ladda ner modellvikterna till ditt system. För att säkerställa att dessa vikter är åtkomliga inifrån containern, skapa först en models-katalog som containern kan monteras mot:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Starta vLLM-containern

Kommandot nedan startar containern och tar dig till ett interaktivt skal. Det monterar models-katalogen du precis skapade och skickar din `IFNAME` till `NCCL_SOCKET_IFNAME` och `GLOO_SOCKET_IFNAME`, vilket talar om för RCCL (biblioteket vLLM använder för att koordinera GPU:er i klustret) vilket gränssnitt som ska användas.

Starta containern med:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Obs**: Ersätt `<IFNAME>` med gränssnittsnamnet från utdata i [1. Bestäm nätverksgränssnitt](#1-determine-network-interfaces)

## Köra modellen på klustret

vLLM använder Ray för att orkestrera klustret och RCCL för att hantera GPU-till-GPU-kommunikation mellan noderna. En maskin fungerar som huvudnod (Maskin 1) och koordinerar inferensen. De tre andra ansluter som arbetarnoder (Maskin 2, 3 och 4) och bidrar med sitt GPU-minne och sin beräkningskapacitet.

> **Obs**: Ray är ett valfritt beroende för vLLM och är endast tillgängligt inifrån den förkonfigurerade Podman-containern.

Vid start delar vLLM upp modellen över alla fyra noderna med hjälp av tensorparallellism. Efter inläsning fortsätter inferensen som om den kördes på en enda accelerator.

#### Förhindra Ray OOM-fel

Som standard övervakar Ray värdminnet på varje nod och avslutar den största processen när minnesanvändningen överstiger 95 %. På din Ryzen™ AI Halo delar GPU:n och värden en gemensam minnespool, så inläsning av en modell kan utlösa ett `ray.exceptions.OutOfMemoryError` och avsluta arbetarprocessen.

För att förhindra detta exporterar vi `RAY_memory_monitor_refresh_ms=0` på varje maskin innan klustret startas och ansluts till.
### Steg 1: Starta Ray-huvudnoden (Maskin 1)

På Maskin 1, starta Ray-huvudnoden för att initiera klustret:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Hitta `<MACHINE_1_IP>`**: Kör `hostname -I | awk '{print $1}'` på Maskin 1 för att hitta dess lokala IP-adress.

### Steg 2: Anslut till klustret (Maskin 2, 3 och 4)

På var och en av Maskin 2, 3 och 4, anslut till huvudnoden för att bilda klustret:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_N_IP> --num-gpus=1
```

> **Hitta `<MACHINE_N_IP>`**: Kör `hostname -I | awk '{print $1}'` på varje arbetsmaskin för att hitta dess lokala IP-adress.

### Steg 3: Servera modellen (Maskin 1)

På Maskin 1, starta vLLM-servern. Detta kommer automatiskt att ladda ner modellen och börja servera den på alla fyra noder:

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

#### Parameterreferens

| Flagga | Syfte |
|------|---------|
| `--port` | Port att servera HTTP-API:et på |
| `--host` | IP-adress att binda servern till (`0.0.0.0` för alla gränssnitt) |
| `--max-model-len` | Maximal kontextlängd i token |
| `--gpu-memory-utilization` | Andel GPU-minne att allokera (0.0–1.0) |
| `--dtype` | Datatyp för modellvikter |
| `--tensor-parallel-size` | Antal GPU:er att dela upp modellen över (sätt till totalt antal GPU:er i klustret) |
| `--distributed-executor-backend` | Backend för multinodsexekvering (`ray` för klusterdistributioner) |
| `--enforce-eager` | Inaktiverar CUDA-graf-kompilering för kompatibilitet |
| `--language-model-only` | Hoppar över laddning av hjälpmodellkomponenter (t.ex. vision-kodare) |
| `--reasoning-parser` | Aktiverar strukturerad tolkning av resonemangsutdata för modellen |

För fullständig information om parameteranvändning, se [vLLM-dokumentationen](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Åtkomst till modellen

vLLM exponerar ett OpenAI-kompatibelt API, så du kan ansluta vilken kompatibel klient eller gränssnitt som helst till ditt kluster. Ett populärt alternativ är [Open WebUI](https://github.com/open-webui/open-webui), som tillhandahåller ett webbläsarbaserat chattgränssnitt.

För att ansluta Open WebUI till din vLLM-slutpunkt:

1. Öppna **Settings** > **Admin Panel** > **Connections**
2. Klicka på **+** vid **Manage OpenAI API Connections**
3. Ställ in **Connection Type** till **External**
4. Ställ in **URL** till `http://<MACHINE_1_IP>:7000/v1`
5. Under **Auth**, välj **None** i rullgardinsmenyn
6. Lämna **Model IDs** tomt för att automatiskt upptäcka alla modeller från slutpunkten

> **Hitta `<MACHINE_1_IP>`**: Kör `hostname -I | awk '{print $1}'` på Maskin 1 för att hitta dess lokala IP-adress. Om du kommer åt Open WebUI från Maskin 1 själv kan du använda `http://localhost:7000/v1`.

![Open WebUI-anslutningsinställningar för vLLM-slutpunkten](assets/openwebui-connection.png)

När du är ansluten, välj modellen från modellens rullgardinsmeny i Open WebUI och börja chatta. Modellen körs nu över alla fyra av dina Ryzen AI Halo-noder:

![Chatta med Qwen3.5-397B i Open WebUI](assets/openwebui-chat.png)

## Nästa steg

- **Utforska andra modeller**: Upptäck nya modeller på [Hugging Face](https://huggingface.co/models?&sort=trending) som passar inom klustrets kombinerade GPU-minne
- **Skala bortom fyra noder**: Lägg till ytterligare Ryzen AI Halo-system som ytterligare Ray-arbetare för att dela upp modeller över ännu fler GPU:er. Följ [Steg 2: Anslut till klustret](#step-2-join-the-cluster-machines-2-3-and-4) på varje ytterligare arbetsmaskin och öka `--tensor-parallel-size` därefter
- **Prova andra parallellstrategier**: vLLM stöder [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) för mixture-of-experts-modeller och [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) för högre genomströmning. Experimentera med `--enable-expert-parallel` och `--data-parallel-size` för att hitta den bästa konfigurationen för din arbetsbelastning