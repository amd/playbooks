<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

# Konfiguracija platforme — Lemonade Local AI

Ta dokument opisuje vnaprej nameščeno programsko opremo, poti do modelov in platformno specifične predpogoje, ki jih predvideva ta priročnik.

## Vnaprej nameščena programska oprema

| Programska oprema | Različica | Namen |
|----------|---------|---------|
| Lemonade Server | Najnovejša izdaja | Lokalni strežnik LLM z API-jem, združljivim z OpenAI |
| Python | 3.10–3.13 | Zahtevan za primer odjemalca Python OpenAI |

## Privzeto shranjevanje modelov

Modeli, preneseni prek Lemonade, se shranjujejo v skladu s specifikacijo Hugging Face Hub:

| Platforma | Privzeta pot |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

Če želite spremeniti lokacijo shranjevanja, nastavite spremenljivko okolja `HF_HOME`.

## Strojne zahteve

| Ciljna strojna oprema | Zahteve |
|----------------|-------------|
| **CPU** | Kateri koli sodoben procesor x86-64 (AMD ali Intel) |
| **GPU (Vulkan)** | Kateri koli GPU s podporo gonilnika Vulkan |
| **GPU (ROCm)** | AMD Radeon RX serije 7000/9000 ali Radeon PRO serije W7000; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | Procesor AMD Ryzen AI 300 series, Windows 11 |

## Omrežne zahteve

- Internetna povezava je potrebna za začetni prenos modela (1–25 GB, odvisno od modela)
- Po prenosu modelov internet ni potreben