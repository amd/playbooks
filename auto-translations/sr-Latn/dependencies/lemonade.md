<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Instaliranje Lemonade-a

<!-- @os:windows -->
Preuzmite najnoviji instalacioni program sa [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) i pokrenite `.msi` fajl.

Nakon instalacije:
- CLI alat `lemonade` se automatski dodaje u sistemsku PATH promenljivu
- Lemonade server je podrazumevano automatski pokrenut u pozadini

Takođe možete izvršiti tihu instalaciju iz komandne linije:
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

Za druge distribucije ili instalaciju iz izvornog koda, pogledajte [sve opcije instalacije](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:end -->


#### Provera instalacije Lemonade-a

Otvorite terminal i pokrenite:
```bash
lemonade --version
```

Trebalo bi da vidite izlaz sličan ovom:
```
lemonade version x.y.z
```

Ako vidite broj verzije, Lemonade je ispravno instaliran i spreman za korišćenje.

Za brzu referencu, evo najčešćih Lemonade CLI komandi:

| Komanda | Šta radi |
| --- | --- |
| `lemonade --help` | Prikazuje sve dostupne komande i oznake. |
| `lemonade --version` | Ispisuje instaliranu verziju Lemonade-a. |
| `lemonade status` | Potvrđuje da li je Lemonade server pokrenut i dostupan. Podrazumevani OpenAI-kompatibilni API bazni URL je `http://localhost:13305/api/v1`. |
| `lemonade list` | Prikazuje listu modela dostupnih za vaše Lemonade okruženje. |
| `lemonade pull <MODEL_NAME>` | Preuzima model bez njegovog pokretanja. |
| `lemonade run <MODEL_NAME>` | Preuzima model ako je potrebno, a zatim ga pokreće za zaključivanje/čet. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | Pokreće llama.cpp model sa ROCm pozadinskim sistemom. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Pokreće llama.cpp model sa Vulkan pozadinskim sistemom. |
| `lemonade config` | Prikazuje trenutne vrednosti Lemonade konfiguracije. |
| `lemonade config set llamacpp.backend=rocm` | Postavlja ROCm kao podrazumevani llama.cpp pozadinski sistem. |

Za najnovije opcije Lemonade servera ili rešavanje problema, pogledajte [zvaničnu Lemonade dokumentaciju](https://lemonade-server.ai/docs/lemonade-cli/).