<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Installera Lemonade

<!-- @os:windows -->
Ladda ner det senaste installationsprogrammet från [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) och kör `.msi`-filen.

Efter installationen:
- CLI-kommandot `lemonade` läggs automatiskt till i systemets PATH
- Lemonade-servern förväntas köras automatiskt i bakgrunden

Du kan även installera tyst från kommandoraden:
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

För andra distributioner eller för att installera från källkod, se [fullständiga installationsalternativ](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:end -->


#### Verifiera Lemonade-installationen

Öppna en terminal och kör:
```bash
lemonade --version
```

Du bör se utdata som liknar följande:
```
lemonade version x.y.z
```

Om du ser ett versionsnummer är Lemonade korrekt installerat och redo att användas.

Som snabbreferens, här är vanliga Lemonade CLI-kommandon:

| Kommando | Vad det gör |
| --- | --- |
| `lemonade --help` | Visar alla tillgängliga kommandon och flaggor. |
| `lemonade --version` | Skriver ut den installerade Lemonade-versionen. |
| `lemonade status` | Bekräftar om Lemonade-servern körs och är nåbar. Standard-URL:en för det OpenAI-kompatibla API:et är `http://localhost:13305/api/v1`. |
| `lemonade list` | Listar modeller som är tillgängliga för din Lemonade-installation. |
| `lemonade pull <MODEL_NAME>` | Laddar ner en modell utan att starta den. |
| `lemonade run <MODEL_NAME>` | Laddar ner modellen om det behövs och startar den sedan för inferens/chatt. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | Startar en llama.cpp-modell med ROCm-backend. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Startar en llama.cpp-modell med Vulkan-backend. |
| `lemonade config` | Visar de aktuella konfigurationsvärdena för Lemonade. |
| `lemonade config set llamacpp.backend=rocm` | Ställer in standard-backend för llama.cpp till ROCm. |

För de senaste alternativen för Lemonade-servern eller felsökning, se den [officiella Lemonade-dokumentationen](https://lemonade-server.ai/docs/lemonade-cli/).