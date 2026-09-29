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

# Négy Ryzen™ AI Halo klaszterezése RPC segítségével

## Áttekintés

Az Ön Ryzen™ AI Halo rendszere már önmagában is képes nagy nyelvi modellek helyi futtatására. A klaszterezés ezt tovább viszi azáltal, hogy több rendszer GPU memóriáját egyesíti helyi hálózaton keresztül, így akár még nagyobb modellekhez is hozzáférhet, amelyek erősebb következtetési képességekkel, jobb kódgenerálással és mélyebb többnyelvű megértéssel rendelkeznek, mindezt teljes egészében a saját hardverén.

Ez az útmutató megtanítja Önnek, hogyan klaszterezzen négy Ryzen AI Halo rendszert a llama.cpp RPC motorjának segítségével, és hogyan futtassa a Kimi K2.6-ot, egy nagy mixture-of-experts modellt mind a négy gépen, AMD ROCm™ gyorsítással.

## Amit meg fog tanulni

- Hogyan bővítheti a VRAM allokációt Ryzen AI Halo rendszereken
- A llama.cpp telepítése ROCm és RPC támogatással
- RPC munkafolyamatok konfigurálása és elosztott következtetés indítása négy csomóponton keresztül
- Egy 1T paraméteres modell futtatása négy hálózatba kötött Ryzen AI Halo rendszeren

## A memória konfiguráció beállítása

> **Megjegyzés**: Ezt a lépést mind a négy gépen végezze el (1. géptől a 4. gépig).

<!-- @os:windows -->
Windows rendszeren, a nagyobb memóriaigényű, nagyobb modellek futtatásához az AMD Variable Graphics Memory (iGPU VRAM) allokációt kell használnunk.

Ez az AMD Software: Adrenalin Edition vezérlőpult megnyitásával és a következő útvonalra navigálással végezhető el: `Performance > Tuning > AMD Variable Graphics Memory`. Állítsa az értéket **96 GB**-ra. Kérjük, indítsa újra a rendszert, hogy a változtatások érvénybe lépjenek.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Linux rendszeren a ROCm egy megosztott rendszermemória-készletet használ, amely alapértelmezés szerint a rendszermemória felére van konfigurálva.

Ez a mennyiség növelhető a kernel Translation Table Manager (TTM) lapbeállításának módosításával, az alábbi utasítások szerint. Az AMD azt javasolja, hogy a BIOS-ban állítsa be a minimális dedikált VRAM-ot (0,5 GB).

* Telepítse a pipx segédprogramot, és adja hozzá a pipx által telepített wheel-ek elérési útját a rendszer keresési útvonalához.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Telepítse az amd-debug-tools wheel-t a PyPI-ból.
  ```bash
  pipx install amd-debug-tools
  ```

* Futtassa az amd-ttm eszközt a megosztott memória jelenlegi beállításainak lekérdezéséhez.
  ```bash
  amd-ttm
  ```

* Konfigurálja át a megosztott memória beállításait **120 GB**-ra:
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

Ehhez az útmutatóhoz négy Ryzen AI Halo egységre és egy Ethernet switch-re van szükség, csillag topológiában összekapcsolva, ahol minden egység közvetlenül a switch-hez van kötve.

| Komponens | Mennyiség | Leírás |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | A klasztert alkotó számítási csomópontok |
| 10 Gbps Ethernet switch | 1 | Központi switch a több csomópontos Ryzen AI Halo kommunikáció lehetővé tételéhez (legalább 4 port) |
| Ethernet kábel | 4 | Az egyes Halo egységeket köti össze a switch-csel (Cat 7 vagy magasabb ajánlott) |

> **Megjegyzés**: Négy Ethernet switch portra van szükség a négy Ryzen AI Halo egység csatlakoztatásához. Egy ötödik portra van szükség, ha egy különálló kliens gépről éri el a modellt, nem pedig az egyik Halo egységről.

### Szoftver
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Kérjük, telepítse a következőket:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) a **Desktop Development with C++** munkaterheléssel
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fizikai hardver beállítása

> **Megjegyzés**: Ezt a lépést mind a négy gépen végezze el (1. géptől a 4. gépig).

Csatlakoztassa az egyes Ryzen AI Halo egységeket az Ethernet switch-hez egy Cat 7 (vagy magasabb) kábel segítségével. Ez hozza létre a 10 Gbps-os kapcsolatot, amelyet a csomópontok közötti nagysebességű kommunikációhoz használnak.
<!-- @os:linux -->
### 1. Hálózati interfészek meghatározása

