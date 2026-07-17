<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Klasterovanje dva Ryzen™ AI Halo sistema pomoću RCCL

## Pregled

Vaš Ryzen™ AI Halo je već sposoban da lokalno pokreće velike jezičke modele. Klasterovanje ide korak dalje kombinovanjem GPU memorije više sistema putem lokalne mreže, što vam daje pristup još većim modelima sa snažnijim rezonovanjem, boljim generisanjem koda i dubljim višejezičnim razumevanjem — sve to isključivo na vašem sopstvenom hardveru.

Ovaj priručnik vas uči kako da klasterujete dva Ryzen AI Halo sistema koristeći RCCL (ROCm Communication Collectives Library) sa vLLM i pokrenete Qwen3.5-397B, model sa 397 milijardi parametara, na oba računara uz ROCm akceleraciju.

## Šta ćete naučiti

- Kako da proširite alokaciju VRAM-a na Ryzen AI Halo sistemima
- Pokretanje vLLM sa ROCm podrškom
- Konfigurisanje RCCL za višečvornu tenzorski paralelnu inferenciju na dva Ryzen AI Halo sistema
- Pokretanje modela sa 397 milijardi parametara na dva umrežena Ryzen AI Halo sistema

## Preduslovi

### Hardver

Ovaj priručnik zahteva dve Ryzen AI Halo jedinice i jedan Ethernet svič, povezane u zvezdastoj topologiji pri čemu je svaka jedinica direktno žičano priključena na svič.

| Komponenta | Količina | Opis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Računarski čvorovi koji čine klaster |
| 10Gbps Ethernet svič | 1 | Centralni svič koji omogućava komunikaciju između više Ryzen AI Halo čvorova (najmanje 2 porta) |
| Ethernet kabl | 2 | Povezuje svaku Halo jedinicu sa svičem (preporučuje se Cat 7 ili viši) |

> **Napomena**: Dva porta Ethernet sviča su potrebna za povezivanje dve Ryzen AI Halo jedinice. Treći port je potreban ako modelu pristupate sa zasebnog klijentskog računara umesto sa jedne od Halo jedinica.

### Softver
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fizičko podešavanje hardvera

> **Napomena**: Ovaj korak izvršite na oba računara — Računaru 1 i Računaru 2.

Povežite svaku Ryzen AI Halo jedinicu sa Ethernet svičem koristeći Cat 7 (ili viši) kabl. Time se uspostavlja 10Gbps veza koja se koristi za brzu komunikaciju između čvorova.

### 1. Određivanje mrežnih interfejsa

Na svakom računaru pronađite naziv njegovog mrežnog interfejsa i zabeležite ga (u ostatku uputstava biće označen kao `IFNAME`). Pokrenite:

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

