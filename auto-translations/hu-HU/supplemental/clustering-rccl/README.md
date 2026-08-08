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

# Két Ryzen™ AI Halo fürtözése RCCL-lel

## Áttekintés

Az Ön Ryzen™ AI Halo rendszere már önmagában is képes nagy nyelvi modellek helyi futtatására. A fürtözés ezt egy szinttel tovább viszi azáltal, hogy több rendszer GPU-memóriáját kombinálja egy helyi hálózaton keresztül, így akár még nagyobb modellekhez is hozzáférhet, erősebb következtetési képességekkel, jobb kódgenerálással és mélyebb többnyelvű megértéssel, mindezt teljes egészében a saját hardverén.

Ez a playbook megtanítja, hogyan fürtözhet két Ryzen AI Halo rendszert az RCCL (ROCm Communication Collectives Library) segítségével vLLM használatával, és hogyan futtathatja a Qwen3.5-397B modellt, amely 397 milliárd paraméterrel rendelkezik, mindkét gépen ROCm-gyorsítással.

## Amit tanulni fog

- Hogyan bővítheti a VRAM-kiosztást Ryzen AI Halo rendszereken
- vLLM indítása ROCm támogatással
- RCCL konfigurálása többcsomópontos, tenzor-párhuzamos következtetéshez két Ryzen AI Halo rendszer között
- Egy 397 milliárd paraméteres modell futtatása két hálózatba kötött Ryzen AI Halo rendszeren

## Előfeltételek

### Hardver

Ehhez a playbookhoz két Ryzen AI Halo egység és egy Ethernet-switch szükséges, csillag topológiába kötve, ahol mindegyik egység közvetlenül a switch-hez van csatlakoztatva.

| Komponens | Mennyiség | Leírás |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | A fürtöt alkotó számítási csomópontok |
| 10 Gbps-os Ethernet-switch | 1 | Központi switch, amely lehetővé teszi a Ryzen AI Halo egységek közötti, több csomópontos kommunikációt (legalább 2 porttal) |
| Ethernet-kábel | 2 | Az egyes Halo egységeket köti össze a switch-csel (Cat 7 vagy magasabb kategória ajánlott) |

> **Megjegyzés**: Két Ethernet-switch portra van szükség a két Ryzen AI Halo egység csatlakoztatásához. Egy harmadik portra akkor van szükség, ha a modellhez egy külön kliensgépről fér hozzá, nem pedig valamelyik Halo egységről.

### Szoftver
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fizikai hardverbeállítás

> **Megjegyzés**: Ezt a lépést mind az 1., mind a 2. gépen végezze el.

Csatlakoztassa mindegyik Ryzen AI Halo egységet az Ethernet-switch-hez egy Cat 7 (vagy magasabb kategóriájú) kábellel. Ez hozza létre a csomópontok közötti nagysebességű kommunikációhoz használt 10 Gbps-os kapcsolatot.

### 1. A hálózati interfészek meghatározása

Mindegyik gépen keresse meg a hálózati interfész nevét, és jegyezze fel (a további utasításokban `IFNAME` néven fogunk hivatkozni rá). Futtassa a következőt:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Ez közvetlenül kiírja az interfész nevét, például:

```bash
enp191s0
```

### 2. A hálózati kapcsolat sebességének ellenőrzése

Győződjön meg róla, hogy a kapcsolat aktív, és teljes sebességgel fut, az interfész sebességének ellenőrzésével:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Megjegyzés**: Cserélje ki a `<IFNAME>` értéket az [1. A hálózati interfészek meghatározása](#1-determine-network-interfaces) szakaszban kapott interfésznévre.

A sebességnek `10000Mb/s`-nak kell lennie:

```bash
	Speed: 10000Mb/s
```

> **Megjegyzés**: Ha a sebesség alacsonyabb, mint `10000Mb/s`, vagy a kapcsolat nem jön létre, ellenőrizze a kábelcsatlakozást, és győződjön meg róla, hogy a switch portja 10 Gbps-re van állítva. Néhány switch esetén ki kell kapcsolni az automatikus egyeztetést, és manuálisan kell beállítani a kapcsolat sebességét; tekintse meg a switch dokumentációját.

## A VRAM-kiosztás bővítése

> **Megjegyzés**: Ezt a lépést mind az 1., mind a 2. gépen végezze el.

### Memóriakonfiguráció nagy modellek futtatásához

Linuxon a ROCm egy megosztott rendszermemória-készletet használ, amely alapértelmezés szerint a rendszermemória felére van beállítva.

Ez a mennyiség a kernel Translation Table Manager (TTM) lapbeállításának módosításával növelhető, az alábbi utasítások szerint. Az AMD azt javasolja, hogy a minimális dedikált VRAM-ot a BIOS-ban állítsa be (0,5 GB).

* Telepítse a pipx segédprogramot, és adja hozzá a pipx által telepített csomagok elérési útját a rendszer keresési útvonalához.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Telepítse az amd-debug-tools csomagot a PyPI-ból.
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

* Indítsa újra a rendszert, hogy a változtatások érvénybe lépjenek.

## A vLLM-konténer inicializálása

> **Megjegyzés**: Ezt a lépést mind az 1., mind a 2. gépen végezze el.

Az Ön Ryzen AI Halo rendszere egy előre elkészített konténerképbe csomagolt vLLM-mel érkezik, amelyet a Podman, egy ingyenes, nyílt forráskódú konténereszköz segítségével futtathat.

### 1. Hozza létre a modellletöltési könyvtárat

Amikor ebben a playbookban kiszolgálja a Qwen3.5-397B modellt, a vLLM automatikusan letölti a modell súlyait a rendszerére. Annak érdekében, hogy ezek a súlyok a konténeren belülről is elérhetők legyenek, először hozzon létre egy modellek könyvtárat, amelyet a konténer csatolni tud:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. A vLLM-konténer indítása

Az alábbi parancs elindítja a konténert, és egy interaktív parancssorba helyezi Önt. Csatolja az imént létrehozott modellek könyvtárat, és átadja az `IFNAME` értékét az `NCCL_SOCKET_IFNAME` és a `GLOO_SOCKET_IFNAME` változóknak, megmondva ezzel az RCCL-nek (a könyvtárnak, amelyet a vLLM a GPU-k összehangolására használ a fürtben), hogy melyik interfészt használja.

Indítsa el a konténert a következővel:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Megjegyzés**: Cserélje ki a `<IFNAME>` értéket az [1. A hálózati interfészek meghatározása](#1-determine-network-interfaces) szakaszban kapott interfésznévre.

## A modell futtatása a fürtön

A vLLM a Ray-t használja a fürt orchestrálásához, és az RCCL-t a csomópontok közötti GPU-GPU kommunikáció kezelésére. Az egyik gép **fej csomópontként** (Machine 1) működik, amely a következtetést koordinálja. A másik **munkás csomópontként** (Machine 2) csatlakozik, hozzájárulva saját GPU-memóriájával és számítási kapacitásával.

> **Megjegyzés**: A Ray a vLLM opcionális függősége, és csak az előre konfigurált Podman-konténeren belülről érhető el.

Indításkor a vLLM a modellt tenzor-párhuzamossággal osztja fel mindkét csomópont között. A betöltés után a következtetés úgy zajlik, mintha egyetlen gyorsítón futna.

### 1. lépés: A Ray fej csomópont elindítása (1. gép)

Az 1. gépen indítsa el a Ray fej csomópontot a fürt inicializálásához:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **`<MACHINE_1_IP>` megkeresése**: Az 1. gépen futtassa a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megkereséséhez.
### 2. lépés: Csatlakozás a fürthöz (2. gép)

A 2. gépen csatlakozzon a fő csomóponthoz a fürt létrehozásához:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **A `<MACHINE_2_IP>` megkeresése**: A 2. gépen futtassa a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megkereséséhez.

### 3. lépés: A modell kiszolgálása (1. gép)

Az 1. gépen indítsa el a vLLM szervert. Ez automatikusan letölti a modellt, és megkezdi annak kiszolgálását mindkét csomóponton:

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

#### Paraméter-referencia

| Jelölő | Cél |
|------|---------|
| `--port` | A port, amelyen a HTTP API-t kiszolgálja |
| `--host` | Az IP-cím, amelyhez a szerver kötve van (`0.0.0.0` az összes interfészhez) |
| `--max-model-len` | Maximális kontextushossz tokenekben |
| `--gpu-memory-utilization` | A lefoglalandó GPU-memória aránya (0.0–1.0) |
| `--dtype` | A modellsúlyok adattípusa |
| `--tensor-parallel-size` | A GPU-k száma, amelyek között a modell szétosztásra kerül (állítsa be a fürtben lévő GPU-k teljes számára) |
| `--distributed-executor-backend` | Háttérrendszer a több csomópontos végrehajtáshoz (`ray` a fürtös telepítésekhez) |
| `--enforce-eager` | Letiltja a CUDA-grafikonok fordítását a kompatibilitás érdekében |
| `--language-model-only` | Kihagyja a kiegészítő modellösszetevők betöltését (pl. vizuális kódoló) |
| `--reasoning-parser` | Engedélyezi a strukturált következtetési kimenet elemzését a modellhez |

A teljes paraszter-használatért lásd a [vLLM dokumentációját](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## A modell elérése

A vLLM egy OpenAI-kompatibilis API-t biztosít, így bármilyen kompatibilis klienst vagy felületet csatlakoztathat a fürtjéhez. Az egyik népszerű lehetőség az [Open WebUI](https://github.com/open-webui/open-webui), amely böngészőalapú csevegőfelületet biztosít.

Az Open WebUI csatlakoztatásához a vLLM végponthoz:

1. Nyissa meg a **Settings** > **Admin Panel** > **Connections** menüpontot
2. Kattintson a **+** gombra a **Manage OpenAI API Connections** résznél
3. Állítsa a **Connection Type** értékét **External**-re
4. Állítsa be az **URL**-t erre: `http://<MACHINE_1_IP>:7000/v1`
5. Az **Auth** alatt válassza a **None** lehetőséget a legördülő menüből
6. Hagyja üresen a **Model IDs** mezőt az összes modell automatikus felderítéséhez a végpontról

> **A `<MACHINE_1_IP>` megkeresése**: Az 1. gépen futtassa a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megkereséséhez. Ha magáról az 1. gépről éri el az Open WebUI-t, használhatja a `http://localhost:7000/v1` címet.

![Open WebUI kapcsolati beállítások a vLLM végponthoz](assets/openwebui-connection.png)

A csatlakozás után válassza ki a modellt az Open WebUI modell-legördülő listájából, és kezdjen el csevegni. A modell mostantól mindkét Ryzen AI Halo csomóponton fut:

![Csevegés a Qwen3.5-397B modellel az Open WebUI-ban](assets/openwebui-chat.png)

## Következő lépések

- **Fedezzen fel más modelleket**: Fedezzen fel új modelleket a [Hugging Face](https://huggingface.co/models?&sort=trending) oldalon, amelyek illeszkednek a fürt kombinált GPU-memóriájához
- **Skálázás négy csomópontra**: Adjon hozzá két további Ryzen AI Halo rendszert kiegészítő Ray-munkásként, hogy a modelleket még több GPU között ossza szét. Ehhez egy legalább négy porttal rendelkező Ethernet-kapcsoló szükséges, csomópontonként egy porttal. Kövesse a [2. lépés: Csatlakozás a fürthöz](#step-2-join-the-cluster-machine-2) útmutatót minden további munkásgépen, és növelje ennek megfelelően a `--tensor-parallel-size` értékét
- **Próbáljon ki más párhuzamosítási stratégiákat**: A vLLM támogatja a [szakértői párhuzamosítást](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) a mixture-of-experts modellekhez, valamint az [adatpárhuzamosítást](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) a nagyobb átviteli sebesség érdekében. Kísérletezzen a `--enable-expert-parallel` és `--data-parallel-size` beállításokkal, hogy megtalálja a munkaterheléséhez legjobban illeszkedő konfigurációt