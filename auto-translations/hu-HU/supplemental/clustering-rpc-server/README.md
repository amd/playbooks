<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ez a playbook olyan speciális címkéket használ, amelyeket a GitHub nem tud megjeleníteni. A tartalom helyes megtekintéséhez látogasson el az [amd.com/playbooks](https://amd.com/playbooks) oldalra.
<!-- @github-only:end -->

# Két Ryzen™ AI Halo klaszterezése RPC segítségével

## Áttekintés

Az Ön Ryzen™ AI Halo rendszere már önmagában is képes helyben futtatni nagy nyelvi modelleket. A klaszterezés ezt viszi tovább azáltal, hogy több rendszer GPU memóriáját kombinálja egy helyi hálózaton keresztül, így még nagyobb modellekhez férhet hozzá, erősebb következtetési képességgel, jobb kódgenerálással és mélyebb többnyelvű megértéssel, mindezt teljes egészében a saját hardverén.

Ez a playbook megtanítja, hogyan lehet két Ryzen AI Halo rendszert klaszterezni a llama.cpp RPC motorjával, és hogyan futtatható a GLM 4.7, egy 358 milliárd paraméteres modell mindkét gépen, AMD ROCm™ gyorsítással.

## Amit meg fog tanulni

- Hogyan bővítheti a VRAM allokációt Ryzen AI Halo rendszereken
- A llama.cpp telepítése ROCm és RPC támogatással
- Egy RPC worker konfigurálása és az elosztott következtetés (inference) elindítása két csomóponton
- Egy 358 milliárd paraméteres modell futtatása két hálózatba kötött Ryzen AI Halo rendszeren

## A memóriakonfiguráció beállítása

> **Megjegyzés**: Ezt a lépést mind az 1., mind a 2. gépen végezze el.

<!-- @os:windows -->
Windows rendszeren, ha nagyobb memóriát igénylő modelleket szeretne futtatni, az AMD Variable Graphics Memory (iGPU VRAM) allokációt kell használnunk.

Ezt az AMD Software: Adrenalin Edition vezérlőpult megnyitásával és a következő útvonalra navigálva teheti meg: `Performance > Tuning > AMD Variable Graphics Memory`. Állítsa be az értéket **96 GB**-ra. A módosítások érvénybe lépéséhez indítsa újra a rendszert.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Linux rendszeren a ROCm egy megosztott rendszermemória-készletet használ, amely alapértelmezés szerint a rendszermemória felére van konfigurálva.

Ez a mennyiség a kernel Translation Table Manager (TTM) oldalbeállításának módosításával növelhető, a következő útmutató alapján. Az AMD azt javasolja, hogy a BIOS-ban állítsa be a minimális dedikált VRAM-ot (0,5 GB).

* Telepítse a pipx segédprogramot, és adja hozzá a pipx által telepített csomagok útvonalát a rendszer keresési útvonalához.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Telepítse az amd-debug-tools csomagot a PyPI-ből.
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

* A módosítások érvénybe lépéséhez indítsa újra a rendszert.


<!-- @os:end -->
<!-- @device:halo_box -->
## Ellenőrizze a szoftverfrissítéseket

<!-- @require:software-update -->
<!-- @device:end -->
## Előfeltételek

### Hardver

Ehhez a playbookhoz két Ryzen AI Halo egységre és egy Ethernet kapcsolóra van szükség, csillag topológiában összekötve, ahol minden egység közvetlenül csatlakozik a kapcsolóhoz.

| Komponens | Mennyiség | Leírás |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | A klasztert alkotó számítási csomópontok |
| 10 Gbps-os Ethernet kapcsoló | 1 | Központi kapcsoló, amely lehetővé teszi a több csomópontos Ryzen AI Halo kommunikációt (legalább 2 port) |
| Ethernet kábel | 2 | Az egyes Halo egységeket köti össze a kapcsolóval (Cat 7 vagy magasabb ajánlott) |

> **Megjegyzés**: Két Ethernet kapcsolóportra van szükség a két Ryzen AI Halo egység összekapcsolásához. Egy harmadik portra akkor van szükség, ha a modellhez egy külön kliensgépről fér hozzá, nem pedig az egyik Halo egységről.

### Szoftver
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Telepítse a következőket:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) a **Desktop Development with C++** munkaterheléssel
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fizikai hardverbeállítás

