<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Két Ryzen™ AI Halo klaszterezése RCCL-lel

## Áttekintés

A Ryzen™ AI Halo már önmagában is képes nagy nyelvi modelleket futtatni helyi környezetben. A klaszterezés ezt tovább viszi azáltal, hogy több rendszer GPU memóriáját kombinálja egy helyi hálózaton keresztül, így még nagyobb modellekhez férhetsz hozzá, erősebb következtetési képességekkel, jobb kódgenerálással és mélyebb többnyelvű megértéssel – mindezt teljesen a saját hardvereden.

Ez a playbook megtanítja, hogyan klaszterezz két Ryzen AI Halo rendszert RCCL (ROCm Communication Collectives Library) segítségével vLLM-mel, és hogyan futtasd a Qwen3.5-397B modellt – egy 397 milliárd paraméteres modellt – mindkét gépen ROCm gyorsítással.

## Mit fogsz megtanulni

- Hogyan bővítsd a VRAM-foglalást Ryzen AI Halo rendszereken
- A vLLM indítása ROCm támogatással
- Az RCCL konfigurálása többcsomópontos tenzor-párhuzamos következtetéshez két Ryzen AI Halo rendszeren keresztül
- Egy 397 milliárd paraméteres modell futtatása két hálózatba kötött Ryzen AI Halo rendszeren

## Előfeltételek

### Hardver

Ez a playbook két Ryzen AI Halo egységet és egy Ethernet kapcsolót igényel, csillag topológiában összekötve, ahol minden egység közvetlenül a kapcsolóhoz van csatlakoztatva.

| Összetevő | Mennyiség | Leírás |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | A klasztert alkotó számítási csomópontok |
| 10 Gbps Ethernet kapcsoló | 1 | Központi kapcsoló a többcsomópontos Ryzen AI Halo kommunikáció lehetővé tételéhez (legalább 2 port) |
| Ethernet kábel | 2 | Minden Halo egységet a kapcsolóhoz csatlakoztat (Cat 7 vagy magasabb ajánlott) |

> **Megjegyzés**: Két Ethernet kapcsolóport szükséges a két Ryzen AI Halo egység csatlakoztatásához. Egy harmadik port szükséges, ha a modellt egy különálló kliensgépről éred el az egyik Halo egység helyett.

### Szoftver
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fizikai hardver beállítása

> **Megjegyzés**: Ezt a lépést mindkét gépen (1. gép és 2. gép) végezd el.

Csatlakoztass minden Ryzen AI Halo egységet az Ethernet kapcsolóhoz Cat 7 (vagy magasabb) kábellel. Ez hozza létre a csomópontok közötti nagy sebességű kommunikációhoz használt 10 Gbps kapcsolatot.

### 1. Hálózati interfészek meghatározása

Minden gépen keresd meg a hálózati interfész nevét, és jegyezd fel (a továbbiakban az utasításokban `IFNAME`-ként hivatkozunk rá). Futtasd:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Ez közvetlenül kiírja az interfész nevét, például:

```bash
enp191s0
```

### 2. Hálózati kapcsolat sebességének ellenőrzése

