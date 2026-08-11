<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Konekäännös.** Tämä sivu on käännetty automaattisesti englannista, eikä sitä ole tarkistanut ihminen. Se voi sisältää virheitä, ja tietyt ohjeet, komennot, lataukset, tuotteiden saatavuus tai muu sisältö voivat vaihdella kielen tai alueen mukaan. Mahdollisten ristiriitaisuuksien tai epäjohdonmukaisuuksien ilmetessä alkuperäinen englanninkielinen playbook on ratkaiseva ja ensisijainen versio.
<!-- auto-translated-disclaimer:end -->

# Alustan kokoonpano

Tässä asiakirjassa kuvataan tämän ohjekirjan suorittamiseen tarvittavat alustakokoonpanot.

## Edellytykset

PyTorch ROCm-tuella on esiasennettu AMD Ryzen™ AI Halo -kehitysalustalle. Kaikissa muissa laitteissa käyttäjien on asennettava PyTorch ROCm-tuella manuaalisesti. Katso käyttöjärjestelmääsi koskeva osio:


### Windows

| Komponentti     | Versio         | Huomautukset                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Esiasennettu AMD Ryzen AI Halo -kehitysalustalle; on asennettava manuaalisesti kaikissa muissa laitteissa |


### Linux

| Komponentti     | Versio         | Huomautukset                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Esiasennettu AMD Ryzen AI Halo -kehitysalustalle; on asennettava manuaalisesti kaikissa muissa laitteissa |


## Vaaditut mallit

Seuraavat mallit on testattu ja optimoitu alustallesi:

| Malli | Parametrit | Koko | Latauspaikka |
|-------|------------|------|-------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16 Gt | Lataa HF:stä

Mallit ladataan automaattisesti Hugging Face -välimuistihakemistoon: `~/.cache/huggingface/hub/`

Varmista, että käytettävissä on vähintään **20 Gt vapaata tilaa** mallien tallennusta varten.

## Verkkovaatimukset

Ensimmäinen käyttöönotto vaatii internetyhteyden mallien lataamiseksi Hugging Facesta. Latauksen jälkeen ohjekirjaa voidaan käyttää offline-tilassa.

- Mallien ensimmäinen lataus voi kestää **5–10 minuuttia** mallin koosta ja yhteysnopeudesta riippuen
- Mallit tallennetaan välimuistiin paikallisesti, eikä niitä tarvitse ladata uudelleen