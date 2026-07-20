<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfiguracja platformy

Ten dokument opisuje oczekiwane konfiguracje platformy do uruchomienia tego playbooka.

## Windows

### Instalacja LM Studio

LM Studio powinno być wstępnie zainstalowane:

| Komponent | Wersja | Lokalizacja |
|-----------|---------|----------|
| **LM Studio (Modele + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Pobieranie modelu

Następujące modele powinny już znajdować się w katalogu modeli LM Studio (`C:\Users\...\.lmstudio\models`):

| Typ modelu | Kwantyzacja | Rozmiar | Lokalizacja |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### Instalacja LM Studio

Więcej informacji można znaleźć w pliku lmstudio.md (w folderze dependencies).

### Pobieranie modelu

Tak samo jak w systemie Windows.