<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Gépi fordítás.** Ez az oldal automatikusan lett lefordítva angol nyelvről, és emberi ellenőrzésen nem esett át. Hibákat tartalmazhat, és bizonyos utasítások, parancsok, letöltések, termékelérhetőség vagy egyéb tartalmak nyelvenként vagy régiónként eltérhetnek. Bármilyen eltérés vagy ellentmondás esetén a playbook eredeti angol nyelvű változata az irányadó.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Ryzen™ AI Halo Klaszterezés Két Rendszer Között RCCL Használatával

## Áttekintés

A Ryzen™ AI Halo rendszered már most is képes nagy nyelvi modellek helyi futtatására. A klaszterezés ezt viszi tovább azáltal, hogy több rendszer GPU memóriáját kombinálja egy helyi hálózaton keresztül, így még nagyobb modellekhez férhetsz hozzá erősebb következtetési képességgel, jobb kódgenerálással és mélyebb többnyelvű megértéssel, mindezt teljes egészében a saját hardvereden.

Ez a útmutató megtanítja, hogyan klaszterezz két Ryzen AI Halo rendszert RCCL (ROCm Communication Collectives Library) segítségével vLLM-mel, és hogyan futtasd a Qwen3.5-397B modellt, egy 397 milliárd paraméteres modellt, mindkét gépen ROCm gyorsítással.

## Amit Meg Fogsz Tanulni

- Hogyan bővítsd ki a VRAM allokációt Ryzen AI Halo rendszereken
- vLLM indítása ROCm támogatással
- RCCL konfigurálása többcsomópontos tenzor-párhuzamos következtetéshez két Ryzen AI Halo rendszer között
- Egy 397 milliárd paraméteres modell futtatása két hálózatba kötött Ryzen AI Halo rendszeren

## Előfeltételek

### Hardver

Ehhez az útmutatóhoz két Ryzen AI Halo egység és egy Ethernet switch szükséges, csillag topológiában összekötve, ahol mindegyik egység közvetlenül a switchhez van csatlakoztatva.

| Komponens | Mennyiség | Leírás |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Számítási csomópontok, amelyek a klasztert alkotják |
| 10Gbps Ethernet switch | 1 | Központi switch a több csomópontos Ryzen AI Halo kommunikáció lehetővé tételéhez (legalább 2 port) |
| Ethernet kábel | 2 | Összeköti mindegyik Halo egységet a switchcsel (Cat 7 vagy magasabb ajánlott) |

> **Megjegyzés**: Két Ethernet switch port szükséges a két Ryzen AI Halo egység csatlakoztatásához. Egy harmadik port szükséges, ha egy különálló kliens gépről éred el a modellt, nem pedig az egyik Halo egységről.

### Szoftver
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fizikai Hardver Beállítás

> **Megjegyzés**: Ezt a lépést hajtsd végre mind az 1. Gépen, mind a 2. Gépen.

Csatlakoztasd mindegyik Ryzen AI Halo egységet az Ethernet switchhez Cat 7 (vagy magasabb) kábellel. Ez hozza létre a 10Gbps kapcsolatot, amely a csomópontok közötti nagy sebességű kommunikációhoz szükséges.

### 1. Hálózati Interfészek Meghatározása

Mindegyik gépen keresd meg a hálózati interfész nevét, és jegyezd fel (a további utasításokban `IFNAME` néven fogunk rá hivatkozni). Futtasd:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Ez közvetlenül kiírja az interfész nevét, például:

```bash
enp191s0
```

### 2. Hálózati Kapcsolat Sebességének Ellenőrzése

