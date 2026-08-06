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

# Két Ryzen™ AI Halo klaszterezése RPC-vel

## Áttekintés

Az Ön Ryzen™ AI Halo rendszere már önmagában is képes nagy nyelvi modellek helyi futtatására. A klaszterezés ezt viszi tovább azáltal, hogy több rendszer GPU memóriáját kombinálja egy helyi hálózaton keresztül, így Ön még nagyobb modellekhez férhet hozzá, erősebb következtetési képességekkel, jobb kódgenerálással és mélyebb többnyelvű megértéssel – mindezt kizárólag a saját hardverén.

Ez az útmutató megtanítja, hogyan lehet két Ryzen AI Halo rendszert klaszterbe rendezni a llama.cpp RPC motorjának használatával, és hogyan futtathatja a GLM 4.7-et, egy 358 milliárd paraméteres modellt, mindkét gépen egyszerre, AMD ROCm™ gyorsítással.

## Amit meg fog tanulni

- Hogyan bővítheti a VRAM-kiosztást Ryzen AI Halo rendszereken
- A llama.cpp telepítése ROCm és RPC támogatással
- Egy RPC munkás konfigurálása és elosztott következtetés indítása két csomóponton
- Egy 358 milliárd paraméteres modell futtatása két hálózatba kötött Ryzen AI Halo rendszeren

## A memóriakonfiguráció beállítása

> **Megjegyzés**: Ezt a lépést mindkét gépen, az 1. és a 2. gépen is végezze el.

<!-- @os:windows -->
Windows alatt, a nagyobb memóriaigényű modellek futtatásához az AMD Variable Graphics Memory (iGPU VRAM) kiosztást kell használnunk.

Ez az AMD Software: Adrenalin Edition vezérlőpult megnyitásával és a `Performance > Tuning > AMD Variable Graphics Memory` menüpontra navigálva tehető meg. Állítsa az értéket **96 GB**-ra. A módosítások érvénybe lépéséhez indítsa újra a rendszert.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Linux alatt a ROCm egy megosztott rendszermemória-készletet használ, amely alapértelmezés szerint a rendszermemória felére van beállítva.

Ez a mennyiség növelhető a kernel Translation Table Manager (TTM) lapbeállításának módosításával, az alábbi utasítások segítségével. Az AMD azt javasolja, hogy a BIOS-ban állítsa be a minimális dedikált VRAM-ot (0,5 GB).

* Telepítse a pipx segédprogramot, és adja hozzá a pipx által telepített csomagok elérési útját a rendszer keresési útvonalához.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Telepítse az amd-debug-tools csomagot a PyPI-ról.
  ```bash
  pipx install amd-debug-tools
  ```

* Futtassa az amd-ttm eszközt a megosztott memória aktuális beállításainak lekérdezéséhez.
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

Ez az útmutató két Ryzen AI Halo egységet és egy Ethernet-kapcsolót igényel, csillag topológiában összekapcsolva, minden egységet közvetlenül a kapcsolóhoz csatlakoztatva.

| Összetevő | Mennyiség | Leírás |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | A klasztert alkotó számítási csomópontok |
| 10 Gbps-os Ethernet-kapcsoló | 1 | Központi kapcsoló, amely lehetővé teszi a több csomópontos Ryzen AI Halo kommunikációt (legalább 2 port) |
| Ethernet-kábel | 2 | Az egyes Halo egységeket köti össze a kapcsolóval (Cat 7 vagy magasabb ajánlott) |

> **Megjegyzés**: Két Ethernet-kapcsolóportra van szükség a két Ryzen AI Halo egység összekapcsolásához. Egy harmadik port akkor szükséges, ha a modellhez egy különálló kliensgépről szeretne hozzáférni, nem pedig az egyik Halo egységről.

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

## Fizikai hardverbeállítás

> **Megjegyzés**: Ezt a lépést mindkét gépen, az 1. és a 2. gépen is végezze el.

Csatlakoztassa mindkét Ryzen AI Halo egységet az Ethernet-kapcsolóhoz Cat 7 (vagy magasabb) kábel segítségével. Ez hozza létre a nagysebességű 10 Gbps-os kapcsolatot, amelyet a csomópontok közötti kommunikáció használ.
<!-- @os:linux -->
### 1. Hálózati interfészek meghatározása

Mindkét gépen keresse meg a hálózati interfész nevét, és jegyezze fel (a továbbiakban `IFNAME` néven hivatkozunk rá). Futtassa:

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

