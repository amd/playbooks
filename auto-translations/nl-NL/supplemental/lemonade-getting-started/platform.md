<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Machinevertaling.** Deze pagina is automatisch vertaald vanuit het Engels en is niet door een mens gecontroleerd. Deze pagina kan fouten bevatten en bepaalde instructies, opdrachten, downloads, productbeschikbaarheid of andere inhoud kan per taal of regio verschillen. In geval van tegenstrijdigheid of discrepantie is de oorspronkelijke Engelse versie van de playbook doorslaggevend en prevaleert deze.
<!-- auto-translated-disclaimer:end -->

# Platformconfiguratie — Lemonade Local AI

Dit document beschrijft de vooraf geïnstalleerde software, modelpaden en platformspecifieke vereisten die in deze playbook worden verondersteld.

## Vooraf geïnstalleerde software

| Software | Versie | Doel |
|----------|---------|---------|
| Lemonade Server | Nieuwste release | Lokale LLM-server met OpenAI-compatibele API |
| Python | 3.10–3.13 | Vereist voor het voorbeeld van de OpenAI Python-client |

## Standaard modelopslag

Modellen die via Lemonade worden gedownload, worden opgeslagen volgens de Hugging Face Hub-specificatie:

| Platform | Standaardpad |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

Om de opslaglocatie te wijzigen, stelt u de omgevingsvariabele `HF_HOME` in.

## Hardwarevereisten

| Hardwaredoel | Vereisten |
|----------------|-------------|
| **CPU** | Elke moderne x86-64-processor (AMD of Intel) |
| **GPU (Vulkan)** | Elke GPU met ondersteuning voor Vulkan-drivers |
| **GPU (ROCm)** | AMD Radeon RX 7000/9000-serie of Radeon PRO W7000-serie; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | AMD Ryzen AI 300-serie processor, Windows 11 |

## Netwerkvereisten

- Internetverbinding vereist voor het initieel downloaden van modellen (1–25 GB, afhankelijk van het model)
- Geen internet vereist nadat modellen zijn gedownload