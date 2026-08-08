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

# Etäkehitys AMD Syncin avulla

## Yleiskatsaus

**AMD Sync** muuttaa kannettavan tietokoneesi AMD Ryzen™ AI Halo -laitteen etäohjaamoksi. Ohita manuaalinen SSH-, avain- ja IDE-asetusten teko — asenna AMD Sync ja saat yhden napsautuksen etäpäätteen, VS Coden, JupyterLabin ja reaaliaikaisen GPU/CPU/muisti-kojelaudan käyttöösi Ryzen AI Halo -laitteella.

Paikallinen laitteesi pysyy tuttuna; jokainen komento, muistikirja ja malli suoritetaan Ryzen AI Halo -laitteella.

> **Vinkki**: Tämä sivu sisältää kaikki AMDSyncin uudet päivitykset. 

## Mitä opit

- Ottamaan SSH:n käyttöön Ryzen AI Halo -laitteella ja yhdistämään siihen AMD Syncistä
- Käynnistämään VS Coden, päätteen, JupyterLabin ja Live Metrics -näkymän Ryzen AI Halo -laitetta vasten yhdellä napsautuksella
- Järjestämään etätyötä AMD Syncin hallinnoimien projektikansioiden avulla

---

## Perusteet

AMD Syncillä on kaksi puolta: **asiakas** (kannettava tietokoneesi, jossa AMD Sync -sovellus on käynnissä) ja **palvelin** (Ryzen AI Halo, jossa on käynnissä SSH-palvelin, johon AMD Sync muodostaa tunnelin). Kaikki AMD Syncistä käynnistämäsi — VS Code, pääte, muistikirja — avautuu paikallisesti mutta suoritetaan Ryzen AI Halo -laitteella.

> **Tuetut asiakaslaitteet:** Windows 11 ja Linux. macOS ei ole tuettu.

---

## Vaihe 1 — Ota SSH käyttöön Ryzen AI Halo -laitteella


> **Huomautus:** Windowsissa Ryzen AI Halo -laite toimitetaan SSH-palvelin *oletuksena pois päältä*. Linuxissa se toimitetaan SSH-palvelin *oletuksena päällä*.

1. Avaa Ryzen AI Halo -laitteella **AMD Ryzen™ AI Developer Center**.
2. Siirry **Remote**-välilehdelle.
3. Kytke **SSH Server** päälle.
4. Merkitse muistiin **Server Information** -kohdassa näkyvät **IP Address**-, **Port**- ja **Username**-tiedot — liität ne myöhemmin AMD Synciin.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Huomautus:** Tämä on Windowsin AMD Developer Center. Linux-versiossa käyttöliittymä voi olla erilainen, mutta etätoiminnot ovat samankaltaisia.

> **Vinkki:** AMD Sync pyytää kyseisen käyttäjän **käyttöjärjestelmän kirjautumissalasanaa**, ei Developer Centerin salasanaa.

---

## Vaihe 2 — Asenna AMD Sync asiakaslaitteellesi

AMD Sync toimii Windows 11:ssä ja Linuxissa. Lataa käyttöjärjestelmääsi vastaava asennusohjelma ja seuraa alla olevia ohjeita. Asennuksen jälkeen napsauta **Accept & Install** **Get Started** -näytöllä — AMD Sync käynnistyy automaattisesti, kun asennus on valmis.

### Windows

