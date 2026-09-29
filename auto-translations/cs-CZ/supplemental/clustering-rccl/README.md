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

# Clustrování dvou Ryzen™ AI Halo pomocí RCCL

## Přehled

Váš Ryzen™ AI Halo je již schopen lokálně spouštět velké jazykové modely. Clustrování jde ještě dál – kombinuje paměť GPU více systémů přes lokální síť, čímž vám umožní přístup k ještě větším modelům se silnějším uvažováním, lepší generací kódu a hlubším porozuměním více jazykům, a to zcela na vašem vlastním hardwaru.

Tento playbook vás naučí, jak sklustrovat dva systémy Ryzen AI Halo pomocí RCCL (ROCm Communication Collectives Library) s vLLM a jak spustit Qwen3.5-397B, model s 397 miliardami parametrů, napříč oběma stroji s akcelerací ROCm.

## Co se naučíte

- Jak rozšířit alokaci VRAM na systémech Ryzen AI Halo
- Spuštění vLLM s podporou ROCm
- Konfiguraci RCCL pro tensorově paralelní inferenci na více uzlech napříč dvěma systémy Ryzen AI Halo
- Spuštění modelu se 397 miliardami parametrů napříč dvěma propojenými systémy Ryzen AI Halo

## Předpoklady

### Hardware

Tento playbook vyžaduje dvě jednotky Ryzen AI Halo a jeden ethernetový přepínač, propojené v hvězdicové topologii, přičemž každá jednotka je připojena přímo k přepínači.

| Komponenta | Množství | Popis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Výpočetní uzly tvořící cluster |
| 10Gbps ethernetový přepínač | 1 | Centrální přepínač umožňující komunikaci mezi více uzly Ryzen AI Halo (alespoň 2 porty) |
| Ethernetový kabel | 2 | Připojuje každou jednotku Halo k přepínači (doporučen Cat 7 nebo vyšší) |

> **Poznámka**: K připojení dvou jednotek Ryzen AI Halo jsou zapotřebí dva porty ethernetového přepínače. Třetí port je zapotřebí, pokud k modelu přistupujete ze samostatného klientského počítače namísto z jedné z jednotek Halo.

### Software
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Nastavení fyzického hardwaru

> **Poznámka**: Tento krok dokončete na obou strojích – Stroj 1 i Stroj 2.

Připojte každou jednotku Ryzen AI Halo k ethernetovému přepínači pomocí kabelu Cat 7 (nebo vyššího). Tím se vytvoří 10Gbps spoj používaný pro vysokorychlostní komunikaci mezi uzly.

### 1. Určení síťových rozhraní

Na každém stroji zjistěte název jeho síťového rozhraní a poznamenejte si ho (v rámci dalších pokynů se na něj bude odkazovat jako `IFNAME`). Spusťte:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Tím se přímo vypíše název rozhraní, například:

```bash
enp191s0
```

### 2. Ověření rychlosti síťového spojení

