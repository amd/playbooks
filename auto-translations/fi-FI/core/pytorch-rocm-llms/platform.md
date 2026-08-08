<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Konekäännös.** Tämä sivu on käännetty automaattisesti englannista, eikä sitä ole tarkistanut ihminen. Se voi sisältää virheitä, ja tietyt ohjeet, komennot, lataukset, tuotteiden saatavuus tai muu sisältö voivat vaihdella kielen tai alueen mukaan. Mahdollisten ristiriitaisuuksien tai epäjohdonmukaisuuksien ilmetessä alkuperäinen englanninkielinen playbook on ratkaiseva ja ensisijainen versio.
<!-- auto-translated-disclaimer:end -->

# Alustan määritys

Tässä asiakirjassa kuvataan tämän ohjekirjan (playbook) suorittamiseen tarvittavat alustan määritykset.

## Edellytykset

ROCm-tuella varustettu PyTorch on asennettu valmiiksi AMD Ryzen™ AI Halo Developer Platform -alustalle. Kaikissa muissa laitteissa käyttäjien on asennettava ROCm-tuella varustettu PyTorch manuaalisesti. Katso käyttöjärjestelmääsi koskeva osio:

### Windows

| Komponentti     | Versio         | Huomiot                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 tai uudempi    | Asennettu valmiiksi AMD Ryzen AI Halo Developer Platform -alustalle; kaikissa muissa laitteissa asennettava manuaalisesti |

### Linux

| Komponentti     | Versio         | Huomiot                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 tai uudempi    | Asennettu valmiiksi AMD Ryzen AI Halo Developer Platform -alustalle; kaikissa muissa laitteissa asennettava manuaalisesti |

## Vaaditut mallit

Seuraavat mallit on testattu ja optimoitu alustallesi:

| Malli | Parametrit | Koko | Latauspaikka |
|-------|------------|------|-------------------|
| **openai/gpt-oss-20b** | 20B | ~40GB | Asennettu valmiiksi AMD Ryzen AI Halo Developer Platform -alustalle; kaikissa muissa laitteissa asennettava manuaalisesti |

Mallit ladataan automaattisesti Hugging Face -välimuistihakemistoon:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Varmista, että käytettävissä on vähintään **50 Gt vapaata tilaa** mallien tallennusta varten.

## Verkkovaatimukset

Alkuasennus edellyttää internetyhteyttä mallien lataamiseksi Hugging Facesta. Latauksen jälkeen ohjekirjaa voidaan käyttää offline-tilassa.

- Mallien ensimmäinen lataus voi kestää **5–10 minuuttia** mallin koosta ja yhteysnopeudesta riippuen
- Mallit tallennetaan välimuistiin paikallisesti, eikä niitä tarvitse ladata uudelleen