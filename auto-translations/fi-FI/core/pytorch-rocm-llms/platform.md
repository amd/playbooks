<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Alustan konfigurointi

Tässä asiakirjassa kuvataan tämän playbook-oppaan suorittamiseen tarvittavat alustan konfiguraatiot.

## Edellytykset

PyTorch ROCm-tuella on esiasennettu AMD Ryzen™ AI Halo Developer Platform -alustalle. Kaikkien muiden laitteiden käyttäjien on asennettava PyTorch ROCm-tuella manuaalisesti. Katso käyttöjärjestelmääsi koskeva osio:

### Windows

| Komponentti   | Versio          | Huomiot                           |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 tai uudempi | Esiasennettu AMD Ryzen AI Halo Developer Platform -alustalle; asennettava manuaalisesti kaikille muille laitteille |

### Linux

| Komponentti   | Versio          | Huomiot                           |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 tai uudempi | Esiasennettu AMD Ryzen AI Halo Developer Platform -alustalle; asennettava manuaalisesti kaikille muille laitteille |

## Vaaditut mallit

Seuraavat mallit on testattu ja optimoitu alustallesi:

| Malli | Parametrit | Koko | Lataussijainti |
|-------|------------|------|----------------|
| **openai/gpt-oss-20b** | 20B | ~40 Gt | Esiasennettu AMD Ryzen AI Halo Developer Platform -alustalle; asennettava manuaalisesti kaikille muille laitteille |

Mallit ladataan automaattisesti Hugging Face -välimuistihakemistoon:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Varmista, että mallien tallentamiseen on vähintään **50 Gt vapaata tilaa**.

## Verkkovaatimukset

Alkuasennus vaatii internet-yhteyden mallien lataamiseksi Hugging Face -palvelusta. Latauksen jälkeen playbook voidaan suorittaa offline-tilassa.

- Ensimmäiset mallilataukset voivat kestää **5–10 minuuttia** mallin koosta ja yhteysnopeudesta riippuen
- Mallit tallennetaan paikalliseen välimuistiin, eikä niitä tarvitse ladata uudelleen