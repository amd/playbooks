<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Konekäännös.** Tämä sivu on käännetty automaattisesti englannista, eikä sitä ole tarkistanut ihminen. Se saattaa sisältää virheitä, ja jotkin vaiheet, komennot, lataukset tai tuotteiden saatavuus voivat vaihdella kielesi tai alueesi mukaan. Jos jokin vaikuttaa virheelliseltä, pidä alkuperäistä englanninkielistä playbookia ensisijaisena lähteenä.
<!-- auto-translated-disclaimer:end -->

# Alustan määritys

Tässä asiakirjassa kuvataan tämän ohjekirjan suorittamiseen tarvittavat alustan määritykset.

## Vaadittavat sovellukset/kehykset

### Windows/Linux

GAIA tulee olla asennettu etukäteen oppaan [GAIA Installation Guide](../../dependencies/gaia.md) ohjeiden mukaisesti.

Lemonade Server tulee olla asennettu etukäteen oppaan [Lemonade Installation Guide](../../dependencies/lemonade.md) ohjeiden mukaisesti.

## Vaadittavat mallit

### Windows/Linux

Hardware Advisor Agent käyttää mallia **Qwen3-Coder-30B** agentin päättelyyn. Tämä malli ladataan automaattisesti komennon `gaia init` yhteydessä. Manuaalisia mallien latauksia ei tarvita.