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

PyTorch z obsługą ROCm jest fabrycznie zainstalowany na platformie AMD Ryzen™ AI Halo Developer Platform. W przypadku wszystkich pozostałych urządzeń użytkownicy muszą ręcznie zainstalować PyTorch z obsługą ROCm. Zapoznaj się z odpowiednią sekcją dla swojego systemu operacyjnego:

### Windows

| Komponent     | Wersja          | Uwagi                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 lub nowszy  | Fabrycznie zainstalowany na platformie AMD Ryzen AI Halo Developer Platform; na wszystkich pozostałych urządzeniach należy zainstalować ręcznie |

### Linux

| Komponent     | Wersja          | Uwagi                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 lub nowszy  | Fabrycznie zainstalowany na platformie AMD Ryzen AI Halo Developer Platform; na wszystkich pozostałych urządzeniach należy zainstalować ręcznie |

## Wymagane modele

Poniższe modele zostały przetestowane i zoptymalizowane pod kątem Twojej platformy:

| Model | Parametry | Rozmiar | Lokalizacja pobierania |
|-------|------------|------|-------------------|
| **openai/gpt-oss-20b** | 20B | ~40GB | Fabrycznie zainstalowany na platformie AMD Ryzen AI Halo Developer Platform; na wszystkich pozostałych urządzeniach należy zainstalować ręcznie |

Modele będą automatycznie pobierane do katalogu pamięci podręcznej Hugging Face:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Zapewnij co najmniej **50GB wolnego miejsca** na przechowywanie modeli.

## Wymagania sieciowe

Wstępna konfiguracja wymaga dostępu do internetu w celu pobrania modeli z Hugging Face. Po pobraniu playbook może działać offline.

- Pierwsze pobieranie modeli może zająć **5-10 minut** w zależności od rozmiaru modelu i szybkości połączenia
- Modele są zapisywane lokalnie w pamięci podręcznej i nie wymagają ponownego pobierania