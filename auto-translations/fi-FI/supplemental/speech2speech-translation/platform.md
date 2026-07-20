# Alustan määritys

Tässä asiakirjassa kuvataan odotetut alustan määritykset tämän playbookin suorittamista varten.

## Edellytykset

PyTorch ROCm-tuella on esiasennettu AMD Ryzen™ AI Halo Developer Platform -alustalle. Kaikkien muiden laitteiden käyttäjien on asennettava PyTorch ROCm-tuella manuaalisesti. Katso tiedot käyttöjärjestelmääsi koskevasta osiosta:

### Windows

| Komponentti     | Versio         | Huomautukset                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 tai uudempi    | Esiasennettu AMD Ryzen AI Halo Developer Platform -alustalle; on asennettava manuaalisesti kaikilla muilla laitteilla |

### Linux

| Komponentti     | Versio         | Huomautukset                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 tai uudempi    | Esiasennettu AMD Ryzen AI Halo Developer Platform -alustalle; on asennettava manuaalisesti kaikilla muilla laitteilla |

## Vaaditut mallit

Seuraavat mallit on testattu ja optimoitu alustallesi:

| Malli | Parametrit | Koko | Latauspaikka |
|-------|------------|------|-------------------|
| **facebook/seamless-m4t-v2-large** | 2.3B | ~10Gt | Esiasennettu AMD Ryzen AI Halo Developer Platform -alustalle; on asennettava manuaalisesti kaikilla muilla laitteilla |

Mallit ladataan automaattisesti Hugging Face -välimuistihakemistoon:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Varmista, että vapaata tilaa on vähintään **20 Gt** mallien tallennusta varten.

## Verkkovaatimukset

Ensimmäinen käyttöönotto vaatii internetyhteyden mallien lataamiseksi Hugging Facesta. Latauksen jälkeen playbookia voi käyttää offline-tilassa.

- Mallien ensimmäinen lataus voi kestää **5–10 minuuttia** mallin koosta ja yhteysnopeudesta riippuen
- Mallit tallennetaan välimuistiin paikallisesti, eikä niitä tarvitse ladata uudelleen