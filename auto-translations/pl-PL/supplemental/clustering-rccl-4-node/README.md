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

# Klastrowanie czterech systemów Ryzen™ AI Halo za pomocą RCCL

## Omówienie

Twój Ryzen™ AI Halo jest już w stanie uruchamiać duże modele językowe lokalnie. Klastrowanie posuwa to o krok dalej, łącząc pamięć GPU wielu systemów w ramach lokalnej sieci, dając Ci dostęp do jeszcze większych modeli o silniejszym rozumowaniu, lepszym generowaniu kodu i głębszym rozumieniu wielojęzycznym, całkowicie na Twoim własnym sprzęcie.

Ten przewodnik pokazuje, jak sklastrować cztery systemy Ryzen AI Halo za pomocą RCCL (ROCm Communication Collectives Library) z vLLM i uruchomić Qwen3.5-397B, model o 397 miliardach parametrów, na wszystkich czterech maszynach z akceleracją ROCm.

## Czego się nauczysz

- Jak rozszerzyć alokację VRAM w systemach Ryzen AI Halo
- Uruchamianie vLLM z obsługą ROCm
- Konfigurowanie RCCL dla wielowęzłowego wnioskowania z równoległością tensorową na czterech systemach Ryzen AI Halo
- Uruchamianie modelu o 397 miliardach parametrów na czterech połączonych w sieć systemach Ryzen AI Halo

## Wymagania wstępne

### Sprzęt

Ten przewodnik wymaga czterech jednostek Ryzen AI Halo oraz jednego przełącznika Ethernet, połączonych w topologii gwiazdy, przy czym każda jednostka jest podłączona bezpośrednio do przełącznika.

| Komponent | Ilość | Opis |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Węzły obliczeniowe tworzące klaster |
| Przełącznik Ethernet 10 Gb/s | 1 | Centralny przełącznik umożliwiający komunikację wieloma węzłami Ryzen AI Halo (co najmniej 4 porty) |
| Kabel Ethernet | 4 | Łączy każdą jednostkę Halo z przełącznikiem (zalecany Cat 7 lub wyższy) |

> **Uwaga**: Do podłączenia czterech jednostek Ryzen AI Halo wymagane są cztery porty przełącznika Ethernet. Piąty port jest wymagany, jeśli dostęp do modelu odbywa się z osobnej maszyny klienckiej, a nie z jednej z jednostek Halo.

### Oprogramowanie
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Konfiguracja sprzętu fizycznego

> **Uwaga**: Wykonaj ten krok na wszystkich czterech maszynach (Maszyna 1 do Maszyny 4).

Podłącz każdą jednostkę Ryzen AI Halo do przełącznika Ethernet za pomocą kabla Cat 7 (lub wyższego). Ustanawia to łącze 10 Gb/s wykorzystywane do komunikacji o dużej prędkości między węzłami.

### 1. Określenie interfejsów sieciowych

Na każdej maszynie znajdź nazwę jej interfejsu sieciowego i zapisz ją (w dalszej części instrukcji będzie ona nazywana `IFNAME`). Uruchom:

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

