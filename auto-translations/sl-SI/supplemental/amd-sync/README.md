<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Oddaljeni razvoj z AMD Sync

## Pregled

**AMD Sync** vaš prenosnik spremeni v oddaljeni nadzorni pult za AMD Ryzen™ AI Halo. Preskočite ročno nastavitev SSH, ključev in IDE-ja — namestite AMD Sync in z enim klikom dobite dostop do oddaljenega terminala, VS Code, JupyterLab in nadzorne plošče v živo za GPU/CPU/pomnilnik na Ryzen AI Halo.

Vaš lokalni računalnik ostane znan; vsak ukaz, zvezek in model se izvaja na Ryzen AI Halo.

> **Nasvet**: Ta stran bo vsebovala vse nove posodobitve za AMDSync. 

## Kaj se boste naučili

- Omogočite SSH na Ryzen AI Halo in se z njim povežite iz AMD Sync
- Zaženite VS Code, terminal, JupyterLab in Live Metrics na Ryzen AI Halo z enim klikom
- Organizirajte oddaljeno delo z uporabo upravljanih projektnih map v AMD Sync

---

## Osnovni koncepti

AMD Sync ima dve strani: **odjemalca** (vaš prenosnik, na katerem teče aplikacija AMD Sync) in **strežnik** (Ryzen AI Halo, na katerem teče strežnik SSH, v katerega se AMD Sync tunelira). Vse, kar zaženete iz AMD Sync — VS Code, terminal, zvezek — se odpre lokalno, izvaja pa se na Ryzen AI Halo.

> **Podprti odjemalci:** Windows 11 in Linux. macOS ni podprt.

---

## Korak 1 — Omogočite SSH na Ryzen AI Halo


> **Opomba:** V sistemu Windows je Ryzen AI Halo v osnovi dobavljen z izklopljenim strežnikom SSH. V sistemu Linux je dobavljen z vklopljenim strežnikom SSH v osnovi.

1. Na Ryzen AI Halo odprite **AMD Ryzen™ AI Developer Center**.
2. Pojdite na zavihek **Remote**.
3. Vklopite **SSH Server**.
4. Zabeležite si **IP Address**, **Port** in **Username**, ki so prikazani pod **Server Information** — te podatke boste prilepili v AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Opomba:** To je AMD Developer Center za Windows. Različica za Linux ima morda drugačen uporabniški vmesnik, vendar podobno funkcionalnost za oddaljeni dostop.

> **Nasvet:** AMD Sync zahteva **geslo za prijavo v operacijski sistem** tega uporabnika, ne gesla iz Developer Center.

---

## Korak 2 — Namestite AMD Sync na svoj odjemalec

AMD Sync deluje na Windows 11 in Linux. Prenesite namestitveni program za svoj operacijski sistem in nato sledite spodnjim korakom. Po namestitvi kliknite **Accept & Install** na zaslonu **Get Started** — AMD Sync se ob zaključku samodejno zažene.

### Windows