Ellenőrizd, hogy a kapcsolat aktív és teljes sebességen fut az interfész sebességének lekérdezésével:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Megjegyzés**: Cseréld le az `<IFNAME>` értéket az [1. Hálózati interfészek meghatározása](#1-determine-network-interfaces) lépésből kapott interfésznévre.

`10000Mb/s` sebességet kell látnod:

```bash
	Speed: 10000Mb/s
```

> **Megjegyzés**: Ha a sebesség alacsonyabb `10000Mb/s`-nál, vagy a kapcsolat nem jön létre, ellenőrizd a kábel csatlakozását, és győződj meg arról, hogy a kapcsolóport 10 Gbps-ra van beállítva. Egyes kapcsolóknál szükség lehet az automatikus tárgyalás letiltására és a kapcsolat sebességének kézi beállítására; lásd a kapcsolód dokumentációját.

## VRAM-foglalás bővítése

> **Megjegyzés**: Ezt a lépést mindkét gépen (1. gép és 2. gép) végezd el.

### Memóriakonfiguráció nagy modellek futtatásához

Linux rendszeren a ROCm egy megosztott rendszermemória-készletet használ, amelyet alapértelmezés szerint a rendszermemória felére konfigurálnak.

Ez az érték növelhető a kernel Translation Table Manager (TTM) oldal beállításának módosításával, az alábbi utasítások szerint. Az AMD azt javasolja, hogy a minimális dedikált VRAM-ot a BIOS-ban állítsd be (0,5 GB).

* Telepítsd a pipx segédprogramot, és add hozzá a pipx által telepített csomagok elérési útját a rendszer keresési útvonalához.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Telepítsd az amd-debug-tools csomagot a PyPI-ről.
  ```bash
  pipx install amd-debug-tools
  ```

* Futtasd az amd-ttm eszközt a megosztott memória jelenlegi beállításainak lekérdezéséhez.
  ```bash
  amd-ttm
  ```

* Konfiguráld újra a megosztott memória beállításait **120 GB**-ra:
  ```bash
  amd-ttm --set 120
  ```

* Indítsd újra a rendszert a változtatások érvénybe lépéséhez.

## vLLM konténer inicializálása

> **Megjegyzés**: Ezt a lépést mindkét gépen (1. gép és 2. gép) végezd el.

A Ryzen AI Halo egy előre elkészített konténerképbe csomagolt vLLM-mel érkezik, amelyet Podman segítségével futtatsz – ez egy ingyenes és nyílt forráskódú konténereszköz.

### 1. A modell letöltési könyvtárának létrehozása

Amikor ebben a playbookban a Qwen3.5-397B modellt kiszolgálod, a vLLM automatikusan letölti a modell súlyait a rendszeredre. Annak érdekében, hogy ezek a súlyok elérhetők legyenek a konténerből, először hozz létre egy models könyvtárat, amelyet a konténer csatolhat:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. A vLLM konténer indítása

Az alábbi parancs elindítja a konténert, és egy interaktív shellbe dob. Csatolja az imént létrehozott models könyvtárat, és átadja az `IFNAME` értékedet az `NCCL_SOCKET_IFNAME` és `GLOO_SOCKET_IFNAME` változóknak, megmondva az RCCL-nek (a könyvtárnak, amelyet a vLLM a GPU-k klaszteren belüli koordinálásához használ), melyik interfészt vegye igénybe.

Indítsd el a konténert a következővel:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Megjegyzés**: Cseréld le az `<IFNAME>` értéket az [1. Hálózati interfészek meghatározása](#1-determine-network-interfaces) lépésből kapott interfésznévre.

## A modell futtatása a klaszteren

A vLLM Ray-t használ a klaszter vezénylésére, és RCCL-t a csomópontok közötti GPU–GPU kommunikáció kezelésére. Az egyik gép **fejcsomópontként** (1. gép) működik, koordinálva a következtetést. A másik **munkáscsomópontként** (2. gép) csatlakozik, hozzájárulva a GPU memóriájával és számítási kapacitásával.

> **Megjegyzés**: A Ray a vLLM opcionális függősége, és csak az előre konfigurált Podman konténerből érhető el.

Indításkor a vLLM tenzor-párhuzamosság segítségével osztja szét a modellt mindkét csomópont között. A betöltés után a következtetés úgy zajlik, mintha egyetlen gyorsítón futna.

### 1. lépés: A Ray fejcsomópont indítása (1. gép)

Az 1. gépen indítsd el a Ray fejcsomópontot a klaszter inicializálásához:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **A `<MACHINE_1_IP>` megkeresése**: Az 1. gépen futtasd a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megkereséséhez.

### 2. lépés: Csatlakozás a klaszterhez (2. gép)

A 2. gépen csatlakozz a fejcsomóponthoz a klaszter kialakításához:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **A `<MACHINE_2_IP>` megkeresése**: A 2. gépen futtasd a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megkereséséhez.

### 3. lépés: A modell kiszolgálása (1. gép)

Az 1. gépen indítsd el a vLLM szervert. Ez automatikusan letölti a modellt, és megkezdi a kiszolgálást mindkét csomóponton keresztül:

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

| Jelző | Cél |
|------|---------|
| `--port` | A HTTP API kiszolgálásához használt port |
| `--host` | IP-cím, amelyhez a szerver kötődik (`0.0.0.0` az összes interfészhez) |
| `--max-model-len` | Maximális kontexthossz tokenekben |
| `--gpu-memory-utilization` | A lefoglalandó GPU memória aránya (0,0–1,0) |
| `--dtype` | A modell súlyainak adattípusa |
| `--tensor-parallel-size` | A modell szétdarabolásához használt GPU-k száma (a klaszterben lévő összes GPU-ra állítva) |
| `--distributed-executor-backend` | Háttérrendszer a többcsomópontos végrehajtáshoz (`ray` klaszteres telepítésekhez) |
| `--enforce-eager` | Letiltja a CUDA gráf fordítást a kompatibilitás érdekében |
| `--language-model-only` | Kihagyja a kiegészítő modellkomponensek betöltését (pl. látáskódoló) |
| `--reasoning-parser` | Engedélyezi a strukturált következtetési kimenet elemzését a modellhez |

A teljes paraméterhasználatért lásd a [vLLM dokumentációját](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## A modell elérése

A vLLM OpenAI-kompatibilis API-t tesz elérhetővé, így bármilyen kompatibilis klienst vagy felületet csatlakoztathatsz a klaszterhez. Az egyik népszerű lehetőség az [Open WebUI](https://github.com/open-webui/open-webui), amely böngészőalapú csevegési felületet biztosít.

Az Open WebUI csatlakoztatásához a vLLM végponthoz:

1. Nyisd meg a **Beállítások** > **Adminisztrációs panel** > **Kapcsolatok** menüpontot
2. Kattints a **+** gombra az **OpenAI API-kapcsolatok kezelése** résznél
3. Állítsd a **Kapcsolat típusát** **Külső**-re
4. Állítsd az **URL**-t `http://<MACHINE_1_IP>:7000/v1`-re
5. A **Hitelesítés** alatt válaszd a **Nincs** lehetőséget a legördülő menüből
6. Hagyd üresen a **Modellazonosítók** mezőt, hogy a végpontról automatikusan felderítse az összes modellt

> **A `<MACHINE_1_IP>` megkeresése**: Az 1. gépen futtasd a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megkereséséhez. Ha az Open WebUI-t magáról az 1. gépről éred el, használhatod a `http://localhost:7000/v1` címet.

![Az Open WebUI kapcsolati beállításai a vLLM végponthoz](assets/openwebui-connection.png)

A csatlakozás után válaszd ki a modellt az Open WebUI modell legördülő menüjéből, és kezdj el csevegni. A modell most mindkét Ryzen AI Halo csomóponton fut:

![Csevegés a Qwen3.5-397B modellel az Open WebUI-ban](assets/openwebui-chat.png)

## Következő lépések

- **Fedezz fel más modelleket**: Fedezz fel új modelleket a [Hugging Face](https://huggingface.co/models?&sort=trending) oldalon, amelyek elférnek a klasztered kombinált GPU memóriájában
- **Bővítés négy csomópontra**: Adj hozzá még két Ryzen AI Halo rendszert további Ray munkásokként, hogy a modelleket még több GPU között oszd szét. Ehhez legalább négy porttal rendelkező Ethernet kapcsoló szükséges, csomópontonként egy. Kövesd a [2. lépés: Csatlakozás a klaszterhez](#step-2-join-the-cluster-machine-2) utasításait minden további munkáson, és növeld a `--tensor-parallel-size` értékét ennek megfelelően
- **Próbálj ki más párhuzamossági stratégiákat**: A vLLM támogatja a [szakértői párhuzamosságot](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) a mixture-of-experts modellekhez és az [adatpárhuzamosságot](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) a nagyobb átviteli sebesség érdekében. Kísérletezz az `--enable-expert-parallel` és `--data-parallel-size` beállításokkal, hogy megtaláld a legjobb konfigurációt a munkaterheledhez