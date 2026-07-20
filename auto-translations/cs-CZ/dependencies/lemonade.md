<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Instalace Lemonade

<!-- @os:windows -->
Stáhněte nejnovější instalační program z [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) a spusťte soubor `.msi`.

Po instalaci:
- Rozhraní příkazového řádku `lemonade` se automaticky přidá do systémové proměnné PATH
- Server Lemonade by měl na pozadí spouštět automaticky

Instalaci lze také provést tiše z příkazového řádku:
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

Pro další distribuce nebo instalaci ze zdrojového kódu si prohlédněte [úplné možnosti instalace](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:end -->


#### Ověření instalace Lemonade

Otevřete terminál a spusťte:
```bash
lemonade --version
```

Měl by se zobrazit výstup podobný tomuto:
```
lemonade version x.y.z
```

Pokud se zobrazí číslo verze, Lemonade je správně nainstalován a připraven k použití.

Pro rychlou orientaci zde uvádíme běžné příkazy CLI nástroje Lemonade:

| Příkaz | Co dělá |
| --- | --- |
| `lemonade --help` | Zobrazí všechny dostupné příkazy a přepínače. |
| `lemonade --version` | Vypíše nainstalovanou verzi Lemonade. |
| `lemonade status` | Potvrdí, zda server Lemonade běží a je dostupný. Výchozí základní URL adresa API kompatibilního s OpenAI je `http://localhost:13305/api/v1`. |
| `lemonade list` | Vypíše modely dostupné pro vaši instalaci Lemonade. |
| `lemonade pull <MODEL_NAME>` | Stáhne model bez jeho spuštění. |
| `lemonade run <MODEL_NAME>` | V případě potřeby stáhne model a poté jej spustí pro odvozování/chat. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | Spustí model llama.cpp s podpůrnou vrstvou ROCm. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Spustí model llama.cpp s podpůrnou vrstvou Vulkan. |
| `lemonade config` | Zobrazí aktuální hodnoty konfigurace Lemonade. |
| `lemonade config set llamacpp.backend=rocm` | Nastaví výchozí podpůrnou vrstvu llama.cpp na ROCm. |

Nejnovější možnosti serveru Lemonade nebo pomoc s řešením problémů naleznete v [oficiální dokumentaci Lemonade](https://lemonade-server.ai/docs/lemonade-cli/).