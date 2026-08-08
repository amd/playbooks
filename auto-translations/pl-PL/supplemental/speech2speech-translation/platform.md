<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tłumaczenie maszynowe.** Ta strona została automatycznie przetłumaczona z języka angielskiego i nie została zweryfikowana przez człowieka. Może zawierać błędy, a niektóre instrukcje, polecenia, pliki do pobrania, dostępność produktów lub inne treści mogą różnić się w zależności od języka lub regionu. W przypadku jakichkolwiek niezgodności lub rozbieżności rozstrzygająca jest oryginalna angielska wersja playbook.
<!-- auto-translated-disclaimer:end -->

# Konfiguracja platformy

Ten dokument opisuje oczekiwane konfiguracje platformy wymagane do uruchomienia tego playbooka.

## Wymagania wstępne

PyTorch z obsługą ROCm jest preinstalowany na platformie AMD Ryzen™ AI Halo Developer Platform. W przypadku wszystkich innych urządzeń użytkownicy muszą ręcznie zainstalować PyTorch z obsługą ROCm. Zapoznaj się z odpowiednią sekcją dla swojego systemu operacyjnego:

### Windows

| Komponent     | Wersja          | Uwagi                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 lub nowsza  | Preinstalowany na platformie AMD Ryzen AI Halo Developer Platform; na wszystkich innych urządzeniach wymaga ręcznej instalacji |

### Linux

| Komponent     | Wersja          | Uwagi                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 lub nowsza  | Preinstalowany na platformie AMD Ryzen AI Halo Developer Platform; na wszystkich innych urządzeniach wymaga ręcznej instalacji |

## Wymagane modele

Poniższe modele zostały przetestowane i zoptymalizowane pod kątem Twojej platformy:

| Model | Parametry | Rozmiar | Lokalizacja pobierania |
|-------|------------|------|-------------------|
| **facebook/seamless-m4t-v2-large** | 2,3 mld | ~10 GB | Preinstalowany na platformie AMD Ryzen AI Halo Developer Platform; na wszystkich innych urządzeniach wymaga ręcznej instalacji |

Modele zostaną automatycznie pobrane do katalogu pamięci podręcznej Hugging Face:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Upewnij się, że dostępne jest co najmniej **20 GB wolnego miejsca** na przechowywanie modeli.

## Wymagania dotyczące sieci

Wstępna konfiguracja wymaga dostępu do internetu w celu pobrania modeli z Hugging Face. Po pobraniu playbook może działać w trybie offline.

- Pierwsze pobieranie modeli może zająć **5–10 minut**, w zależności od rozmiaru modelu i szybkości połączenia
- Modele są przechowywane lokalnie w pamięci podręcznej i nie wymagają ponownego pobierania