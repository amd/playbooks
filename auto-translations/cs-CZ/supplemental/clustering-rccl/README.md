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

Váš Ryzen™ AI Halo je již schopen lokálně spouštět velké jazykové modely. Clustering jde ještě dále tím, že kombinuje paměť GPU více systémů přes lokální síť, což vám poskytuje přístup k ještě větším modelům se silnějším uvažováním, lepší generací kódu a hlubším vícejazyčným porozuměním, a to zcela na vašem vlastním hardwaru.

Tento playbook vás naučí, jak clusterovat dva systémy Ryzen AI Halo pomocí RCCL (ROCm Communication Collectives Library) s vLLM a spustit Qwen3.5-397B, model se 397 miliardami parametrů, na obou strojích s akcelerací ROCm.

## Co se naučíte

- Jak rozšířit alokaci VRAM na systémech Ryzen AI Halo
- Spuštění vLLM s podporou ROCm
- Konfigurace RCCL pro víceuzlovou tensor-paralelní inferenci napříč dvěma systémy Ryzen AI Halo
- Spuštění modelu se 397B parametry na dvou propojených systémech Ryzen AI Halo

## Předpoklady

### Hardware

Tento playbook vyžaduje dvě jednotky Ryzen AI Halo a jeden ethernetový přepínač, propojené v hvězdicové topologii, kde je každá jednotka připojena přímo k přepínači.

| Komponenta | Množství | Popis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Výpočetní uzly tvořící cluster |
| 10Gbps ethernetový přepínač | 1 | Centrální přepínač umožňující komunikaci mezi více uzly Ryzen AI Halo (alespoň 2 porty) |
| Ethernetový kabel | 2 | Připojuje každou jednotku Halo k přepínači (doporučen Cat 7 nebo vyšší) |

> **Poznámka**: Pro připojení obou jednotek Ryzen AI Halo jsou vyžadovány dva porty ethernetového přepínače. Třetí port je vyžadován, pokud k modelu přistupujete ze samostatného klientského počítače namísto z jedné z jednotek Halo.

### Software
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Nastavení fyzického hardwaru

> **Poznámka**: Proveďte tento krok jak na Stroji 1, tak na Stroji 2.

Připojte každou jednotku Ryzen AI Halo k ethernetovému přepínači pomocí kabelu Cat 7 (nebo vyššího). Tím se vytvoří 10Gbps propojení používané pro vysokorychlostní komunikaci mezi uzly.

### 1. Určení síťových rozhraní

Na každém stroji zjistěte název jeho síťového rozhraní a poznamenejte si jej (v dalších částech instrukcí bude označován jako `IFNAME`). Spusťte:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Tímto se přímo vypíše název rozhraní, například:

```bash
enp191s0
```

### 2. Ověření rychlosti síťového propojení

