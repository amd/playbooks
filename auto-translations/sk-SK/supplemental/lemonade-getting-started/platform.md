<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré pokyny, príkazy, súbory na stiahnutie, dostupnosť produktov alebo iný obsah sa môžu líšiť v závislosti od jazyka alebo regiónu. V prípade akéhokoľvek nesúladu alebo rozdielu je rozhodujúca a záväzná pôvodná anglická verzia playbook.
<!-- auto-translated-disclaimer:end -->

# Konfigurácia platformy — Lemonade Local AI

Tento dokument opisuje predinštalovaný softvér, cesty k modelom a špecifické predpoklady platformy predpokladané touto príručkou.

## Predinštalovaný softvér

| Softvér | Verzia | Účel |
|----------|---------|---------|
| Lemonade Server | Najnovšia verzia | Lokálny LLM server s OpenAI-kompatibilným API |
| Python | 3.10–3.13 | Vyžaduje sa pre príklad klienta OpenAI Python |

## Predvolené úložisko modelov

Modely stiahnuté prostredníctvom Lemonade sa ukladajú podľa špecifikácie Hugging Face Hub:

| Platforma | Predvolená cesta |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

Ak chcete zmeniť umiestnenie úložiska, nastavte premennú prostredia `HF_HOME`.

## Hardvérové požiadavky

| Cieľový hardvér | Požiadavky |
|----------------|-------------|
| **CPU** | Akýkoľvek moderný procesor x86-64 (AMD alebo Intel) |
| **GPU (Vulkan)** | Akékoľvek GPU s podporou ovládača Vulkan |
| **GPU (ROCm)** | AMD Radeon RX radu 7000/9000 alebo Radeon PRO radu W7000; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | Procesor AMD Ryzen AI radu 300, Windows 11 |

## Sieťové požiadavky

- Na počiatočné stiahnutie modelu je potrebné internetové pripojenie (1 – 25 GB v závislosti od modelu)
- Po stiahnutí modelov nie je internet potrebný