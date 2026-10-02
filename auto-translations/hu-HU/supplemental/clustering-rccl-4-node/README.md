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

# Négy Ryzen™ AI Halo klaszterezése RCCL-lel

## Áttekintés

A Ryzen™ AI Halo máris képes nagy nyelvi modellek helyi futtatására. A klaszterezés ezt tovább fejleszti azáltal, hogy több rendszer GPU-memóriáját kombinálja egy helyi hálózaton keresztül, így még nagyobb modellekhez férhet hozzá, erősebb következtetési képességekkel, jobb kódgenerálással és mélyebb többnyelvű megértéssel – mindezt teljes egészében a saját hardverén.

Ez az útmutató megtanítja, hogyan klaszterezzen négy Ryzen AI Halo rendszert RCCL (ROCm Communication Collectives Library) segítségével vLLM-mel, és hogyan futtassa a Qwen3.5-397B modellt, amely 397 milliárd paraméteres, mind a négy gépen ROCm gyorsítással.

## Amit meg fog tanulni

- Hogyan bővítse ki a VRAM-allokációt Ryzen AI Halo rendszereken
- A vLLM indítása ROCm támogatással
- Az RCCL konfigurálása többcsomópontos tenzor-párhuzamos következtetéshez négy Ryzen AI Halo rendszer között
- Egy 397 milliárd paraméteres modell futtatása négy hálózatba kötött Ryzen AI Halo rendszeren

## Előfeltételek

### Hardver

Ehhez az útmutatóhoz négy Ryzen AI Halo egységre és egy Ethernet switchre van szükség, csillag topológiában összekötve, ahol minden egység közvetlenül a switchhez csatlakozik.

| Komponens | Mennyiség | Leírás |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | A klasztert alkotó számítási csomópontok |
| 10 Gbps-os Ethernet switch | 1 | Központi switch a Ryzen AI Halo egységek közötti, több csomópontos kommunikáció lehetővé tételéhez (legalább 4 port) |
| Ethernet kábel | 4 | Minden Halo egységet a switchhez csatlakoztat (Cat 7 vagy magasabb ajánlott) |

> **Megjegyzés**: Négy Ethernet switch portra van szükség a négy Ryzen AI Halo egység csatlakoztatásához. Egy ötödik portra van szükség, ha egy különálló klienseszközről éri el a modellt, nem pedig az egyik Halo egységről.

### Szoftver
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fizikai hardverbeállítás

> **Megjegyzés**: Ezt a lépést mind a négy gépen végezze el (1-es géptől a 4-es gépig).

Csatlakoztassa az egyes Ryzen AI Halo egységeket az Ethernet switchhez egy Cat 7 (vagy magasabb) kábel segítségével. Ez hozza létre a csomópontok közötti nagy sebességű kommunikációhoz használt 10 Gbps-os kapcsolatot.

### 1. A hálózati interfészek meghatározása

Minden gépen keresse meg a hálózati interfész nevét, és jegyezze fel (a további útmutatásokban `IFNAME` néven fogunk rá hivatkozni). Futtassa a következőt:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Ez közvetlenül kiírja az interfész nevét, például:

```bash
enp191s0
```

### 2. A hálózati kapcsolat sebességének ellenőrzése

