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

## Wymagania wstępne

### Windows

| Komponent | Wersja | Uwagi |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Preinstalowany i dostępny w PATH na AMD Ryzen™ AI Halo Developer Platform; na wszystkich innych urządzeniach musi zostać zainstalowany ręcznie |
| **Lemonade Server** | najnowsza | Działa na `http://localhost:13305/api/v1` |

### Linux

| Komponent | Wersja | Uwagi |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Preinstalowany i dostępny w PATH na AMD Ryzen™ AI Halo Developer Platform; na wszystkich innych urządzeniach musi zostać zainstalowany ręcznie |
| **Lemonade Server** | najnowsza | Działa na `http://localhost:13305/api/v1` |


## Lemonade LLM

Serwer Lemonade powinien być uruchomiony z modelem odpowiednim dla danego urządzenia (patrz README, aby poznać polecenie `lemonade run` dla Twojego urządzenia):

| Urządzenie | Punkt końcowy | Model |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |