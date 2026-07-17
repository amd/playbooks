<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Instalowanie Lemonade

<!-- @os:windows -->
Pobierz najnowszy instalator ze strony [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) i uruchom plik `.msi`.

Po instalacji:
- CLI `lemonade` jest automatycznie dodawane do systemowej zmiennej PATH
- Serwer Lemonade powinien automatycznie działać w tle

Możesz również zainstalować w trybie cichym z wiersza poleceń:
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

W przypadku innych dystrybucji lub instalacji ze źródeł, zapoznaj się z [pełnymi opcjami instalacji](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:end -->


#### Weryfikacja instalacji Lemonade

Otwórz terminal i uruchom:
```bash
lemonade --version
```

Powinieneś zobaczyć dane wyjściowe podobne do:
```
lemonade version x.y.z
```

Jeśli widzisz numer wersji, Lemonade jest poprawnie zainstalowane i gotowe do użycia.

Poniżej znajduje się krótki przewodnik po typowych poleceniach CLI Lemonade:

| Polecenie | Co robi |
| --- | --- |
| `lemonade --help` | Wyświetla wszystkie dostępne polecenia i flagi. |
| `lemonade --version` | Wyświetla zainstalowaną wersję Lemonade. |
| `lemonade status` | Potwierdza, czy serwer Lemonade działa i jest osiągalny. Domyślny bazowy adres URL API zgodnego z OpenAI to `http://localhost:13305/api/v1`. |
| `lemonade list` | Wyświetla modele dostępne w konfiguracji Lemonade. |
| `lemonade pull <MODEL_NAME>` | Pobiera model bez jego uruchamiania. |
| `lemonade run <MODEL_NAME>` | Pobiera model, jeśli jest to konieczne, a następnie uruchamia go do wnioskowania/czatu. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | Uruchamia model llama.cpp z backendem ROCm. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Uruchamia model llama.cpp z backendem Vulkan. |
| `lemonade config` | Wyświetla bieżące wartości konfiguracji Lemonade. |
| `lemonade config set llamacpp.backend=rocm` | Ustawia domyślny backend llama.cpp na ROCm. |

Aby uzyskać najnowsze opcje serwera Lemonade lub informacje dotyczące rozwiązywania problemów, zapoznaj się z [oficjalną dokumentacją Lemonade](https://lemonade-server.ai/docs/lemonade-cli/).