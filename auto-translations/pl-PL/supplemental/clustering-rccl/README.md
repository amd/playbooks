<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Klastrowanie dwóch systemów Ryzen™ AI Halo z RCCL

## Przegląd

Twój Ryzen™ AI Halo jest już zdolny do lokalnego uruchamiania dużych modeli językowych. Klastrowanie idzie o krok dalej, łącząc pamięć GPU wielu systemów przez sieć lokalną, co daje dostęp do jeszcze większych modeli z silniejszym rozumowaniem, lepszym generowaniem kodu i głębszym rozumieniem wielojęzycznym — wszystko wyłącznie na własnym sprzęcie.

Ten poradnik uczy, jak klastrować dwa systemy Ryzen AI Halo przy użyciu RCCL (ROCm Communication Collectives Library) z vLLM oraz uruchamiać Qwen3.5-397B, model o 397 miliardach parametrów, na obu maszynach z akceleracją ROCm.

## Czego się nauczysz

- Jak rozszerzyć alokację VRAM w systemach Ryzen AI Halo
- Uruchamianie vLLM z obsługą ROCm
- Konfigurowanie RCCL do wielowęzłowego wnioskowania z równoległością tensorową na dwóch systemach Ryzen AI Halo
- Uruchamianie modelu o 397 miliardach parametrów na dwóch połączonych sieciowo systemach Ryzen AI Halo

## Wymagania wstępne

### Sprzęt

Ten poradnik wymaga dwóch jednostek Ryzen AI Halo oraz jednego przełącznika Ethernet, połączonych w topologii gwiazdy, gdzie każda jednostka jest podłączona bezpośrednio do przełącznika.

| Komponent | Ilość | Opis |
|-----------|-------|-------|
| Ryzen AI Halo | 2 | Węzły obliczeniowe tworzące klaster |
| Przełącznik Ethernet 10 Gbps | 1 | Centralny przełącznik umożliwiający komunikację między węzłami Ryzen AI Halo (co najmniej 2 porty) |
| Kabel Ethernet | 2 | Łączy każdą jednostkę Halo z przełącznikiem (zalecany Cat 7 lub wyższy) |

> **Uwaga**: Do połączenia dwóch jednostek Ryzen AI Halo wymagane są dwa porty przełącznika Ethernet. Trzeci port jest potrzebny, jeśli dostęp do modelu uzyskujesz z oddzielnej maszyny klienckiej zamiast z jednej z jednostek Halo.

### Oprogramowanie
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Fizyczna konfiguracja sprzętu

> **Uwaga**: Wykonaj ten krok na obu maszynach — Maszynie 1 i Maszynie 2.

Podłącz każdą jednostkę Ryzen AI Halo do przełącznika Ethernet kablem Cat 7 (lub wyższym). Ustanawia to łącze 10 Gbps używane do szybkiej komunikacji między węzłami.

### 1. Określenie interfejsów sieciowych

Na każdej maszynie znajdź nazwę jej interfejsu sieciowego i zanotuj ją (w dalszej części instrukcji będzie ona określana jako `IFNAME`). Uruchom:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Wyświetla to bezpośrednio nazwę interfejsu, na przykład:

```bash
enp191s0
```

### 2. Weryfikacja prędkości łącza sieciowego

