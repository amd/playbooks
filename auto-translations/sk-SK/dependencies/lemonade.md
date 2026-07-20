<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Inštalácia Lemonade

<!-- @os:windows -->
Stiahnite si najnovší inštalačný program zo stránky [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) a spustite súbor `.msi`. 

Po inštalácii:
- CLI nástroj `lemonade` sa automaticky pridá do systémovej premennej PATH
- Server Lemonade sa automaticky spúšťa na pozadí

Inštaláciu môžete vykonať aj tiché (bez zásahu používateľa) priamo z príkazového riadku:
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

Ak chcete inštaláciu z iných distribúcií alebo zo zdrojového kódu, pozrite si [úplné možnosti inštalácie](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:end -->


#### Overenie inštalácie Lemonade

Otvorte terminál a spustite:
```bash
lemonade --version
```

Mal by sa zobraziť výstup podobný tomuto:
```
lemonade version x.y.z
```

Ak sa zobrazí číslo verzie, Lemonade je správne nainštalovaný a pripravený na použitie.

Pre rýchlu orientáciu tu uvádzame bežné príkazy CLI nástroja Lemonade:

| Príkaz | Čo robí |
| --- | --- |
| `lemonade --help` | Zobrazí všetky dostupné príkazy a prepínače. |
| `lemonade --version` | Vypíše nainštalovanú verziu nástroja Lemonade. |
| `lemonade status` | Overí, či server Lemonade beží a je dostupný. Predvolená základná adresa URL rozhrania API kompatibilného s OpenAI je `http://localhost:13305/api/v1`. |
| `lemonade list` | Zobrazí zoznam modelov dostupných vo vašom nastavení Lemonade. |
| `lemonade pull <MODEL_NAME>` | Stiahne model bez jeho spustenia. |
| `lemonade run <MODEL_NAME>` | V prípade potreby stiahne model a následne ho spustí na inferenciu/chat. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | Spustí model llama.cpp s backendom ROCm. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Spustí model llama.cpp s backendom Vulkan. |
| `lemonade config` | Zobrazí aktuálne hodnoty konfigurácie Lemonade. |
| `lemonade config set llamacpp.backend=rocm` | Nastaví predvolený backend llama.cpp na ROCm. |

Najnovšie informácie o možnostiach servera Lemonade alebo pomoc pri riešení problémov nájdete v [oficiálnej dokumentácii Lemonade](https://lemonade-server.ai/docs/lemonade-cli/).