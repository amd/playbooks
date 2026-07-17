<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Clustering dvou Ryzen™ AI Halo pomocí RCCL

## Přehled

Váš Ryzen™ AI Halo je již schopen lokálně spouštět velké jazykové modely. Clustering to posouvá dále tím, že kombinuje paměť GPU více systémů přes lokální síť, čímž získáte přístup k ještě větším modelům se silnějším uvažováním, lepším generováním kódu a hlubším vícejazyčným porozuměním – vše zcela na vlastním hardwaru.

Tento playbook vás naučí, jak propojit dva systémy Ryzen AI Halo do clusteru pomocí RCCL (ROCm Communication Collectives Library) s vLLM a spustit Qwen3.5-397B, model s 397 miliardami parametrů, na obou strojích s akcelerací ROCm.

## Co se naučíte

- Jak rozšířit alokaci VRAM na systémech Ryzen AI Halo
- Spouštění vLLM s podporou ROCm
- Konfigurace RCCL pro víceuzlové tensor-paralelní inference napříč dvěma systémy Ryzen AI Halo
- Spuštění modelu s 397 miliardami parametrů napříč dvěma propojenými systémy Ryzen AI Halo

## Předpoklady

### Hardware

Tento playbook vyžaduje dvě jednotky Ryzen AI Halo a jeden ethernetový switch, zapojené v hvězdicové topologii, přičemž každá jednotka je přímo připojena ke switchi.

| Komponenta | Množství | Popis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Výpočetní uzly tvořící cluster |
| 10Gbps ethernetový switch | 1 | Centrální switch umožňující komunikaci mezi uzly Ryzen AI Halo (alespoň 2 porty) |
| Ethernetový kabel | 2 | Propojuje každou jednotku Halo se switchem (doporučeno Cat 7 nebo vyšší) |

> **Poznámka**: Pro připojení dvou jednotek Ryzen AI Halo jsou potřeba dva porty ethernetového switche. Třetí port je nutný, pokud přistupujete k modelu ze samostatného klientského stroje místo z jedné z jednotek Halo.

### Software
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fyzické nastavení hardwaru

> **Poznámka**: Tento krok proveďte na obou strojích – Machine 1 i Machine 2.

Připojte každou jednotku Ryzen AI Halo k ethernetovému switchi pomocí kabelu Cat 7 (nebo vyššího). Tím se vytvoří 10Gbps linka používaná pro vysokorychlostní komunikaci mezi uzly.

### 1. Zjistěte síťová rozhraní

Na každém stroji zjistěte název jeho síťového rozhraní a poznamenejte si ho (ve zbytku pokynů bude označováno jako `IFNAME`). Spusťte:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Tím se přímo vypíše název rozhraní, například:

```bash
enp191s0
```

### 2. Ověřte rychlosti síťového spojení

