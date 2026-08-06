<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Konekäännös.** Tämä sivu on käännetty automaattisesti englannista, eikä sitä ole tarkistanut ihminen. Se voi sisältää virheitä, ja tietyt ohjeet, komennot, lataukset, tuotteiden saatavuus tai muu sisältö voivat vaihdella kielen tai alueen mukaan. Mahdollisten ristiriitaisuuksien tai epäjohdonmukaisuuksien ilmetessä alkuperäinen englanninkielinen playbook on ratkaiseva ja ensisijainen versio.
<!-- auto-translated-disclaimer:end -->

# Alustan määritys

Tässä asiakirjassa kuvataan odotettu alustan määritys tämän playbookin suorittamista varten.

## Vaaditut sovellukset/kehykset

### Windows/Linux
Lemonade tulisi olla esiasennettuna [täältä](https://lemonade-server.ai/install_options.html). 

- **Open WebUI** (frontend-verkkosovellus)
- **Lemonade Server** (backend-mallipalvelin)

> Tämä playbook suorittaa **Lemonaden** (Lemonade server/app) **natiivisti**. **Open WebUI** toimii **konttina** Linuxissa (Podmanin kautta) ja **Python-pakettina** Windowsissa. `open-webui` PyPI-paketti tukee vain Python ≤ 3.12 -versioita, joten Linux-kontti välttää vanhempien Python-versioiden hallinnan tarpeen.  

## Mallit (Lemonadessa)

Mallit tulisi ladata **Lemonade-sovelluksen** sisällä (käyttäen sisäänrakennettua Model Manageria) tai Lemonaden mallinhallintakomentojen kautta (`lemonade pull <model_name>`). Tämä playbook olettaa, että alla suositellut mallit on ladattu ja ne näkyvät mallien listausrajapinnassa.

Tarkista mallien saatavuus:
- Avaa: `http://localhost:13305/api/v1/models`
- Ladatut mallit listataan kohdassa `"data"`.

### Suositellut mallit

| Ominaisuus | Malli-ID | Huomiot |
|---|----|-----|
| LLM (Teksti sisään → Teksti ulos) | `Qwen3-4B-Hybrid` (tai vastaava) | Mikä tahansa Lemonade LLM -malli chattiin, tekstin täydennykseen, koodaukseen tai päättelyyn |
| VLM (Kuva → Teksti) | `Qwen3.5-4B-GGUF` (tai mikä tahansa **Vision**-kategorian malli) | Mikä tahansa multimodaalinen/näkökykyinen malli, joka voi ottaa kuvia osana syötettään |
| Kuvan generointi (Teksti → Kuva) | `SDXL-Turbo` (tai mikä tahansa **Image**-kategorian malli) | Mikä tahansa Stable Diffusion -malli, joka generoi kuvia tekstikehotteesta |
| Ääni (Puhe → Teksti) | `Whisper-Large-v3` (tai mikä tahansa **Audio**-kategorian malli) | Mikä tahansa ASR-malli, joka muuntaa äänen tekstiksi |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Käytetyt portit

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Jos nämä portit ovat jo käytössä järjestelmässäsi, vaihda ne palvelinta/palvelimia käynnistettäessä.