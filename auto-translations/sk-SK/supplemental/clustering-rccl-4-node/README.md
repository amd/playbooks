<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré pokyny, príkazy, súbory na stiahnutie, dostupnosť produktov alebo iný obsah sa môžu líšiť v závislosti od jazyka alebo regiónu. V prípade akéhokoľvek nesúladu alebo rozdielu je rozhodujúca a záväzná pôvodná anglická verzia playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Clustrovanie štyroch Ryzen™ AI Halo pomocou RCCL

## Prehľad

Váš Ryzen™ AI Halo je už schopný lokálne spúšťať veľké jazykové modely. Clustrovanie posúva túto schopnosť ešte ďalej tým, že kombinuje GPU pamäť viacerých systémov cez lokálnu sieť, čím vám poskytuje prístup k ešte väčším modelom so silnejším uvažovaním, lepším generovaním kódu a hlbším viacjazyčným porozumením, a to všetko výlučne na vašom vlastnom hardvéri.

Tento návod vás naučí, ako naklastrovať štyri systémy Ryzen AI Halo pomocou RCCL (ROCm Communication Collectives Library) spolu s vLLM a ako na všetkých štyroch strojoch spustiť Qwen3.5-397B, model so 397B parametrami, s akceleráciou ROCm.

## Čo sa naučíte

- Ako rozšíriť alokáciu VRAM na systémoch Ryzen AI Halo
- Spúšťanie vLLM s podporou ROCm
- Konfiguráciu RCCL pre multi-node tensorovo paralelnú inferenciu naprieč štyrmi systémami Ryzen AI Halo
- Spúšťanie modelu so 397B parametrami naprieč štyrmi sieťovo prepojenými systémami Ryzen AI Halo

## Predpoklady

### Hardvér

Tento návod vyžaduje štyri jednotky Ryzen AI Halo a jeden Ethernet switch, zapojené v topológii hviezda, pričom každá jednotka je priamo prepojená so switchom.

| Komponent | Množstvo | Popis |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Výpočtové uzly, ktoré tvoria cluster |
| 10Gbps Ethernet switch | 1 | Centrálny switch umožňujúci komunikáciu medzi uzlami Ryzen AI Halo (minimálne 4 porty) |
| Ethernet kábel | 4 | Prepája každú jednotku Halo so switchom (odporúča sa Cat 7 alebo vyšší) |

> **Poznámka**: Na pripojenie štyroch jednotiek Ryzen AI Halo sú potrebné štyri porty Ethernet switchu. Piaty port je potrebný, ak k modelu pristupujete zo samostatného klientskeho stroja namiesto z jednej z jednotiek Halo.

### Softvér
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fyzické nastavenie hardvéru

> **Poznámka**: Tento krok vykonajte na všetkých štyroch strojoch (Stroj 1 až Stroj 4).

Pripojte každú jednotku Ryzen AI Halo k Ethernet switchu pomocou kábla Cat 7 (alebo vyššieho). Tým sa vytvorí 10Gbps spojenie používané na vysokorýchlostnú komunikáciu medzi uzlami.

### 1. Zistenie sieťových rozhraní

Na každom stroji zistite názov jeho sieťového rozhrania a zapíšte si ho (v zvyšku pokynov sa naň bude odkazovať ako `IFNAME`). Spustite:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Toto priamo vypíše názov rozhrania, napríklad:

```bash
enp191s0
```

### 2. Overenie rýchlosti sieťového spojenia