Ověřte, že je propojení aktivní a běží na plnou rychlost, zkontrolováním rychlosti vašeho rozhraní:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Poznámka**: Nahraďte `<IFNAME>` výstupním názvem rozhraní z [1. Určení síťových rozhraní](#1-určení-síťových-rozhraní)

Měli byste vidět rychlost `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Poznámka**: Pokud je rychlost nižší než `10000Mb/s` nebo se propojení nenaváže, zkontrolujte kabelové připojení a potvrďte, že je port přepínače nastaven na 10Gbps. Některé přepínače vyžadují zakázání auto-negotiation a ruční nastavení rychlosti propojení; podívejte se do dokumentace vašeho přepínače.

## Rozšíření alokace VRAM

> **Poznámka**: Proveďte tento krok jak na Stroji 1, tak na Stroji 2.

### Konfigurace paměti pro spouštění velkých modelů

Na Linuxu ROCm využívá sdílený fond systémové paměti, který je ve výchozím nastavení konfigurován na polovinu systémové paměti.

Toto množství lze zvýšit změnou nastavení stránkování Translation Table Manager (TTM) jádra podle následujících instrukcí. AMD doporučuje nastavit minimální vyhrazenou VRAM v BIOSu (0,5 GB).

* Nainstalujte nástroj pipx a přidejte cestu k nainstalovaným wheel balíčkům pipx do systémové vyhledávací cesty.

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

* Přenastavte nastavení sdílené paměti na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Restartujte systém, aby se změny projevily.

## Inicializace kontejneru vLLM

> **Poznámka**: Proveďte tento krok jak na Stroji 1, tak na Stroji 2.

Váš Ryzen AI Halo je dodáván s vLLM zabaleným uvnitř předpřipraveného kontejnerového obrazu, který spouštíte pomocí Podman, bezplatného open source kontejnerového nástroje.

### 1. Vytvoření adresáře pro stažení modelu

Když v tomto playbooku budete servírovat model Qwen3.5-397B, vLLM automaticky stáhne váhy modelu do vašeho systému. Aby byly tyto váhy přístupné z kontejneru, nejprve vytvořte adresář pro modely, který může kontejner připojit:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Spuštění kontejneru vLLM

Níže uvedený příkaz spustí kontejner a přepne vás do interaktivního shellu. Připojí adresář pro modely, který jste právě vytvořili, a předá váš `IFNAME` do `NCCL_SOCKET_IFNAME` a `GLOO_SOCKET_IFNAME`, čímž sdělí RCCL (knihovně, kterou vLLM používá ke koordinaci GPU napříč clusterem), které rozhraní má použít.

Spusťte kontejner pomocí:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Poznámka**: Nahraďte `<IFNAME>` výstupním názvem rozhraní z [1. Určení síťových rozhraní](#1-určení-síťových-rozhraní)

## Spuštění modelu na clusteru

vLLM používá Ray k orchestraci clusteru a RCCL k zajištění komunikace mezi GPU napříč uzly. Jeden stroj funguje jako **hlavní uzel** (Stroj 1), který koordinuje inferenci. Druhý se připojuje jako **pracovní uzel** (Stroj 2), přispívá svou pamětí GPU a výpočetním výkonem.

> **Poznámka**: Ray je volitelnou závislostí pro vLLM a je dostupný pouze v rámci předkonfigurovaného kontejneru Podman.

Při spuštění vLLM rozdělí model mezi oba uzly pomocí tensor paralelismu. Jakmile je model načten, inference probíhá, jako by běžela na jediném akcelerátoru.

### Krok 1: Spuštění hlavního uzlu Ray (Stroj 1)

Na Stroji 1 spusťte hlavní uzel Ray pro inicializaci clusteru:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Zjištění `<MACHINE_1_IP>`**: Na Stroji 1 spusťte `hostname -I | awk '{print $1}'` pro zjištění jeho lokální IP adresy.
### Krok 2: Připojení ke clusteru (Machine 2)

Na Machine 2 se připojte k hlavnímu uzlu a vytvořte cluster:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Zjištění `<MACHINE_2_IP>`**: Na Machine 2 spusťte `hostname -I | awk '{print $1}'`, čímž zjistíte jeho lokální IP adresu.

### Krok 3: Zpřístupnění modelu (Machine 1)

Na Machine 1 spusťte server vLLM. Ten automaticky stáhne model a začne ho zpřístupňovat napříč oběma uzly:

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
| `--port` | Port, na kterém se zpřístupní HTTP API |
| `--host` | IP adresa, na kterou se server naváže (`0.0.0.0` pro všechna rozhraní) |
| `--max-model-len` | Maximální délka kontextu v tokenech |
| `--gpu-memory-utilization` | Podíl paměti GPU, který se má alokovat (0.0–1.0) |
| `--dtype` | Datový typ pro váhy modelu |
| `--tensor-parallel-size` | Počet GPU, mezi které se model rozdělí (nastavte na celkový počet GPU v clusteru) |
| `--distributed-executor-backend` | Backend pro spouštění na více uzlech (`ray` pro clusterová nasazení) |
| `--enforce-eager` | Vypne kompilaci CUDA grafů kvůli kompatibilitě |
| `--language-model-only` | Přeskočí načtení pomocných komponent modelu (např. vizuálního enkodéru) |
| `--reasoning-parser` | Zapne strukturované parsování výstupu s reasoningem pro daný model |

Úplný přehled použití parametrů naleznete v [dokumentaci vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Přístup k modelu

vLLM poskytuje API kompatibilní s OpenAI, takže k vašemu clusteru můžete připojit jakéhokoli kompatibilního klienta nebo rozhraní. Jednou z oblíbených možností je [Open WebUI](https://github.com/open-webui/open-webui), které poskytuje chatovací rozhraní v prohlížeči.

Připojení Open WebUI k vašemu koncovému bodu vLLM:

1. Otevřete **Settings** > **Admin Panel** > **Connections**
2. Klikněte na **+** u **Manage OpenAI API Connections**
3. Nastavte **Connection Type** na **External**
4. Nastavte **URL** na `http://<MACHINE_1_IP>:7000/v1`
5. V části **Auth** vyberte z rozevíracího seznamu **None**
6. Ponechte **Model IDs** prázdné, aby se všechny modely z koncového bodu automaticky vyhledaly

> **Zjištění `<MACHINE_1_IP>`**: Na Machine 1 spusťte `hostname -I | awk '{print $1}'`, čímž zjistíte jeho lokální IP adresu. Pokud přistupujete k Open WebUI přímo z Machine 1, můžete použít `http://localhost:7000/v1`.

![Nastavení připojení Open WebUI ke koncovému bodu vLLM](assets/openwebui-connection.png)

Po připojení vyberte model z rozevíracího seznamu modelů v Open WebUI a začněte chatovat. Model nyní běží napříč oběma vašimi uzly Ryzen AI Halo:

![Chatování s Qwen3.5-397B v Open WebUI](assets/openwebui-chat.png)

## Další kroky

- **Prozkoumejte další modely**: Objevte na [Hugging Face](https://huggingface.co/models?&sort=trending) nové modely, které se vejdou do kombinované paměti GPU vašeho clusteru
- **Rozšiřte na čtyři uzly**: Přidejte další dva systémy Ryzen AI Halo jako další pracovní uzly (workery) Ray, abyste mohli rozdělovat modely mezi ještě větší počet GPU. To vyžaduje ethernetový přepínač s alespoň čtyřmi porty, po jednom pro každý uzel. Na každém dalším workeru postupujte podle [Kroku 2: Připojení ke clusteru](#step-2-join-the-cluster-machine-2) a odpovídajícím způsobem zvyšte hodnotu `--tensor-parallel-size`
- **Vyzkoušejte další strategie paralelizace**: vLLM podporuje [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) pro modely typu mixture-of-experts a [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) pro vyšší propustnost. Vyzkoušejte `--enable-expert-parallel` a `--data-parallel-size`, abyste našli nejlepší konfiguraci pro vaši zátěž