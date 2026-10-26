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

# Négy Ryzen™ AI Halo fürtözése RPC-vel

## Áttekintés

A Ryzen™ AI Halo rendszer már önmagában is képes nagy nyelvi modellek helyi futtatására. A fürtözés ezt tovább fokozza azáltal, hogy több rendszer GPU-memóriáját kombinálja helyi hálózaton keresztül, így még nagyobb modellekhez férhet hozzá, amelyek erősebb következtetési képességgel, jobb kódgenerálással és mélyebb többnyelvű megértéssel rendelkeznek, mindezt teljes mértékben a saját hardverén.

Ez a útmutató megtanítja, hogyan fürtözzön négy Ryzen AI Halo rendszert a llama.cpp RPC motorjának használatával, és hogyan futtassa a Kimi K2.6-ot, egy nagy mixture-of-experts modellt mind a négy gépen AMD ROCm™ gyorsítással.

## Amit megtanulhat

- Hogyan bővítheti ki a VRAM-allokációt a Ryzen AI Halo rendszereken
- A llama.cpp telepítése ROCm és RPC támogatással
- RPC munkafolyamatok konfigurálása és elosztott következtetés indítása négy csomóponton
- Egy 1 billió paraméteres modell futtatása négy hálózatba kötött Ryzen AI Halo rendszeren

## A memóriakonfiguráció beállítása

> **Megjegyzés**: Ezt a lépést mind a négy gépen végezze el (1-4. gép).

<!-- @device:halo_box -->
<!-- @os:windows -->
> **128 GB közeli vagy afeletti modellek futtatása:** Az AMD Ryzen™ AI Max 400 sorozatú (Gorgon Halo) rendszereken, Windows alatt, azok a modellek, amelyek megközelítik vagy meghaladják a 128 GB memóriát, további konfigurációt igényelnek a hibamentes futtatáshoz. Kövesse az [AMD Ryzen AI Max PRO 400 Series Windows OS Guidelines](https://docs.amd.com/v/u/en-US/73342_1.00_AMD_Ryzen_AI_Max_PRO_400_Series_Windows_OS_Guidelines) útmutatót a modell betöltése előtt.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:windows -->
Windows alatt, nagyobb memóriaigényű modellek futtatásához az AMD Variable Graphics Memory (iGPU VRAM) allokációt kell használnunk.

Ezt az AMD Software: Adrenalin Edition vezérlőpult megnyitásával és a következő útvonalra navigálva teheti meg: `Performance > Tuning > AMD Variable Graphics Memory`. Állítsa az értéket **96 GB**-ra. Indítsa újra a rendszert, hogy a változtatások érvénybe lépjenek.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Linux alatt a ROCm egy megosztott rendszermemória-készletet használ, és ez a készlet alapértelmezés szerint a rendszermemória felére van konfigurálva.

Ez a mennyiség növelhető a kernel Translation Table Manager (TTM) lapméret-beállításának módosításával, az alábbi utasítások alapján. Az AMD azt javasolja, hogy a BIOS-ban állítsa be a minimális dedikált VRAM-ot (0,5 GB).

* Telepítse a pipx segédprogramot, és adja hozzá a pipx által telepített wheel-ek elérési útját a rendszer keresési útvonalához.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Telepítse az amd-debug-tools wheel-t a PyPI-ről.
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

* Indítsa újra a rendszert, hogy a változtatások érvénybe lépjenek.


<!-- @os:end -->
<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése

<!-- @require:software-update -->
<!-- @device:end -->
## Előfeltételek

### Hardver

Ehhez az útmutatóhoz négy Ryzen AI Halo egységre és egy Ethernet-switch-re van szükség, csillag topológiában összekötve, ahol minden egység közvetlenül a switch-hez van kötve.

| Komponens | Mennyiség | Leírás |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | A fürtöt alkotó számítási csomópontok |
| 10 Gbps-os Ethernet switch | 1 | Központi switch, amely lehetővé teszi a több Ryzen AI Halo csomópont közötti kommunikációt (legalább 4 port) |
| Ethernet-kábel | 4 | Minden Halo egységet a switch-hez csatlakoztat (Cat 7 vagy magasabb kategória ajánlott) |

> **Megjegyzés**: Négy Ethernet switch portra van szükség a négy Ryzen AI Halo egység csatlakoztatásához. Egy ötödik portra akkor van szükség, ha a modellt egy különálló kliens gépről éri el, nem pedig az egyik Halo egységről.

### Szoftver
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Telepítse a következőket:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) a **Desktop Development with C++** munkaterhelésssel
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Fizikai hardverbeállítás

