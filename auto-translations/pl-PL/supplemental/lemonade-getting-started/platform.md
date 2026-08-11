<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tłumaczenie maszynowe.** Ta strona została automatycznie przetłumaczona z języka angielskiego i nie została zweryfikowana przez człowieka. Może zawierać błędy, a niektóre instrukcje, polecenia, pliki do pobrania, dostępność produktów lub inne treści mogą różnić się w zależności od języka lub regionu. W przypadku jakichkolwiek niezgodności lub rozbieżności rozstrzygająca jest oryginalna angielska wersja playbook.
<!-- auto-translated-disclaimer:end -->

# Konfiguracja platformy — Lemonade Local AI

Ten dokument opisuje wstępnie zainstalowane oprogramowanie, ścieżki modeli oraz wymagania wstępne specyficzne dla platformy, przyjęte w tym przewodniku.

## Wstępnie zainstalowane oprogramowanie

| Oprogramowanie | Wersja | Cel |
|----------|---------|---------|
| Lemonade Server | Najnowsze wydanie | Lokalny serwer LLM z API zgodnym z OpenAI |
| Python | 3.10–3.13 | Wymagany do przykładu z klientem Python OpenAI |

## Domyślne miejsce przechowywania modeli

Modele pobrane za pomocą Lemonade są przechowywane zgodnie ze specyfikacją Hugging Face Hub:

| Platforma | Domyślna ścieżka |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

Aby zmienić lokalizację przechowywania, ustaw zmienną środowiskową `HF_HOME`.

## Wymagania sprzętowe

| Docelowy sprzęt | Wymagania |
|----------------|-------------|
| **CPU** | Dowolny nowoczesny procesor x86-64 (AMD lub Intel) |
| **GPU (Vulkan)** | Dowolne GPU z obsługą sterownika Vulkan |
| **GPU (ROCm)** | AMD Radeon RX serii 7000/9000 lub Radeon PRO serii W7000; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | Procesor AMD Ryzen AI serii 300, Windows 11 |

## Wymagania sieciowe

- Wymagane połączenie internetowe do wstępnego pobrania modelu (1–25 GB w zależności od modelu)
- Po pobraniu modeli internet nie jest wymagany