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

**AMD Sync** muuttaa kannettavasi AMD Ryzen™ AI Halo -laitteen etäohjaamoksi. Ohita manuaalinen SSH-, avain- ja IDE-asennus — asenna AMD Sync ja saat yhdellä klikkauksella pääsyn etäpäätteeseen, VS Codeen, JupyterLabiin ja reaaliaikaiseen GPU/CPU/muistikojelautaan Ryzen AI Halo -laitteella.

Paikallinen koneesi pysyy tuttuna; jokainen komento, muistikirja ja malli suoritetaan Ryzen AI Halo -laitteella.

> **Vinkki**: Tälle sivulle lisätään kaikki AMDSyncin uudet päivitykset. 

## Mitä opit

- Ota SSH käyttöön Ryzen AI Halo -laitteella ja muodosta yhteys siihen AMD Sync -sovelluksesta
- Käynnistä VS Code, Terminal, JupyterLab ja Live Metrics Ryzen AI Halo -laitteelle yhdellä klikkauksella
- Järjestä etätyö AMD Syncin hallinnoimien projektikansioiden avulla

---

## Peruskäsitteet

AMD Syncissä on kaksi puolta: **asiakas** (kannettavasi, jolla AMD Sync -sovellus toimii) ja **palvelin** (Ryzen AI Halo, jolla toimii SSH-palvelin, johon AMD Sync muodostaa tunnelin). Kaikki, minkä käynnistät AMD Syncistä — VS Code, pääte, muistikirja — avautuu paikallisesti mutta suoritetaan Ryzen AI Halo -laitteella.

> **Tuetut asiakkaat:** Windows 11 ja Linux. macOS ei ole tuettu.

---

## Vaihe 1 — Ota SSH käyttöön Ryzen AI Halo -laitteella


> **Huomautus:** Windowsissa Ryzen AI Halo toimitetaan SSH-palvelin *oletuksena pois päältä*. Linuxissa SSH-palvelin on *oletuksena päällä*.

1. Avaa Ryzen AI Halo -laitteella **AMD Ryzen™ AI Developer Center**.
2. Siirry **Remote**-välilehdelle.
3. Kytke **SSH Server** päälle.
4. Merkitse muistiin **Server Information** -kohdassa näkyvät **IP Address**, **Port** ja **Username** — liität ne myöhemmin AMD Synciin.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Huomautus:** Tämä on Windowsin AMD Developer Center. Linux-versiossa käyttöliittymä voi olla erilainen, mutta etätoiminnot ovat samankaltaiset.

> **Vinkki:** AMD Sync kysyy kyseisen käyttäjän **käyttöjärjestelmän kirjautumissalasanaa**, ei Developer Centerin salasanaa.

---

## Vaihe 2 — Asenna AMD Sync asiakaskoneellesi

AMD Sync toimii Windows 11:ssä ja Linuxissa. Lataa käyttöjärjestelmääsi vastaava asennusohjelma ja seuraa alla olevia ohjeita. Asennuksen jälkeen napsauta **Accept & Install** **Get Started** -näytöllä — AMD Sync käynnistyy automaattisesti, kun asennus on valmis.

### Windows

