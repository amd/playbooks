<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducere automată.** Această pagină a fost tradusă automat din limba engleză și nu a fost revizuită de o persoană. Aceasta poate conține erori, iar anumite instrucțiuni, comenzi, descărcări, disponibilitatea produselor sau alt conținut pot varia în funcție de limbă sau regiune. În cazul oricărei neconcordanțe sau discrepanțe, versiunea originală în limba engleză a playbook-ului prevalează.
<!-- auto-translated-disclaimer:end -->

# Configurare platformă — Lemonade Local AI

Acest document descrie software-ul preinstalat, căile modelelor și cerințele preliminare specifice platformei presupuse de acest playbook.

## Software preinstalat

| Software | Versiune | Scop |
|----------|---------|-------|
| Lemonade Server | Cea mai recentă versiune | Server LLM local cu API compatibil OpenAI |
| Python | 3.10–3.13 | Necesar pentru exemplul cu clientul Python OpenAI |

## Stocarea implicită a modelelor

Modelele descărcate prin Lemonade sunt stocate conform specificației Hugging Face Hub:

| Platformă | Cale implicită |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

Pentru a schimba locația de stocare, setați variabila de mediu `HF_HOME`.

## Cerințe hardware

| Țintă hardware | Cerințe |
|----------------|-------------|
| **CPU** | Orice procesor x86-64 modern (AMD sau Intel) |
| **GPU (Vulkan)** | Orice GPU cu suport pentru driver Vulkan |
| **GPU (ROCm)** | AMD Radeon RX seria 7000/9000 sau Radeon PRO seria W7000; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | Procesor AMD Ryzen AI seria 300, Windows 11 |

## Cerințe de rețea

- Este necesară o conexiune la internet pentru descărcarea inițială a modelului (1–25 GB în funcție de model)
- Nu este necesar internet după descărcarea modelelor