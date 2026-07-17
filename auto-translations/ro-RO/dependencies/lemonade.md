<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Instalarea Lemonade

<!-- @os:windows -->
Descărcați cel mai recent program de instalare de la [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) și rulați fișierul `.msi`.

După instalare:
- CLI-ul `lemonade` este adăugat automat în PATH-ul sistemului
- Serverul Lemonade este configurat să ruleze automat în fundal

Puteți instala și în mod silențios din linia de comandă:
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

Pentru alte distribuții sau pentru instalare din sursă, consultați [opțiunile complete de instalare](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:end -->


#### Verificarea instalării Lemonade

Deschideți un terminal și rulați:
```bash
lemonade --version
```

Ar trebui să vedeți un rezultat similar cu:
```
lemonade version x.y.z
```

Dacă vedeți un număr de versiune, Lemonade este instalat corect și gata de utilizare.

Pentru referință rapidă, iată comenzile CLI comune pentru Lemonade:

| Comandă | Ce face |
| --- | --- |
| `lemonade --help` | Afișează toate comenzile și opțiunile disponibile. |
| `lemonade --version` | Afișează versiunea Lemonade instalată. |
| `lemonade status` | Confirmă dacă serverul Lemonade rulează și este accesibil. URL-ul de bază implicit compatibil cu OpenAI este `http://localhost:13305/api/v1`. |
| `lemonade list` | Listează modelele disponibile pentru configurația dvs. Lemonade. |
| `lemonade pull <MODEL_NAME>` | Descarcă un model fără a-l lansa. |
| `lemonade run <MODEL_NAME>` | Descarcă modelul dacă este necesar, apoi îl pornește pentru inferență/chat. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | Pornește un model llama.cpp cu backend-ul ROCm. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Pornește un model llama.cpp cu backend-ul Vulkan. |
| `lemonade config` | Afișează valorile curente ale configurației Lemonade. |
| `lemonade config set llamacpp.backend=rocm` | Setează backend-ul implicit llama.cpp la ROCm. |

Pentru cele mai recente opțiuni ale serverului Lemonade sau pentru depanare, consultați [documentația oficială Lemonade](https://lemonade-server.ai/docs/lemonade-cli/).