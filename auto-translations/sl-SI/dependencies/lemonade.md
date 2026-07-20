<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Nameščanje Lemonade

<!-- @os:windows -->
Prenesite najnovejši namestitveni program s spletnega mesta [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) in zaženite datoteko `.msi`.

Po namestitvi:
- Ukaz `lemonade` CLI se samodejno doda v sistemsko spremenljivko PATH
- Strežnik Lemonade naj bi se samodejno zagnal v ozadju

Namestite ga lahko tudi tiho iz ukazne vrstice:
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

Za druge distribucije ali namestitev iz izvorne kode glejte [vse možnosti namestitve](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:end -->


#### Preverjanje namestitve Lemonade

Odprite terminal in zaženite:
```bash
lemonade --version
```

Videti bi morali izpis, podoben temu:
```
lemonade version x.y.z
```

Če vidite številko različice, je Lemonade pravilno nameščen in pripravljen za uporabo.

Za hiter pregled so tukaj pogosti ukazi CLI za Lemonade:

| Ukaz | Kaj naredi |
| --- | --- |
| `lemonade --help` | Prikaže vse razpoložljive ukaze in zastavice. |
| `lemonade --version` | Izpiše nameščeno različico Lemonade. |
| `lemonade status` | Potrdi, ali strežnik Lemonade deluje in je dosegljiv. Privzeti osnovni URL naslov API-ja, združljivega z OpenAI, je `http://localhost:13305/api/v1`. |
| `lemonade list` | Izpiše modele, ki so na voljo za vašo namestitev Lemonade. |
| `lemonade pull <MODEL_NAME>` | Prenese model, ne da bi ga zagnal. |
| `lemonade run <MODEL_NAME>` | Po potrebi prenese model, nato ga zažene za sklepanje/klepet. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | Zažene model llama.cpp z zaledjem ROCm. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Zažene model llama.cpp z zaledjem Vulkan. |
| `lemonade config` | Prikaže trenutne vrednosti konfiguracije Lemonade. |
| `lemonade config set llamacpp.backend=rocm` | Nastavi privzeto zaledje llama.cpp na ROCm. |

Za najnovejše možnosti strežnika Lemonade ali odpravljanje težav glejte [uradno dokumentacijo Lemonade](https://lemonade-server.ai/docs/lemonade-cli/).