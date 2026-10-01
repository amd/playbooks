<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Konekäännös.** Tämä sivu on käännetty automaattisesti englannista, eikä sitä ole tarkistanut ihminen. Se voi sisältää virheitä, ja tietyt ohjeet, komennot, lataukset, tuotteiden saatavuus tai muu sisältö voivat vaihdella kielen tai alueen mukaan. Mahdollisten ristiriitaisuuksien tai epäjohdonmukaisuuksien ilmetessä alkuperäinen englanninkielinen playbook on ratkaiseva ja ensisijainen versio.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Etäkehitys AMD Sync -sovelluksella

## Yleiskatsaus

**AMD Sync** muuttaa kannettavan tietokoneesi etäohjaamoksi AMD Ryzen™ AI Halolle. Ohita manuaalinen SSH-, avain- ja IDE-asennus — asenna AMD Sync ja saat yhdellä napsautuksella pääsyn etäpäätteeseen, VS Codeen, JupyterLabiin sekä reaaliaikaiseen GPU/CPU/muisti-kojelautaan Ryzen AI Halolla.

Paikallinen koneesi pysyy tuttuna; jokainen komento, muistikirja ja malli suoritetaan Ryzen AI Halolla.

> **Vinkki**: Tälle sivulle lisätään kaikki uudet AMDSyncin päivitykset. 

## Mitä opit

- Ota SSH käyttöön Ryzen AI Halolla ja muodosta yhteys siihen AMD Syncistä
- Käynnistä VS Code, pääte, JupyterLab ja Live Metrics Ryzen AI Haloa vasten yhdellä napsautuksella
- Järjestä etätyöskentely AMD Syncin hallinnoitujen projektikansioiden avulla

---

## Peruskäsitteet

AMD Syncissä on kaksi puolta: **asiakas** (kannettava tietokoneesi, jossa AMD Sync -sovellus toimii) ja **palvelin** (Ryzen AI Halo, jossa toimii SSH-palvelin, johon AMD Sync muodostaa tunnelin). Kaikki, mitä käynnistät AMD Syncistä — VS Code, pääte, muistikirja — avautuu paikallisesti, mutta suoritetaan Ryzen AI Halolla.

> **Tuetut asiakaslaitteet:** Windows 11 ja Linux. macOS:ää ei tueta.

---

## Vaihe 1 — Ota SSH käyttöön Ryzen AI Halolla


> **Huomautus:** Windowsissa Ryzen AI Halo toimitetaan siten, että SSH-palvelin on *oletuksena pois päältä*. Linuxissa se toimitetaan siten, että SSH-palvelin on *oletuksena päällä*.

1. Avaa Ryzen AI Halolla **AMD Ryzen™ AI Developer Center**.
2. Siirry välilehdelle **Remote**.
3. Kytke **SSH Server** päälle.
4. Huomioi **IP Address**-, **Port**- ja **Username**-tiedot, jotka näkyvät kohdassa **Server Information** — liität ne myöhemmin AMD Synciin.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Huomautus:** Tämä on AMD Developer Center Windowsille. Linux-versiossa käyttöliittymä voi olla erilainen, mutta etäominaisuudet ovat samankaltaiset.

> **Vinkki:** AMD Sync pyytää kyseisen käyttäjän **käyttöjärjestelmän kirjautumissalasanaa**, ei Developer Centerin salasanaa.

---

## Vaihe 2 — Asenna AMD Sync asiakaslaitteellesi

AMD Sync toimii Windows 11:llä ja Linuxilla. Lataa asennusohjelma käyttöjärjestelmällesi ja seuraa alla olevia ohjeita. Asennuksen jälkeen napsauta **Accept & Install** **Get Started** -näytöllä — AMD Sync käynnistyy automaattisesti, kun asennus on valmis.

### Windows

