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

# Klasterovanje dva Ryzen™ AI Halo sistema pomoću RCCL

## Pregled

Vaš Ryzen™ AI Halo je već sposoban da pokreće velike jezičke modele lokalno. Klasterovanje ovo dodatno unapređuje kombinovanjem GPU memorije više sistema preko lokalne mreže, pružajući vam pristup još većim modelima sa jačim rasuđivanjem, boljim generisanjem koda i dubljim razumevanjem više jezika, potpuno na sopstvenom hardveru.

Ovaj vodič vas uči kako da klasterujete dva Ryzen AI Halo sistema koristeći RCCL (ROCm Communication Collectives Library) sa vLLM i pokrenete Qwen3.5-397B, model sa 397 milijardi parametara, na obe mašine uz ROCm akceleraciju.

## Šta ćete naučiti

- Kako da proširite VRAM alokaciju na Ryzen AI Halo sistemima
- Pokretanje vLLM sa ROCm podrškom
- Konfigurisanje RCCL za multi-node tensor-parallel zaključivanje na dva Ryzen AI Halo sistema
- Pokretanje modela sa 397 milijardi parametara na dva umrežena Ryzen AI Halo sistema

## Preduslovi

### Hardver

Ovaj vodič zahteva dve Ryzen AI Halo jedinice i jedan Ethernet svič, povezane u zvezda topologiji, gde je svaka jedinica direktno povezana sa svičem.

| Komponenta | Količina | Opis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Kompjuterski čvorovi koji čine klaster |
| 10Gbps Ethernet svič | 1 | Centralni svič koji omogućava komunikaciju više Ryzen AI Halo čvorova (najmanje 2 porta) |
| Ethernet kabl | 2 | Povezuje svaku Halo jedinicu sa svičem (preporučuje se Cat 7 ili viši) |

> **Napomena**: Potrebna su dva porta na Ethernet sviču da bi se povezale dve Ryzen AI Halo jedinice. Treći port je potreban ako pristupate modelu sa posebne klijentske mašine umesto sa jedne od Halo jedinica.

### Softver
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Podešavanje fizičkog hardvera

> **Napomena**: Ovaj korak izvršite i na Mašini 1 i na Mašini 2.

Povežite svaku Ryzen AI Halo jedinicu sa Ethernet svičem koristeći Cat 7 (ili viši) kabl. Ovo uspostavlja 10Gbps vezu koja se koristi za brzu komunikaciju između čvorova.

### 1. Određivanje mrežnih interfejsa

Na svakoj mašini, pronađite naziv njenog mrežnog interfejsa i zabeležite ga (u ostatku uputstva će se nazivati `IFNAME`). Pokrenite:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Ovo ispisuje naziv interfejsa direktno, na primer:

```bash
enp191s0
```

### 2. Provera brzina mrežne veze

