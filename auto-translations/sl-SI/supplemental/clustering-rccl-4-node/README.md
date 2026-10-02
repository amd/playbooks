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

# Gručenje štirih naprav Ryzen™ AI Halo s pomočjo RCCL

## Pregled

Vaša naprava Ryzen™ AI Halo že zmore lokalno izvajati velike jezikovne modele. Gručenje to zmožnost nadgradi tako, da združi GPU pomnilnik več sistemov prek lokalnega omrežja, kar vam omogoča dostop do še večjih modelov z boljšim sklepanjem, boljšim generiranjem kode in globljim večjezičnim razumevanjem – vse to popolnoma na vaši lastni strojni opremi.

Ta vodnik vas nauči, kako gručiti štiri sisteme Ryzen AI Halo s pomočjo RCCL (ROCm Communication Collectives Library) skupaj z vLLM in kako izvesti model Qwen3.5-397B, model s 397 milijardami parametrov, na vseh štirih napravah s ROCm pospeševanjem.

## Kaj se boste naučili

- Kako razširiti dodelitev VRAM na sistemih Ryzen AI Halo
- Zagon vLLM s podporo ROCm
- Konfiguracija RCCL za sklepanje z več vozlišči in tenzorsko vzporednostjo na štirih sistemih Ryzen AI Halo
- Izvajanje modela s 397 milijardami parametrov na štirih omreženih sistemih Ryzen AI Halo

## Predpogoji

### Strojna oprema

Ta vodnik zahteva štiri enote Ryzen AI Halo in eno Ethernet stikalo, povezane v zvezdasti topologiji, pri čemer je vsaka enota neposredno povezana s stikalom.

| Komponenta | Količina | Opis |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Računska vozlišča, ki tvorijo gručo |
| 10Gbps Ethernet stikalo | 1 | Centralno stikalo za omogočanje komunikacije med več vozlišči Ryzen AI Halo (vsaj 4 vrata) |
| Ethernet kabel | 4 | Povezuje vsako enoto Halo s stikalom (priporočena vsaj kategorija Cat 7) |

> **Opomba**: Za povezavo štirih enot Ryzen AI Halo so potrebna štiri vrata Ethernet stikala. Peto vrata so potrebna, če do modela dostopate z ločenega odjemalskega računalnika namesto z ene od enot Halo.

### Programska oprema
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Namestitev fizične strojne opreme

> **Opomba**: Ta korak izvedite na vseh štirih napravah (naprava 1 do naprave 4).

Vsako enoto Ryzen AI Halo povežite z Ethernet stikalom s kablom Cat 7 (ali višje kategorije). S tem vzpostavite 10 Gbps povezavo, ki se uporablja za visokohitrostno komunikacijo med vozlišči.

### 1. Ugotovitev omrežnih vmesnikov

Na vsaki napravi poiščite ime njenega omrežnega vmesnika in si ga zabeležite (v nadaljevanju navodil se bo nanj sklicevalo kot `IFNAME`). Zaženite:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

To neposredno izpiše ime vmesnika, na primer:

```bash
enp191s0
```

### 2. Preverjanje hitrosti omrežne povezave

