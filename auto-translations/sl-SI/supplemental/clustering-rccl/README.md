<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Povezovanje dveh sistemov Ryzen™ AI Halo v gručo z RCCL

## Pregled

Vaš Ryzen™ AI Halo je že sposoben lokalno poganjati velike jezikovne modele. Povezovanje v gručo to zmožnost razširi še dlje, saj združi GPU pomnilnik več sistemov prek lokalnega omrežja, kar vam omogoča dostop do še večjih modelov z močnejšim sklepanjem, boljšim generiranjem kode in globljim razumevanjem več jezikov – vse to popolnoma na vaši lastni strojni opremi.

Ta priročnik vas nauči, kako povezati dva sistema Ryzen AI Halo v gručo z uporabo RCCL (ROCm Communication Collectives Library) skupaj z vLLM ter kako poganjati Qwen3.5-397B, model s 397 milijardami parametrov, na obeh napravah hkrati z ROCm pospeševanjem.

## Kaj se boste naučili

- Kako razširiti dodelitev VRAM na sistemih Ryzen AI Halo
- Zagon vLLM s podporo ROCm
- Konfiguracija RCCL za sklepanje s tenzorsko paralelizacijo prek več vozlišč med dvema sistemoma Ryzen AI Halo
- Poganjanje modela s 397 milijardami parametrov na dveh povezanih sistemih Ryzen AI Halo

## Predpogoji

### Strojna oprema

Ta priročnik zahteva dve enoti Ryzen AI Halo in eno Ethernet stikalo, povezani v topologijo zvezde, pri čemer je vsaka enota povezana neposredno s stikalom.

| Komponenta | Količina | Opis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Računalniška vozlišča, ki tvorita gručo |
| 10 Gbps Ethernet stikalo | 1 | Osrednje stikalo, ki omogoča komunikacijo med več vozlišči Ryzen AI Halo (vsaj 2 vrati) |
| Ethernet kabel | 2 | Povezuje vsako enoto Halo s stikalom (priporočena kategorija Cat 7 ali višja) |

> **Opomba**: Za povezavo dveh enot Ryzen AI Halo sta potrebni dve vrati Ethernet stikala. Tretja vrata so potrebna, če do modela dostopate s ločenega odjemalskega računalnika namesto z ene od enot Halo.

### Programska oprema
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fizična namestitev strojne opreme

> **Opomba**: Ta korak izvedite tako na Napravi 1 kot na Napravi 2.

Povežite vsako enoto Ryzen AI Halo s stikalom Ethernet s kablom Cat 7 (ali višjim). S tem vzpostavite 10 Gbps povezavo, ki se uporablja za hitro komunikacijo med vozlišči.

### 1. Ugotovitev omrežnih vmesnikov

Na vsakem računalniku poiščite ime njegovega omrežnega vmesnika in si ga zapišite (v nadaljevanju navodil se bo imenovalo `IFNAME`). Zaženite:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

To izpiše ime vmesnika neposredno, na primer:

```bash
enp191s0
```

### 2. Preverjanje hitrosti omrežne povezave

