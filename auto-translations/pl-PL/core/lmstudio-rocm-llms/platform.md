<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tłumaczenie maszynowe.** Ta strona została automatycznie przetłumaczona z języka angielskiego i nie została zweryfikowana przez człowieka. Może zawierać błędy, a niektóre instrukcje, polecenia, pliki do pobrania, dostępność produktów lub inne treści mogą różnić się w zależności od języka lub regionu. W przypadku jakichkolwiek niezgodności lub rozbieżności rozstrzygająca jest oryginalna angielska wersja playbook.
<!-- auto-translated-disclaimer:end -->

# Konfiguracja platformy

Ten dokument opisuje oczekiwane konfiguracje platformy do uruchomienia tego playbooka.

## Windows

### Instalacja LM Studio

LM Studio powinno być wstępnie zainstalowane:

| Komponent | Wersja | Lokalizacja |
|-----------|---------|----------|
| **LM Studio (Modele + Inne)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Pamięć podręczna)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Pobieranie modelu

Poniższe modele powinny już znajdować się w katalogu modeli LM Studio (`C:\Users\...\.lmstudio\models`):

| Urządzenie | Typ modelu | Kwantyzacja | Rozmiar (GB) | Lokalizacja |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### Instalacja LM Studio

Więcej szczegółów znajdziesz w [lmstudio.md](../../dependencies/lmstudio.md).

### Pobieranie modelu

Tak samo jak w systemie Windows.