<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Inštalácia Lemonade

<!-- @os:windows -->
Stiahnite si najnovší inštalátor z [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) a spustite súbor `.msi`.

Po inštalácii:
- CLI `lemonade` sa automaticky pridá do systémovej premennej PATH
- Lemonade server by mal automaticky bežať na pozadí

Môžete tiež vykonať tichú inštaláciu z príkazového riadka:
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

Pre ostatné distribúcie alebo inštaláciu zo zdrojového kódu si pozrite [úplné možnosti inštalácie](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:end -->


#### Overenie inštalácie Lemonade

Otvorte terminál a spustite:
```bash
lemonade --version
```

Mali by ste vidieť výstup podobný tomuto:
```
lemonade version x.y.z
```

Ak vidíte číslo verzie, Lemonade je správne nainštalovaný a pripravený na použitie.

Pre rýchlu referenciu tu sú bežné príkazy Lemonade CLI:

| Príkaz | Čo robí |
| --- | --- |
| `lemonade --help` | Zobrazí všetky dostupné príkazy a príznaky. |
| `lemonade --version` | Vypíše nainštalovanú verziu Lemonade. |
| `lemonade status` | Potvrdí, či Lemonade server beží a je dostupný. Predvolená základná URL kompatibilná s OpenAI je `http://localhost:13305/api/v1`. |
| `lemonade list` | Zobrazí zoznam modelov dostupných pre vaše nastavenie Lemonade. |
| `lemonade pull <MODEL_NAME>` | Stiahne model bez jeho spustenia. |
| `lemonade run <MODEL_NAME>` | V prípade potreby stiahne model a potom ho spustí pre inferenciu/chat. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | Spustí model llama.cpp s backendom ROCm. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Spustí model llama.cpp s backendom Vulkan. |
| `lemonade config` | Zobrazí aktuálne konfiguračné hodnoty Lemonade. |
| `lemonade config set llamacpp.backend=rocm` | Nastaví predvolený backend llama.cpp na ROCm. |

Pre najnovšie možnosti Lemonade servera alebo riešenie problémov si pozrite [oficiálnu dokumentáciu Lemonade](https://lemonade-server.ai/docs/lemonade-cli/).