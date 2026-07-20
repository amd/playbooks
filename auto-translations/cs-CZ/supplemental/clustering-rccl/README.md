<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Tento playbook používá speciální značky, které GitHub neumí vykreslit. Pro správné zobrazení tohoto obsahu prosím navštivte [amd.com/playbooks](https://amd.com/playbooks).
<!-- @github-only:end -->

# Clustering dvou Ryzen™ AI Halo pomocí RCCL

## Přehled

Váš Ryzen™ AI Halo už dokáže spouštět velké jazykové modely lokálně. Clustering jde ještě dál – kombinuje paměť GPU více systémů přes lokální síť, což vám umožní pracovat s ještě většími modely s lepším uvažováním, kvalitnějším generováním kódu a hlubším víceresazykovým porozuměním, a to zcela na vašem vlastním hardwaru.

Tento playbook vás naučí, jak clusterovat dva systémy Ryzen AI Halo pomocí RCCL (ROCm Communication Collectives Library) s vLLM a spustit model Qwen3.5-397B, model se 397 miliardami parametrů, napříč oběma stroji s akcelerací ROCm.

## Co se naučíte

- Jak rozšířit alokaci VRAM na systémech Ryzen AI Halo
- Spuštění vLLM s podporou ROCm
- Konfiguraci RCCL pro multi-node tensor-paralelní inferenci napříč dvěma systémy Ryzen AI Halo
- Spuštění modelu se 397 miliardami parametrů napříč dvěma propojenými systémy Ryzen AI Halo

## Požadavky

### Hardware

Tento playbook vyžaduje dvě jednotky Ryzen AI Halo a jeden ethernetový switch, propojené v topologii hvězdy, kde je každá jednotka připojena přímo ke switchi.

| Komponenta | Množství | Popis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Výpočetní uzly tvořící cluster |
| 10Gbps ethernetový switch | 1 | Centrální switch umožňující komunikaci mezi více uzly Ryzen AI Halo (alespoň 2 porty) |
| Ethernetový kabel | 2 | Připojuje každou jednotku Halo ke switchi (doporučen Cat 7 nebo vyšší) |

> **Poznámka**: Pro propojení dvou jednotek Ryzen AI Halo jsou potřeba dva porty ethernetového switche. Třetí port je potřeba, pokud k modelu přistupujete ze samostatného klientského počítače namísto z jedné z jednotek Halo.

### Software
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fyzická instalace hardwaru

> **Poznámka**: Tento krok proveďte na obou strojích, Machine 1 i Machine 2.

Připojte každou jednotku Ryzen AI Halo k ethernetovému switchi pomocí kabelu Cat 7 (nebo vyššího). Tím se vytvoří 10Gbps spojení používané pro vysokorychlostní komunikaci mezi uzly.

### 1. Zjištění síťových rozhraní

Na každém stroji zjistěte název jeho síťového rozhraní a poznamenejte si ho (v dalších pokynech se na něj bude odkazovat jako na `IFNAME`). Spusťte:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Tím se přímo vypíše název rozhraní, například:

```bash
enp191s0
```

### 2. Ověření rychlosti síťového spojení

Potvrďte, že je spojení aktivní a běží na plné rychlosti, zkontrolováním rychlosti vašeho rozhraní:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Poznámka**: Nahraďte `<IFNAME>` výstupním názvem rozhraní z kroku [1. Zjištění síťových rozhraní](#1-determine-network-interfaces)

Měli byste vidět rychlost `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Poznámka**: Pokud je rychlost nižší než `10000Mb/s` nebo se spojení nenaváže, zkontrolujte kabelové připojení a ujistěte se, že je port switche nastaven na 10Gbps. Některé switche vyžadují vypnutí automatické negociace a ruční nastavení rychlosti spojení; postupujte podle dokumentace svého switche.

## Rozšíření alokace VRAM

> **Poznámka**: Tento krok proveďte na obou strojích, Machine 1 i Machine 2.

### Konfigurace paměti pro spouštění velkých modelů

V systému Linux využívá ROCm sdílený fond systémové paměti, který je ve výchozím nastavení nakonfigurován na polovinu systémové paměti.

Toto množství lze zvýšit změnou nastavení stránek Translation Table Manager (TTM) v jádře podle následujících pokynů. AMD doporučuje nastavit minimální vyhrazenou VRAM v BIOSu (0,5 GB).

* Nainstalujte nástroj pipx a přidejte cestu k balíčkům instalovaným pomocí pipx do systémové cesty pro vyhledávání.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Nainstalujte balíček amd-debug-tools z PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Spusťte nástroj amd-ttm pro zjištění aktuálního nastavení sdílené paměti.
  ```bash
  amd-ttm
  ```

* Nastavte znovu velikost sdílené paměti na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Restartujte systém, aby se změny projevily.

## Inicializace kontejneru vLLM

> **Poznámka**: Tento krok proveďte na obou strojích, Machine 1 i Machine 2.

Váš Ryzen AI Halo je dodáván s vLLM zabaleným uvnitř předpřipraveného image kontejneru, který spouštíte pomocí Podman, bezplatného open source nástroje pro kontejnery.

### 1. Vytvoření adresáře pro stahování modelu

Když v tomto playbooku spustíte model Qwen3.5-397B, vLLM automaticky stáhne váhy modelu do vašeho systému. Aby byly tyto váhy dostupné i uvnitř kontejneru, nejprve vytvořte adresář pro modely, který lze do kontejneru připojit:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Spuštění kontejneru vLLM

Následující příkaz spustí kontejner a přepne vás do interaktivního shellu. Připojí adresář pro modely, který jste právě vytvořili, a předá vaše `IFNAME` proměnným `NCCL_SOCKET_IFNAME` a `GLOO_SOCKET_IFNAME`, čímž sdělí RCCL (knihovně, kterou vLLM používá pro koordinaci GPU napříč clusterem), které rozhraní má použít.

Spusťte kontejner pomocí:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Poznámka**: Nahraďte `<IFNAME>` výstupním názvem rozhraní z kroku [1. Zjištění síťových rozhraní](#1-determine-network-interfaces)

## Spuštění modelu na clusteru

vLLM používá Ray k orchestraci clusteru a RCCL ke zpracování komunikace mezi GPU napříč uzly. Jeden stroj funguje jako **hlavní uzel** (Machine 1) a koordinuje inferenci. Druhý se připojí jako **pracovní uzel** (Machine 2) a přispívá svou pamětí GPU a výpočetním výkonem.

> **Poznámka**: Ray je volitelná závislost pro vLLM a je dostupná pouze v rámci předkonfigurovaného kontejneru Podman.

Při spuštění vLLM rozdělí model mezi oba uzly pomocí tensor paralelismu. Po načtení probíhá inference stejně, jako by běžela na jediném akcelerátoru.

### Krok 1: Spuštění hlavního uzlu Ray (Machine 1)

Na Machine 1 spusťte hlavní uzel Ray a inicializujte cluster:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Zjištění `<MACHINE_1_IP>`**: Na Machine 1 spusťte `hostname -I | awk '{print $1}'` a zjistěte jeho lokální IP adresu.
### Krok 2: Připojení ke clusteru (Machine 2)

Na Machine 2 se připojte k hlavnímu uzlu a vytvořte cluster:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Zjištění `<MACHINE_2_IP>`**: Na Machine 2 spusťte `hostname -I | awk '{print $1}'`, čímž zjistíte její lokální IP adresu.

### Krok 3: Nasazení modelu (Machine 1)

Na Machine 1 spusťte server vLLM. Ten automaticky stáhne model a začne jej obsluhovat napříč oběma uzly:

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
| `--port` | Port, na kterém bude HTTP API obsluhováno |
| `--host` | IP adresa, na kterou se má server navázat (`0.0.0.0` pro všechna rozhraní) |
| `--max-model-len` | Maximální délka kontextu v tokenech |
| `--gpu-memory-utilization` | Podíl paměti GPU, který se má alokovat (0,0–1,0) |
| `--dtype` | Datový typ vah modelu |
| `--tensor-parallel-size` | Počet GPU, mezi které se má model rozdělit (nastavte na celkový počet GPU v clusteru) |
| `--distributed-executor-backend` | Backend pro vícenodové spuštění (`ray` pro nasazení v clusteru) |
| `--enforce-eager` | Zakáže kompilaci CUDA grafů kvůli kompatibilitě |
| `--language-model-only` | Přeskočí načítání pomocných komponent modelu (např. vision enkodéru) |
| `--reasoning-parser` | Povolí strukturované zpracování výstupu uvažování modelu |

Úplný přehled parametrů najdete v [dokumentaci vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Přístup k modelu

vLLM poskytuje API kompatibilní s OpenAI, takže ke svému clusteru můžete připojit libovolného kompatibilního klienta nebo rozhraní. Jednou z oblíbených možností je [Open WebUI](https://github.com/open-webui/open-webui), které poskytuje chatovací rozhraní přístupné z prohlížeče.

Pro připojení Open WebUI k vašemu endpointu vLLM:

1. Otevřete **Settings** > **Admin Panel** > **Connections**
2. Klikněte na **+** u položky **Manage OpenAI API Connections**
3. Nastavte **Connection Type** na **External**
4. Nastavte **URL** na `http://<MACHINE_1_IP>:7000/v1`
5. V sekci **Auth** vyberte z rozbalovací nabídky **None**
6. Ponechte **Model IDs** prázdné, aby se automaticky vyhledaly všechny modely z daného endpointu

> **Zjištění `<MACHINE_1_IP>`**: Na Machine 1 spusťte `hostname -I | awk '{print $1}'`, čímž zjistíte její lokální IP adresu. Pokud přistupujete k Open WebUI přímo z Machine 1, můžete použít `http://localhost:7000/v1`.

![Nastavení připojení Open WebUI k endpointu vLLM](assets/openwebui-connection.png)

Po připojení vyberte model z rozbalovací nabídky modelů v Open WebUI a začněte chatovat. Model nyní běží napříč oběma vašimi uzly Ryzen AI Halo:

![Chatování s Qwen3.5-397B v Open WebUI](assets/openwebui-chat.png)

## Další kroky

- **Vyzkoušejte další modely**: Objevte nové modely na [Hugging Face](https://huggingface.co/models?&sort=trending), které se vejdou do kombinované paměti GPU vašeho clusteru
- **Rozšiřte na čtyři uzly**: Přidejte další dva systémy Ryzen AI Halo jako další pracovní uzly Ray, abyste mohli rozdělit modely mezi ještě více GPU. To vyžaduje ethernetový přepínač alespoň se čtyřmi porty, jedním pro každý uzel. Na každém dalším pracovním uzlu postupujte podle [Kroku 2: Připojení ke clusteru](#step-2-join-the-cluster-machine-2) a odpovídajícím způsobem zvyšte hodnotu `--tensor-parallel-size`
- **Vyzkoušejte další strategie paralelismu**: vLLM podporuje [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) pro modely typu mixture-of-experts a [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) pro vyšší propustnost. Vyzkoušejte `--enable-expert-parallel` a `--data-parallel-size`, abyste našli nejlepší konfiguraci pro svou zátěž