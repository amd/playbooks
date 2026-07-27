<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Lemonade installeren

<!-- @os:windows -->
Download het nieuwste installatieprogramma van [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) en voer het `.msi`-bestand uit.

Na de installatie:
- Wordt de `lemonade` CLI automatisch aan uw systeem-PATH toegevoegd
- Wordt verwacht dat de Lemonade-server automatisch op de achtergrond draait

U kunt ook stil installeren vanaf de opdrachtregel:
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

Zie voor andere distributies of om vanuit de broncode te installeren de [volledige installatieopties](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:end -->


#### Lemonade-installatie verifiëren

Open een terminal en voer het volgende uit:
```bash
lemonade --version
```

U zou een uitvoer moeten zien zoals:
```
lemonade version x.y.z
```

Als u een versienummer ziet, is Lemonade correct geïnstalleerd en klaar voor gebruik.

Hieronder vindt u, voor snelle raadpleging, veelgebruikte Lemonade CLI-opdrachten:

| Opdracht | Wat het doet |
| --- | --- |
| `lemonade --help` | Toont alle beschikbare opdrachten en vlaggen. |
| `lemonade --version` | Drukt de geïnstalleerde Lemonade-versie af. |
| `lemonade status` | Bevestigt of de Lemonade-server actief en bereikbaar is. De standaard OpenAI-compatibele API-basis-URL is `http://localhost:13305/api/v1`. |
| `lemonade list` | Toont de modellen die beschikbaar zijn voor uw Lemonade-configuratie. |
| `lemonade pull <MODEL_NAME>` | Downloadt een model zonder het te starten. |
| `lemonade run <MODEL_NAME>` | Downloadt het model indien nodig en start het vervolgens voor inferentie/chat. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | Start een llama.cpp-model met de ROCm-backend. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Start een llama.cpp-model met de Vulkan-backend. |
| `lemonade config` | Toont de huidige Lemonade-configuratiewaarden. |
| `lemonade config set llamacpp.backend=rocm` | Stelt de standaard llama.cpp-backend in op ROCm. |

Raadpleeg voor de nieuwste Lemonade-serveropties of voor probleemoplossing de [officiële Lemonade-documentatie](https://lemonade-server.ai/docs/lemonade-cli/).