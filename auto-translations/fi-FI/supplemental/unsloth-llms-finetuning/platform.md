# Alustan kokoonpano

Tässä asiakirjassa kuvataan tämän ohjekirjan (playbook) suorittamiseen tarvittavat odotetut alustan kokoonpanot.

## Edellytykset

PyTorch ROCm-tuella on esiasennettu AMD Ryzen™ AI Halo Developer Platform -alustalle. Kaikkiin muihin laitteisiin käyttäjien on asennettava PyTorch ROCm-tuella manuaalisesti. Katso käyttöjärjestelmääsi koskeva osio:


### Windows

| Komponentti     | Versio         | Huomautukset                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Esiasennettu AMD Ryzen AI Halo Developer Platform -alustalle; on asennettava manuaalisesti kaikkiin muihin laitteisiin |


### Linux

| Komponentti     | Versio         | Huomautukset                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Esiasennettu AMD Ryzen AI Halo Developer Platform -alustalle; on asennettava manuaalisesti kaikkiin muihin laitteisiin |


## Vaaditut mallit

Seuraavat mallit on testattu ja optimoitu alustallesi:

| Malli | Parametrit | Koko | Latauspaikka |
|-------|------------|------|-------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Lataa HF:stä

Mallit ladataan automaattisesti Hugging Face -välimuistihakemistoon: `~/.cache/huggingface/hub/`

Varmista, että käytettävissä on vähintään **20 Gt vapaata tilaa** mallien tallentamista varten.

## Verkkovaatimukset

Ensimmäinen käyttöönotto edellyttää internetyhteyttä mallien lataamiseksi Hugging Facesta. Latauksen jälkeen ohjekirjaa voidaan käyttää offline-tilassa.

- Mallien ensimmäinen lataus voi kestää **5–10 minuuttia** riippuen mallin koosta ja yhteysnopeudesta
- Mallit tallennetaan välimuistiin paikallisesti, eikä niitä tarvitse ladata uudelleen