Overte, že spojenie je aktívne a beží na plnej rýchlosti, kontrolou rýchlosti vášho rozhrania:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Poznámka**: Nahraďte `<IFNAME>` názvom výstupného rozhrania z [1. Zistenie sieťových rozhraní](#1-determine-network-interfaces)

Mali by ste vidieť rýchlosť `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Poznámka**: Ak je rýchlosť nižšia ako `10000Mb/s` alebo sa spojenie nenadviaže, skontrolujte pripojenie kábla a overte, či je port switchu nastavený na 10Gbps. Niektoré switche vyžadujú vypnutie automatického vyjednávania a manuálne nastavenie rýchlosti spojenia; postupujte podľa dokumentácie vášho switchu.

## Rozšírenie alokácie VRAM

> **Poznámka**: Tento krok vykonajte na všetkých štyroch strojoch (Stroj 1 až Stroj 4).

### Konfigurácia pamäte pre spúšťanie veľkých modelov

V systéme Linux ROCm využíva zdieľaný pool systémovej pamäte, ktorý je štandardne nakonfigurovaný na polovicu systémovej pamäte.

Toto množstvo je možné zvýšiť zmenou nastavenia stránok Translation Table Manager (TTM) jadra podľa nasledujúcich pokynov. AMD odporúča nastaviť minimálnu vyhradenú VRAM v BIOSe (0,5 GB).

* Nainštalujte nástroj pipx a pridajte cestu pre pipx nainštalované balíčky (wheels) do systémovej vyhľadávacej cesty.

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

> **Poznámka**: Tento krok vykonajte na všetkých štyroch strojoch (Stroj 1 až Stroj 4).

Váš Ryzen AI Halo sa dodáva s vLLM zabaleným vo vopred zostavenom kontajnerovom obraze, ktorý spúšťate pomocou Podman, bezplatného nástroja na správu kontajnerov s otvoreným zdrojovým kódom.

### 1. Vytvorenie adresára na sťahovanie modelu

Keď v tomto návode spustíte model Qwen3.5-397B, vLLM automaticky stiahne váhy modelu do vášho systému. Aby boli tieto váhy dostupné z vnútra kontajnera, najskôr vytvorte adresár models, ktorý môže kontajner pripojiť:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Spustenie kontajnera vLLM

Príkaz nižšie spustí kontajner a presunie vás do interaktívneho shellu. Pripojí adresár models, ktorý ste práve vytvorili, a odovzdá váš `IFNAME` do premenných `NCCL_SOCKET_IFNAME` a `GLOO_SOCKET_IFNAME`, čím oznámi RCCL (knižnici, ktorú vLLM používa na koordináciu GPU naprieč clusterom), ktoré rozhranie má použiť.

Spustite kontajner pomocou:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Poznámka**: Nahraďte `<IFNAME>` názvom výstupného rozhrania z [1. Zistenie sieťových rozhraní](#1-determine-network-interfaces)

## Spustenie modelu na clusteri

vLLM používa Ray na orchestráciu clusteru a RCCL na zabezpečenie komunikácie medzi GPU naprieč uzlami. Jeden stroj funguje ako hlavný uzol (Stroj 1), ktorý koordinuje inferenciu. Ostatné tri sa pripájajú ako pracovné uzly (Stroje 2, 3 a 4), pričom prispievajú svojou GPU pamäťou a výpočtovým výkonom.

> **Poznámka**: Ray je voliteľná závislosť pre vLLM a je dostupný iba z vnútra preddefinovaného kontajnera Podman.

Pri spustení vLLM rozdelí model naprieč všetkými štyrmi uzlami pomocou tensorového paralelizmu. Po načítaní prebieha inferencia, akoby bežala na jedinom akcelerátore.

#### Predchádzanie chybám Ray OOM

V predvolenom nastavení Ray sleduje pamäť hostiteľa na každom uzle a ukončí najväčší proces, keď využitie pamäte prekročí 95 %. Na vašom Ryzen™ AI Halo zdieľa GPU a hostiteľ jeden spoločný pool pamäte, takže načítanie modelu môže vyvolať `ray.exceptions.OutOfMemoryError` a ukončiť pracovný proces.

Aby sme tomu predišli, pred spustením a pripojením ku clusteru exportujeme na každom stroji `RAY_memory_monitor_refresh_ms=0`.
### Krok 1: Spustenie hlavného uzla Ray (Stroj 1)

Na stroji 1 spustite hlavný uzol Ray, aby ste inicializovali klaster:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Zistenie `<MACHINE_1_IP>`**: Na stroji 1 spustite príkaz `hostname -I | awk '{print $1}'`, aby ste zistili jeho lokálnu IP adresu.

### Krok 2: Pripojenie ku klastru (Stroje 2, 3 a 4)

Na každom zo strojov 2, 3 a 4 sa pripojte k hlavnému uzlu, aby ste vytvorili klaster:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_N_IP> --num-gpus=1
```

> **Zistenie `<MACHINE_N_IP>`**: Na každom pracovnom stroji spustite príkaz `hostname -I | awk '{print $1}'`, aby ste zistili jeho lokálnu IP adresu.

### Krok 3: Nasadenie modelu (Stroj 1)

Na stroji 1 spustite server vLLM. Tento automaticky stiahne model a začne ho poskytovať naprieč všetkými štyrmi uzlami:

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

#### Referencia parametrov

| Príznak | Účel |
|------|---------|
| `--port` | Port, na ktorom sa poskytuje HTTP API |
| `--host` | IP adresa, na ktorú sa server naviaže (`0.0.0.0` pre všetky rozhrania) |
| `--max-model-len` | Maximálna dĺžka kontextu v tokenoch |
| `--gpu-memory-utilization` | Podiel pamäte GPU, ktorý sa má alokovať (0,0–1,0) |
| `--dtype` | Dátový typ pre váhy modelu |
| `--tensor-parallel-size` | Počet GPU, medzi ktoré sa model rozdelí (nastavte na celkový počet GPU v klastri) |
| `--distributed-executor-backend` | Backend pre vykonávanie na viacerých uzloch (`ray` pre klastrové nasadenia) |
| `--enforce-eager` | Vypne kompiláciu CUDA grafov kvôli kompatibilite |
| `--language-model-only` | Preskočí načítanie pomocných komponentov modelu (napr. vizuálneho enkodéra) |
| `--reasoning-parser` | Zapne štruktúrované spracovanie výstupu uvažovania pre model |

Úplný popis použitia parametrov nájdete v [dokumentácii vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Prístup k modelu

vLLM poskytuje API kompatibilné s OpenAI, takže k vášmu klastru môžete pripojiť akéhokoľvek kompatibilného klienta alebo rozhranie. Jednou obľúbenou možnosťou je [Open WebUI](https://github.com/open-webui/open-webui), ktorý poskytuje chatovacie rozhranie v prehliadači.

Pripojenie Open WebUI k vášmu koncovému bodu vLLM:

1. Otvorte **Settings** > **Admin Panel** > **Connections**
2. Kliknite na **+** pri **Manage OpenAI API Connections**
3. Nastavte **Connection Type** na **External**
4. Nastavte **URL** na `http://<MACHINE_1_IP>:7000/v1`
5. V časti **Auth** vyberte z rozbaľovacieho zoznamu **None**
6. Ponechajte **Model IDs** prázdne, aby sa automaticky zistili všetky modely z koncového bodu

> **Zistenie `<MACHINE_1_IP>`**: Na stroji 1 spustite príkaz `hostname -I | awk '{print $1}'`, aby ste zistili jeho lokálnu IP adresu. Ak pristupujete k Open WebUI priamo zo stroja 1, môžete použiť `http://localhost:7000/v1`.

![Nastavenia pripojenia Open WebUI pre koncový bod vLLM](assets/openwebui-connection.png)

Po pripojení vyberte model z rozbaľovacieho zoznamu modelov v Open WebUI a začnite chatovať. Model teraz beží naprieč všetkými štyrmi vašimi uzlami Ryzen AI Halo:

![Chatovanie s Qwen3.5-397B v Open WebUI](assets/openwebui-chat.png)

## Ďalšie kroky

- **Preskúmajte ďalšie modely**: Objavte nové modely na [Hugging Face](https://huggingface.co/models?&sort=trending), ktoré sa zmestia do kombinovanej pamäte GPU vášho klastra
- **Rozšírenie nad rámec štyroch uzlov**: Pridajte ďalšie systémy Ryzen AI Halo ako ďalších pracovníkov Ray, aby ste mohli rozdeľovať modely medzi ešte viac GPU. Postupujte podľa [Krok 2: Pripojenie ku klastru](#step-2-join-the-cluster-machines-2-3-and-4) na každom ďalšom pracovnom stroji a podľa toho zvýšte `--tensor-parallel-size`
- **Vyskúšajte ďalšie stratégie paralelizmu**: vLLM podporuje [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) pre modely typu mixture-of-experts a [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) pre vyššiu priepustnosť. Experimentujte s `--enable-expert-parallel` a `--data-parallel-size`, aby ste našli najlepšiu konfiguráciu pre vašu záťaž