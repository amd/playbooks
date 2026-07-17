<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration — Lemonade Local AI

Ez a dokumentum leírja az előre telepített szoftvereket, a modellek elérési útjait és a platform-specifikus előfeltételeket, amelyeket ez a playbook feltételez.

## Előre Telepített Szoftverek

| Szoftver | Verzió | Cél |
|----------|---------|---------|
| Lemonade Server | Legújabb kiadás | Helyi LLM szerver OpenAI-kompatibilis API-val |
| Python | 3.10–3.13 | Az OpenAI Python kliens példához szükséges |

## Alapértelmezett Modeltároló

A Lemonade-en keresztül letöltött modellek a Hugging Face Hub specifikáció szerint kerülnek tárolásra:

| Platform | Alapértelmezett Elérési Út |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

A tárolási hely megváltoztatásához állítsa be a `HF_HOME` környezeti változót.

## Hardverkövetelmények

| Hardvercél | Követelmények |
|----------------|-------------|
| **CPU** | Bármely modern x86-64 processzor (AMD vagy Intel) |
| **GPU (Vulkan)** | Bármely GPU Vulkan illesztőprogram-támogatással |
| **GPU (ROCm)** | AMD Radeon RX 7000/9000 sorozat vagy Radeon PRO W7000 sorozat; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | AMD Ryzen AI 300 sorozatú processzor, Windows 11 |

## Hálózati Követelmények

- Az első modell letöltéséhez internetkapcsolat szükséges (1–25 GB a modelltől függően)
- A modellek letöltése után nincs szükség internetre