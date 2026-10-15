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

# Klastrovanie dvoch Ryzen™ AI Halo pomocou RCCL

## Prehľad

Váš Ryzen™ AI Halo je už schopný lokálne spúšťať veľké jazykové modely. Klastrovanie posúva túto možnosť ešte ďalej tým, že spája GPU pamäť viacerých systémov cez lokálnu sieť, čím vám poskytuje prístup k ešte väčším modelom so silnejším uvažovaním, lepším generovaním kódu a hlbším viacjazyčným porozumením, a to úplne na vašom vlastnom hardvéri.

Táto príručka vás naučí, ako klastrovať dva systémy Ryzen AI Halo pomocou RCCL (ROCm Communication Collectives Library) s vLLM a spustiť Qwen3.5-397B, model so 397 miliardami parametrov, naprieč oboma zariadeniami s akceleráciou ROCm.

## Čo sa naučíte

- Ako rozšíriť alokáciu VRAM na systémoch Ryzen AI Halo
- Spustenie vLLM s podporou ROCm
- Konfiguráciu RCCL pre multi-node tensor-parallel inferenciu naprieč dvoma systémami Ryzen AI Halo
- Spustenie modelu so 397 miliardami parametrov naprieč dvoma prepojenými systémami Ryzen AI Halo

## Predpoklady

### Hardvér

Táto príručka vyžaduje dve jednotky Ryzen AI Halo a jeden ethernetový switch, prepojené v hviezdicovej topológii, pričom každá jednotka je pripojená priamo k switchu.

| Komponent | Množstvo | Popis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Výpočtové uzly tvoriace klaster |
| 10 Gb/s ethernetový switch | 1 | Centrálny switch umožňujúci komunikáciu medzi viacerými uzlami Ryzen AI Halo (aspoň 2 porty) |
| Ethernetový kábel | 2 | Pripája každú jednotku Halo k switchu (odporúča sa Cat 7 alebo vyšší) |

> **Poznámka**: Na pripojenie dvoch jednotiek Ryzen AI Halo sú potrebné dva porty ethernetového switchu. Tretí port je potrebný, ak k modelu pristupujete zo samostatného klientskeho zariadenia namiesto z jednej z jednotiek Halo.

### Softvér
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Nastavenie fyzického hardvéru

> **Poznámka**: Tento krok vykonajte na Zariadení 1 aj Zariadení 2.

Pripojte každú jednotku Ryzen AI Halo k ethernetovému switchu pomocou kábla Cat 7 (alebo vyššej kategórie). Tým sa vytvorí 10 Gb/s spojenie používané na vysokorýchlostnú komunikáciu medzi uzlami.

### 1. Zistenie sieťových rozhraní

Na každom zariadení zistite názov jeho sieťového rozhrania a poznamenajte si ho (v ďalších pokynoch sa naň bude odkazovať ako `IFNAME`). Spustite:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Toto vypíše priamo názov rozhrania, napríklad:

```bash
enp191s0
```

### 2. Overenie rýchlosti sieťového spojenia

