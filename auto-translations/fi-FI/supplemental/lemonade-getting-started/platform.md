<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Alustan konfiguraatio — Lemonade Local AI

Tässä asiakirjassa kuvataan tämän playbook-oppaan olettama esiasennetttu ohjelmisto, mallien polut ja alustakohtaiset edellytykset.

## Esiasennettu ohjelmisto

| Ohjelmisto | Versio | Tarkoitus |
|----------|---------|---------|
| Lemonade Server | Uusin julkaisu | Paikallinen LLM-palvelin OpenAI-yhteensopivalla API:lla |
| Python | 3.10–3.13 | Vaaditaan OpenAI Python -asiakasesimerkkiä varten |

## Oletusarvoinen mallien tallennussijainti

Lemonade-palvelun kautta ladatut mallit tallennetaan Hugging Face Hub -määrityksen mukaisesti:

| Alusta | Oletuspolku |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

Voit muuttaa tallennussijaintia asettamalla `HF_HOME`-ympäristömuuttujan.

## Laitteistovaatimukset

| Laitteistokohde | Vaatimukset |
|----------------|-------------|
| **CPU** | Mikä tahansa moderni x86-64-suoritin (AMD tai Intel) |
| **GPU (Vulkan)** | Mikä tahansa GPU, jossa on Vulkan-ajurituki |
| **GPU (ROCm)** | AMD Radeon RX 7000/9000 -sarja tai Radeon PRO W7000 -sarja; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | AMD Ryzen AI 300 -sarjan suoritin, Windows 11 |

## Verkkovaatimukset

- Internet-yhteys vaaditaan mallin ensimmäistä latausta varten (1–25 Gt mallista riippuen)
- Internet-yhteyttä ei tarvita mallien lataamisen jälkeen