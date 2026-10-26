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

# Etäkehitys AMD Syncillä

## Yleiskatsaus

**AMD Sync** muuttaa kannettavasi AMD Ryzen™ AI Halo -laitteen etäohjaamoksi. Unohda manuaalinen SSH-, avain- ja IDE-asetusten määrittäminen — asenna AMD Sync ja saat yhdellä klikkauksella käyttöösi etäpäätteen, VS Coden, JupyterLabin sekä reaaliaikaisen GPU/CPU/muisti-kojelaudan Ryzen AI Halo -laitteella.

Paikallinen koneesi pysyy tuttuna; jokainen komento, muistikirja ja malli suoritetaan Ryzen AI Halo -laitteella.

> **Vinkki**: Tämä sivu sisältää kaikki uudet AMDSyncin päivitykset. 

## Mitä opit

- Ottamaan SSH:n käyttöön Ryzen AI Halo -laitteella ja yhdistämään siihen AMD Syncistä
- Käynnistämään VS Coden, päätteen, JupyterLabin ja Live Metrics -toiminnon Ryzen AI Halo -laitetta vasten yhdellä klikkauksella
- Organisoimaan etätyöskentelyn AMD Syncin hallinnoimien projektikansioiden avulla

---

## Keskeiset käsitteet

AMD Syncissä on kaksi puolta: **asiakas** (kannettavasi, jolla AMD Sync -sovellus toimii) ja **palvelin** (Ryzen AI Halo, jolla toimii SSH-palvelin, johon AMD Sync muodostaa tunnelin). Kaikki, mitä käynnistät AMD Syncistä — VS Code, pääte, muistikirja — avautuu paikallisesti mutta suoritetaan Ryzen AI Halo -laitteella.

> **Tuetut asiakkaat:** Windows 11 ja Linux. macOS ei ole tuettu.

---

## Vaihe 1 — SSH:n käyttöönotto Ryzen AI Halo -laitteella


> **Huomautus:** Windowsissa Ryzen AI Halo toimitetaan niin, että SSH-palvelin on *oletusarvoisesti pois päältä*. Linuxissa se tulee *oletusarvoisesti päällä*.

1. Avaa Ryzen AI Halo -laitteella **AMD Ryzen™ AI Developer Center**.
2. Siirry **Remote**-välilehdelle.
3. Kytke **SSH Server** päälle.
4. Huomioi **IP-osoite**, **portti** ja **käyttäjänimi**, jotka näkyvät kohdassa **Server Information** — liität ne myöhemmin AMD Synciin.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Huomautus:** Tämä on Windowsin AMD Developer Center. Linux-versiossa käyttöliittymä saattaa olla erilainen, mutta etätoiminnot ovat samankaltaiset.

> **Vinkki:** AMD Sync kysyy kyseisen käyttäjän **käyttöjärjestelmän kirjautumissalasanaa**, ei Developer Centerin salasanaa.

---

## Vaihe 2 — AMD Syncin asentaminen asiakaslaitteellesi

AMD Sync toimii Windows 11:ssä ja Linuxissa. Lataa käyttöjärjestelmääsi sopiva asennusohjelma ja noudata alla olevia ohjeita. Asennuksen jälkeen napsauta **Accept & Install** **Get Started** -näytöllä — AMD Sync käynnistyy automaattisesti, kun asennus on valmis.

### Windows

