<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfiguracja platformy

Ten dokument opisuje oczekiwane konfiguracje platformy do uruchamiania tego playbooka.

## Windows

### Instalacja LM Studio

LM Studio powinno być wstępnie zainstalowane:

| Komponent | Wersja | Lokalizacja |
|-----------|---------|----------|
| **LM Studio (Modele + Różne)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Pamięć podręczna)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Pobieranie modeli

Następujące modele powinny być już obecne w katalogu modeli LM Studio (`C:\Users\...\.lmstudio\models`):

| Urządzenie | Typ modelu | Kwantyzacja | Rozmiar (GB) | Lokalizacja |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### Instalacja LM Studio

Więcej szczegółów znajdziesz w [lmstudio.md](../../dependencies/lmstudio.md).

### Pobieranie modeli

Tak samo jak w systemie Windows.