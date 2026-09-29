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

# Klastrowanie dwóch systemów Ryzen™ AI Halo za pomocą RCCL

## Przegląd

Twój Ryzen™ AI Halo już teraz jest w stanie uruchamiać duże modele językowe lokalnie. Klastrowanie idzie o krok dalej, łącząc pamięć GPU wielu systemów za pośrednictwem lokalnej sieci, dając dostęp do jeszcze większych modeli o silniejszym rozumowaniu, lepszej generacji kodu i głębszym rozumieniu wielojęzycznym — w całości na własnym sprzęcie.

Ten przewodnik pokazuje, jak sklastrować dwa systemy Ryzen AI Halo przy użyciu RCCL (ROCm Communication Collectives Library) wraz z vLLM oraz jak uruchomić model Qwen3.5-397B, liczący 397 miliardów parametrów, na obu maszynach jednocześnie z akceleracją ROCm.

## Czego się nauczysz

- Jak rozszerzyć przydział pamięci VRAM w systemach Ryzen AI Halo
- Uruchamianie vLLM z obsługą ROCm
- Konfigurowanie RCCL do wnioskowania z równoległością tensorową typu multi-node na dwóch systemach Ryzen AI Halo
- Uruchamianie modelu liczącego 397 miliardów parametrów na dwóch połączonych w sieć systemach Ryzen AI Halo

## Wymagania wstępne

### Sprzęt

Ten przewodnik wymaga dwóch jednostek Ryzen AI Halo oraz jednego przełącznika Ethernet, połączonych w topologii gwiazdy, gdzie każda jednostka jest podłączona bezpośrednio do przełącznika.

| Komponent | Ilość | Opis |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Węzły obliczeniowe tworzące klaster |
| Przełącznik Ethernet 10 Gb/s | 1 | Centralny przełącznik umożliwiający komunikację wielu węzłów Ryzen AI Halo (co najmniej 2 porty) |
| Kabel Ethernet | 2 | Łączy każdą jednostkę Halo z przełącznikiem (zalecany Cat 7 lub wyższy) |

> **Uwaga**: Do połączenia dwóch jednostek Ryzen AI Halo wymagane są dwa porty przełącznika Ethernet. Trzeci port jest wymagany, jeśli chcesz uzyskać dostęp do modelu z osobnej maszyny klienckiej zamiast z jednej z jednostek Halo.

### Oprogramowanie
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fizyczna konfiguracja sprzętu

> **Uwaga**: Wykonaj ten krok zarówno na Maszynie 1, jak i na Maszynie 2.

Podłącz każdą jednostkę Ryzen AI Halo do przełącznika Ethernet za pomocą kabla Cat 7 (lub wyższego). Ustanawia to łącze 10 Gb/s wykorzystywane do szybkiej komunikacji między węzłami.

### 1. Ustalenie interfejsów sieciowych

Na każdej maszynie znajdź nazwę jej interfejsu sieciowego i zapisz ją (będzie ona nazywana w dalszej części instrukcji `IFNAME`). Uruchom:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Wyświetli to bezpośrednio nazwę interfejsu, na przykład:

```bash
enp191s0
```

### 2. Weryfikacja prędkości łącza sieciowego

