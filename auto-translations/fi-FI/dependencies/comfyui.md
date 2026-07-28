<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. Lataa uusin Windows-käyttöjärjestelmälle tarkoitettu ComfyUI-asennusohjelma osoitteesta [download.comfy.org](https://download.comfy.org/windows/nsis/x64).
2. Valitse laitteistokokoonpanosi: Valitse `AMD ROCm`.
3. Valitse, mihin ComfyUI asennetaan: Käytä oletuspolkua tai haluamaasi kansiota.
4. Työpöytäsovelluksen asetukset: Suosittelemme poistamaan valinnan "Automatic Updates" -kohdasta, jotta käytössäsi on tämän sovelluksen suositeltu versio.
5. Aloita asennus painamalla "Next".

<!-- @os:end -->

<!-- @os:linux -->
#### Kloonaa ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (Valinnainen) Vaihda tiettyyn versioon
```bash
git checkout v0.19.2
```

#### Asenna ComfyUI:n vaatimukset

Kun Python-virtuaaliympäristö on aktivoitu, suorita:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **Huomautus**: Katso lisätietoja osoitteesta [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI).

<!-- @os:end -->