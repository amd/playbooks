<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfiguracja platformy

Ten dokument opisuje oczekiwaną konfigurację platformy do uruchomienia tego playbooka.

## Wymagane aplikacje/frameworki

### Windows/Linux
Lemonade powinno być zainstalowane wcześniej, zgodnie z instrukcją dostępną [tutaj](https://lemonade-server.ai/install_options.html).

- **Open WebUI** (frontendowa aplikacja webowa)
- **Lemonade Server** (backendowy serwer modeli)

> Ten playbook uruchamia **Lemonade** (serwer/aplikację Lemonade) **natywnie**. **Open WebUI** działa jako **kontener** na Linux (za pośrednictwem Podman) oraz jako **pakiet Python** na Windows. Pakiet PyPI `open-webui` obsługuje wyłącznie Python ≤ 3.12, dlatego kontener na Linux pozwala uniknąć konieczności zarządzania starszymi wersjami Pythona.

## Modele (w Lemonade)

Modele należy pobrać w **aplikacji Lemonade** (korzystając z wbudowanego Menedżera modeli) lub za pomocą poleceń zarządzania modelami Lemonade (`lemonade pull <model_name>`). Ten playbook zakłada, że poniższe zalecane modele zostały pobrane i są widoczne w punkcie końcowym listy modeli.

Sprawdź dostępność modeli:
- Otwórz: `http://localhost:13305/api/v1/models`
- Pobrane modele będą wymienione w sekcji `"data"`.

### Zalecane modele

| Możliwość | ID modelu | Uwagi |
|---|----|-----|
| LLM (wejście tekstowe → wyjście tekstowe) | `Qwen3-4B-Hybrid` (lub podobny) | Dowolny model LLM Lemonade do czatu, uzupełniania tekstu, kodowania lub wnioskowania |
| VLM (obraz → tekst) | `Qwen3.5-4B-GGUF` (lub dowolny model z kategorii **Vision**) | Dowolny model multimodalny/obsługujący wizję, który może przyjmować obrazy jako część danych wejściowych |
| Generowanie obrazów (tekst → obraz) | `SDXL-Turbo` (lub dowolny model z kategorii **Image**) | Dowolny model Stable Diffusion generujący obrazy na podstawie podpowiedzi tekstowej |
| Audio (mowa → tekst) | `Whisper-Large-v3` (lub dowolny model z kategorii **Audio**) | Dowolny model ASR konwertujący audio na tekst |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Używane porty

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Jeśli te porty są już zajęte w Twoim systemie, zmień je podczas uruchamiania serwera (serwerów).