Ellenőrizd, hogy a kapcsolat aktív és teljes sebességgel fut, az interfész sebességének ellenőrzésével:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Megjegyzés**: Cseréld le a `<IFNAME>`-et a [1. Hálózati Interfészek Meghatározása](#1-determine-network-interfaces) résznél kapott interfész névvel

`10000Mb/s` sebességet kell látnod:

```bash
	Speed: 10000Mb/s
```

> **Megjegyzés**: Ha a sebesség alacsonyabb, mint `10000Mb/s`, vagy a kapcsolat nem jön létre, ellenőrizd a kábel csatlakozását, és győződj meg róla, hogy a switch port 10Gbps-re van állítva. Néhány switch esetén szükséges lehet az automatikus egyeztetés (auto-negotiation) letiltása és a kapcsolat sebességének manuális beállítása; nézd meg a switch dokumentációját.

## VRAM Allokáció Kibővítése

> **Megjegyzés**: Ezt a lépést hajtsd végre mind az 1. Gépen, mind a 2. Gépen.

### Memória Konfiguráció Nagy Modellek Futtatásához

Linux alatt a ROCm egy megosztott rendszermemória-poolt használ, és ez a pool alapértelmezetten a rendszermemória felére van beállítva.

Ez a mennyiség növelhető a kernel Translation Table Manager (TTM) oldal beállításának megváltoztatásával, az alábbi utasítások szerint. Az AMD azt javasolja, hogy a minimális dedikált VRAM-ot a BIOS-ban állítsd be (0.5 GB).

* Telepítsd a pipx segédprogramot, és add hozzá a pipx által telepített wheel-ek elérési útját a rendszer keresési útvonalához.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Telepítsd az amd-debug-tools wheel-t a PyPI-ból.
  ```bash
  pipx install amd-debug-tools
  ```

* Futtasd az amd-ttm eszközt a megosztott memória jelenlegi beállításainak lekérdezéséhez.
  ```bash
  amd-ttm
  ```

* Konfiguráld át a megosztott memória beállításait **120 GB**-ra:
  ```bash
  amd-ttm --set 120
  ```

* Indítsd újra a rendszert, hogy a változtatások érvénybe lépjenek.

## vLLM Konténer Inicializálás

> **Megjegyzés**: Ezt a lépést hajtsd végre mind az 1. Gépen, mind a 2. Gépen.

A Ryzen AI Halo rendszered a vLLM-et egy előre elkészített konténer image-be csomagolva tartalmazza, amelyet a Podman, egy ingyenes és nyílt forráskódú konténereszköz segítségével futtathatsz.

### 1. Modell Letöltési Könyvtár Létrehozása

Amikor ebben az útmutatóban a Qwen3.5-397B modellt szolgáltatod, a vLLM automatikusan letölti a modell súlyokat a rendszeredre. Annak érdekében, hogy ezek a súlyok elérhetők legyenek a konténeren belülről, először hozz létre egy models könyvtárat, amelyet a konténer csatolni tud:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. A vLLM Konténer Indítása

Az alábbi parancs elindítja a konténert, és egy interaktív shell-be helyez. Csatolja az imént létrehozott models könyvtárat, és átadja az `IFNAME`-edet az `NCCL_SOCKET_IFNAME` és `GLOO_SOCKET_IFNAME` számára, megmondva az RCCL-nek (a könyvtárnak, amelyet a vLLM használ a GPU-k koordinálásához a klaszteren belül), hogy melyik interfészt használja.

Indítsd el a konténert ezzel:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Megjegyzés**: Cseréld le a `<IFNAME>`-et a [1. Hálózati Interfészek Meghatározása](#1-determine-network-interfaces) résznél kapott interfész névvel

## A Modell Futtatása a Klaszteren

A vLLM a Ray-t használja a klaszter orkesztrálásához, és az RCCL-t a csomópontok közötti GPU-GPU kommunikáció kezeléséhez. Az egyik gép **fej csomópontként** (head node) működik (1. Gép), koordinálva a következtetést. A másik **worker csomópontként** csatlakozik (2. Gép), hozzájárulva a saját GPU memóriájával és számítási kapacitásával.

> **Megjegyzés**: A Ray egy opcionális függőség a vLLM számára, és csak az előre konfigurált Podman konténeren belülről érhető el.

Indításkor a vLLM tenzor-párhuzamosítás segítségével megosztja a modellt mindkét csomópont között. Betöltés után a következtetés úgy zajlik, mintha egyetlen gyorsítón futna.

#### Ray OOM Hibák Megelőzése

Alapértelmezés szerint a Ray figyeli a host memóriát mindegyik csomóponton, és leállítja a legnagyobb folyamatot, amikor a memóriahasználat átlépi a 95%-ot. A Ryzen™ AI Halo rendszereden a GPU és a host egy közös memóriapoolt osztanak meg, így egy modell betöltése kiválthat egy `ray.exceptions.OutOfMemoryError` hibát, és leállíthatja a worker folyamatot.

Ennek megelőzése érdekében exportáljuk a `RAY_memory_monitor_refresh_ms=0` beállítást mindegyik gépen, mielőtt elindítanánk és csatlakoznánk a klaszterhez.
### 1. lépés: A Ray fejcsomópont elindítása (1. gép)

Az 1. gépen indítsa el a Ray fejcsomópontot a fürt inicializálásához:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **A `<MACHINE_1_IP>` megkeresése**: Az 1. gépen futtassa a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megkereséséhez.

### 2. lépés: Csatlakozás a fürthöz (2. gép)

A 2. gépen csatlakozzon a fejcsomóponthoz a fürt létrehozásához:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **A `<MACHINE_2_IP>` megkeresése**: A 2. gépen futtassa a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megkereséséhez.

### 3. lépés: A modell kiszolgálása (1. gép)

Az 1. gépen indítsa el a vLLM szervert. Ez automatikusan letölti a modellt, és megkezdi annak kiszolgálását mindkét csomóponton keresztül:

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

#### Paraméterreferencia

| Jelző | Cél |
|------|---------|
| `--port` | A HTTP API kiszolgálásához használt port |
| `--host` | Az az IP-cím, amelyhez a szerver kötődik (`0.0.0.0` minden interfészhez) |
| `--max-model-len` | Maximális kontextushossz tokenekben |
| `--gpu-memory-utilization` | A lefoglalandó GPU-memória aránya (0,0–1,0) |
| `--dtype` | A modellsúlyok adattípusa |
| `--tensor-parallel-size` | Azon GPU-k száma, amelyek között a modell felosztásra kerül (állítsa be a fürtben lévő GPU-k teljes számára) |
| `--distributed-executor-backend` | A több csomópontos végrehajtás háttérrendszere (`ray` fürtös üzembe helyezésekhez) |
| `--enforce-eager` | Letiltja a CUDA gráf fordítását a kompatibilitás érdekében |
| `--language-model-only` | Kihagyja a kiegészítő modellösszetevők betöltését (pl. vizuális kódoló) |
| `--reasoning-parser` | Engedélyezi a strukturált érvelési kimenet elemzését a modell számára |

A paraméterek teljes körű használatához tekintse meg a [vLLM dokumentációját](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## A modell elérése

A vLLM egy OpenAI-kompatibilis API-t biztosít, így bármely kompatibilis klienst vagy felületet csatlakoztathat a fürtjéhez. Az egyik népszerű megoldás az [Open WebUI](https://github.com/open-webui/open-webui), amely böngészőalapú csevegőfelületet biztosít.

Az Open WebUI csatlakoztatása a vLLM végponthoz:

1. Nyissa meg a **Settings** > **Admin Panel** > **Connections** menüpontot
2. Kattintson a **+** jelre a **Manage OpenAI API Connections** résznél
3. Állítsa a **Connection Type** értékét **External**-re
4. Állítsa be az **URL**-t: `http://<MACHINE_1_IP>:7000/v1`
5. Az **Auth** alatt válassza a **None** opciót a legördülő listából
6. Hagyja üresen a **Model IDs** mezőt, hogy az összes modell automatikusan felfedezésre kerüljön a végpontról

> **A `<MACHINE_1_IP>` megkeresése**: Az 1. gépen futtassa a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megkereséséhez. Ha magáról az 1. gépről éri el az Open WebUI-t, használhatja a `http://localhost:7000/v1` címet is.

![Open WebUI kapcsolati beállítások a vLLM végponthoz](assets/openwebui-connection.png)

A csatlakozás után válassza ki a modellt az Open WebUI modell-legördülő menüjéből, és kezdjen el csevegni. A modell mostantól mindkét Ryzen AI Halo csomóponton fut:

![Csevegés a Qwen3.5-397B modellel az Open WebUI-ban](assets/openwebui-chat.png)

## Következő lépések

- **Fedezzen fel más modelleket**: Keressen új modelleket a [Hugging Face](https://huggingface.co/models?&sort=trending) oldalon, amelyek beleférnek a fürt kombinált GPU-memóriájába
- **Bővítés négy csomópontra**: Adjon hozzá két további Ryzen AI Halo rendszert Ray-munkavállalóként, hogy a modelleket még több GPU között ossza fel. Ehhez legalább négy portos Ethernet-kapcsolóra van szükség, egy-egy portra minden csomóponthoz. Kövesse a [2. lépést: Csatlakozás a fürthöz](#step-2-join-the-cluster-machine-2) minden további munkavállaló gépen, és ennek megfelelően növelje a `--tensor-parallel-size` értékét
- **Próbáljon ki más párhuzamosítási stratégiákat**: A vLLM támogatja a [szakértői párhuzamosítást](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) mixture-of-experts modellekhez, valamint az [adatpárhuzamosítást](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) a nagyobb átviteli sebesség érdekében. Kísérletezzen a `--enable-expert-parallel` és `--data-parallel-size` paraméterekkel, hogy megtalálja a munkaterheléséhez legjobban illő konfigurációt