Potvrdite da je veza aktivna i da radi punom brzinom proverom brzine vašeg interfejsa:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Napomena**: Zamenite `<IFNAME>` sa nazivom izlaznog interfejsa iz [1. Određivanje mrežnih interfejsa](#1-određivanje-mrežnih-interfejsa)

Trebalo bi da vidite brzinu od `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Napomena**: Ako je brzina niža od `10000Mb/s` ili veza ne radi, proverite vezu kabla i potvrdite da je port na sviču podešen na 10Gbps. Neki svičevi zahtevaju da automatska negocijacija bude isključena i da se brzina veze podesi ručno; pogledajte dokumentaciju svog sviča.

## Proširenje VRAM alokacije

> **Napomena**: Ovaj korak izvršite i na Mašini 1 i na Mašini 2.

### Konfiguracija memorije za pokretanje velikih modela

Na Linuxu, ROCm koristi deljeni pul sistemske memorije, a ovaj pul je podrazumevano podešen na polovinu sistemske memorije.

Ova količina se može povećati promenom podešavanja stranica kernelovog Translation Table Manager-a (TTM), prema sledećim uputstvima. AMD preporučuje da se u BIOS-u podesi minimalna dedicirana VRAM memorija (0.5 GB).

* Instalirajte pipx alat i dodajte putanju za pipx instalirane wheel-ove u sistemsku putanju pretrage.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Instalirajte amd-debug-tools wheel sa PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Pokrenite amd-ttm alat da biste proverili trenutna podešavanja za deljenu memoriju.
  ```bash
  amd-ttm
  ```

* Ponovo konfigurišite podešavanja deljene memorije na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Ponovo pokrenite sistem da bi promene stupile na snagu.

## Inicijalizacija vLLM kontejnera

> **Napomena**: Ovaj korak izvršite i na Mašini 1 i na Mašini 2.

Vaš Ryzen AI Halo dolazi sa vLLM upakovanim unutar unapred izgrađene slike kontejnera, koju pokrećete koristeći Podman, besplatan alat otvorenog koda za kontejnere.

### 1. Kreiranje direktorijuma za preuzimanje modela

Kada budete servirali Qwen3.5-397B model u ovom vodiču, vLLM će automatski preuzeti težine modela na vaš sistem. Da biste bili sigurni da su te težine dostupne unutar kontejnera, prvo kreirajte direktorijum za modele koji kontejner može da montira:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Pokretanje vLLM kontejnera

Komanda ispod pokreće kontejner i prebacuje vas u interaktivnu ljusku. Montira direktorijum za modele koji ste upravo kreirali i prosleđuje vaš `IFNAME` promenljivama `NCCL_SOCKET_IFNAME` i `GLOO_SOCKET_IFNAME`, čime se RCCL biblioteci (koju vLLM koristi za koordinaciju GPU-ova u okviru klastera) saopštava koji interfejs da koristi.

Pokrenite kontejner sa:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Napomena**: Zamenite `<IFNAME>` sa nazivom izlaznog interfejsa iz [1. Određivanje mrežnih interfejsa](#1-određivanje-mrežnih-interfejsa)

## Pokretanje modela na klasteru

vLLM koristi Ray za orkestraciju klastera i RCCL za rukovanje komunikacijom GPU-GPU između čvorova. Jedna mašina deluje kao **glavni čvor** (Mašina 1), koordinišući zaključivanje. Druga se pridružuje kao **radni čvor** (Mašina 2), doprinoseći svojom GPU memorijom i računarskom snagom.

> **Napomena**: Ray je opciona zavisnost za vLLM i dostupan je samo iz unapred konfigurisanog Podman kontejnera.

Prilikom pokretanja, vLLM deli model između oba čvora koristeći tensor paralelizam. Nakon učitavanja, zaključivanje se odvija kao da se izvršava na jednom akceleratoru.

### Korak 1: Pokretanje Ray glavnog čvora (Mašina 1)

Na Mašini 1, pokrenite Ray glavni čvor da biste inicijalizovali klaster:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Pronalaženje `<MACHINE_1_IP>`**: Na Mašini 1, pokrenite `hostname -I | awk '{print $1}'` da biste pronašli njenu lokalnu IP adresu.
### Korak 2: Pridruživanje klasteru (Mašina 2)

Na Mašini 2, povežite se sa glavnim čvorom da biste formirali klaster:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Pronalaženje `<MACHINE_2_IP>`**: Na Mašini 2, pokrenite `hostname -I | awk '{print $1}'` da biste pronašli njenu lokalnu IP adresu.

### Korak 3: Posluživanje modela (Mašina 1)

Na Mašini 1, pokrenite vLLM server. Ovo će automatski preuzeti model i početi da ga poslužuje na oba čvora:

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

#### Referenca parametara

| Oznaka | Namena |
|------|---------|
| `--port` | Port na kojem se poslužuje HTTP API |
| `--host` | IP adresa na koju se server vezuje (`0.0.0.0` za sve interfejse) |
| `--max-model-len` | Maksimalna dužina konteksta u tokenima |
| `--gpu-memory-utilization` | Deo GPU memorije koji se alocira (0.0–1.0) |
| `--dtype` | Tip podataka za težine modela |
| `--tensor-parallel-size` | Broj GPU-ova na koje se model deli (postaviti na ukupan broj GPU-ova u klasteru) |
| `--distributed-executor-backend` | Pozadinski sistem za izvršavanje na više čvorova (`ray` za implementacije na klasteru) |
| `--enforce-eager` | Onemogućava kompajliranje CUDA grafova radi kompatibilnosti |
| `--language-model-only` | Preskače učitavanje pomoćnih komponenti modela (npr. enkodera za vizuelne podatke) |
| `--reasoning-parser` | Omogućava strukturirano parsiranje izlaza rezonovanja za model |

Za potpuno korišćenje parametara, pogledajte [vLLM dokumentaciju](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Pristupanje modelu

vLLM izlaže API kompatibilan sa OpenAI, tako da možete povezati bilo kog kompatibilnog klijenta ili interfejs sa vašim klasterom. Jedna popularna opcija je [Open WebUI](https://github.com/open-webui/open-webui), koji pruža interfejs za ćaskanje zasnovan na pregledaču.

Da biste povezali Open WebUI sa vašim vLLM krajnjim taskom (endpoint):

1. Otvorite **Settings** > **Admin Panel** > **Connections**
2. Kliknite na **+** kod **Manage OpenAI API Connections**
3. Postavite **Connection Type** na **External**
4. Postavite **URL** na `http://<MACHINE_1_IP>:7000/v1`
5. U okviru **Auth**, izaberite **None** iz padajućeg menija
6. Ostavite **Model IDs** prazno kako biste automatski otkrili sve modele sa krajnje tačke

> **Pronalaženje `<MACHINE_1_IP>`**: Na Mašini 1, pokrenite `hostname -I | awk '{print $1}'` da biste pronašli njenu lokalnu IP adresu. Ako pristupate Open WebUI sa same Mašine 1, možete koristiti `http://localhost:7000/v1`.

![Podešavanja veze Open WebUI za vLLM krajnju tačku](assets/openwebui-connection.png)

Kada se povežete, izaberite model iz padajućeg menija modela u Open WebUI i počnite ćaskanje. Model sada radi na oba vaša Ryzen AI Halo čvora:

![Ćaskanje sa Qwen3.5-397B u Open WebUI](assets/openwebui-chat.png)

## Sledeći koraci

- **Istražite druge modele**: Otkrijte nove modele na [Hugging Face](https://huggingface.co/models?&sort=trending) koji stanu u kombinovanu GPU memoriju vašeg klastera
- **Proširite na četiri čvora**: Dodajte još dva Ryzen AI Halo sistema kao dodatne Ray radnike da biste delili modele na još više GPU-ova. Ovo zahteva Ethernet svič sa najmanje četiri porta, po jedan za svaki čvor. Pratite [Korak 2: Pridruživanje klasteru](#step-2-join-the-cluster-machine-2) na svakom dodatnom radniku i povećajte `--tensor-parallel-size` u skladu s tim
- **Isprobajte druge strategije paralelizacije**: vLLM podržava [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) za modele tipa mešavine eksperata (mixture-of-experts) i [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) za veći propusni opseg. Eksperimentišite sa `--enable-expert-parallel` i `--data-parallel-size` da biste pronašli najbolju konfiguraciju za vaše radno opterećenje