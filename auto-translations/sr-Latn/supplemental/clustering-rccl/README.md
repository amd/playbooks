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

# Klasterovanje dva Ryzen™ AI Halo sistema pomoću RCCL-a

## Pregled

Vaš Ryzen™ AI Halo sistem je već sposoban da lokalno pokreće velike jezičke modele. Klasterovanje ovo podiže na viši nivo tako što kombinuje GPU memoriju više sistema preko lokalne mreže, dajući vam pristup još većim modelima sa jačim rezonovanjem, boljim generisanjem koda i dubljim razumevanjem više jezika, a sve to potpuno na vašem sopstvenom hardveru.

Ovaj vodič vas uči kako da klasterujete dva Ryzen AI Halo sistema koristeći RCCL (ROCm Communication Collectives Library) sa vLLM-om i pokrenete Qwen3.5-397B, model sa 397 milijardi parametara, na obe mašine uz ROCm akceleraciju.

## Šta ćete naučiti

- Kako da proširite alokaciju VRAM-a na Ryzen AI Halo sistemima
- Pokretanje vLLM-a sa ROCm podrškom
- Konfigurisanje RCCL-a za tensor-paralelno zaključivanje na više čvorova preko dva Ryzen AI Halo sistema
- Pokretanje modela sa 397 milijardi parametara na dva umrežena Ryzen AI Halo sistema

## Preduslovi

### Hardver

Ovaj vodič zahteva dve Ryzen AI Halo jedinice i jedan Ethernet svič, povezane u zvezda topologiji, pri čemu je svaka jedinica direktno povezana kablom sa svičem.

| Komponenta | Količina | Opis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Računarski čvorovi koji čine klaster |
| 10Gbps Ethernet svič | 1 | Centralni svič koji omogućava komunikaciju između više Ryzen AI Halo čvorova (najmanje 2 porta) |
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

Povežite svaku Ryzen AI Halo jedinicu sa Ethernet sličem koristeći Cat 7 (ili viši) kabl. Ovim se uspostavlja 10Gbps veza koja se koristi za brzu komunikaciju između čvorova.

### 1. Utvrđivanje mrežnih interfejsa

Na svakoj mašini pronađite naziv njenog mrežnog interfejsa i zabeležite ga (u ostatku uputstva će se navoditi kao `IFNAME`). Pokrenite:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Ovo direktno ispisuje naziv interfejsa, na primer:

```bash
enp191s0
```

### 2. Provera brzine mrežne veze

