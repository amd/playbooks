<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tłumaczenie maszynowe.** Ta strona została automatycznie przetłumaczona z języka angielskiego i nie została zweryfikowana przez człowieka. Może zawierać błędy, a niektóre instrukcje, polecenia, pliki do pobrania, dostępność produktów lub inne treści mogą różnić się w zależności od języka lub regionu. W przypadku jakichkolwiek niezgodności lub rozbieżności rozstrzygająca jest oryginalna angielska wersja playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Klastrowanie czterech Ryzen™ AI Halo za pomocą RPC

## Przegląd

Twój Ryzen™ AI Halo jest już w stanie uruchamiać duże modele językowe lokalnie. Klastrowanie idzie o krok dalej, łącząc pamięć GPU wielu systemów w sieci lokalnej, co daje dostęp do jeszcze większych modeli o silniejszym rozumowaniu, lepszej generacji kodu i głębszym rozumieniu wielojęzycznym — całkowicie na Twoim własnym sprzęcie.

Ten przewodnik pokazuje, jak sklastrować cztery systemy Ryzen AI Halo za pomocą silnika RPC llama.cpp i uruchomić Kimi K2.6, duży model typu mixture-of-experts, na wszystkich czterech maszynach z akceleracją AMD ROCm™.

## Czego się nauczysz

- Jak rozszerzyć alokację pamięci VRAM na systemach Ryzen AI Halo
- Instalacja llama.cpp z obsługą ROCm i RPC
- Konfiguracja workerów RPC i uruchamianie rozproszonego wnioskowania na czterech węzłach
- Uruchomienie modelu z 1 bilionem parametrów na czterech połączonych sieciowo systemach Ryzen AI Halo

## Konfiguracja pamięci

> **Uwaga**: Wykonaj ten krok na wszystkich czterech maszynach (Maszyna 1 do Maszyny 4).

<!-- @os:windows -->
W systemie Windows, aby uruchamiać większe modele wymagające większej ilości pamięci, musimy skorzystać z alokacji AMD Variable Graphics Memory (pamięć VRAM iGPU).

Można to zrobić, otwierając panel sterowania AMD Software: Adrenalin Edition i przechodząc do: `Performance > Tuning > AMD Variable Graphics Memory`. Ustaw wartość na **96 GB**. Uruchom ponownie system, aby zmiany zostały zastosowane.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
W systemie Linux ROCm korzysta ze współdzielonej puli pamięci systemowej, a pula ta jest domyślnie skonfigurowana na połowę pamięci systemowej.

Tę ilość można zwiększyć, zmieniając ustawienie stron Translation Table Manager (TTM) jądra, postępując zgodnie z poniższymi instrukcjami. AMD zaleca ustawienie minimalnej dedykowanej pamięci VRAM w BIOS-ie (0,5 GB).

* Zainstaluj narzędzie pipx i dodaj ścieżkę do pakietów wheel zainstalowanych przez pipx do systemowej ścieżki wyszukiwania.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Zainstaluj pakiet wheel amd-debug-tools z PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Uruchom narzędzie amd-ttm, aby sprawdzić bieżące ustawienia pamięci współdzielonej.
  ```bash
  amd-ttm
  ```

* Zmień ustawienia pamięci współdzielonej na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Uruchom ponownie system, aby zmiany zostały zastosowane.


<!-- @os:end -->
<!-- @device:halo_box -->
## Sprawdzanie aktualizacji oprogramowania

<!-- @require:software-update -->
<!-- @device:end -->
## Wymagania wstępne

### Sprzęt

Ten przewodnik wymaga czterech jednostek Ryzen AI Halo oraz jednego switcha Ethernet, połączonych w topologii gwiazdy, przy czym każda jednostka jest podłączona bezpośrednio do switcha.

| Komponent | Ilość | Opis |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Węzły obliczeniowe tworzące klaster |
| Switch Ethernet 10Gbps | 1 | Centralny switch umożliwiający komunikację wieloma węzłami Ryzen AI Halo (co najmniej 4 porty) |
| Kabel Ethernet | 4 | Łączy każdą jednostkę Halo ze switchem (zalecany Cat 7 lub wyższy) |

