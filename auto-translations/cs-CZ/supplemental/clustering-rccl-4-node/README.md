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

# Clustering čtyř Ryzen™ AI Halo pomocí RCCL

## Přehled

Váš Ryzen™ AI Halo je již schopen lokálně spouštět velké jazykové modely. Clustering jde ještě dál – spojuje paměť GPU více systémů přes lokální síť, čímž vám umožňuje přístup k ještě větším modelům se silnějším uvažováním, lepší generací kódu a hlubším porozuměním více jazykům, a to zcela na vašem vlastním hardwaru.

Tento návod vás naučí, jak vytvořit cluster ze čtyř systémů Ryzen AI Halo pomocí RCCL (ROCm Communication Collectives Library) ve spojení s vLLM a spustit model Qwen3.5-397B s 397 miliardami parametrů napříč všemi čtyřmi stroji s akcelerací ROCm.

## Co se naučíte

- Jak rozšířit alokaci VRAM na systémech Ryzen AI Halo
- Spouštění vLLM s podporou ROCm
- Konfiguraci RCCL pro multi-node tensor-paralelní inferenci napříč čtyřmi systémy Ryzen AI Halo
- Spuštění modelu se 397 miliardami parametrů napříč čtyřmi propojenými systémy Ryzen AI Halo

## Požadavky

### Hardware

Tento návod vyžaduje čtyři jednotky Ryzen AI Halo a jeden ethernetový switch, zapojené v topologii hvězdy, kde je každá jednotka připojena přímo ke switchi.

| Komponenta | Množství | Popis |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Výpočetní uzly tvořící cluster |
| 10Gbps ethernetový switch | 1 | Centrální switch umožňující komunikaci mezi uzly Ryzen AI Halo (alespoň 4 porty) |
| Ethernetový kabel | 4 | Propojuje každou jednotku Halo se switchem (doporučuje se Cat 7 nebo vyšší) |

> **Poznámka**: Pro připojení čtyř jednotek Ryzen AI Halo jsou potřeba čtyři porty ethernetového switche. Pátý port je potřeba, pokud k modelu přistupujete ze samostatného klientského stroje místo z jedné z jednotek Halo.

### Software
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Nastavení fyzického hardwaru

> **Poznámka**: Tento krok proveďte na všech čtyřech strojích (Stroj 1 až Stroj 4).

Připojte každou jednotku Ryzen AI Halo k ethernetovému switchi pomocí kabelu Cat 7 (nebo vyššího). Tím se vytvoří 10Gbps spojení používané pro vysokorychlostní komunikaci mezi uzly.

### 1. Zjištění síťových rozhraní

Na každém stroji zjistěte název jeho síťového rozhraní a poznamenejte si jej (v dalším textu bude označován jako `IFNAME`). Spusťte:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Toto přímo vypíše název rozhraní, například:

```bash
enp191s0
```

### 2. Ověření rychlosti síťového spojení