[Lataa AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Kaksoisnapsauta `AMDSyncInstaller.exe`-tiedostoa.
2. Napsauta **Accept & Install**.

> Jos Windowsin palomuuri kysyy lupaa, salli AMD Syncille verkkoyhteys, jotta se voi tavoittaa Ryzen AI Halo -laitteen SSH:n kautta.

### Linux

Napsauta linkkiä ladataksesi haluamasi tiedostomuodon:

| Muoto | Lataus | Asennuskomento |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Huomautus:** Ubuntu App Center saattaa merkitä paikallisesti avatun `.deb`-tiedoston *"Potentially unsafe"* (mahdollisesti vaaralliseksi). Tämä on tavanomainen varoitus mille tahansa kolmannen osapuolen paikalliselle asennusohjelmalle. Jos `.deb`-tiedoston kaksoisnapsautus ei onnistu, käytä yllä olevaa päätekomentoa.

---

## Vaihe 3 — Yhdistä Ryzen AI Halo -laitteeseesi

Ensimmäisellä käynnistyskerralla AMD Sync näyttää **Add a Remote Device** -lomakkeen. Täytä se Developer Centerin **Remote**-välilehdeltä saamillasi arvoilla.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Kenttä | Huomautukset |
|-------|-------|
| **Device Name** *(valinnainen)* | Kuvaava nimi, esimerkiksi `Ryzen AI Halo`. Oletusarvot ovat `Device 1`, `Device 2`, … |
| **Hostname or IP** | Remote-välilehdeltä |
| **SSH Port** | Remote-välilehdeltä (vain numeroita) |
| **Username** | Käyttöjärjestelmätilisi nimi Ryzen AI Halo -laitteella |
| **Password** | Käyttöjärjestelmän kirjautumissalasanasi — piilotetaan kirjoitettaessa |

Napsauta **Add Device**. Lyhyen latausnäytön jälkeen näet ilmoituksen **"Connection Successful"** ja saavut aloitusnäkymään, joka sijaitsee järjestelmän ilmoitusalueella. Sulje ikkuna napsauttamalla sen ulkopuolelle; AMD Sync jää käyntiin ja on aina yhden napsautuksen päässä.

> **Jos yhteys epäonnistuu,** AMD Sync palaa lomakkeeseen arvojesi säilyessä. Yleisimmät syyt ovat SSH:n olevan pois käytöstä Ryzen AI Halo -laitteella, väärä salasana tai laitteiden oleminen eri verkoissa.

---

## Vaihe 4 — Käynnistä ensimmäinen etätyökalusi

Aloitusnäkymä tarjoaa viisi yhden napsautuksen komponenttia — kaikki käytettävissä riippumatta siitä, mitä käyttöjärjestelmää asiakaslaite ja Ryzen AI Halo käyttävät.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponentti | Mitä se tekee |
|-----------|--------------|
| **Directory** | Valitsee kansion Ryzen AI Halo -laitteella, jossa VS Code, Terminal ja JupyterLab avautuvat. Oletuksena hallinnoitu `Documents/AMD_Sync`-työtila. |
| **VS Code** | Avaa VS Coden paikallisesti SSH-tunnelilla valittuun kansioon. |
| **Terminal** | Avaa paikallisen päätteen SSH-yhteydellä Ryzen AI Halo -laitteeseen, valitussa kansiossa. |
| **JupyterLab** | Käynnistää muistikirjaprojektin SSH-yhteydellä Ryzen AI Halo -laitteeseen, rajattuna valittuun kansioon. |
| **Live Metrics** | Reaaliaikainen näkymä Ryzen AI Halo -laitteen GPU-, muisti- ja CPU-käytöstä. |

### Kokeile VS Codea

Kokeile ensimmäisellä käynnistyskerralla **VS Codea**.

1. Jätä **Directory** oletusarvoon `~/Documents/AMD_Sync`.
2. Napsauta **VS Code**.
3. AMD Sync luo kansion `Documents/AMD_Sync/Project_1` Ryzen AI Halo -laitteelle ja avaa VS Coden paikallisesti tunneloituna siihen.

Muokkaat nyt tiedostoja, jotka sijaitsevat Ryzen AI Halo -laitteella, käyttäen paikallista VS Code -asennustasi. Luo `helloworld.py`-tiedosto, lisää siihen `print("hello world")`, avaa integroitu pääte (`` Ctrl + ` ``) ja suorita se:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Tilapalkissa lukee **SSH: Linux** — todiste siitä, että koodisi suoritetaan Ryzen AI Halo -laitteella, ei kannettavassa tietokoneessasi.
### Kokeile Terminaalia

Napsauta **Terminal**-painiketta siirtyäksesi samaan kansioon SSH:n kautta poistumatta näppäimistön äärestä.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Windowsissa oletusterminaali on **PowerShell** — vaihda **Windows Command Prompt** -vaihtoehtoon asetusvalikosta, jos haluat. Linuxissa AMD Sync käyttää järjestelmäsi oletusterminaalia.

---

## Miten hakemisto toimii

**Directory**-pudotusvalikko on AMD Syncin tärkein yksittäinen säädin — se määrittää, minne jokainen käynnistämäsi työkalu sijoittuu Ryzen AI Halo -laitteella.

- **`~/Documents/AMD_Sync` (oletus)** — VS Coden tai JupyterLabin käynnistäminen tästä luo automaattisesti uuden projektikansion (`Project_1`, `Project_2`, … VS Codelle; `Notebook_Project_1`, `Notebook_Project_2`, … JupyterLabille).
- **Olemassa olevat projektikansiot** — Mikä tahansa `AMD_Sync`-kansion suora alikansio (mukaan lukien kansiot, jotka luot manuaalisesti Ryzen AI Halo -laitteella) näkyy pudotusvalikossa. Viimeksi käyttämästäsi kansiosta tulee oletus seuraavalla kerralla.
- **Mukautetut polut** — Kirjoita mikä tahansa absoluuttinen polku avataksesi kansion muualta Ryzen AI Halo -laitteelta. AMD Sync ainoastaan *avaa* sen — se ei luo kansioita `AMD_Sync`-kansion ulkopuolelle, eivätkä mukautetut polut tallennu istuntojen välillä.

Jos mukautettu polku ei toimi, AMD Sync kertoo miksi: virheellinen syntaksi, kansiota ei ole olemassa tai polku osoittaa tiedostoon.

---

## Live Metrics ja JupyterLab

- **Live Metrics** — Reaaliaikainen kojelauta GPU-, muisti- ja CPU-käytöstä. Nopein tapa varmistaa, että etäkäytössä oleva koulutusajo todella kuormittaa laitteistoa.
- **JupyterLab** — Täysimittainen muistikirjaprojekti, joka on SSH-yhteydessä Ryzen AI Halo -laitteeseen, ja jossa on oma integroitu terminaali muistikirjan solujen ja komentorivikomentojen yhdistämiseen poistumatta käyttöliittymästä.

---

## Asetukset ja useat laitteet

**Settings**-valikossa on kolme välilehteä:

| Välilehti | Mitä se kattaa |
|-----|----------------|
| **Devices** | Luettelo jokaisesta Ryzen AI Halo -laitteesta, johon olet onnistuneesti yhdistänyt. Muodosta yhteys uudelleen, muokkaa tunnuksia tai lisää uusi laite. |
| **Information** | Linkit dokumentaatioon ja foorumituen tukeen. |
| **Customize** | Siirrä sovellus työpöydälläsi, vaihda terminaalityyppiä (vain Windows) ja tarkista AMD Sync -päivitykset. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Terminaalityyppi (Windows)** — Valitse **PowerShellin** (oletus) ja **Windows Command Promptin** väliltä.
- **Terminaalityyppi (Linux)** — Käytettävissä on vain järjestelmän oletusterminaali.
- **Sovelluspäivitykset** — Tämä välilehti on oikea paikka tarkistaa ja asentaa uusia AMD Sync -versioita suoraan käyttöliittymästä; erillistä päivitysohjelmaa ei tarvita.

> Laite näkyy **Devices**-kohdassa vasta onnistuneen ensimmäisen yhteyden jälkeen, joten epäonnistuneet yritykset eivät tuki listaa.

---

## Vianmääritys

- **Yhteys epäonnistuu heti** — Varmista, että SSH-palvelin on käytössä Ryzen AI Halo -laitteen **Remote**-välilehdellä Developer Centerissä.
- **Väärä salasana -virhe** — Käytä Ryzen AI Halo -laitteen **käyttöjärjestelmän kirjautumissalasanaa**, älä Developer Centeristä otettuja salasanoja.
- **VS Code -painike ei tee mitään** — Asenna VS Code asiakaskoneellesi osoitteesta [code.visualstudio.com](https://code.visualstudio.com).
- **AMD Sync -ilmaisinkuvake puuttuu (Linux/GNOME)** — Asenna ja ota käyttöön AppIndicator-laajennus.
- **`.deb`-tiedosto ei avaudu tiedostonhallinnasta** — Käytä komentoa `sudo apt install ./AMDSyncInstaller.deb` terminaalista.

---