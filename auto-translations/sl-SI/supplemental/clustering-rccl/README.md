<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Združevanje dveh sistemov Ryzen™ AI Halo z RCCL

## Pregled

Vaš sistem Ryzen™ AI Halo je že zmožen lokalno poganjati velike jezikovne modele. Združevanje v gručo to nadgradi s kombiniranjem pomnilnika GPU več sistemov prek lokalnega omrežja, kar vam omogoča dostop do še večjih modelov z močnejšim sklepanjem, boljšim generiranjem kode in globljim večjezičnim razumevanjem – vse skupaj v celoti na vaši lastni strojni opremi.

Ta priročnik vas uči, kako združiti dva sistema Ryzen AI Halo v gručo z uporabo RCCL (ROCm Communication Collectives Library) skupaj z vLLM ter poganjati Qwen3.5-397B, model s 397 milijardami parametrov, na obeh strojih s pospeševanjem ROCm.

## Kaj se boste naučili

- Kako razširiti dodelitev VRAM na sistemih Ryzen AI Halo
- Zagon vLLM s podporo ROCm
- Konfiguriranje RCCL za večvozliščno vzporedno sklepanje s tenzorji na dveh sistemih Ryzen AI Halo
- Poganjanje modela s 397 milijardami parametrov na dveh omrežno povezanih sistemih Ryzen AI Halo

## Predpogoji

### Strojna oprema

Ta priročnik zahteva dve enoti Ryzen AI Halo in en stikalo Ethernet, povezano v zvezdasto topologijo, pri čemer je vsaka enota neposredno žično priključena na stikalo.

| Komponenta | Količina | Opis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Računska vozlišča, ki tvorijo gručo |
| Stikalo Ethernet 10 Gbps | 1 | Centralno stikalo za komunikacijo med vozlišči Ryzen AI Halo (vsaj 2 vrati) |
| Kabel Ethernet | 2 | Poveže vsako enoto Halo s stikalom (priporočen Cat 7 ali višji) |

> **Opomba**: Za povezavo dveh enot Ryzen AI Halo sta potrebni dve vrati stikala Ethernet. Tretja vrata so potrebna, če do modela dostopate z ločenega odjemalskega računalnika namesto z ene od enot Halo.

### Programska oprema
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Namestitev fizične strojne opreme

> **Opomba**: Ta korak izvedite na obeh računalnikih – Računalniku 1 in Računalniku 2.

Vsako enoto Ryzen AI Halo priključite na stikalo Ethernet s kablom Cat 7 (ali višjim). S tem vzpostavite povezavo 10 Gbps, ki se uporablja za hitro komunikacijo med vozlišči.

### 1. Določite omrežne vmesnike

Na vsakem računalniku poiščite ime njegovega omrežnega vmesnika in si ga zabeležite (v nadaljevanju navodil bo označeno kot `IFNAME`). Zaženite:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

To neposredno izpiše ime vmesnika, na primer:

```bash
enp191s0
```

### 2. Preverite hitrosti omrežnih povezav

