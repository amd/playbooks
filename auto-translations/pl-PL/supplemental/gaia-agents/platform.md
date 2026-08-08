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

GAIA powinna być wcześniej zainstalowana zgodnie z instrukcjami podanymi w [Przewodniku instalacji GAIA](../../dependencies/gaia.md).

Lemonade Server powinien być wcześniej zainstalowany zgodnie z instrukcjami podanymi w [Przewodniku instalacji Lemonade](../../dependencies/lemonade.md).

## Wymagane modele

### Windows/Linux

Hardware Advisor Agent wykorzystuje **Qwen3-Coder-30B** do wnioskowania agenta. Ten model jest automatycznie pobierany podczas `gaia init`. Ręczne pobieranie modeli nie jest wymagane.