[Lataa AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Kaksoisnapsauta `AMDSyncInstaller.exe`.
2. Napsauta **Accept & Install**.

> Jos Windowsin palomuuri kehottaa, salli AMD Syncille verkkoyhteys, jotta se voi ottaa yhteyden Ryzen AI Halo -laitteeseen SSH:n kautta.

### Linux

Napsauta linkkiä ladataksesi haluamasi muodon:

| Muoto | Lataus | Asennuskomento |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Huomautus:** Ubuntu App Center saattaa merkitä paikallisesti avatun `.deb`-tiedoston *"Potentiaalisesti vaaralliseksi."* Tämä on tavanomainen varoitus mille tahansa kolmannen osapuolen paikalliselle asennusohjelmalle. Jos `.deb`-tiedoston kaksoisnapsautus epäonnistuu, käytä yllä olevaa pääteskomentoa.

---

## Vaihe 3 — Yhdistä Ryzen AI Halo -laitteeseen

Ensimmäisellä käynnistyskerralla AMD Sync näyttää **Add a Remote Device** -lomakkeen. Täytä se Developer Centerin **Remote**-välilehdeltä saaduilla arvoilla.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Kenttä | Huomautukset |
|-------|-------|
| **Device Name** *(valinnainen)* | Ystävällinen nimi, esimerkiksi `Ryzen AI Halo`. Oletuksena `Device 1`, `Device 2`, … |
| **Hostname or IP** | Remote-välilehdeltä |
| **SSH Port** | Remote-välilehdeltä (vain numeroita) |
| **Username** | Käyttöjärjestelmätilisi nimi Ryzen AI Halo -laitteella |
| **Password** | Käyttöjärjestelmän kirjautumissalasanasi — piilotettu kirjoittaessasi |

Napsauta **Add Device**. Lyhyen latausnäytön jälkeen näet ilmoituksen **"Connection Successful"** ja siirryt kotinäkymään, joka sijaitsee järjestelmäpalkissasi. Sulje ikkuna napsauttamalla sen ulkopuolelle; AMD Sync jatkaa toimintaansa taustalla ja on yhden klikkauksen päässä.

> **Jos yhteys epäonnistuu,** AMD Sync palaa lomakkeeseen arvosi säilyttäen. Yleisimmät syyt ovat SSH:n poissa oleminen käytöstä Ryzen AI Halo -laitteella, väärä salasana tai laitteiden sijainti eri verkoissa.

---

## Vaihe 4 — Käynnistä ensimmäinen etätyökalusi

Kotinäkymä tarjoaa viisi yhdellä klikkauksella käytettävää komponenttia — kaikki saatavilla riippumatta siitä, mitä käyttöjärjestelmää asiakas ja Ryzen AI Halo käyttävät.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponentti | Mitä se tekee |
|-----------|--------------|
| **Directory** | Valitsee kansion Ryzen AI Halo -laitteella, jossa VS Code, Terminal ja JupyterLab avautuvat. Oletuksena hallinnoitu `Documents/AMD_Sync`-työtila. |
| **VS Code** | Avaa VS Coden paikallisesti SSH-tunnelilla valittuun kansioon. |
| **Terminal** | Avaa paikallisen päätteen SSH-yhteydellä Ryzen AI Halo -laitteeseen, valitussa kansiossa. |
| **JupyterLab** | Käynnistää muistikirjaprojektin SSH-yhteydellä Ryzen AI Halo -laitteeseen, rajattuna valittuun kansioon. |
| **Live Metrics** | Reaaliaikainen näkymä GPU:n, muistin ja CPU:n käytöstä Ryzen AI Halo -laitteella. |

### Kokeile VS Codea

Ensimmäistä käynnistystäsi varten kokeile **VS Codea**.

1. Jätä **Directory** oletusarvoon `~/Documents/AMD_Sync`.
2. Napsauta **VS Code**.
3. AMD Sync luo kansion `Documents/AMD_Sync/Project_1` Ryzen AI Halo -laitteelle ja avaa VS Coden paikallisesti tunnelilla siihen.

Nyt muokkaat tiedostoja, jotka sijaitsevat Ryzen AI Halo -laitteella, käyttäen paikallista VS Code -asennustasi. Luo `helloworld.py`, lisää `print("hello world")`, avaa integroitu pääte (`` Ctrl + ` ``) ja suorita se:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Tilarivillä lukee **SSH: Linux** — todiste siitä, että koodisi suoritetaan Ryzen AI Halo -laitteella, ei kannettavallasi.
### Kokeile Terminaalia

Napsauta **Terminal**-painiketta siirtyäksesi samaan kansioon SSH:n kautta poistumatta näppäimistön äärestä.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Windowsissa oletusterminaali on **PowerShell** — vaihda **Windows Command Promptiin** Asetukset-valikosta, jos haluat. Linuxissa AMD Sync käyttää järjestelmäsi oletusterminaalia.

---

## Miten Hakemisto toimii

**Directory**-alasvetovalikko on AMD Syncin tärkein yksittäinen hallintaelementti — se määrää, minne jokainen käynnistämäsi työkalu päätyy Ryzen AI Halo -laitteella.

- **`~/Documents/AMD_Sync` (oletus)** — VS Coden tai JupyterLabin käynnistäminen täältä luo automaattisesti uuden projektikansion (`Project_1`, `Project_2`, … VS Codelle; `Notebook_Project_1`, `Notebook_Project_2`, … JupyterLabille).
- **Olemassa olevat projektikansiot** — Mikä tahansa `AMD_Sync`-kansion suora alikansio (mukaan lukien kansiot, jotka luot manuaalisesti Ryzen AI Halo -laitteella) näkyy alasvetovalikossa. Viimeksi käyttämästäsi kansiosta tulee oletus seuraavalla kerralla.
- **Mukautetut polut** — Kirjoita mikä tahansa absoluuttinen polku avataksesi kansion muualta Ryzen AI Halo -laitteelta. AMD Sync ainoastaan *avaa* sen — se ei luo kansioita `AMD_Sync`-kansion ulkopuolelle, eivätkä mukautetut polut tallennu istuntojen välillä.

Jos mukautettu polku ei toimi, AMD Sync kertoo miksi: virheellinen syntaksi, kansiota ei ole olemassa, tai polku osoittaa tiedostoon.

---

## Reaaliaikaiset mittarit ja JupyterLab

- **Live Metrics** — Reaaliaikainen kojelauta GPU:n, muistin ja CPU:n käytöstä. Nopein tapa varmistaa, että etäkoulutusajo todella käyttää laitteistoa.
- **JupyterLab** — Täysi muistikirjaprojekti, joka on SSH-yhteydessä Ryzen AI Halo -laitteeseen, ja jossa on oma integroitu terminaali muistikirjan solujen ja komentotulkkikomentojen sekoittamiseen poistumatta käyttöliittymästä.

---

## Asetukset ja useat laitteet

**Settings**-valikossa on kolme välilehteä:

| Välilehti | Mitä se kattaa |
|-----|----------------|
| **Devices** | Listaa jokaisen Ryzen AI Halo -laitteen, johon olet onnistuneesti muodostanut yhteyden. Muodosta yhteys uudelleen, muokkaa kirjautumistietoja tai lisää uusi laite. |
| **Information** | Linkkejä dokumentaatioon ja foorumitukeen. |
| **Customize** | Siirrä sovellus toiseen kohtaan työpöydälläsi, vaihda terminaalityyppiä (vain Windows) ja tarkista AMD Sync -päivitykset. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Terminaalityyppi (Windows)** — Valitse **PowerShellin** (oletus) ja **Windows Command Promptin** väliltä.
- **Terminaalityyppi (Linux)** — Saatavilla on vain järjestelmän oletusterminaali.
- **Sovelluspäivitykset** — Tämä välilehti on oikea paikka tarkistaa ja asentaa uusia AMD Sync -versioita suoraan käyttöliittymästä; erillistä päivitysohjelmaa ei tarvita.

> Laite näkyy **Devices**-välilehdellä vasta onnistuneen ensimmäisen yhteyden jälkeen, joten epäonnistuneet yritykset eivät ruuhkauta listaa.

---

## Vianmääritys

- **Yhteys epäonnistuu heti** — Varmista, että SSH-palvelin on käytössä Ryzen AI Halo -laitteen **Remote**-välilehdellä Developer Centerissä.
- **Väärä salasana -virhe** — Käytä **käyttöjärjestelmän kirjautumissalasanaa** Ryzen AI Halo -laitteella, älä Developer Centeristä otettuja salasanoja.
- **VS Code -painike ei tee mitään** — Asenna VS Code asiakaskoneellesi osoitteesta [code.visualstudio.com](https://code.visualstudio.com).
- **AMD Sync -ilmaisinkuvake puuttuu (Linux/GNOME)** — Asenna ja ota käyttöön AppIndicator-laajennus.
- **`.deb`-tiedosto ei avaudu tiedostonhallinnasta** — Käytä komentoa `sudo apt install ./AMDSyncInstaller.deb` terminaalista.
- **Asennus tulee näkyviin joka käynnistyksellä (Linux)**: avaa kirjautumisavainnippusi lukituksesta tai käynnistä sovellus valitsimella `--password-store=gnome-libsecret`, ja tee asennus sitten kerran uudelleen.

---