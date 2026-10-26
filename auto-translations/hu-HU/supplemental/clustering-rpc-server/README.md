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

# Két Ryzen™ AI Halo fürtözése RPC-vel

## Áttekintés

Az Ön Ryzen™ AI Halo rendszere már most is képes nagy nyelvi modellek helyi futtatására. A fürtözés ezt tovább fejleszti azáltal, hogy több rendszer GPU memóriáját kombinálja egy helyi hálózaton keresztül, így hozzáférést biztosítva még nagyobb modellekhez, erősebb következtetési képességgel, jobb kódgenerálással és mélyebb többnyelvű megértéssel – mindezt teljes egészében a saját hardverén.

Ez a útmutató megtanítja, hogyan fürtözzön két Ryzen AI Halo rendszert a llama.cpp RPC motorjával, és hogyan futtassa a GLM 4.7-et, egy 358 milliárd paraméteres modellt, mindkét gépen AMD ROCm™ gyorsítással.

## Amit meg fog tanulni

- Hogyan bővítse a VRAM-allokációt Ryzen AI Halo rendszereken
- A llama.cpp telepítése ROCm és RPC támogatással
- Egy RPC worker konfigurálása és elosztott következtetés indítása két csomóponton
- Egy 358 milliárd paraméteres modell futtatása két hálózatba kötött Ryzen AI Halo rendszeren

## A memóriakonfiguráció beállítása

> **Megjegyzés**: Ezt a lépést mindkét gépen, az 1. gépen és a 2. gépen is végezze el.

<!-- @device:halo_box -->
<!-- @os:windows -->
> **128 GB közeli vagy afeletti modellek futtatása:** AMD Ryzen™ AI Max 400 sorozatú (Gorgon Halo) rendszereken, Windows alatt, a 128 GB memóriát megközelítő vagy meghaladó modellek futtatásához további konfigurációra van szükség a hibamentes működéshez. Kövesse az [AMD Ryzen AI Max PRO 400 Series Windows OS Guidelines](https://docs.amd.com/v/u/en-US/73342_1.00_AMD_Ryzen_AI_Max_PRO_400_Series_Windows_OS_Guidelines) útmutatót a modell betöltése előtt.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:windows -->
Windows alatt, a nagyobb memóriát igénylő modellek futtatásához az AMD Variable Graphics Memory (iGPU VRAM) allokációt kell használnunk.

Ez megtehető az AMD Software: Adrenalin Edition vezérlőpult megnyitásával, majd a következő útvonalra navigálva: `Performance > Tuning > AMD Variable Graphics Memory`. Állítsa az értéket **96 GB**-ra. A változtatások érvénybe lépéséhez indítsa újra a rendszert.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Linux alatt a ROCm egy megosztott rendszermemória-készletet használ, amely alapértelmezés szerint a rendszermemória felére van beállítva.

Ez a mennyiség növelhető a kernel Translation Table Manager (TTM) lapméret-beállításának módosításával, az alábbi utasítások szerint. Az AMD azt javasolja, hogy a BIOS-ban állítsa be a minimális dedikált VRAM-ot (0,5 GB).

* Telepítse a pipx segédprogramot, és adja hozzá a pipx által telepített csomagok elérési útját a rendszer keresési útvonalához.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Telepítse az amd-debug-tools csomagot a PyPI-ről.
  ```bash
  pipx install amd-debug-tools
  ```

* Futtassa az amd-ttm eszközt a megosztott memória jelenlegi beállításainak lekérdezéséhez.
  ```bash
  amd-ttm
  ```

* Állítsa át a megosztott memória beállításait **120 GB**-ra:
  ```bash
  amd-ttm --set 120
  ```

* A változtatások érvénybe lépéséhez indítsa újra a rendszert.


<!-- @os:end -->
<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése

<!-- @require:software-update -->
<!-- @device:end -->
## Előfeltételek

### Hardver

Ehhez az útmutatóhoz két Ryzen AI Halo egységre és egy Ethernet switch-re van szükség, csillag topológiában összekötve, ahol minden egység közvetlenül a switch-hez van kötve.

| Komponens | Mennyiség | Leírás |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | A fürtöt alkotó számítási csomópontok |
| 10 Gbps Ethernet switch | 1 | Központi switch, amely lehetővé teszi a több csomópontos Ryzen AI Halo kommunikációt (legalább 2 port) |
| Ethernet kábel | 2 | Minden Halo egységet a switch-hez köt (Cat 7 vagy magasabb ajánlott) |

> **Megjegyzés**: Két Ethernet switch portra van szükség a két Ryzen AI Halo egység összekötéséhez. Egy harmadik portra akkor van szükség, ha a modellhez egy különálló kliensgépről fér hozzá, nem pedig az egyik Halo egységről.

### Szoftver
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Kérjük, telepítse a következőket:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) a **Desktop Development with C++** munkaterhelésben
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fizikai hardver beüzemelése

