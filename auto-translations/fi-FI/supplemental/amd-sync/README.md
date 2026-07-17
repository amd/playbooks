<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Etäkehitys AMD Syncin avulla

## Yleiskatsaus

**AMD Sync** muuttaa kannettavasi AMD Ryzen™ AI Halon etäohjaamoon. Unohda manuaalinen SSH-, avain- ja IDE-määritys — asenna AMD Sync ja saat yhdellä napsautuksella pääsyn etäterminaaliin, VS Codeen, JupyterLabiin sekä reaaliaikaiseen GPU/CPU/muisti-kojelautaan Ryzen AI Halossa.

Paikallinen koneesi pysyy tuttuna; jokainen komento, muistikirja ja malli suoritetaan Ryzen AI Halossa.

> **Vinkki**: Tämä sivu sisältää kaikki AMDSyncin uudet päivitykset.

## Mitä opit

- SSH:n käyttöönotto Ryzen AI Halossa ja siihen yhdistäminen AMD Syncin kautta
- VS Coden, terminaalin, JupyterLabin ja reaaliaikaisten mittareiden käynnistäminen Ryzen AI Haloa vasten yhdellä napsautuksella
- Etätyön järjestäminen AMD Syncin hallittujen projektikohteiden avulla

---

## Peruskäsitteet

AMD Syncissä on kaksi puolta: **asiakas** (kannettavasi, jossa AMD Sync -sovellus on käynnissä) ja **palvelin** (Ryzen AI Halo, jossa SSH-palvelin on käynnissä ja johon AMD Sync muodostaa tunnelin). Kaikki AMD Syncistä käynnistämäsi — VS Code, terminaali, muistikirja — avautuu paikallisesti, mutta suoritetaan Ryzen AI Halossa.

> **Tuetut asiakkaat:** Windows 11 ja Linux. macOS ei ole tuettu.

---

## Vaihe 1 — SSH:n käyttöönotto Ryzen AI Halossa

> **Huomio:** Windowsissa Ryzen AI Halo toimitetaan SSH-palvelin *oletuksena pois päältä*. Linuxissa se toimitetaan SSH-palvelin *oletuksena päällä*.

1. Avaa Ryzen AI Halossa **AMD Ryzen™ AI Developer Center**.
2. Siirry **Remote**-välilehteen.
3. Kytke **SSH Server** päälle.
4. Merkitse muistiin **IP-osoite**, **portti** ja **käyttäjänimi**, jotka näkyvät kohdassa **Server Information** — liität ne AMD Synciin.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Huomio:** Tämä on AMD Developer Center Windowsille. Linuxin versio saattaa näyttää erilaiselta, mutta siinä on vastaava etätoiminnallisuus.

> **Vinkki:** AMD Sync pyytää kyseisen käyttäjän **käyttöjärjestelmän kirjautumissalasanaa**, ei Developer Centerin salasanaa.

---

## Vaihe 2 — AMD Syncin asentaminen asiakkaalle

AMD Sync toimii Windows 11:ssä ja Linuxissa. Lataa asennusohjelma käyttöjärjestelmällesi ja noudata alla olevia ohjeita. Asennuksen jälkeen napsauta **Accept & Install** **Get Started** -näytöllä — AMD Sync käynnistyy automaattisesti, kun asennus on valmis.

### Windows

