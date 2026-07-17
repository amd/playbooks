<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### A Lemonade telepítése

<!-- @os:windows -->
Töltse le a legújabb telepítőt a [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) oldalról, és futtassa a `.msi` fájlt.

A telepítés után:
- A `lemonade` CLI automatikusan hozzáadódik a rendszer PATH-jához
- A Lemonade szerver várhatóan automatikusan fut a háttérben

Csendes telepítést is végezhet parancssorból:
```cmd
msiexec /i lemonade-server-minimal.msi /qn
```
<!-- @os:end -->

<!-- @os:linux -->
**Ubuntu:**
```bash
sudo add-apt-repository ppa:lemonade-team/stable
sudo apt install lemonade-server
```

**Arch Linux (AUR):**
```bash
yay -S lemonade-server
```

Más disztribúciókhoz vagy forráskódból való telepítéshez tekintse meg a [teljes telepítési lehetőségeket](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:end -->


#### A Lemonade telepítésének ellenőrzése

Nyisson meg egy terminált, és futtassa:
```bash
lemonade --version
```

A következőhöz hasonló kimenetet kell látnia:
```
lemonade version x.y.z
```

Ha verziószámot lát, a Lemonade megfelelően van telepítve és használatra kész.

Gyors referenciának itt találhatók a gyakori Lemonade CLI parancsok:

| Parancs | Mit csinál |
| --- | --- |
| `lemonade --help` | Megjeleníti az összes elérhető parancsot és jelzőt. |
| `lemonade --version` | Kiírja a telepített Lemonade verziót. |
| `lemonade status` | Megerősíti, hogy a Lemonade szerver fut-e és elérhető-e. Az alapértelmezett OpenAI-kompatibilis API alap URL: `http://localhost:13305/api/v1`. |
| `lemonade list` | Felsorolja a Lemonade beállításában elérhető modelleket. |
| `lemonade pull <MODEL_NAME>` | Letölt egy modellt anélkül, hogy elindítaná. |
| `lemonade run <MODEL_NAME>` | Szükség esetén letölti a modellt, majd elindítja inferencia/csevegés céljából. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | Elindít egy llama.cpp modellt a ROCm háttérrendszerrel. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Elindít egy llama.cpp modellt a Vulkan háttérrendszerrel. |
| `lemonade config` | Megjeleníti az aktuális Lemonade konfigurációs értékeket. |
| `lemonade config set llamacpp.backend=rocm` | Az alapértelmezett llama.cpp háttérrendszert ROCm-re állítja. |

A legújabb Lemonade szerver beállításokért vagy hibaelhárításhoz kérjük, tekintse meg a [hivatalos Lemonade dokumentációt](https://lemonade-server.ai/docs/lemonade-cli/).