Minden egyes gépen keresse meg a hálózati interfész nevét, és jegyezze fel (a továbbiakban `IFNAME` néven hivatkozunk rá). Futtassa:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Ez közvetlenül kiírja az interfész nevét, például:

```bash
enp191s0
```

### 2. A hálózati kapcsolat sebességének ellenőrzése

Győződjön meg arról, hogy a kapcsolat aktív, és teljes sebességgel fut, ellenőrizve az interfész sebességét:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Megjegyzés**: Cserélje ki a `<IFNAME>` értéket az [1. Hálózati interfészek meghatározása](#1-determine-network-interfaces) szakaszból kapott kimeneti interfész névre

Egy `10000Mb/s` sebességet kell látnia:

```bash
	Speed: 10000Mb/s
```

> **Megjegyzés**: Ha a sebesség alacsonyabb, mint `10000Mb/s`, vagy a kapcsolat nem jön létre, ellenőrizze a kábelcsatlakozást, és győződjön meg róla, hogy a switch port 10 Gbps-re van állítva. Egyes switch-ek esetén ki kell kapcsolni az automatikus egyeztetést, és a kapcsolat sebességét manuálisan kell beállítani; ehhez tekintse meg a switch dokumentációját.

<!-- @os:end -->

<!-- @os:windows -->
### Hálózati kapcsolat sebességének ellenőrzése

Minden egyes gépen ellenőrizze a hálózati interfészek kapcsolatsebességét:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Az Ethernet interfésznek `Up` állapotúnak kell lennie, és `10 Gbps` sebességgel kell futnia:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Megjegyzés**: Ha a sebesség alacsonyabb, mint `10 Gbps`, vagy a kapcsolat nem jön létre, ellenőrizze a kábelcsatlakozást, és győződjön meg róla, hogy a switch port 10 Gbps-re van állítva. Egyes switch-ek esetén ki kell kapcsolni az automatikus egyeztetést, és a kapcsolat sebességét manuálisan kell beállítani; ehhez tekintse meg a switch dokumentációját.

<!-- @os:end -->

## A llama.cpp telepítése

> **Megjegyzés**: Ezt a lépést mind a négy gépen végezze el (1. géptől a 4. gépig).

Két telepítési lehetőség áll rendelkezésre:

- [1. lehetőség: Lemonade SDK (Ajánlott)](#option-1-lemonade-sdk-recommended) - előre elkészített binárisok, leggyorsabb beállítás
- [2. lehetőség: Manuális forráskódból történő build](#option-2-manual-source-build) - build forráskódból, teljes kontrollal a build jelzők felett

### 1. lehetőség: Lemonade SDK (Ajánlott)

A Lemonade SDK éjszakai build-eket biztosít a llama.cpp-hez AMD ROCm 7 gyorsítással, olyan GPU-kat célozva meg, mint a gfx1151 (Strix Halo / Ryzen AI Max+ 395) és más újabb Radeon architektúrák.

<!-- @os:windows -->
#### 1. lépés: Az előre elkészített binárisok letöltése

Navigáljon a legutóbbi kiadás oldalára, és töltse le a platformjának és GPU-célpontjának megfelelő archívumot:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Töltse le a `llama-bxxxx-windows-rocm-gfx1151-x64.zip` nevű fájlt (ahol az `xxxx` a build számát jelöli).

#### 2. lépés: A binárisok kicsomagolása

Csomagolja ki a letöltött archívumot:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Ez a könyvtár mostantól a `llama-cli.exe`, a `llama-server.exe` és a `ggml-rpc-server.exe` ROCm-alapú buildjeit tartalmazza, amelyek a Ryzen AI Halo rendszerére vannak előre lefordítva.

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

Navigáljon a legutóbbi kiadás oldalára, és töltse le a platformjának és GPU-célpontjának megfelelő archívumot:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Töltse le a `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` nevű fájlt (ahol az `xxxx` a build számát jelöli).

#### 2. lépés: A binárisok kicsomagolása és előkészítése

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Ez a könyvtár mostantól a `llama-cli`, a `llama-server` és a `rpc-server` ROCm-alapú buildjeit tartalmazza, amelyek a Ryzen AI Halo rendszerére vannak előre lefordítva.

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
Miután a llama.cpp minden csomóponton elő van készítve, folytassa a [Modell letöltése](#downloading-the-model) résznél.

### 2. lehetőség: Manuális forrásból történő build

<!-- @os:windows -->
#### 1. lépés: A llama.cpp buildelése

Nyissa meg az **x64 Native Tools Command Prompt** parancssort (a Visual Studio Build Tools telepíti), és klónozza a tárolót:

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

A fenti build lépés csak az aktuális munkamenetre állította be a `%HIP_PATH%\bin` értéket. Ahhoz, hogy a HIP könyvtárak bármely terminálban elérhetők legyenek (nem csak az x64 Native Tools Command Promptban), adja hozzá véglegesen a felhasználói `PATH` változóhoz:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Miután a llama.cpp minden csomóponton elő van készítve, folytassa a [Modell letöltése](#downloading-the-model) résznél.
<!-- @os:end -->

<!-- @os:linux -->
#### 1. lépés: A llama.cpp buildelése

Klónozza a tárolót:

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
| `-DGGML_HIP=ON` | Engedélyezi a ROCm szoftverkészletet |
| `-DGGML_RPC=ON` | Engedélyezi az RPC-t az elosztott következtetéshez |
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

Miután a llama.cpp minden csomóponton elő van készítve, folytassa a [Modell letöltése](#downloading-the-model) résznél.
<!-- @os:end -->

## A modell letöltése

Ez a playbook a [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) modellt használja `UD-Q2_K_XL` kvantálásban, az [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL) forrásból. Ez a kvantálás elfér négy Ryzen AI Halo csomópont összesített GPU-memóriájában.

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

> **Megjegyzés**: A modell letöltését az 1. gépen (a vezérlőn) kell elvégezni. Az RPC worker csomópontoknak (2., 3. és 4. gép) nincs szükségük a modellfájlok helyi másolatára.

## A modell elindítása a klaszteren

A llama.cpp RPC (Remote Procedure Call) motor lehetővé teszi, hogy egyetlen llama.cpp példány kihelyezze a modell rétegeit a hálózaton keresztül távoli workerekre. Az egyik gép **vezérlőként** (1. gép) működik, és a tokenizálást, ütemezést és orkesztrálást végzi. A másik három gép mindegyike egy könnyű **RPC szervert** futtat (2., 3. és 4. gép), amely elérhetővé teszi a GPU-memóriáját és számítási kapacitását a vezérlő számára.

Betöltéskor a llama.cpp az összes négy csomóponton szétosztja a modellt. A betöltés után a következtetés úgy zajlik, mintha egyetlen gyorsítón futna. Az RPC a háttérben kezeli a tenzorátviteleket és a szinkronizációt.

### 1. lépés: Az RPC szerverek elindítása (2., 3. és 4. gép)

A 2., 3. és 4. gépen egyenként indítsa el az RPC szervert, hogy elérhetővé tegye a GPU-erőforrásait a vezérlő számára:
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
| `-p` | A port, amelyen az RPC szerver közvetít |
| `-c` | Engedélyezi a helyi gyorsítótárat a nagy tenzorokhoz, elkerülve az ismételt hálózati átviteleket a modell betöltése során |
| `--host` | Az IP-cím, amelyhez az RPC szerver kötődik (`0.0.0.0` az összes interfészhez) |

További beállításokért tekintse meg a [llama.cpp RPC dokumentációját](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### 2. lépés: A modell elindítása (1. gép)

Miután az RPC szerverek futnak a 2., 3. és 4. gépen, indítsa el a következtetést az 1. gépről a `llama-cli` vagy a `llama-server` használatával.
#### llama-cli

A `llama-cli` egy terminálalapú felületet biztosít a modellel való közvetlen interakcióhoz. Ideális teljesítménytesztekhez, hibakereséshez és alacsony szintű kísérletezéshez.

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

> **A `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>` megkeresése**: A 2., 3. és 4. gépen futtassa a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megkereséséhez.
<!-- @os:end -->

<!-- @os:windows -->
> **Megjegyzés**: Ezt a parancsot terminálban (Powershell) futtassa.

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

> **A `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>` megkeresése**: A 2., 3. és 4. gépen futtassa az `ipconfig | findstr /C:"IPv4"` parancsot terminálban (Powershell) a helyi IP-cím megkereséséhez.

<!-- @os:end -->

Elindulás után a `llama-cli` megjeleníti a modell betöltésének folyamatát, majd belép egy interaktív parancssorba, ahol közvetlenül cseveghet a modellel:

![llama-cli a Kimi K2.6 modellt futtatja négy csomóponton keresztül](assets/llama-cli-example.png)

#### llama-server

A `llama-server` ugyanazt a következtetési motort teszi elérhetővé egy tartós szerverfolyamaton keresztül, integrált webes felhasználói felülettel és OpenAI-kompatibilis HTTP API-val. Ez az előnyben részesített felület a hosszabb ideig futó telepítésekhez, a több felhasználós hozzáféréshez és a külső eszközökkel való integrációhoz.

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

> **A `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>` megkeresése**: A 2., 3. és 4. gépen futtassa a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megkereséséhez.
<!-- @os:end -->

<!-- @os:windows -->
> **Megjegyzés**: Ezt a parancsot terminálban (Powershell) futtassa.

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

> **A `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>` megkeresése**: A 2., 3. és 4. gépen futtassa az `ipconfig | findstr /C:"IPv4"` parancsot terminálban (Powershell) a helyi IP-cím megkereséséhez.
<!-- @os:end -->

Az elindítás után nyissa meg a `http://<HOST_IP>:8081` címet a böngészőjében a beépített webes felhasználói felület eléréséhez. Ez egy böngészőalapú csevegőfelületet biztosít a modellel való interakcióhoz:

![llama-server webes felhasználói felület a Kimi K2.6 modellt futtatja négy csomóponton keresztül](assets/llama-server-example.png)

<!-- @os:linux -->
> **A `<HOST_IP>` megkeresése**: Az 1. gépen futtassa a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megkereséséhez.
<!-- @os:end -->

<!-- @os:windows -->
> **A `<HOST_IP>` megkeresése**: Az 1. gépen futtassa az `ipconfig | findstr /C:"IPv4"` parancsot terminálban (Powershell) a helyi IP-cím megkereséséhez.
<!-- @os:end -->

#### Paraméterek referenciája

| Jelölő | Cél |
|------|---------|
| `-m` | A GGUF modellfájl elérési útja (az első szeletet használja, `00001-of-00008`) |
| `-c` | Kontextusméret tokenben. A nagyobb értékek több memóriát használnak |
| `-fa on` | Engedélyezi a rocWMMA Flash Attention funkciót a jobb teljesítmény érdekében AMD GPU-kon |
| `-ngl 999` | Az összes modellréteget áthelyezi a GPU-ra |
| `-lm none` | A modell betöltési módját `none` értékre állítja, letiltva a memóriaképzést, ami csökkenti a betöltési időt, ha a modell mérete meghaladja a rendszer RAM-ját, de elfér a VRAM-ban |
| `-b` | Logikai kötegméret tokenben. A 4096-ra állítás egyensúlyt teremt az átviteli sebesség és a memóriahasználat között a csomópontok között |
| `-ub` | Fizikai (mikro) kötegméret a prompt feldolgozásához. A `-b` értékkel való egyezés elkerüli a felesleges darabolási többletterhelést |
| `--host` | Az az IP-cím, amelyhez a `llama-server` kötődik (kizárólag `llama-server` esetén) |
| `--port` | A HTTP API kiszolgálásához használt port (kizárólag `llama-server` esetén) |
| `--rpc` | Vesszővel elválasztott lista az RPC worker végpontokról (`IP:port`) |

A paraméterek teljes körű használatáról a [llama-cli dokumentációban](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) és a [llama-server dokumentációban](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md) tájékozódhat.

## Következő lépések

- **Harmadik féltől származó alkalmazások csatlakoztatása**: A `llama-server` egy OpenAI-kompatibilis API-t tesz elérhetővé. Irányítson bármely OpenAI-kompatibilis alkalmazást (például az Open WebUI-t) a `http://<HOST_IP>:8081` címre bármilyen helyőrző API-kulccsal (pl. `none`) a klaszterhez való csatlakozáshoz
- **Más modellek felfedezése**: Böngésszen kvantált GGUF-modellek között a [Hugging Face](https://huggingface.co/models?search=gguf) oldalon, hogy olyan modelleket találjon, amelyek elférnek a klaszter együttes GPU-memóriájában
- **Bővítés négy csomóponton túl**: Adjon hozzá további Ryzen AI Halo rendszereket kiegészítő RPC worker-ekként, hogy 1 billió paraméter feletti modellekhez is hozzáférjen. Adjon meg további végpontokat a `--rpc` paraméterhez vesszővel elválasztott listaként (pl. `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)