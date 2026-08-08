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

## Wymagane aplikacje/frameworki

### Windows/Linux

- **Lemonade Server** powinien zostać zainstalowany zgodnie z
  [przewodnikiem instalacji Lemonade](https://lemonade-server.ai/docs/guide/install/).
- **Node.js 22.12 lub nowszy** oraz `npm`, używane przez CLI `agent-canvas` oraz serwery MCP
  uruchamiane za pomocą `npx`.
- **uv**, menedżer pakietów Pythona, którego Agent Canvas używa do zarządzania środowiskiem
  serwera agenta. Zainstaluj go, korzystając z
  [przewodnika instalacji uv](https://docs.astral.sh/uv/getting-started/installation/).

## Wymagane modele

### Windows/Linux

Poniższy model musi być dostępny w Lemonade Server przed uruchomieniem
playbooka.

| Typ modelu | ID modelu | Uwagi |
| --- | --- | --- |
| Model czatu GGUF | `Qwen3.6-35B-A3B-GGUF` | Udostępniany przez Lemonade Server pod adresem `http://127.0.0.1:13305/api/v1`. Na urządzeniach z mniej niż 32 GB pamięci użyj mniejszego modelu GGUF. |

Uruchom model za pomocą:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

## Zewnętrzne dane uwierzytelniające

Ten playbook wymaga:

- Tokenu GitHub z dostępem do odczytu repozytorium, które ma zostać podsumowane.
- Tokenu bota Slack z uprawnieniami `chat:write` oraz dostępem do odczytu kanału.
- ID zespołu Slack oraz ID docelowego kanału Slack.