Potvrďte, že je spojenie aktívne a beží plnou rýchlosťou, kontrolou rýchlosti vášho rozhrania:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Poznámka**: Nahraďte `<IFNAME>` názvom výstupného rozhrania z časti [1. Zistenie sieťových rozhraní](#1-determine-network-interfaces)

Mali by ste vidieť rýchlosť `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Poznámka**: Ak je rýchlosť nižšia ako `10000Mb/s` alebo sa spojenie nenadviaže, skontrolujte pripojenie kábla a potvrďte, že je port switcha nastavený na 10 Gb/s. Niektoré switche vyžadujú vypnutie automatického vyjednávania a manuálne nastavenie rýchlosti spojenia; pozrite si dokumentáciu vášho switcha.

## Rozšírenie alokácie VRAM

> **Poznámka**: Tento krok vykonajte na Zariadení 1 aj Zariadení 2.

### Konfigurácia pamäte pre spúšťanie veľkých modelov

V systéme Linux využíva ROCm zdieľaný pool systémovej pamäte, ktorý je predvolene nastavený na polovicu systémovej pamäte.

Toto množstvo je možné zvýšiť zmenou nastavenia stránok Translation Table Manager (TTM) jadra podľa nasledujúcich pokynov. AMD odporúča nastaviť minimálnu vyhradenú VRAM v BIOSe (0,5 GB).

* Nainštalujte nástroj pipx a pridajte cestu k balíčkom (wheels) nainštalovaným cez pipx do systémovej vyhľadávacej cesty.

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

* Zmeňte nastavenie zdieľanej pamäte na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Reštartujte systém, aby sa zmeny prejavili.

## Inicializácia kontajnera vLLM

> **Poznámka**: Tento krok vykonajte na Zariadení 1 aj Zariadení 2.

Váš Ryzen AI Halo obsahuje vLLM zabalené v predpripravenom kontajnerovom obraze, ktorý spúšťate pomocou nástroja Podman, bezplatného open source nástroja na prácu s kontajnermi.

### 1. Vytvorenie adresára pre sťahovanie modelu

Keď v tejto príručke spustíte model Qwen3.5-397B, vLLM automaticky stiahne váhy modelu do vášho systému. Aby boli tieto váhy prístupné z vnútra kontajnera, najprv vytvorte adresár pre modely, ktorý bude možné do kontajnera pripojiť:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Spustenie kontajnera vLLM

Nasledujúci príkaz spustí kontajner a prenesie vás do interaktívneho shellu. Pripojí adresár pre modely, ktorý ste práve vytvorili, a odovzdá vaše `IFNAME` premenným `NCCL_SOCKET_IFNAME` a `GLOO_SOCKET_IFNAME`, čím oznámi RCCL (knižnici, ktorú vLLM používa na koordináciu GPU naprieč klastrom), ktoré rozhranie sa má použiť.

Spustite kontajner pomocou:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Poznámka**: Nahraďte `<IFNAME>` názvom výstupného rozhrania z časti [1. Zistenie sieťových rozhraní](#1-determine-network-interfaces)

## Spustenie modelu na klastri

vLLM používa Ray na orchestráciu klastra a RCCL na spracovanie komunikácie medzi GPU naprieč uzlami. Jedno zariadenie funguje ako **hlavný uzol (head node)** (Zariadenie 1), ktorý koordinuje inferenciu. Druhé sa pripája ako **pracovný uzol (worker node)** (Zariadenie 2), ktorý prispieva svojou pamäťou GPU a výpočtovým výkonom.

> **Poznámka**: Ray je voliteľná závislosť pre vLLM a je dostupný len z vnútra predkonfigurovaného kontajnera Podman.

Pri spustení vLLM rozdelí model naprieč oboma uzlami pomocou tensor-parallelizmu. Po načítaní prebieha inferencia tak, ako keby bežala na jednom akcelerátore.

#### Predchádzanie chybám Ray OOM

Ray predvolene monitoruje pamäť hostiteľa na každom uzle a ukončí najväčší proces, keď využitie pamäte prekročí 95 %. Na vašom Ryzen™ AI Halo zdieľajú GPU a hostiteľ jeden spoločný pool pamäte, takže načítanie modelu môže vyvolať chybu `ray.exceptions.OutOfMemoryError` a ukončiť pracovný proces.

Aby sme tomu predišli, pred spustením a pripojením sa ku klastru exportujeme na každom zariadení premennú `RAY_memory_monitor_refresh_ms=0`.
### Krok 1: Spustenie hlavného uzla Ray (Machine 1)

Na Machine 1 spustite hlavný uzol Ray na inicializáciu klastra:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Zistenie `<MACHINE_1_IP>`**: Na Machine 1 spustite `hostname -I | awk '{print $1}'`, aby ste zistili jeho lokálnu IP adresu.

### Krok 2: Pripojenie do klastra (Machine 2)

Na Machine 2 sa pripojte k hlavnému uzlu, aby ste vytvorili klaster:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Zistenie `<MACHINE_2_IP>`**: Na Machine 2 spustite `hostname -I | awk '{print $1}'`, aby ste zistili jeho lokálnu IP adresu.

### Krok 3: Poskytovanie modelu (Machine 1)

Na Machine 1 spustite server vLLM. Toto automaticky stiahne model a začne ho poskytovať naprieč oboma uzlami:

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

#### Referencia parametrov

| Príznak | Účel |
|------|---------|
| `--port` | Port, na ktorom sa poskytuje HTTP API |
| `--host` | IP adresa, na ktorú sa server naviaže (`0.0.0.0` pre všetky rozhrania) |
| `--max-model-len` | Maximálna dĺžka kontextu v tokenoch |
| `--gpu-memory-utilization` | Podiel pamäte GPU, ktorý sa má alokovať (0,0 – 1,0) |
| `--dtype` | Dátový typ pre váhy modelu |
| `--tensor-parallel-size` | Počet GPU, medzi ktoré sa má model rozdeliť (nastavte na celkový počet GPU v klastri) |
| `--distributed-executor-backend` | Backend pre viacuzlové vykonávanie (`ray` pre nasadenia v klastri) |
| `--enforce-eager` | Vypne kompiláciu CUDA grafov kvôli kompatibilite |
| `--language-model-only` | Preskočí načítanie pomocných komponentov modelu (napr. vizuálneho enkodéra) |
| `--reasoning-parser` | Zapne parsovanie štruktúrovaného výstupu uvažovania pre model |

Úplný popis použitia parametrov nájdete v [dokumentácii vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Prístup k modelu

vLLM poskytuje API kompatibilné s OpenAI, takže k svojmu klastru môžete pripojiť ľubovoľného kompatibilného klienta alebo rozhranie. Jednou z obľúbených možností je [Open WebUI](https://github.com/open-webui/open-webui), ktoré poskytuje chatovacie rozhranie v prehliadači.

Ak chcete pripojiť Open WebUI k svojmu koncovému bodu vLLM:

1. Otvorte **Settings** > **Admin Panel** > **Connections**
2. Kliknite na **+** v časti **Manage OpenAI API Connections**
3. Nastavte **Connection Type** na **External**
4. Nastavte **URL** na `http://<MACHINE_1_IP>:7000/v1`
5. V časti **Auth** vyberte z rozbaľovacej ponuky možnosť **None**
6. Ponechajte **Model IDs** prázdne, aby sa automaticky zistili všetky modely z koncového bodu

> **Zistenie `<MACHINE_1_IP>`**: Na Machine 1 spustite `hostname -I | awk '{print $1}'`, aby ste zistili jeho lokálnu IP adresu. Ak pristupujete k Open WebUI priamo z Machine 1, môžete použiť `http://localhost:7000/v1`.

![Nastavenia pripojenia Open WebUI pre koncový bod vLLM](assets/openwebui-connection.png)

Po pripojení vyberte model z rozbaľovacieho zoznamu modelov v Open WebUI a začnite konverzovať. Model teraz beží naprieč oboma vašimi uzlami Ryzen AI Halo:

![Konverzácia s Qwen3.5-397B v Open WebUI](assets/openwebui-chat.png)

## Ďalšie kroky

- **Preskúmajte ďalšie modely**: Objavte nové modely na [Hugging Face](https://huggingface.co/models?&sort=trending), ktoré sa zmestia do kombinovanej pamäte GPU vášho klastra
- **Rozšírenie na štyri uzly**: Pridajte ďalšie dva systémy Ryzen AI Halo ako ďalšie pracovné uzly Ray, aby ste mohli rozdeliť modely medzi ešte viac GPU. Toto vyžaduje ethernetový switch s aspoň štyrmi portami, jedným pre každý uzol. Na každom ďalšom pracovnom uzle postupujte podľa [Krok 2: Pripojenie do klastra](#step-2-join-the-cluster-machine-2) a podľa toho zvýšte `--tensor-parallel-size`
- **Vyskúšajte iné stratégie paralelizmu**: vLLM podporuje [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) pre modely typu mixture-of-experts a [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) pre vyššiu priepustnosť. Experimentujte s `--enable-expert-parallel` a `--data-parallel-size`, aby ste našli najlepšiu konfiguráciu pre svoju záťaž