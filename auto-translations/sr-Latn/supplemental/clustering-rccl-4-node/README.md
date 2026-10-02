<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Mašinski prevod.** Ova stranica je automatski prevedena sa engleskog jezika i nije proveravana od strane čoveka. Može sadržati greške, a određena uputstva, komande, preuzimanja, dostupnost proizvoda ili drugi sadržaj mogu se razlikovati u zavisnosti od jezika ili regiona. U slučaju bilo kakve nedoslednosti ili neslaganja, merodavna je originalna verzija playbook-a na engleskom jeziku.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Klasterovanje četiri Ryzen™ AI Halo sistema pomoću RCCL-a

## Pregled

Vaš Ryzen™ AI Halo već može lokalno da pokreće velike jezičke modele. Klasterovanje ovo podiže na viši nivo kombinovanjem GPU memorije više sistema preko lokalne mreže, čime dobijate pristup još većim modelima sa jačim rezonovanjem, boljim generisanjem koda i dubljim razumevanjem više jezika, a sve u potpunosti na sopstvenom hardveru.

Ovaj vodič vas uči kako da klasterujete četiri Ryzen AI Halo sistema koristeći RCCL (ROCm Communication Collectives Library) sa vLLM-om i pokrenete Qwen3.5-397B, model sa 397 milijardi parametara, na sve četiri mašine uz ROCm akceleraciju.

## Šta ćete naučiti

- Kako da proširite alokaciju VRAM-a na Ryzen AI Halo sistemima
- Pokretanje vLLM-a sa ROCm podrškom
- Konfigurisanje RCCL-a za tenzorski-paralelno zaključivanje na više čvorova preko četiri Ryzen AI Halo sistema
- Pokretanje modela sa 397 milijardi parametara na četiri umrežena Ryzen AI Halo sistema

## Preduslovi

### Hardver

Ovaj vodič zahteva četiri Ryzen AI Halo uređaja i jedan Ethernet switch, povezane u zvezdastu topologiju gde je svaki uređaj direktno povezan kablom sa switch-om.

| Komponenta | Količina | Opis |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Računarski čvorovi koji čine klaster |
| 10Gbps Ethernet switch | 1 | Centralni switch koji omogućava komunikaciju više Ryzen AI Halo čvorova (najmanje 4 porta) |
| Ethernet kabl | 4 | Povezuje svaki Halo uređaj sa switch-om (preporučuje se Cat 7 ili viši) |

> **Napomena**: Potrebna su četiri porta na Ethernet switch-u za povezivanje četiri Ryzen AI Halo uređaja. Peti port je potreban ako modelu pristupate sa posebne klijentske mašine umesto sa jednog od Halo uređaja.

### Softver
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Podešavanje fizičkog hardvera

> **Napomena**: Ovaj korak izvršite na sve četiri mašine (Mašina 1 do Mašine 4).

Povežite svaki Ryzen AI Halo uređaj sa Ethernet switch-om koristeći Cat 7 (ili viši) kabl. Ovim se uspostavlja 10Gbps veza koja se koristi za brzu komunikaciju između čvorova.

### 1. Utvrđivanje mrežnih interfejsa

Na svakoj mašini pronađite naziv njenog mrežnog interfejsa i zabeležite ga (u ostatku uputstva se naziva `IFNAME`). Pokrenite:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Ovo direktno ispisuje naziv interfejsa, na primer:

```bash
enp191s0
```

### 2. Provera brzine mrežne veze