> **Megjegyzés**: Ezt a lépést mind a négy gépen végezze el (1-4. gép).

Csatlakoztassa az egyes Ryzen AI Halo egységeket az Ethernet switch-hez egy Cat 7 (vagy magasabb kategóriájú) kábellel. Ez hozza létre a csomópontok közötti nagy sebességű kommunikációhoz használt 10 Gbps-os kapcsolatot.
<!-- @os:linux -->
### 1. A hálózati interfészek meghatározása

Minden gépen keresse meg a hálózati interfész nevét, és jegyezze fel (a továbbiakban `IFNAME`-ként hivatkozunk rá). Futtassa:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Ez közvetlenül kiírja az interfész nevét, például:

```bash
enp191s0
```

### 2. A hálózati kapcsolat sebességének ellenőrzése

Győződjön meg arról, hogy a kapcsolat aktív és teljes sebességgel működik, az interfész sebességének ellenőrzésével:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Megjegyzés**: Cserélje ki a `<IFNAME>` értéket az [1. A hálózati interfészek meghatározása](#1-determine-network-interfaces) pontban kapott kimeneti interfész névre

A sebességnek `10000Mb/s`-nak kell lennie:

```bash
	Speed: 10000Mb/s
```

> **Megjegyzés**: Ha a sebesség alacsonyabb, mint `10000Mb/s`, vagy a kapcsolat nem jön létre, ellenőrizze a kábelcsatlakozást, és győződjön meg arról, hogy a switch portja 10 Gbps-ra van állítva. Egyes switch-ek esetén az automatikus egyeztetést ki kell kapcsolni, és a kapcsolat sebességét manuálisan kell beállítani; tekintse meg a switch dokumentációját.

<!-- @os:end -->

<!-- @os:windows -->
### Hálózati kapcsolat sebességének ellenőrzése

Minden gépen ellenőrizze a hálózati interfészek kapcsolati sebességét:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Az Ethernet interfésznek `Up` állapotban kell lennie, és `10 Gbps` sebességgel kell futnia:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Megjegyzés**: Ha a sebesség alacsonyabb, mint `10 Gbps`, vagy a kapcsolat nem jön létre, ellenőrizze a kábelcsatlakozást, és győződjön meg arról, hogy a switch portja 10 Gbps-ra van állítva. Egyes switch-ek esetén az automatikus egyeztetést ki kell kapcsolni, és a kapcsolat sebességét manuálisan kell beállítani; tekintse meg a switch dokumentációját.

<!-- @os:end -->

## A llama.cpp telepítése

> **Megjegyzés**: Ezt a lépést mind a négy gépen végezze el (1-4. gép).

Két telepítési lehetőség áll rendelkezésre:

- [1. lehetőség: Lemonade SDK (Ajánlott)](#option-1-lemonade-sdk-recommended) - előre elkészített binárisok, leggyorsabb beállítás
- [2. lehetőség: Manuális forráskódból történő build](#option-2-manual-source-build) - forráskódból történő build teljes kontrollal a build jelzők felett
### 1. opció: Lemonade SDK (ajánlott)

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

Ez a könyvtár most már tartalmazza a `llama-cli.exe`, `llama-server.exe` és `ggml-rpc-server.exe` ROCm-képes buildjeit, előre lefordítva az Ön Ryzen AI Halo rendszeréhez.

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

Navigáljon a legújabb kiadás oldalára, és töltse le a platformjának és GPU-céljának megfelelő archívumot:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Töltse le a `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` nevű fájlt (ahol az `xxxx` a build számát jelöli).

#### 2. lépés: A binárisok kicsomagolása és előkészítése

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Ez a könyvtár most már tartalmazza a `llama-cli`, `llama-server` és `rpc-server` ROCm-képes buildjeit, előre lefordítva az Ön Ryzen AI Halo rendszeréhez.

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
Miután a llama.cpp minden csomóponton elő van készítve, folytassa [A modell letöltése](#downloading-the-model) résznél.

### 2. opció: Kézi forráskódból történő build

<!-- @os:windows -->
#### 1. lépés: A llama.cpp buildelése

Nyissa meg az **x64 Native Tools Command Prompt** ablakot (a Visual Studio Build Tools telepíti), és klónozza a repository-t:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Adja hozzá a HIP-et az elérési útvonalához, és buildeljen ROCm és RPC támogatással:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Build jelző | Cél |
|-----------|---------|
| `-DGGML_HIP=ON` | Engedélyezi a ROCm/HIP szoftverstack-et |
| `-DGGML_RPC=ON` | Engedélyezi az RPC-t az elosztott következtetéshez |
| `-DGPU_TARGETS=gfx1151` | A Ryzen AI Halo GPU-t célozza (Radeon 8060s) |
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

A fenti build lépés csak az aktuális munkamenetre állította be a `%HIP_PATH%\bin` útvonalat. Ahhoz, hogy a HIP könyvtárak bármely terminálban elérhetők legyenek (nemcsak az x64 Native Tools Command Promptban), adja hozzá tartósan a felhasználói `PATH` változóhoz:

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
| `-DGGML_HIP=ON` | Engedélyezi a ROCm szoftverstack-et |
| `-DGGML_RPC=ON` | Engedélyezi az RPC-t az elosztott következtetéshez |
| `-DAMDGPU_TARGETS="gfx1151"` | A Ryzen AI Halo GPU-t célozza (Radeon 8060s) |

További build opciókért tekintse meg a [llama.cpp build dokumentációt](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

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

Miután a llama.cpp minden csomóponton elő van készítve, folytassa [A modell letöltése](#downloading-the-model) résznél.
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

> **Megjegyzés**: A modell letöltését az 1. gépen (a vezérlőn) kell elvégezni. Az RPC munkavégző csomópontoknak (2., 3. és 4. gép) nincs szükségük a modellfájlok helyi másolatára.

## A modell elindítása a fürtön

A llama.cpp RPC (Remote Procedure Call) motor lehetővé teszi, hogy egyetlen llama.cpp példány a modell rétegeit távoli munkavégzőkre terhelje a hálózaton keresztül. Az egyik gép **vezérlőként** (1. gép) működik, és a tokenizálásért, az ütemezésért és az orkesztrálásért felel. A másik három gép mindegyike egy könnyű **RPC szervert** futtat (2., 3. és 4. gép), amely a GPU-memóriáját és számítási kapacitását a vezérlő számára elérhetővé teszi.

Betöltéskor a llama.cpp a modellt mind a négy csomópont között szétosztja. A betöltés után a következtetés úgy zajlik, mintha egyetlen gyorsítón futna. Az RPC a háttérben kezeli a tenzorátviteleket és a szinkronizációt.

### 1. lépés: Az RPC szerverek indítása (2., 3. és 4. gép)

A 2., 3. és 4. gép mindegyikén indítsa el az RPC szervert, hogy a GPU-erőforrásait elérhetővé tegye a vezérlő számára:
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
| `-p` | Az a port, amelyen az RPC szerver sugározni fog |
| `-c` | Engedélyezi a nagy tenzorok helyi gyorsítótárazását, elkerülve az ismételt hálózati átvitelt a modell betöltése közben |
| `--host` | Az az IP-cím, amelyhez az RPC szervert kötni kell (`0.0.0.0` minden interfészhez) |

További opciókért tekintse meg a [llama.cpp RPC dokumentációt](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

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

> **`<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>` megkeresése**: A 2., 3. és 4. gépen futtassa a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megállapításához.
<!-- @os:end -->

<!-- @os:windows -->
> **Megjegyzés**: Futtassa ezt a parancsot Terminálban (Powershell).

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

> **`<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>` megkeresése**: A 2., 3. és 4. gépen futtassa az `ipconfig | findstr /C:"IPv4"` parancsot Terminálban (Powershell) a helyi IP-cím megállapításához.

<!-- @os:end -->

A futás megkezdése után a `llama-cli` megjeleníti a modell betöltésének folyamatát, majd belép egy interaktív promptba, ahol közvetlenül cseveghet a modellel:

![llama-cli futtatja a Kimi K2.6-ot négy csomóponton](assets/llama-cli-example.png)

#### llama-server

A `llama-server` ugyanazt a következtetési motort teszi elérhetővé egy állandó szerverfolyamaton keresztül, integrált webes felhasználói felülettel és OpenAI-kompatibilis HTTP API-val. Ez a preferált felület hosszabb ideig futó üzemeltetésekhez, több felhasználós hozzáféréshez és külső eszközökkel való integrációhoz.

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

> **`<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>` megkeresése**: A 2., 3. és 4. gépen futtassa a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megállapításához.
<!-- @os:end -->

<!-- @os:windows -->
> **Megjegyzés**: Futtassa ezt a parancsot Terminálban (Powershell).

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

> **`<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>` megkeresése**: A 2., 3. és 4. gépen futtassa az `ipconfig | findstr /C:"IPv4"` parancsot Terminálban (Powershell) a helyi IP-cím megállapításához.
<!-- @os:end -->

Az indítás után nyissa meg a `http://<HOST_IP>:8081` címet a böngészőjében, hogy hozzáférjen a beépített webes felhasználói felülethez. Ez egy böngészőalapú csevegőfelületet biztosít a modellel való interakcióhoz:

![llama-server webes felhasználói felület a Kimi K2.6-ot futtatva négy csomóponton](assets/llama-server-example.png)

<!-- @os:linux -->
> **`<HOST_IP>` megkeresése**: Az 1. gépen futtassa a `hostname -I | awk '{print $1}'` parancsot a helyi IP-cím megállapításához.
<!-- @os:end -->

<!-- @os:windows -->
> **`<HOST_IP>` megkeresése**: Az 1. gépen futtassa az `ipconfig | findstr /C:"IPv4"` parancsot Terminálban (Powershell) a helyi IP-cím megállapításához.
<!-- @os:end -->

#### Paraméter-referencia

| Jelző | Cél |
|------|---------|
| `-m` | A GGUF modellfájl elérési útja (használja az első szegmenst, `00001-of-00008`) |
| `-c` | Kontextusméret tokenekben. A nagyobb értékek több memóriát használnak |
| `-fa on` | Engedélyezi a rocWMMA Flash Attention funkciót a jobb teljesítmény érdekében AMD GPU-kon |
| `-ngl 999` | Az összes modellréteget áthelyezi a GPU-ra |
| `-lm none` | A modell betöltési módját `none` értékre állítja, letiltva a memória-leképezést, hogy csökkentse a betöltési időt, ha a modell mérete meghaladja a rendszermemóriát, de elfér a VRAM-ban |
| `-b` | Logikai kötegméret tokenekben. A 4096-ra állítás egyensúlyt teremt az átviteli sebesség és a memóriahasználat között a csomópontok között |
| `-ub` | Fizikai (mikro) kötegméret a prompt feldolgozásához. A `-b` értékkel való egyeztetés elkerüli a felesleges darabolási többletterhelést |
| `--host` | Az IP-cím, amelyhez a `llama-server`-t kötni kell (csak `llama-server`) |
| `--port` | A port, amelyen a HTTP API elérhető lesz (csak `llama-server`) |
| `--rpc` | Vesszővel elválasztott lista az RPC worker végpontokról (`IP:port`) |

A paraméterek teljes körű használatához tekintse meg a [llama-cli dokumentációt](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) és a [llama-server dokumentációt](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Következő lépések

- **Harmadik féltől származó alkalmazások csatlakoztatása**: A `llama-server` egy OpenAI-kompatibilis API-t tesz elérhetővé. Irányítson bármely OpenAI-kompatibilis alkalmazást (például Open WebUI) a `http://<HOST_IP>:8081` címre bármilyen helyőrző API-kulccsal (pl. `none`), hogy csatlakozzon a fürtjéhez
- **További modellek felfedezése**: Böngésszen kvantált GGUF-ok között a [Hugging Face](https://huggingface.co/models?search=gguf) oldalon, hogy olyan modelleket találjon, amelyek beleférnek a fürt kombinált GPU-memóriájába
- **Négy csomóponton túli skálázás**: Adjon hozzá további Ryzen AI Halo rendszereket további RPC worker-ekként, hogy 1 billió paraméteres skálán túli modellekhez férjen hozzá. Adjon meg további végpontokat a `--rpc` paraméterhez vesszővel elválasztott listaként (pl. `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)