Preverite, da je povezava aktivna in deluje s polno hitrostjo, tako da preverite hitrost svojega vmesnika:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Opomba**: Nadomestite `<IFNAME>` z imenom izhodnega vmesnika iz poglavja [1. Ugotovitev omrežnih vmesnikov](#1-determine-network-interfaces)

Videti morate hitrost `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Opomba**: Če je hitrost nižja od `10000Mb/s` ali se povezava ne vzpostavi, preverite kabelsko povezavo in potrdite, da so vrata stikala nastavljena na 10 Gbps. Nekatera stikala zahtevajo, da onemogočite samodejno pogajanje (auto-negotiation) in ročno nastavite hitrost povezave; za več informacij glejte dokumentacijo vašega stikala.

## Razširitev dodelitve VRAM

> **Opomba**: Ta korak izvedite na vseh štirih napravah (naprava 1 do naprave 4).

### Konfiguracija pomnilnika za izvajanje velikih modelov

V sistemu Linux ROCm uporablja skupni nabor sistemskega pomnilnika, ta nabor pa je privzeto nastavljen na polovico sistemskega pomnilnika.

To količino lahko povečate s spremembo nastavitve strani v Translation Table Manager (TTM) jedra, kot je opisano v naslednjih navodilih. AMD priporoča nastavitev minimalnega namenskega VRAM-a v BIOS-u (0,5 GB).

* Namestite orodje pipx in dodajte pot za nameščene pakete pipx v sistemsko iskalno pot.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Namestite paket amd-debug-tools iz PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Zaženite orodje amd-ttm, da preverite trenutne nastavitve skupnega pomnilnika.
  ```bash
  amd-ttm
  ```

* Ponovno konfigurirajte nastavitve skupnega pomnilnika na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Ponovno zaženite sistem, da se spremembe uveljavijo.

## Inicializacija vsebnika vLLM

> **Opomba**: Ta korak izvedite na vseh štirih napravah (naprava 1 do naprave 4).

Vaša naprava Ryzen AI Halo je dobavljena z vLLM, zapakiranim v vnaprej pripravljeni sliki vsebnika, ki ga zaženete s pomočjo Podman, brezplačnega in odprtokodnega orodja za vsebnike.

### 1. Ustvarite imenik za prenos modela

Ko v tem vodniku strežete model Qwen3.5-397B, bo vLLM samodejno prenesel uteži modela v vaš sistem. Da zagotovite dostopnost teh uteži znotraj vsebnika, najprej ustvarite imenik za modele, ki ga lahko vsebnik priklopi:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Zaženite vsebnik vLLM

Spodnji ukaz zažene vsebnik in vas postavi v interaktivno lupino. Priklopi imenik za modele, ki ste ga pravkar ustvarili, in posreduje vaš `IFNAME` v `NCCL_SOCKET_IFNAME` in `GLOO_SOCKET_IFNAME`, s čimer sporoči RCCL (knjižnici, ki jo vLLM uporablja za usklajevanje GPU-jev v gruči), kateri vmesnik naj uporabi.

Zaženite vsebnik z:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Opomba**: Nadomestite `<IFNAME>` z imenom izhodnega vmesnika iz poglavja [1. Ugotovitev omrežnih vmesnikov](#1-determine-network-interfaces)

## Izvajanje modela na gruči

vLLM uporablja Ray za orkestracijo gruče in RCCL za upravljanje komunikacije med GPU-ji na različnih vozliščih. Ena naprava deluje kot glavno vozlišče (naprava 1), ki usklajuje sklepanje. Ostale tri se pridružijo kot delovna vozlišča (naprave 2, 3 in 4), ki prispevajo svoj GPU pomnilnik in zmogljivost.

> **Opomba**: Ray je neobvezna odvisnost za vLLM in je na voljo samo znotraj vnaprej konfiguriranega vsebnika Podman.

Ob zagonu vLLM razdeli model na vsa štiri vozlišča s pomočjo tenzorske vzporednosti. Ko je model naložen, sklepanje poteka, kot da bi se izvajalo na enem samem pospeševalniku.

#### Preprečevanje napak Ray OOM

Ray privzeto spremlja pomnilnik gostitelja na vsakem vozlišču in ustavi največji proces, ko poraba pomnilnika preseže 95 %. Na vaši napravi Ryzen™ AI Halo si GPU in gostitelj delita en sam nabor pomnilnika, zato lahko nalaganje modela sproži `ray.exceptions.OutOfMemoryError` in ustavi delovni proces.

Da bi to preprečili, bomo na vsaki napravi pred zagonom in priključitvijo h gruči izvozili `RAY_memory_monitor_refresh_ms=0`.
### Korak 1: Zagon glave vozlišča Ray (Stroj 1)

Na Stroju 1 zaženite glavo vozlišča Ray za inicializacijo gruče:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Iskanje `<MACHINE_1_IP>`**: Na Stroju 1 zaženite `hostname -I | awk '{print $1}'`, da poiščete njegov lokalni IP naslov.

### Korak 2: Pridružitev gruči (Stroji 2, 3 in 4)

Na vsakem od Strojev 2, 3 in 4 se povežite z glavo vozlišča, da oblikujete gručo:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_N_IP> --num-gpus=1
```

> **Iskanje `<MACHINE_N_IP>`**: Na vsakem delovnem stroju zaženite `hostname -I | awk '{print $1}'`, da poiščete njegov lokalni IP naslov.

### Korak 3: Serviranje modela (Stroj 1)

Na Stroju 1 zaženite strežnik vLLM. To bo samodejno preneslo model in ga začelo servirati preko vseh štirih vozlišč:

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

#### Referenca parametrov

| Zastavica | Namen |
|------|---------|
| `--port` | Vrata, na katerih se servira HTTP API |
| `--host` | IP naslov, na katerega se veže strežnik (`0.0.0.0` za vse vmesnike) |
| `--max-model-len` | Največja dolžina konteksta v žetonih |
| `--gpu-memory-utilization` | Delež pomnilnika GPU-ja za dodelitev (0,0–1,0) |
| `--dtype` | Podatkovni tip za uteži modela |
| `--tensor-parallel-size` | Število GPU-jev, med katerimi se razdeli model (nastavite na skupno število GPU-jev v gruči) |
| `--distributed-executor-backend` | Zaledje za izvajanje na več vozliščih (`ray` za razporejene namestitve) |
| `--enforce-eager` | Onemogoči prevajanje CUDA graph za združljivost |
| `--language-model-only` | Preskoči nalaganje pomožnih komponent modela (npr. vizualnega kodirnika) |
| `--reasoning-parser` | Omogoči strukturirano razčlenjevanje izhoda sklepanja za model |

Za celoten opis uporabe parametrov glejte [dokumentacijo vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Dostop do modela

vLLM izpostavi API, združljiv z OpenAI, tako da lahko s svojo gručo povežete kateri koli združljiv odjemalec ali vmesnik. Ena priljubljena možnost je [Open WebUI](https://github.com/open-webui/open-webui), ki ponuja klepetalni vmesnik v brskalniku.

Za povezavo Open WebUI z vašo vLLM končno točko:

1. Odprite **Settings** > **Admin Panel** > **Connections**
2. Kliknite **+** pri **Manage OpenAI API Connections**
3. Nastavite **Connection Type** na **External**
4. Nastavite **URL** na `http://<MACHINE_1_IP>:7000/v1`
5. Pod **Auth** izberite **None** iz spustnega menija
6. Pustite **Model IDs** prazno, da se samodejno odkrijejo vsi modeli s končne točke

> **Iskanje `<MACHINE_1_IP>`**: Na Stroju 1 zaženite `hostname -I | awk '{print $1}'`, da poiščete njegov lokalni IP naslov. Če dostopate do Open WebUI s Stroja 1, lahko uporabite `http://localhost:7000/v1`.

![Nastavitve povezave Open WebUI za vLLM končno točko](assets/openwebui-connection.png)

Ko ste povezani, izberite model iz spustnega menija modelov v Open WebUI in začnite klepetati. Model zdaj teče preko vseh štirih vaših vozlišč Ryzen AI Halo:

![Klepet z Qwen3.5-397B v Open WebUI](assets/openwebui-chat.png)

## Naslednji koraki

- **Raziščite druge modele**: Odkrijte nove modele na [Hugging Face](https://huggingface.co/models?&sort=trending), ki se prilegajo skupnemu pomnilniku GPU-jev vaše gruče
- **Razširitev preko štirih vozlišč**: Dodajte dodatne sisteme Ryzen AI Halo kot dodatne delavce Ray za razdelitev modelov med še več GPU-jev. Sledite navodilom [Korak 2: Pridružitev gruči](#step-2-join-the-cluster-machines-2-3-and-4) na vsakem dodatnem delovnem stroju in ustrezno povečajte `--tensor-parallel-size`
- **Preizkusite druge strategije vzporednosti**: vLLM podpira [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) za modele tipa mixture-of-experts in [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) za večjo prepustnost. Eksperimentirajte z `--enable-expert-parallel` in `--data-parallel-size`, da najdete najboljšo konfiguracijo za vašo delovno obremenitev