Potrdite, da je povezava aktivna in deluje s polno hitrostjo, tako da preverite hitrost svojega vmesnika:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Opomba**: Zamenjajte `<IFNAME>` z izhodnim imenom vmesnika iz razdelka [1. Ugotovitev omrežnih vmesnikov](#1-determine-network-interfaces)

Videti bi morali hitrost `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Opomba**: Če je hitrost nižja od `10000Mb/s` ali če se povezava ne vzpostavi, preverite priključitev kabla in potrdite, da so vrata stikala nastavljena na 10 Gbps. Nekatera stikala zahtevajo, da onemogočite samodejno pogajanje in ročno nastavite hitrost povezave; oglejte si dokumentacijo svojega stikala.

## Razširitev dodelitve VRAM

> **Opomba**: Ta korak izvedite tako na Napravi 1 kot na Napravi 2.

### Konfiguracija pomnilnika za poganjanje velikih modelov

Na sistemu Linux ROCm uporablja skupen sistemski pomnilniški nabor, ki je privzeto nastavljen na polovico sistemskega pomnilnika.

To količino je mogoče povečati s spremembo nastavitve strani Translation Table Manager (TTM) v jedru, po naslednjih navodilih. AMD priporoča, da v BIOS-u nastavite minimalni namenski VRAM (0,5 GB).

* Namestite orodje pipx in dodajte pot do namestitvenih paketov (wheel) pipx v sistemsko iskalno pot.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Namestite paket amd-debug-tools s PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Zaženite orodje amd-ttm za poizvedovanje po trenutnih nastavitvah skupnega pomnilnika.
  ```bash
  amd-ttm
  ```

* Ponovno konfigurirajte nastavitve skupnega pomnilnika na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Znova zaženite sistem, da se spremembe uveljavijo.

## Inicializacija vLLM vsebnika

> **Opomba**: Ta korak izvedite tako na Napravi 1 kot na Napravi 2.

Vaš Ryzen AI Halo je opremljen z vLLM, ki je vključen v vnaprej pripravljeni vsebniški (container) sliki, katero poganjate z Podman, brezplačnim in odprtokodnim orodjem za vsebnike.

### 1. Ustvarite mapo za prenos modelov

Ko boste v tem priročniku posredovali model Qwen3.5-397B, bo vLLM samodejno prenesel uteži modela v vaš sistem. Da zagotovite dostopnost teh uteži znotraj vsebnika, najprej ustvarite mapo za modele, ki jo bo vsebnik lahko priklopil:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Zagon vLLM vsebnika

Spodnji ukaz zažene vsebnik in vas postavi v interaktivno lupino. Priklopi mapo za modele, ki ste jo pravkar ustvarili, in posreduje vaš `IFNAME` v `NCCL_SOCKET_IFNAME` in `GLOO_SOCKET_IFNAME`, s čimer RCCL (knjižnici, ki jo vLLM uporablja za usklajevanje GPU-jev po gruči) sporoči, kateri vmesnik naj uporabi.

Zaženite vsebnik z:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Opomba**: Zamenjajte `<IFNAME>` z izhodnim imenom vmesnika iz razdelka [1. Ugotovitev omrežnih vmesnikov](#1-determine-network-interfaces)

## Poganjanje modela na gruči

vLLM uporablja Ray za organizacijo gruče in RCCL za obravnavo komunikacije med GPU-ji na različnih vozliščih. En računalnik deluje kot **glavno vozlišče** (Naprava 1), ki usklajuje sklepanje. Drugi se pridruži kot **delovno vozlišče** (Naprava 2) in prispeva svoj GPU pomnilnik ter računsko zmogljivost.

> **Opomba**: Ray je neobvezna odvisnost za vLLM in je na voljo samo znotraj vnaprej konfiguriranega Podman vsebnika.

Ob zagonu vLLM razdeli model med obe vozlišči z uporabo tenzorske paralelizacije. Ko je model naložen, sklepanje poteka, kot da bi teklo na enem samem pospeševalniku.

### Korak 1: Zagon glavnega vozlišča Ray (Naprava 1)

Na Napravi 1 zaženite glavno vozlišče Ray za inicializacijo gruče:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Iskanje `<MACHINE_1_IP>`**: Na Napravi 1 zaženite `hostname -I | awk '{print $1}'`, da poiščete njen lokalni IP naslov.
### 2. korak: Pridružitev gruči (Stroj 2)

Na Stroju 2 se povežite z glavnim vozliščem, da tvorite gručo:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Iskanje `<MACHINE_2_IP>`**: Na Stroju 2 zaženite `hostname -I | awk '{print $1}'`, da poiščete njegov lokalni IP naslov.

### 3. korak: Postrezite model (Stroj 1)

Na Stroju 1 zaženite strežnik vLLM. To bo samodejno preneslo model in ga začelo postrezati v obeh vozliščih:

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

#### Referenca parametrov

| Zastavica | Namen |
|------|---------|
| `--port` | Vrata, na katerih se postreže HTTP API |
| `--host` | IP naslov, na katerega je vezan strežnik (`0.0.0.0` za vse vmesnike) |
| `--max-model-len` | Največja dolžina konteksta v žetonih |
| `--gpu-memory-utilization` | Delež pomnilnika GPU, ki naj se dodeli (0,0–1,0) |
| `--dtype` | Podatkovni tip za uteži modela |
| `--tensor-parallel-size` | Število GPU-jev, med katerimi naj se model razdeli (nastavite na skupno število GPU-jev v gruči) |
| `--distributed-executor-backend` | Zaledje za izvajanje na več vozliščih (`ray` za razporejene namestitve gruč) |
| `--enforce-eager` | Onemogoči prevajanje grafov CUDA zaradi združljivosti |
| `--language-model-only` | Preskoči nalaganje pomožnih komponent modela (npr. kodirnik za vid) |
| `--reasoning-parser` | Omogoči strukturirano razčlenjevanje izhoda sklepanja za model |

Za popolno uporabo parametrov glejte [dokumentacijo vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Dostop do modela

vLLM izpostavlja API, združljiv z OpenAI, zato lahko na svojo gručo povežete kateri koli združljiv odjemalec ali vmesnik. Ena priljubljenih možnosti je [Open WebUI](https://github.com/open-webui/open-webui), ki ponuja klepetalni vmesnik v brskalniku.

Za povezavo Open WebUI z vašo končno točko vLLM:

1. Odprite **Settings** > **Admin Panel** > **Connections**
2. Kliknite **+** pri **Manage OpenAI API Connections**
3. Nastavite **Connection Type** na **External**
4. Nastavite **URL** na `http://<MACHINE_1_IP>:7000/v1`
5. Pod **Auth** izberite **None** iz spustnega seznama
6. Pustite **Model IDs** prazno, da se samodejno odkrijejo vsi modeli iz končne točke

> **Iskanje `<MACHINE_1_IP>`**: Na Stroju 1 zaženite `hostname -I | awk '{print $1}'`, da poiščete njegov lokalni IP naslov. Če dostopate do Open WebUI iz samega Stroja 1, lahko uporabite `http://localhost:7000/v1`.

![Nastavitve povezave Open WebUI za končno točko vLLM](assets/openwebui-connection.png)

Ko ste povezani, izberite model iz spustnega seznama modelov v Open WebUI in začnite klepetati. Model zdaj teče na obeh vaših vozliščih Ryzen AI Halo:

![Klepet z Qwen3.5-397B v Open WebUI](assets/openwebui-chat.png)

## Naslednji koraki

- **Raziščite druge modele**: Odkrijte nove modele na [Hugging Face](https://huggingface.co/models?&sort=trending), ki ustrezajo skupnemu pomnilniku GPU vaše gruče
- **Razširite na štiri vozlišča**: Dodajte še dva sistema Ryzen AI Halo kot dodatna delovna vozlišča Ray, da razdelite modele na še več GPU-jev. To zahteva stikalo Ethernet z vsaj štirimi vrati, po enim za vsako vozlišče. Sledite [2. koraku: Pridružitev gruči](#step-2-join-the-cluster-machine-2) na vsakem dodatnem delovnem vozlišču in ustrezno povečajte `--tensor-parallel-size`
- **Preizkusite druge strategije paralelizma**: vLLM podpira [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) za modele mešanice ekspertov (mixture-of-experts) in [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) za večjo prepustnost. Eksperimentirajte z `--enable-expert-parallel` in `--data-parallel-size`, da najdete najboljšo konfiguracijo za svojo delovno obremenitev