> **Megjegyzés**: Cserélje ki a `<IFNAME>` értéket az [1. Hálózati interfészek meghatározása](#1-determine-network-interfaces) fejezetből kapott interfész névre.

A sebességnek `10000Mb/s`-nak kell lennie:

```bash
	Speed: 10000Mb/s
```

> **Megjegyzés**: Ha a sebesség alacsonyabb, mint `10000Mb/s`, vagy a kapcsolat nem jön létre, ellenőrizze a kábelcsatlakozást, és győződjön meg arról, hogy a kapcsolóport 10 Gbps-ra van beállítva. Egyes kapcsolóknál ki kell kapcsolni az automatikus egyeztetést, és manuálisan kell beállítani a kapcsolat sebességét; ehhez tekintse meg a kapcsoló dokumentációját.

<!-- @os:end -->

<!-- @os:windows -->
### Hálózati kapcsolat sebességének ellenőrzése

Mindkét gépen ellenőrizze a hálózati interfészek kapcsolatsebességét:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Az Ethernet-interfésznek `Up` állapotban kell lennie, és `10 Gbps` sebességgel kell futnia:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Megjegyzés**: Ha a sebesség alacsonyabb, mint `10 Gbps`, vagy a kapcsolat nem jön létre, ellenőrizze a kábelcsatlakozást, és győződjön meg arról, hogy a kapcsolóport 10 Gbps-ra van beállítva. Egyes kapcsolóknál ki kell kapcsolni az automatikus egyeztetést, és manuálisan kell beállítani a kapcsolat sebességét; ehhez tekintse meg a kapcsoló dokumentációját.

<!-- @os:end -->

## A llama.cpp telepítése

> **Megjegyzés**: Ezt a lépést mindkét gépen, az 1. és a 2. gépen is végezze el.

Két telepítési lehetőség áll rendelkezésre:

- [1. lehetőség: Lemonade SDK (Ajánlott)](#option-1-lemonade-sdk-recommended) - előre elkészített binárisok, leggyorsabb beállítás
- [2. lehetőség: Manuális forráskódból történő build](#option-2-manual-source-build) - build forráskódból, teljes kontrollal a build jelzők felett

### 1. lehetőség: Lemonade SDK (Ajánlott)

A Lemonade SDK éjszakai buildeket biztosít a llama.cpp-ből AMD ROCm 7 gyorsítással, olyan GPU-kat célozva meg, mint a gfx1151 (Strix Halo / Ryzen AI Max+ 395) és más újabb Radeon architektúrák.

<!-- @os:windows -->
#### Step 1: Előre elkészített binárisok letöltése

Navigáljon a legfrissebb kiadás oldalára, és töltse le a platformjának és GPU-célpontjának megfelelő archívumot:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Töltse le a `llama-bxxxx-windows-rocm-gfx1151-x64.zip` nevű fájlt (ahol az `xxxx` a build számát jelöli).

#### Step 2: Binárisok kicsomagolása

Csomagolja ki a letöltött archívumot:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Ez a könyvtár most már tartalmazza a `llama-cli.exe`, `llama-server.exe` és `rpc-server.exe` ROCm-képes buildjeit, amelyeket előre lefordítottak az Ön Ryzen AI Halo rendszeréhez.

#### Step 3: GPU-felismerés ellenőrzése

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
#### Step 1: Előre elkészített binárisok letöltése

Navigáljon a legfrissebb kiadás oldalára, és töltse le a platformjának és GPU-célpontjának megfelelő archívumot:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Töltse le a `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` nevű fájlt (ahol az `xxxx` a build számát jelöli).

#### Step 2: Binárisok kicsomagolása és előkészítése

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Ez a könyvtár most már tartalmazza a `llama-cli`, `llama-server` és `rpc-server` ROCm-képes buildjeit, amelyeket előre lefordítottak az Ön Ryzen AI Halo rendszeréhez.

#### Step 3: GPU-felismerés ellenőrzése

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
Miután a llama.cpp elő van készítve minden csomóponton, folytassa a [Modell letöltése](#downloading-the-model) résznél.

### 2. lehetőség: Manuális forrásból történő build

<!-- @os:windows -->
#### Step 1: A llama.cpp buildelése

Nyissa meg az **x64 Native Tools Command Prompt**-ot (a Visual Studio Build Tools-szal telepítve), és klónozza a tárolót:

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

| Build jelző | Cél |
|-----------|---------|
| `-DGGML_HIP=ON` | Engedélyezi a ROCm/HIP szoftverkészletet |
| `-DGGML_RPC=ON` | Engedélyezi az RPC-t az elosztott következtetéshez |
| `-DGPU_TARGETS=gfx1151` | A Ryzen AI Halo GPU-t (Radeon 8060s) célozza meg |
| `-G Ninja` | A Ninja build rendszert használja |

#### Step 2: GPU-felismerés ellenőrzése

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

#### Step 3: A HIP hozzáadása a felhasználói elérési úthoz

A fenti build lépés csak az aktuális munkamenetre állította be a `%HIP_PATH%\bin` értéket. Ahhoz, hogy a HIP könyvtárak bármely terminálban elérhetők legyenek (nem csak az x64 Native Tools Command Prompt-ban), adja hozzá véglegesen a felhasználói `PATH` értékéhez:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Miután a llama.cpp elő van készítve minden csomóponton, folytassa a [Modell letöltése](#downloading-the-model) résznél.
<!-- @os:end -->

<!-- @os:linux -->
#### Step 1: A llama.cpp buildelése

Klónozza a tárolót:

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
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Engedélyezi a rocWMMA-t a fokozott Flash Attention-höz az AMD GPU-kon |
| `-DAMDGPU_TARGETS="gfx1151"` | A Ryzen AI Halo GPU-t (Radeon 8060s) célozza meg |

További build opciókért tekintse meg a [llama.cpp build dokumentációját](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Step 2: GPU-felismerés ellenőrzése

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

Miután a llama.cpp elő van készítve minden csomóponton, folytassa a [Modell letöltése](#downloading-the-model) résznél.
<!-- @os:end -->

## A modell letöltése

Ez a segédlet a [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7) modellt használja, amely egy 358 milliárd paraméteres modell `Q4_K_XL` kvantálásban, az [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL) által biztosítva. Ezen a kvantáláson a modell körülbelül 205 GB tárhelyet igényel, és beleférnek két Ryzen AI Halo csomópont GPU-memóriájának összesített kapacitásába.

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

> **Megjegyzés**: A modell letöltését az 1. gépen (a vezérlőn) kell befejezni. Az RPC munkavállaló csomópontoknak nincs szükségük a modellfájlok helyi másolatára.

## A modell elindítása a fürtön

A llama.cpp RPC (Remote Procedure Call) motor lehetővé teszi, hogy egyetlen llama.cpp példány a modell rétegeit távoli munkavállalóknak töltse át a hálózaton keresztül. Az egyik gép **vezérlőként** (1. gép) működik, amely a tokenizálást, ütemezést és orkesztrálást végzi. A másik gép egy könnyűsúlyú **RPC szervert** (2. gép) futtat, amely a GPU-memóriáját és számítási kapacitását teszi elérhetővé a vezérlő számára.

Betöltéskor a llama.cpp a modellt mindkét csomópont között felosztja. A betöltés után a következtetés úgy zajlik, mintha egyetlen gyorsítón futna. Az RPC a háttérben kezeli a tenzorátviteleket és a szinkronizálást.

### Step 1: Az RPC szerver elindítása (2. gép)

A 2. gépen indítsa el az RPC szervert, hogy elérhetővé tegye annak GPU-erőforrásait a vezérlő számára:
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
| `-p` | Az a port, amelyen az RPC szerver közvetít |
| `-c` | Engedélyezi a nagy tenzorok helyi gyorsítótárazását, elkerülve az ismétlődő hálózati átviteleket a modell betöltése során |
| `--host` | Az IP-cím, amelyre az RPC szervert bindolni kell (`0.0.0.0` az összes interfészhez) |

További lehetőségekért tekintse meg a [llama.cpp RPC dokumentációját](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Step 2: A modell elindítása (1. gép)

Miután az RPC szerver fut a 2. gépen, indítsa el a következtetést az 1. gépről a `llama-cli` vagy a `llama-server` segítségével.

#### llama-cli

A `llama-cli` egy terminálalapú felületet biztosít, amellyel közvetlenül interakcióba léphet a modellel. Kiválóan alkalmas benchmarkoláshoz, hibakereséshez és alacsony szintű kísérletezéshez.

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
> **Megjegyzés**: Ezt a parancsot a Terminálban (Powershell) futtassa.

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **A `<RPC_WORKER_IP>` megkeresése**: A 2. gépen futtassa az `ipconfig | findstr /C:"IPv4"` parancsot a Terminálban (Powershell) a helyi IP-cím megkereséséhez.

<!-- @os:end -->

Az indítás után a `llama-cli` megjeleníti a modell betöltésének folyamatát, majd egy interaktív promptba lép, ahol közvetlenül csevegheti a modellel:

![llama-cli GLM 4.7 futtatása két csomóponton](assets/llama-cli-example.png)
#### llama-server

A `llama-server` ugyanazt a következtetési motort teszi elérhetővé egy állandó szerverfolyamaton keresztül, integrált webes felhasználói felülettel és OpenAI-kompatibilis HTTP API-val. Ez a preferált felület a hosszabb ideig futó telepítésekhez, a több felhasználós hozzáféréshez, valamint a külső eszközökkel való integrációhoz.

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

> **A `<RPC_WORKER_IP>` megkeresése**: A 2. gépen futtassa a `hostname -I | awk '{print $1}'` parancsot a helyi IP-címének megkereséséhez.
<!-- @os:end -->

<!-- @os:windows -->
> **Megjegyzés**: Ezt a parancsot a Terminálban (Powershell) futtassa.

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

> **A `<RPC_WORKER_IP>` megkeresése**: A 2. gépen futtassa az `ipconfig | findstr /C:"IPv4"` parancsot a Terminálban (Powershell) a helyi IP-címének megkereséséhez.
<!-- @os:end -->

Az indítást követően nyissa meg a `http://<HOST_IP>:8081` címet a böngészőjében, hogy hozzáférjen a beépített webes felhasználói felülethez. Ez egy böngészőalapú csevegőfelületet biztosít a modellel való interakcióhoz:

![llama-server webes felhasználói felület GLM 4.7 modellt futtatva két csomóponton](assets/llama-server-example.png)

<!-- @os:linux -->
> **A `<HOST_IP>` megkeresése**: Az 1. gépen futtassa a `hostname -I | awk '{print $1}'` parancsot a helyi IP-címének megkereséséhez.
<!-- @os:end -->

<!-- @os:windows -->
> **A `<HOST_IP>` megkeresése**: Az 1. gépen futtassa az `ipconfig | findstr /C:"IPv4"` parancsot a Terminálban (Powershell) a helyi IP-címének megkereséséhez.
<!-- @os:end -->

#### Paraméterreferencia

| Jelző | Cél |
|------|---------|
| `-m` | A GGUF modellfájl elérési útja (az első szeletet használja, `00001-of-00005`) |
| `-c` | A kontextusméret tokenekben. A nagyobb értékek több memóriát használnak |
| `-fa on` | Bekapcsolja a rocWMMA Flash Attention funkciót a jobb teljesítmény érdekében AMD GPU-kon |
| `-ngl 999` | A modell összes rétegét áthelyezi a GPU-ra |
| `--no-mmap` | Kikapcsolja a memórialeképezést, csökkentve a betöltési időt, ha a modell mérete meghaladja a rendszer RAM-ját, de elfér a VRAM-ban |
| `--host` | Az IP-cím, amelyhez a `llama-server`-t kötni kell (csak `llama-server` esetén) |
| `--port` | A HTTP API kiszolgálásához használt port (csak `llama-server` esetén) |
| `--rpc` | Az RPC munkavégző végpontok (`IP:port`) vesszővel elválasztott listája |

A teljes paraszméterhasználatért tekintse meg a [llama-cli dokumentációt](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) és a [llama-server dokumentációt](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Következő lépések

- **Harmadik féltől származó alkalmazások csatlakoztatása**: A `llama-server` egy OpenAI-kompatibilis API-t tesz elérhetővé. Irányítson bármely OpenAI-kompatibilis alkalmazást (például az Open WebUI-t) a `http://<HOST_IP>:8081` címre bármilyen helyőrző API-kulccsal (pl. `none`), hogy csatlakozzon a fürtjéhez
- **Fedezzen fel más modelleket**: Böngésszen kvantált GGUF-ok között a [Hugging Face](https://huggingface.co/models?search=gguf) oldalon, hogy olyan modelleket találjon, amelyek elférnek a fürt összesített GPU-memóriájában
- **Skálázás négy csomópontra**: Adjon hozzá további két Ryzen AI Halo rendszert kiegészítő RPC munkavégzőként, hogy elérje az 1 billió paraméteres nagyságrendű modelleket. Adja meg a további végpontokat a `--rpc` paraméterhez vesszővel elválasztott listaként (pl. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)