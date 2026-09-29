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

# Gručenje dveh sistemov Ryzen™ AI Halo z RCCL

## Pregled

Vaš sistem Ryzen™ AI Halo je že sposoben lokalno poganjati velike jezikovne modele. Gručenje to zmožnost razširi tako, da povezuje GPU pomnilnik več sistemov prek lokalnega omrežja, kar vam omogoča dostop do še večjih modelov z močnejšim sklepanjem, boljšim generiranjem kode in globljim razumevanjem več jezikov, in to povsem na vaši lastni strojni opremi.

Ta vodnik vas nauči, kako gručiti dva sistema Ryzen AI Halo z uporabo RCCL (ROCm Communication Collectives Library) skupaj z vLLM in kako na obeh strojih z ROCm pospeševanjem poganjati Qwen3.5-397B, model s 397 milijardami parametrov.

## Kaj se boste naučili

- Kako razširiti dodelitev VRAM na sistemih Ryzen AI Halo
- Zagon vLLM s podporo ROCm
- Konfiguracijo RCCL za tenzorsko-paralelno sklepanje na več vozliščih med dvema sistemoma Ryzen AI Halo
- Poganjanje modela s 397 milijardami parametrov na dveh povezanih sistemih Ryzen AI Halo v omrežju

## Predpogoji

### Strojna oprema

Ta vodnik zahteva dve enoti Ryzen AI Halo in eno Ethernet stikalo, povezane v zvezdasto topologijo, pri čemer je vsaka enota povezana neposredno s stikalom.

| Komponenta | Količina | Opis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Računski vozlišči, ki tvorita gručo |
| 10Gbps Ethernet stikalo | 1 | Osrednje stikalo, ki omogoča komunikacijo med več vozlišči Ryzen AI Halo (vsaj 2 vrat) |
| Ethernet kabel | 2 | Povezuje vsako enoto Halo s stikalom (priporočena kategorija Cat 7 ali višja) |

> **Opomba**: Za povezavo obeh enot Ryzen AI Halo sta potrebni dve vrata Ethernet stikala. Tretja vrata so potrebna, če do modela dostopate z ločenega odjemalskega računalnika namesto z ene od enot Halo.

### Programska oprema
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Namestitev fizične strojne opreme

> **Opomba**: Ta korak izvedite tako na Stroju 1 kot na Stroju 2.

Vsako enoto Ryzen AI Halo povežite z Ethernet stikalom s kablom Cat 7 (ali višje kategorije). S tem vzpostavite 10Gbps povezavo, ki se uporablja za visokohitrostno komunikacijo med vozlišči.

### 1. Določitev omrežnih vmesnikov

Na vsakem stroju poiščite ime njegovega omrežnega vmesnika in si ga zapišite (v nadaljevanju navodil bo imenovan `IFNAME`). Zaženite:

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