[Lataa AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Kaksoisnapsauta `AMDSyncInstaller.exe`.
2. Napsauta **Accept & Install**.

> Jos Windows Firewall pyytää lupaa, salli AMD Syncin verkkoyhteys, jotta se voi tavoittaa Ryzen AI Halon SSH:n kautta.

### Linux

Napsauta linkkiä ladataksesi haluamasi muodon:

| Muoto | Lataus | Asennuskomento |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Huomio:** Ubuntu App Center saattaa merkitä paikallisesti avatun `.deb`-tiedoston *"Mahdollisesti vaaralliseksi."* Tämä on tavallinen varoitus kaikille kolmannen osapuolen paikallisille asennusohjelmille. Jos `.deb`-tiedoston kaksoisnapsautus epäonnistuu, käytä yllä olevaa terminaalikomentoa.

---

## Vaihe 3 — Yhdistäminen Ryzen AI Haloon

Ensimmäisellä käynnistyskerralla AMD Sync näyttää **Add a Remote Device** -lomakkeen. Täytä se Developer Centerin **Remote**-välilehden arvoilla.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Kenttä | Huomiot |
|-------|-------|
| **Device Name** *(valinnainen)* | Kuvaava nimi, kuten `Ryzen AI Halo`. Oletuksena `Device 1`, `Device 2`, … |
| **Hostname or IP** | Remote-välilehdeltä |
| **SSH Port** | Remote-välilehdeltä (vain numerot) |
| **Username** | Käyttöjärjestelmätilisi nimi Ryzen AI Halossa |
| **Password** | Käyttöjärjestelmän kirjautumissalasanasi — peitetty kirjoittaessasi |

Napsauta **Add Device**. Lyhyen latausnäytön jälkeen näet **"Connection Successful"** ja päädyt kotinäkymään, joka sijaitsee järjestelmäpalkissasi. Napsauta ikkunan ulkopuolelle sulkeaksesi sen; AMD Sync jää käynnissä ja on yhden napsautuksen päässä.

> **Jos yhteys epäonnistuu,** AMD Sync palaa lomakkeeseen säilyttäen syöttämäsi arvot. Tavallisimmat syyt ovat SSH:n poissaolo käytöstä Ryzen AI Halossa, väärä salasana tai laitteiden sijainti eri verkoissa.

---

## Vaihe 4 — Ensimmäisen etätyökalun käynnistäminen

Kotinäkymässä on viisi yhdellä napsautuksella käytettävää komponenttia — kaikki käytettävissä riippumatta siitä, mitä käyttöjärjestelmää asiakas ja Ryzen AI Halo käyttävät.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponentti | Mitä se tekee |
|-----------|--------------|
| **Directory** | Valitsee kansion Ryzen AI Halossa, johon VS Code, terminaali ja JupyterLab avautuvat. Oletuksena hallittu `Documents/AMD_Sync`-työtila. |
| **VS Code** | Avaa VS Coden paikallisesti SSH-tunnelilla valittuun kansioon. |
| **Terminal** | Avaa paikallisen terminaalin SSH-yhteydellä Ryzen AI Haloon valitussa kansiossa. |
| **JupyterLab** | Käynnistää muistikirjaprojektin SSH-yhteydellä Ryzen AI Haloon, rajattuna valittuun kansioon. |
| **Live Metrics** | Reaaliaikainen näkymä GPU:n, muistin ja CPU:n käyttöasteesta Ryzen AI Halossa. |

### Kokeile VS Codea

Ensimmäiseksi käynnistykseksi kokeile **VS Codea**.

1. Jätä **Directory** oletukseen `~/Documents/AMD_Sync`.
2. Napsauta **VS Code**.
3. AMD Sync luo `Documents/AMD_Sync/Project_1`-kansion Ryzen AI Haloon ja avaa VS Coden paikallisesti tunnelöituna siihen.

Nyt muokkaat tiedostoja, jotka sijaitsevat Ryzen AI Halossa, paikallisella VS Code -asetuksellasi. Luo `helloworld.py`, lisää `print("hello world")`, avaa integroitu terminaali (`` Ctrl + ` ``) ja suorita se:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Tilapalkissa lukee **SSH: Linux** — todiste siitä, että koodisi suoritetaan Ryzen AI Halossa, ei kannettavassasi.

### Kokeile terminaalia

Napsauta **Terminal** pudotaksesi samaan kansioon SSH:n kautta ilman näppäimistöltä poistumista.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Windowsissa oletusterminaali on **PowerShell** — vaihda **Windows Command Promptiin** Asetukset-valikosta, jos haluat. Linuxissa AMD Sync käyttää järjestelmäsi oletusterminaalia.

---

## Kuinka hakemisto toimii

**Directory**-pudotusvalikko on AMD Syncin tärkein ohjain — se päättää, mihin jokainen käynnistämäsi työkalu sijoittuu Ryzen AI Halossa.

- **`~/Documents/AMD_Sync` (oletus)** — VS Coden tai JupyterLabin käynnistäminen tästä luo automaattisesti uuden projektikohtaisen kansion (`Project_1`, `Project_2`, … VS Codelle; `Notebook_Project_1`, `Notebook_Project_2`, … JupyterLabille).
- **Olemassa olevat projektikansiot** — Kaikki `AMD_Sync`-kansion välittömät alikansiot (mukaan lukien kansiot, jotka luot manuaalisesti Ryzen AI Halossa) näkyvät pudotusvalikossa. Viimeksi käyttämästäsi kansiosta tulee seuraavan kerran oletus.
- **Mukautetut polut** — Kirjoita mikä tahansa absoluuttinen polku avataksesi kansion muualta Ryzen AI Halossa. AMD Sync vain *avaa* sen — se ei luo kansioita `AMD_Sync`-kansion ulkopuolelle, eikä mukautettuja polkuja tallenneta istuntojen välillä.

Jos mukautettu polku ei toimi, AMD Sync kertoo syyn: virheellinen syntaksi, kansiota ei ole olemassa tai polku osoittaa tiedostoon.

---

## Live Metrics ja JupyterLab

- **Live Metrics** — Reaaliaikainen kojelauta GPU:n, muistin ja CPU:n käyttöasteesta. Nopein tapa varmistaa, että etäkoulutusajo todella käyttää laitteistoa.
- **JupyterLab** — Täydellinen muistikirjaprojekti SSH-yhteydellä Ryzen AI Haloon, omalla integroidulla terminaalilla muistikirjasolujen ja komentotulkkikomentojen yhdistämiseen ilman käyttöliittymästä poistumista.

---

## Asetukset ja useat laitteet

**Settings**-valikossa on kolme välilehteä:

| Välilehti | Mitä se kattaa |
|-----|----------------|
| **Devices** | Listaa kaikki Ryzen AI Halot, joihin olet yhdistänyt onnistuneesti. Yhdistä uudelleen, muokkaa tunnistetietoja tai lisää uusi laite. |
| **Information** | Linkit dokumentaatioon ja foorumitukeen. |
| **Customize** | Sijoita sovellus uudelleen työpöydällä, vaihda terminaalityyppiä (vain Windows) ja tarkista AMD Sync -päivitykset. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>

- **Terminaalityyppi (Windows)** — Valitse **PowerShellin** (oletus) ja **Windows Command Promptin** välillä.
- **Terminaalityyppi (Linux)** — Vain järjestelmän oletusterminaali on käytettävissä.
- **Sovelluspäivitykset** — Tämä välilehti on oikea paikka tarkistaa ja asentaa uudet AMD Sync -versiot käyttöliittymästä; erillistä päivitysohjelmaa ei tarvita.

> Laite näkyy **Devices**-kohdassa vasta onnistuneen ensimmäisen yhteyden jälkeen, joten epäonnistuneet yritykset eivät täytä listaa.

---

## Vianmääritys

- **Yhteys epäonnistuu välittömästi** — Varmista, että SSH-palvelin on käytössä Ryzen AI Halon **Remote**-välilehdellä Developer Centerissä.
- **Väärä salasana -virhe** — Käytä Ryzen AI Halon **käyttöjärjestelmän kirjautumissalasanaa**, älä Developer Centeristä otettuja salasanoja.
- **VS Code -painike ei tee mitään** — Asenna VS Code asiakaskoneellesi osoitteesta [code.visualstudio.com](https://code.visualstudio.com).
- **AMD Sync -ilmaisinalue puuttuu (Linux/GNOME)** — Asenna ja ota käyttöön AppIndicator-laajennus.
- **`.deb` ei avaudu tiedostonhallinnasta** — Käytä `sudo apt install ./AMDSyncInstaller.deb` terminaalista.

---