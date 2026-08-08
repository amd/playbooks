<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tłumaczenie maszynowe.** Ta strona została automatycznie przetłumaczona z języka angielskiego i nie została zweryfikowana przez człowieka. Może zawierać błędy, a niektóre instrukcje, polecenia, pliki do pobrania, dostępność produktów lub inne treści mogą różnić się w zależności od języka lub regionu. W przypadku jakichkolwiek niezgodności lub rozbieżności rozstrzygająca jest oryginalna angielska wersja playbook.
<!-- auto-translated-disclaimer:end -->

# Konfiguracja platformy

Ten dokument opisuje oczekiwaną konfigurację platformy wymaganą do uruchomienia tego playbooka.

## Wymagane aplikacje/frameworki

### Windows/Linux
Lemonade powinno być wcześniej zainstalowane, zgodnie z instrukcjami [tutaj](https://lemonade-server.ai/install_options.html). 

- **Open WebUI** (aplikacja webowa typu frontend)
- **Lemonade Server** (backendowy serwer modeli)

> Ten playbook uruchamia **Lemonade** (serwer/aplikację Lemonade) **natywnie**. **Open WebUI** działa jako **kontener** na Linuksie (poprzez Podman) oraz jako **pakiet Python** na Windows. Pakiet PyPI `open-webui` obsługuje wyłącznie Python ≤ 3.12, dlatego kontener na Linuksie pozwala uniknąć konieczności zarządzania starszymi wersjami Pythona.  

## Modele (w Lemonade)

Modele powinny być pobierane wewnątrz **aplikacji Lemonade** (za pomocą wbudowanego Model Manager) lub za pomocą poleceń zarządzania modelami Lemonade (`lemonade pull <model_name>`). Ten playbook zakłada, że poniższe zalecane modele zostały pobrane i widnieją na liście punktu końcowego modeli.

Sprawdź dostępność modeli:
- Otwórz: `http://localhost:13305/api/v1/models`
- Pobrane modele będą wymienione w sekcji `"data"`.

### Zalecane modele

| Funkcjonalność | Identyfikator modelu | Uwagi |
|---|----|-----|
| LLM (wejście tekstowe → wyjście tekstowe) | `Qwen3-4B-Hybrid` (lub podobny) | Dowolny model LLM Lemonade do czatu, uzupełniania tekstu, kodowania lub wnioskowania |
| VLM (obraz → tekst) | `Qwen3.5-4B-GGUF` (lub dowolny model z kategorii **Vision**) | Dowolny multimodalny model z obsługą obrazów, który może przyjmować obrazy jako część danych wejściowych |
| Generowanie obrazów (tekst → obraz) | `SDXL-Turbo` (lub dowolny model z kategorii **Image**) | Dowolny model Stable Diffusion generujący obrazy na podstawie tekstowego polecenia |
| Audio (mowa → tekst) | `Whisper-Large-v3` (lub dowolny model z kategorii **Audio**) | Dowolny model ASR konwertujący dźwięk na tekst |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Używane porty

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Jeśli te porty są już zajęte w Twoim systemie, zmień je podczas uruchamiania serwera(-ów).