[Lataa AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Kaksoisnapsauta `AMDSyncInstaller.exe`.
2. Napsauta **Accept & Install**.

> Jos Windowsin palomuuri kysyy lupaa, salli AMD Syncille verkkoyhteys, jotta se voi tavoittaa Ryzen AI Halo -laitteen SSH:n kautta.

### Linux

Napsauta linkkiä ladataksesi haluamasi tiedostomuodon:

| Muoto | Lataus | Asennuskomento |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Huomautus:** Ubuntu App Center saattaa merkitä paikallisesti avatun `.deb`-tiedoston *"Potentially unsafe"* -varoituksella. Tämä on tavanomainen varoitus mille tahansa kolmannen osapuolen paikalliselle asennusohjelmalle. Jos `.deb`-tiedoston kaksoisnapsautus epäonnistuu, käytä yllä olevaa pääteohjelmaa.

---

## Vaihe 3 — Yhdistäminen Ryzen AI Halo -laitteeseen

Ensimmäisellä käynnistyskerralla AMD Sync näyttää **Add a Remote Device** -lomakkeen. Täytä se Developer Centerin **Remote**-välilehden arvoilla.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Kenttä | Huomautuksia |
|-------|-------|
| **Device Name** *(valinnainen)* | Ystävällinen nimi, kuten `Ryzen AI Halo`. Oletuksena `Device 1`, `Device 2`, … |
| **Hostname or IP** | Remote-välilehdeltä |
| **SSH Port** | Remote-välilehdeltä (pelkät numerot) |
| **Username** | Käyttöjärjestelmätilisi nimi Ryzen AI Halo -laitteella |
| **Password** | Käyttöjärjestelmän kirjautumissalasanasi — piilotettu kirjoitettaessa |

Napsauta **Add Device**. Lyhyen latausnäytön jälkeen näet tekstin **"Connection Successful"** ja pääset kotinäkymään, joka sijaitsee järjestelmäpalkissasi. Napsauta ikkunan ulkopuolelle sulkeaksesi sen; AMD Sync jää käyntiin ja on yhden klikkauksen päässä.

> **Jos yhteys epäonnistuu,** AMD Sync palaa lomakkeeseen arvosi säilyttäen. Tavallisimmat syyt ovat SSH:n poistaminen käytöstä Ryzen AI Halo -laitteella, väärä salasana tai se, että laitteet ovat eri verkoissa.

---

## Vaihe 4 — Ensimmäisen etätyökalun käynnistäminen

Kotinäkymä tarjoaa viisi yhden klikkauksen komponenttia — kaikki saatavilla riippumatta siitä, mitä käyttöjärjestelmää asiakas ja Ryzen AI Halo käyttävät.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponentti | Mitä se tekee |
|-----------|--------------|
| **Directory** | Valitsee Ryzen AI Halo -laitteella sijaitsevan kansion, johon VS Code, Terminal ja JupyterLab avautuvat. Oletuksena hallinnoitu `Documents/AMD_Sync`-työtila. |
| **VS Code** | Avaa VS Coden paikallisesti SSH-tunnelilla valittuun kansioon. |
| **Terminal** | Avaa paikallisen päätteen, joka on SSH-yhteydessä Ryzen AI Halo -laitteeseen, valitussa kansiossa. |
| **JupyterLab** | Käynnistää muistikirjaprojektin, joka on SSH-yhteydessä Ryzen AI Halo -laitteeseen, rajattuna valittuun kansioon. |
| **Live Metrics** | Reaaliaikainen näkymä GPU:n, muistin ja CPU:n käytöstä Ryzen AI Halo -laitteella. |

### Kokeile VS Codea

Kokeile ensimmäisellä käynnistyskerralla **VS Codea**. Seuraavat ohjeet on tarkoitettu Linuxille, mutta Windows-kokemus on samankaltainen.

1. Jätä **Directory** oletusarvoon `~/Documents/AMD_Sync`.
2. Napsauta **VS Code**.
3. AMD Sync luo hakemiston `Documents/AMD_Sync/Project_1` Ryzen AI Halo -laitteelle ja avaa VS Coden paikallisesti siihen tunneloituna.

Nyt muokkaat tiedostoja, jotka sijaitsevat Ryzen AI Halo -laitteella, omalla paikallisella VS Code -asennuksellasi. Luo tiedosto `helloworld.py`, lisää siihen `print("hello world")`, avaa integroitu pääte (`` Ctrl + ` ``) ja suorita se:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Tilarivillä lukee **SSH: Linux** — todiste siitä, että koodisi suoritetaan Ryzen AI Halo -laitteella, ei kannettavallasi.
### Kokeile Terminaalia

Napsauta **Terminal**, niin pääset samaan kansioon SSH:n kautta poistumatta näppäimistön äärestä.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Windowsissa oletusterminaali on **PowerShell** — vaihda **Windows Command Promptiin** asetusvalikosta, jos haluat mieluummin sen. Linuxissa AMD Sync käyttää järjestelmäsi oletusterminaalia.

---

## Miten Directory toimii

**Directory**-pudotusvalikko on AMD Syncin tärkein yksittäinen hallintaelementti — se määrittää, minne jokainen käynnistämäsi työkalu sijoittuu Ryzen AI Halossa.

- **`~/Documents/AMD_Sync` (oletus)** — Kun käynnistät VS Coden tai JupyterLabin täältä, uusi projektikansio luodaan automaattisesti (`Project_1`, `Project_2`, … VS Codelle; `Notebook_Project_1`, `Notebook_Project_2`, … JupyterLabille).
- **Olemassa olevat projektikansiot** — Jokainen `AMD_Sync`-kansion suora alikansio (mukaan lukien kansiot, jotka olet luonut manuaalisesti Ryzen AI Haloon) näkyy pudotusvalikossa. Viimeksi käyttämäsi kansio asetetaan oletukseksi seuraavalla kerralla.
- **Mukautetut polut** — Kirjoita mikä tahansa absoluuttinen polku avataksesi kansion jostain muualta Ryzen AI Halosta. AMD Sync vain *avaa* sen — se ei luo kansioita `AMD_Sync`-kansion ulkopuolelle, eikä mukautettuja polkuja tallenneta istuntojen välillä.

Jos mukautettu polku ei toimi, AMD Sync kertoo syyn: virheellinen syntaksi, kansiota ei ole olemassa, tai polku osoittaa tiedostoon.

---

## Live Metrics ja JupyterLab

- **Live Metrics** — Reaaliaikainen kojelauta GPU-, muisti- ja CPU-käytöstä. Nopein tapa varmistaa, että etäkoulutusajo todella kuormittaa laitteistoa.
- **JupyterLab** — Täysimittainen muistikirjaprojekti, joka on SSH-yhteydessä Ryzen AI Haloon, ja jolla on oma integroitu terminaalinsa muistikirjasolujen ja komentorivikomentojen sekoittamiseen poistumatta käyttöliittymästä.

---

## Settings ja useat laitteet

**Settings**-valikossa on kolme välilehteä:

| Välilehti | Mitä se kattaa |
|-----|----------------|
| **Devices** | Listaa jokaisen Ryzen AI Halon, johon olet onnistuneesti yhdistänyt. Yhdistä uudelleen, muokkaa tunnistetietoja tai lisää uusi laite. |
| **Information** | Linkkejä dokumentaatioon ja foorumitukeen. |
| **Customize** | Siirrä sovellus toiseen kohtaan työpöydälläsi, vaihda terminaalityyppiä (vain Windows) ja tarkista AMD Syncin päivitykset. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Terminaalityyppi (Windows)** — Valitse **PowerShellin** (oletus) ja **Windows Command Promptin** välillä.
- **Terminaalityyppi (Linux)** — Vain järjestelmän oletusterminaali on käytettävissä.
- **Sovelluspäivitykset** — Tämä välilehti on oikea paikka tarkistaa ja asentaa uusia AMD Sync -versioita suoraan käyttöliittymästä; erillistä päivitysohjelmaa ei tarvita.

> Laite näkyy **Devices**-välilehdellä vasta onnistuneen ensimmäisen yhteyden jälkeen, joten epäonnistuneet yritykset eivät täytä listaa.

---

## Vianmääritys

- **Yhteys epäonnistuu välittömästi** — Varmista, että SSH-palvelin on käytössä Ryzen AI Halon **Remote**-välilehdellä Developer Centerissä.
- **Väärä salasana -virhe** — Käytä Ryzen AI Halon **käyttöjärjestelmän kirjautumissalasanaa**, älä Developer Centeristä otettuja salasanoja.
- **VS Code -painike ei tee mitään** — Asenna VS Code asiakaskoneellesi osoitteesta [code.visualstudio.com](https://code.visualstudio.com).
- **AMD Syncin ilmaisinkuvake puuttuu (Linux/GNOME)** — Asenna ja ota käyttöön AppIndicator-laajennus.
- **`.deb`-tiedosto ei avaudu tiedostonhallinnasta** — Käytä komentoa `sudo apt install ./AMDSyncInstaller.deb` terminaalista.
- **Asennus näkyy uudelleen joka käynnistyksellä (Linux)**: avaa kirjautumisen avainnippu lukituksesta tai käynnistä parametrilla `--password-store=gnome-libsecret`, ja tee asennus sen jälkeen uudelleen kerran.

---