> **Megjegyzés**: Ezt a lépést mind az 1., mind a 2. gépen végezze el.

Csatlakoztassa mindkét Ryzen AI Halo egységet az Ethernet kapcsolóhoz egy Cat 7 (vagy magasabb) kábellel. Ez hozza létre a csomópontok közötti nagy sebességű kommunikációhoz használt 10 Gbps-os kapcsolatot.
<!-- @os:linux -->
### 1. A hálózati interfészek meghatározása

Mindegyik gépen keresse meg a hálózati interfész nevét, és jegyezze fel (a továbbiakban `IFNAME`-ként hivatkozunk rá). Futtassa:

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

> **Megjegyzés**: Cserélje ki a `<IFNAME>` értéket az [1. A hálózati interfészek meghatározása](#1-determine-network-interfaces) lépésben kapott kimeneti interfész nevére

A sebességnek `10000Mb/s`-nak kell lennie:

```bash
	Speed: 10000Mb/s
```

> **Megjegyzés**: Ha a sebesség alacsonyabb, mint `10000Mb/s`, vagy a kapcsolat nem jön létre, ellenőrizze a kábelcsatlakozást, és győződjön meg róla, hogy a kapcsoló portja 10 Gbps-ra van állítva. Egyes kapcsolók esetén az automatikus egyeztetést ki kell kapcsolni, és a kapcsolat sebességét manuálisan kell beállítani; ehhez tekintse meg a kapcsoló dokumentációját.

<!-- @os:end -->

<!-- @os:windows -->
### A hálózati kapcsolat sebességének ellenőrzése

Mindegyik gépen ellenőrizze a hálózati interfészek kapcsolat sebességét:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Az Ethernet interfésznek `Up` állapotban kell lennie, és `10 Gbps` sebességgel kell működnie:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Megjegyzés**: Ha a sebesség alacsonyabb, mint `10 Gbps`, vagy a kapcsolat nem jön létre, ellenőrizze a kábelcsatlakozást, és győződjön meg róla, hogy a kapcsoló portja 10 Gbps-ra van állítva. Egyes kapcsolók esetén az automatikus egyeztetést ki kell kapcsolni, és a kapcsolat sebességét manuálisan kell beállítani; ehhez tekintse meg a kapcsoló dokumentációját.

<!-- @os:end -->

## A llama.cpp telepítése

> **Megjegyzés**: Ezt a lépést mind az 1., mind a 2. gépen végezze el.

Két telepítési lehetőség áll rendelkezésre:

- [1. lehetőség: Lemonade SDK (ajánlott)](#option-1-lemonade-sdk-recommended) - előre elkészített binárisok, leggyorsabb beállítás
- [2. lehetőség: Manuális forráskódból történő build](#option-2-manual-source-build) - build forráskódból, teljes kontrollal a build flag-ek felett

### 1. lehetőség: Lemonade SDK (ajánlott)

A Lemonade SDK a llama.cpp éjszakai (nightly) buildjeit biztosítja AMD ROCm 7 gyorsítással, olyan GPU-kat célozva meg, mint a gfx1151 (Strix Halo / Ryzen AI Max+ 395) és más újabb Radeon architektúrák.

<!-- @os:windows -->
#### 1. lépés: Az előre elkészített binárisok letöltése

Navigáljon a legfrissebb kiadás oldalára, és töltse le a platformjának és GPU-célpontjának megfelelő archívumot:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Töltse le a `llama-bxxxx-windows-rocm-gfx1151-x64.zip` nevű fájlt (ahol az `xxxx` a build számát jelöli).

#### 2. lépés: A binárisok kicsomagolása

Csomagolja ki a letöltött archívumot:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Ez a könyvtár immár tartalmazza a `llama-cli.exe`, a `llama-server.exe` és az `rpc-server.exe` ROCm-alapú buildjeit, amelyeket a Ryzen AI Halo rendszerhez fordítottak le előre.

#### 3. lépés: A GPU-felismerés ellenőrzése

```bash
.\llama-cli.exe --list-devices
```

Várt kimenet:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### 1. lépés: Az előre elkészített binárisok letöltése

Navigáljon a legfrissebb kiadás oldalára, és töltse le a platformjának és GPU-célpontjának megfelelő archívumot:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Töltse le a `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` nevű fájlt (ahol az `xxxx` a build számát jelöli).

#### 2. lépés: A binárisok kicsomagolása és előkészítése

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Ez a könyvtár immár tartalmazza a `llama-cli`, a `llama-server` és az `rpc-server` ROCm-alapú buildjeit, amelyeket a Ryzen AI Halo rendszerhez fordítottak le előre.

#### 3. lépés: A GPU-felismerés ellenőrzése

```bash
./llama-cli --list-devices
```

Várt kimenet:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
Miután a llama.cpp mindkét csomóponton elő van készítve, folytassa a [Modell letöltése](#downloading-the-model) résszel.

### 2. lehetőség: Kézi forrásból történő build

<!-- @os:windows -->
#### 1. lépés: A llama.cpp buildelése

Nyissa meg az **x64 Native Tools Command Prompt** ablakot (a Visual Studio Build Tools telepíti), és klónozza a repót:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Adja hozzá a HIP-et az elérési útjához, majd buildeljen ROCm és RPC támogatással:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Build jelző | Cél |
|-----------|---------|
| `-DGGML_HIP=ON` | Engedélyezi a ROCm/HIP szoftverkészletet |
| `-DGGML_RPC=ON` | Engedélyezi az RPC-t az elosztott következtetéshez |
| `-DGPU_TARGETS=gfx1151` | A Ryzen AI Halo GPU-t (Radeon 8060s) célozza meg |
| `-G Ninja` | A Ninja build rendszert használja |

#### 2. lépés: A GPU-felismerés ellenőrzése

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

Várt kimenet:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### 3. lépés: A HIP hozzáadása a felhasználói elérési úthoz

A fenti buildlépés a `%HIP_PATH%\bin` értéket csak az aktuális munkamenetre állította be. Ahhoz, hogy a HIP-könyvtárak bármely terminálban elérhetők legyenek (nem csak az x64 Native Tools Command Prompt-ban), adja hozzá véglegesen a felhasználói `PATH`-hoz:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Miután a llama.cpp mindkét csomóponton elő van készítve, folytassa a [Modell letöltése](#downloading-the-model) résszel.
<!-- @os:end -->

<!-- @os:linux -->
#### 1. lépés: A llama.cpp buildelése

Klónozza a repót:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Buildeljen ROCm és RPC támogatással:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Build jelző | Cél |
|-----------|---------|
| `-DGGML_HIP=ON` | Engedélyezi a ROCm szoftverkészletet |
| `-DGGML_RPC=ON` | Engedélyezi az RPC-t az elosztott következtetéshez |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Engedélyezi a rocWMMA-t a jobb Flash Attention teljesítményhez AMD GPU-kon |
| `-DAMDGPU_TARGETS="gfx1151"` | A Ryzen AI Halo GPU-t (Radeon 8060s) célozza meg |

További build opciókért tekintse meg a [llama.cpp build dokumentációját](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### 2. lépés: A GPU-felismerés ellenőrzése

```bash
cd rocm/bin
./llama-cli --list-devices
```

Várt kimenet:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

Miután a llama.cpp mindkét csomóponton elő van készítve, folytassa a [Modell letöltése](#downloading-the-model) résszel.
<!-- @os:end -->

## A modell letöltése

Ez a útmutató a [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7) modellt használja, amely egy 358B paraméteres modell `Q4_K_XL` kvantálásban az [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL) forrásból. Ezen a kvantálási szinten a modell körülbelül 205 GB tárhelyet igényel, és beleférhet két Ryzen AI Halo csomópont kombinált GPU-memóriájába.

Töltse le a GGUF-fájlokat a Hugging Face CLI segítségével:
<!-- @os:linux -->
```bash
pip install huggingface-hub
hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

> **Megjegyzés**: A modell letöltését az 1. gépen (a vezérlőn) kell elvégezni. Az RPC munkavégző csomópontoknak nincs szükségük a modellfájlok helyi másolatára.

## A modell elindítása a klaszteren

A llama.cpp RPC (Remote Procedure Call) motorja lehetővé teszi, hogy egyetlen llama.cpp példány áthelyezze a modell rétegeit távoli munkavégzőkre a hálózaton keresztül. Az egyik gép **vezérlőként** (1. gép) működik, amely a tokenizálást, az ütemezést és az orchesztrációt végzi. A másik gép egy könnyűsúlyú **RPC szervert** futtat (2. gép), amely a GPU-memóriáját és számítási kapacitását teszi elérhetővé a vezérlő számára.

Betöltéskor a llama.cpp mindkét csomóponton szétosztja a modellt. A betöltés után a következtetés úgy zajlik, mintha egyetlen gyorsítón futna. Az RPC a háttérben kezeli a tenzorátviteleket és a szinkronizálást.

### 1. lépés: Az RPC szerver elindítása (2. gép)

A 2. gépen indítsa el az RPC szervert, hogy elérhetővé tegye a GPU-erőforrásait a vezérlő számára:
<!-- @os:linux -->
```bash
./rpc-server -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
.\rpc-server.exe -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

| Jelző | Cél |
|------|---------|
| `-p` | Az a port, amelyen az RPC szerver közvetít |
| `-c` | Engedélyezi a nagy tenzorok helyi gyorsítótárazását, elkerülve az ismétlődő hálózati átviteleket a modell betöltése közben |
| `--host` | Az IP-cím, amelyre az RPC szervert kötik (`0.0.0.0` az összes interfészhez) |

További opciókért tekintse meg a [llama.cpp RPC dokumentációját](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### 2. lépés: A modell elindítása (1. gép)

Miután az RPC szerver fut a 2. gépen, indítsa el a következtetést az 1. gépről a `llama-cli` vagy a `llama-server` segítségével.

#### llama-cli

A `llama-cli` egy terminálalapú felületet biztosít a modellel való közvetlen interakcióhoz. Ideális teljesítménytesztekhez, hibakereséshez és alacsony szintű kísérletezéshez.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --rpc <RPC_WORKER_IP>:50053
```

> **A `<RPC_WORKER_IP>` megkeresése**: A 2. gépen futtassa a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megkereséséhez.
<!-- @os:end -->

<!-- @os:windows -->
> **Megjegyzés**: Ezt a parancsot a Terminal (Powershell) ablakban futtassa.

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **A `<RPC_WORKER_IP>` megkeresése**: A 2. gépen futtassa az `ipconfig | findstr /C:"IPv4"` parancsot a Terminal (Powershell) ablakban a helyi IP-cím megkereséséhez.

<!-- @os:end -->

Miután elindult, a `llama-cli` megjeleníti a modell betöltési folyamatát, majd belép egy interaktív promptba, ahol közvetlenül csevegehet a modellel:

![llama-cli GLM 4.7-et futtat két csomóponton](assets/llama-cli-example.png)
#### llama-server

A `llama-server` ugyanazt a következtetési motort teszi elérhetővé egy állandóan futó szerverfolyamaton keresztül, beépített webes felhasználói felülettel és OpenAI-kompatibilis HTTP API-val. Ez az előnyben részesített felület a hosszabb ideig futó telepítésekhez, a többfelhasználós hozzáféréshez és a külső eszközökkel való integrációhoz.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_IP>:50053
```

> **A `<RPC_WORKER_IP>` megkeresése**: A 2. gépen futtassa a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megkereséséhez.
<!-- @os:end -->

<!-- @os:windows -->
> **Megjegyzés**: Ezt a parancsot terminálban (Powershell) futtassa.

```powershell
.\llama-server.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_IP>:50053
```

> **A `<RPC_WORKER_IP>` megkeresése**: A 2. gépen futtassa az `ipconfig | findstr /C:"IPv4"` parancsot terminálban (Powershell) a helyi IP-cím megkereséséhez.
<!-- @os:end -->

Az indítás után nyissa meg a `http://<HOST_IP>:8081` címet a böngészőjében, hogy hozzáférjen a beépített webes felhasználói felülethez. Ez egy böngészőalapú csevegőfelületet biztosít a modellel való interakcióhoz:

![A GLM 4.7 modellt két csomóponton futtató llama-server webes felhasználói felülete](assets/llama-server-example.png)

<!-- @os:linux -->
> **A `<HOST_IP>` megkeresése**: Az 1. gépen futtassa a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megkereséséhez.
<!-- @os:end -->

<!-- @os:windows -->
> **A `<HOST_IP>` megkeresése**: Az 1. gépen futtassa az `ipconfig | findstr /C:"IPv4"` parancsot terminálban (Powershell) a helyi IP-cím megkereséséhez.
<!-- @os:end -->

#### Paraméterreferencia

| Jelző | Cél |
|------|---------|
| `-m` | A GGUF modellfájl elérési útja (az első szeletet használja, `00001-of-00005`) |
| `-c` | A kontextusméret tokenben. A nagyobb értékek több memóriát használnak |
| `-fa on` | Engedélyezi a rocWMMA Flash Attention funkciót a jobb teljesítmény érdekében AMD GPU-kon |
| `-ngl 999` | Az összes modellréteget áthelyezi a GPU-ra |
| `--no-mmap` | Letiltja a memórialeképezést, csökkentve a betöltési időt, ha a modell mérete meghaladja a rendszer RAM-ját, de elfér a VRAM-ban |
| `--host` | Az IP-cím, amelyhez a `llama-server` csatlakozik (csak `llama-server`) |
| `--port` | A port, amelyen a HTTP API elérhető (csak `llama-server`) |
| `--rpc` | Vesszővel elválasztott lista az RPC munkavégző végpontjairól (`IP:port`) |

A teljes paraszterhasználatért tekintse meg a [llama-cli dokumentációt](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) és a [llama-server dokumentációt](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Következő lépések

- **Külső alkalmazások csatlakoztatása**: A `llama-server` egy OpenAI-kompatibilis API-t tesz elérhetővé. Irányítson bármilyen OpenAI-kompatibilis alkalmazást (például az Open WebUI-t) a `http://<HOST_IP>:8081` címre bármilyen helyőrző API-kulccsal (pl. `none`), hogy csatlakozzon a klaszteréhez
- **Más modellek felfedezése**: Böngésszen kvantált GGUF-okat a [Hugging Face](https://huggingface.co/models?search=gguf) oldalon, hogy olyan modelleket találjon, amelyek beleférnek a klaszter együttes GPU-memóriájába
- **Skálázás négy csomópontra**: Adjon hozzá még két Ryzen AI Halo rendszert további RPC munkavégzőként, hogy 1 billió paraméteres méretű modellekhez férjen hozzá. Adja meg a további végpontokat a `--rpc` paraméterhez vesszővel elválasztott listaként (pl. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)