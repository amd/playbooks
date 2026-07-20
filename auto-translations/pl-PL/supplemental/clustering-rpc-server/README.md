<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ten podręcznik korzysta ze specjalnych tagów, których GitHub nie potrafi wyrenderować. Aby poprawnie wyświetlić tę treść, odwiedź stronę [amd.com/playbooks](https://amd.com/playbooks).
<!-- @github-only:end -->

# Łączenie dwóch systemów Ryzen™ AI Halo w klaster za pomocą RPC

## Przegląd

Twój system Ryzen™ AI Halo jest już w stanie lokalnie uruchamiać duże modele językowe. Klastrowanie idzie o krok dalej, łącząc pamięć GPU wielu systemów w ramach lokalnej sieci, dając dostęp do jeszcze większych modeli o mocniejszym rozumowaniu, lepszym generowaniu kodu i głębszym rozumieniu wielojęzycznym, całkowicie na Twoim własnym sprzęcie.

Ten podręcznik pokazuje, jak połączyć w klaster dwa systemy Ryzen AI Halo za pomocą silnika RPC z llama.cpp i uruchomić model GLM 4.7 o 358 miliardach parametrów na obu maszynach jednocześnie, z akceleracją AMD ROCm™.

## Czego się nauczysz

- Jak rozszerzyć alokację pamięci VRAM na systemach Ryzen AI Halo
- Instalowanie llama.cpp z obsługą ROCm i RPC
- Konfigurowanie workera RPC i uruchamianie rozproszonego wnioskowania na dwóch węzłach
- Uruchamianie modelu o 358 miliardach parametrów na dwóch połączonych siecią systemach Ryzen AI Halo

## Konfiguracja pamięci

> **Uwaga**: Wykonaj ten krok zarówno na Maszynie 1, jak i na Maszynie 2.

<!-- @os:windows -->
W systemie Windows, aby uruchamiać większe modele wymagające większej ilości pamięci, musimy skorzystać z alokacji AMD Variable Graphics Memory (pamięć VRAM iGPU).

Można to zrobić, otwierając panel sterowania AMD Software: Adrenalin Edition i przechodząc do: `Performance > Tuning > AMD Variable Graphics Memory`. Ustaw wartość na **96 GB**. Uruchom ponownie system, aby zmiany zaczęły obowiązywać.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
W systemie Linux ROCm korzysta ze współdzielonej puli pamięci systemowej, która domyślnie jest skonfigurowana na połowę pamięci systemowej.

Ilość tę można zwiększyć, zmieniając ustawienie stron Translation Table Manager (TTM) w jądrze systemu, zgodnie z poniższymi instrukcjami. AMD zaleca ustawienie minimalnej dedykowanej pamięci VRAM w BIOS-ie (0,5 GB).

* Zainstaluj narzędzie pipx i dodaj ścieżkę do zainstalowanych przez pipx pakietów wheel do systemowej ścieżki wyszukiwania.

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

* Uruchom ponownie system, aby zmiany zaczęły obowiązywać.


<!-- @os:end -->
<!-- @device:halo_box -->
## Sprawdzanie aktualizacji oprogramowania

<!-- @require:software-update -->
<!-- @device:end -->
## Wymagania wstępne

### Sprzęt

Ten podręcznik wymaga dwóch jednostek Ryzen AI Halo i jednego przełącznika Ethernet, połączonych w topologii gwiazdy, gdzie każda jednostka jest podłączona bezpośrednio do przełącznika.

| Komponent | Ilość | Opis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Węzły obliczeniowe tworzące klaster |
| Przełącznik Ethernet 10Gbps | 1 | Centralny przełącznik umożliwiający komunikację wielowęzłową Ryzen AI Halo (co najmniej 2 porty) |
| Kabel Ethernet | 2 | Łączy każdą jednostkę Halo z przełącznikiem (zalecany Cat 7 lub wyższy) |

> **Uwaga**: Do połączenia dwóch jednostek Ryzen AI Halo wymagane są dwa porty przełącznika Ethernet. Trzeci port jest wymagany, jeśli dostęp do modelu odbywa się z osobnej maszyny klienckiej zamiast z jednej z jednostek Halo.

### Oprogramowanie
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Zainstaluj:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) z zestawem funkcji **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Konfiguracja fizycznego sprzętu

> **Uwaga**: Wykonaj ten krok zarówno na Maszynie 1, jak i na Maszynie 2.

