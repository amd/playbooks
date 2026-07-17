<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Két Ryzen™ AI Halo klaszterezése RPC-vel

## Áttekintés

A Ryzen™ AI Halo már képes nagy nyelvi modellek helyi futtatására. A klaszterezés ezt tovább viszi azáltal, hogy több rendszer GPU memóriáját kombinálja egy helyi hálózaton keresztül, így még nagyobb modellekhez férhetsz hozzá erősebb következtetési képességekkel, jobb kódgenerálással és mélyebb többnyelvű megértéssel – mindezt teljesen a saját hardvereden.

Ez a playbook megtanítja, hogyan klaszterezz két Ryzen AI Halo rendszert a llama.cpp RPC motorjával, és hogyan futtasd a GLM 4.7-et, egy 358 milliárd paraméteres modellt, mindkét gépen AMD ROCm™ gyorsítással.

## Mit fogsz megtanulni

- Hogyan bővítsd a VRAM-foglalást Ryzen AI Halo rendszereken
- A llama.cpp telepítése ROCm és RPC támogatással
- RPC worker konfigurálása és elosztott következtetés indítása két csomópont között
- Egy 358 milliárd paraméteres modell futtatása két hálózatba kötött Ryzen AI Halo rendszeren

## A memóriakonfiguráció beállítása

> **Megjegyzés**: Ezt a lépést mindkét gépen (1. gép és 2. gép) el kell végezni.

<!-- @os:windows -->
Windows rendszeren a nagyobb, több memóriát igénylő modellek futtatásához az AMD Variable Graphics Memory (iGPU VRAM) foglalást kell használnunk.

Ezt az AMD Software: Adrenalin Edition vezérlőpult megnyitásával és a következő útvonalra navigálással lehet elvégezni: `Performance > Tuning > AMD Variable Graphics Memory`. Állítsd az értéket **96 GB**-ra. A változtatások érvénybe lépéséhez indítsd újra a rendszert.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Linux rendszeren a ROCm egy megosztott rendszermemória-készletet használ, amely alapértelmezés szerint a rendszermemória felére van beállítva.

Ez az érték növelhető a kernel Translation Table Manager (TTM) lapbeállításának módosításával, az alábbi utasítások szerint. Az AMD azt javasolja, hogy a BIOS-ban állítsd be a minimális dedikált VRAM-ot (0,5 GB).

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

* A változtatások érvénybe lépéséhez indítsd újra a rendszert.


<!-- @os:end -->
<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése

<!-- @require:software-update -->
<!-- @device:end -->
## Előfeltételek

### Hardver

Ez a playbook két Ryzen AI Halo egységet és egy Ethernet kapcsolót igényel, csillag topológiában összekötve, ahol minden egység közvetlenül a kapcsolóhoz van csatlakoztatva.

| Összetevő | Mennyiség | Leírás |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | A klasztert alkotó számítási csomópontok |
| 10 Gbps Ethernet kapcsoló | 1 | Központi kapcsoló a több csomópontos Ryzen AI Halo kommunikáció lehetővé tételéhez (legalább 2 port) |
| Ethernet kábel | 2 | Minden Halo egységet a kapcsolóhoz csatlakoztat (Cat 7 vagy magasabb ajánlott) |

> **Megjegyzés**: Két Ethernet kapcsolóport szükséges a két Ryzen AI Halo egység csatlakoztatásához. Egy harmadik port szükséges, ha a modellt egy különálló kliensgépről éred el az egyik Halo egység helyett.

### Szoftver
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Kérjük, telepítsd a következőket:
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

## Fizikai hardver beállítása

> **Megjegyzés**: Ezt a lépést mindkét gépen (1. gép és 2. gép) el kell végezni.

Csatlakoztass minden Ryzen AI Halo egységet az Ethernet kapcsolóhoz Cat 7 (vagy magasabb) kábellel. Ez hozza létre a csomópontok közötti nagy sebességű kommunikációhoz használt 10 Gbps kapcsolatot.
<!-- @os:linux -->
### 1. Hálózati interfészek meghatározása

Minden gépen keresd meg a hálózati interfész nevét, és jegyezd fel (az alábbiakban `IFNAME`-ként hivatkozunk rá). Futtasd:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Ez közvetlenül kiírja az interfész nevét, például:

```bash
enp191s0
```

### 2. Hálózati kapcsolat sebességének ellenőrzése