[Prenesite AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Dvokliknite `AMDSyncInstaller.exe`.
2. Kliknite **Accept & Install**.

> Če vas Windows Firewall pozove, dovolite AMD Sync omrežni dostop, da lahko doseže Ryzen AI Halo prek SSH.

### Linux

Kliknite povezavo za prenos želene oblike:

| Oblika | Prenos | Ukaz za namestitev |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Opomba:** Ubuntu App Center lahko lokalno odprt `.deb` označi kot *»Potencialno nevarno«*. To je standardno opozorilo za vsak lokalno nameščen program tretje osebe. Če dvoklik na `.deb` ne uspe, uporabite zgornji terminalski ukaz.

---

## Korak 3 — Povežite se s svojim Ryzen AI Halo

Ob prvem zagonu AMD Sync prikaže obrazec **Add a Remote Device**. Izpolnite ga z vrednostmi iz zavihka **Remote** v Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Polje | Opombe |
|-------|-------|
| **Device Name** *(neobvezno)* | Prijazna oznaka, npr. `Ryzen AI Halo`. Privzeto je `Device 1`, `Device 2`, … |
| **Hostname or IP** | Iz zavihka Remote |
| **SSH Port** | Iz zavihka Remote (samo številke) |
| **Username** | Ime vašega uporabniškega računa v operacijskem sistemu na Ryzen AI Halo |
| **Password** | Vaše geslo za prijavo v operacijski sistem — med tipkanjem je zakrito |

Kliknite **Add Device**. Po kratkem nalaganju boste videli sporočilo **»Connection Successful«** in se znašli na domačem zaslonu, ki se nahaja v vaši sistemski vrstici. Kliknite izven okna, da ga zaprete; AMD Sync ostane zagnan in je oddaljen le en klik.

> **Če povezava ne uspe,** se AMD Sync vrne na obrazec z ohranjenimi vnesenimi vrednostmi. Običajni vzroki so onemogočen SSH na Ryzen AI Halo, napačno geslo ali dejstvo, da sta napravi v različnih omrežjih.

---

## Korak 4 — Zaženite svoje prvo oddaljeno orodje

Domači zaslon ponuja pet komponent z enim klikom — vse so na voljo ne glede na to, kateri operacijski sistem uporabljata odjemalec in Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponenta | Kaj počne |
|-----------|--------------|
| **Directory** | Izbere mapo na Ryzen AI Halo, v kateri se bodo odprli VS Code, Terminal in JupyterLab. Privzeto je nastavljen upravljan delovni prostor `Documents/AMD_Sync`. |
| **VS Code** | Odpre VS Code lokalno s tunelom SSH v izbrano mapo. |
| **Terminal** | Odpre lokalni terminal, povezan prek SSH z Ryzen AI Halo, v izbrani mapi. |
| **JupyterLab** | Zažene projekt zvezka, povezan prek SSH z Ryzen AI Halo, omejen na izbrano mapo. |
| **Live Metrics** | Prikaz izkoriščenosti GPE, pomnilnika in CPE na Ryzen AI Halo v realnem času. |

### Preizkusite VS Code

Za prvi zagon preizkusite **VS Code**.

1. Pustite **Directory** na privzeti vrednosti `~/Documents/AMD_Sync`.
2. Kliknite **VS Code**.
3. AMD Sync ustvari `Documents/AMD_Sync/Project_1` na Ryzen AI Halo in lokalno odpre VS Code, tuneliran vanj.

Zdaj urejate datoteke, ki se nahajajo na Ryzen AI Halo, z vašo lokalno nastavitvijo VS Code. Ustvarite `helloworld.py`, dodajte `print("hello world")`, odprite vgrajeni terminal (`` Ctrl + ` ``) in ga zaženite:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

V statusni vrstici piše **SSH: Linux** — dokaz, da se vaša koda izvaja na Ryzen AI Halo, ne na vašem prenosniku.
### Preizkusite terminal

Kliknite **Terminal**, da se prek SSH povežete z isto mapo, ne da bi zapustili tipkovnico.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

V sistemu Windows je privzeti terminal **PowerShell** – če želite, ga lahko v meniju z nastavitvami zamenjate za **Windows Command Prompt**. V sistemu Linux AMD Sync uporablja privzeti sistemski terminal.

---

## Kako deluje mapa (Directory)

Spustni meni **Directory** je najpomembnejši kontrolnik v AMD Sync – določa, kam na Ryzen AI Halo pristane vsako orodje, ki ga zaženete.

- **`~/Documents/AMD_Sync` (privzeto)** – Zagon VS Code ali JupyterLab iz te mape samodejno ustvari novo mapo projekta (`Project_1`, `Project_2`, … za VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … za JupyterLab).
- **Obstoječe mape projektov** – V spustnem meniju se prikaže vsak neposredni podrejeni element mape `AMD_Sync` (vključno z mapami, ki jih ročno ustvarite na Ryzen AI Halo). Zadnja uporabljena mapa postane privzeta ob naslednji uporabi.
- **Poti po meri** – Vnesite katero koli absolutno pot, da odprete mapo drugje na Ryzen AI Halo. AMD Sync jo le *odpre* – ne ustvarja map zunaj mape `AMD_Sync`, poti po meri pa se med sejami ne shranjujejo.

Če pot po meri ne deluje, vam AMD Sync sporoči zakaj: neveljavna sintaksa, mapa ne obstaja ali pa pot kaže na datoteko.

---

## Sprotne meritve (Live Metrics) in JupyterLab

- **Live Metrics** – Nadzorna plošča v živo za prikaz uporabe GPU, pomnilnika in CPU. Najhitrejši način za potrditev, da oddaljeno učenje dejansko obremenjuje strojno opremo.
- **JupyterLab** – Popoln projekt z zvezkom, povezan prek SSH z Ryzen AI Halo, z lastnim vgrajenim terminalom za mešanje celic zvezka in ukazov lupine, ne da bi zapustili uporabniški vmesnik.

---

## Nastavitve in več naprav

Meni **Settings** ima tri zavihke:

| Zavihek | Kaj vsebuje |
|-----|----------------|
| **Devices** | Prikaže vse naprave Ryzen AI Halo, s katerimi ste se uspešno povezali. Ponovno se povežite, uredite poverilnice ali dodajte novo napravo. |
| **Information** | Povezave do dokumentacije in podpore na forumu. |
| **Customize** | Premaknite aplikacijo na namizju, preklopite vrsto terminala (samo Windows) in preverite posodobitve za AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Vrsta terminala (Windows)** – Izbirate lahko med **PowerShell** (privzeto) in **Windows Command Prompt**.
- **Vrsta terminala (Linux)** – Na voljo je le privzeti sistemski terminal.
- **Posodobitve aplikacije** – Ta zavihek je pravo mesto za preverjanje in namestitev novih različic AMD Sync neposredno iz uporabniškega vmesnika; ločen posodabljalnik ni potreben.

> Naprava se pod **Devices** prikaže šele po uspešni prvi povezavi, tako da neuspeli poskusi ne zamašijo seznama.

---

## Odpravljanje težav

- **Povezava takoj spodleti** – Preverite, ali je strežnik SSH omogočen na zavihku **Remote** v razvijalskem centru (Developer Center) na Ryzen AI Halo.
- **Napaka zaradi napačnega gesla** – Uporabite svoje **prijavno geslo operacijskega sistema** na Ryzen AI Halo, ne gesel iz razvijalskega centra.
- **Gumb VS Code ne naredi ničesar** – Namestite VS Code na svoj odjemalski računalnik s spletnega mesta [code.visualstudio.com](https://code.visualstudio.com).
- **Ikona AMD Sync v pladnju manjka (Linux/GNOME)** – Namestite in omogočite razširitev AppIndicator.
- **Datoteka `.deb` se ne odpre iz upravitelja datotek** – V terminalu uporabite `sudo apt install ./AMDSyncInstaller.deb`.
- **Namestitev se prikaže ob vsakem zagonu (Linux)**: odklenite svoj prijavni obroček s ključi (login keyring) ali zaženite z `--password-store=gnome-libsecret`, nato pa še enkrat opravite nastavitev.

---