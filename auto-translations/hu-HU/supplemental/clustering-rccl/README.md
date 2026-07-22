<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Gépi fordítás.** Ez az oldal automatikusan lett lefordítva angolról, és emberi lektorálás nem történt. Hibákat tartalmazhat, és egyes lépések, parancsok, letöltések vagy termékelérhetőségek eltérhetnek az Ön nyelvében vagy régiójában. Ha bármi hibásnak tűnik, tekintse az eredeti angol nyelvű playbookot mérvadó forrásnak.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> Ez a útmutató speciális címkéket használ, amelyeket a GitHub nem tud megjeleníteni. A tartalom helyes megtekintéséhez látogasson el a [amd.com/playbooks](https://amd.com/playbooks) oldalra.
<!-- @github-only:end -->

# Két Ryzen™ AI Halo rendszer klaszterezése RCCL segítségével

## Áttekintés

Az Ön Ryzen™ AI Halo rendszere már önmagában is képes nagy nyelvi modellek helyi futtatására. A klaszterezés ezt tovább viszi azáltal, hogy több rendszer GPU-memóriáját kombinálja egy helyi hálózaton keresztül, így hozzáférést biztosítva még nagyobb modellekhez, erősebb következtetési képességgel, jobb kódgenerálással és mélyebb többnyelvű megértéssel, mindezt teljes egészében a saját hardveren.

Ez az útmutató megtanítja, hogyan klaszterezzen két Ryzen AI Halo rendszert RCCL (ROCm Communication Collectives Library) segítségével vLLM-mel, és hogyan futtassa a Qwen3.5-397B, egy 397 milliárd paraméteres modellt mindkét gépen ROCm gyorsítással.

## Amit meg fog tanulni

- Hogyan bővítheti ki a VRAM-allokációt Ryzen AI Halo rendszereken
- vLLM indítása ROCm támogatással
- RCCL konfigurálása többcsomópontos tenzorpárhuzamos következtetéshez két Ryzen AI Halo rendszer között
- Egy 397 milliárd paraméteres modell futtatása két hálózatba kötött Ryzen AI Halo rendszeren

## Előfeltételek

### Hardver

Ehhez az útmutatóhoz két Ryzen AI Halo egység és egy Ethernet switch szükséges, csillag topológiában összekötve, mindegyik egység közvetlenül a switchhez csatlakoztatva.

| Komponens | Mennyiség | Leírás |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | A klasztert alkotó számítási csomópontok |
| 10 Gbps-os Ethernet switch | 1 | Központi switch a többcsomópontos Ryzen AI Halo kommunikáció lehetővé tételéhez (legalább 2 port) |
| Ethernet kábel | 2 | Az egyes Halo egységeket köti össze a switchhel (Cat 7 vagy magasabb ajánlott) |

> **Megjegyzés**: Két Ethernet switch port szükséges a két Ryzen AI Halo egység összekötéséhez. Egy harmadik port szükséges, ha a modellhez egy külön kliensgépről fér hozzá, nem pedig az egyik Halo egységről.

### Szoftver
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fizikai hardver beállítása

> **Megjegyzés**: Ezt a lépést végezze el mind az 1. gépen, mind a 2. gépen.

Csatlakoztassa mindkét Ryzen AI Halo egységet az Ethernet switchhez egy Cat 7 (vagy magasabb) kábellel. Ez hozza létre a 10 Gbps-os kapcsolatot, amelyet a csomópontok közötti nagysebességű kommunikáció használ.

### 1. Hálózati interfészek meghatározása

Mindegyik gépen keresse meg a hálózati interfész nevét, és jegyezze fel (az utasítások további részében `IFNAME`-ként fogunk rá hivatkozni). Futtassa:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Ez közvetlenül kiírja az interfész nevét, például:

```bash
enp191s0
```

### 2. Hálózati kapcsolat sebességének ellenőrzése

Győződjön meg arról, hogy a kapcsolat aktív és teljes sebességgel fut, az interfész sebességének ellenőrzésével:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Megjegyzés**: Cserélje ki a `<IFNAME>` értékét az [1. Hálózati interfészek meghatározása](#1-hálózati-interfészek-meghatározása) lépésben kapott kimeneti interfész nevére

`10000Mb/s` sebességet kell látnia:

```bash
	Speed: 10000Mb/s
```

> **Megjegyzés**: Ha a sebesség alacsonyabb, mint `10000Mb/s`, vagy a kapcsolat nem jön létre, ellenőrizze a kábelcsatlakozást, és győződjön meg róla, hogy a switch portja 10 Gbps-ra van állítva. Néhány switch esetén szükséges lehet az automatikus egyeztetés (auto-negotiation) kikapcsolása és a kapcsolat sebességének manuális beállítása; tekintse meg a switch dokumentációját.

## VRAM-allokáció kibővítése

> **Megjegyzés**: Ezt a lépést végezze el mind az 1. gépen, mind a 2. gépen.

### Memóriakonfiguráció nagy modellek futtatásához

Linuxon a ROCm egy megosztott rendszermemória-készletet használ, és ez a készlet alapértelmezés szerint a rendszermemória felére van beállítva.

Ez a mennyiség növelhető a kernel Translation Table Manager (TTM) oldalbeállításának módosításával, az alábbi utasítások szerint. Az AMD javasolja a minimális dedikált VRAM beállítását a BIOS-ban (0,5 GB).

* Telepítse a pipx segédprogramot, és adja hozzá a pipx által telepített wheel-ek elérési útját a rendszer keresési útvonalához.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Telepítse az amd-debug-tools wheel csomagot a PyPI-ról.
  ```bash
  pipx install amd-debug-tools
  ```

* Futtassa az amd-ttm eszközt a megosztott memória jelenlegi beállításainak lekérdezéséhez.
  ```bash
  amd-ttm
  ```

* Állítsa be a megosztott memória beállításait **120 GB**-ra:
  ```bash
  amd-ttm --set 120
  ```

* Indítsa újra a rendszert, hogy a változtatások életbe lépjenek.

## vLLM konténer inicializálása

> **Megjegyzés**: Ezt a lépést végezze el mind az 1. gépen, mind a 2. gépen.

Az Ön Ryzen AI Halo rendszere vLLM-mel érkezik, amely egy előre elkészített konténer image-be van csomagolva, amelyet a Podman, egy ingyenes és nyílt forráskódú konténereszköz segítségével futtathat.

### 1. Modellletöltési könyvtár létrehozása

Amikor ebben az útmutatóban a Qwen3.5-397B modellt kiszolgálja, a vLLM automatikusan letölti a modell súlyait a rendszerére. Annak érdekében, hogy ezek a súlyok elérhetők legyenek a konténeren belülről, először hozzon létre egy models könyvtárat, amelyet a konténer csatolni tud:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. vLLM konténer indítása

Az alábbi parancs elindítja a konténert, és egy interaktív parancssorba helyezi Önt. Csatolja az imént létrehozott models könyvtárat, és átadja az Ön `IFNAME` értékét a `NCCL_SOCKET_IFNAME` és `GLOO_SOCKET_IFNAME` változóknak, jelezve az RCCL-nek (a könyvtárnak, amelyet a vLLM a GPU-k klaszteren belüli koordinálásához használ), hogy melyik interfészt használja.

Indítsa el a konténert:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Megjegyzés**: Cserélje ki a `<IFNAME>` értékét az [1. Hálózati interfészek meghatározása](#1-hálózati-interfészek-meghatározása) lépésben kapott kimeneti interfész nevére

## A modell futtatása a klaszteren

A vLLM a Ray-t használja a klaszter orkesztrálásához, és az RCCL-t a csomópontok közötti GPU-GPU kommunikáció kezeléséhez. Az egyik gép **fő csomópontként** (Machine 1) működik, koordinálva a következtetést. A másik **worker csomópontként** (Machine 2) csatlakozik, hozzájárulva GPU-memóriájával és számítási kapacitásával.

> **Megjegyzés**: A Ray egy opcionális függőség a vLLM számára, és csak az előre konfigurált Podman konténeren belülről érhető el.

Indításkor a vLLM tenzorpárhuzamosság segítségével felosztja a modellt mindkét csomópont között. A betöltés után a következtetés úgy zajlik, mintha egyetlen gyorsítón futna.

### 1. lépés: Ray fő csomópont indítása (1. gép)

Az 1. gépen indítsa el a Ray fő csomópontot a klaszter inicializálásához:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **`<MACHINE_1_IP>` megkeresése**: Az 1. gépen futtassa a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megkereséséhez.
### 2. lépés: Csatlakozás a fürthöz (2. gép)

A 2. gépen csatlakozzon a fejcsomóponthoz a fürt létrehozásához:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **A `<MACHINE_2_IP>` megkeresése**: A 2. gépen futtassa a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megkereséséhez.

### 3. lépés: A modell kiszolgálása (1. gép)

Az 1. gépen indítsa el a vLLM szervert. Ez automatikusan letölti a modellt, és megkezdi a kiszolgálását mindkét csomóponton keresztül:

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

#### Paraméterek referenciája

| Jelző | Cél |
|------|---------|
| `--port` | A HTTP API kiszolgálásához használt port |
| `--host` | Az IP-cím, amelyhez a szerver kötődik (`0.0.0.0` az összes interfészhez) |
| `--max-model-len` | Maximális kontextushossz tokenekben |
| `--gpu-memory-utilization` | A lefoglalandó GPU-memória aránya (0,0–1,0) |
| `--dtype` | A modell súlyainak adattípusa |
| `--tensor-parallel-size` | A modell particionálásához használt GPU-k száma (állítsa be a fürtben lévő GPU-k teljes számára) |
| `--distributed-executor-backend` | A többcsomópontos végrehajtás háttérrendszere (`ray` fürtös telepítésekhez) |
| `--enforce-eager` | Letiltja a CUDA gráf fordítást a kompatibilitás érdekében |
| `--language-model-only` | Kihagyja a kiegészítő modellkomponensek betöltését (pl. látáskódoló) |
| `--reasoning-parser` | Engedélyezi a strukturált érvelési kimenet elemzését a modellhez |

A teljes paraméterhasználatért lásd a [vLLM dokumentációt](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## A modell elérése

A vLLM egy OpenAI-kompatibilis API-t biztosít, így bármilyen kompatibilis klienst vagy felületet csatlakoztathat a fürthöz. Az egyik népszerű megoldás az [Open WebUI](https://github.com/open-webui/open-webui), amely böngészőalapú csevegőfelületet biztosít.

Az Open WebUI csatlakoztatásához a vLLM végponthoz:

1. Nyissa meg a **Settings** > **Admin Panel** > **Connections** menüpontot
2. Kattintson a **+** jelre a **Manage OpenAI API Connections** résznél
3. Állítsa a **Connection Type** értékét **External**-re
4. Állítsa az **URL** mezőt erre: `http://<MACHINE_1_IP>:7000/v1`
5. Az **Auth** alatt válassza a **None** lehetőséget a legördülő listából
6. Hagyja üresen a **Model IDs** mezőt, hogy automatikusan felfedezze az összes modellt a végpontról

> **A `<MACHINE_1_IP>` megkeresése**: Az 1. gépen futtassa a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megkereséséhez. Ha magáról az 1. gépről éri el az Open WebUI-t, használhatja a `http://localhost:7000/v1` címet is.

![Open WebUI csatlakozási beállítások a vLLM végponthoz](assets/openwebui-connection.png)

A csatlakozás után válassza ki a modellt a legördülő listából az Open WebUI-ban, és kezdjen el csevegni. A modell most már mindkét Ryzen AI Halo csomóponton fut:

![Csevegés a Qwen3.5-397B modellel az Open WebUI-ban](assets/openwebui-chat.png)

## Következő lépések

- **Más modellek felfedezése**: Fedezzen fel új modelleket a [Hugging Face](https://huggingface.co/models?&sort=trending) oldalon, amelyek beleférnek a fürt összesített GPU-memóriájába
- **Bővítés négy csomópontra**: Adjon hozzá még két Ryzen AI Halo rendszert további Ray munkavégzőként, hogy még több GPU között particionálja a modelleket. Ehhez legalább négy portos Ethernet switch szükséges, egy-egy port minden csomóponthoz. Kövesse a [2. lépés: Csatlakozás a fürthöz](#step-2-join-the-cluster-machine-2) útmutatót minden további munkavégzőn, és növelje a `--tensor-parallel-size` értékét ennek megfelelően
- **Más párhuzamosítási stratégiák kipróbálása**: A vLLM támogatja az [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) módot mixture-of-experts modellekhez, valamint a [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) módot nagyobb átviteli sebességhez. Kísérletezzen az `--enable-expert-parallel` és `--data-parallel-size` beállításokkal, hogy megtalálja a munkaterheléséhez legjobb konfigurációt