Potvrdite da je veza aktivna i da radi punom brzinom proverom brzine vašeg interfejsa:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Napomena**: Zamenite `<IFNAME>` izlaznim nazivom interfejsa iz koraka [1. Utvrđivanje mrežnih interfejsa](#1-determine-network-interfaces)

Trebalo bi da vidite brzinu od `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Napomena**: Ako je brzina niža od `10000Mb/s` ili veza ne radi, proverite kablovsku vezu i potvrdite da je port na switch-u podešen na 10Gbps. Neki switch-evi zahtevaju da se auto-pregovaranje onemogući i brzina veze ručno podesi; pogledajte dokumentaciju vašeg switch-a.

## Proširivanje alokacije VRAM-a

> **Napomena**: Ovaj korak izvršite na sve četiri mašine (Mašina 1 do Mašine 4).

### Konfiguracija memorije za pokretanje velikih modela

Na Linux-u, ROCm koristi deljeni memorijski bazen sistema, a ovaj bazen je podrazumevano konfigurisan na polovinu memorije sistema.

Ova količina se može povećati promenom podešavanja Translation Table Manager (TTM) stranica u kernelu, prema sledećim uputstvima. AMD preporučuje da se u BIOS-u podesi minimalna namenska VRAM memorija (0.5 GB).

* Instalirajte pipx alat i dodajte putanju za pipx instalirane wheel-ove u sistemsku putanju pretrage.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Instalirajte amd-debug-tools wheel sa PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Pokrenite amd-ttm alat kako biste proverili trenutna podešavanja deljene memorije.
  ```bash
  amd-ttm
  ```

* Rekonfigurišite podešavanja deljene memorije na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Ponovo pokrenite sistem da bi promene stupile na snagu.

## Inicijalizacija vLLM kontejnera

> **Napomena**: Ovaj korak izvršite na sve četiri mašine (Mašina 1 do Mašine 4).

Vaš Ryzen AI Halo dolazi sa vLLM-om spakovanim unutar unapred izgrađene slike kontejnera, koju pokrećete pomoću Podman-a, besplatnog alata otvorenog koda za kontejnere.

### 1. Kreiranje direktorijuma za preuzimanje modela

Kada budete servirali Qwen3.5-397B model u ovom vodiču, vLLM će automatski preuzeti težine modela na vaš sistem. Da bi te težine bile dostupne iz kontejnera, prvo kreirajte direktorijum za modele koji kontejner može da montira:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Pokretanje vLLM kontejnera

Komanda ispod pokreće kontejner i prebacuje vas u interaktivnu ljusku. Montira direktorijum za modele koji ste upravo kreirali i prosleđuje vaš `IFNAME` promenljivama `NCCL_SOCKET_IFNAME` i `GLOO_SOCKET_IFNAME`, govoreći RCCL-u (biblioteci koju vLLM koristi za koordinaciju GPU-a širom klastera) koji interfejs da koristi.

Pokrenite kontejner sa:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Napomena**: Zamenite `<IFNAME>` izlaznim nazivom interfejsa iz koraka [1. Utvrđivanje mrežnih interfejsa](#1-determine-network-interfaces)

## Pokretanje modela na klasteru

vLLM koristi Ray za orkestraciju klastera i RCCL za upravljanje komunikacijom između GPU-a na različitim čvorovima. Jedna mašina ima ulogu glavnog čvora (Mašina 1), koordinišući zaključivanje. Ostale tri se pridružuju kao radni čvorovi (Mašine 2, 3 i 4), doprinoseći svojom GPU memorijom i procesorskom snagom.

> **Napomena**: Ray je opciona zavisnost za vLLM i dostupan je samo unutar unapred konfigurisanog Podman kontejnera.

Pri pokretanju, vLLM deli model na sve četiri čvora koristeći tenzorski paralelizam. Nakon učitavanja, zaključivanje se odvija kao da se izvršava na jednom akceleratoru.

#### Sprečavanje Ray OOM grešaka

Podrazumevano, Ray nadgleda memoriju hosta na svakom čvoru i prekida najveći proces kada upotreba memorije pređe 95%. Na vašem Ryzen™ AI Halo uređaju, GPU i host dele jedan bazen memorije, tako da učitavanje modela može da izazove `ray.exceptions.OutOfMemoryError` i prekine radni proces.

Da bismo ovo sprečili, izvešćemo (export) `RAY_memory_monitor_refresh_ms=0` na svakoj mašini pre pokretanja i pridruživanja klasteru.
### Korak 1: Pokretanje Ray glavnog čvora (Mašina 1)

Na Mašini 1 pokrenite Ray glavni čvor da biste inicijalizovali klaster:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Pronalaženje `<MACHINE_1_IP>`**: Na Mašini 1 pokrenite `hostname -I | awk '{print $1}'` da biste pronašli njenu lokalnu IP adresu.

### Korak 2: Pridruživanje klasteru (Mašine 2, 3 i 4)

Na svakoj od Mašina 2, 3 i 4 povežite se sa glavnim čvorom da biste formirali klaster:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_N_IP> --num-gpus=1
```

> **Pronalaženje `<MACHINE_N_IP>`**: Na svakoj radnoj mašini pokrenite `hostname -I | awk '{print $1}'` da biste pronašli njenu lokalnu IP adresu.

### Korak 3: Serviranje modela (Mašina 1)

Na Mašini 1 pokrenite vLLM server. Ovo će automatski preuzeti model i početi da ga servira na sva četiri čvora:

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

#### Referenca parametara

| Oznaka | Svrha |
|------|---------|
| `--port` | Port na kome se servira HTTP API |
| `--host` | IP adresa na koju se vezuje server (`0.0.0.0` za sve interfejse) |
| `--max-model-len` | Maksimalna dužina konteksta u tokenima |
| `--gpu-memory-utilization` | Udeo GPU memorije koji se alocira (0.0–1.0) |
| `--dtype` | Tip podataka za težine modela |
| `--tensor-parallel-size` | Broj GPU-ova preko kojih se model deli (postaviti na ukupan broj GPU-ova u klasteru) |
| `--distributed-executor-backend` | Pozadinski sistem za izvršavanje na više čvorova (`ray` za implementacije na klasteru) |
| `--enforce-eager` | Onemogućava kompilaciju CUDA grafova radi kompatibilnosti |
| `--language-model-only` | Preskače učitavanje pomoćnih komponenti modela (npr. enkoder za viziju) |
| `--reasoning-parser` | Omogućava strukturisano parsiranje izlaza rezonovanja za model |

Za potpuno korišćenje parametara, pogledajte [vLLM dokumentaciju](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Pristupanje modelu

vLLM izlaže API kompatibilan sa OpenAI, tako da možete povezati bilo kog kompatibilnog klijenta ili interfejs sa vašim klasterom. Jedna popularna opcija je [Open WebUI](https://github.com/open-webui/open-webui), koji pruža interfejs za ćaskanje zasnovan na pregledaču.

Da biste povezali Open WebUI sa vašim vLLM krajnjom tačkom:

1. Otvorite **Settings** > **Admin Panel** > **Connections**
2. Kliknite na **+** pored **Manage OpenAI API Connections**
3. Postavite **Connection Type** na **External**
4. Postavite **URL** na `http://<MACHINE_1_IP>:7000/v1`
5. U okviru **Auth**, izaberite **None** iz padajućeg menija
6. Ostavite **Model IDs** prazno da bi se automatski otkrili svi modeli sa krajnje tačke

> **Pronalaženje `<MACHINE_1_IP>`**: Na Mašini 1 pokrenite `hostname -I | awk '{print $1}'` da biste pronašli njenu lokalnu IP adresu. Ako pristupate Open WebUI sa same Mašine 1, možete koristiti `http://localhost:7000/v1`.

![Podešavanja Open WebUI konekcije za vLLM krajnju tačku](assets/openwebui-connection.png)

Nakon povezivanja, izaberite model iz padajućeg menija modela u Open WebUI i započnite ćaskanje. Model sada radi na sva četiri vaša Ryzen AI Halo čvora:

![Ćaskanje sa Qwen3.5-397B u Open WebUI](assets/openwebui-chat.png)

## Sledeći koraci

- **Istražite druge modele**: Pronađite nove modele na [Hugging Face](https://huggingface.co/models?&sort=trending) koji se uklapaju u kombinovanu GPU memoriju vašeg klastera
- **Proširite se preko četiri čvora**: Dodajte dodatne Ryzen AI Halo sisteme kao dodatne Ray radne čvorove da biste delili modele preko još više GPU-ova. Pratite [Korak 2: Pridruživanje klasteru](#step-2-join-the-cluster-machines-2-3-and-4) na svakom dodatnom radnom čvoru i povećajte `--tensor-parallel-size` u skladu s tim
- **Isprobajte druge strategije paralelizacije**: vLLM podržava [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) za modele tipa mešavine eksperata i [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) za veću propusnost. Eksperimentišite sa `--enable-expert-parallel` i `--data-parallel-size` da biste pronašli najbolju konfiguraciju za vaše opterećenje