Erősítsd meg, hogy a kapcsolat aktív és teljes sebességen fut az interfész sebességének ellenőrzésével:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Megjegyzés**: Cseréld le az `<IFNAME>` értéket az [1. Hálózati interfészek meghatározása](#1-determine-network-interfaces) lépésből kapott interfésznévre.

`10000Mb/s` sebességet kell látnod:

```bash
	Speed: 10000Mb/s
```

> **Megjegyzés**: Ha a sebesség alacsonyabb, mint `10000Mb/s`, vagy a kapcsolat nem jön létre, ellenőrizd a kábel csatlakozását, és győződj meg arról, hogy a kapcsolóport 10 Gbps-ra van beállítva. Egyes kapcsolóknál le kell tiltani az automatikus tárgyalást, és manuálisan kell beállítani a kapcsolat sebességét; lásd a kapcsoló dokumentációját.

<!-- @os:end -->

<!-- @os:windows -->
### Hálózati kapcsolat sebességének ellenőrzése

Minden gépen ellenőrizd a hálózati interfészek kapcsolati sebességét:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Az Ethernet interfésznek `Up` állapotban kell lennie és `10 Gbps` sebességen kell futnia:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Megjegyzés**: Ha a sebesség alacsonyabb, mint `10 Gbps`, vagy a kapcsolat nem jön létre, ellenőrizd a kábel csatlakozását, és győződj meg arról, hogy a kapcsolóport 10 Gbps-ra van beállítva. Egyes kapcsolóknál le kell tiltani az automatikus tárgyalást, és manuálisan kell beállítani a kapcsolat sebességét; lásd a kapcsoló dokumentációját.

<!-- @os:end -->

## A llama.cpp telepítése

> **Megjegyzés**: Ezt a lépést mindkét gépen (1. gép és 2. gép) el kell végezni.

Két telepítési lehetőség áll rendelkezésre:

- [1. lehetőség: Lemonade SDK (Ajánlott)](#option-1-lemonade-sdk-recommended) – előre lefordított binárisok, leggyorsabb beállítás
- [2. lehetőség: Manuális forráskód-fordítás](#option-2-manual-source-build) – fordítás forrásból, teljes irányítással a fordítási jelzők felett

### 1. lehetőség: Lemonade SDK (Ajánlott)

A Lemonade SDK éjszakai buildeket biztosít a llama.cpp-hez AMD ROCm 7 gyorsítással, olyan GPU-kat célozva, mint a gfx1151 (Strix Halo / Ryzen AI Max+ 395) és más újabb Radeon architektúrák.

<!-- @os:windows -->
#### 1. lépés: Az előre lefordított binárisok letöltése

Navigálj a legújabb kiadás oldalára, és töltsd le a platformodnak és GPU célodnak megfelelő archívumot:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Töltsd le a `llama-bxxxx-windows-rocm-gfx1151-x64.zip` nevű fájlt (ahol `xxxx` a build száma).

#### 2. lépés: A binárisok kicsomagolása

Csomagold ki a letöltött archívumot:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Ez a könyvtár most tartalmazza a `llama-cli.exe`, `llama-server.exe` és `rpc-server.exe` ROCm-kompatibilis buildjeit, amelyek előre le vannak fordítva a Ryzen AI Halo rendszeredhez.

#### 3. lépés: GPU-felismerés ellenőrzése

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
#### 1. lépés: Az előre lefordított binárisok letöltése

Navigálj a legújabb kiadás oldalára, és töltsd le a platformodnak és GPU célodnak megfelelő archívumot:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Töltsd le a `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` nevű fájlt (ahol `xxxx` a build száma).

#### 2. lépés: A binárisok kicsomagolása és előkészítése

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Ez a könyvtár most tartalmazza a `llama-cli`, `llama-server` és `rpc-server` ROCm-kompatibilis buildjeit, amelyek előre le vannak fordítva a Ryzen AI Halo rendszeredhez.

#### 3. lépés: GPU-felismerés ellenőrzése

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
Miután a llama.cpp minden csomóponton elő van készítve, folytasd a [Modell letöltése](#downloading-the-model) résszel.

### 2. lehetőség: Manuális forráskód-fordítás

<!-- @os:windows -->
#### 1. lépés: A llama.cpp fordítása

Nyisd meg az **x64 Native Tools Command Prompt** ablakot (a Visual Studio Build Tools-szal telepítve), és klónozd a tárolót:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Add hozzá a HIP-et az útvonalhoz, és fordítsd le ROCm és RPC támogatással:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Fordítási jelző | Cél |
|-----------|---------|
| `-DGGML_HIP=ON` | Engedélyezi a ROCm/HIP szoftververmet |
| `-DGGML_RPC=ON` | Engedélyezi az RPC-t az elosztott következtetéshez |
| `-DGPU_TARGETS=gfx1151` | A Ryzen AI Halo GPU-t célozza (Radeon 8060s) |
| `-G Ninja` | A Ninja build rendszert használja |

#### 2. lépés: GPU-felismerés ellenőrzése

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

#### 3. lépés: A HIP hozzáadása a felhasználói útvonalhoz

A fenti fordítási lépés csak az aktuális munkamenethez állította be a `%HIP_PATH%\bin` értéket. Ahhoz, hogy a HIP könyvtárak bármely terminálban elérhetők legyenek (nem csak az x64 Native Tools Command Prompt-ban), add hozzá állandóan a felhasználói `PATH`-hoz:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Miután a llama.cpp minden csomóponton elő van készítve, folytasd a [Modell letöltése](#downloading-the-model) résszel.
<!-- @os:end -->

<!-- @os:linux -->
#### 1. lépés: A llama.cpp fordítása

Klónozd a tárolót:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Fordítsd le ROCm és RPC támogatással:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Fordítási jelző | Cél |
|-----------|---------|
| `-DGGML_HIP=ON` | Engedélyezi a ROCm szoftververmet |
| `-DGGML_RPC=ON` | Engedélyezi az RPC-t az elosztott következtetéshez |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Engedélyezi a rocWMMA-t a továbbfejlesztett Flash Attention funkcióhoz AMD GPU-kon |
| `-DAMDGPU_TARGETS="gfx1151"` | A Ryzen AI Halo GPU-t célozza (Radeon 8060s) |

További fordítási lehetőségekért lásd a [llama.cpp fordítási dokumentációját](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### 2. lépés: GPU-felismerés ellenőrzése

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

Miután a llama.cpp minden csomóponton elő van készítve, folytasd a [Modell letöltése](#downloading-the-model) résszel.
<!-- @os:end -->

## A modell letöltése

Ez a playbook a [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7)-et használja, egy 358 milliárd paraméteres modellt `Q4_K_XL` kvantálásban az [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL)-tól. Ennél a kvantálásnál a modell körülbelül 205 GB tárhelyet igényel, és belefér két Ryzen AI Halo csomópont kombinált GPU memóriájába.

Töltsd le a GGUF fájlokat a Hugging Face CLI segítségével:
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

> **Megjegyzés**: A modell letöltését az 1. gépen (a vezérlőn) kell elvégezni. Az RPC worker csomópontoknak nincs szükségük a modellfájlok helyi másolatára.

## A modell indítása a klaszteren

A llama.cpp RPC (Remote Procedure Call) motor lehetővé teszi, hogy egyetlen llama.cpp példány a modell rétegeit távoli workerekre töltse ki a hálózaton keresztül. Az egyik gép **vezérlőként** (1. gép) működik, kezelve a tokenizálást, ütemezést és vezénylést. A másik gép egy könnyűsúlyú **RPC szervert** futtat (2. gép), amely a GPU memóriáját és számítási kapacitását a vezérlő rendelkezésére bocsátja.

Betöltéskor a llama.cpp mindkét csomópont között szétdarabolja a modellt. A betöltés után a következtetés úgy zajlik, mintha egyetlen gyorsítón futna. Az RPC a háttérben kezeli a tenzorátadásokat és a szinkronizálást.

### 1. lépés: Az RPC szerver indítása (2. gép)

A 2. gépen indítsd el az RPC szervert, hogy a GPU erőforrásait elérhetővé tedd a vezérlő számára:
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
| `-p` | Az RPC szerver által használt port |
| `-c` | Helyi gyorsítótárat engedélyez a nagy tenzorokhoz, elkerülve az ismételt hálózati átviteleket a modell betöltése során |
| `--host` | IP-cím, amelyhez az RPC szerver kötődik (`0.0.0.0` az összes interfészhez) |

További lehetőségekért lásd a [llama.cpp RPC dokumentációját](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### 2. lépés: A modell indítása (1. gép)

Miután az RPC szerver fut a 2. gépen, indítsd el a következtetést az 1. gépről a `llama-cli` vagy a `llama-server` segítségével.

#### llama-cli

A `llama-cli` terminál alapú felületet biztosít a modellel való közvetlen interakcióhoz. Ideális teljesítményméréshez, hibakereséshez és alacsony szintű kísérletezéshez.

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

> **Az `<RPC_WORKER_IP>` megkeresése**: A 2. gépen futtasd a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megkereséséhez.
<!-- @os:end -->

<!-- @os:windows -->
> **Megjegyzés**: Ezt a parancsot a Terminálban (Powershell) futtasd.

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **Az `<RPC_WORKER_IP>` megkeresése**: A 2. gépen futtasd az `ipconfig | findstr /C:"IPv4"` parancsot a Terminálban (Powershell) a helyi IP-cím megkereséséhez.

<!-- @os:end -->

Futás közben a `llama-cli` megjeleníti a modell betöltési folyamatát, majd egy interaktív promptba lép, ahol közvetlenül cseveghet a modellel:

![llama-cli futtatja a GLM 4.7-et két csomóponton](assets/llama-cli-example.png)

#### llama-server

A `llama-server` ugyanazt a következtetési motort teszi elérhetővé egy állandó szerverfolyamaton keresztül, integrált webes felhasználói felülettel és OpenAI-kompatibilis HTTP API-val. Ez az előnyben részesített felület hosszabb futású telepítésekhez, több felhasználós hozzáféréshez és külső eszközökkel való integrációhoz.

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

> **Az `<RPC_WORKER_IP>` megkeresése**: A 2. gépen futtasd a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megkereséséhez.
<!-- @os:end -->

<!-- @os:windows -->
> **Megjegyzés**: Ezt a parancsot a Terminálban (Powershell) futtasd.

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

> **Az `<RPC_WORKER_IP>` megkeresése**: A 2. gépen futtasd az `ipconfig | findstr /C:"IPv4"` parancsot a Terminálban (Powershell) a helyi IP-cím megkereséséhez.
<!-- @os:end -->

Az indítás után nyisd meg a `http://<HOST_IP>:8081` címet a böngésződben a beépített webes felhasználói felület eléréséhez. Ez egy böngésző alapú csevegési felületet biztosít a modellel való interakcióhoz:

![llama-server webes felhasználói felület futtatja a GLM 4.7-et két csomóponton](assets/llama-server-example.png)

<!-- @os:linux -->
> **A `<HOST_IP>` megkeresése**: Az 1. gépen futtasd a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megkereséséhez.
<!-- @os:end -->

<!-- @os:windows -->
> **A `<HOST_IP>` megkeresése**: Az 1. gépen futtasd az `ipconfig | findstr /C:"IPv4"` parancsot a Terminálban (Powershell) a helyi IP-cím megkereséséhez.
<!-- @os:end -->

#### Paraméter-referencia

| Jelző | Cél |
|------|---------|
| `-m` | A GGUF modellfájl elérési útja (az első szilánkot használd: `00001-of-00005`) |
| `-c` | Kontextusméret tokenekben. A nagyobb értékek több memóriát használnak |
| `-fa on` | Engedélyezi a rocWMMA Flash Attention funkciót a jobb teljesítmény érdekében AMD GPU-kon |
| `-ngl 999` | Az összes modellréteget a GPU-ra tölti ki |
| `--no-mmap` | Letiltja a memória-leképezést, csökkentve a betöltési időt, ha a modell mérete meghaladja a rendszer RAM-ját, de belefér a VRAM-ba |
| `--host` | IP-cím, amelyhez a `llama-server` kötődik (csak `llama-server`) |
| `--port` | Port, amelyen a HTTP API-t kiszolgálja (csak `llama-server`) |
| `--rpc` | Vesszővel elválasztott RPC worker végpontok listája (`IP:port`) |

A teljes paraméterhasználatért lásd a [llama-cli dokumentációját](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) és a [llama-server dokumentációját](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Következő lépések

- **Harmadik féltől származó alkalmazások csatlakoztatása**: A `llama-server` OpenAI-kompatibilis API-t tesz elérhetővé. Irányítsd bármely OpenAI-kompatibilis alkalmazást (például Open WebUI) a `http://<HOST_IP>:8081` címre bármilyen helyőrző API-kulccsal (pl. `none`) a klaszterhez való csatlakozáshoz
- **Más modellek felfedezése**: Böngéssz kvantált GGUF-ok között a [Hugging Face](https://huggingface.co/models?search=gguf) oldalon, hogy megtaláld a klasztered kombinált GPU memóriájába illő modelleket
- **Skálázás négy csomópontra**: Adj hozzá még két Ryzen AI Halo rendszert további RPC workerként, hogy hozzáférj az 1 billió paraméteres skálájú modellekhez. Add meg a további végpontokat a `--rpc` paraméternek vesszővel elválasztott listaként (pl. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)