Potrdite, da je povezava aktivna in deluje pri polni hitrosti, tako da preverite hitrost vašega vmesnika:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Opomba**: Zamenjajte `<IFNAME>` z imenom izhodnega vmesnika iz razdelka [1. Določite omrežne vmesnike](#1-determine-network-interfaces)

Prikazati bi se morala hitrost `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Opomba**: Če je hitrost nižja od `10000Mb/s` ali se povezava ne vzpostavi, preverite kabelsko priključitev in potrdite, da je vrata stikala nastavljeno na 10 Gbps. Nekatera stikala zahtevajo onemogočanje samodejnega pogajanja in ročno nastavitev hitrosti povezave; glejte dokumentacijo vašega stikala.

## Razširitev dodelitve VRAM

> **Opomba**: Ta korak izvedite na obeh računalnikih – Računalniku 1 in Računalniku 2.

### Konfiguracija pomnilnika za poganjanje velikih modelov

V sistemu Linux ROCm uporablja skupni sistemski pomnilniški bazen, ki je privzeto konfiguriran na polovico sistemskega pomnilnika.

To količino je mogoče povečati s spremembo nastavitve strani Translation Table Manager (TTM) jedra, z naslednjimi navodili. AMD priporoča nastavitev minimalnega namenskega VRAM v BIOS-u (0,5 GB).

* Namestite pripomoček pipx in dodajte pot za kolesa, nameščena s pipx, v sistemsko iskalno pot.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Namestite kolo amd-debug-tools iz PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Zaženite orodje amd-ttm za poizvedbo o trenutnih nastavitvah skupnega pomnilnika.
  ```bash
  amd-ttm
  ```

* Znova konfigurirajte nastavitve skupnega pomnilnika na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Znova zaženite sistem, da spremembe začnejo veljati.

## Inicializacija vsebnika vLLM

> **Opomba**: Ta korak izvedite na obeh računalnikih – Računalniku 1 in Računalniku 2.

Vaš Ryzen AI Halo je opremljen z vLLM, zapakiranim v vnaprej pripravljeno sliko vsebnika, ki jo zaženete z orodjem Podman – brezplačnim odprtokodnim orodjem za vsebnike.

### 1. Ustvarite imenik za prenos modelov

Ko v tem priročniku strežete model Qwen3.5-397B, bo vLLM samodejno prenesel uteži modela v vaš sistem. Da zagotovite dostopnost teh uteži znotraj vsebnika, najprej ustvarite imenik za modele, ki ga vsebnik lahko priklopi:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Zaženite vsebnik vLLM

Spodnji ukaz zažene vsebnik in vas postavi v interaktivno lupino. Priklopi imenik za modele, ki ste ga pravkar ustvarili, in posreduje vaš `IFNAME` spremenljivkama `NCCL_SOCKET_IFNAME` in `GLOO_SOCKET_IFNAME`, s čimer RCCL-u (knjižnici, ki jo vLLM uporablja za usklajevanje GPU-jev v gruči) sporoči, kateri vmesnik naj uporabi.

Zaženite vsebnik z:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Opomba**: Zamenjajte `<IFNAME>` z imenom izhodnega vmesnika iz razdelka [1. Določite omrežne vmesnike](#1-determine-network-interfaces)

## Poganjanje modela na gruči

vLLM uporablja Ray za orkestracijo gruče in RCCL za upravljanje komunikacije GPU-GPU med vozlišči. En računalnik deluje kot **glavo vozlišče** (Računalnik 1) in usklajuje sklepanje. Drugi se pridruži kot **delavsko vozlišče** (Računalnik 2) in prispeva svoj pomnilnik GPU ter računsko moč.

> **Opomba**: Ray je neobvezna odvisnost za vLLM in je na voljo samo znotraj vnaprej konfiguriranega vsebnika Podman.

Ob zagonu vLLM razdeli model med obe vozlišči z uporabo tenzorske vzporednosti. Ko je model naložen, sklepanje poteka, kot da bi teklo na enem samem pospeševalniku.

### Korak 1: Zaženite glavo vozlišče Ray (Računalnik 1)

Na Računalniku 1 zaženite glavo vozlišče Ray za inicializacijo gruče:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Iskanje `<MACHINE_1_IP>`**: Na Računalniku 1 zaženite `hostname -I | awk '{print $1}'`, da poiščete njegov lokalni IP naslov.

### Korak 2: Pridružite se gruči (Računalnik 2)

Na Računalniku 2 se povežite z glavnim vozliščem, da tvorite gručo:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Iskanje `<MACHINE_2_IP>`**: Na Računalniku 2 zaženite `hostname -I | awk '{print $1}'`, da poiščete njegov lokalni IP naslov.

### Korak 3: Strežite model (Računalnik 1)

Na Računalniku 1 zaženite strežnik vLLM. Ta bo samodejno prenesel model in ga začel strežiti prek obeh vozlišč:

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
| `--host` | IP naslov, na katerega se strežnik poveže (`0.0.0.0` za vse vmesnike) |
| `--max-model-len` | Največja dolžina konteksta v žetonih |
| `--gpu-memory-utilization` | Delež pomnilnika GPU za dodelitev (0,0–1,0) |
| `--dtype` | Podatkovni tip za uteži modela |
| `--tensor-parallel-size` | Število GPU-jev za razdelitev modela (nastavljeno na skupno število GPU-jev v gruči) |
| `--distributed-executor-backend` | Zaledni sistem za večvozliščno izvajanje (`ray` za namestitve v gruči) |
| `--enforce-eager` | Onemogoči prevajanje grafov CUDA za združljivost |
| `--language-model-only` | Preskoči nalaganje pomožnih komponent modela (npr. kodiralnika slik) |
| `--reasoning-parser` | Omogoči strukturirano razčlenjevanje izhodnih sklepov za model |

Za celotno uporabo parametrov glejte [dokumentacijo vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Dostop do modela

vLLM izpostavlja API, združljiv z OpenAI, zato lahko na svojo gručo povežete katerega koli združljivega odjemalca ali vmesnik. Ena priljubljena možnost je [Open WebUI](https://github.com/open-webui/open-webui), ki zagotavlja klepetalni vmesnik v brskalniku.

Za povezavo Open WebUI z vašo končno točko vLLM:

1. Odprite **Nastavitve** > **Skrbniška plošča** > **Povezave**
2. Kliknite **+** pri **Upravljanje povezav OpenAI API**
3. Nastavite **Vrsto povezave** na **Zunanja**
4. Nastavite **URL** na `http://<MACHINE_1_IP>:7000/v1`
5. Pod **Avtentikacija** izberite **Brez** iz spustnega menija
6. Pustite **ID-je modelov** prazne za samodejno odkrivanje vseh modelov iz končne točke

> **Iskanje `<MACHINE_1_IP>`**: Na Računalniku 1 zaženite `hostname -I | awk '{print $1}'`, da poiščete njegov lokalni IP naslov. Če dostopate do Open WebUI z Računalnika 1, lahko uporabite `http://localhost:7000/v1`.

![Nastavitve povezave Open WebUI za končno točko vLLM](assets/openwebui-connection.png)

Ko je povezava vzpostavljena, izberite model iz spustnega menija modelov v Open WebUI in začnite klepetati. Model zdaj teče na obeh vaših vozliščih Ryzen AI Halo:

![Klepet z modelom Qwen3.5-397B v Open WebUI](assets/openwebui-chat.png)

## Naslednji koraki

- **Raziščite druge modele**: Odkrijte nove modele na [Hugging Face](https://huggingface.co/models?&sort=trending), ki ustrezajo skupnemu pomnilniku GPU vaše gruče
- **Razširite na štiri vozlišča**: Dodajte še dva sistema Ryzen AI Halo kot dodatna delavska vozlišča Ray za razdelitev modelov prek še več GPU-jev. To zahteva stikalo Ethernet z vsaj štirimi vrati, po eno za vsako vozlišče. Sledite razdelku [Korak 2: Pridružite se gruči](#step-2-join-the-cluster-machine-2) na vsakem dodatnem delavcu in ustrezno povečajte `--tensor-parallel-size`
- **Preizkusite druge strategije vzporednosti**: vLLM podpira [vzporednost strokovnjakov](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) za modele mixture-of-experts in [podatkovno vzporednost](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) za večjo prepustnost. Eksperimentirajte z `--enable-expert-parallel` in `--data-parallel-size`, da poiščete najboljšo konfiguracijo za vaše delovno obremenitev