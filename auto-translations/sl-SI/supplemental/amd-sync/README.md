<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Oddaljeni razvoj z aplikacijo AMD Sync

## Pregled

**AMD Sync** vaš prenosnik spremeni v oddaljeno nadzorno ploščo za AMD Ryzen™ AI Halo. Izognite se ročni nastavitvi SSH, ključev in razvojnega okolja — namestite AMD Sync in z enim klikom dostopajte do oddaljenega terminala, VS Code, JupyterLab ter nadzorne plošče za GPU/CPU/pomnilnik v živo na Ryzen AI Halo.

Vaš lokalni računalnik ostane enak, kot ga poznate; vsak ukaz, beležka in model pa se izvajajo na Ryzen AI Halo.

> **Nasvet**: Ta stran bo vsebovala vse nove posodobitve za AMDSync.

## Kaj se boste naučili

- Omogočiti SSH na Ryzen AI Halo in se z njim povezati iz aplikacije AMD Sync
- Z enim klikom zagnati VS Code, terminal, JupyterLab in metrike v živo na Ryzen AI Halo
- Organizirati oddaljeno delo z upravljanimi projektnimi mapami v AMD Sync

---

## Osnovni koncepti

AMD Sync ima dve strani: **odjemalca** (vaš prenosnik, kjer teče aplikacija AMD Sync) in **strežnik** (Ryzen AI Halo, kjer teče strežnik SSH, v katerega se AMD Sync tunelira). Vse, kar zaženete iz AMD Sync — VS Code, terminal, beležko — se odpre lokalno, izvaja pa se na Ryzen AI Halo.

> **Podprti odjemalci:** Windows 11 in Linux. macOS ni podprt.

---

## 1. korak — omogočite SSH na Ryzen AI Halo


> **Opomba:** V sistemu Windows je Ryzen AI Halo privzeto dobavljen z *izklopljenim* strežnikom SSH. V sistemu Linux je strežnik SSH privzeto *vklopljen*.

1. Na Ryzen AI Halo odprite **AMD Ryzen™ AI Developer Center**.
2. Pojdite na zavihek **Remote**.
3. Vklopite **SSH Server**.
4. Zabeležite si **IP Address**, **Port** in **Username**, prikazane pod **Server Information** — te podatke boste prilepili v AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Opomba:** To je AMD Developer Center za Windows. Različica za Linux ima lahko drugačen uporabniški vmesnik, vendar podobno funkcionalnost za oddaljeni dostop.

> **Nasvet:** AMD Sync zahteva **geslo za prijavo v operacijski sistem** tega uporabnika, ne gesla iz Developer Center.

---

## 2. korak — namestite AMD Sync na odjemalski napravi

AMD Sync deluje v sistemih Windows 11 in Linux. Prenesite namestitveni program za svoj operacijski sistem in sledite spodnjim korakom. Po namestitvi kliknite **Accept & Install** na zaslonu **Get Started** — AMD Sync se ob zaključku samodejno zažene.

### Windows

