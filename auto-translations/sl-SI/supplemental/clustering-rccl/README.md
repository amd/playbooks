<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, nekateri koraki, ukazi, prenosi ali razpoložljivost izdelkov pa se lahko razlikujejo glede na vaš jezik ali regijo. Če se vam kaj zdi napačno, upoštevajte, da je izvirni angleški playbook merodajni vir.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> V tem priročniku so uporabljene posebne oznake, ki jih GitHub ne more upodobiti. Za pravilen predogled te vsebine obiščite [amd.com/playbooks](https://amd.com/playbooks).
<!-- @github-only:end -->

# Povezovanje dveh sistemov Ryzen™ AI Halo v gručo z RCCL

## Pregled

Vaš sistem Ryzen™ AI Halo je že sposoben lokalno poganjati velike jezikovne modele. Povezovanje v gručo to zmožnost še razširi, saj združi pomnilnik GPU več sistemov prek lokalnega omrežja, kar vam omogoča dostop do še večjih modelov z močnejšim sklepanjem, boljšim generiranjem kode in globljim razumevanjem več jezikov – vse to popolnoma na vaši lastni strojni opremi.

Ta priročnik vas nauči, kako povezati dva sistema Ryzen AI Halo v gručo z uporabo RCCL (ROCm Communication Collectives Library) skupaj z vLLM ter kako na obeh napravah zagnati Qwen3.5-397B, model s 397 milijardami parametrov, z pospeševanjem ROCm.

## Kaj se boste naučili

- Kako razširiti dodelitev pomnilnika VRAM na sistemih Ryzen AI Halo
- Zagon vLLM s podporo ROCm
- Konfiguracija RCCL za medvozliščno tenzorsko-paralelno sklepanje na dveh sistemih Ryzen AI Halo
- Zagon modela s 397 milijardami parametrov na dveh povezanih sistemih Ryzen AI Halo

## Predpogoji

### Strojna oprema

Ta priročnik zahteva dve enoti Ryzen AI Halo in eno omrežno stikalo Ethernet, povezani v zvezdasto topologijo, pri čemer je vsaka enota povezana neposredno s stikalom.

| Komponenta | Količina | Opis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Računalniška vozlišča, ki tvorita gručo |
| 10-gigabitno omrežno stikalo Ethernet | 1 | Osrednje stikalo, ki omogoča komunikacijo med več vozlišči Ryzen AI Halo (vsaj 2 vrat) |
| Kabel Ethernet | 2 | Poveže vsako enoto Halo s stikalom (priporočen Cat 7 ali boljši) |

> **Opomba**: Za povezavo obeh enot Ryzen AI Halo sta potrebni dve vrata omrežnega stikala. Tretja vrata so potrebna, če do modela dostopate z ločenega odjemalskega računalnika namesto z ene od enot Halo.

### Programska oprema
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fizična priprava strojne opreme

> **Opomba**: Ta korak izvedite na Napravi 1 in Napravi 2.

Vsako enoto Ryzen AI Halo povežite z omrežnim stikalom s kablom Cat 7 (ali boljšim). S tem vzpostavite 10-gigabitno povezavo, ki se uporablja za visokohitrostno komunikacijo med vozlišči.

### 1. Ugotovitev omrežnih vmesnikov

Na vsaki napravi poiščite ime njenega omrežnega vmesnika in si ga zapišite (v nadaljevanju navodil bo imenovan `IFNAME`). Zaženite:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

To izpiše ime vmesnika, na primer:

```bash
enp191s0
```

### 2. Preverjanje hitrosti omrežne povezave

Prepričajte se, da je povezava aktivna in deluje s polno hitrostjo, tako da preverite hitrost svojega vmesnika:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Opomba**: `<IFNAME>` zamenjajte z imenom izhodnega vmesnika iz razdelka [1. Ugotovitev omrežnih vmesnikov](#1-determine-network-interfaces)

Videti bi morali hitrost `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Opomba**: Če je hitrost nižja od `10000Mb/s` ali povezava ne deluje, preverite kabelsko povezavo in se prepričajte, da so vrata stikala nastavljena na 10 Gb/s. Nekatera stikala zahtevajo, da onemogočite samodejno pogajanje o hitrosti in hitrost povezave nastavite ročno; za več informacij glejte dokumentacijo svojega stikala.

## Razširitev dodelitve pomnilnika VRAM

> **Opomba**: Ta korak izvedite na Napravi 1 in Napravi 2.

### Konfiguracija pomnilnika za zagon velikih modelov

V sistemu Linux ROCm uporablja skupni sistemski pomnilniški nabor, ki je privzeto konfiguriran na polovico sistemskega pomnilnika.

To količino lahko povečate s spremembo nastavitve strani upravitelja prevajalne tabele (Translation Table Manager, TTM) jedra, in sicer po naslednjih navodilih. AMD priporoča, da v BIOS-u nastavite minimalno namensko VRAM (0,5 GB).

* Namestite pripomoček pipx in dodajte pot za lupine (wheels), nameščene s pipx, v sistemsko iskalno pot.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Namestite lupino amd-debug-tools iz PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Zaženite orodje amd-ttm za poizvedbo trenutnih nastavitev skupnega pomnilnika.
  ```bash
  amd-ttm
  ```

* Ponovno konfigurirajte nastavitve skupnega pomnilnika na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Znova zaženite sistem, da se spremembe uveljavijo.

## Inicializacija vsebnika vLLM

> **Opomba**: Ta korak izvedite na Napravi 1 in Napravi 2.

Vaš sistem Ryzen AI Halo je opremljen z vLLM, pakiranim znotraj vnaprej pripravljene vsebniške slike, ki jo zaženete z orodjem Podman, brezplačnim in odprtokodnim orodjem za vsebnike.

### 1. Ustvarjanje mape za prenos modela

Ko boste v tem priročniku poganjali model Qwen3.5-397B, bo vLLM samodejno prenesel uteži modela v vaš sistem. Da bodo te uteži dostopne znotraj vsebnika, najprej ustvarite mapo za modele, ki jo bo vsebnik lahko priklopil:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Zagon vsebnika vLLM

Spodnji ukaz zažene vsebnik in vas postavi v interaktivno lupino. Priklopi mapo za modele, ki ste jo pravkar ustvarili, in posreduje vaš `IFNAME` spremenljivkama `NCCL_SOCKET_IFNAME` in `GLOO_SOCKET_IFNAME`, s čimer knjižnici RCCL (ki jo vLLM uporablja za usklajevanje procesnih enot GPU po celotni gruči) sporoči, kateri vmesnik naj uporabi.

Zaženite vsebnik z ukazom:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Opomba**: `<IFNAME>` zamenjajte z imenom izhodnega vmesnika iz razdelka [1. Ugotovitev omrežnih vmesnikov](#1-determine-network-interfaces)

## Zagon modela v gruči

vLLM uporablja Ray za orkestracijo gruče in RCCL za obravnavo komunikacije med procesnimi enotami GPU na različnih vozliščih. Ena naprava deluje kot **glavno vozlišče** (Naprava 1) in usklajuje sklepanje. Druga se pridruži kot **delovno vozlišče** (Naprava 2) ter prispeva svoj pomnilnik GPU in računsko zmogljivost.

> **Opomba**: Ray je neobvezna odvisnost za vLLM in je na voljo samo znotraj vnaprej konfiguriranega vsebnika Podman.

Ob zagonu vLLM razdeli model na oba vozla z uporabo tenzorske paralelizacije. Ko je model naložen, sklepanje poteka tako, kot da bi teklo na eni sami pospeševalni napravi.

### Korak 1: Zagon glavnega vozlišča Ray (Naprava 1)

Na Napravi 1 zaženite glavno vozlišče Ray, da inicializirate gručo:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Iskanje `<MACHINE_1_IP>`**: Na Napravi 1 zaženite `hostname -I | awk '{print $1}'`, da poiščete njen lokalni naslov IP.
### Korak 2: Pridružitev gruči (Naprava 2)

Na Napravi 2 se povežite z glavnim vozliščem, da tvorite gručo:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Iskanje `<MACHINE_2_IP>`**: Na Napravi 2 zaženite `hostname -I | awk '{print $1}'`, da poiščete njen lokalni IP naslov.

### Korak 3: Postrezite model (Naprava 1)

Na Napravi 1 zaženite strežnik vLLM. To bo samodejno preneslo model in ga začelo strežiti na obeh vozliščih:

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
| `--port` | Vrata za streženje HTTP API-ja |
| `--host` | IP naslov, na katerega se veže strežnik (`0.0.0.0` za vse vmesnike) |
| `--max-model-len` | Največja dolžina konteksta v žetonih |
| `--gpu-memory-utilization` | Delež pomnilnika GPE, ki naj se dodeli (0.0–1.0) |
| `--dtype` | Podatkovni tip za uteži modela |
| `--tensor-parallel-size` | Število GPE-jev, med katerimi naj se model razdeli (nastavite na skupno število GPE-jev v gruči) |
| `--distributed-executor-backend` | Zaledje za izvajanje na več vozliščih (`ray` za razporeditve gruč) |
| `--enforce-eager` | Onemogoči prevajanje grafov CUDA zaradi združljivosti |
| `--language-model-only` | Preskoči nalaganje pomožnih komponent modela (npr. vizualnega kodirnika) |
| `--reasoning-parser` | Omogoči razčlenjevanje strukturiranega izhoda sklepanja za model |

Za popolno uporabo parametrov glejte [dokumentacijo vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Dostop do modela

vLLM izpostavi API, združljiv z OpenAI, tako da lahko na svojo gručo povežete kateri koli združljiv odjemalec ali vmesnik. Ena priljubljena možnost je [Open WebUI](https://github.com/open-webui/open-webui), ki ponuja klepetalni vmesnik prek brskalnika.

Za povezavo Open WebUI z vašo končno točko vLLM:

1. Odprite **Settings** > **Admin Panel** > **Connections**
2. Kliknite **+** na **Manage OpenAI API Connections**
3. Nastavite **Connection Type** na **External**
4. Nastavite **URL** na `http://<MACHINE_1_IP>:7000/v1`
5. Pod **Auth** izberite **None** iz spustnega seznama
6. Pustite **Model IDs** prazno, da se samodejno odkrijejo vsi modeli iz končne točke

> **Iskanje `<MACHINE_1_IP>`**: Na Napravi 1 zaženite `hostname -I | awk '{print $1}'`, da poiščete njen lokalni IP naslov. Če do Open WebUI dostopate z same Naprave 1, lahko uporabite `http://localhost:7000/v1`.

![Nastavitve povezave Open WebUI za končno točko vLLM](assets/openwebui-connection.png)

Ko je povezava vzpostavljena, izberite model iz spustnega seznama modelov v Open WebUI in začnite klepetati. Model zdaj deluje na obeh vaših vozliščih Ryzen AI Halo:

![Klepet z Qwen3.5-397B v Open WebUI](assets/openwebui-chat.png)

## Naslednji koraki

- **Raziščite druge modele**: Odkrijte nove modele na [Hugging Face](https://huggingface.co/models?&sort=trending), ki ustrezajo skupnemu pomnilniku GPE vaše gruče
- **Razširitev na štiri vozlišča**: Dodajte še dva sistema Ryzen AI Halo kot dodatna delovna vozlišča Ray za razdelitev modelov na še več GPE-jev. To zahteva ethernetno stikalo z vsaj štirimi vrati, po enim za vsako vozlišče. Sledite navodilom v [Korak 2: Pridružitev gruči](#step-2-join-the-cluster-machine-2) na vsakem dodatnem delovnem vozlišču in ustrezno povečajte `--tensor-parallel-size`
- **Preizkusite druge strategije paralelizma**: vLLM podpira [ekspertni paralelizem](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) za modele tipa mixture-of-experts in [podatkovni paralelizem](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) za višjo prepustnost. Eksperimentirajte z `--enable-expert-parallel` in `--data-parallel-size`, da najdete najboljšo konfiguracijo za vašo delovno obremenitev