> **Uwaga**: Zastąp `<IFNAME>` nazwą interfejsu wyjściowego z kroku [1. Określenie interfejsów sieciowych](#1-determine-network-interfaces)

Powinieneś zobaczyć prędkość `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Uwaga**: Jeśli prędkość jest niższa niż `10000Mb/s` lub łącze nie zostaje nawiązane, sprawdź podłączenie kabla i upewnij się, że port przełącznika jest ustawiony na 10 Gb/s. Niektóre przełączniki wymagają wyłączenia auto-negocjacji i ręcznego ustawienia prędkości łącza; zapoznaj się z dokumentacją swojego przełącznika.

## Rozszerzanie alokacji VRAM

> **Uwaga**: Wykonaj ten krok na wszystkich czterech maszynach (Maszyna 1 do Maszyny 4).

### Konfiguracja pamięci do uruchamiania dużych modeli

W systemie Linux ROCm wykorzystuje współdzieloną pulę pamięci systemowej, a ta pula jest domyślnie skonfigurowana na połowę pamięci systemowej.

Ilość tę można zwiększyć, zmieniając ustawienie stron Translation Table Manager (TTM) jądra, zgodnie z poniższymi instrukcjami. AMD zaleca ustawienie minimalnej dedykowanej pamięci VRAM w BIOS-ie (0,5 GB).

* Zainstaluj narzędzie pipx i dodaj ścieżkę do pakietów wheel zainstalowanych przez pipx do systemowej ścieżki wyszukiwania.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Zainstaluj pakiet wheel amd-debug-tools z PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Uruchom narzędzie amd-ttm, aby odczytać bieżące ustawienia pamięci współdzielonej.
  ```bash
  amd-ttm
  ```

* Zmień konfigurację ustawień pamięci współdzielonej na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Uruchom ponownie system, aby zmiany zaczęły obowiązywać.

## Inicjalizacja kontenera vLLM

> **Uwaga**: Wykonaj ten krok na wszystkich czterech maszynach (Maszyna 1 do Maszyny 4).

Twój Ryzen AI Halo jest dostarczany z vLLM spakowanym wewnątrz gotowego obrazu kontenera, który uruchamiasz za pomocą Podman, darmowego narzędzia do kontenerów typu open source.

### 1. Utworzenie katalogu do pobierania modelu

Gdy w tym przewodniku uruchomisz model Qwen3.5-397B, vLLM automatycznie pobierze wagi modelu do Twojego systemu. Aby upewnić się, że te wagi są dostępne z poziomu kontenera, najpierw utwórz katalog models, który kontener będzie mógł zamontować:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Uruchomienie kontenera vLLM

Poniższe polecenie uruchamia kontener i przenosi Cię do interaktywnej powłoki. Montuje właśnie utworzony katalog models i przekazuje Twój `IFNAME` do `NCCL_SOCKET_IFNAME` oraz `GLOO_SOCKET_IFNAME`, informując RCCL (bibliotekę, której vLLM używa do koordynowania GPU w całym klastrze), którego interfejsu użyć.

Uruchom kontener za pomocą:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Uwaga**: Zastąp `<IFNAME>` nazwą interfejsu wyjściowego z kroku [1. Określenie interfejsów sieciowych](#1-determine-network-interfaces)

## Uruchamianie modelu na klastrze

vLLM wykorzystuje Ray do orkiestracji klastra oraz RCCL do obsługi komunikacji GPU-GPU między węzłami. Jedna maszyna pełni rolę węzła głównego (Maszyna 1), koordynując wnioskowanie. Pozostałe trzy dołączają jako węzły robocze (Maszyny 2, 3 i 4), udostępniając swoją pamięć GPU i moc obliczeniową.

> **Uwaga**: Ray jest opcjonalną zależnością dla vLLM i jest dostępny wyłącznie z poziomu wstępnie skonfigurowanego kontenera Podman.

Przy uruchomieniu vLLM dzieli model na wszystkie cztery węzły, wykorzystując równoległość tensorową. Po załadowaniu wnioskowanie przebiega tak, jakby odbywało się na pojedynczym akceleratorze.

#### Zapobieganie błędom OOM w Ray

Domyślnie Ray monitoruje pamięć hosta na każdym węźle i zabija największy proces, gdy wykorzystanie pamięci przekroczy 95%. Na Twoim Ryzen™ AI Halo GPU i host współdzielą jedną pulę pamięci, więc ładowanie modelu może wywołać błąd `ray.exceptions.OutOfMemoryError` i zakończyć proces roboczy.

Aby temu zapobiec, wyeksportujemy `RAY_memory_monitor_refresh_ms=0` na każdej maszynie przed uruchomieniem i dołączeniem do klastra.
### Krok 1: Uruchom węzeł główny Ray (Maszyna 1)

Na Maszynie 1 uruchom węzeł główny Ray, aby zainicjować klaster:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Znajdowanie `<MACHINE_1_IP>`**: Na Maszynie 1 uruchom `hostname -I | awk '{print $1}'`, aby znaleźć jej lokalny adres IP.

### Krok 2: Dołącz do klastra (Maszyny 2, 3 i 4)

Na każdej z Maszyn 2, 3 i 4 połącz się z węzłem głównym, aby utworzyć klaster:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_N_IP> --num-gpus=1
```

> **Znajdowanie `<MACHINE_N_IP>`**: Na każdej maszynie roboczej uruchom `hostname -I | awk '{print $1}'`, aby znaleźć jej lokalny adres IP.

### Krok 3: Udostępnij model (Maszyna 1)

Na Maszynie 1 uruchom serwer vLLM. Spowoduje to automatyczne pobranie modelu i rozpoczęcie jego udostępniania na wszystkich czterech węzłach:

```bash
vllm serve Qwen/Qwen3.5-397B-A17B-GPTQ-Int4 \
  --port 7000 \
  --host 0.0.0.0 \
  --max-model-len 131072 \
  --gpu-memory-utilization 0.8 \
  --dtype float16 \
  --tensor-parallel-size 4 \
  --distributed-executor-backend ray \
  --enforce-eager \
  --language-model-only \
  --reasoning-parser qwen3
```

#### Opis parametrów

| Flaga | Przeznaczenie |
|------|---------|
| `--port` | Port, na którym udostępniane jest API HTTP |
| `--host` | Adres IP, do którego przypisywany jest serwer (`0.0.0.0` dla wszystkich interfejsów) |
| `--max-model-len` | Maksymalna długość kontekstu w tokenach |
| `--gpu-memory-utilization` | Ułamek pamięci GPU do przydzielenia (0.0–1.0) |
| `--dtype` | Typ danych dla wag modelu |
| `--tensor-parallel-size` | Liczba GPU, między którymi dzielony jest model (ustaw na łączną liczbę GPU w klastrze) |
| `--distributed-executor-backend` | Backend do wykonywania na wielu węzłach (`ray` dla wdrożeń klastrowych) |
| `--enforce-eager` | Wyłącza kompilację grafów CUDA dla zapewnienia zgodności |
| `--language-model-only` | Pomija ładowanie pomocniczych komponentów modelu (np. enkodera wizji) |
| `--reasoning-parser` | Włącza strukturalne parsowanie wyników rozumowania dla modelu |

Pełny opis użycia parametrów znajdziesz w [dokumentacji vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Dostęp do modelu

vLLM udostępnia API zgodne z OpenAI, dzięki czemu możesz połączyć dowolnego kompatybilnego klienta lub interfejs ze swoim klastrem. Jedną z popularnych opcji jest [Open WebUI](https://github.com/open-webui/open-webui), który zapewnia interfejs czatu działający w przeglądarce.

Aby połączyć Open WebUI z punktem końcowym vLLM:

1. Otwórz **Settings** > **Admin Panel** > **Connections**
2. Kliknij **+** przy **Manage OpenAI API Connections**
3. Ustaw **Connection Type** na **External**
4. Ustaw **URL** na `http://<MACHINE_1_IP>:7000/v1`
5. W sekcji **Auth** wybierz **None** z listy rozwijanej
6. Pozostaw pole **Model IDs** puste, aby automatycznie wykryć wszystkie modele z punktu końcowego

> **Znajdowanie `<MACHINE_1_IP>`**: Na Maszynie 1 uruchom `hostname -I | awk '{print $1}'`, aby znaleźć jej lokalny adres IP. Jeśli korzystasz z Open WebUI bezpośrednio na Maszynie 1, możesz użyć `http://localhost:7000/v1`.

![Ustawienia połączenia Open WebUI dla punktu końcowego vLLM](assets/openwebui-connection.png)

Po nawiązaniu połączenia wybierz model z listy rozwijanej modeli w Open WebUI i rozpocznij czat. Model działa teraz na wszystkich czterech węzłach Ryzen AI Halo:

![Czat z Qwen3.5-397B w Open WebUI](assets/openwebui-chat.png)

## Kolejne kroki

- **Poznaj inne modele**: Odkryj nowe modele na [Hugging Face](https://huggingface.co/models?&sort=trending), które mieszczą się w łącznej pamięci GPU Twojego klastra
- **Skaluj poza cztery węzły**: Dodaj kolejne systemy Ryzen AI Halo jako dodatkowe węzły robocze Ray, aby dzielić modele między jeszcze większą liczbę GPU. Wykonaj [Krok 2: Dołącz do klastra](#step-2-join-the-cluster-machines-2-3-and-4) na każdej dodatkowej maszynie roboczej i odpowiednio zwiększ wartość `--tensor-parallel-size`
- **Wypróbuj inne strategie równoległości**: vLLM obsługuje [równoległość ekspertów](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) dla modeli typu mixture-of-experts oraz [równoległość danych](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) dla większej przepustowości. Eksperymentuj z `--enable-expert-parallel` i `--data-parallel-size`, aby znaleźć najlepszą konfigurację dla swojego obciążenia roboczego