> **Uwaga**: Do połączenia czterech jednostek Ryzen AI Halo wymagane są cztery porty switcha Ethernet. Piąty port jest wymagany, jeśli dostęp do modelu odbywa się z osobnej maszyny klienckiej, a nie z jednej z jednostek Halo.

### Oprogramowanie
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Zainstaluj:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) wraz z obciążeniem **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Konfiguracja sprzętu fizycznego

> **Uwaga**: Wykonaj ten krok na wszystkich czterech maszynach (Maszyna 1 do Maszyny 4).

Podłącz każdą jednostkę Ryzen AI Halo do switcha Ethernet za pomocą kabla Cat 7 (lub wyższego). Ustanawia to łącze 10Gbps wykorzystywane do szybkiej komunikacji między węzłami.
<!-- @os:linux -->
### 1. Określanie interfejsów sieciowych

Na każdej maszynie znajdź nazwę jej interfejsu sieciowego i zapisz ją (poniżej będzie ona nazywana `IFNAME`). Uruchom:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

To wyświetla nazwę interfejsu bezpośrednio, na przykład:

```bash
enp191s0
```

### 2. Weryfikacja prędkości łącza sieciowego

Potwierdź, że łącze jest aktywne i działa z pełną prędkością, sprawdzając prędkość swojego interfejsu:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Uwaga**: Zastąp `<IFNAME>` nazwą interfejsu wyjściowego z [1. Określanie interfejsów sieciowych](#1-determine-network-interfaces)

Powinieneś zobaczyć prędkość `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Uwaga**: Jeśli prędkość jest niższa niż `10000Mb/s` lub łącze się nie uruchamia, sprawdź podłączenie kabla i upewnij się, że port switcha jest ustawiony na 10Gbps. Niektóre switche wymagają wyłączenia auto-negocjacji i ręcznego ustawienia prędkości łącza; zapoznaj się z dokumentacją swojego switcha.

<!-- @os:end -->

<!-- @os:windows -->
### Weryfikacja prędkości łącza sieciowego

Na każdej maszynie sprawdź prędkość łącza interfejsów sieciowych:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Twój interfejs Ethernet powinien być `Up` i działać z prędkością `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Uwaga**: Jeśli prędkość jest niższa niż `10 Gbps` lub łącze się nie uruchamia, sprawdź podłączenie kabla i upewnij się, że port switcha jest ustawiony na 10Gbps. Niektóre switche wymagają wyłączenia auto-negocjacji i ręcznego ustawienia prędkości łącza; zapoznaj się z dokumentacją swojego switcha.

<!-- @os:end -->

## Instalacja llama.cpp

> **Uwaga**: Wykonaj ten krok na wszystkich czterech maszynach (Maszyna 1 do Maszyny 4).

Dostępne są dwie opcje instalacji:

- [Opcja 1: Lemonade SDK (zalecane)](#option-1-lemonade-sdk-recommended) - gotowe pliki binarne, najszybsza konfiguracja
- [Opcja 2: Ręczna kompilacja ze źródeł](#option-2-manual-source-build) - kompilacja ze źródeł z pełną kontrolą nad flagami kompilacji

### Opcja 1: Lemonade SDK (zalecane)

Lemonade SDK udostępnia nocne kompilacje (nightly builds) llama.cpp z akceleracją AMD ROCm 7, przeznaczone dla GPU takich jak gfx1151 (Strix Halo / Ryzen AI Max+ 395) oraz innych nowszych architektur Radeon.

<!-- @os:windows -->
#### Krok 1: Pobierz gotowe pliki binarne

Przejdź do strony najnowszego wydania i pobierz archiwum odpowiadające Twojej platformie i docelowemu GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Pobierz plik o nazwie `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (gdzie `xxxx` to numer kompilacji).

#### Krok 2: Rozpakuj pliki binarne

Rozpakuj pobrane archiwum:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Ten katalog zawiera teraz kompilacje `llama-cli.exe`, `llama-server.exe` i `ggml-rpc-server.exe` z obsługą ROCm, wstępnie skompilowane dla systemu Ryzen AI Halo.

#### Krok 3: Zweryfikuj wykrywanie GPU

```bash
.\llama-cli.exe --list-devices
```

Oczekiwany wynik:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### Krok 1: Pobierz gotowe pliki binarne

Przejdź do strony najnowszego wydania i pobierz archiwum odpowiadające Twojej platformie i docelowemu GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Pobierz plik o nazwie `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (gdzie `xxxx` to numer kompilacji).

#### Krok 2: Rozpakuj i przygotuj pliki binarne

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Ten katalog zawiera teraz kompilacje `llama-cli`, `llama-server` i `rpc-server` z obsługą ROCm, wstępnie skompilowane dla systemu Ryzen AI Halo.

#### Krok 3: Zweryfikuj wykrywanie GPU

```bash
./llama-cli --list-devices
```

Oczekiwany wynik:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
Po przygotowaniu llama.cpp na każdym węźle, przejdź do sekcji [Pobieranie modelu](#downloading-the-model).

### Opcja 2: Ręczna kompilacja ze źródeł

<!-- @os:windows -->
#### Krok 1: Skompiluj llama.cpp

Otwórz **x64 Native Tools Command Prompt** (zainstalowane wraz z Visual Studio Build Tools) i sklonuj repozytorium:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Dodaj HIP do ścieżki i skompiluj z obsługą ROCm i RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Flaga kompilacji | Przeznaczenie |
|-----------|---------|
| `-DGGML_HIP=ON` | Włącza stos oprogramowania ROCm/HIP |
| `-DGGML_RPC=ON` | Włącza RPC dla wnioskowania rozproszonego |
| `-DGPU_TARGETS=gfx1151` | Kieruje na GPU Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Używa systemu kompilacji Ninja |

#### Krok 2: Zweryfikuj wykrywanie GPU

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

Oczekiwany wynik:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### Krok 3: Dodaj HIP do ścieżki użytkownika

Powyższy krok kompilacji ustawił `%HIP_PATH%\bin` tylko dla bieżącej sesji. Aby udostępnić biblioteki HIP w dowolnym terminalu (nie tylko w x64 Native Tools Command Prompt), dodaj je na stałe do zmiennej `PATH` użytkownika:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Po przygotowaniu llama.cpp na każdym węźle, przejdź do sekcji [Pobieranie modelu](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Krok 1: Skompiluj llama.cpp

Sklonuj repozytorium:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Skompiluj z obsługą ROCm i RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Flaga kompilacji | Przeznaczenie |
|-----------|---------|
| `-DGGML_HIP=ON` | Włącza stos oprogramowania ROCm |
| `-DGGML_RPC=ON` | Włącza RPC dla wnioskowania rozproszonego |
| `-DAMDGPU_TARGETS="gfx1151"` | Kieruje na GPU Ryzen AI Halo (Radeon 8060s) |

Więcej opcji kompilacji znajdziesz w [dokumentacji kompilacji llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Krok 2: Zweryfikuj wykrywanie GPU

```bash
cd rocm/bin
./llama-cli --list-devices
```

Oczekiwany wynik:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

Po przygotowaniu llama.cpp na każdym węźle, przejdź do sekcji [Pobieranie modelu](#downloading-the-model).
<!-- @os:end -->

## Pobieranie modelu

Ten przewodnik wykorzystuje model [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) w kwantyzacji `UD-Q2_K_XL` od [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL). Ta kwantyzacja mieści się w łącznej pamięci GPU czterech węzłów Ryzen AI Halo.

Pobierz pliki GGUF za pomocą interfejsu CLI Hugging Face:
<!-- @os:linux -->
```bash
pip install huggingface-hub
hf download unsloth/Kimi-K2.6-GGUF --include "UD-Q2_K_XL/*" --local-dir Kimi-K2.6-GGUF
```
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/Kimi-K2.6-GGUF --include "UD-Q2_K_XL/*" --local-dir Kimi-K2.6-GGUF
```
<!-- @os:end -->

> **Uwaga**: Pobieranie modelu musi zostać wykonane na Maszynie 1 (kontrolerze). Węzły robocze RPC (Maszyny 2, 3 i 4) nie potrzebują lokalnej kopii plików modelu.

## Uruchamianie modelu w klastrze

Silnik RPC (Remote Procedure Call) llama.cpp umożliwia jednej instancji llama.cpp przekazywanie warstw modelu do zdalnych węzłów roboczych przez sieć. Jedna maszyna pełni rolę **kontrolera** (Maszyna 1), obsługując tokenizację, planowanie i orkiestrację. Pozostałe trzy maszyny uruchamiają lekki **serwer RPC** (Maszyny 2, 3 i 4), który udostępnia kontrolerowi swoją pamięć GPU i moc obliczeniową.

W momencie ładowania llama.cpp dzieli model na fragmenty rozłożone na wszystkie cztery węzły. Po załadowaniu wnioskowanie przebiega tak, jakby działało na pojedynczym akceleratorze. RPC obsługuje w tle transfery tensorów i synchronizację.

### Krok 1: Uruchom serwery RPC (Maszyny 2, 3 i 4)

Na każdej z Maszyn 2, 3 i 4 uruchom serwer RPC, aby udostępnić jej zasoby GPU kontrolerowi:
<!-- @os:linux -->
```bash
./ggml-rpc-server -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
.\ggml-rpc-server.exe -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

| Flaga | Przeznaczenie |
|------|---------|
| `-p` | Port, na którym serwer RPC jest udostępniany |
| `-c` | Włącza lokalną pamięć podręczną dla dużych tensorów, unikając wielokrotnych transferów sieciowych podczas ładowania modelu |
| `--host` | Adres IP, do którego przypisywany jest serwer RPC (`0.0.0.0` dla wszystkich interfejsów) |

Więcej opcji znajdziesz w [dokumentacji RPC llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Krok 2: Uruchom model (Maszyna 1)

Gdy serwery RPC działają na Maszynach 2, 3 i 4, uruchom wnioskowanie z Maszyny 1, używając `llama-cli` lub `llama-server`.
#### llama-cli

`llama-cli` zapewnia interfejs terminalowy do bezpośredniej interakcji z modelem. Jest idealny do testów wydajności, debugowania i eksperymentów na niskim poziomie.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/Kimi-K2.6-GGUF/UD-Q2_K_XL/Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  -b 4096 \
  -ub 4096 \
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **Znajdowanie `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na każdej z maszyn 2, 3 i 4 uruchom `hostname -I | awk '{print $1}'`, aby znaleźć jej lokalny adres IP.
<!-- @os:end -->

<!-- @os:windows -->
> **Uwaga**: Uruchom to polecenie w terminalu (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\Kimi-K2.6-GGUF\UD-Q2_K_XL\Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  -b 4096 `
  -ub 4096 `
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **Znajdowanie `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na każdej z maszyn 2, 3 i 4 uruchom `ipconfig | findstr /C:"IPv4"` w terminalu (Powershell), aby znaleźć jej lokalny adres IP.

<!-- @os:end -->

Po uruchomieniu `llama-cli` wyświetla postęp wczytywania modelu i przechodzi do interaktywnego wiersza poleceń, w którym można prowadzić bezpośredni czat z modelem:

![llama-cli uruchomione z Kimi K2.6 na czterech węzłach](assets/llama-cli-example.png)

#### llama-server

`llama-server` udostępnia ten sam silnik wnioskowania poprzez trwały proces serwera ze zintegrowanym interfejsem webowym i interfejsem API HTTP zgodnym z OpenAI. Jest to preferowany interfejs w przypadku dłużej działających wdrożeń, dostępu wielu użytkowników oraz integracji z zewnętrznymi narzędziami.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/Kimi-K2.6-GGUF/UD-Q2_K_XL/Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  -b 4096 \
  -ub 4096 \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **Znajdowanie `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na każdej z maszyn 2, 3 i 4 uruchom `hostname -I | awk '{print $1}'`, aby znaleźć jej lokalny adres IP.
<!-- @os:end -->

<!-- @os:windows -->
> **Uwaga**: Uruchom to polecenie w terminalu (Powershell).

```powershell
.\llama-server.exe `
  -m C:\path\to\Kimi-K2.6-GGUF\UD-Q2_K_XL\Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  -b 4096 `
  -ub 4096 `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **Znajdowanie `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Na każdej z maszyn 2, 3 i 4 uruchom `ipconfig | findstr /C:"IPv4"` w terminalu (Powershell), aby znaleźć jej lokalny adres IP.
<!-- @os:end -->

Po uruchomieniu otwórz `http://<HOST_IP>:8081` w przeglądarce, aby uzyskać dostęp do wbudowanego interfejsu webowego. Zapewnia on interfejs czatu działający w przeglądarce do interakcji z modelem:

![Interfejs webowy llama-server uruchomiony z Kimi K2.6 na czterech węzłach](assets/llama-server-example.png)

<!-- @os:linux -->
> **Znajdowanie `<HOST_IP>`**: Na maszynie 1 uruchom `hostname -I | awk '{print $1}'`, aby znaleźć jej lokalny adres IP.
<!-- @os:end -->

<!-- @os:windows -->
> **Znajdowanie `<HOST_IP>`**: Na maszynie 1 uruchom `ipconfig | findstr /C:"IPv4"` w terminalu (Powershell), aby znaleźć jej lokalny adres IP.
<!-- @os:end -->

#### Opis parametrów

| Flaga | Przeznaczenie |
|------|---------|
| `-m` | Ścieżka do pliku modelu GGUF (użyj pierwszego fragmentu, `00001-of-00008`) |
| `-c` | Rozmiar kontekstu w tokenach. Większe wartości zużywają więcej pamięci |
| `-fa on` | Włącza rocWMMA Flash Attention w celu poprawy wydajności na GPU AMD |
| `-ngl 999` | Przenosi wszystkie warstwy modelu na GPU |
| `-lm none` | Ustawia tryb wczytywania modelu na `none`, wyłączając mapowanie pamięci (memory-mapping), aby skrócić czas wczytywania, gdy rozmiar modelu przekracza dostępną pamięć RAM systemu, ale mieści się w pamięci VRAM |
| `-b` | Logiczny rozmiar wsadu (batch) w tokenach. Ustawienie na 4096 zapewnia równowagę między przepustowością a zużyciem pamięci na wszystkich węzłach |
| `-ub` | Fizyczny (mikro) rozmiar wsadu do przetwarzania promptu. Ustawienie zgodne z `-b` pozwala uniknąć niepotrzebnego narzutu związanego z dzieleniem na fragmenty |
| `--host` | Adres IP, do którego ma być powiązany `llama-server` (tylko `llama-server`) |
| `--port` | Port, na którym udostępniane jest API HTTP (tylko `llama-server`) |
| `--rpc` | Rozdzielona przecinkami lista punktów końcowych workerów RPC (`IP:port`) |

Pełny opis parametrów można znaleźć w [dokumentacji llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) oraz [dokumentacji llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Kolejne kroki

- **Połącz aplikacje firm trzecich**: `llama-server` udostępnia interfejs API zgodny z OpenAI. Skieruj dowolną aplikację zgodną z OpenAI (na przykład Open WebUI) na adres `http://<HOST_IP>:8081`, podając dowolny zastępczy klucz API (np. `none`), aby połączyć się z klastrem
- **Poznaj inne modele**: Przeglądaj skwantyzowane pliki GGUF w serwisie [Hugging Face](https://huggingface.co/models?search=gguf), aby znaleźć modele mieszczące się w łącznej pamięci GPU klastra
- **Skaluj poza cztery węzły**: Dodaj kolejne systemy Ryzen AI Halo jako dodatkowe workery RPC, aby uzyskać dostęp do modeli przekraczających skalę 1 biliona parametrów. Przekaż dodatkowe punkty końcowe do `--rpc` jako listę rozdzieloną przecinkami (np. `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)