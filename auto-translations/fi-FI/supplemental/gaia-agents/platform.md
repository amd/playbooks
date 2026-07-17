<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Alustan konfigurointi

Tässä asiakirjassa kuvataan tämän playbook-ohjelman suorittamiseen tarvittavat alustan konfiguraatiot.

## Vaaditut sovellukset/kehykset

### Windows/Linux

GAIA tulee olla esiasennettuna [GAIA-asennusoppaan](../../dependencies/gaia.md) ohjeiden mukaisesti.

Lemonade Server tulee olla esiasennettuna [Lemonade-asennusoppaan](../../dependencies/lemonade.md) ohjeiden mukaisesti.

## Vaaditut mallit

### Windows/Linux

Hardware Advisor Agent käyttää **Qwen3-Coder-30B**-mallia agentin päättelyyn. Tämä malli ladataan automaattisesti `gaia init`-komennon suorituksen aikana. Manuaalisia mallilatauksia ei tarvita.