<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Instalacija Lemonade

<!-- @os:windows -->
Preuzmite najnoviji instalater sa [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) i pokrenite `.msi` fajl.

Nakon instalacije:
- `lemonade` CLI se automatski dodaje u sistemski PATH
- Očekuje se da Lemonade server radi automatski u pozadini

Takođe možete instalirati tiho putem komandne linije:
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

Za ostale distribucije ili instalaciju iz izvornog koda, pogledajte [sve opcije instalacije](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:end -->


#### Verifikacija instalacije Lemonade

Otvorite terminal i pokrenite:
```bash
lemonade --version
```

Trebalo bi da vidite izlaz poput:
```
lemonade version x.y.z
```

Ako vidite broj verzije, Lemonade je ispravno instaliran i spreman za upotrebu.

Za brzu referencu, ovde su uobičajene Lemonade CLI komande:

| Komanda | Šta radi |
| --- | --- |
| `lemonade --help` | Prikazuje sve dostupne komande i zastavice. |
| `lemonade --version` | Ispisuje instaliranu verziju Lemonade. |
| `lemonade status` | Potvrđuje da li Lemonade server radi i da li je dostupan. Podrazumevani OpenAI-kompatibilni API osnovni URL je `http://localhost:13305/api/v1`. |
| `lemonade list` | Prikazuje modele dostupne u vašem Lemonade okruženju. |
| `lemonade pull <MODEL_NAME>` | Preuzima model bez pokretanja. |
| `lemonade run <MODEL_NAME>` | Preuzima model ako je potrebno, zatim ga pokreće za inferenciju/razgovor. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | Pokreće llama.cpp model sa ROCm backendom. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Pokreće llama.cpp model sa Vulkan backendom. |
| `lemonade config` | Prikazuje trenutne vrednosti Lemonade konfiguracije. |
| `lemonade config set llamacpp.backend=rocm` | Postavlja podrazumevani llama.cpp backend na ROCm. |

Za najnovije opcije Lemonade servera ili rešavanje problema, pogledajte [zvaničnu Lemonade dokumentaciju](https://lemonade-server.ai/docs/lemonade-cli/).