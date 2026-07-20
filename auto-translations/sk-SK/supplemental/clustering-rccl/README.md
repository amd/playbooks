<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Tento návod používa špeciálne značky, ktoré GitHub nedokáže vykresliť. Navštívte prosím [amd.com/playbooks](https://amd.com/playbooks), aby sa vám tento obsah zobrazil správne.
<!-- @github-only:end -->

# Clustrovanie dvoch systémov Ryzen™ AI Halo pomocou RCCL

## Prehľad

Váš Ryzen™ AI Halo je už teraz schopný lokálne spúšťať veľké jazykové modely. Clustrovanie posúva túto možnosť ešte ďalej tým, že kombinuje pamäť GPU viacerých systémov cez lokálnu sieť, čím vám poskytuje prístup k ešte väčším modelom so silnejším uvažovaním, lepším generovaním kódu a hlbším porozumením viacerým jazykom, a to výhradne na vašom vlastnom hardvéri.

Tento návod vás naučí, ako vytvoriť cluster dvoch systémov Ryzen AI Halo pomocou RCCL (ROCm Communication Collectives Library) s vLLM a spustiť Qwen3.5-397B, model so 397 miliardami parametrov, na oboch strojoch súčasne s akceleráciou ROCm.

## Čo sa naučíte

- Ako rozšíriť pridelenie VRAM na systémoch Ryzen AI Halo
- Spúšťanie vLLM s podporou ROCm
- Konfigurácia RCCL pre viacuzlové tenzorovo-paralelné odvodzovanie naprieč dvoma systémami Ryzen AI Halo
- Spustenie modelu so 397 miliardami parametrov naprieč dvoma sieťovo prepojenými systémami Ryzen AI Halo

## Predpoklady

### Hardvér

Tento návod vyžaduje dve jednotky Ryzen AI Halo a jeden ethernetový switch, zapojené v topológii hviezdy, pričom každá jednotka je pripojená priamo k switchu.

| Komponent | Množstvo | Popis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Výpočtové uzly tvoriace cluster |
| 10Gbps ethernetový switch | 1 | Centrálny switch umožňujúci komunikáciu medzi viacerými uzlami Ryzen AI Halo (aspoň 2 porty) |
| Ethernetový kábel | 2 | Prepája každú jednotku Halo so switchom (odporúča sa kategória Cat 7 alebo vyššia) |

> **Poznámka**: Na prepojenie dvoch jednotiek Ryzen AI Halo sú potrebné dva porty ethernetového switchu. Tretí port je potrebný, ak pristupujete k modelu zo samostatného klientskeho zariadenia namiesto jednej z jednotiek Halo.

### Softvér
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fyzické nastavenie hardvéru

> **Poznámka**: Tento krok vykonajte na oboch strojoch – Machine 1 aj Machine 2.

Pripojte každú jednotku Ryzen AI Halo k ethernetovému switchu pomocou kábla kategórie Cat 7 (alebo vyššej). Tým sa vytvorí 10Gbps spojenie používané na vysokorýchlostnú komunikáciu medzi uzlami.

### 1. Zistenie sieťových rozhraní

Na každom stroji zistite názov jeho sieťového rozhrania a poznačte si ho (v zvyšku pokynov sa naň bude odkazovať ako `IFNAME`). Spustite:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Toto priamo vypíše názov rozhrania, napríklad:

```bash
enp191s0
```

### 2. Overenie rýchlosti sieťového pripojenia

Overte, že spojenie je aktívne a beží plnou rýchlosťou, kontrolou rýchlosti vášho rozhrania:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Poznámka**: Nahraďte `<IFNAME>` názvom výstupného rozhrania z kroku [1. Zistenie sieťových rozhraní](#1-determine-network-interfaces)

Mali by ste vidieť rýchlosť `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Poznámka**: Ak je rýchlosť nižšia ako `10000Mb/s` alebo sa spojenie nenadviaže, skontrolujte pripojenie kábla a overte, či je port switchu nastavený na 10Gbps. Niektoré switche vyžadujú deaktiváciu automatického vyjednávania a manuálne nastavenie rýchlosti spojenia; postupujte podľa dokumentácie svojho switchu.

## Rozšírenie pridelenia VRAM

> **Poznámka**: Tento krok vykonajte na oboch strojoch – Machine 1 aj Machine 2.

### Konfigurácia pamäte pre spúšťanie veľkých modelov

V systéme Linux ROCm využíva zdieľaný pool systémovej pamäte, ktorý je predvolene nakonfigurovaný na polovicu systémovej pamäte.

Toto množstvo je možné zvýšiť zmenou nastavenia stránok Translation Table Manager (TTM) jadra podľa nasledujúcich pokynov. AMD odporúča nastaviť minimálnu vyhradenú VRAM v BIOS-e (0,5 GB).

* Nainštalujte nástroj pipx a pridajte cestu k balíčkom (wheels) nainštalovaným pomocou pipx do systémovej vyhľadávacej cesty.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Nainštalujte balíček amd-debug-tools z PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Spustite nástroj amd-ttm na zistenie aktuálneho nastavenia zdieľanej pamäte.
  ```bash
  amd-ttm
  ```

* Prekonfigurujte nastavenia zdieľanej pamäte na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Reštartujte systém, aby sa zmeny prejavili.

## Inicializácia kontajnera vLLM

> **Poznámka**: Tento krok vykonajte na oboch strojoch – Machine 1 aj Machine 2.

Váš Ryzen AI Halo obsahuje vLLM zabalené v predpripravenom obraze kontajnera, ktorý spúšťate pomocou nástroja Podman, bezplatného open source nástroja na správu kontajnerov.

### 1. Vytvorenie adresára na sťahovanie modelov

Keď v tomto návode spustíte model Qwen3.5-397B, vLLM automaticky stiahne váhy modelu do vášho systému. Aby boli tieto váhy dostupné z vnútra kontajnera, najprv vytvorte adresár pre modely, ktorý bude môcť kontajner pripojiť:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Spustenie kontajnera vLLM

Nasledujúci príkaz spustí kontajner a presunie vás do interaktívneho shellu. Pripája adresár pre modely, ktorý ste práve vytvorili, a odovzdáva váš `IFNAME` premenným `NCCL_SOCKET_IFNAME` a `GLOO_SOCKET_IFNAME`, čím oznamuje RCCL (knižnici, ktorú vLLM používa na koordináciu GPU naprieč clustrom), ktoré rozhranie má použiť.

Spustite kontajner príkazom:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Poznámka**: Nahraďte `<IFNAME>` názvom výstupného rozhrania z kroku [1. Zistenie sieťových rozhraní](#1-determine-network-interfaces)

## Spustenie modelu na clustri

vLLM využíva Ray na orchestráciu clustra a RCCL na zabezpečenie komunikácie medzi GPU naprieč uzlami. Jeden stroj funguje ako **hlavný uzol** (Machine 1), ktorý koordinuje odvodzovanie. Druhý sa pripája ako **pracovný uzol** (Machine 2) a prispieva svojou pamäťou GPU a výpočtovým výkonom.

> **Poznámka**: Ray je voliteľná závislosť pre vLLM a je dostupná iba z vnútra vopred nakonfigurovaného kontajnera Podman.

Pri spustení vLLM rozdelí model naprieč oboma uzlami pomocou tenzorového paralelizmu. Po načítaní odvodzovanie prebieha, akoby bežalo na jedinom akcelerátore.

### Krok 1: Spustenie hlavného uzla Ray (Machine 1)

Na stroji Machine 1 spustite hlavný uzol Ray na inicializáciu clustra:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Zistenie `<MACHINE_1_IP>`**: Na stroji Machine 1 spustite `hostname -I | awk '{print $1}'`, aby ste zistili jeho lokálnu IP adresu.
### Krok 2: Pripojenie ku klastru (Zariadenie 2)

Na Zariadení 2 sa pripojte k hlavnému uzlu a vytvorte klaster:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Zisťovanie `<MACHINE_2_IP>`**: Na Zariadení 2 spustite príkaz `hostname -I | awk '{print $1}'`, aby ste zistili jeho lokálnu IP adresu.

### Krok 3: Sprístupnenie modelu (Zariadenie 1)

Na Zariadení 1 spustite server vLLM. Tým sa automaticky stiahne model a začne sa jeho sprístupňovanie naprieč oboma uzlami:

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

#### Prehľad parametrov

| Príznak | Účel |
|------|---------|
| `--port` | Port, na ktorom sa sprístupňuje HTTP API |
| `--host` | IP adresa, na ktorú sa server naviaže (`0.0.0.0` pre všetky rozhrania) |
| `--max-model-len` | Maximálna dĺžka kontextu v tokenoch |
| `--gpu-memory-utilization` | Podiel pamäte GPU, ktorý sa má alokovať (0,0 – 1,0) |
| `--dtype` | Dátový typ pre váhy modelu |
| `--tensor-parallel-size` | Počet GPU, medzi ktoré sa má model rozdeliť (nastavte na celkový počet GPU v klastri) |
| `--distributed-executor-backend` | Backend pre spúšťanie na viacerých uzloch (`ray` pre nasadenia v klastri) |
| `--enforce-eager` | Vypína kompiláciu CUDA grafov kvôli kompatibilite |
| `--language-model-only` | Preskočí načítanie pomocných komponentov modelu (napr. vizuálneho enkodéra) |
| `--reasoning-parser` | Povolí štruktúrovaný výstup uvažovania (reasoning) pre model |

Úplný popis parametrov nájdete v [dokumentácii vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Prístup k modelu

vLLM poskytuje API kompatibilné s OpenAI, takže ku svojmu klastru môžete pripojiť ľubovoľného kompatibilného klienta alebo rozhranie. Jednou z obľúbených možností je [Open WebUI](https://github.com/open-webui/open-webui), ktoré poskytuje chatové rozhranie v prehliadači.

Ak chcete pripojiť Open WebUI k vášmu koncovému bodu vLLM:

1. Otvorte **Settings** > **Admin Panel** > **Connections**
2. Kliknite na **+** pri položke **Manage OpenAI API Connections**
3. Nastavte **Connection Type** na **External**
4. Nastavte **URL** na `http://<MACHINE_1_IP>:7000/v1`
5. V časti **Auth** vyberte z rozbaľovacieho zoznamu možnosť **None**
6. Ponechajte pole **Model IDs** prázdne, aby sa automaticky rozpoznali všetky modely z daného koncového bodu

> **Zisťovanie `<MACHINE_1_IP>`**: Na Zariadení 1 spustite príkaz `hostname -I | awk '{print $1}'`, aby ste zistili jeho lokálnu IP adresu. Ak pristupujete k Open WebUI priamo zo Zariadenia 1, môžete použiť `http://localhost:7000/v1`.

![Nastavenia pripojenia Open WebUI pre koncový bod vLLM](assets/openwebui-connection.png)

Po pripojení vyberte model z rozbaľovacieho zoznamu modelov v Open WebUI a začnite chatovať. Model teraz beží na oboch vašich uzloch Ryzen AI Halo:

![Chatovanie s Qwen3.5-397B v Open WebUI](assets/openwebui-chat.png)

## Ďalšie kroky

- **Preskúmajte ďalšie modely**: Objavte nové modely na [Hugging Face](https://huggingface.co/models?&sort=trending), ktoré sa zmestia do celkovej pamäte GPU vášho klastra
- **Rozšírenie na štyri uzly**: Pridajte ďalšie dva systémy Ryzen AI Halo ako dodatočné pracovné uzly (Ray workers) na rozdelenie modelov medzi ešte väčší počet GPU. To si vyžaduje ethernetový switch aspoň so štyrmi portmi, jeden pre každý uzol. Na každom ďalšom pracovnom uzle postupujte podľa [Kroku 2: Pripojenie ku klastru](#step-2-join-the-cluster-machine-2) a zodpovedajúco zvýšte hodnotu `--tensor-parallel-size`
- **Vyskúšajte ďalšie stratégie paralelizmu**: vLLM podporuje [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) pre modely typu mixture-of-experts a [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) pre vyššiu priepustnosť. Experimentujte s `--enable-expert-parallel` a `--data-parallel-size`, aby ste našli najlepšiu konfiguráciu pre svoju záťaž