<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Namestitev Lemonade

<!-- @os:windows -->
Prenesite najnovejši namestitveni program s [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) in zaženite datoteko `.msi`.

Po namestitvi:
- CLI `lemonade` se samodejno doda v sistemski PATH
- Pričakuje se, da strežnik Lemonade samodejno deluje v ozadju

Namestitev lahko izvedete tudi tiho iz ukazne vrstice:
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

Za druge distribucije ali namestitev iz izvorne kode glejte [celotne možnosti namestitve](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:end -->


#### Preverjanje namestitve Lemonade

Odprite terminal in zaženite:
```bash
lemonade --version
```

Prikazati bi se morala izhod, podoben:
```
lemonade version x.y.z
```

Če vidite številko različice, je Lemonade pravilno nameščen in pripravljen za uporabo.

Za hitro referenco so tukaj pogosti ukazi CLI Lemonade:

| Ukaz | Kaj naredi |
| --- | --- |
| `lemonade --help` | Prikaže vse razpoložljive ukaze in zastavice. |
| `lemonade --version` | Izpiše nameščeno različico Lemonade. |
| `lemonade status` | Potrdi, ali strežnik Lemonade deluje in je dosegljiv. Privzeti osnovni URL API-ja, združljivega z OpenAI, je `http://localhost:13305/api/v1`. |
| `lemonade list` | Navede modele, ki so na voljo za vašo namestitev Lemonade. |
| `lemonade pull <MODEL_NAME>` | Prenese model brez zagona. |
| `lemonade run <MODEL_NAME>` | Po potrebi prenese model, nato pa ga zažene za sklepanje/klepet. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | Zažene model llama.cpp z zaledjem ROCm. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Zažene model llama.cpp z zaledjem Vulkan. |
| `lemonade config` | Prikaže trenutne konfiguracijske vrednosti Lemonade. |
| `lemonade config set llamacpp.backend=rocm` | Nastavi privzeto zaledje llama.cpp na ROCm. |

Za najnovejše možnosti strežnika Lemonade ali odpravljanje težav si oglejte [uradno dokumentacijo Lemonade](https://lemonade-server.ai/docs/lemonade-cli/).