> **Napomena**: Zamenite `<IFNAME>` nazivom izlaznog interfejsa iz koraka [1. Određivanje mrežnih interfejsa](#1-određivanje-mrežnih-interfejsa)

Trebalo bi da vidite brzinu od `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Napomena**: Ako je brzina manja od `10000Mb/s` ili veza ne uspostavi konekciju, proverite kablovski priključak i potvrdite da je port sviča podešen na 10Gbps. Neki svičevi zahtevaju da se automatsko pregovaranje onemogući i da se brzina veze postavi ručno; pogledajte dokumentaciju vašeg sviča.

## Proširivanje alokacije VRAM-a

> **Napomena**: Ovaj korak izvršite na oba računara — Računaru 1 i Računaru 2.

### Konfiguracija memorije za pokretanje velikih modela

Na Linuxu, ROCm koristi zajednički sistemski memorijski bazen, koji je podrazumevano konfigurisan na polovinu sistemske memorije.

Ovaj iznos može se povećati promenom postavke TTM (Translation Table Manager) stranica kernela, prema sledećim uputstvima. AMD preporučuje postavljanje minimalne namenske VRAM vrednosti u BIOS-u (0,5 GB).

* Instalirajte pipx alatku i dodajte putanju za pipx instalirane pakete u sistemsku putanju pretrage.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Instalirajte amd-debug-tools paket sa PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Pokrenite amd-ttm alatku da biste upitali trenutne postavke deljene memorije.
  ```bash
  amd-ttm
  ```

* Rekonfigurirajte postavke deljene memorije na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Restartujte sistem da bi promene stupile na snagu.

## Inicijalizacija vLLM kontejnera

> **Napomena**: Ovaj korak izvršite na oba računara — Računaru 1 i Računaru 2.

Vaš Ryzen AI Halo isporučuje se sa vLLM upakovnim unutar unapred izgrađene slike kontejnera, koju pokrećete pomoću Podmana, besplatnog alata za kontejnere otvorenog koda.

### 1. Kreiranje direktorijuma za preuzimanje modela

Kada u ovom priručniku pokrenete Qwen3.5-397B model, vLLM će automatski preuzeti težine modela na vaš sistem. Da biste osigurali da su te težine dostupne unutar kontejnera, najpre kreirajte direktorijum za modele koji kontejner može da montira:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Pokretanje vLLM kontejnera

Komanda ispod pokreće kontejner i otvara interaktivnu ljusku. Montira direktorijum za modele koji ste upravo kreirali i prosleđuje vaš `IFNAME` promenljivama `NCCL_SOCKET_IFNAME` i `GLOO_SOCKET_IFNAME`, čime se RCCL-u (biblioteci koju vLLM koristi za koordinaciju GPU-ova u klasteru) govori koji interfejs da koristi.

Pokrenite kontejner sa:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Napomena**: Zamenite `<IFNAME>` nazivom izlaznog interfejsa iz koraka [1. Određivanje mrežnih interfejsa](#1-određivanje-mrežnih-interfejsa)

## Pokretanje modela na klasteru

vLLM koristi Ray za orkestraciju klastera i RCCL za upravljanje GPU-to-GPU komunikacijom između čvorova. Jedan računar deluje kao **glavni čvor** (Računar 1), koordinirajući inferenciju. Drugi se pridružuje kao **radni čvor** (Računar 2), doprinoseći svojom GPU memorijom i računarskim kapacitetom.

> **Napomena**: Ray je opciona zavisnost za vLLM i dostupan je samo unutar unapred konfigurisanog Podman kontejnera.

Pri pokretanju, vLLM deli model između oba čvora koristeći tenzorski paralelizam. Nakon učitavanja, inferencija se odvija kao da se izvršava na jednom akceleratoru.

### Korak 1: Pokretanje Ray glavnog čvora (Računar 1)

Na Računaru 1, pokrenite Ray glavni čvor da biste inicijalizovali klaster:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Pronalaženje `<MACHINE_1_IP>`**: Na Računaru 1, pokrenite `hostname -I | awk '{print $1}'` da biste pronašli njegovu lokalnu IP adresu.

### Korak 2: Pridruživanje klasteru (Računar 2)

Na Računaru 2, povežite se sa glavnim čvorom da biste formirali klaster:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Pronalaženje `<MACHINE_2_IP>`**: Na Računaru 2, pokrenite `hostname -I | awk '{print $1}'` da biste pronašli njegovu lokalnu IP adresu.

### Korak 3: Pokretanje modela (Računar 1)

Na Računaru 1, pokrenite vLLM server. Ovo će automatski preuzeti model i početi da ga servira na oba čvora:

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

| Zastavica | Svrha |
|------|---------|
| `--port` | Port na kome se servira HTTP API |
| `--host` | IP adresa na koju se server vezuje (`0.0.0.0` za sve interfejse) |
| `--max-model-len` | Maksimalna dužina konteksta u tokenima |
| `--gpu-memory-utilization` | Udeo GPU memorije koji se alocira (0,0–1,0) |
| `--dtype` | Tip podataka za težine modela |
| `--tensor-parallel-size` | Broj GPU-ova na koje se model deli (postaviti na ukupan broj GPU-ova u klasteru) |
| `--distributed-executor-backend` | Pozadinski sistem za višečvornu egzekuciju (`ray` za klasterska okruženja) |
| `--enforce-eager` | Onemogućava CUDA graph kompilaciju radi kompatibilnosti |
| `--language-model-only` | Preskače učitavanje pomoćnih komponenti modela (npr. enkoder za viziju) |
| `--reasoning-parser` | Omogućava strukturirano parsiranje izlaza rezonovanja za model |

Za potpunu upotrebu parametara, pogledajte [vLLM dokumentaciju](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Pristupanje modelu

vLLM izlaže OpenAI-kompatibilan API, tako da možete da povežete bilo koji kompatibilan klijent ili interfejs sa vašim klasterom. Jedna popularna opcija je [Open WebUI](https://github.com/open-webui/open-webui), koji pruža interfejs za ćaskanje zasnovan na pregledaču.

Da biste povezali Open WebUI sa vašim vLLM krajnjim tačkama:

1. Otvorite **Settings** > **Admin Panel** > **Connections**
2. Kliknite na **+** pored **Manage OpenAI API Connections**
3. Postavite **Connection Type** na **External**
4. Postavite **URL** na `http://<MACHINE_1_IP>:7000/v1`
5. Pod **Auth**, izaberite **None** iz padajućeg menija
6. Ostavite **Model IDs** prazno da biste automatski otkrili sve modele sa krajnje tačke

> **Pronalaženje `<MACHINE_1_IP>`**: Na Računaru 1, pokrenite `hostname -I | awk '{print $1}'` da biste pronašli njegovu lokalnu IP adresu. Ako pristupate Open WebUI sa samog Računara 1, možete koristiti `http://localhost:7000/v1`.

![Postavke veze Open WebUI za vLLM krajnju tačku](assets/openwebui-connection.png)

Nakon povezivanja, izaberite model iz padajućeg menija modela u Open WebUI i počnite da ćaskate. Model sada radi na oba vaša Ryzen AI Halo čvora:

![Ćaskanje sa Qwen3.5-397B u Open WebUI](assets/openwebui-chat.png)

## Sledeći koraci

- **Istražite druge modele**: Otkrijte nove modele na [Hugging Face](https://huggingface.co/models?&sort=trending) koji se uklapaju u kombinovanu GPU memoriju vašeg klastera
- **Proširite na četiri čvora**: Dodajte još dva Ryzen AI Halo sistema kao dodatne Ray radnike da biste podelili modele na još više GPU-ova. Ovo zahteva Ethernet svič sa najmanje četiri porta, po jedan za svaki čvor. Pratite [Korak 2: Pridruživanje klasteru](#korak-2-pridruživanje-klasteru-računar-2) na svakom dodatnom radniku i povećajte `--tensor-parallel-size` u skladu s tim
- **Isprobajte druge strategije paralelizma**: vLLM podržava [ekspertski paralelizam](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) za modele mešavine eksperata i [podatkovni paralelizam](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) za veći propusni opseg. Eksperimentišite sa `--enable-expert-parallel` i `--data-parallel-size` da biste pronašli najbolju konfiguraciju za vaše radno opterećenje