Podłącz każdą jednostkę Ryzen AI Halo do przełącznika Ethernet za pomocą kabla Cat 7 (lub wyższego). Ustanawia to łącze 10Gbps wykorzystywane do szybkiej komunikacji między węzłami.
<!-- @os:linux -->
### 1. Ustalenie interfejsów sieciowych

Na każdej maszynie znajdź nazwę jej interfejsu sieciowego i zapisz ją (będzie ona nazywana poniżej `IFNAME`). Uruchom:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Wyświetli to bezpośrednio nazwę interfejsu, na przykład:

```bash
enp191s0
```

### 2. Weryfikacja prędkości łącza sieciowego

Potwierdź, że łącze jest aktywne i działa z pełną prędkością, sprawdzając prędkość swojego interfejsu:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Uwaga**: Zastąp `<IFNAME>` nazwą interfejsu wyjściowego z sekcji [1. Ustalenie interfejsów sieciowych](#1-determine-network-interfaces)

Powinieneś zobaczyć prędkość `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Uwaga**: Jeśli prędkość jest niższa niż `10000Mb/s` lub łącze nie zostaje nawiązane, sprawdź podłączenie kabla i upewnij się, że port przełącznika jest ustawiony na 10Gbps. Niektóre przełączniki wymagają wyłączenia auto-negocjacji i ręcznego ustawienia prędkości łącza; zapoznaj się z dokumentacją swojego przełącznika.

<!-- @os:end -->

<!-- @os:windows -->
### Weryfikacja prędkości łącza sieciowego

Na każdej maszynie sprawdź prędkość łącza swoich interfejsów sieciowych:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Twój interfejs Ethernet powinien być w stanie `Up` i działać z prędkością `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Uwaga**: Jeśli prędkość jest niższa niż `10 Gbps` lub łącze nie zostaje nawiązane, sprawdź podłączenie kabla i upewnij się, że port przełącznika jest ustawiony na 10Gbps. Niektóre przełączniki wymagają wyłączenia auto-negocjacji i ręcznego ustawienia prędkości łącza; zapoznaj się z dokumentacją swojego przełącznika.

<!-- @os:end -->

## Instalowanie llama.cpp

> **Uwaga**: Wykonaj ten krok zarówno na Maszynie 1, jak i na Maszynie 2.

Dostępne są dwie opcje instalacji:

- [Opcja 1: Lemonade SDK (Zalecane)](#option-1-lemonade-sdk-recommended) - gotowe pliki binarne, najszybsza konfiguracja
- [Opcja 2: Ręczna kompilacja ze źródeł](#option-2-manual-source-build) - kompilacja ze źródeł z pełną kontrolą nad flagami kompilacji

### Opcja 1: Lemonade SDK (Zalecane)

Lemonade SDK dostarcza nocne kompilacje llama.cpp z akceleracją AMD ROCm 7, przeznaczone dla GPU takich jak gfx1151 (Strix Halo / Ryzen AI Max+ 395) oraz innych nowszych architektur Radeon.

<!-- @os:windows -->
#### Krok 1: Pobierz gotowe pliki binarne

Przejdź na stronę najnowszego wydania i pobierz archiwum odpowiadające Twojej platformie i docelowemu GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Pobierz plik o nazwie `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (gdzie `xxxx` to numer kompilacji).

#### Krok 2: Rozpakuj pliki binarne

Rozpakuj pobrane archiwum:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Ten katalog zawiera teraz kompilacje `llama-cli.exe`, `llama-server.exe` i `rpc-server.exe` z obsługą ROCm, wstępnie skompilowane dla Twojego systemu Ryzen AI Halo.

#### Krok 3: Zweryfikuj wykrycie GPU

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

Przejdź na stronę najnowszego wydania i pobierz archiwum odpowiadające Twojej platformie i docelowemu GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Pobierz plik o nazwie `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (gdzie `xxxx` to numer kompilacji).

#### Krok 2: Rozpakuj i przygotuj pliki binarne

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Ten katalog zawiera teraz kompilacje `llama-cli`, `llama-server` i `rpc-server` z obsługą ROCm, wstępnie skompilowane dla Twojego systemu Ryzen AI Halo.

#### Krok 3: Zweryfikuj wykrycie GPU

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

Otwórz **x64 Native Tools Command Prompt** (zainstalowany razem z Visual Studio Build Tools) i sklonuj repozytorium:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Dodaj HIP do swojej ścieżki i skompiluj z obsługą ROCm i RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Flaga kompilacji | Cel |
|-----------|---------|
| `-DGGML_HIP=ON` | Włącza stos oprogramowania ROCm/HIP |
| `-DGGML_RPC=ON` | Włącza RPC dla rozproszonego wnioskowania |
| `-DGPU_TARGETS=gfx1151` | Kieruje kompilację na GPU Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Używa systemu budowania Ninja |

#### Krok 2: Zweryfikuj wykrycie GPU

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

#### Krok 3: Dodaj HIP do swojej ścieżki użytkownika

Powyższy krok kompilacji ustawił `%HIP_PATH%\bin` tylko dla bieżącej sesji. Aby biblioteki HIP były dostępne w dowolnym terminalu (nie tylko w x64 Native Tools Command Prompt), dodaj tę ścieżkę na stałe do zmiennej `PATH` użytkownika:

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
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Flaga kompilacji | Cel |
|-----------|---------|
| `-DGGML_HIP=ON` | Włącza stos oprogramowania ROCm |
| `-DGGML_RPC=ON` | Włącza RPC dla rozproszonego wnioskowania |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Włącza rocWMMA dla ulepszonej Flash Attention na GPU AMD |
| `-DAMDGPU_TARGETS="gfx1151"` | Kieruje kompilację na GPU Ryzen AI Halo (Radeon 8060s) |

Więcej opcji kompilacji znajdziesz w [dokumentacji budowania llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Krok 2: Zweryfikuj wykrycie GPU

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

Ten przewodnik korzysta z modelu [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), modelu z 358 miliardami parametrów w kwantyzacji `Q4_K_XL` od [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Przy tej kwantyzacji model wymaga około 205 GB pamięci masowej i mieści się w łącznej pamięci GPU dwóch węzłów Ryzen AI Halo.

Pobierz pliki GGUF za pomocą interfejsu wiersza poleceń Hugging Face:
<!-- @os:linux -->
```bash
pip install huggingface-hub
hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

> **Uwaga**: Pobieranie modelu musi zostać wykonane na Maszynie 1 (kontrolerze). Węzły robocze RPC nie potrzebują lokalnej kopii plików modelu.

## Uruchamianie modelu w klastrze

Silnik RPC (Remote Procedure Call) llama.cpp umożliwia pojedynczej instancji llama.cpp przekazywanie warstw modelu do zdalnych węzłów roboczych przez sieć. Jedna maszyna pełni rolę **kontrolera** (Maszyna 1), obsługując tokenizację, planowanie i orkiestrację. Druga maszyna uruchamia lekki **serwer RPC** (Maszyna 2), który udostępnia swoją pamięć GPU i moc obliczeniową kontrolerowi.

W momencie ładowania llama.cpp dzieli model pomiędzy oba węzły. Po załadowaniu wnioskowanie przebiega tak, jakby działało na pojedynczym akceleratorze. RPC zajmuje się przesyłaniem tensorów i synchronizacją w tle.

### Krok 1: Uruchom serwer RPC (Maszyna 2)

Na Maszynie 2 uruchom serwer RPC, aby udostępnić jej zasoby GPU kontrolerowi:
<!-- @os:linux -->
```bash
./rpc-server -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
.\rpc-server.exe -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

| Flaga | Cel |
|------|---------|
| `-p` | Port, na którym rozgłaszany jest serwer RPC |
| `-c` | Włącza lokalny cache dla dużych tensorów, unikając powtarzających się transferów sieciowych podczas ładowania modelu |
| `--host` | Adres IP, do którego ma zostać przypisany serwer RPC (`0.0.0.0` dla wszystkich interfejsów) |

Więcej opcji znajdziesz w [dokumentacji RPC llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Krok 2: Uruchom model (Maszyna 1)

Po uruchomieniu serwera RPC na Maszynie 2, uruchom wnioskowanie z Maszyny 1, używając `llama-cli` lub `llama-server`.

#### llama-cli

`llama-cli` zapewnia interfejs terminalowy do bezpośredniej interakcji z modelem. Jest idealny do testów wydajności, debugowania i eksperymentów na niskim poziomie.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --rpc <RPC_WORKER_IP>:50053
```

> **Znajdowanie `<RPC_WORKER_IP>`**: Na Maszynie 2 uruchom `hostname -I | awk '{print $1}'`, aby znaleźć jej lokalny adres IP.
<!-- @os:end -->

<!-- @os:windows -->
> **Uwaga**: Uruchom to polecenie w Terminalu (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **Znajdowanie `<RPC_WORKER_IP>`**: Na Maszynie 2 uruchom `ipconfig | findstr /C:"IPv4"` w Terminalu (Powershell), aby znaleźć jej lokalny adres IP.

<!-- @os:end -->

Po uruchomieniu `llama-cli` wyświetla postęp ładowania modelu i przechodzi do interaktywnego trybu, w którym możesz bezpośrednio rozmawiać z modelem:

![llama-cli uruchamiający GLM 4.7 na dwóch węzłach](assets/llama-cli-example.png)
#### llama-server

`llama-server` udostępnia ten sam silnik wnioskowania poprzez trwały proces serwera z zintegrowanym interfejsem webowym oraz API HTTP zgodnym z OpenAI. Jest to preferowany interfejs w przypadku dłużej działających wdrożeń, dostępu wielu użytkowników oraz integracji z zewnętrznymi narzędziami.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_IP>:50053
```

> **Znajdowanie `<RPC_WORKER_IP>`**: Na Maszynie 2 uruchom `hostname -I | awk '{print $1}'`, aby znaleźć jej lokalny adres IP.
<!-- @os:end -->

<!-- @os:windows -->
> **Uwaga**: Uruchom to polecenie w Terminalu (Powershell).

```powershell
.\llama-server.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_IP>:50053
```

> **Znajdowanie `<RPC_WORKER_IP>`**: Na Maszynie 2 uruchom `ipconfig | findstr /C:"IPv4"` w Terminalu (Powershell), aby znaleźć jej lokalny adres IP.
<!-- @os:end -->

Po uruchomieniu otwórz `http://<HOST_IP>:8081` w przeglądarce, aby uzyskać dostęp do wbudowanego interfejsu webowego. Zapewnia on interfejs czatu oparty na przeglądarce do interakcji z modelem:

![Interfejs webowy llama-server uruchomiony z GLM 4.7 na dwóch węzłach](assets/llama-server-example.png)

<!-- @os:linux -->
> **Znajdowanie `<HOST_IP>`**: Na Maszynie 1 uruchom `hostname -I | awk '{print $1}'`, aby znaleźć jej lokalny adres IP.
<!-- @os:end -->

<!-- @os:windows -->
> **Znajdowanie `<HOST_IP>`**: Na Maszynie 1 uruchom `ipconfig | findstr /C:"IPv4"` w Terminalu (Powershell), aby znaleźć jej lokalny adres IP.
<!-- @os:end -->

#### Opis parametrów

| Flaga | Przeznaczenie |
|------|---------|
| `-m` | Ścieżka do pliku modelu GGUF (użyj pierwszego fragmentu, `00001-of-00005`) |
| `-c` | Rozmiar kontekstu w tokenach. Większe wartości zużywają więcej pamięci |
| `-fa on` | Włącza rocWMMA Flash Attention w celu poprawy wydajności na GPU AMD |
| `-ngl 999` | Przenosi wszystkie warstwy modelu do GPU |
| `--no-mmap` | Wyłącza mapowanie pamięci, skracając czas ładowania, gdy rozmiar modelu przekracza pamięć RAM systemu, ale mieści się w VRAM |
| `--host` | Adres IP, do którego ma być powiązany `llama-server` (tylko `llama-server`) |
| `--port` | Port, na którym udostępniane jest API HTTP (tylko `llama-server`) |
| `--rpc` | Lista punktów końcowych workerów RPC rozdzielona przecinkami (`IP:port`) |

Pełny opis użycia parametrów można znaleźć w [dokumentacji llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) oraz [dokumentacji llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Kolejne kroki

- **Połącz aplikacje firm trzecich**: `llama-server` udostępnia API zgodne z OpenAI. Skieruj dowolną aplikację zgodną z OpenAI (np. Open WebUI) na adres `http://<HOST_IP>:8081`, podając dowolny zastępczy klucz API (np. `none`), aby połączyć się z klastrem
- **Poznaj inne modele**: Przeglądaj skwantyzowane pliki GGUF na [Hugging Face](https://huggingface.co/models?search=gguf), aby znaleźć modele mieszczące się w łącznej pamięci GPU klastra
- **Skaluj do czterech węzłów**: Dodaj dwa kolejne systemy Ryzen AI Halo jako dodatkowe workery RPC, aby uzyskać dostęp do modeli o skali biliona parametrów. Przekaż dodatkowe punkty końcowe do `--rpc` jako listę rozdzieloną przecinkami (np. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)