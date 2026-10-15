<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový překlad.** Tato stránka byla automaticky přeložena z angličtiny a nebyla zkontrolována člověkem. Může obsahovat chyby a určité pokyny, příkazy, soubory ke stažení, dostupnost produktů nebo jiný obsah se může lišit podle jazyka nebo regionu. V případě jakéhokoli nesouladu nebo rozporu je rozhodující původní anglická verze playbooku.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Clustering dvou Ryzen™ AI Halo pomocí RCCL

## Přehled

Váš Ryzen™ AI Halo dokáže lokálně spouštět velké jazykové modely už teď. Clustering jde ještě dál – kombinuje GPU paměť více systémů přes lokální síť, což vám poskytuje přístup k ještě větším modelům se silnějším uvažováním, lepší generováním kódu a hlubším porozuměním více jazykům, a to zcela na vašem vlastním hardwaru.

Tato příručka vás naučí, jak vytvořit cluster ze dvou systémů Ryzen AI Halo pomocí RCCL (ROCm Communication Collectives Library) s vLLM a jak spustit Qwen3.5-397B, model se 397 miliardami parametrů, napříč oběma stroji s akcelerací ROCm.

## Co se naučíte

- Jak rozšířit alokaci VRAM na systémech Ryzen AI Halo
- Spouštění vLLM s podporou ROCm
- Konfiguraci RCCL pro multi-node tensor-paralelní inferenci napříč dvěma systémy Ryzen AI Halo
- Spuštění modelu se 397 miliardami parametrů napříč dvěma propojenými systémy Ryzen AI Halo

## Požadavky

### Hardware

Tato příručka vyžaduje dvě jednotky Ryzen AI Halo a jeden ethernetový přepínač, zapojené v topologii hvězda, kde je každá jednotka připojena přímo k přepínači.

| Komponenta | Množství | Popis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Výpočetní uzly tvořící cluster |
| 10Gbps ethernetový přepínač | 1 | Centrální přepínač umožňující komunikaci více uzlů Ryzen AI Halo (alespoň 2 porty) |
| Ethernetový kabel | 2 | Připojuje každou jednotku Halo k přepínači (doporučuje se Cat 7 nebo vyšší) |

> **Poznámka**: Ke připojení dvou jednotek Ryzen AI Halo jsou potřeba dva porty ethernetového přepínače. Třetí port je potřeba, pokud k modelu přistupujete ze samostatného klientského počítače namísto z jedné z jednotek Halo.

### Software
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fyzická příprava hardwaru

> **Poznámka**: Tento krok proveďte na obou strojích – Machine 1 i Machine 2.

Připojte každou jednotku Ryzen AI Halo k ethernetovému přepínači pomocí kabelu Cat 7 (nebo vyššího). Tím se vytvoří 10Gbps spojení používané pro vysokorychlostní komunikaci mezi uzly.

### 1. Zjištění síťových rozhraní

Na každém stroji zjistěte název jeho síťového rozhraní a poznamenejte si ho (v dalších pokynech se na něj bude odkazovat jako `IFNAME`). Spusťte:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Tím se vypíše přímo název rozhraní, například:

```bash
enp191s0
```

### 2. Ověření rychlosti síťového spojení

