<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Klastrovanie dvoch Ryzen™ AI Halo pomocou RCCL

## Prehľad

Váš Ryzen™ AI Halo je už schopný spúšťať veľké jazykové modely lokálne. Klastrovanie to posúva ďalej tým, že kombinuje GPU pamäť viacerých systémov cez lokálnu sieť, čím získate prístup k ešte väčším modelom so silnejším uvažovaním, lepším generovaním kódu a hlbším viacjazyčným porozumením – všetko výhradne na vašom vlastnom hardvéri.

Tento playbook vás naučí, ako zklastrovať dva systémy Ryzen AI Halo pomocou RCCL (ROCm Communication Collectives Library) s vLLM a spustiť Qwen3.5-397B, model s 397 miliardami parametrov, naprieč oboma strojmi s akceleráciou ROCm.

## Čo sa naučíte

- Ako rozšíriť alokáciu VRAM na systémoch Ryzen AI Halo
- Spustenie vLLM s podporou ROCm
- Konfigurácia RCCL pre viacuzlovú tensor-paralelnú inferenciu naprieč dvoma systémami Ryzen AI Halo
- Spustenie modelu s 397 miliardami parametrov naprieč dvoma sieťovo prepojenými systémami Ryzen AI Halo

## Predpoklady

### Hardvér

Tento playbook vyžaduje dve jednotky Ryzen AI Halo a jeden ethernetový prepínač, prepojené v hviezdicovej topológii, pričom každá jednotka je priamo zapojená do prepínača.

| Komponent | Množstvo | Popis |
|-----------|----------|-------|
| Ryzen AI Halo | 2 | Výpočtové uzly tvoriace klaster |
| 10Gbps ethernetový prepínač | 1 | Centrálny prepínač umožňujúci komunikáciu viacerých uzlov Ryzen AI Halo (minimálne 2 porty) |
| Ethernetový kábel | 2 | Prepája každú jednotku Halo s prepínačom (odporúča sa Cat 7 alebo vyšší) |

> **Poznámka**: Na prepojenie dvoch jednotiek Ryzen AI Halo sú potrebné dva porty ethernetového prepínača. Tretí port je potrebný, ak pristupujete k modelu zo samostatného klientského stroja namiesto z jednej z jednotiek Halo.

### Softvér
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fyzické nastavenie hardvéru

> **Poznámka**: Tento krok vykonajte na Stroji 1 aj Stroji 2.

Pripojte každú jednotku Ryzen AI Halo k ethernetovému prepínači pomocou kábla Cat 7 (alebo vyššieho). Tým sa vytvorí 10Gbps linka používaná na vysokorýchlostnú komunikáciu medzi uzlami.

### 1. Určenie sieťových rozhraní

Na každom stroji nájdite názov jeho sieťového rozhrania a poznačte si ho (v ďalších pokynoch bude označovaný ako `IFNAME`). Spustite:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Tým sa priamo vypíše názov rozhrania, napríklad:

```bash
enp191s0
```

### 2. Overenie rýchlostí sieťového spojenia

