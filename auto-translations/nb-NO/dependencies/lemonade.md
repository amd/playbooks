<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Installere Lemonade

<!-- @os:windows -->
Last ned den nyeste installasjonsprogrammet fra [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) og kjør `.msi`-filen.

Etter installasjon:
- `lemonade` CLI legges automatisk til i systemets PATH
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

For andre distribusjoner eller for å installere fra kildekode, se [fullstendige installasjonsalternativer](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:end -->


#### Verifisere Lemonade-installasjon

Åpne en terminal og kjør:
```bash
lemonade --version
```

Du skal se utdata som:
```
lemonade version x.y.z
```

Hvis du ser et versjonsnummer, er Lemonade installert korrekt og klar til bruk.

For rask referanse, her er vanlige Lemonade CLI-kommandoer:

| Kommando | Hva den gjør |
| --- | --- |
| `lemonade --help` | Viser alle tilgjengelige kommandoer og flagg. |
| `lemonade --version` | Skriver ut den installerte Lemonade-versjonen. |
| `lemonade status` | Bekrefter om Lemonade-serveren kjører og er tilgjengelig. Standard OpenAI-kompatibel API-basis-URL er `http://localhost:13305/api/v1`. |
| `lemonade list` | Lister opp modeller tilgjengelig for Lemonade-oppsettet ditt. |
| `lemonade pull <MODEL_NAME>` | Laster ned en modell uten å starte den. |
| `lemonade run <MODEL_NAME>` | Laster ned modellen om nødvendig, og starter den deretter for inferens/chat. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | Starter en llama.cpp-modell med ROCm-backend. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Starter en llama.cpp-modell med Vulkan-backend. |
| `lemonade config` | Viser gjeldende Lemonade-konfigurasjonsverdier. |
| `lemonade config set llamacpp.backend=rocm` | Setter standard llama.cpp-backend til ROCm. |

For de nyeste Lemonade-serveralternativene eller feilsøking, se den [offisielle Lemonade-dokumentasjonen](https://lemonade-server.ai/docs/lemonade-cli/).