Potvrďte, že je spojení aktivní a běží plnou rychlostí, kontrolou rychlosti vašeho rozhraní:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Poznámka**: Nahraďte `<IFNAME>` výstupním názvem rozhraní z kroku [1. Zjištění síťových rozhraní](#1-determine-network-interfaces)

Měli byste vidět rychlost `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Poznámka**: Pokud je rychlost nižší než `10000Mb/s` nebo se spojení nenaváže, zkontrolujte připojení kabelu a ověřte, že je port přepínače nastaven na 10Gbps. Některé přepínače vyžadují vypnutí automatického vyjednávání a ruční nastavení rychlosti spojení; podrobnosti najdete v dokumentaci vašeho přepínače.

## Rozšíření alokace VRAM

> **Poznámka**: Tento krok proveďte na obou strojích – Machine 1 i Machine 2.

### Konfigurace paměti pro spouštění velkých modelů

Na Linuxu využívá ROCm sdílenou poolu systémové paměti a tato pool je ve výchozím nastavení nakonfigurována na polovinu systémové paměti.

Toto množství lze zvýšit změnou nastavení stránek Translation Table Manager (TTM) jádra podle následujících pokynů. AMD doporučuje nastavit minimální vyhrazenou VRAM v BIOSu (0,5 GB).

* Nainstalujte nástroj pipx a přidejte cestu k balíčkům wheel instalovaným přes pipx do systémové vyhledávací cesty.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Nainstalujte balíček wheel amd-debug-tools z PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Spusťte nástroj amd-ttm pro zjištění aktuálního nastavení sdílené paměti.
  ```bash
  amd-ttm
  ```

* Přenastavte konfiguraci sdílené paměti na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Restartujte systém, aby se změny projevily.

## Inicializace kontejneru vLLM

> **Poznámka**: Tento krok proveďte na obou strojích – Machine 1 i Machine 2.

Váš Ryzen AI Halo je dodáván s vLLM zabaleným uvnitř předpřipraveného image kontejneru, který spouštíte pomocí nástroje Podman, což je bezplatný open source nástroj pro kontejnery.

### 1. Vytvoření adresáře pro stahování modelu

Když v této příručce spustíte model Qwen3.5-397B, vLLM automaticky stáhne váhy modelu do vašeho systému. Aby byly tyto váhy dostupné i uvnitř kontejneru, nejprve vytvořte adresář pro modely, který lze do kontejneru připojit:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Spuštění kontejneru vLLM

Následující příkaz spustí kontejner a přenese vás do interaktivního shellu. Připojí adresář pro modely, který jste právě vytvořili, a předá váš `IFNAME` proměnným `NCCL_SOCKET_IFNAME` a `GLOO_SOCKET_IFNAME`, čímž sdělí RCCL (knihovně, kterou vLLM používá ke koordinaci GPU napříč clusterem), které rozhraní má použít.

Spusťte kontejner pomocí:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Poznámka**: Nahraďte `<IFNAME>` výstupním názvem rozhraní z kroku [1. Zjištění síťových rozhraní](#1-determine-network-interfaces)

## Spuštění modelu na clusteru

vLLM používá Ray k orchestraci clusteru a RCCL ke zpracování komunikace mezi GPU napříč uzly. Jeden stroj funguje jako **head node** (Machine 1), koordinující inferenci. Druhý se připojuje jako **worker node** (Machine 2) a přispívá svou GPU pamětí a výpočetním výkonem.

> **Poznámka**: Ray je volitelná závislost pro vLLM a je dostupná pouze uvnitř předpřipraveného kontejneru Podman.

Při spuštění vLLM rozdělí model napříč oběma uzly pomocí tensor paralelismu. Jakmile je model načten, inference probíhá, jako by běžela na jediném akcelerátoru.

#### Prevence chyb OOM u Ray

Ve výchozím nastavení Ray monitoruje paměť hostitele na každém uzlu a zabíjí největší proces, jakmile využití paměti překročí 95 %. Na vašem Ryzen™ AI Halo sdílí GPU a hostitel jednu poolu paměti, takže načtení modelu může vyvolat chybu `ray.exceptions.OutOfMemoryError` a zabít worker proces.

Abyste tomu předešli, exportujeme na každém stroji `RAY_memory_monitor_refresh_ms=0` před spuštěním a připojením k clusteru.
### Krok 1: Spuštění hlavního uzlu Ray (Stroj 1)

Na Stroji 1 spusťte hlavní uzel Ray a inicializujte tak cluster:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Zjištění `<MACHINE_1_IP>`**: Na Stroji 1 spusťte `hostname -I | awk '{print $1}'`, abyste zjistili jeho lokální IP adresu.

### Krok 2: Připojení ke clusteru (Stroj 2)

Na Stroji 2 se připojte k hlavnímu uzlu a vytvořte tak cluster:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Zjištění `<MACHINE_2_IP>`**: Na Stroji 2 spusťte `hostname -I | awk '{print $1}'`, abyste zjistili jeho lokální IP adresu.

### Krok 3: Obsluha modelu (Stroj 1)

Na Stroji 1 spusťte server vLLM. Ten automaticky stáhne model a začne jej obsluhovat napříč oběma uzly:

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

#### Přehled parametrů

| Příznak | Účel |
|------|---------|
| `--port` | Port, na kterém bude obsluhováno HTTP API |
| `--host` | IP adresa, na kterou se server naváže (`0.0.0.0` pro všechna rozhraní) |
| `--max-model-len` | Maximální délka kontextu v tokenech |
| `--gpu-memory-utilization` | Podíl paměti GPU, který se má alokovat (0,0–1,0) |
| `--dtype` | Datový typ pro váhy modelu |
| `--tensor-parallel-size` | Počet GPU, mezi které se má model rozdělit (nastavte na celkový počet GPU v clusteru) |
| `--distributed-executor-backend` | Backend pro spuštění napříč více uzly (`ray` pro nasazení do clusteru) |
| `--enforce-eager` | Zakáže kompilaci CUDA grafů kvůli kompatibilitě |
| `--language-model-only` | Přeskočí načítání pomocných komponent modelu (např. vizuálního enkodéru) |
| `--reasoning-parser` | Povolí strukturované parsování výstupu uvažování (reasoning) pro daný model |

Úplný popis parametrů naleznete v [dokumentaci vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Přístup k modelu

vLLM poskytuje API kompatibilní s OpenAI, takže ke svému clusteru můžete připojit libovolného kompatibilního klienta nebo rozhraní. Jednou z oblíbených možností je [Open WebUI](https://github.com/open-webui/open-webui), které poskytuje chatovací rozhraní přístupné z prohlížeče.

Chcete-li propojit Open WebUI s vaším koncovým bodem vLLM:

1. Otevřete **Settings** > **Admin Panel** > **Connections**
2. Klikněte na **+** u položky **Manage OpenAI API Connections**
3. Nastavte **Connection Type** na **External**
4. Nastavte **URL** na `http://<MACHINE_1_IP>:7000/v1`
5. V části **Auth** vyberte z rozbalovací nabídky **None**
6. Pole **Model IDs** ponechte prázdné, aby se všechny modely z daného koncového bodu automaticky rozpoznaly

> **Zjištění `<MACHINE_1_IP>`**: Na Stroji 1 spusťte `hostname -I | awk '{print $1}'`, abyste zjistili jeho lokální IP adresu. Pokud přistupujete k Open WebUI přímo ze Stroje 1, můžete použít `http://localhost:7000/v1`.

![Nastavení připojení Open WebUI ke koncovému bodu vLLM](assets/openwebui-connection.png)

Po připojení vyberte model z rozbalovací nabídky modelů v Open WebUI a začněte chatovat. Model nyní běží napříč oběma vašimi uzly Ryzen AI Halo:

![Chatování s Qwen3.5-397B v Open WebUI](assets/openwebui-chat.png)

## Další kroky

- **Prozkoumejte další modely**: Objevte nové modely na [Hugging Face](https://huggingface.co/models?&sort=trending), které se vejdou do kombinované paměti GPU vašeho clusteru
- **Rozšíření na čtyři uzly**: Přidejte další dva systémy Ryzen AI Halo jako další pracovní uzly Ray a rozdělte modely mezi ještě více GPU. To vyžaduje ethernetový přepínač s alespoň čtyřmi porty, jedním pro každý uzel. Na každém dalším pracovním uzlu postupujte podle [Kroku 2: Připojení ke clusteru](#step-2-join-the-cluster-machine-2) a odpovídajícím způsobem zvyšte hodnotu `--tensor-parallel-size`
- **Vyzkoušejte další strategie paralelizace**: vLLM podporuje [expertní paralelismus](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) pro modely typu mixture-of-experts a [datový paralelismus](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) pro vyšší propustnost. Experimentujte s `--enable-expert-parallel` a `--data-parallel-size`, abyste našli nejlepší konfiguraci pro svou zátěž