> **Megjegyzés**: Ezt a lépést mindkét gépen, az 1. gépen és a 2. gépen is végezze el.

Csatlakoztassa mindkét Ryzen AI Halo egységet az Ethernet switch-hez egy Cat 7 (vagy magasabb) kábellel. Ez hozza létre a csomópontok közötti nagy sebességű kommunikációhoz használt 10 Gbps-es kapcsolatot.
<!-- @os:linux -->
### 1. A hálózati interfészek meghatározása

Mindkét gépen keresse meg a hálózati interfész nevét, és jegyezze fel (a továbbiakban `IFNAME` néven hivatkozunk rá). Futtassa:

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

> **Megjegyzés**: Cserélje ki a `<IFNAME>` értékét az [1. A hálózati interfészek meghatározása](#1-determine-network-interfaces) lépésben kapott interfész névre.

A sebességnek `10000Mb/s`-nak kell lennie:

```bash
	Speed: 10000Mb/s
```

> **Megjegyzés**: Ha a sebesség alacsonyabb, mint `10000Mb/s`, vagy a kapcsolat nem jön létre, ellenőrizze a kábelcsatlakozást, és győződjön meg róla, hogy a switch portja 10 Gbps-re van állítva. Egyes switch-ek esetén le kell tiltani az automatikus egyeztetést, és manuálisan kell beállítani a kapcsolat sebességét; tekintse meg a switch dokumentációját.

<!-- @os:end -->

<!-- @os:windows -->
### A hálózati kapcsolat sebességének ellenőrzése

Mindkét gépen ellenőrizze a hálózati interfészek kapcsolati sebességét:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Az Ethernet interfésznek `Up` állapotban kell lennie, és `10 Gbps` sebességgel kell futnia:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Megjegyzés**: Ha a sebesség alacsonyabb, mint `10 Gbps`, vagy a kapcsolat nem jön létre, ellenőrizze a kábelcsatlakozást, és győződjön meg róla, hogy a switch portja 10 Gbps-re van állítva. Egyes switch-ek esetén le kell tiltani az automatikus egyeztetést, és manuálisan kell beállítani a kapcsolat sebességét; tekintse meg a switch dokumentációját.

<!-- @os:end -->

## A llama.cpp telepítése

> **Megjegyzés**: Ezt a lépést mindkét gépen, az 1. gépen és a 2. gépen is végezze el.

Két telepítési lehetőség áll rendelkezésre:

- [1. lehetőség: Lemonade SDK (ajánlott)](#option-1-lemonade-sdk-recommended) - előre elkészített binárisok, leggyorsabb beállítás
- [2. lehetőség: Manuális forráskódból történő build](#option-2-manual-source-build) - forráskódból történő buildelés, teljes kontrollal a build flagek felett
### 1. lehetőség: Lemonade SDK (Ajánlott)

A Lemonade SDK éjszakai (nightly) buildeket biztosít a llama.cpp-hez AMD ROCm 7 gyorsítással, olyan GPU-kat célozva, mint a gfx1151 (Strix Halo / Ryzen AI Max+ 395) és más újabb Radeon architektúrák.

<!-- @os:windows -->
#### 1. lépés: Az előre elkészített binárisok letöltése

Navigáljon a legújabb kiadás oldalára, és töltse le a platformjának és GPU céljának megfelelő archívumot:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Töltse le a `llama-bxxxx-windows-rocm-gfx1151-x64.zip` nevű fájlt (ahol az `xxxx` a build számát jelöli).

#### 2. lépés: A binárisok kicsomagolása

Csomagolja ki a letöltött archívumot:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Ez a könyvtár most már tartalmazza a `llama-cli.exe`, a `llama-server.exe` és az `rpc-server.exe` ROCm-képes buildjeit, előre lefordítva az Ön Ryzen AI Halo rendszeréhez.

#### 3. lépés: A GPU felismerésének ellenőrzése

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

Navigáljon a legújabb kiadás oldalára, és töltse le a platformjának és GPU céljának megfelelő archívumot:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Töltse le a `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` nevű fájlt (ahol az `xxxx` a build számát jelöli).

#### 2. lépés: A binárisok kicsomagolása és előkészítése

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Ez a könyvtár most már tartalmazza a `llama-cli`, a `llama-server` és az `rpc-server` ROCm-képes buildjeit, előre lefordítva az Ön Ryzen AI Halo rendszeréhez.

#### 3. lépés: A GPU felismerésének ellenőrzése

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
Miután a llama.cpp minden csomóponton elő van készítve, folytassa [A modell letöltése](#downloading-the-model) résznél.

### 2. lehetőség: Manuális forráskódból történő build

<!-- @os:windows -->
#### 1. lépés: A llama.cpp buildelése

Nyissa meg az **x64 Native Tools Command Prompt**-ot (a Visual Studio Build Tools telepíti), és klónozza a repository-t:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Adja hozzá a HIP-et az elérési útvonalhoz, és buildeljen ROCm és RPC támogatással:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Build jelző | Cél |
|-----------|---------|
| `-DGGML_HIP=ON` | Engedélyezi a ROCm/HIP szoftverstacket |
| `-DGGML_RPC=ON` | Engedélyezi az RPC-t az elosztott következtetéshez |
| `-DGPU_TARGETS=gfx1151` | A Ryzen AI Halo GPU-t (Radeon 8060s) célozza |
| `-G Ninja` | A Ninja build rendszert használja |

#### 2. lépés: A GPU felismerésének ellenőrzése

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

#### 3. lépés: A HIP hozzáadása a felhasználói elérési útvonalhoz

A fenti build lépés csak az aktuális munkamenetre állította be a `%HIP_PATH%\bin` útvonalat. Ahhoz, hogy a HIP könyvtárak bármely terminálban elérhetők legyenek (nem csak az x64 Native Tools Command Promptban), adja hozzá véglegesen a felhasználói `PATH` változóhoz:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Miután a llama.cpp minden csomóponton elő van készítve, folytassa [A modell letöltése](#downloading-the-model) résznél.
<!-- @os:end -->

<!-- @os:linux -->
#### 1. lépés: A llama.cpp buildelése

Klónozza a repository-t:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Buildeljen ROCm és RPC támogatással:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Build jelző | Cél |
|-----------|---------|
| `-DGGML_HIP=ON` | Engedélyezi a ROCm szoftverstacket |
| `-DGGML_RPC=ON` | Engedélyezi az RPC-t az elosztott következtetéshez |
| `-DAMDGPU_TARGETS="gfx1151"` | A Ryzen AI Halo GPU-t (Radeon 8060s) célozza |

További build opciókért tekintse meg a [llama.cpp build dokumentációját](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### 2. lépés: A GPU felismerésének ellenőrzése

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

Miután a llama.cpp minden csomóponton elő van készítve, folytassa [A modell letöltése](#downloading-the-model) résznél.
<!-- @os:end -->

## A modell letöltése

Ez a játékkönyv a [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7) modellt használja, amely egy 358 milliárd paraméteres modell `Q4_K_XL` kvantálásban, az [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL) oldaláról. Ennél a kvantálásnál a modell körülbelül 205 GB tárhelyet igényel, és elfér két Ryzen AI Halo csomópont kombinált GPU memóriájában.

Töltse le a GGUF fájlokat a Hugging Face CLI segítségével:
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

A llama.cpp RPC (Remote Procedure Call) motor lehetővé teszi, hogy egyetlen llama.cpp példány áthelyezze a modell rétegeit távoli munkavégzőkre a hálózaton keresztül. Az egyik gép **vezérlőként** (1. gép) működik, és ellátja a tokenizálást, az ütemezést és az orchesztrációt. A másik gép egy könnyűsúlyú **RPC szervert** (2. gép) futtat, amely a saját GPU memóriáját és számítási kapacitását teszi elérhetővé a vezérlő számára.

Betöltéskor a llama.cpp szétosztja a modellt a két csomópont között. A betöltés után a következtetés úgy zajlik, mintha egyetlen gyorsítón futna. Az RPC a háttérben kezeli a tenzor-átviteleket és a szinkronizációt.

### 1. lépés: Az RPC szerver elindítása (2. gép)

A 2. gépen indítsa el az RPC szervert, hogy elérhetővé tegye a GPU erőforrásait a vezérlő számára:
<!-- @os:linux -->
```bash
./ggml-rpc-server -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
.\ggml-rpc-server.exe -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

| Jelző | Cél |
|------|---------|
| `-p` | A port, amelyen az RPC szerver sugározza magát |
| `-c` | Engedélyez egy helyi gyorsítótárat a nagy tenzorokhoz, elkerülve az ismételt hálózati átviteleket a modell betöltése közben |
| `--host` | Az IP cím, amelyhez az RPC szervert kötni kívánja (`0.0.0.0` minden interfészhez) |

További opciókért tekintse meg a [llama.cpp RPC dokumentációját](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### 2. lépés: A modell elindítása (1. gép)

Miután az RPC szerver fut a 2. gépen, indítsa el a következtetést az 1. gépről a `llama-cli` vagy a `llama-server` segítségével.
#### llama-cli

A `llama-cli` egy terminál alapú felületet biztosít a modellel való közvetlen interakcióhoz. Ideális benchmarkoláshoz, hibakereséshez és alacsony szintű kísérletezéshez.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>` megkeresése**: A 2. gépen futtassa a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megállapításához.
<!-- @os:end -->

<!-- @os:windows -->
> **Megjegyzés**: Ezt a parancsot a Terminálban (Powershell) futtassa.

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>` megkeresése**: A 2. gépen futtassa az `ipconfig | findstr /C:"IPv4"` parancsot a Terminálban (Powershell) a helyi IP-cím megállapításához.

<!-- @os:end -->

Az elindítás után a `llama-cli` megjeleníti a modell betöltésének folyamatát, majd belép egy interaktív promptba, ahol közvetlenül cseveghet a modellel:

![llama-cli futtatja a GLM 4.7-et két csomóponton](assets/llama-cli-example.png)

#### llama-server

A `llama-server` ugyanazt a következtetési motort teszi elérhetővé egy állandó szerverfolyamaton keresztül, integrált webes felhasználói felülettel és OpenAI-kompatibilis HTTP API-val. Ez az előnyben részesített felület hosszabb ideig futó üzemeltetésekhez, több felhasználós hozzáféréshez és külső eszközökkel való integrációhoz.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>` megkeresése**: A 2. gépen futtassa a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megállapításához.
<!-- @os:end -->

<!-- @os:windows -->
> **Megjegyzés**: Ezt a parancsot a Terminálban (Powershell) futtassa.

```powershell
.\llama-server.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>` megkeresése**: A 2. gépen futtassa az `ipconfig | findstr /C:"IPv4"` parancsot a Terminálban (Powershell) a helyi IP-cím megállapításához.
<!-- @os:end -->

Az elindítás után nyissa meg a `http://<HOST_IP>:8081` címet a böngészőjében a beépített webes felület eléréséhez. Ez egy böngésző alapú csevegőfelületet biztosít a modellel való interakcióhoz:

![llama-server webes felülete, amely a GLM 4.7-et futtatja két csomóponton](assets/llama-server-example.png)

<!-- @os:linux -->
> **`<HOST_IP>` megkeresése**: Az 1. gépen futtassa a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megállapításához.
<!-- @os:end -->

<!-- @os:windows -->
> **`<HOST_IP>` megkeresése**: Az 1. gépen futtassa az `ipconfig | findstr /C:"IPv4"` parancsot a Terminálban (Powershell) a helyi IP-cím megállapításához.
<!-- @os:end -->

#### Paraméter referencia

| Jelölő | Cél |
|------|---------|
| `-m` | A GGUF modellfájl elérési útja (az első szeletet használja, `00001-of-00005`) |
| `-c` | Kontextusméret tokenekben. A nagyobb értékek több memóriát használnak |
| `-fa on` | Engedélyezi a rocWMMA Flash Attention funkciót a jobb teljesítmény érdekében AMD GPU-kon |
| `-ngl 999` | A modell összes rétegét áthelyezi a GPU-ra |
| `-lm none` | A modell betöltési módját `none` értékre állítja, letiltva a memórialeképezést, hogy csökkentse a betöltési időt, ha a modell mérete meghaladja a rendszer RAM-ját, de belefér a VRAM-ba |
| `--host` | Az IP-cím, amelyhez a `llama-server`-t kötni kell (csak a `llama-server`) |
| `--port` | A port, amelyen a HTTP API-t kiszolgálja (csak a `llama-server`) |
| `--rpc` | Vesszővel elválasztott lista az RPC worker végpontokról (`IP:port`) |

A teljes paraméterhasználatért tekintse meg a [llama-cli dokumentációt](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) és a [llama-server dokumentációt](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Következő lépések

- **Harmadik féltől származó alkalmazások csatlakoztatása**: A `llama-server` egy OpenAI-kompatibilis API-t tesz elérhetővé. Irányítson bármilyen OpenAI-kompatibilis alkalmazást (például az Open WebUI-t) a `http://<HOST_IP>:8081` címre bármilyen helyőrző API-kulccsal (pl. `none`), hogy csatlakozzon a klaszteréhez
- **Más modellek felfedezése**: Böngésszen kvantált GGUF-okat a [Hugging Face](https://huggingface.co/models?search=gguf) oldalon, hogy olyan modelleket találjon, amelyek beleférnek a klasztere kombinált GPU-memóriájába
- **Bővítés négy csomópontra**: Adjon hozzá további két Ryzen AI Halo rendszert további RPC workerként, hogy elérje az 1 billió paraméter skálájú modelleket. Adjon át további végpontokat a `--rpc` paraméternek vesszővel elválasztott listaként (pl. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)