Potvrďte, že spojenie je aktívne a beží na plnej rýchlosti, skontrolovaním rýchlosti vášho rozhrania:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Poznámka**: Nahraďte `<IFNAME>` názvom výstupného rozhrania z kroku [1. Určenie sieťových rozhraní](#1-determine-network-interfaces)

Mali by ste vidieť rýchlosť `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Poznámka**: Ak je rýchlosť nižšia ako `10000Mb/s` alebo spojenie nenabehne, skontrolujte pripojenie kábla a overte, či je port prepínača nastavený na 10Gbps. Niektoré prepínače vyžadujú vypnutie automatického vyjednávania a manuálne nastavenie rýchlosti spojenia; pozrite si dokumentáciu vášho prepínača.

## Rozšírenie alokácie VRAM

> **Poznámka**: Tento krok vykonajte na Stroji 1 aj Stroji 2.

### Konfigurácia pamäte pre spúšťanie veľkých modelov

V systéme Linux ROCm využíva zdieľaný systémový pamäťový fond, ktorý je predvolene nakonfigurovaný na polovicu systémovej pamäte.

Toto množstvo je možné zvýšiť zmenou nastavenia stránky Translation Table Manager (TTM) jadra podľa nasledujúcich pokynov. AMD odporúča nastaviť minimálnu dedikovanú VRAM v BIOS-e (0,5 GB).

* Nainštalujte nástroj pipx a pridajte cestu pre kolieska nainštalované cez pipx do systémovej vyhľadávacej cesty.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Nainštalujte koliesko amd-debug-tools z PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Spustite nástroj amd-ttm na dotaz aktuálnych nastavení zdieľanej pamäte.
  ```bash
  amd-ttm
  ```

* Prekonfigurujte nastavenia zdieľanej pamäte na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Reštartujte systém, aby sa zmeny prejavili.

## Inicializácia kontajnera vLLM

> **Poznámka**: Tento krok vykonajte na Stroji 1 aj Stroji 2.

Váš Ryzen AI Halo sa dodáva s vLLM zabaleným v predpripravenom obraze kontajnera, ktorý spúšťate pomocou Podman – bezplatného nástroja na správu kontajnerov s otvoreným zdrojovým kódom.

### 1. Vytvorenie adresára na sťahovanie modelov

Keď v tomto playbooku spustíte model Qwen3.5-397B, vLLM automaticky stiahne váhy modelu do vášho systému. Aby boli tieto váhy dostupné zvnútra kontajnera, najprv vytvorte adresár modelov, ktorý môže kontajner pripojiť:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Spustenie kontajnera vLLM

Príkaz nižšie spustí kontajner a prepne vás do interaktívneho shellu. Pripojí adresár modelov, ktorý ste práve vytvorili, a odovzdá váš `IFNAME` do `NCCL_SOCKET_IFNAME` a `GLOO_SOCKET_IFNAME`, čím informuje RCCL (knižnicu, ktorú vLLM používa na koordináciu GPU naprieč klastrom), ktoré rozhranie má použiť.

Spustite kontajner pomocou:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Poznámka**: Nahraďte `<IFNAME>` názvom výstupného rozhrania z kroku [1. Určenie sieťových rozhraní](#1-determine-network-interfaces)

## Spustenie modelu na klastri

vLLM používa Ray na orchestráciu klastra a RCCL na zabezpečenie komunikácie GPU-GPU naprieč uzlami. Jeden stroj funguje ako **hlavný uzol** (Stroj 1) a koordinuje inferenciu. Druhý sa pripája ako **pracovný uzol** (Stroj 2) a prispieva svojou GPU pamäťou a výpočtovým výkonom.

> **Poznámka**: Ray je voliteľná závislosť pre vLLM a je dostupná iba zvnútra predkonfigurovaného kontajnera Podman.

Pri spustení vLLM rozdelí model naprieč oboma uzlami pomocou tenzorového paralelizmu. Po načítaní prebieha inferencia, akoby bežala na jednom akcelerátore.

### Krok 1: Spustenie hlavného uzla Ray (Stroj 1)

Na Stroji 1 spustite hlavný uzol Ray na inicializáciu klastra:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Nájdenie `<MACHINE_1_IP>`**: Na Stroji 1 spustite `hostname -I | awk '{print $1}'` na zistenie jeho lokálnej IP adresy.

### Krok 2: Pripojenie ku klastra (Stroj 2)

Na Stroji 2 sa pripojte k hlavnému uzlu a vytvorte klaster:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Nájdenie `<MACHINE_2_IP>`**: Na Stroji 2 spustite `hostname -I | awk '{print $1}'` na zistenie jeho lokálnej IP adresy.

### Krok 3: Spustenie modelu (Stroj 1)

Na Stroji 1 spustite server vLLM. Automaticky stiahne model a začne ho obsluhovať naprieč oboma uzlami:

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
|---------|------|
| `--port` | Port, na ktorom sa obsluhuje HTTP API |
| `--host` | IP adresa, na ktorú sa server viaže (`0.0.0.0` pre všetky rozhrania) |
| `--max-model-len` | Maximálna dĺžka kontextu v tokenoch |
| `--gpu-memory-utilization` | Podiel GPU pamäte na alokáciu (0,0–1,0) |
| `--dtype` | Dátový typ pre váhy modelu |
| `--tensor-parallel-size` | Počet GPU, naprieč ktorými sa model rozdelí (nastavte na celkový počet GPU v klastri) |
| `--distributed-executor-backend` | Backend pre viacuzlovú exekúciu (`ray` pre nasadenia v klastri) |
| `--enforce-eager` | Vypína kompiláciu grafov CUDA pre kompatibilitu |
| `--language-model-only` | Preskočí načítanie pomocných komponentov modelu (napr. vizuálny enkodér) |
| `--reasoning-parser` | Umožňuje štruktúrované parsovanie výstupu uvažovania pre model |

Úplné použitie parametrov nájdete v [dokumentácii vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Prístup k modelu

vLLM sprístupňuje API kompatibilné s OpenAI, takže k vášmu klastra môžete pripojiť akéhokoľvek kompatibilného klienta alebo rozhranie. Jednou z obľúbených možností je [Open WebUI](https://github.com/open-webui/open-webui), ktorý poskytuje chatové rozhranie v prehliadači.

Na pripojenie Open WebUI k vášmu koncovému bodu vLLM:

1. Otvorte **Nastavenia** > **Administrátorský panel** > **Pripojenia**
2. Kliknite na **+** pri **Spravovať pripojenia OpenAI API**
3. Nastavte **Typ pripojenia** na **Externé**
4. Nastavte **URL** na `http://<MACHINE_1_IP>:7000/v1`
5. V časti **Auth** vyberte z rozbaľovacieho zoznamu **Žiadne**
6. Ponechajte **ID modelov** prázdne, aby sa automaticky objavili všetky modely z koncového bodu

> **Nájdenie `<MACHINE_1_IP>`**: Na Stroji 1 spustite `hostname -I | awk '{print $1}'` na zistenie jeho lokálnej IP adresy. Ak pristupujete k Open WebUI zo Stroja 1, môžete použiť `http://localhost:7000/v1`.

![Nastavenia pripojenia Open WebUI pre koncový bod vLLM](assets/openwebui-connection.png)

Po pripojení vyberte model z rozbaľovacieho zoznamu modelov v Open WebUI a začnite chatovať. Model teraz beží naprieč oboma vašimi uzlami Ryzen AI Halo:

![Chatovanie s Qwen3.5-397B v Open WebUI](assets/openwebui-chat.png)

## Ďalšie kroky

- **Preskúmajte ďalšie modely**: Objavte nové modely na [Hugging Face](https://huggingface.co/models?&sort=trending), ktoré sa zmestia do kombinovanej GPU pamäte vášho klastra
- **Rozšírte na štyri uzly**: Pridajte ďalšie dva systémy Ryzen AI Halo ako dodatočných pracovníkov Ray na rozdelenie modelov naprieč ešte viacerými GPU. Vyžaduje to ethernetový prepínač s minimálne štyrmi portmi, po jednom pre každý uzol. Postupujte podľa [Kroku 2: Pripojenie ku klastra](#step-2-join-the-cluster-machine-2) na každom ďalšom pracovnom uzle a zodpovedajúcim spôsobom zvýšte `--tensor-parallel-size`
- **Vyskúšajte iné stratégie paralelizmu**: vLLM podporuje [expertný paralelizmus](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) pre modely mixture-of-experts a [dátový paralelizmus](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) pre vyššiu priepustnosť. Experimentujte s `--enable-expert-parallel` a `--data-parallel-size` na nájdenie najlepšej konfigurácie pre vaše pracovné zaťaženie