Potvrďte, že je spojení aktivní a běží na plnou rychlost, kontrolou rychlosti vašeho rozhraní:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Poznámka**: Nahraďte `<IFNAME>` výstupním názvem rozhraní z kroku [1. Určení síťových rozhraní](#1-determine-network-interfaces)

Měli byste vidět rychlost `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Poznámka**: Pokud je rychlost nižší než `10000Mb/s` nebo se spojení nenaváže, zkontrolujte připojení kabelu a potvrďte, že je port přepínače nastaven na 10Gbps. Některé přepínače vyžadují vypnutí automatického vyjednávání rychlosti a její ruční nastavení; postupujte podle dokumentace svého přepínače.

## Rozšíření alokace VRAM

> **Poznámka**: Tento krok dokončete na obou strojích – Stroj 1 i Stroj 2.

### Konfigurace paměti pro spouštění velkých modelů

Na Linuxu ROCm využívá sdílený systémový paměťový pool, který je ve výchozím nastavení konfigurován na polovinu systémové paměti.

Toto množství lze zvýšit změnou nastavení stránek Translation Table Manageru (TTM) jádra, podle následujících pokynů. AMD doporučuje nastavit minimální vyhrazenou VRAM v BIOSu (0,5 GB).

* Nainstalujte nástroj pipx a přidejte cestu k balíčkům nainstalovaným přes pipx do systémové vyhledávací cesty.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Nainstalujte wheel balíček amd-debug-tools z PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Spusťte nástroj amd-ttm pro zjištění aktuálního nastavení sdílené paměti.
  ```bash
  amd-ttm
  ```

* Nastavte znovu nastavení sdílené paměti na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Restartujte systém, aby se změny projevily.

## Inicializace kontejneru vLLM

> **Poznámka**: Tento krok dokončete na obou strojích – Stroj 1 i Stroj 2.

Váš Ryzen AI Halo je dodáván s vLLM zabaleným uvnitř předpřipraveného image kontejneru, který spouštíte pomocí Podmanu, bezplatného open source nástroje pro kontejnery.

### 1. Vytvoření adresáře pro stahování modelu

Když v tomto playbooku obsloužíte model Qwen3.5-397B, vLLM automaticky stáhne váhy modelu do vašeho systému. Aby byly tyto váhy přístupné zevnitř kontejneru, nejprve vytvořte adresář models, který lze do kontejneru připojit (mount):

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Spuštění kontejneru vLLM

Následující příkaz spustí kontejner a přesune vás do interaktivního shellu. Připojí adresář models, který jste právě vytvořili, a předá váš `IFNAME` proměnným `NCCL_SOCKET_IFNAME` a `GLOO_SOCKET_IFNAME`, čímž sdělí RCCL (knihovně, kterou vLLM používá ke koordinaci GPU napříč clusterem), které rozhraní má použít.

Spusťte kontejner pomocí:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Poznámka**: Nahraďte `<IFNAME>` výstupním názvem rozhraní z kroku [1. Určení síťových rozhraní](#1-determine-network-interfaces)

## Spuštění modelu na clusteru

vLLM používá Ray k orchestraci clusteru a RCCL ke zpracování komunikace mezi GPU napříč uzly. Jeden stroj funguje jako **hlavní uzel** (Stroj 1), koordinující inferenci. Druhý se připojuje jako **pracovní uzel** (Stroj 2), přispívající svou pamětí GPU a výpočetním výkonem.

> **Poznámka**: Ray je volitelná závislost pro vLLM a je k dispozici pouze zevnitř předkonfigurovaného kontejneru Podman.

Při spuštění vLLM rozdělí model napříč oběma uzly pomocí tensorové paralelizace. Jakmile je model načten, inference probíhá, jako by běžela na jediném akcelerátoru.

#### Zabránění chybám OOM u Ray

Ve výchozím nastavení Ray monitoruje paměť hostitele na každém uzlu a ukončí největší proces, jakmile využití paměti překročí 95 %. Na vašem Ryzen™ AI Halo sdílí GPU a hostitel jeden paměťový pool, takže načtení modelu může vyvolat `ray.exceptions.OutOfMemoryError` a ukončit pracovní proces.

Abychom tomu zabránili, před spuštěním a připojením ke clusteru na každém stroji exportujeme proměnnou `RAY_memory_monitor_refresh_ms=0`.
### Krok 1: Spuštění hlavního uzlu Ray (Machine 1)

Na Machine 1 spusťte hlavní uzel Ray, abyste inicializovali cluster:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Zjištění `<MACHINE_1_IP>`**: Na Machine 1 spusťte `hostname -I | awk '{print $1}'`, abyste zjistili jeho lokální IP adresu.

### Krok 2: Připojení ke clusteru (Machine 2)

Na Machine 2 se připojte k hlavnímu uzlu a vytvořte tak cluster:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Zjištění `<MACHINE_2_IP>`**: Na Machine 2 spusťte `hostname -I | awk '{print $1}'`, abyste zjistili jeho lokální IP adresu.

### Krok 3: Nasazení modelu (Machine 1)

Na Machine 1 spusťte server vLLM. Ten automaticky stáhne model a začne jej poskytovat napříč oběma uzly:

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
| `--port` | Port, na kterém bude HTTP API poskytováno |
| `--host` | IP adresa, na kterou se server naváže (`0.0.0.0` pro všechna rozhraní) |
| `--max-model-len` | Maximální délka kontextu v tokenech |
| `--gpu-memory-utilization` | Podíl paměti GPU, který se má alokovat (0,0–1,0) |
| `--dtype` | Datový typ pro váhy modelu |
| `--tensor-parallel-size` | Počet GPU, mezi které se model rozdělí (nastavte na celkový počet GPU v clusteru) |
| `--distributed-executor-backend` | Backend pro spuštění na více uzlech (`ray` pro nasazení v clusteru) |
| `--enforce-eager` | Vypne kompilaci CUDA grafů kvůli kompatibilitě |
| `--language-model-only` | Přeskočí načtení pomocných komponent modelu (např. vizuálního enkodéru) |
| `--reasoning-parser` | Zapne strukturované zpracování výstupu úvah pro model |

Úplný popis použití parametrů naleznete v [dokumentaci vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Přístup k modelu

vLLM poskytuje API kompatibilní s OpenAI, takže ke svému clusteru můžete připojit jakéhokoli kompatibilního klienta nebo rozhraní. Jednou z oblíbených možností je [Open WebUI](https://github.com/open-webui/open-webui), které poskytuje chatovací rozhraní v prohlížeči.

Připojení Open WebUI k vašemu endpointu vLLM:

1. Otevřete **Settings** > **Admin Panel** > **Connections**
2. Klikněte na **+** u **Manage OpenAI API Connections**
3. Nastavte **Connection Type** na **External**
4. Nastavte **URL** na `http://<MACHINE_1_IP>:7000/v1`
5. V sekci **Auth** vyberte z rozevíracího seznamu **None**
6. Ponechte **Model IDs** prázdné, aby se automaticky vyhledaly všechny modely z daného endpointu

> **Zjištění `<MACHINE_1_IP>`**: Na Machine 1 spusťte `hostname -I | awk '{print $1}'`, abyste zjistili jeho lokální IP adresu. Pokud přistupujete k Open WebUI přímo z Machine 1, můžete použít `http://localhost:7000/v1`.

![Nastavení připojení Open WebUI k endpointu vLLM](assets/openwebui-connection.png)

Jakmile jste připojeni, vyberte model z rozevíracího seznamu modelů v Open WebUI a začněte chatovat. Model nyní běží napříč oběma vašimi uzly Ryzen AI Halo:

![Chatování s Qwen3.5-397B v Open WebUI](assets/openwebui-chat.png)

## Další kroky

- **Prozkoumejte další modely**: Objevte nové modely na [Hugging Face](https://huggingface.co/models?&sort=trending), které se vejdou do celkové paměti GPU vašeho clusteru
- **Rozšiřte na čtyři uzly**: Přidejte další dva systémy Ryzen AI Halo jako další pracovní uzly (Ray workers) a rozdělte modely mezi ještě více GPU. To vyžaduje síťový přepínač Ethernet s alespoň čtyřmi porty, po jednom pro každý uzel. Na každém dalším pracovním uzlu postupujte podle [Krok 2: Připojení ke clusteru](#step-2-join-the-cluster-machine-2) a odpovídajícím způsobem zvyšte `--tensor-parallel-size`
- **Vyzkoušejte další strategie paralelismu**: vLLM podporuje [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) pro modely typu mixture-of-experts a [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) pro vyšší propustnost. Vyzkoušejte `--enable-expert-parallel` a `--data-parallel-size`, abyste našli nejlepší konfiguraci pro svou zátěž