Győződjön meg róla, hogy a kapcsolat aktív és teljes sebességgel működik, az interfész sebességének ellenőrzésével:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Megjegyzés**: Cserélje ki a `<IFNAME>` szót a [1. A hálózati interfészek meghatározása](#1-determine-network-interfaces) szakaszból származó interfésznévre.

A sebességnek `10000Mb/s` értékűnek kell lennie:

```bash
	Speed: 10000Mb/s
```

> **Megjegyzés**: Ha a sebesség alacsonyabb, mint `10000Mb/s`, vagy a kapcsolat nem jön létre, ellenőrizze a kábelcsatlakozást, és győződjön meg róla, hogy a switch portja 10 Gbps-ra van állítva. Egyes switcheknél az automatikus egyeztetést le kell tiltani, és a kapcsolat sebességét kézileg kell beállítani; nézze meg a switch dokumentációját.

## A VRAM-allokáció bővítése

> **Megjegyzés**: Ezt a lépést mind a négy gépen végezze el (1-es géptől a 4-es gépig).

### Memóriakonfiguráció nagy modellek futtatásához

Linuxon a ROCm egy megosztott rendszermemória-készletet használ, amely alapértelmezés szerint a rendszermemória felére van beállítva.

Ez a mennyiség növelhető a kernel Translation Table Manager (TTM) lapbeállításának módosításával, az alábbi utasítások szerint. Az AMD azt javasolja, hogy a BIOS-ban állítsa be a minimális dedikált VRAM-ot (0,5 GB).

* Telepítse a pipx segédprogramot, és adja hozzá a pipx által telepített wheel-ek elérési útját a rendszer keresési útvonalához.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Telepítse az amd-debug-tools wheel-t a PyPI-ről.
  ```bash
  pipx install amd-debug-tools
  ```

* Futtassa az amd-ttm eszközt a megosztott memória aktuális beállításainak lekérdezéséhez.
  ```bash
  amd-ttm
  ```

* Állítsa be a megosztott memória beállításait **120 GB**-ra:
  ```bash
  amd-ttm --set 120
  ```

* Indítsa újra a rendszert a változtatások érvénybe léptetéséhez.

## A vLLM konténer inicializálása

> **Megjegyzés**: Ezt a lépést mind a négy gépen végezze el (1-es géptől a 4-es gépig).

A Ryzen AI Halo egy előre elkészített konténerképben csomagolt vLLM-mel érkezik, amelyet a Podman, egy ingyenes és nyílt forráskódú konténereszköz segítségével futtathat.

### 1. Hozza létre a modellletöltési könyvtárat

Amikor ebben az útmutatóban kiszolgálja a Qwen3.5-397B modellt, a vLLM automatikusan letölti a modell súlyait a rendszerére. Annak biztosítására, hogy ezek a súlyok elérhetők legyenek a konténeren belülről, először hozzon létre egy models könyvtárat, amelyet a konténer csatolni tud:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Indítsa el a vLLM konténert

Az alábbi parancs elindítja a konténert, és egy interaktív shellbe helyezi. Csatolja az imént létrehozott models könyvtárat, és átadja az `IFNAME` értéket a `NCCL_SOCKET_IFNAME` és `GLOO_SOCKET_IFNAME` beállításoknak, megmondva az RCCL-nek (a könyvtárnak, amelyet a vLLM a GPU-k klaszteren keresztüli koordinálására használ), hogy melyik interfészt használja.

Indítsa el a konténert az alábbival:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Megjegyzés**: Cserélje ki a `<IFNAME>` szót a [1. A hálózati interfészek meghatározása](#1-determine-network-interfaces) szakaszból származó interfésznévre.

## A modell futtatása a klaszteren

A vLLM a Ray-t használja a klaszter koordinálásához, és az RCCL-t a csomópontok közötti GPU-GPU kommunikáció kezelésére. Az egyik gép fő csomópontként (head node) funkcionál (1-es gép), amely koordinálja a következtetést. A másik három munkacsomópontként (worker node) csatlakozik (2-es, 3-as és 4-es gép), hozzájárulva a GPU-memóriájukkal és számítási kapacitásukkal.

> **Megjegyzés**: A Ray egy opcionális függőség a vLLM számára, és csak az előre konfigurált Podman konténeren belülről érhető el.

Indításkor a vLLM tenzor-párhuzamosság segítségével osztja fel a modellt mind a négy csomópont között. Betöltés után a következtetés úgy zajlik, mintha egyetlen gyorsítón futna.

#### A Ray OOM-hibáinak megelőzése

Alapértelmezés szerint a Ray figyeli a gazdagép memóriáját minden csomóponton, és leállítja a legnagyobb folyamatot, amikor a memóriahasználat átlépi a 95%-ot. A Ryzen™ AI Halo-n a GPU és a gazdagép egyetlen közös memóriakészletet oszt meg, így egy modell betöltése kiválthat egy `ray.exceptions.OutOfMemoryError` hibát, és leállíthatja a munkafolyamatot.

Ennek megelőzésére exportáljuk a `RAY_memory_monitor_refresh_ms=0` beállítást minden gépen, mielőtt elindítanánk és csatlakoznánk a klaszterhez.
### 1. lépés: A Ray fővezérlő csomópont indítása (1. gép)

Az 1. gépen indítsa el a Ray fővezérlő csomópontot a fürt inicializálásához:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **A `<MACHINE_1_IP>` megkeresése**: Az 1. gépen futtassa a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megkereséséhez.

### 2. lépés: Csatlakozás a fürthöz (2., 3. és 4. gép)

A 2., 3. és 4. gépen csatlakozzon a fővezérlő csomóponthoz a fürt létrehozásához:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_N_IP> --num-gpus=1
```

> **A `<MACHINE_N_IP>` megkeresése**: Minden egyes worker gépen futtassa a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megkereséséhez.

### 3. lépés: A modell kiszolgálása (1. gép)

Az 1. gépen indítsa el a vLLM szervert. Ez automatikusan letölti a modellt, és megkezdi annak kiszolgálását mind a négy csomóponton:

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

#### Paraméterek áttekintése

| Jelző | Cél |
|------|-------|
| `--port` | A HTTP API kiszolgálásához használt port |
| `--host` | Az IP-cím, amelyhez a szerver kötődik (`0.0.0.0` minden interfész esetén) |
| `--max-model-len` | A maximális kontextushossz tokenben |
| `--gpu-memory-utilization` | A lefoglalandó GPU-memória aránya (0,0–1,0) |
| `--dtype` | A modell súlyainak adattípusa |
| `--tensor-parallel-size` | A modell particionálásához használt GPU-k száma (állítsa be a fürtben lévő GPU-k teljes számára) |
| `--distributed-executor-backend` | A többcsomópontos végrehajtás háttérrendszere (`ray` a fürtös üzembe helyezésekhez) |
| `--enforce-eager` | Letiltja a CUDA grafikonok fordítását a kompatibilitás érdekében |
| `--language-model-only` | Kihagyja a kiegészítő modellkomponensek (pl. vizuális kódoló) betöltését |
| `--reasoning-parser` | Engedélyezi a strukturált gondolkodási kimenet elemzését a modellhez |

A paraméterek teljes körű használatáért tekintse meg a [vLLM dokumentációját](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## A modell elérése

A vLLM egy OpenAI-kompatibilis API-t biztosít, így bármilyen kompatibilis klienst vagy felületet csatlakoztathat a fürtjéhez. Az egyik népszerű lehetőség az [Open WebUI](https://github.com/open-webui/open-webui), amely böngészőalapú csevegőfelületet biztosít.

Az Open WebUI csatlakoztatása a vLLM végponthoz:

1. Nyissa meg a **Settings** > **Admin Panel** > **Connections** menüpontot
2. Kattintson a **+** gombra a **Manage OpenAI API Connections** résznél
3. Állítsa a **Connection Type** értékét **External**-re
4. Állítsa az **URL** mezőt `http://<MACHINE_1_IP>:7000/v1` értékre
5. Az **Auth** részben válassza a **None** opciót a legördülő listából
6. Hagyja üresen a **Model IDs** mezőt, hogy a rendszer automatikusan felismerje az összes modellt a végpontról

> **A `<MACHINE_1_IP>` megkeresése**: Az 1. gépen futtassa a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megkereséséhez. Ha magáról az 1. gépről éri el az Open WebUI-t, használhatja a `http://localhost:7000/v1` címet is.

![Open WebUI kapcsolódási beállítások a vLLM végponthoz](assets/openwebui-connection.png)

A kapcsolódás után válassza ki a modellt az Open WebUI modell-legördülő listájából, és kezdjen el csevegni. A modell most mind a négy Ryzen AI Halo csomóponton fut:

![Csevegés a Qwen3.5-397B modellel az Open WebUI-ban](assets/openwebui-chat.png)

## Következő lépések

- **Más modellek felfedezése**: Fedezzen fel új modelleket a [Hugging Face](https://huggingface.co/models?&sort=trending) oldalán, amelyek beleférnek a fürt összesített GPU-memóriájába
- **Bővítés négy csomóponton túl**: Adjon hozzá további Ryzen AI Halo rendszereket további Ray workerként, hogy a modelleket még több GPU között particionálja. Kövesse a [2. lépés: Csatlakozás a fürthöz](#step-2-join-the-cluster-machines-2-3-and-4) útmutatót minden további worker esetében, és ennek megfelelően növelje a `--tensor-parallel-size` értékét
- **Más párhuzamosítási stratégiák kipróbálása**: A vLLM támogatja az [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) megoldást a mixture-of-experts modellekhez, valamint a [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) megoldást a nagyobb áteresztőképességhez. Kísérletezzen a `--enable-expert-parallel` és `--data-parallel-size` beállításokkal, hogy megtalálja a munkaterheléséhez legjobban illeszkedő konfigurációt