Potvrďte, že je spojení aktivní a běží plnou rychlostí, kontrolou rychlosti vašeho rozhraní:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Poznámka**: Nahraďte `<IFNAME>` názvem výstupního rozhraní z [1. Zjištění síťových rozhraní](#1-determine-network-interfaces)

Měli byste vidět rychlost `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Poznámka**: Pokud je rychlost nižší než `10000Mb/s` nebo se spojení nenaváže, zkontrolujte zapojení kabelu a potvrďte, že je port switche nastaven na 10Gbps. Některé switche vyžadují zakázání auto-negotiation a ruční nastavení rychlosti spojení; postupujte podle dokumentace vašeho switche.

## Rozšíření alokace VRAM

> **Poznámka**: Tento krok proveďte na všech čtyřech strojích (Stroj 1 až Stroj 4).

### Konfigurace paměti pro spouštění velkých modelů

Na Linuxu využívá ROCm sdílenou poolovou systémovou paměť, přičemž tato pool je ve výchozím nastavení konfigurována na polovinu systémové paměti.

Toto množství lze zvětšit změnou nastavení stránky Translation Table Manager (TTM) jádra podle následujících pokynů. AMD doporučuje nastavit minimální vyhrazenou VRAM v BIOSu (0,5 GB).

* Nainstalujte nástroj pipx a přidejte cestu k wheelům nainstalovaným přes pipx do systémové vyhledávací cesty.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Nainstalujte wheel amd-debug-tools z PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Spusťte nástroj amd-ttm pro zjištění aktuálního nastavení sdílené paměti.
  ```bash
  amd-ttm
  ```

* Přenastavte sdílenou paměť na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Restartujte systém, aby se změny projevily.

## Inicializace kontejneru vLLM

> **Poznámka**: Tento krok proveďte na všech čtyřech strojích (Stroj 1 až Stroj 4).

Váš Ryzen AI Halo je dodáván s vLLM zabaleným uvnitř předpřipraveného kontejnerového obrazu, který spouštíte pomocí Podman, bezplatného open source nástroje pro kontejnery.

### 1. Vytvoření adresáře pro stahování modelů

Při obsluze modelu Qwen3.5-397B v tomto návodu vLLM automaticky stáhne váhy modelu do vašeho systému. Aby byly tyto váhy dostupné zevnitř kontejneru, nejprve vytvořte adresář pro modely, který lze do kontejneru připojit:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Spuštění kontejneru vLLM

Níže uvedený příkaz spustí kontejner a přenese vás do interaktivního shellu. Připojuje adresář pro modely, který jste právě vytvořili, a předává váš `IFNAME` proměnným `NCCL_SOCKET_IFNAME` a `GLOO_SOCKET_IFNAME`, čímž sděluje RCCL (knihovně, kterou vLLM používá ke koordinaci GPU napříč clusterem), které rozhraní má použít.

Spusťte kontejner pomocí:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Poznámka**: Nahraďte `<IFNAME>` názvem výstupního rozhraní z [1. Zjištění síťových rozhraní](#1-determine-network-interfaces)

## Spuštění modelu na clusteru

vLLM používá Ray k orchestraci clusteru a RCCL ke zpracování komunikace mezi GPU napříč uzly. Jeden stroj funguje jako hlavní uzel (Stroj 1), který koordinuje inferenci. Další tři se připojují jako pracovní uzly (Stroje 2, 3 a 4), přispívajíce svou pamětí GPU a výpočetním výkonem.

> **Poznámka**: Ray je volitelná závislost vLLM a je dostupný pouze z předkonfigurovaného kontejneru Podman.

Při spuštění vLLM rozdělí model napříč všemi čtyřmi uzly pomocí tensor paralelismu. Jakmile je model načten, inference probíhá, jako by běžela na jediném akcelerátoru.

#### Prevence chyb Ray OOM

Ray ve výchozím nastavení monitoruje paměť hostitele na každém uzlu a ukončí největší proces, jakmile využití paměti překročí 95 %. Na vašem Ryzen™ AI Halo sdílí GPU a hostitel jeden pool paměti, takže načítání modelu může spustit chybu `ray.exceptions.OutOfMemoryError` a ukončit pracovní proces.

Abychom tomu zabránili, nastavíme proměnnou `RAY_memory_monitor_refresh_ms=0` na každém stroji před spuštěním a připojením do clusteru.
### Krok 1: Spuštění hlavního uzlu Ray (Stroj 1)

Na Stroji 1 spusťte hlavní uzel Ray a inicializujte tak cluster:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Zjištění `<MACHINE_1_IP>`**: Na Stroji 1 spusťte příkaz `hostname -I | awk '{print $1}'` a zjistíte tak jeho lokální IP adresu.

### Krok 2: Připojení ke clusteru (Stroje 2, 3 a 4)

Na každém ze Strojů 2, 3 a 4 se připojte k hlavnímu uzlu a vytvořte tak cluster:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_N_IP> --num-gpus=1
```

> **Zjištění `<MACHINE_N_IP>`**: Na každém pracovním stroji spusťte příkaz `hostname -I | awk '{print $1}'` a zjistíte tak jeho lokální IP adresu.

### Krok 3: Spuštění modelu (Stroj 1)

Na Stroji 1 spusťte server vLLM. Ten automaticky stáhne model a začne jej poskytovat napříč všemi čtyřmi uzly:

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

#### Přehled parametrů

| Příznak | Účel |
|------|---------|
| `--port` | Port, na kterém je poskytováno HTTP API |
| `--host` | IP adresa, na kterou se server naváže (`0.0.0.0` pro všechna rozhraní) |
| `--max-model-len` | Maximální délka kontextu v tokenech |
| `--gpu-memory-utilization` | Podíl paměti GPU, který se má přidělit (0,0–1,0) |
| `--dtype` | Datový typ pro váhy modelu |
| `--tensor-parallel-size` | Počet GPU, mezi které se má model rozdělit (nastavte na celkový počet GPU v clusteru) |
| `--distributed-executor-backend` | Backend pro vícestrojové spouštění (`ray` pro clusterová nasazení) |
| `--enforce-eager` | Vypne kompilaci CUDA grafů kvůli kompatibilitě |
| `--language-model-only` | Přeskočí načítání pomocných komponent modelu (např. vizuálního enkodéru) |
| `--reasoning-parser` | Zapne strukturované parsování výstupu uvažování modelu |

Úplný popis použití parametrů najdete v [dokumentaci vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Přístup k modelu

vLLM poskytuje API kompatibilní s OpenAI, takže k vašemu clusteru můžete připojit libovolného kompatibilního klienta nebo rozhraní. Jednou z oblíbených možností je [Open WebUI](https://github.com/open-webui/open-webui), které poskytuje chatovací rozhraní v prohlížeči.

Pro připojení Open WebUI k vašemu koncovému bodu vLLM:

1. Otevřete **Settings** > **Admin Panel** > **Connections**
2. Klikněte na **+** u **Manage OpenAI API Connections**
3. Nastavte **Connection Type** na **External**
4. Nastavte **URL** na `http://<MACHINE_1_IP>:7000/v1`
5. V sekci **Auth** vyberte z rozbalovací nabídky **None**
6. Pole **Model IDs** ponechte prázdné, aby se automaticky zjistily všechny modely z daného koncového bodu

> **Zjištění `<MACHINE_1_IP>`**: Na Stroji 1 spusťte příkaz `hostname -I | awk '{print $1}'` a zjistíte tak jeho lokální IP adresu. Pokud přistupujete k Open WebUI přímo ze Stroje 1, můžete použít `http://localhost:7000/v1`.

![Nastavení připojení Open WebUI pro koncový bod vLLM](assets/openwebui-connection.png)

Po připojení vyberte model z rozbalovací nabídky modelů v Open WebUI a začněte chatovat. Model nyní běží napříč všemi čtyřmi uzly Ryzen AI Halo:

![Konverzace s Qwen3.5-397B v Open WebUI](assets/openwebui-chat.png)

## Další kroky

- **Prozkoumejte další modely**: Objevte nové modely na [Hugging Face](https://huggingface.co/models?&sort=trending), které se vejdou do celkové kapacity paměti GPU vašeho clusteru
- **Rozšiřte cluster nad rámec čtyř uzlů**: Přidejte další systémy Ryzen AI Halo jako další pracovní uzly Ray a rozdělte modely mezi ještě více GPU. Na každém dalším pracovním stroji postupujte podle [Kroku 2: Připojení ke clusteru](#step-2-join-the-cluster-machines-2-3-and-4) a odpovídajícím způsobem zvyšte hodnotu `--tensor-parallel-size`
- **Vyzkoušejte další strategie paralelizace**: vLLM podporuje [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) pro modely typu mixture-of-experts a [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) pro vyšší propustnost. Vyzkoušejte `--enable-expert-parallel` a `--data-parallel-size` a najděte nejlepší konfiguraci pro svou pracovní zátěž