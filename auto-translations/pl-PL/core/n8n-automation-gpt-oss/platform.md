<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfiguracja platformy

Ten dokument opisuje oczekiwane konfiguracje platformy do uruchamiania tego playbooka.

## Wymagania wstępne

### Windows

| Komponent | Wersja | Uwagi |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Preinstalowany i dostępny w PATH na AMD Ryzen™ AI Halo Developer Platform; na wszystkich innych urządzeniach należy zainstalować ręcznie |
| **Lemonade Server** | najnowsza | Uruchomiony na `http://localhost:13305/api/v1` |

### Linux

| Komponent | Wersja | Uwagi |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Preinstalowany i dostępny w PATH na AMD Ryzen™ AI Halo Developer Platform; na wszystkich innych urządzeniach należy zainstalować ręcznie |
| **Lemonade Server** | najnowsza | Uruchomiony na `http://localhost:13305/api/v1` |


## Lemonade LLM

Serwer Lemonade powinien być uruchomiony z załadowanym modelem odpowiednim dla danego urządzenia (zapoznaj się z plikiem README, aby uzyskać polecenie `lemonade run` dla swojego urządzenia):

| Urządzenie | Punkt końcowy | Model |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |