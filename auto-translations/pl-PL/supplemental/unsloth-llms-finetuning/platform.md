<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tłumaczenie maszynowe.** Ta strona została automatycznie przetłumaczona z języka angielskiego i nie została zweryfikowana przez człowieka. Może zawierać błędy, a niektóre instrukcje, polecenia, pliki do pobrania, dostępność produktów lub inne treści mogą różnić się w zależności od języka lub regionu. W przypadku jakichkolwiek niezgodności lub rozbieżności rozstrzygająca jest oryginalna angielska wersja playbook.
<!-- auto-translated-disclaimer:end -->

# Konfiguracja platformy

Ten dokument opisuje oczekiwane konfiguracje platformy do uruchamiania tego playbooka.

## Wymagania wstępne

PyTorch z obsługą ROCm jest preinstalowany na AMD Ryzen™ AI Halo Developer Platform. W przypadku wszystkich innych urządzeń użytkownicy muszą ręcznie zainstalować PyTorch z obsługą ROCm. Zapoznaj się z odpowiednią sekcją dla swojego systemu operacyjnego:


### Windows

| Komponent     | Wersja         | Uwagi                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Preinstalowany na AMD Ryzen AI Halo Developer Platform; na wszystkich innych urządzeniach musi zostać zainstalowany ręcznie |


### Linux

| Komponent     | Wersja         | Uwagi                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Preinstalowany na AMD Ryzen AI Halo Developer Platform; na wszystkich innych urządzeniach musi zostać zainstalowany ręcznie |


## Wymagane modele

Następujące modele zostały przetestowane i zoptymalizowane pod kątem Twojej platformy:

| Model | Parametry | Rozmiar | Lokalizacja pobierania |
|-------|------------|------|-------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Pobierz z HF

Modele zostaną automatycznie pobrane do katalogu pamięci podręcznej Hugging Face: `~/.cache/huggingface/hub/`

Zapewnij co najmniej **20GB wolnego miejsca** na przechowywanie modeli.

## Wymagania sieciowe

Wstępna konfiguracja wymaga dostępu do internetu w celu pobrania modeli z Hugging Face. Po pobraniu playbook może działać w trybie offline.

- Pierwsze pobieranie modeli może zająć **5-10 minut**, w zależności od rozmiaru modelu i prędkości połączenia
- Modele są zapisywane lokalnie w pamięci podręcznej i nie wymagają ponownego pobierania