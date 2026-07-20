# Konfiguracja platformy

Ten dokument opisuje oczekiwane konfiguracje platformy do uruchamiania tego playbooka.

## Wymagania wstępne

PyTorch z obsługą ROCm jest preinstalowany na AMD Ryzen™ AI Halo Developer Platform. W przypadku wszystkich innych urządzeń użytkownicy muszą ręcznie zainstalować PyTorch z obsługą ROCm. Proszę zapoznać się z odpowiednią sekcją dla swojego systemu operacyjnego:


### Windows

| Komponent     | Wersja         | Uwagi                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Preinstalowany na AMD Ryzen AI Halo Developer Platform; musi być ręcznie zainstalowany na wszystkich innych urządzeniach |


### Linux

| Komponent     | Wersja         | Uwagi                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Preinstalowany na AMD Ryzen AI Halo Developer Platform; musi być ręcznie zainstalowany na wszystkich innych urządzeniach |


## Wymagane modele

Poniższe modele zostały przetestowane i zoptymalizowane pod kątem Twojej platformy:

| Model | Parametry | Rozmiar | Lokalizacja pobierania |
|-------|------------|------|-------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Pobierz z HF

Modele zostaną automatycznie pobrane do katalogu pamięci podręcznej Hugging Face: `~/.cache/huggingface/hub/`

Zapewnij co najmniej **20GB wolnego miejsca** na przechowywanie modeli.

## Wymagania sieciowe

Konfiguracja początkowa wymaga dostępu do internetu w celu pobrania modeli z Hugging Face. Po pobraniu playbook może działać offline.

- Pierwsze pobieranie modeli może zająć **5–10 minut**, w zależności od rozmiaru modelu i szybkości połączenia
- Modele są zapisywane lokalnie w pamięci podręcznej i nie muszą być pobierane ponownie