Potwierdź, że łącze jest aktywne i działa z pełną prędkością, sprawdzając prędkość swojego interfejsu:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Uwaga**: Zastąp `<IFNAME>` nazwą interfejsu wyjściowego z [1. Określenie interfejsów sieciowych](#1-determine-network-interfaces)

Powinieneś zobaczyć prędkość `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Uwaga**: Jeśli prędkość jest niższa niż `10000Mb/s` lub łącze nie nawiązuje połączenia, sprawdź połączenie kablowe i upewnij się, że port przełącznika jest ustawiony na 10 Gbps. Niektóre przełączniki wymagają wyłączenia automatycznej negocjacji i ręcznego ustawienia prędkości łącza; zapoznaj się z dokumentacją swojego przełącznika.

## Rozszerzanie alokacji VRAM

> **Uwaga**: Wykonaj ten krok na obu maszynach — Maszynie 1 i Maszynie 2.

### Konfiguracja pamięci do uruchamiania dużych modeli

W systemie Linux ROCm wykorzystuje współdzieloną pulę pamięci systemowej, która domyślnie jest skonfigurowana na połowę pamięci systemowej.

Tę wartość można zwiększyć, zmieniając ustawienie strony Translation Table Manager (TTM) jądra, zgodnie z poniższymi instrukcjami. AMD zaleca ustawienie minimalnej dedykowanej pamięci VRAM w BIOS-ie (0,5 GB).

* Zainstaluj narzędzie pipx i dodaj ścieżkę dla kół zainstalowanych przez pipx do systemowej ścieżki wyszukiwania.

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

* Skonfiguruj ponownie ustawienia pamięci współdzielonej na **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Uruchom ponownie system, aby zmiany zostały zastosowane.

## Inicjalizacja kontenera vLLM

> **Uwaga**: Wykonaj ten krok na obu maszynach — Maszynie 1 i Maszynie 2.

Twój Ryzen AI Halo jest dostarczany z vLLM spakowanym wewnątrz gotowego obrazu kontenera, który uruchamiasz za pomocą Podman — bezpłatnego narzędzia do kontenerów o otwartym kodzie źródłowym.

### 1. Utwórz katalog pobierania modeli

Gdy w tym poradniku uruchomisz model Qwen3.5-397B, vLLM automatycznie pobierze wagi modelu do Twojego systemu. Aby upewnić się, że te wagi są dostępne z wnętrza kontenera, najpierw utwórz katalog modeli, który kontener może zamontować:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Uruchom kontener vLLM

Poniższe polecenie uruchamia kontener i przenosi Cię do interaktywnej powłoki. Montuje katalog modeli, który właśnie utworzyłeś, i przekazuje Twój `IFNAME` do `NCCL_SOCKET_IFNAME` oraz `GLOO_SOCKET_IFNAME`, informując RCCL (bibliotekę używaną przez vLLM do koordynacji GPU w klastrze), którego interfejsu użyć.

Uruchom kontener poleceniem:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Uwaga**: Zastąp `<IFNAME>` nazwą interfejsu wyjściowego z [1. Określenie interfejsów sieciowych](#1-determine-network-interfaces)

## Uruchamianie modelu na klastrze

vLLM używa Ray do orkiestracji klastra i RCCL do obsługi komunikacji GPU-GPU między węzłami. Jedna maszyna pełni rolę **węzła głównego** (Maszyna 1), koordynując wnioskowanie. Druga dołącza jako **węzeł roboczy** (Maszyna 2), wnosząc swoją pamięć GPU i moc obliczeniową.

> **Uwaga**: Ray jest opcjonalną zależnością dla vLLM i jest dostępny wyłącznie z poziomu wstępnie skonfigurowanego kontenera Podman.

Podczas uruchamiania vLLM dzieli model na oba węzły przy użyciu równoległości tensorowej. Po załadowaniu wnioskowanie przebiega tak, jakby działało na jednym akceleratorze.

### Krok 1: Uruchom węzeł główny Ray (Maszyna 1)

Na Maszynie 1 uruchom węzeł główny Ray, aby zainicjalizować klaster:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Znajdowanie `<MACHINE_1_IP>`**: Na Maszynie 1 uruchom `hostname -I | awk '{print $1}'`, aby znaleźć jej lokalny adres IP.

### Krok 2: Dołącz do klastra (Maszyna 2)

Na Maszynie 2 połącz się z węzłem głównym, aby utworzyć klaster:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Znajdowanie `<MACHINE_2_IP>`**: Na Maszynie 2 uruchom `hostname -I | awk '{print $1}'`, aby znaleźć jej lokalny adres IP.

### Krok 3: Uruchom model (Maszyna 1)

Na Maszynie 1 uruchom serwer vLLM. Automatycznie pobierze on model i rozpocznie jego obsługę na obu węzłach:

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
|-------|--------------|
| `--port` | Port, na którym ma być udostępniane API HTTP |
| `--host` | Adres IP, do którego ma być przypisany serwer (`0.0.0.0` dla wszystkich interfejsów) |
| `--max-model-len` | Maksymalna długość kontekstu w tokenach |
| `--gpu-memory-utilization` | Ułamek pamięci GPU do przydzielenia (0,0–1,0) |
| `--dtype` | Typ danych dla wag modelu |
| `--tensor-parallel-size` | Liczba GPU, na które ma być podzielony model (ustaw na łączną liczbę GPU w klastrze) |
| `--distributed-executor-backend` | Backend do wielowęzłowego wykonywania (`ray` dla wdrożeń klastrowych) |
| `--enforce-eager` | Wyłącza kompilację grafu CUDA dla zapewnienia zgodności |
| `--language-model-only` | Pomija ładowanie pomocniczych komponentów modelu (np. enkodera wizji) |
| `--reasoning-parser` | Włącza strukturalne parsowanie wyników rozumowania dla modelu |

Pełne informacje o użyciu parametrów znajdziesz w [dokumentacji vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Dostęp do modelu

vLLM udostępnia API zgodne z OpenAI, dzięki czemu możesz podłączyć dowolny zgodny klient lub interfejs do swojego klastra. Jedną z popularnych opcji jest [Open WebUI](https://github.com/open-webui/open-webui), który zapewnia oparty na przeglądarce interfejs czatu.

Aby połączyć Open WebUI z punktem końcowym vLLM:

1. Otwórz **Ustawienia** > **Panel administratora** > **Połączenia**
2. Kliknij **+** przy **Zarządzaj połączeniami OpenAI API**
3. Ustaw **Typ połączenia** na **Zewnętrzny**
4. Ustaw **URL** na `http://<MACHINE_1_IP>:7000/v1`
5. W sekcji **Uwierzytelnianie** wybierz **Brak** z listy rozwijanej
6. Pozostaw pole **Identyfikatory modeli** puste, aby automatycznie wykryć wszystkie modele z punktu końcowego

> **Znajdowanie `<MACHINE_1_IP>`**: Na Maszynie 1 uruchom `hostname -I | awk '{print $1}'`, aby znaleźć jej lokalny adres IP. Jeśli uzyskujesz dostęp do Open WebUI z samej Maszyny 1, możesz użyć `http://localhost:7000/v1`.

![Ustawienia połączenia Open WebUI dla punktu końcowego vLLM](assets/openwebui-connection.png)

Po nawiązaniu połączenia wybierz model z listy rozwijanej modeli w Open WebUI i rozpocznij rozmowę. Model działa teraz na obu węzłach Ryzen AI Halo:

![Rozmowa z Qwen3.5-397B w Open WebUI](assets/openwebui-chat.png)

## Kolejne kroki

- **Odkrywaj inne modele**: Znajdź nowe modele na [Hugging Face](https://huggingface.co/models?&sort=trending), które mieszczą się w łącznej pamięci GPU Twojego klastra
- **Skaluj do czterech węzłów**: Dodaj dwa kolejne systemy Ryzen AI Halo jako dodatkowe węzły robocze Ray, aby podzielić modele na jeszcze więcej GPU. Wymaga to przełącznika Ethernet z co najmniej czterema portami, po jednym dla każdego węzła. Wykonaj [Krok 2: Dołącz do klastra](#step-2-join-the-cluster-machine-2) na każdym dodatkowym węźle roboczym i odpowiednio zwiększ wartość `--tensor-parallel-size`
- **Wypróbuj inne strategie równoległości**: vLLM obsługuje [równoległość ekspertów](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) dla modeli mixture-of-experts oraz [równoległość danych](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) dla wyższej przepustowości. Eksperymentuj z `--enable-expert-parallel` i `--data-parallel-size`, aby znaleźć najlepszą konfigurację dla swojego obciążenia