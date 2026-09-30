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

# Négy Ryzen™ AI Halo klaszterezése RPC-vel

## Áttekintés

A Ryzen™ AI Halo már önmagában is képes nagy nyelvi modellek helyi futtatására. A klaszterezés ezt viszi tovább azáltal, hogy több rendszer GPU-memóriáját kombinálja egy helyi hálózaton keresztül, így még nagyobb modellekhez férhet hozzá, erősebb következtetési képességgel, jobb kódgenerálással és mélyebb többnyelvű megértéssel – mindezt teljes egészében a saját hardverén.

Ez a útmutató megtanítja, hogyan lehet négy Ryzen AI Halo rendszert klaszterbe szervezni a llama.cpp RPC motorjának segítségével, majd hogyan futtassa a Kimi K2.6-ot, egy nagy mixture-of-experts modellt mind a négy gépen, AMD ROCm™ gyorsítással.

## Amit meg fog tanulni

- Hogyan bővítheti a VRAM-allokációt Ryzen AI Halo rendszereken
- A llama.cpp telepítése ROCm és RPC támogatással
- RPC workerek konfigurálása és elosztott következtetés indítása négy csomóponton keresztül
- Egy 1T paraméteres modell futtatása négy hálózatba kötött Ryzen AI Halo rendszeren keresztül

## Memóriakonfiguráció beállítása

> **Megjegyzés**: Ezt a lépést mind a négy gépen (1–4. gép) hajtsa végre.

<!-- @os:windows -->
Windows rendszeren, a nagyobb memóriát igénylő modellek futtatásához az AMD Variable Graphics Memory (iGPU VRAM) allokációt kell használnunk.

Ez az AMD Software: Adrenalin Edition vezérlőpanel megnyitásával és a következő útvonalra navigálva tehető meg: `Performance > Tuning > AMD Variable Graphics Memory`. Állítsa az értéket **96 GB**-ra. Kérjük, indítsa újra a rendszert, hogy a változtatások érvénybe lépjenek.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Linuxon a ROCm egy megosztott rendszermemória-készletet használ, amely alapértelmezés szerint a rendszermemória felére van beállítva.

Ez az érték a következő utasításokkal növelhető, a kernel Translation Table Manager (TTM) lapbeállításának módosításával. Az AMD azt javasolja, hogy a BIOS-ban állítsa be a minimális dedikált VRAM-ot (0,5 GB).

* Telepítse a pipx segédprogramot, és adja hozzá a pipx által telepített wheel csomagok elérési útját a rendszer keresési útvonalához.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Telepítse az amd-debug-tools wheel csomagot a PyPI-ból.
  ```bash
  pipx install amd-debug-tools
  ```

* Futtassa az amd-ttm eszközt a megosztott memória jelenlegi beállításainak lekérdezéséhez.
  ```bash
  amd-ttm
  ```

* Állítsa be újra a megosztott memória beállításait **120 GB**-ra:
  ```bash
  amd-ttm --set 120
  ```

* Indítsa újra a rendszert, hogy a változtatások érvénybe lépjenek.


<!-- @os:end -->
<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése

<!-- @require:software-update -->
<!-- @device:end -->
## Előfeltételek

### Hardver

Ehhez az útmutatóhoz négy Ryzen AI Halo egységre és egy Ethernet switchre van szükség, csillag topológiában összekötve, ahol minden egység közvetlenül a switchhez van csatlakoztatva.

| Komponens | Mennyiség | Leírás |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | A klasztert alkotó számítási csomópontok |
| 10 Gbps-es Ethernet switch | 1 | Központi switch, amely lehetővé teszi a többcsomópontos Ryzen AI Halo kommunikációt (legalább 4 porttal) |
| Ethernet kábel | 4 | Összeköti az egyes Halo egységeket a switchel (Cat 7 vagy magasabb kategória ajánlott) |

