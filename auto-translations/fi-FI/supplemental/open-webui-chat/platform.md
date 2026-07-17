<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Alustan konfigurointi

Tässä asiakirjassa kuvataan tämän playbook-oppaan suorittamiseen tarvittava alustan konfigurointi.

## Vaaditut sovellukset/kehykset

### Windows/Linux
Lemonade tulee olla asennettuna etukäteen [täältä](https://lemonade-server.ai/install_options.html).

- **Open WebUI** (selainpohjainen käyttöliittymäsovellus)
- **Lemonade Server** (taustapalvelimen mallipalvelin)

> Tämä playbook suorittaa **Lemonade**-palvelimen (Lemonade server/app) **natiivisti**. **Open WebUI** toimii **konttina** Linuxilla (Podmanin kautta) ja **Python-pakettina** Windowsilla. `open-webui` PyPI-paketti tukee vain Python ≤ 3.12 -versioita, joten Linux-kontti välttää vanhempien Python-versioiden hallinnan tarpeen.

## Mallit (Lemonadessa)

Mallit tulee ladata **Lemonade**-sovelluksen sisällä (käyttämällä sisäänrakennettua Model Manager -hallintaa) tai Lemonaden mallinhallintakomennoilla (`lemonade pull <model_name>`). Tämä playbook olettaa, että alla suositellut mallit on ladattu ja ne näkyvät mallien listauspäätepistteessä.

Tarkista mallien saatavuus:
- Avaa: `http://localhost:13305/api/v1/models`
- Ladatut mallit näkyvät `"data"`-kohdan alla.

### Suositellut mallit

| Ominaisuus | Mallin tunnus | Huomiot |
|---|----|-----|
| LLM (Tekstisyöte → Tekstituloste) | `Qwen3-4B-Hybrid` (tai vastaava) | Mikä tahansa Lemonade LLM -malli chattiin, tekstin täydentämiseen, koodaukseen tai päättelyyn |
| VLM (Kuva → Teksti) | `Qwen3.5-4B-GGUF` (tai mikä tahansa **Vision**-kategorian malli) | Mikä tahansa multimodaalinen/näkökykyinen malli, joka voi ottaa kuvia syötteenä |
| Kuvien luonti (Teksti → Kuva) | `SDXL-Turbo` (tai mikä tahansa **Image**-kategorian malli) | Mikä tahansa Stable Diffusion -malli, joka luo kuvia tekstikehotteen perusteella |
| Ääni (Puhe → Teksti) | `Whisper-Large-v3` (tai mikä tahansa **Audio**-kategorian malli) | Mikä tahansa ASR-malli, joka muuntaa äänen tekstiksi |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Käytetyt portit

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Jos nämä portit ovat jo käytössä järjestelmässäsi, vaihda ne palvelimia käynnistettäessä.