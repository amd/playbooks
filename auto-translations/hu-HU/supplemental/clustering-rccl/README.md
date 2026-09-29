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

# Két Ryzen™ AI Halo klaszterezése RCCL-lel

## Áttekintés

A Ryzen™ AI Halo rendszered már önmagában is képes nagy nyelvi modellek helyi futtatására. A klaszterezés ezt továbbfejleszti azáltal, hogy több rendszer GPU memóriáját egyesíti egy helyi hálózaton keresztül, így még nagyobb modellekhez férhetsz hozzá, erősebb következtetési képességekkel, jobb kódgenerálással és mélyebb többnyelvű megértéssel, mindezt teljesen a saját hardvereden.

Ez az útmutató megtanítja, hogyan lehet két Ryzen AI Halo rendszert klaszterbe rendezni az RCCL (ROCm Communication Collectives Library) segítségével vLLM-mel, és hogyan futtathatod a Qwen3.5-397B modellt, egy 397 milliárd paraméteres modellt, mindkét gépen keresztül ROCm gyorsítással.

## Amit meg fogsz tanulni

- Hogyan bővítsd a VRAM allokációt Ryzen AI Halo rendszereken
- A vLLM elindítása ROCm támogatással
- Az RCCL konfigurálása többcsomópontos tensor-párhuzamos következtetéshez két Ryzen AI Halo rendszer között
- Egy 397 milliárd paraméteres modell futtatása két hálózatba kötött Ryzen AI Halo rendszeren

## Előfeltételek

### Hardver

Ez az útmutató két Ryzen AI Halo egységet és egy Ethernet switch-et igényel, csillag topológiába kötve, ahol mindegyik egység közvetlenül a switch-hez van csatlakoztatva.

| Komponens | Mennyiség | Leírás |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | A klasztert alkotó számítási csomópontok |
| 10 Gbps-os Ethernet switch | 1 | Központi switch a Ryzen AI Halo többcsomópontos kommunikációjának lehetővé tételéhez (legalább 2 port) |
| Ethernet kábel | 2 | Az egyes Halo egységeket köti a switch-hez (Cat 7 vagy magasabb ajánlott) |

> **Megjegyzés**: A két Ryzen AI Halo egység összekötéséhez két Ethernet switch port szükséges. Egy harmadik port akkor szükséges, ha a modellt egy különálló kliens géprő éred el, nem pedig az egyik Halo egységről.

### Szoftver
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fizikai hardver beállítása

> **Megjegyzés**: Ezt a lépést mindkét gépen, az 1. és a 2. gépen is végezd el.

Csatlakoztasd mindkét Ryzen AI Halo egységet az Ethernet switch-hez egy Cat 7 (vagy magasabb) kábellel. Ez létrehozza a csomópontok közötti nagy sebességű kommunikációhoz használt 10 Gbps-os kapcsolatot.

### 1. A hálózati interfészek meghatározása

Mindegyik gépen keresd meg a hálózati interfész nevét, és jegyezd fel (az útmutató további részében erre `IFNAME`-ként hivatkozunk). Futtasd:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Ez közvetlenül kiírja az interfész nevét, például:

```bash
enp191s0
```

### 2. A hálózati kapcsolat sebességének ellenőrzése