Potvrďte, že linka je aktivní a běží na plné rychlosti, kontrolou rychlosti vašeho rozhraní:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Poznámka**: Nahraďte `<IFNAME>` názvem výstupního rozhraní z části [1. Zjistěte síťová rozhraní](#1-determine-network-interfaces)

Měli byste vidět rychlost `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Poznámka**: Pokud je rychlost nižší než `10000Mb/s` nebo linka nenabíhá, zkontrolujte připojení kabelu a ověřte, zda je port switche nastaven na 10Gbps. Některé switche vyžadují vypnutí automatického vyjednávání a ruční nastavení rychlosti linky; viz dokumentaci vašeho switche.

## Rozšíření alokace VRAM

> **Poznámka**: Tento krok proveďte na obou strojích – Machine 1 i Machine 2.

### Konfigurace paměti pro spouštění velkých modelů

V systému Linux ROCm využívá sdílený systémový paměťový pool, který je ve výchozím nastavení nakonfigurován na polovinu systémové paměti.

Toto množství lze zvýšit změnou nastavení stránky Translation Table Manager (TTM) jádra pomocí následujících pokynů. AMD doporučuje nastavit minimální vyhrazenou VRAM v BIOSu (0,5 GB).

* Nainstalujte nástroj pipx a přidejte cestu pro kola nainstalovaná přes pipx do systémové vyhledávací cesty.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Nainstalujte kolo amd-debug-tools z PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Spusťte nástroj amd-ttm pro dotaz na aktuální nastavení sdílené paměti.
  ```bash
  amd-ttm
  ```

* Překonfigurujte nastavení sdílené paměti na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Restartujte systém, aby se změny projevily.

## Inicializace kontejneru vLLM

> **Poznámka**: Tento krok proveďte na obou strojích – Machine 1 i Machine 2.

Váš Ryzen AI Halo je dodáván s vLLM zabaleným v předem připraveném obrazu kontejneru, který spouštíte pomocí Podman – bezplatného nástroje pro kontejnery s otevřeným zdrojovým kódem.

### 1. Vytvořte adresář pro stahování modelů

Při obsluze modelu Qwen3.5-397B v tomto playbooku vLLM automaticky stáhne váhy modelu do vašeho systému. Aby byly tyto váhy přístupné zevnitř kontejneru, nejprve vytvořte adresář models, který může kontejner připojit:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Spusťte kontejner vLLM

Níže uvedený příkaz spustí kontejner a přenese vás do interaktivního shellu. Připojí adresář models, který jste právě vytvořili, a předá váš `IFNAME` do `NCCL_SOCKET_IFNAME` a `GLOO_SOCKET_IFNAME`, čímž RCCL (knihovně, kterou vLLM používá ke koordinaci GPU napříč clusterem) sdělí, které rozhraní má použít.

Spusťte kontejner pomocí:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Poznámka**: Nahraďte `<IFNAME>` názvem výstupního rozhraní z části [1. Zjistěte síťová rozhraní](#1-determine-network-interfaces)

## Spuštění modelu na clusteru

vLLM používá Ray k orchestraci clusteru a RCCL ke zpracování komunikace GPU-GPU napříč uzly. Jeden stroj funguje jako **hlavní uzel** (Machine 1) a koordinuje inference. Druhý se připojuje jako **pracovní uzel** (Machine 2) a přispívá svou pamětí GPU a výpočetním výkonem.

> **Poznámka**: Ray je volitelná závislost pro vLLM a je dostupná pouze zevnitř předkonfigurovaného kontejneru Podman.

Při spuštění vLLM rozdělí model napříč oběma uzly pomocí tenzorového paralelismu. Po načtení probíhá inference, jako by běžela na jediném akcelerátoru.

### Krok 1: Spusťte hlavní uzel Ray (Machine 1)

Na Machine 1 spusťte hlavní uzel Ray pro inicializaci clusteru:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Nalezení `<MACHINE_1_IP>`**: Na Machine 1 spusťte `hostname -I | awk '{print $1}'` pro zjištění jeho lokální IP adresy.

### Krok 2: Připojte se ke clusteru (Machine 2)

Na Machine 2 se připojte k hlavnímu uzlu a vytvořte cluster:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Nalezení `<MACHINE_2_IP>`**: Na Machine 2 spusťte `hostname -I | awk '{print $1}'` pro zjištění jeho lokální IP adresy.

### Krok 3: Spusťte obsluhu modelu (Machine 1)

Na Machine 1 spusťte server vLLM. Ten automaticky stáhne model a začne ho obsluhovat napříč oběma uzly:

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
| `--port` | Port, na kterém bude obslouženo HTTP API |
| `--host` | IP adresa, na které bude server naslouchat (`0.0.0.0` pro všechna rozhraní) |
| `--max-model-len` | Maximální délka kontextu v tokenech |
| `--gpu-memory-utilization` | Podíl paměti GPU k alokaci (0,0–1,0) |
| `--dtype` | Datový typ pro váhy modelu |
| `--tensor-parallel-size` | Počet GPU, přes které se model rozdělí (nastavte na celkový počet GPU v clusteru) |
| `--distributed-executor-backend` | Backend pro víceuzlové spouštění (`ray` pro nasazení v clusteru) |
| `--enforce-eager` | Zakáže kompilaci grafu CUDA pro zajištění kompatibility |
| `--language-model-only` | Přeskočí načítání pomocných komponent modelu (např. vizuálního enkodéru) |
| `--reasoning-parser` | Umožňuje strukturované parsování výstupu uvažování pro model |

Úplné použití parametrů naleznete v [dokumentaci vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Přístup k modelu

vLLM zpřístupňuje API kompatibilní s OpenAI, takže ke svému clusteru můžete připojit jakéhokoli kompatibilního klienta nebo rozhraní. Jednou z oblíbených možností je [Open WebUI](https://github.com/open-webui/open-webui), které poskytuje chatovací rozhraní v prohlížeči.

Připojení Open WebUI k vašemu endpointu vLLM:

1. Otevřete **Nastavení** > **Panel správce** > **Připojení**
2. Klikněte na **+** u **Správa připojení OpenAI API**
3. Nastavte **Typ připojení** na **Externí**
4. Nastavte **URL** na `http://<MACHINE_1_IP>:7000/v1`
5. V části **Ověření** vyberte z rozbalovací nabídky **Žádné**
6. Pole **ID modelů** ponechte prázdné pro automatické zjištění všech modelů z endpointu

> **Nalezení `<MACHINE_1_IP>`**: Na Machine 1 spusťte `hostname -I | awk '{print $1}'` pro zjištění jeho lokální IP adresy. Pokud přistupujete k Open WebUI přímo z Machine 1, můžete použít `http://localhost:7000/v1`.

![Nastavení připojení Open WebUI pro endpoint vLLM](assets/openwebui-connection.png)

Po připojení vyberte model z rozbalovací nabídky modelů v Open WebUI a začněte chatovat. Model nyní běží napříč oběma uzly Ryzen AI Halo:

![Chatování s Qwen3.5-397B v Open WebUI](assets/openwebui-chat.png)

## Další kroky

- **Prozkoumejte další modely**: Objevte nové modely na [Hugging Face](https://huggingface.co/models?&sort=trending), které se vejdou do kombinované paměti GPU vašeho clusteru
- **Rozšiřte na čtyři uzly**: Přidejte další dva systémy Ryzen AI Halo jako další pracovní uzly Ray pro rozdělení modelů napříč ještě více GPU. To vyžaduje ethernetový switch s alespoň čtyřmi porty, po jednom pro každý uzel. Postupujte podle [Kroku 2: Připojte se ke clusteru](#step-2-join-the-cluster-machine-2) na každém dalším pracovním uzlu a odpovídajícím způsobem zvyšte `--tensor-parallel-size`
- **Vyzkoušejte jiné strategie paralelismu**: vLLM podporuje [expertní paralelismus](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) pro modely mixture-of-experts a [datový paralelismus](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) pro vyšší propustnost. Experimentujte s `--enable-expert-parallel` a `--data-parallel-size` pro nalezení nejlepší konfigurace pro vaši pracovní zátěž