[Prenesite AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Dvokliknite `AMDSyncInstaller.exe`.
2. Kliknite **Accept & Install**.

> Če vas Windows Firewall pozove, dovolite AMD Sync dostop do omrežja, da lahko doseže Ryzen AI Halo prek SSH.

### Linux

Kliknite povezavo za prenos želene oblike:

| Oblika | Prenos | Namestitveni ukaz |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Opomba:** Ubuntu App Center lahko lokalno odprt `.deb` označi kot *"Potencialno nevarno."* To je standardno opozorilo za vsak lokalni namestitveni program tretje osebe. Če dvoklik na `.deb` ne uspe, uporabite zgornji terminalski ukaz.

---

## 3. korak — povežite se s svojim Ryzen AI Halo

Ob prvem zagonu AMD Sync prikaže obrazec **Add a Remote Device**. Izpolnite ga z vrednostmi iz zavihka **Remote** v Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Polje | Opombe |
|-------|-------|
| **Device Name** *(izbirno)* | Prijazna oznaka, na primer `Ryzen AI Halo`. Privzeto `Device 1`, `Device 2`, … |
| **Hostname or IP** | Iz zavihka Remote |
| **SSH Port** | Iz zavihka Remote (samo številke) |
| **Username** | Ime vašega uporabniškega računa OS na Ryzen AI Halo |
| **Password** | Vaše geslo za prijavo v OS — med tipkanjem je skrito |

Kliknite **Add Device**. Po kratkem zaslonu nalaganja boste videli **"Connection Successful"** in pristali na domačem pogledu, ki se nahaja v sistemski vrstici. Kliknite izven okna, da ga zaprete; AMD Sync ostane zagnan in je oddaljen en klik stran.

> **Če povezava ne uspe,** se AMD Sync vrne na obrazec z ohranjenimi vrednostmi. Običajni vzroki so onemogočen SSH na Ryzen AI Halo, napačno geslo ali to, da sta napravi v različnih omrežjih.

---

## 4. korak — zaženite svoje prvo oddaljeno orodje

Domači pogled ponuja pet komponent z enim klikom — vse so na voljo ne glede na to, kateri OS uporabljata odjemalec in Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponenta | Kaj počne |
|-----------|--------------|
| **Directory** | Izbere mapo na Ryzen AI Halo, v kateri se bodo odprli VS Code, Terminal in JupyterLab. Privzeto upravljano delovno okolje `Documents/AMD_Sync`. |
| **VS Code** | Lokalno odpre VS Code s SSH tunelom v izbrano mapo. |
| **Terminal** | Odpre lokalni terminal, povezan prek SSH z Ryzen AI Halo, v izbrani mapi. |
| **JupyterLab** | Zažene projekt z beležko, povezan prek SSH z Ryzen AI Halo, omejen na izbrano mapo. |
| **Live Metrics** | Prikaz izrabe GPU, pomnilnika in CPU na Ryzen AI Halo v realnem času. |

### Preizkusite VS Code

Za prvi zagon preizkusite **VS Code**. Spodnja navodila veljajo za Linux, izkušnja v sistemu Windows pa je podobna.

1. Pustite **Directory** na privzeti vrednosti `~/Documents/AMD_Sync`.
2. Kliknite **VS Code**.
3. AMD Sync ustvari `Documents/AMD_Sync/Project_1` na Ryzen AI Halo in lokalno odpre VS Code, tuneliran vanj.

Zdaj urejate datoteke, ki se nahajajo na Ryzen AI Halo, z lokalno nastavitvijo VS Code. Ustvarite `helloworld.py`, dodajte `print("hello world")`, odprite vgrajeni terminal (`` Ctrl + ` ``) in ga zaženite:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Vrstica stanja prikazuje **SSH: Linux** — dokaz, da se vaša koda izvaja na Ryzen AI Halo, ne na vašem prenosniku.
### Preizkusite terminal

Kliknite **Terminal**, da se prek SSH takoj znajdete v isti mapi, ne da bi zapustili tipkovnico.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

V sistemu Windows je privzeti terminal **PowerShell** — če želite, lahko v meniju z nastavitvami preklopite na **Windows Command Prompt**. V sistemu Linux AMD Sync uporablja privzeti sistemski terminal.

---

## Kako deluje imenik (Directory)

Spustni meni **Directory** je najpomembnejši kontrolnik v AMD Sync — odloča, kje bo pristalo vsako orodje, ki ga zaženete na Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (privzeto)** — Z zagonom VS Code ali JupyterLab iz te mape se samodejno ustvari nova projektna mapa (`Project_1`, `Project_2`, … za VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … za JupyterLab).
- **Obstoječe projektne mape** — V spustnem meniju se prikaže vsak neposredni podrejeni element mape `AMD_Sync` (vključno z mapami, ki jih ročno ustvarite na Ryzen AI Halo). Zadnja uporabljena mapa postane privzeta naslednjič.
- **Mape po meri** — Vnesite poljubno absolutno pot, da odprete mapo drugje na Ryzen AI Halo. AMD Sync jo le *odpre* — ne ustvari map zunaj mape `AMD_Sync`, poti po meri pa se med sejami ne shranjujejo.

Če pot po meri ne deluje, vam AMD Sync pove zakaj: neveljavna sintaksa, mapa ne obstaja ali pa pot kaže na datoteko.

---

## Meritve v živo in JupyterLab

- **Meritve v živo (Live Metrics)** — Nadzorna plošča v živo za uporabo GPU, pomnilnika in CPU. Najhitrejši način za potrditev, da oddaljeno učenje modela dejansko obremenjuje strojno opremo.
- **JupyterLab** — Celoten projekt z zvezki, povezan prek SSH z Ryzen AI Halo, z lastnim vgrajenim terminalom za mešanje celic zvezka in ukazov lupine, ne da bi zapustili uporabniški vmesnik.

---

## Nastavitve in več naprav

Meni **Settings** ima tri zavihke:

| Zavihek | Kaj vsebuje |
|-----|----------------|
| **Devices** | Prikaže vse naprave Ryzen AI Halo, s katerimi ste se uspešno povezali. Ponovno se povežite, uredite poverilnice ali dodajte novo napravo. |
| **Information** | Povezave do dokumentacije in podpore na forumu. |
| **Customize** | Premaknite aplikacijo po namizju, preklopite vrsto terminala (samo Windows) in preverite posodobitve za AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Vrsta terminala (Windows)** — Izbirajte med **PowerShell** (privzeto) in **Windows Command Prompt**.
- **Vrsta terminala (Linux)** — Na voljo je samo privzeti sistemski terminal.
- **Posodobitve aplikacije** — Ta zavihek je pravo mesto za preverjanje in nameščanje novih različic AMD Sync neposredno iz uporabniškega vmesnika; ločen posodobitveni program ni potreben.

> Naprava se pod zavihkom **Devices** prikaže šele po uspešni prvi povezavi, zato neuspeli poskusi ne zamašijo seznama.

---

## Odpravljanje težav

- **Povezava takoj spodleti** — Preverite, ali je strežnik SSH omogočen na zavihku **Remote** v razvijalskem centru (Developer Center) na Ryzen AI Halo.
- **Napaka napačnega gesla** — Uporabite svoje **geslo za prijavo v operacijski sistem** na Ryzen AI Halo, ne gesel iz razvijalskega centra (Developer Center).
- **Gumb VS Code ne naredi nič** — Namestite VS Code na svoj odjemalski računalnik s strani [code.visualstudio.com](https://code.visualstudio.com).
- **Ikona AMD Sync v pladnju manjka (Linux/GNOME)** — Namestite in omogočite razširitev AppIndicator.
- **Datoteka `.deb` se ne odpre iz upravitelja datotek** — V terminalu uporabite `sudo apt install ./AMDSyncInstaller.deb`.
- **Nastavitev se ponovno prikaže ob vsakem zagonu (Linux)**: odklenite svojo prijavno zbirko ključev (keyring) ali zaženite z `--password-store=gnome-libsecret`, nato pa enkrat ponovite namestitev.

---