Potwierdź, że łącze jest aktywne i działa z pełną prędkością, sprawdzając prędkość interfejsu:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Uwaga**: Zastąp `<IFNAME>` nazwą interfejsu uzyskaną w kroku [1. Ustalenie interfejsów sieciowych](#1-determine-network-interfaces)

Powinieneś zobaczyć prędkość `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Uwaga**: Jeśli prędkość jest niższa niż `10000Mb/s` lub łącze się nie ustanawia, sprawdź podłączenie kabla i upewnij się, że port przełącznika jest ustawiony na 10 Gb/s. Niektóre przełączniki wymagają wyłączenia auto-negocjacji i ręcznego ustawienia prędkości łącza; zapoznaj się z dokumentacją swojego przełącznika.

## Rozszerzanie przydziału pamięci VRAM

> **Uwaga**: Wykonaj ten krok zarówno na Maszynie 1, jak i na Maszynie 2.

### Konfiguracja pamięci do uruchamiania dużych modeli

W systemie Linux ROCm wykorzystuje współdzieloną pulę pamięci systemowej, która domyślnie jest skonfigurowana na połowę pamięci systemowej.

Tę ilość można zwiększyć, zmieniając ustawienie stron Translation Table Manager (TTM) jądra, zgodnie z poniższymi instrukcjami. AMD zaleca ustawienie minimalnej dedykowanej pamięci VRAM w BIOS-ie (0,5 GB).

* Zainstaluj narzędzie pipx i dodaj ścieżkę do pakietów instalowanych przez pipx do systemowej ścieżki wyszukiwania.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Zainstaluj pakiet amd-debug-tools z PyPI.
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

* Zrestartuj system, aby zmiany zostały zastosowane.

## Inicjalizacja kontenera vLLM

> **Uwaga**: Wykonaj ten krok zarówno na Maszynie 1, jak i na Maszynie 2.

Twój Ryzen AI Halo jest dostarczany z vLLM spakowanym wewnątrz gotowego obrazu kontenera, który uruchamiasz za pomocą Podman — darmowego narzędzia do kontenerów o otwartym kodzie źródłowym.

### 1. Utworzenie katalogu pobierania modelu

Gdy uruchomisz model Qwen3.5-397B w tym przewodniku, vLLM automatycznie pobierze wagi modelu do Twojego systemu. Aby upewnić się, że te wagi są dostępne z poziomu kontenera, najpierw utwórz katalog na modele, który kontener będzie mógł zamontować:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Uruchomienie kontenera vLLM

Poniższe polecenie uruchamia kontener i przenosi Cię do interaktywnej powłoki. Montuje utworzony wcześniej katalog na modele oraz przekazuje Twój `IFNAME` do `NCCL_SOCKET_IFNAME` i `GLOO_SOCKET_IFNAME`, informując RCCL (bibliotekę, której vLLM używa do koordynacji GPU w całym klastrze), którego interfejsu użyć.

Uruchom kontener za pomocą:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Uwaga**: Zastąp `<IFNAME>` nazwą interfejsu uzyskaną w kroku [1. Ustalenie interfejsów sieciowych](#1-determine-network-interfaces)

## Uruchamianie modelu na klastrze

vLLM wykorzystuje Ray do orkiestracji klastra oraz RCCL do obsługi komunikacji GPU-GPU między węzłami. Jedna maszyna pełni rolę **węzła głównego** (Maszyna 1), koordynującego wnioskowanie. Druga dołącza jako **węzeł roboczy** (Maszyna 2), wnosząc swoją pamięć GPU i moc obliczeniową.

> **Uwaga**: Ray jest opcjonalną zależnością vLLM i jest dostępny wyłącznie w ramach wstępnie skonfigurowanego kontenera Podman.

Podczas uruchamiania vLLM dzieli model między oba węzły, wykorzystując równoległość tensorową. Po załadowaniu wnioskowanie przebiega tak, jakby odbywało się na pojedynczym akceleratorze.

#### Zapobieganie błędom OOM w Ray

Domyślnie Ray monitoruje pamięć hosta na każdym węźle i zabija największy proces, gdy wykorzystanie pamięci przekroczy 95%. W Twoim Ryzen™ AI Halo GPU i host współdzielą jedną pulę pamięci, więc załadowanie modelu może wywołać `ray.exceptions.OutOfMemoryError` i zabić proces roboczy.

Aby temu zapobiec, przed uruchomieniem i dołączeniem do klastra wyeksportujemy na każdej maszynie zmienną `RAY_memory_monitor_refresh_ms=0`.
### Krok 1: Uruchom węzeł główny Ray (Maszyna 1)

Na Maszynie 1 uruchom węzeł główny Ray, aby zainicjować klaster:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Znajdowanie `<MACHINE_1_IP>`**: Na Maszynie 1 uruchom `hostname -I | awk '{print $1}'`, aby znaleźć jej lokalny adres IP.

### Krok 2: Dołącz do klastra (Maszyna 2)

Na Maszynie 2 połącz się z węzłem głównym, aby utworzyć klaster:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Znajdowanie `<MACHINE_2_IP>`**: Na Maszynie 2 uruchom `hostname -I | awk '{print $1}'`, aby znaleźć jej lokalny adres IP.

### Krok 3: Udostępnij model (Maszyna 1)

Na Maszynie 1 uruchom serwer vLLM. Spowoduje to automatyczne pobranie modelu i rozpoczęcie jego udostępniania na obu węzłach:

```bash
vllm serve Qwen/Qwen3.5-397B-A17B-GPTQ-Int4 \
  --port 7000 \
  --host 0.0.0.0 \
  --max-model-len 32768 \
  --gpu-memory-utilization 0.9 \
  --dtype float16 \
  --tensor-parallel-size 2 \
  --distributed-executor-backend ray \
  --enforce-eager \
  --language-model-only \
  --reasoning-parser qwen3
```

#### Opis parametrów

| Flaga | Przeznaczenie |
|------|---------|
| `--port` | Port, na którym udostępniane jest API HTTP |
| `--host` | Adres IP, do którego przypisany jest serwer (`0.0.0.0` dla wszystkich interfejsów) |
| `--max-model-len` | Maksymalna długość kontekstu w tokenach |
| `--gpu-memory-utilization` | Ułamek pamięci GPU do przydzielenia (0.0–1.0) |
| `--dtype` | Typ danych dla wag modelu |
| `--tensor-parallel-size` | Liczba GPU, między które dzielony jest model (ustaw na łączną liczbę GPU w klastrze) |
| `--distributed-executor-backend` | Backend do wykonywania wieloWęzłowego (`ray` dla wdrożeń klastrowych) |
| `--enforce-eager` | Wyłącza kompilację grafów CUDA w celu zapewnienia zgodności |
| `--language-model-only` | Pomija ładowanie pomocniczych komponentów modelu (np. enkodera wizji) |
| `--reasoning-parser` | Włącza parsowanie ustrukturyzowanego wyniku rozumowania dla modelu |

Pełny opis użycia parametrów znajdziesz w [dokumentacji vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Uzyskiwanie dostępu do modelu

vLLM udostępnia API kompatybilne z OpenAI, dzięki czemu możesz połączyć dowolnego kompatybilnego klienta lub interfejs z klastrem. Jedną z popularnych opcji jest [Open WebUI](https://github.com/open-webui/open-webui), które zapewnia interfejs czatu oparty na przeglądarce.

Aby połączyć Open WebUI z punktem końcowym vLLM:

1. Otwórz **Settings** > **Admin Panel** > **Connections**
2. Kliknij **+** przy **Manage OpenAI API Connections**
3. Ustaw **Connection Type** na **External**
4. Ustaw **URL** na `http://<MACHINE_1_IP>:7000/v1`
5. W sekcji **Auth** wybierz **None** z listy rozwijanej
6. Pozostaw pole **Model IDs** puste, aby automatycznie wykryć wszystkie modele z punktu końcowego

> **Znajdowanie `<MACHINE_1_IP>`**: Na Maszynie 1 uruchom `hostname -I | awk '{print $1}'`, aby znaleźć jej lokalny adres IP. Jeśli korzystasz z Open WebUI bezpośrednio na Maszynie 1, możesz użyć `http://localhost:7000/v1`.

![Ustawienia połączenia Open WebUI dla punktu końcowego vLLM](assets/openwebui-connection.png)

Po nawiązaniu połączenia wybierz model z listy rozwijanej modeli w Open WebUI i rozpocznij czat. Model działa teraz na obu węzłach Ryzen AI Halo:

![Czat z Qwen3.5-397B w Open WebUI](assets/openwebui-chat.png)

## Kolejne kroki

- **Poznaj inne modele**: Odkryj nowe modele na [Hugging Face](https://huggingface.co/models?&sort=trending), które zmieszczą się w łącznej pamięci GPU Twojego klastra
- **Skaluj do czterech węzłów**: Dodaj dwa kolejne systemy Ryzen AI Halo jako dodatkowe procesy robocze Ray, aby dzielić modele na jeszcze większą liczbę GPU. Wymaga to przełącznika Ethernet z co najmniej czterema portami, po jednym dla każdego węzła. Wykonaj [Krok 2: Dołącz do klastra](#step-2-join-the-cluster-machine-2) na każdym dodatkowym procesie roboczym i odpowiednio zwiększ `--tensor-parallel-size`
- **Wypróbuj inne strategie równoległości**: vLLM obsługuje [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) dla modeli typu mixture-of-experts oraz [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) dla większej przepustowości. Poeksperymentuj z `--enable-expert-parallel` i `--data-parallel-size`, aby znaleźć najlepszą konfigurację dla Twojego obciążenia