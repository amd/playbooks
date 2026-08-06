<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinöversättning.** Den här sidan har automatiskt översatts från engelska och har inte granskats av en människa. Den kan innehålla fel, och vissa instruktioner, kommandon, nedladdningar, produkttillgänglighet eller annat innehåll kan variera beroende på språk eller region. Vid eventuella motsägelser eller avvikelser är det den ursprungliga engelska versionen av playbook som gäller och har företräde.
<!-- auto-translated-disclaimer:end -->

# Plattformskonfiguration — Lemonade Local AI

Detta dokument beskriver den förinstallerade programvaran, modellsökvägar och plattformsspecifika förutsättningar som antas av denna handbok.

## Förinstallerad programvara

| Programvara | Version | Syfte |
|----------|---------|---------|
| Lemonade Server | Senaste version | Lokal LLM-server med OpenAI-kompatibelt API |
| Python | 3.10–3.13 | Krävs för exemplet med OpenAI Python-klienten |

## Standardplats för modellagring

Modeller som laddas ner via Lemonade lagras enligt Hugging Face Hub-specifikationen:

| Plattform | Standardsökväg |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

För att ändra lagringsplatsen, ställ in miljövariabeln `HF_HOME`.

## Hårdvarukrav

| Hårdvarumål | Krav |
|----------------|-------------|
| **CPU** | Vilken modern x86-64-processor som helst (AMD eller Intel) |
| **GPU (Vulkan)** | Vilken GPU som helst med stöd för Vulkan-drivrutin |
| **GPU (ROCm)** | AMD Radeon RX 7000/9000-serien eller Radeon PRO W7000-serien; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | AMD Ryzen AI 300-seriens processor, Windows 11 |

## Nätverkskrav

- Internetanslutning krävs för den första modellnedladdningen (1–25 GB beroende på modell)
- Ingen internetanslutning krävs efter att modellerna har laddats ner