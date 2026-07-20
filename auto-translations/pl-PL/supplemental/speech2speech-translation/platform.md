# Konfiguracja platformy

Ten dokument opisuje oczekiwane konfiguracje platformy do uruchomienia tego playbooka.

## Wymagania wstępne

PyTorch z obsługą ROCm jest wstępnie zainstalowany na platformie AMD Ryzen™ AI Halo Developer Platform. W przypadku wszystkich innych urządzeń użytkownicy muszą ręcznie zainstalować PyTorch z obsługą ROCm. Zapoznaj się z odpowiednią sekcją dla swojego systemu operacyjnego:

### Windows

| Komponent     | Wersja          | Uwagi                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 lub nowsza  | Wstępnie zainstalowany na platformie AMD Ryzen AI Halo Developer Platform; na wszystkich innych urządzeniach musi zostać zainstalowany ręcznie |

### Linux

| Komponent     | Wersja          | Uwagi                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 lub nowsza  | Wstępnie zainstalowany na platformie AMD Ryzen AI Halo Developer Platform; na wszystkich innych urządzeniach musi zostać zainstalowany ręcznie |

## Wymagane modele

Poniższe modele zostały przetestowane i zoptymalizowane pod kątem Twojej platformy:

| Model | Parametry | Rozmiar | Lokalizacja pobierania |
|-------|------------|------|-------------------|
| **facebook/seamless-m4t-v2-large** | 2.3B | ~10GB | Wstępnie zainstalowany na platformie AMD Ryzen AI Halo Developer Platform; na wszystkich innych urządzeniach musi zostać zainstalowany ręcznie |

Modele zostaną automatycznie pobrane do katalogu pamięci podręcznej Hugging Face:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Zapewnij co najmniej **20 GB wolnego miejsca** na przechowywanie modeli.

## Wymagania sieciowe

Wstępna konfiguracja wymaga dostępu do internetu w celu pobrania modeli z Hugging Face. Po pobraniu playbook może działać w trybie offline.

- Pierwsze pobieranie modeli może zająć **5-10 minut**, w zależności od rozmiaru modelu i prędkości połączenia
- Modele są zapisywane lokalnie w pamięci podręcznej i nie wymagają ponownego pobierania