[Lataa AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Kaksoisnapsauta tiedostoa `AMDSyncInstaller.exe`.
2. Napsauta **Accept & Install**.

> Jos Windowsin palomuuri kysyy lupaa, salli AMD Syncille verkkoyhteys, jotta se voi ottaa yhteyden Ryzen AI Haloon SSH:n kautta.

### Linux

Napsauta linkkiä ladataksesi haluamasi muodon:

| Muoto | Lataus | Asennuskomento |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Huomautus:** Ubuntu App Center saattaa merkitä paikallisesti avatun `.deb`-tiedoston *"Potentially unsafe"* -varoituksella. Tämä on tavanomainen varoitus mille tahansa kolmannen osapuolen paikalliselle asennusohjelmalle. Jos `.deb`-tiedoston kaksoisnapsautus ei onnistu, käytä yllä olevaa pääteohjelman komentoa.

---

## Vaihe 3 — Muodosta yhteys Ryzen AI Haloosi

Ensimmäisellä käynnistyskerralla AMD Sync näyttää **Add a Remote Device** -lomakkeen. Täytä se Developer Centerin **Remote**-välilehden arvoilla.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Kenttä | Huomautuksia |
|-------|-------|
| **Device Name** *(valinnainen)* | Kuvaava nimi, kuten `Ryzen AI Halo`. Oletuksena `Device 1`, `Device 2`, … |
| **Hostname or IP** | Remote-välilehdeltä |
| **SSH Port** | Remote-välilehdeltä (vain numeroita) |
| **Username** | Käyttöjärjestelmätilisi nimi Ryzen AI Halolla |
| **Password** | Käyttöjärjestelmän kirjautumissalasanasi — piilotettuna kirjoittaessasi |

Napsauta **Add Device**. Lyhyen latausnäytön jälkeen näet ilmoituksen **"Connection Successful"** ja päädyt kotinäkymään, joka sijaitsee järjestelmän ilmaisinalueella. Napsauta ikkunan ulkopuolelle sulkeaksesi sen; AMD Sync jää käyntiin ja on aina yhden napsautuksen päässä.

> **Jos yhteys epäonnistuu,** AMD Sync palaa lomakkeeseen aiemmin syöttämillesi arvoilla. Tavallisimmat syyt ovat SSH pois käytöstä Ryzen AI Halolla, väärä salasana tai laitteiden sijaitseminen eri verkoissa.

---

## Vaihe 4 — Käynnistä ensimmäinen etätyökalusi

Kotinäkymä tarjoaa viisi yhden napsautuksen komponenttia — kaikki käytettävissä riippumatta siitä, mitä käyttöjärjestelmää asiakaslaite ja Ryzen AI Halo käyttävät.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponentti | Mitä se tekee |
|-----------|--------------|
| **Directory** | Valitsee kansion Ryzen AI Halolla, johon VS Code, pääte ja JupyterLab avautuvat. Oletuksena hallinnoitu `Documents/AMD_Sync`-työtila. |
| **VS Code** | Avaa VS Coden paikallisesti SSH-tunnelilla valittuun kansioon. |
| **Terminal** | Avaa paikallisen päätteen, joka on SSH-yhteydessä Ryzen AI Haloon, valitussa kansiossa. |
| **JupyterLab** | Käynnistää muistikirjaprojektin, joka on SSH-yhteydessä Ryzen AI Haloon ja rajattu valittuun kansioon. |
| **Live Metrics** | Reaaliaikainen näkymä GPU:n, muistin ja CPU:n käytöstä Ryzen AI Halolla. |

### Kokeile VS Codea

Kokeile ensimmäisellä käynnistyskerralla **VS Codea**.

1. Jätä **Directory** oletusarvoon `~/Documents/AMD_Sync`.
2. Napsauta **VS Code**.
3. AMD Sync luo kansion `Documents/AMD_Sync/Project_1` Ryzen AI Halolle ja avaa VS Coden paikallisesti tunnelin kautta siihen.

Muokkaat nyt tiedostoja, jotka sijaitsevat Ryzen AI Halolla, paikallisella VS Code -asennuksellasi. Luo tiedosto `helloworld.py`, lisää siihen `print("hello world")`, avaa integroitu pääte (`` Ctrl + ` ``) ja suorita se:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Tilarivillä lukee **SSH: Linux** — todiste siitä, että koodisi suoritetaan Ryzen AI Halolla, ei kannettavassa tietokoneessasi.
### Kokeile Terminaalia

Napsauta **Terminal** siirtyäksesi samaan kansioon SSH-yhteyden kautta poistumatta näppäimistön ääreltä.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Windowsissa oletusterminaali on **PowerShell** — vaihda **Windows Command Prompt** -vaihtoehtoon Asetukset-valikosta, jos haluat. Linuxissa AMD Sync käyttää järjestelmän oletusterminaalia.

---

## Miten Hakemisto toimii

**Directory**-valikko on AMD Syncin tärkein yksittäinen hallintaelementti — se määrittää, minne jokainen käynnistämäsi työkalu tallentuu Ryzen AI Halo -laitteella.

- **`~/Documents/AMD_Sync` (oletus)** — VS Coden tai JupyterLabin käynnistäminen täältä luo automaattisesti uuden projektikansion (`Project_1`, `Project_2`, … VS Codelle; `Notebook_Project_1`, `Notebook_Project_2`, … JupyterLabille).
- **Olemassa olevat projektikansiot** — Jokainen `AMD_Sync`-kansion suora alikansio (mukaan lukien kansiot, jotka olet luonut manuaalisesti Ryzen AI Halo -laitteelle) näkyy pudotusvalikossa. Viimeksi käyttämästäsi kansiosta tulee oletus seuraavalla kerralla.
- **Mukautetut polut** — Kirjoita mikä tahansa absoluuttinen polku avataksesi kansion muualta Ryzen AI Halo -laitteelta. AMD Sync vain *avaa* sen — se ei luo kansioita `AMD_Sync`-kansion ulkopuolelle, eikä mukautettuja polkuja tallenneta istuntojen välillä.

Jos mukautettu polku ei toimi, AMD Sync kertoo syyn: virheellinen syntaksi, kansiota ei ole olemassa tai polku osoittaa tiedostoon.

---

## Live-mittarit ja JupyterLab

- **Live Metrics** — Reaaliaikainen kojelauta GPU:n, muistin ja CPU:n käytöstä. Nopein tapa varmistaa, että etäkoulutusajo todella käyttää laitteistoa.
- **JupyterLab** — Täysimittainen muistikirjaprojekti SSH-yhteydellä Ryzen AI Halo -laitteeseen, jossa on oma integroitu terminaali muistikirjasolujen ja komentorivikomentojen sekoittamiseen poistumatta käyttöliittymästä.

---

## Asetukset ja useat laitteet

**Settings**-valikossa on kolme välilehteä:

| Välilehti | Mitä se kattaa |
|-----|----------------|
| **Devices** | Listaa jokaisen Ryzen AI Halo -laitteen, johon olet onnistuneesti muodostanut yhteyden. Muodosta yhteys uudelleen, muokkaa tunnuksia tai lisää uusi laite. |
| **Information** | Linkkejä dokumentaatioon ja foorumituki. |
| **Customize** | Siirrä sovellus toiseen paikkaan työpöydällä, vaihda terminaalityyppiä (vain Windows) ja tarkista AMD Sync -päivitykset. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Terminaalityyppi (Windows)** — Valitse **PowerShell** (oletus) tai **Windows Command Prompt** väliltä.
- **Terminaalityyppi (Linux)** — Käytettävissä on vain järjestelmän oletusterminaali.
- **Sovelluspäivitykset** — Tämä välilehti on oikea paikka tarkistaa ja asentaa uusia AMD Sync -versioita suoraan käyttöliittymästä; erillistä päivitystyökalua ei tarvita.

> Laite näkyy **Devices**-välilehdellä vasta onnistuneen ensimmäisen yhteyden jälkeen, joten epäonnistuneet yritykset eivät sotke listaa.

---

## Vianmääritys

- **Yhteys epäonnistuu heti** — Varmista, että SSH-palvelin on käytössä Ryzen AI Halo -laitteen **Remote**-välilehdellä Developer Centerissä.
- **Väärä salasana -virhe** — Käytä **käyttöjärjestelmän kirjautumissalasanaa** Ryzen AI Halo -laitteella, älä Developer Centeristä otettuja salasanoja.
- **VS Code -painike ei tee mitään** — Asenna VS Code asiakaskoneellesi osoitteesta [code.visualstudio.com](https://code.visualstudio.com).
- **AMD Sync -kuvake puuttuu ilmoitusalueelta (Linux/GNOME)** — Asenna ja ota käyttöön AppIndicator-laajennus.
- **`.deb`-tiedosto ei avaudu tiedostonhallinnasta** — Käytä komentoa `sudo apt install ./AMDSyncInstaller.deb` terminaalissa.
- **Asennus näkyy uudelleen joka käynnistyksellä (Linux)**: avaa kirjautumisavainrenkaasi lukitus tai käynnistä parametrilla `--password-store=gnome-libsecret` ja tee asennus uudelleen kerran.

---