Ellenőrizd, hogy a kapcsolat aktív, és teljes sebességen fut, az interfész sebességének megvizsgálásával:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Megjegyzés**: Cseréld ki a `<IFNAME>`-et a [1. A hálózati interfészek meghatározása](#1-determine-network-interfaces) lépésből származó interfész névre.

A sebességnek `10000Mb/s`-nak kell lennie:

```bash
	Speed: 10000Mb/s
```

> **Megjegyzés**: Ha a sebesség alacsonyabb, mint `10000Mb/s`, vagy a kapcsolat nem jön létre, ellenőrizd a kábelcsatlakozást, és győződj meg róla, hogy a switch port 10 Gbps-ra van állítva. Egyes switch-eknél le kell tiltani az automatikus egyeztetést, és manuálisan kell beállítani a kapcsolat sebességét; ehhez tekintsd meg a switch dokumentációját.

## A VRAM allokáció bővítése

> **Megjegyzés**: Ezt a lépést mindkét gépen, az 1. és a 2. gépen is végezd el.

### Memória konfiguráció nagy modellek futtatásához

Linux alatt a ROCm egy megosztott rendszermemória-készletet használ, amely alapértelmezés szerint a rendszermemória felére van konfigurálva.

Ez a mennyiség növelhető a kernel Translation Table Manager (TTM) lapbeállításának módosításával, az alábbi utasítások alapján. Az AMD azt javasolja, hogy a BIOS-ban állítsd be a minimális dedikált VRAM-ot (0,5 GB).

* Telepítsd a pipx segédprogramot, és add hozzá a pipx által telepített wheel-ek elérési útját a rendszer keresési útvonalához.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Telepítsd az amd-debug-tools wheel csomagot a PyPI-ból.
  ```bash
  pipx install amd-debug-tools
  ```

* Futtasd az amd-ttm eszközt a jelenlegi megosztott memória beállítások lekérdezéséhez.
  ```bash
  amd-ttm
  ```

* Állítsd át a megosztott memória beállításait **120 GB**-ra:
  ```bash
  amd-ttm --set 120
  ```

* Indítsd újra a rendszert, hogy a változtatások érvénybe lépjenek.

## vLLM konténer inicializálása

> **Megjegyzés**: Ezt a lépést mindkét gépen, az 1. és a 2. gépen is végezd el.

A Ryzen AI Halo egy előre elkészített konténer image-be csomagolt vLLM-mel érkezik, amelyet a Podman segítségével futtathatsz, ami egy ingyenes és nyílt forráskódú konténereszköz.

### 1. A modellletöltési könyvtár létrehozása

Amikor ebben az útmutatóban kiszolgálod a Qwen3.5-397B modellt, a vLLM automatikusan letölti a modell súlyait a rendszeredre. Ahhoz, hogy ezek a súlyok elérhetők legyenek a konténeren belülről, hozz létre először egy models könyvtárat, amelyet a konténer csatolni tud:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. A vLLM konténer elindítása

Az alábbi parancs elindítja a konténert, és egy interaktív shell-be helyez téged. Csatolja az imént létrehozott models könyvtárat, és átadja a `IFNAME`-et a `NCCL_SOCKET_IFNAME` és a `GLOO_SOCKET_IFNAME` számára, jelezve az RCCL-nek (a könyvtárnak, amelyet a vLLM használ a GPU-k koordinálásához a klaszteren belül), hogy melyik interfészt használja.

Indítsd el a konténert a következővel:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Megjegyzés**: Cseréld ki a `<IFNAME>`-et a [1. A hálózati interfészek meghatározása](#1-determine-network-interfaces) lépésből származó interfész névre.

## A modell futtatása a klaszteren

A vLLM a Ray-t használja a klaszter irányítására, és az RCCL-t a csomópontok közötti GPU-GPU kommunikáció kezelésére. Az egyik gép **head node**-ként (fő csomópontként) működik (1. gép), és irányítja a következtetést. A másik **worker node**-ként (dolgozó csomópontként) csatlakozik (2. gép), hozzájárulva a saját GPU memóriájával és számítási kapacitásával.

> **Megjegyzés**: A Ray a vLLM egy opcionális függősége, és csak az előre konfigurált Podman konténeren belülről érhető el.

Indításkor a vLLM tensor párhuzamossággal osztja fel a modellt mindkét csomópont között. Betöltés után a következtetés úgy zajlik, mintha egyetlen gyorsítón futna.

#### Ray OOM hibák megelőzése

Alapértelmezés szerint a Ray minden csomóponton figyeli a gazdagép memóriahasználatát, és leállítja a legnagyobb folyamatot, amikor a memóriahasználat átlépi a 95%-ot. A Ryzen™ AI Halo rendszeren a GPU és a gazdagép egy közös memóriakészletet oszt meg, így egy modell betöltése kiválthat egy `ray.exceptions.OutOfMemoryError` hibát, és leállíthatja a worker folyamatot.

Ennek megelőzésére exportáljuk a `RAY_memory_monitor_refresh_ms=0` beállítást mindegyik gépen, mielőtt elindítanánk és csatlakoznánk a klaszterhez.
### 1. lépés: Ray fejcsomópont indítása (1-es gép)

Az 1-es gépen indítsa el a Ray fejcsomópontot a fürt inicializálásához:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **A `<MACHINE_1_IP>` megkeresése**: Az 1-es gépen futtassa a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megkereséséhez.

### 2. lépés: Csatlakozás a fürthöz (2-es gép)

A 2-es gépen csatlakozzon a fejcsomóponthoz a fürt létrehozásához:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **A `<MACHINE_2_IP>` megkeresése**: A 2-es gépen futtassa a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megkereséséhez.

### 3. lépés: A modell kiszolgálása (1-es gép)

Az 1-es gépen indítsa el a vLLM szervert. Ez automatikusan letölti a modellt, és megkezdi annak kiszolgálását mindkét csomóponton keresztül:

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

#### Paraméterek listája

| Jelző | Cél |
|------|---------|
| `--port` | A HTTP API kiszolgálásához használt port |
| `--host` | A szerverhez társítandó IP-cím (`0.0.0.0` az összes interfészhez) |
| `--max-model-len` | Maximális kontextushossz tokenekben |
| `--gpu-memory-utilization` | A lefoglalandó GPU-memória aránya (0,0–1,0) |
| `--dtype` | A modell súlyainak adattípusa |
| `--tensor-parallel-size` | Azon GPU-k száma, amelyek között a modell felosztásra kerül (állítsa a fürtben lévő GPU-k teljes számára) |
| `--distributed-executor-backend` | A több csomópontos végrehajtás háttérrendszere (fürtös üzemeltetéshez `ray`) |
| `--enforce-eager` | Letiltja a CUDA-gráf fordítását a kompatibilitás érdekében |
| `--language-model-only` | Kihagyja a kiegészítő modellösszetevők (pl. vizuális kódoló) betöltését |
| `--reasoning-parser` | Engedélyezi a strukturált gondolkodási kimenet elemzését a modellhez |

A paraméterek teljes leírásáért tekintse meg a [vLLM dokumentációját](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Hozzáférés a modellhez

A vLLM egy OpenAI-kompatibilis API-t tesz elérhetővé, így bármilyen kompatibilis klienst vagy felületet csatlakoztathat a fürtjéhez. Az egyik népszerű megoldás az [Open WebUI](https://github.com/open-webui/open-webui), amely böngészőalapú csevegőfelületet biztosít.

Az Open WebUI csatlakoztatásához a vLLM végponthoz:

1. Nyissa meg a **Settings** > **Admin Panel** > **Connections** menüpontot
2. Kattintson a **+** gombra a **Manage OpenAI API Connections** részen
3. Állítsa a **Connection Type** értékét **External** típusra
4. Állítsa az **URL** mezőt erre: `http://<MACHINE_1_IP>:7000/v1`
5. Az **Auth** részen válassza a **None** lehetőséget a legördülő menüből
6. Hagyja üresen a **Model IDs** mezőt az összes modell automatikus felismeréséhez a végpontról

> **A `<MACHINE_1_IP>` megkeresése**: Az 1-es gépen futtassa a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megkereséséhez. Ha az Open WebUI-t magáról az 1-es gépről éri el, használhatja a `http://localhost:7000/v1` címet is.

![Open WebUI kapcsolatbeállítások a vLLM végponthoz](assets/openwebui-connection.png)

A csatlakozás után válassza ki a modellt az Open WebUI modell legördülő menüjéből, és kezdje el a csevegést. A modell most már mindkét Ryzen AI Halo csomóponton fut:

![Csevegés a Qwen3.5-397B modellel az Open WebUI-ban](assets/openwebui-chat.png)

## Következő lépések

- **Fedezzen fel más modelleket**: Nézzen szét a [Hugging Face](https://huggingface.co/models?&sort=trending) oldalon olyan modellek után, amelyek beleférnek a fürt egyesített GPU-memóriájába
- **Bővítés négy csomópontra**: Adjon hozzá még két Ryzen AI Halo rendszert további Ray workerként, hogy a modelleket még több GPU között ossza fel. Ehhez legalább négyportos Ethernet-kapcsolóra van szükség, egy portra minden csomóponthoz. Kövesse a [2. lépés: Csatlakozás a fürthöz](#step-2-join-the-cluster-machine-2) útmutatót minden további workeren, és növelje a `--tensor-parallel-size` értékét ennek megfelelően
- **Próbáljon ki más párhuzamosítási stratégiákat is**: A vLLM támogatja az [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) módot mixture-of-experts modellekhez, valamint a [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) módot a nagyobb átviteli sebesség érdekében. Kísérletezzen a `--enable-expert-parallel` és `--data-parallel-size` beállításokkal, hogy megtalálja a munkaterheléséhez legjobban illeszkedő konfigurációt