<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Installation af Lemonade

<!-- @os:windows -->
Download det seneste installationsprogram fra [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) og kør `.msi`-filen.

Efter installation:
- `lemonade` CLI tilføjes automatisk til dit systems PATH
- Lemonade-serveren forventes at køre i baggrunden automatisk

Du kan også installere lydløst fra kommandolinjen:
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

For andre distributioner eller for at installere fra kildekode, se de [fulde installationsmuligheder](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:end -->


#### Verificering af Lemonade-installation

Åbn en terminal og kør:
```bash
lemonade --version
```

Du bør se output som:
```
lemonade version x.y.z
```

Hvis du ser et versionsnummer, er Lemonade installeret korrekt og klar til brug.

Her er en hurtig oversigt over almindelige Lemonade CLI-kommandoer:

| Kommando | Hvad den gør |
| --- | --- |
| `lemonade --help` | Viser alle tilgængelige kommandoer og flag. |
| `lemonade --version` | Udskriver den installerede Lemonade-version. |
| `lemonade status` | Bekræfter, om Lemonade-serveren kører og er tilgængelig. Standard OpenAI-kompatibel API-basis-URL er `http://localhost:13305/api/v1`. |
| `lemonade list` | Viser modeller, der er tilgængelige for din Lemonade-opsætning. |
| `lemonade pull <MODEL_NAME>` | Downloader en model uden at starte den. |
| `lemonade run <MODEL_NAME>` | Downloader modellen om nødvendigt og starter den derefter til inferens/chat. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | Starter en llama.cpp-model med ROCm-backend. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Starter en llama.cpp-model med Vulkan-backend. |
| `lemonade config` | Viser de aktuelle Lemonade-konfigurationsværdier. |
| `lemonade config set llamacpp.backend=rocm` | Indstiller standard llama.cpp-backend til ROCm. |

For de seneste Lemonade-serverindstillinger eller fejlfinding, se venligst den [officielle Lemonade-dokumentation](https://lemonade-server.ai/docs/lemonade-cli/).