<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Konekäännös.** Tämä sivu on käännetty automaattisesti englannista, eikä sitä ole tarkistanut ihminen. Se saattaa sisältää virheitä, ja jotkin vaiheet, komennot, lataukset tai tuotteiden saatavuus voivat vaihdella kielesi tai alueesi mukaan. Jos jokin vaikuttaa virheelliseltä, pidä alkuperäistä englanninkielistä playbookia ensisijaisena lähteenä.
<!-- auto-translated-disclaimer:end -->

# Alustan määritys — Lemonade Local AI

Tässä asiakirjassa kuvataan valmiiksi asennettu ohjelmisto, mallien polut ja alustakohtaiset esivaatimukset, joita tämä ohjekirja edellyttää.

## Valmiiksi asennettu ohjelmisto

| Ohjelmisto | Versio | Tarkoitus |
|----------|---------|---------|
| Lemonade Server | Uusin julkaisu | Paikallinen LLM-palvelin, jossa on OpenAI-yhteensopiva API |
| Python | 3.10–3.13 | Vaaditaan OpenAI Python -asiakasesimerkkiä varten |

## Mallien oletustallennuspaikka

Lemonaden kautta ladatut mallit tallennetaan Hugging Face Hub -määrityksen mukaisesti:

| Alusta | Oletuspolku |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

Voit muuttaa tallennussijaintia asettamalla `HF_HOME`-ympäristömuuttujan.

## Laitteistovaatimukset

| Laitteistokohde | Vaatimukset |
|----------------|-------------|
| **CPU** | Mikä tahansa nykyaikainen x86-64-suoritin (AMD tai Intel) |
| **GPU (Vulkan)** | Mikä tahansa GPU, joka tukee Vulkan-ajuria |
| **GPU (ROCm)** | AMD Radeon RX 7000/9000 -sarja tai Radeon PRO W7000 -sarja; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | AMD Ryzen AI 300 -sarjan suoritin, Windows 11 |

## Verkkovaatimukset

- Internet-yhteys vaaditaan mallin ensimmäistä latausta varten (1–25 Gt mallista riippuen)
- Internet-yhteyttä ei vaadita sen jälkeen, kun mallit on ladattu