<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfiguracja platformy

Ten dokument opisuje oczekiwane konfiguracje platformy do uruchomienia tego playbooka.

## Wymagania wstępne

PyTorch z obsługą ROCm jest preinstalowany na platformie deweloperskiej AMD Ryzen™ AI Halo. W przypadku wszystkich innych urządzeń użytkownicy muszą ręcznie zainstalować PyTorch z obsługą ROCm. Zapoznaj się z odpowiednią sekcją dla swojego systemu operacyjnego:

### Windows

| Komponent     | Wersja          | Uwagi                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 lub nowszy  | Preinstalowany na platformie deweloperskiej AMD Ryzen AI Halo; na wszystkich innych urządzeniach należy zainstalować ręcznie |

### Linux

| Komponent     | Wersja          | Uwagi                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 lub nowszy  | Preinstalowany na platformie deweloperskiej AMD Ryzen AI Halo; na wszystkich innych urządzeniach należy zainstalować ręcznie |

## Wymagane modele

Następujące modele zostały przetestowane i zoptymalizowane pod kątem Twojej platformy:

| Model | Parametry | Rozmiar | Lokalizacja pobierania |
|-------|-----------|---------|------------------------|
| **openai/gpt-oss-20b** | 20B | ~40GB | Preinstalowany na platformie deweloperskiej AMD Ryzen AI Halo; na wszystkich innych urządzeniach należy zainstalować ręcznie |

Modele będą automatycznie pobierane do katalogu pamięci podręcznej Hugging Face:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Upewnij się, że dostępne jest co najmniej **50 GB wolnego miejsca** na przechowywanie modeli.

## Wymagania sieciowe

Wstępna konfiguracja wymaga dostępu do internetu w celu pobrania modeli z Hugging Face. Po pobraniu playbook może działać w trybie offline.

- Pierwsze pobieranie modeli może zająć **5–10 minut** w zależności od rozmiaru modelu i prędkości połączenia
- Modele są buforowane lokalnie i nie wymagają ponownego pobierania