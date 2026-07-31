<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Lemonade telepítése

<!-- @os:windows -->
Töltsd le a legújabb telepítőt a [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) oldalról, és futtasd a `.msi` fájlt.

A telepítés után:
- A `lemonade` CLI automatikusan bekerül a rendszer PATH-jába
- A Lemonade szerver a háttérben automatikusan elindul

Csendes telepítést is végezhetsz a parancssorból:
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

Egyéb disztribúciók esetén, vagy ha forrásból szeretnéd telepíteni, lásd a [teljes telepítési lehetőségeket](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:end -->


#### A Lemonade telepítésének ellenőrzése

Nyiss meg egy terminált, és futtasd:
```bash
lemonade --version
```

Az alábbihoz hasonló kimenetet kell látnod:
```
lemonade version x.y.z
```

Ha egy verziószámot látsz, a Lemonade megfelelően telepítve van, és készen áll a használatra.

Gyors áttekintésként itt vannak a leggyakoribb Lemonade CLI parancsok:

| Parancs | Mit csinál |
| --- | --- |
| `lemonade --help` | Megjeleníti az összes elérhető parancsot és kapcsolót. |
| `lemonade --version` | Kiírja a telepített Lemonade verziót. |
| `lemonade status` | Megerősíti, hogy a Lemonade szerver fut-e és elérhető-e. Az alapértelmezett OpenAI-kompatibilis API bázis URL a `http://localhost:13305/api/v1`. |
| `lemonade list` | Felsorolja a Lemonade beállításodban elérhető modelleket. |
| `lemonade pull <MODEL_NAME>` | Letölt egy modellt anélkül, hogy elindítaná. |
| `lemonade run <MODEL_NAME>` | Letölti a modellt, ha szükséges, majd elindítja következtetéshez/csevegéshez. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | Elindít egy llama.cpp modellt a ROCm háttérrendszerrel. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Elindít egy llama.cpp modellt a Vulkan háttérrendszerrel. |
| `lemonade config` | Megjeleníti az aktuális Lemonade konfigurációs értékeket. |
| `lemonade config set llamacpp.backend=rocm` | Beállítja az alapértelmezett llama.cpp háttérrendszert ROCm-re. |

A legújabb Lemonade szerver beállításokért vagy hibaelhárításért kérjük, nézd meg a [hivatalos Lemonade dokumentációt](https://lemonade-server.ai/docs/lemonade-cli/).