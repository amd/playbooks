<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Installere Lemonade

<!-- @os:windows -->
Last ned den nyeste installasjonsfilen fra [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) og kjør `.msi`-filen.

Etter installasjonen:
- CLI-verktøyet `lemonade` blir automatisk lagt til i systemets PATH
- Lemonade-serveren forventes å kjøre i bakgrunnen automatisk

Du kan også installere stille fra kommandolinjen:
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

For andre distribusjoner, eller for å installere fra kildekode, se [fullstendige installasjonsalternativer](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:end -->


#### Verifisere Lemonade-installasjonen

Åpne en terminal og kjør:
```bash
lemonade --version
```

Du bør se følgende utdata:
```
lemonade version x.y.z
```

Hvis du ser et versjonsnummer, er Lemonade riktig installert og klar til bruk.

Som en rask referanse finner du her vanlige Lemonade CLI-kommandoer:

| Kommando | Hva den gjør |
| --- | --- |
| `lemonade --help` | Viser alle tilgjengelige kommandoer og flagg. |
| `lemonade --version` | Skriver ut den installerte Lemonade-versjonen. |
| `lemonade status` | Bekrefter om Lemonade-serveren kjører og er tilgjengelig. Standard OpenAI-kompatibel API-base-URL er `http://localhost:13305/api/v1`. |
| `lemonade list` | Viser modeller som er tilgjengelige for ditt Lemonade-oppsett. |
| `lemonade pull <MODEL_NAME>` | Laster ned en modell uten å starte den. |
| `lemonade run <MODEL_NAME>` | Laster ned modellen om nødvendig, og starter den deretter for inferens/chat. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | Starter en llama.cpp-modell med ROCm-backend. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Starter en llama.cpp-modell med Vulkan-backend. |
| `lemonade config` | Viser gjeldende Lemonade-konfigurasjonsverdier. |
| `lemonade config set llamacpp.backend=rocm` | Setter standard llama.cpp-backend til ROCm. |

For de nyeste alternativene for Lemonade-serveren eller feilsøking, se [offisiell Lemonade-dokumentasjon](https://lemonade-server.ai/docs/lemonade-cli/).