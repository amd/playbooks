<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Instalace Lemonade

<!-- @os:windows -->
Stáhněte nejnovější instalátor z [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) a spusťte soubor `.msi`.

Po instalaci:
- CLI `lemonade` je automaticky přidáno do systémové proměnné PATH
- Server Lemonade by měl automaticky běžet na pozadí

Instalaci lze také provést tiše z příkazové řádky:
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

Pro ostatní distribuce nebo instalaci ze zdrojového kódu si přečtěte [úplné možnosti instalace](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:end -->


#### Ověření instalace Lemonade

Otevřete terminál a spusťte:
```bash
lemonade --version
```

Měli byste vidět výstup podobný tomuto:
```
lemonade version x.y.z
```

Pokud se zobrazí číslo verze, Lemonade je správně nainstalováno a připraveno k použití.

Pro rychlý přehled jsou zde běžné příkazy CLI Lemonade:

| Příkaz | Co dělá |
| --- | --- |
| `lemonade --help` | Zobrazí všechny dostupné příkazy a přepínače. |
| `lemonade --version` | Vypíše nainstalovanou verzi Lemonade. |
| `lemonade status` | Potvrdí, zda server Lemonade běží a je dostupný. Výchozí základní URL API kompatibilního s OpenAI je `http://localhost:13305/api/v1`. |
| `lemonade list` | Vypíše modely dostupné pro vaše nastavení Lemonade. |
| `lemonade pull <MODEL_NAME>` | Stáhne model bez jeho spuštění. |
| `lemonade run <MODEL_NAME>` | V případě potřeby stáhne model a poté ho spustí pro inferenci/chat. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | Spustí model llama.cpp s backendem ROCm. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Spustí model llama.cpp s backendem Vulkan. |
| `lemonade config` | Zobrazí aktuální konfigurační hodnoty Lemonade. |
| `lemonade config set llamacpp.backend=rocm` | Nastaví výchozí backend llama.cpp na ROCm. |

Nejnovější možnosti serveru Lemonade nebo řešení problémů naleznete v [oficiální dokumentaci Lemonade](https://lemonade-server.ai/docs/lemonade-cli/).