<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. Lataa uusin Windows ComfyUI -asennusohjelma osoitteesta [download.comfy.org](https://download.comfy.org/windows/nsis/x64).
2. Valitse laitteistokokoonpanosi: Valitse `AMD ROCm`.
3. Valitse ComfyUI:n asennussijainti: Käytä oletuspolkua tai haluamaasi kansiota.
4. Työpöytäsovelluksen asetukset: Suosittelemme poistamaan valinnan "Automatic Updates", jotta käytät sovelluksen suositeltua versiota.
5. Paina "Next" aloittaaksesi asennuksen.

<!-- @os:end -->

<!-- @os:linux -->
#### Kloonaa ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (Valinnainen) Siirry tiettyyn versioon
```bash
git checkout v0.19.2
```

#### Asenna ComfyUI:n vaatimukset

Kun Python-virtuaaliympäristö on aktivoitu, suorita:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **Huomio**: Katso lisätietoja [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI) -sivulta.

<!-- @os:end -->