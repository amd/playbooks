<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Konekäännös.** Tämä sivu on käännetty automaattisesti englannista, eikä sitä ole tarkistanut ihminen. Se voi sisältää virheitä, ja tietyt ohjeet, komennot, lataukset, tuotteiden saatavuus tai muu sisältö voivat vaihdella kielen tai alueen mukaan. Mahdollisten ristiriitaisuuksien tai epäjohdonmukaisuuksien ilmetessä alkuperäinen englanninkielinen playbook on ratkaiseva ja ensisijainen versio.
<!-- auto-translated-disclaimer:end -->

# Alustan määritys

Tässä dokumentissa kuvataan tämän ohjekokoelman ajamiseen tarvittavat alustan määritykset.

## Edellytykset

ROCm-tuella varustettu PyTorch on esiasennettu AMD Ryzen™ AI Halo Developer Platform -alustalle. Kaikissa muissa laitteissa käyttäjien on asennettava ROCm-tukea sisältävä PyTorch manuaalisesti. Katso käyttöjärjestelmääsi koskeva osio:

### Windows

| Komponentti     | Versio         | Huomautukset                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 tai uudempi    | Esiasennettu AMD Ryzen AI Halo Developer Platform -alustalle; muissa laitteissa asennettava manuaalisesti |

### Linux

| Komponentti     | Versio         | Huomautukset                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 tai uudempi    | Esiasennettu AMD Ryzen AI Halo Developer Platform -alustalle; muissa laitteissa asennettava manuaalisesti |

## Vaaditut mallit

Seuraavat mallit on testattu ja optimoitu alustallesi:

| Malli | Parametrit | Koko | Latauspaikka |
|-------|------------|------|-------------------|
| **facebook/seamless-m4t-v2-large** | 2.3B | ~10 Gt | Esiasennettu AMD Ryzen AI Halo Developer Platform -alustalle; muissa laitteissa asennettava manuaalisesti |

Mallit ladataan automaattisesti Hugging Face -välimuistihakemistoon:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Varmista, että käytettävissä on vähintään **20 Gt vapaata tilaa** mallien tallennusta varten.

## Verkkovaatimukset

Ensimmäinen käyttöönotto vaatii internetyhteyden mallien lataamiseksi Hugging Facesta. Latauksen jälkeen ohjekokoelmaa voidaan käyttää offline-tilassa.

- Mallien ensimmäinen lataus voi kestää **5–10 minuuttia** mallin koosta ja yhteysnopeudesta riippuen
- Mallit tallennetaan välimuistiin paikallisesti, eikä niitä tarvitse ladata uudelleen