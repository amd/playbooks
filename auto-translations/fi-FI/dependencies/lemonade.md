<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Lemonaden asentaminen

<!-- @os:windows -->
Lataa uusin asennusohjelma osoitteesta [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) ja suorita `.msi`-tiedosto.

Asennuksen jälkeen:
- `lemonade`-CLI lisätään automaattisesti järjestelmän PATH-muuttujaan
- Lemonade-palvelimen odotetaan käynnistyvän automaattisesti taustalle

Voit myös asentaa hiljaisesti komentoriviltä:
```cmd
msiexec /i lemonade-server-minimal.msi /qn
```
<!-- @os:end -->

<!-- @os:linux -->
**Ubuntu:**
```bash
sudo add-apt-repository ppa:lemonade-team/stable
sudo apt install lemonade-server
```

**Arch Linux (AUR):**
```bash
yay -S lemonade-server
```

Muita jakeluita varten tai lähdekoodista asentamiseksi, katso [koko asennusvaihtoehdot](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:end -->


#### Lemonade-asennuksen tarkistaminen

Avaa pääte ja suorita:
```bash
lemonade --version
```

Näet tulosteen, joka näyttää tältä:
```
lemonade version x.y.z
```

Jos näet versionumeron, Lemonade on asennettu oikein ja valmis käytettäväksi.

Nopeaa viitteeksi, tässä yleisimmät Lemonade CLI -komennot:

| Komento | Mitä se tekee |
| --- | --- |
| `lemonade --help` | Näyttää kaikki käytettävissä olevat komennot ja liput. |
| `lemonade --version` | Tulostaa asennetun Lemonade-version. |
| `lemonade status` | Vahvistaa, onko Lemonade-palvelin käynnissä ja tavoitettavissa. Oletuksena käytettävä OpenAI-yhteensopiva API-perus-URL-osoite on `http://localhost:13305/api/v1`. |
| `lemonade list` | Listaa mallit, jotka ovat käytettävissä Lemonade-asennuksessasi. |
| `lemonade pull <MODEL_NAME>` | Lataa mallin käynnistämättä sitä. |
| `lemonade run <MODEL_NAME>` | Lataa mallin tarvittaessa ja käynnistää sen sitten päättelyä/keskustelua varten. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | Käynnistää llama.cpp-mallin ROCm-taustajärjestelmällä. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Käynnistää llama.cpp-mallin Vulkan-taustajärjestelmällä. |
| `lemonade config` | Näyttää nykyiset Lemonade-määritysarvot. |
| `lemonade config set llamacpp.backend=rocm` | Asettaa oletusarvoiseksi llama.cpp-taustajärjestelmäksi ROCm:n. |

Uusimpia Lemonade-palvelimen asetuksia tai vianmääritystä varten katso [virallinen Lemonade-dokumentaatio](https://lemonade-server.ai/docs/lemonade-cli/).