> **Opomba**: Zamenjajte `<IFNAME>` z imenom izhodnega vmesnika iz [1. Določitev omrežnih vmesnikov](#1-določitev-omrežnih-vmesnikov)

Videti bi morali hitrost `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Opomba**: Če je hitrost nižja od `10000Mb/s` ali povezava ne vzpostavi, preverite kabelsko povezavo in potrdite, da so vrata stikala nastavljena na 10Gbps. Nekatera stikala zahtevajo onemogočeno samodejno pogajanje in ročno nastavitev hitrosti povezave; za podrobnosti glejte dokumentacijo svojega stikala.

## Razširitev dodelitve VRAM

> **Opomba**: Ta korak izvedite tako na Stroju 1 kot na Stroju 2.

### Konfiguracija pomnilnika za poganjanje velikih modelov

V sistemu Linux ROCm uporablja skupni sistemski pomnilniški bazen, ta bazen pa je privzeto nastavljen na polovico sistemskega pomnilnika.

To količino je mogoče povečati s spremembo nastavitve strani upravitelja prevajalne tabele (TTM) jedra, kot je opisano v naslednjih navodilih. AMD priporoča, da v BIOS-u nastavite minimalni namenski VRAM (0,5 GB).

* Namestite pripomoček pipx in dodajte pot do wheelov, nameščenih s pipx, v iskalno pot sistema.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Namestite wheel amd-debug-tools iz PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Zaženite orodje amd-ttm za poizvedbo trenutnih nastavitev skupnega pomnilnika.
  ```bash
  amd-ttm
  ```

* Ponastavite nastavitve skupnega pomnilnika na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Ponovno zaženite sistem, da se spremembe uveljavijo.

## Inicializacija vsebnika vLLM

> **Opomba**: Ta korak izvedite tako na Stroju 1 kot na Stroju 2.

Vaš sistem Ryzen AI Halo je opremljen z vLLM, vgrajenim v vnaprej pripravljeno sliko vsebnika, ki jo poganjate z orodjem Podman, brezplačnim odprtokodnim orodjem za vsebnike.

### 1. Ustvarite mapo za prenos modelov

Ko v tem vodniku strežete model Qwen3.5-397B, bo vLLM samodejno prenesel uteži modela na vaš sistem. Da bi zagotovili, da so te uteži dostopne znotraj vsebnika, najprej ustvarite mapo za modele, ki jo lahko vsebnik priklopi:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Zaženite vsebnik vLLM

Spodnji ukaz zažene vsebnik in vas postavi v interaktivno lupino. Priklopi mapo za modele, ki ste jo pravkar ustvarili, in posreduje vaš `IFNAME` v `NCCL_SOCKET_IFNAME` ter `GLOO_SOCKET_IFNAME`, s čimer sporoči RCCL (knjižnici, ki jo vLLM uporablja za usklajevanje GPU-jev v gruči), kateri vmesnik naj uporabi.

Zaženite vsebnik z:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Opomba**: Zamenjajte `<IFNAME>` z imenom izhodnega vmesnika iz [1. Določitev omrežnih vmesnikov](#1-določitev-omrežnih-vmesnikov)

## Poganjanje modela na gruči

vLLM za organizacijo gruče uporablja Ray, za komunikacijo med GPU-ji na različnih vozliščih pa RCCL. En stroj deluje kot **glavno vozlišče** (Stroj 1) in usklajuje sklepanje. Drugi se pridruži kot **delovno vozlišče** (Stroj 2) ter prispeva svoj GPU pomnilnik in računsko zmogljivost.

> **Opomba**: Ray je izbirna odvisnost za vLLM in je na voljo samo znotraj vnaprej konfiguriranega vsebnika Podman.

Ob zagonu vLLM razdeli model med obe vozlišči z uporabo tenzorske paralelizacije. Ko je model naložen, sklepanje poteka, kot da bi teklo na enem samem pospeševalniku.

#### Preprečevanje napak OOM v Ray

Ray privzeto nadzoruje pomnilnik gostitelja na vsakem vozlišču in ustavi največji proces, ko poraba pomnilnika preseže 95 %. Na vašem sistemu Ryzen™ AI Halo si GPU in gostitelj delita en sam pomnilniški bazen, zato lahko nalaganje modela sproži napako `ray.exceptions.OutOfMemoryError` in ustavi delovni proces.

Da to preprečimo, bomo na vsakem stroju pred zagonom in priključitvijo v gručo izvozili spremenljivko `RAY_memory_monitor_refresh_ms=0`.
### Korak 1: Zaženite Ray glavno vozlišče (Machine 1)

Na Machine 1 zaženite Ray glavno vozlišče, da inicializirate gručo:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Iskanje `<MACHINE_1_IP>`**: Na Machine 1 zaženite `hostname -I | awk '{print $1}'`, da poiščete njegov lokalni naslov IP.

### Korak 2: Pridružite se gruči (Machine 2)

Na Machine 2 se povežite z glavnim vozliščem, da tvorite gručo:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Iskanje `<MACHINE_2_IP>`**: Na Machine 2 zaženite `hostname -I | awk '{print $1}'`, da poiščete njegov lokalni naslov IP.

### Korak 3: Postrezite model (Machine 1)

Na Machine 1 zaženite strežnik vLLM. To bo samodejno preneslo model in ga začelo postreči prek obeh vozlišč:

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
| `--port` | Vrata za postrežbo HTTP API |
| `--host` | Naslov IP, na katerega se veže strežnik (`0.0.0.0` za vse vmesnike) |
| `--max-model-len` | Največja dolžina konteksta v žetonih |
| `--gpu-memory-utilization` | Delež pomnilnika GPU za dodelitev (0,0–1,0) |
| `--dtype` | Podatkovni tip za uteži modela |
| `--tensor-parallel-size` | Število GPE-jev, med katerimi se razdeli model (nastavite na skupno število GPE-jev v gruči) |
| `--distributed-executor-backend` | Zaledje za izvajanje na več vozliščih (`ray` za razporeditve v gruči) |
| `--enforce-eager` | Onemogoči prevajanje CUDA graf za združljivost |
| `--language-model-only` | Preskoči nalaganje pomožnih komponent modela (npr. vizualni kodirnik) |
| `--reasoning-parser` | Omogoči strukturirano razčlenjevanje izhoda sklepanja za model |

Za popolno uporabo parametrov si oglejte [dokumentacijo vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Dostop do modela

vLLM izpostavlja API, združljiv z OpenAI, zato lahko na svojo gručo povežete kateri koli združljiv odjemalec ali vmesnik. Ena priljubljena možnost je [Open WebUI](https://github.com/open-webui/open-webui), ki ponuja klepetalni vmesnik v brskalniku.

Za povezavo Open WebUI z vašo končno točko vLLM:

1. Odprite **Settings** > **Admin Panel** > **Connections**
2. Kliknite **+** pri **Manage OpenAI API Connections**
3. Nastavite **Connection Type** na **External**
4. Nastavite **URL** na `http://<MACHINE_1_IP>:7000/v1`
5. Pod **Auth** izberite **None** iz spustnega seznama
6. Pustite **Model IDs** prazno, da se samodejno odkrijejo vsi modeli s končne točke

> **Iskanje `<MACHINE_1_IP>`**: Na Machine 1 zaženite `hostname -I | awk '{print $1}'`, da poiščete njegov lokalni naslov IP. Če dostopate do Open WebUI z Machine 1 samega, lahko uporabite `http://localhost:7000/v1`.

![Nastavitve povezave Open WebUI za končno točko vLLM](assets/openwebui-connection.png)

Ko je povezava vzpostavljena, izberite model iz spustnega seznama modelov v Open WebUI in začnite klepetati. Model zdaj deluje na obeh vaših vozliščih Ryzen AI Halo:

![Klepetanje z Qwen3.5-397B v Open WebUI](assets/openwebui-chat.png)

## Naslednji koraki

- **Raziščite druge modele**: Odkrijte nove modele na [Hugging Face](https://huggingface.co/models?&sort=trending), ki ustrezajo skupnemu pomnilniku GPU vaše gruče
- **Razširite na štiri vozlišča**: Dodajte še dva sistema Ryzen AI Halo kot dodatna Ray delovna vozlišča, da razdelite modele med še več GPE-jev. To zahteva stikalo Ethernet z vsaj štirimi vrati, po enim za vsako vozlišče. Sledite [Koraku 2: Pridružite se gruči](#step-2-join-the-cluster-machine-2) na vsakem dodatnem delovnem vozlišču in ustrezno povečajte `--tensor-parallel-size`
- **Preizkusite druge strategije vzporednosti**: vLLM podpira [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) za modele tipa mixture-of-experts in [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) za večjo prepustnost. Eksperimentirajte z `--enable-expert-parallel` in `--data-parallel-size`, da najdete najboljšo konfiguracijo za svojo delovno obremenitev