> **Megjegyzés**: Négy Ethernet switch portra van szükség a négy Ryzen AI Halo egység csatlakoztatásához. Egy ötödik portra akkor van szükség, ha a modellt egy külön kliens gépről, nem pedig az egyik Halo egységről éri el.

### Szoftver
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Kérjük, telepítse a következőket:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) a **Desktop Development with C++** munkaterhelés kiválasztásával
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fizikai hardver beállítása

> **Megjegyzés**: Ezt a lépést mind a négy gépen (1–4. gép) hajtsa végre.

Csatlakoztassa az egyes Ryzen AI Halo egységeket az Ethernet switchhez egy Cat 7 (vagy magasabb kategóriájú) kábellel. Ez létrehozza a 10 Gbps-es kapcsolatot, amelyet a csomópontok közötti nagysebességű kommunikációhoz használunk.
<!-- @os:linux -->
### 1. Hálózati interfészek meghatározása

Minden egyes gépen keresse meg a hálózati interfész nevét, és jegyezze fel (a továbbiakban `IFNAME`-ként hivatkozunk rá). Futtassa:

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

> **Megjegyzés**: Cserélje ki a `<IFNAME>` értéket az [1. Hálózati interfészek meghatározása](#1-determine-network-interfaces) kimeneti interfész nevére

A sebességnek `10000Mb/s`-nek kell lennie:

```bash
	Speed: 10000Mb/s
```

> **Megjegyzés**: Ha a sebesség alacsonyabb, mint `10000Mb/s`, vagy a kapcsolat nem jön létre, ellenőrizze a kábelcsatlakozást, és győződjön meg arról, hogy a switch port 10 Gbps-re van állítva. Egyes switchek esetén az automatikus egyeztetést ki kell kapcsolni, és a kapcsolat sebességét manuálisan kell beállítani; olvassa el a switch dokumentációját.

<!-- @os:end -->

<!-- @os:windows -->
### Hálózati kapcsolat sebességének ellenőrzése

Minden egyes gépen ellenőrizze a hálózati interfészek kapcsolati sebességét:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Az Ethernet interfésznek `Up` állapotban kell lennie, `10 Gbps` sebességgel futva:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Megjegyzés**: Ha a sebesség alacsonyabb, mint `10 Gbps`, vagy a kapcsolat nem jön létre, ellenőrizze a kábelcsatlakozást, és győződjön meg arról, hogy a switch port 10 Gbps-re van állítva. Egyes switchek esetén az automatikus egyeztetést ki kell kapcsolni, és a kapcsolat sebességét manuálisan kell beállítani; olvassa el a switch dokumentációját.

<!-- @os:end -->

## A llama.cpp telepítése

> **Megjegyzés**: Ezt a lépést mind a négy gépen (1–4. gép) hajtsa végre.

Két telepítési lehetőség érhető el:

- [1. lehetőség: Lemonade SDK (Ajánlott)](#option-1-lemonade-sdk-recommended) – előre elkészített binárisok, leggyorsabb beállítás
- [2. lehetőség: Manuális forráskódból történő build](#option-2-manual-source-build) – build forráskódból, teljes kontrollal a build flag-ek felett

### 1. lehetőség: Lemonade SDK (Ajánlott)

A Lemonade SDK éjszakai (nightly) buildeket biztosít a llama.cpp-hez AMD ROCm 7 gyorsítással, olyan GPU-kat célozva, mint a gfx1151 (Strix Halo / Ryzen AI Max+ 395) és más újabb Radeon architektúrák.

<!-- @os:windows -->
#### 1. lépés: Az előre elkészített binárisok letöltése

Navigáljon a legújabb kiadás oldalára, és töltse le a platformjának és GPU-céljának megfelelő archívumot:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Töltse le a `llama-bxxxx-windows-rocm-gfx1151-x64.zip` nevű fájlt (ahol az `xxxx` a build számát jelöli).

#### 2. lépés: A binárisok kicsomagolása

Csomagolja ki a letöltött archívumot:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Ez a könyvtár most már tartalmazza a `llama-cli.exe`, `llama-server.exe` és `ggml-rpc-server.exe` ROCm-képes buildjeit, amelyek előre le lettek fordítva az Ön Ryzen AI Halo rendszeréhez.

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

Navigáljon a legújabb kiadás oldalára, és töltse le a platformjának és GPU-céljának megfelelő archívumot:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Töltse le a `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` nevű fájlt (ahol az `xxxx` a build számát jelöli).

#### 2. lépés: A binárisok kicsomagolása és előkészítése

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Ez a könyvtár most már tartalmazza a `llama-cli`, `llama-server` és `rpc-server` ROCm-képes buildjeit, amelyek előre le lettek fordítva az Ön Ryzen AI Halo rendszeréhez.

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
Miután a llama.cpp elő van készítve minden csomóponton, folytassa a [Model letöltése](#downloading-the-model) résszel.

### 2. lehetőség: Manuális forrásból történő build

<!-- @os:windows -->
#### 1. lépés: A llama.cpp buildelése

Nyissa meg az **x64 Native Tools Command Prompt** ablakot (a Visual Studio Build Tools telepíti), és klónozza a repót:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Adja hozzá a HIP-et az elérési útjához, és buildeljen ROCm és RPC támogatással:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Build kapcsoló | Cél |
|-----------|---------|
| `-DGGML_HIP=ON` | Engedélyezi a ROCm/HIP szoftverstacket |
| `-DGGML_RPC=ON` | Engedélyezi az RPC-t az elosztott következtetéshez |
| `-DGPU_TARGETS=gfx1151` | A Ryzen AI Halo GPU-t (Radeon 8060s) célozza meg |
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

#### 3. lépés: A HIP hozzáadása a felhasználói elérési útjához

A fenti build lépés csak az aktuális munkamenetre állította be a `%HIP_PATH%\bin` értékét. Ahhoz, hogy a HIP könyvtárak bármely terminálban elérhetők legyenek (nem csak az x64 Native Tools Command Prompt-ban), adja hozzá véglegesen a felhasználói `PATH` változóhoz:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Miután a llama.cpp elő van készítve minden csomóponton, folytassa a [Model letöltése](#downloading-the-model) résszel.
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
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Build kapcsoló | Cél |
|-----------|---------|
| `-DGGML_HIP=ON` | Engedélyezi a ROCm szoftverstacket |
| `-DGGML_RPC=ON` | Engedélyezi az RPC-t az elosztott következtetéshez |
| `-DAMDGPU_TARGETS="gfx1151"` | A Ryzen AI Halo GPU-t (Radeon 8060s) célozza meg |

További build beállításokért tekintse meg a [llama.cpp build dokumentációját](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

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

Miután a llama.cpp elő van készítve minden csomóponton, folytassa a [Model letöltése](#downloading-the-model) résszel.
<!-- @os:end -->

## A modell letöltése

Ez a playbook a [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) modellt használja a `UD-Q2_K_XL` kvantálásban, az [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL) forrásból. Ez a kvantálás elfér négy Ryzen AI Halo csomópont együttes GPU-memóriájában.

Töltse le a GGUF fájlokat a Hugging Face CLI segítségével:
<!-- @os:linux -->
```bash
pip install huggingface-hub
hf download unsloth/Kimi-K2.6-GGUF --include "UD-Q2_K_XL/*" --local-dir Kimi-K2.6-GGUF
```
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/Kimi-K2.6-GGUF --include "UD-Q2_K_XL/*" --local-dir Kimi-K2.6-GGUF
```
<!-- @os:end -->

> **Megjegyzés**: A modell letöltését az 1. gépen (a vezérlőn) kell elvégezni. Az RPC munkavégző csomópontoknak (2., 3. és 4. gép) nincs szükségük a modellfájlok helyi másolatára.

## A modell elindítása a fürtön

A llama.cpp RPC (Remote Procedure Call) motor lehetővé teszi, hogy egyetlen llama.cpp példány a hálózaton keresztül távoli munkavégzőkre helyezze át a modell rétegeit. Az egyik gép **vezérlőként** (1. gép) működik, amely a tokenizálást, ütemezést és a folyamatszervezést végzi. A másik három gép mindegyike egy könnyűsúlyú **RPC szervert** futtat (2., 3. és 4. gép), amely a saját GPU-memóriáját és számítási kapacitását teszi elérhetővé a vezérlő számára.

Betöltéskor a llama.cpp a modellt mind a négy csomópont között particionálja. A betöltés után a következtetés úgy zajlik, mintha egyetlen gyorsítón futna. Az RPC a háttérben kezeli a tenzorátviteleket és a szinkronizációt.

### 1. lépés: Az RPC szerverek elindítása (2., 3. és 4. gép)

A 2., 3. és 4. gép mindegyikén indítsa el az RPC szervert, hogy elérhetővé tegye a GPU-erőforrásait a vezérlő számára:
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

| Kapcsoló | Cél |
|------|---------|
| `-p` | Az a port, amelyen az RPC szerver közvetít |
| `-c` | Engedélyezi a nagy tenzorok helyi gyorsítótárazását, elkerülve az ismételt hálózati átviteleket a modell betöltése során |
| `--host` | Az IP-cím, amelyhez az RPC szervert kötni kell (`0.0.0.0` az összes interfészhez) |

További lehetőségekért tekintse meg a [llama.cpp RPC dokumentációját](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### 2. lépés: A modell elindítása (1. gép)

Miután az RPC szerverek futnak a 2., 3. és 4. gépen, indítsa el a következtetést az 1. gépről a `llama-cli` vagy a `llama-server` segítségével.
#### llama-cli

A `llama-cli` egy terminálalapú felületet biztosít a modellel való közvetlen interakcióhoz. Ideális teljesítménymérésre, hibakeresésre és alacsony szintű kísérletezésre.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/Kimi-K2.6-GGUF/UD-Q2_K_XL/Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  -b 4096 \
  -ub 4096 \
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **A `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>` megkeresése**: A 2., 3. és 4. gépen futtassa le a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megkereséséhez.
<!-- @os:end -->

<!-- @os:windows -->
> **Megjegyzés**: Futtassa le ezt a parancsot a Terminálban (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\Kimi-K2.6-GGUF\UD-Q2_K_XL\Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  -b 4096 `
  -ub 4096 `
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **A `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>` megkeresése**: A 2., 3. és 4. gépen futtassa le az `ipconfig | findstr /C:"IPv4"` parancsot a Terminálban (Powershell) a helyi IP-cím megkereséséhez.

<!-- @os:end -->

Az elindítást követően a `llama-cli` megjeleníti a modell betöltésének folyamatát, majd egy interaktív parancssort nyit meg, ahol közvetlenül cseveghet a modellel:

![llama-cli futtatja a Kimi K2.6-ot négy csomóponton keresztül](assets/llama-cli-example.png)

#### llama-server

A `llama-server` ugyanazt a következtetési motort teszi elérhetővé egy állandó szerverfolyamaton keresztül, integrált webes felhasználói felülettel és OpenAI-kompatibilis HTTP API-val. Ez az előnyben részesített felület hosszabb ideig futó telepítésekhez, több felhasználós hozzáféréshez és külső eszközökkel való integrációhoz.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/Kimi-K2.6-GGUF/UD-Q2_K_XL/Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  -b 4096 \
  -ub 4096 \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **A `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>` megkeresése**: A 2., 3. és 4. gépen futtassa le a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megkereséséhez.
<!-- @os:end -->

<!-- @os:windows -->
> **Megjegyzés**: Futtassa le ezt a parancsot a Terminálban (Powershell).

```powershell
.\llama-server.exe `
  -m C:\path\to\Kimi-K2.6-GGUF\UD-Q2_K_XL\Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  -b 4096 `
  -ub 4096 `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **A `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>` megkeresése**: A 2., 3. és 4. gépen futtassa le az `ipconfig | findstr /C:"IPv4"` parancsot a Terminálban (Powershell) a helyi IP-cím megkereséséhez.
<!-- @os:end -->

Az indítást követően nyissa meg a `http://<HOST_IP>:8081` címet a böngészőjében a beépített webes felhasználói felület eléréséhez. Ez egy böngészőalapú csevegőfelületet biztosít a modellel való interakcióhoz:

![llama-server webes felhasználói felület futtatja a Kimi K2.6-ot négy csomóponton keresztül](assets/llama-server-example.png)

<!-- @os:linux -->
> **A `<HOST_IP>` megkeresése**: Az 1. gépen futtassa le a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megkereséséhez.
<!-- @os:end -->

<!-- @os:windows -->
> **A `<HOST_IP>` megkeresése**: Az 1. gépen futtassa le az `ipconfig | findstr /C:"IPv4"` parancsot a Terminálban (Powershell) a helyi IP-cím megkereséséhez.
<!-- @os:end -->

#### Paraméterreferencia

| Jelző | Cél |
|------|---------|
| `-m` | A GGUF modellfájl elérési útja (az első szeletet használja, `00001-of-00008`) |
| `-c` | Kontextusméret tokenekben. A nagyobb értékek több memóriát használnak |
| `-fa on` | Bekapcsolja a rocWMMA Flash Attention funkciót a jobb teljesítmény érdekében AMD GPU-kon |
| `-ngl 999` | A modell összes rétegét a GPU-ra tölti át |
| `-lm none` | A modell betöltési módját `none` értékre állítja, kikapcsolva a memórialeképezést, hogy csökkentse a betöltési időt, amikor a modell mérete meghaladja a rendszer RAM méretét, de elfér a VRAM-ban |
| `-b` | Logikai kötegméret tokenekben. A 4096-ra állítás egyensúlyt teremt az átviteli sebesség és a memóriahasználat között a csomópontok között |
| `-ub` | Fizikai (mikro) kötegméret a prompt feldolgozásához. A `-b` értékkel való egyeztetés elkerüli a felesleges darabolási többletterhelést |
| `--host` | Az az IP-cím, amelyhez a `llama-server` kötődik (csak `llama-server`) |
| `--port` | A HTTP API kiszolgálásához használt port (csak `llama-server`) |
| `--rpc` | Vesszővel elválasztott lista az RPC worker végpontokról (`IP:port`) |

A teljes paraméterhasználatért tekintse meg a [llama-cli dokumentációt](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) és a [llama-server dokumentációt](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Következő lépések

- **Harmadik féltől származó alkalmazások csatlakoztatása**: A `llama-server` egy OpenAI-kompatibilis API-t tesz elérhetővé. Irányítson bármely OpenAI-kompatibilis alkalmazást (például az Open WebUI-t) a `http://<HOST_IP>:8081` címre bármilyen helykitöltő API-kulccsal (pl. `none`), hogy csatlakozzon a fürtjéhez
- **Egyéb modellek felfedezése**: Böngésszen kvantált GGUF-okat a [Hugging Face](https://huggingface.co/models?search=gguf) oldalon, hogy olyan modelleket találjon, amelyek beleférnek a fürt kombinált GPU memóriájába
- **Bővítés négy csomóponton túl**: Adjon hozzá további Ryzen AI Halo rendszereket további RPC workerekként, hogy elérje az 1 billió paraméteres skálán túli modelleket. Adjon meg további végpontokat a `--rpc` paraméternek vesszővel elválasztott listaként (pl. `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)