<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Instalowanie Lemonade

<!-- @os:windows -->
Pobierz najnowszy instalator ze strony [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) i uruchom plik `.msi`. 

Po instalacji:
- Interfejs wiersza poleceń `lemonade` jest automatycznie dodawany do ścieżki systemowej PATH
- Serwer Lemonade domyślnie uruchamia się automatycznie w tle

Instalację można również przeprowadzić w trybie cichym z poziomu wiersza poleceń:
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

Informacje na temat innych dystrybucji lub instalacji ze źródeł znajdziesz w [pełnym opisie opcji instalacji](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:end -->


#### Weryfikacja instalacji Lemonade

Otwórz terminal i uruchom:
```bash
lemonade --version
```

Powinieneś zobaczyć wynik podobny do:
```
lemonade version x.y.z
```

Jeśli widzisz numer wersji, oznacza to, że Lemonade został poprawnie zainstalowany i jest gotowy do użycia.

Dla szybkiego odniesienia, oto najczęściej używane polecenia CLI Lemonade:

| Polecenie | Co robi |
| --- | --- |
| `lemonade --help` | Wyświetla wszystkie dostępne polecenia i flagi. |
| `lemonade --version` | Wyświetla zainstalowaną wersję Lemonade. |
| `lemonade status` | Sprawdza, czy serwer Lemonade jest uruchomiony i dostępny. Domyślny bazowy adres URL API zgodnego ze standardem OpenAI to `http://localhost:13305/api/v1`. |
| `lemonade list` | Wyświetla listę modeli dostępnych w Twojej instalacji Lemonade. |
| `lemonade pull <MODEL_NAME>` | Pobiera model bez jego uruchamiania. |
| `lemonade run <MODEL_NAME>` | Pobiera model, jeśli to konieczne, a następnie uruchamia go do wnioskowania/czatu. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | Uruchamia model llama.cpp z backendem ROCm. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Uruchamia model llama.cpp z backendem Vulkan. |
| `lemonade config` | Wyświetla bieżące wartości konfiguracji Lemonade. |
| `lemonade config set llamacpp.backend=rocm` | Ustawia ROCm jako domyślny backend dla llama.cpp. |

Aby zapoznać się z najnowszymi opcjami serwera Lemonade lub rozwiązywaniem problemów, zajrzyj do [oficjalnej dokumentacji Lemonade](https://lemonade-server.ai/docs/lemonade-cli/).