Potvrdite da je veza aktivna i da radi punom brzinom tako što ćete proveriti brzinu vašeg interfejsa:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Napomena**: Zamenite `<IFNAME>` sa nazivom izlaznog interfejsa iz [1. Utvrđivanje mrežnih interfejsa](#1-determine-network-interfaces)

Trebalo bi da vidite brzinu od `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Napomena**: Ako je brzina niža od `10000Mb/s` ili veza ne uspostavlja, proverite kabl i potvrdite da je port na sviču podešen na 10Gbps. Neki svičevi zahtevaju da se auto-negotiation isključi i da se brzina veze ručno podesi; pogledajte dokumentaciju vašeg sviča.

## Proširivanje alokacije VRAM-a

> **Napomena**: Ovaj korak izvršite i na Mašini 1 i na Mašini 2.

### Konfiguracija memorije za pokretanje velikih modela

Na Linux-u, ROCm koristi zajednički sistemski memorijski pul, koji je podrazumevano podešen na polovinu sistemske memorije.

Ova količina se može povećati promenom podešavanja Translation Table Manager (TTM) stranica u kernelu, prema sledećim uputstvima. AMD preporučuje da se minimalna namenska VRAM memorija podesi u BIOS-u (0.5 GB).

* Instalirajte pipx alat i dodajte putanju za pipx instalirane wheel pakete u sistemsku search putanju.

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

* Rekonfigurišite podešavanja deljene memorije na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Restartujte sistem da bi promene stupile na snagu.

## Inicijalizacija vLLM kontejnera

> **Napomena**: Ovaj korak izvršite i na Mašini 1 i na Mašini 2.

Vaš Ryzen AI Halo sistem dolazi sa vLLM-om upakovanim u unapred izgrađenu container sliku, koju pokrećete pomoću Podman-a, besplatnog alata otvorenog koda za kontejnere.

### 1. Kreiranje direktorijuma za preuzimanje modela

Kada u ovom vodiču pokrenete Qwen3.5-397B model, vLLM će automatski preuzeti težine modela na vaš sistem. Da biste bili sigurni da su te težine dostupne iz kontejnera, prvo kreirajte direktorijum za modele koji kontejner može da montira:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Pokretanje vLLM kontejnera

Komanda ispod pokreće kontejner i ubacuje vas u interaktivnu ljusku. Ona montira direktorijum za modele koji ste upravo kreirali i prosleđuje vaš `IFNAME` promenljivama `NCCL_SOCKET_IFNAME` i `GLOO_SOCKET_IFNAME`, govoreći RCCL-u (biblioteci koju vLLM koristi za koordinaciju GPU-ova na klasteru) koji interfejs da koristi.

Pokrenite kontejner sa:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Napomena**: Zamenite `<IFNAME>` sa nazivom izlaznog interfejsa iz [1. Utvrđivanje mrežnih interfejsa](#1-determine-network-interfaces)

## Pokretanje modela na klasteru

vLLM koristi Ray za orkestraciju klastera i RCCL za obradu komunikacije između GPU-ova preko čvorova. Jedna mašina deluje kao **glavni čvor (head node)** (Mašina 1), koordinišući zaključivanje. Druga se pridružuje kao **radni čvor (worker node)** (Mašina 2), doprinoseći svojom GPU memorijom i računarskom snagom.

> **Napomena**: Ray je opciona zavisnost za vLLM i dostupan je samo unutar unapred konfigurisanog Podman kontejnera.

Prilikom pokretanja, vLLM deli model na oba čvora koristeći tensor paralelizam. Nakon učitavanja, zaključivanje se odvija kao da se izvršava na jednom akceleratoru.

#### Sprečavanje Ray OOM grešaka

Podrazumevano, Ray nadgleda memoriju hosta na svakom čvoru i ubija najveći proces kada iskorišćenost memorije pređe 95%. Na vašem Ryzen™ AI Halo sistemu, GPU i host dele jedan zajednički memorijski pul, tako da učitavanje modela može izazvati `ray.exceptions.OutOfMemoryError` grešku i ubiti radni proces.

Da bismo to sprečili, izvezaćemo (export) `RAY_memory_monitor_refresh_ms=0` na svakoj mašini pre pokretanja i pridruživanja klasteru.
### Korak 1: Pokretanje Ray Head čvora (Mašina 1)

Na Mašini 1, pokrenite Ray head čvor da biste inicijalizovali klaster:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Pronalaženje `<MACHINE_1_IP>`**: Na Mašini 1, pokrenite `hostname -I | awk '{print $1}'` da biste pronašli njenu lokalnu IP adresu.

### Korak 2: Pridruživanje klasteru (Mašina 2)

Na Mašini 2, povežite se sa head čvorom da biste formirali klaster:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Pronalaženje `<MACHINE_2_IP>`**: Na Mašini 2, pokrenite `hostname -I | awk '{print $1}'` da biste pronašli njenu lokalnu IP adresu.

### Korak 3: Serviranje modela (Mašina 1)

Na Mašini 1, pokrenite vLLM server. Ovo će automatski preuzeti model i početi da ga servira na oba čvora:

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

| Oznaka | Svrha |
|------|---------|
| `--port` | Port na kom se servira HTTP API |
| `--host` | IP adresa na koju se server vezuje (`0.0.0.0` za sve interfejse) |
| `--max-model-len` | Maksimalna dužina konteksta u tokenima |
| `--gpu-memory-utilization` | Deo GPU memorije koji se alocira (0.0–1.0) |
| `--dtype` | Tip podataka za težine modela |
| `--tensor-parallel-size` | Broj GPU-ova na koje se model deli (postaviti na ukupan broj GPU-ova u klasteru) |
| `--distributed-executor-backend` | Pozadinski sistem za izvršavanje na više čvorova (`ray` za implementacije klastera) |
| `--enforce-eager` | Onemogućava kompajliranje CUDA grafova radi kompatibilnosti |
| `--language-model-only` | Preskače učitavanje pomoćnih komponenti modela (npr. vizuelnog enkodera) |
| `--reasoning-parser` | Omogućava strukturirano parsiranje izlaza rezonovanja za model |

Za potpuno korišćenje parametara, pogledajte [vLLM dokumentaciju](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Pristupanje modelu

vLLM izlaže API kompatibilan sa OpenAI, tako da možete povezati bilo koji kompatibilan klijent ili interfejs sa svojim klasterom. Jedna popularna opcija je [Open WebUI](https://github.com/open-webui/open-webui), koji pruža interfejs za ćaskanje zasnovan na pregledaču.

Da biste povezali Open WebUI sa vašim vLLM krajnjom tačkom:

1. Otvorite **Settings** > **Admin Panel** > **Connections**
2. Kliknite na **+** na **Manage OpenAI API Connections**
3. Podesite **Connection Type** na **External**
4. Podesite **URL** na `http://<MACHINE_1_IP>:7000/v1`
5. Pod **Auth**, izaberite **None** iz padajućeg menija
6. Ostavite **Model IDs** prazno da biste automatski otkrili sve modele sa krajnje tačke

> **Pronalaženje `<MACHINE_1_IP>`**: Na Mašini 1, pokrenite `hostname -I | awk '{print $1}'` da biste pronašli njenu lokalnu IP adresu. Ako pristupate Open WebUI-ju sa same Mašine 1, možete koristiti `http://localhost:7000/v1`.

![Podešavanja Open WebUI konekcije za vLLM krajnju tačku](assets/openwebui-connection.png)

Kada se povežete, izaberite model iz padajućeg menija modela u Open WebUI-ju i počnite da ćaskate. Model sada radi na oba vaša Ryzen AI Halo čvora:

![Ćaskanje sa Qwen3.5-397B u Open WebUI-ju](assets/openwebui-chat.png)

## Sledeći koraci

- **Istražite druge modele**: Otkrijte nove modele na [Hugging Face](https://huggingface.co/models?&sort=trending) koji se uklapaju u kombinovanu GPU memoriju vašeg klastera
- **Skalirajte na četiri čvora**: Dodajte još dva Ryzen AI Halo sistema kao dodatne Ray radne čvorove kako biste podelili modele na još više GPU-ova. Ovo zahteva Ethernet svič sa najmanje četiri porta, po jedan za svaki čvor. Sledite [Korak 2: Pridruživanje klasteru](#step-2-join-the-cluster-machine-2) na svakom dodatnom radnom čvoru i povećajte `--tensor-parallel-size` u skladu s tim
- **Isprobajte druge strategije paralelizma**: vLLM podržava [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) za modele tipa mixture-of-experts i [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) za veći propusni kapacitet. Eksperimentišite sa `--enable-expert-parallel` i `--data-parallel-size` da biste pronašli najbolju konfiguraciju za svoje radno opterećenje