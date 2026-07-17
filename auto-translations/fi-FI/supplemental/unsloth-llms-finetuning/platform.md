# Alustan Konfigurointi

Tässä asiakirjassa kuvataan tämän playbook-ohjelman suorittamiseen tarvittavat alustan konfiguraatiot.

## Edellytykset

PyTorch ROCm-tuella on esiasennettu AMD Ryzen™ AI Halo Developer Platform -alustalle. Kaikkien muiden laitteiden käyttäjien on asennettava PyTorch ROCm-tuella manuaalisesti. Katso käyttöjärjestelmääsi koskeva osio:


### Windows

| Komponentti   | Versio          | Huomiot                           |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Esiasennettu AMD Ryzen AI Halo Developer Platform -alustalle; asennettava manuaalisesti kaikille muille laitteille |


### Linux

| Komponentti   | Versio          | Huomiot                           |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Esiasennettu AMD Ryzen AI Halo Developer Platform -alustalle; asennettava manuaalisesti kaikille muille laitteille |


## Vaaditut mallit

Seuraavat mallit on testattu ja optimoitu alustallesi:

| Malli | Parametrit | Koko | Latauslinkki |
|-------|------------|------|--------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Lataa HF:stä

Mallit ladataan automaattisesti Hugging Face -välimuistihakemistoon: `~/.cache/huggingface/hub/`

Varmista, että mallien tallentamiseen on vähintään **20 Gt vapaata tilaa**.

## Verkkovaatimukset

Alkuasennus vaatii internet-yhteyden mallien lataamiseksi Hugging Face -palvelusta. Latauksen jälkeen playbook voidaan suorittaa offline-tilassa.

- Ensimmäiset mallilataukset voivat kestää **5–10 minuuttia** mallin koosta ja yhteysnopeudesta riippuen
- Mallit tallennetaan paikalliseen välimuistiin, eikä niitä tarvitse ladata uudelleen