<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Oddaljeni razvoj z AMD Sync

## Pregled

**AMD Sync** vaš prenosnik spremeni v oddaljeni kokpit za AMD Ryzen™ AI Halo. Preskočite ročno nastavljanje SSH, ključev in IDE — namestite AMD Sync in z enim klikom dostopajte do oddaljenega terminala, VS Code, JupyterLab in živega nadzornega zaslona GPU/CPU/pomnilnika na Ryzen AI Halo.

Vaš lokalni računalnik ostane znan; vsak ukaz, zvezek in model se izvaja na Ryzen AI Halo.

> **Nasvet**: Ta stran bo vsebovala vse nove posodobitve za AMDSync.

## Kaj se boste naučili

- Omogočiti SSH na Ryzen AI Halo in se nanj povezati prek AMD Sync
- Z enim klikom zagnati VS Code, Terminal, JupyterLab in Live Metrics na Ryzen AI Halo
- Organizirati oddaljeno delo z upravljanimi projektnimi mapami AMD Sync

---

## Osnovni koncepti

AMD Sync ima dve strani: **odjemalec** (vaš prenosnik, ki poganja aplikacijo AMD Sync) in **strežnik** (Ryzen AI Halo, ki poganja strežnik SSH, v katerega AMD Sync vzpostavi tunel). Vse, kar zaženete iz AMD Sync — VS Code, terminal, zvezek — se odpre lokalno, a izvaja na Ryzen AI Halo.

> **Podprti odjemalci:** Windows 11 in Linux. macOS ni podprt.

---

## Korak 1 — Omogočite SSH na Ryzen AI Halo


> **Opomba:** V sistemu Windows je strežnik SSH na Ryzen AI Halo privzeto *izklopljen*. V sistemu Linux je strežnik SSH privzeto *vklopljen*.

1. Na Ryzen AI Halo odprite **AMD Ryzen™ AI Developer Center**.
2. Pojdite na zavihek **Remote**.
3. Vklopite **SSH Server**.
4. Zabeležite si **IP Address**, **Port** in **Username**, prikazane pod **Server Information** — vnesli jih boste v AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Opomba:** To je AMD Developer Center za Windows. Različica za Linux ima lahko drugačen vmesnik, a podobno funkcionalnost za oddaljeni dostop.

> **Nasvet:** AMD Sync zahteva **geslo za prijavo v OS** tega uporabnika, ne gesla iz Developer Center.

---

## Korak 2 — Namestite AMD Sync na odjemalca

AMD Sync deluje v sistemih Windows 11 in Linux. Prenesite namestitveni program za vaš OS in sledite spodnjim korakom. Po namestitvi kliknite **Accept & Install** na zaslonu **Get Started** — AMD Sync se samodejno zažene, ko je nameščen.

### Windows

[Prenesite AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Dvokliknite `AMDSyncInstaller.exe`.
2. Kliknite **Accept & Install**.

> Če vas Windows Firewall pozove, dovolite AMD Sync dostop do omrežja, da bo lahko dosegel Ryzen AI Halo prek SSH.

### Linux

Kliknite povezavo za prenos želenega formata:

| Format | Prenos | Ukaz za namestitev |
|--------|--------|--------------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Opomba:** Ubuntu App Center lahko lokalno odprt `.deb` označi kot *»Potentially unsafe.«* To je standardno opozorilo za vsak lokalni namestitveni program tretjih oseb. Če z dvoklikom na `.deb` ne uspe, uporabite zgornji terminalski ukaz.

---

## Korak 3 — Povežite se z Ryzen AI Halo

Ob prvem zagonu AMD Sync prikaže obrazec **Add a Remote Device**. Izpolnite ga z vrednostmi iz zavihka **Remote** v Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Polje | Opombe |
|-------|--------|
| **Device Name** *(neobvezno)* | Prijazna oznaka, npr. `Ryzen AI Halo`. Privzeto je `Device 1`, `Device 2`, … |
| **Hostname or IP** | Iz zavihka Remote |
| **SSH Port** | Iz zavihka Remote (samo številke) |
| **Username** | Ime vašega OS računa na Ryzen AI Halo |
| **Password** | Vaše geslo za prijavo v OS — med tipkanjem je skrito |

Kliknite **Add Device**. Po kratkem nalagalnem zaslonu se prikaže **»Connection Successful«** in pristanete na domačem pogledu, ki se nahaja v sistemski vrstici. Kliknite zunaj okna, da ga zaprete; AMD Sync ostane v teku in je dosegljiv z enim klikom.

> **Če povezava ne uspe,** se AMD Sync vrne na obrazec z ohranjenimi vrednostmi. Najpogostejši vzroki so onemogočen SSH na Ryzen AI Halo, napačno geslo ali naprave v različnih omrežjih.

---

## Korak 4 — Zaženite prvo oddaljeno orodje

Domači pogled ponuja pet komponent z enim klikom — vse so na voljo ne glede na to, kateri OS poganjata odjemalec in Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponenta | Kaj počne |
|------------|-----------|
| **Directory** | Izbere mapo na Ryzen AI Halo, v kateri se bodo odprli VS Code, Terminal in JupyterLab. Privzeto je upravljano delovno okolje `Documents/AMD_Sync`. |
| **VS Code** | Odpre VS Code lokalno s SSH tunelom v izbrano mapo. |
| **Terminal** | Odpre lokalni terminal, povezan prek SSH z Ryzen AI Halo, v izbrani mapi. |
| **JupyterLab** | Zažene projekt z zvezki, povezan prek SSH z Ryzen AI Halo, omejen na izbrano mapo. |
| **Live Metrics** | Prikaz v realnem času za izkoriščenost GPU, pomnilnika in CPU na Ryzen AI Halo. |

### Preizkusite VS Code

Za prvi zagon preizkusite **VS Code**.

1. Pustite **Directory** na privzetem `~/Documents/AMD_Sync`.
2. Kliknite **VS Code**.
3. AMD Sync ustvari `Documents/AMD_Sync/Project_1` na Ryzen AI Halo in lokalno odpre VS Code s tunelom vanj.

Zdaj urejate datoteke, ki se nahajajo na Ryzen AI Halo, z vašo lokalno namestitvijo VS Code. Ustvarite `helloworld.py`, dodajte `print("hello world")`, odprite integrirani terminal (`` Ctrl + ` ``) in ga zaženite:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Vrstica stanja prikazuje **SSH: Linux** — dokaz, da se vaša koda izvaja na Ryzen AI Halo in ne na vašem prenosniku.

### Preizkusite Terminal

Kliknite **Terminal**, da se brez tipkovnice spustite v isto mapo prek SSH.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

V sistemu Windows je privzeti terminal **PowerShell** — v meniju Nastavitve preklopite na **Windows Command Prompt**, če ga raje uporabljate. V sistemu Linux AMD Sync uporablja vaš privzeti sistemski terminal.

---

## Kako deluje Directory

Spustni seznam **Directory** je najpomembnejši nadzorni element v AMD Sync — določa, kje na Ryzen AI Halo se odpre vsako orodje, ki ga zaženete.

- **`~/Documents/AMD_Sync` (privzeto)** — Zagon VS Code ali JupyterLab od tu samodejno ustvari novo projektno mapo (`Project_1`, `Project_2`, … za VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … za JupyterLab).
- **Obstoječe projektne mape** — Vsaka neposredna podmapa `AMD_Sync` (vključno z mapami, ki jih ročno ustvarite na Ryzen AI Halo) se prikaže v spustnem seznamu. Zadnja uporabljena mapa postane privzeta naslednjič.
- **Mape po meri** — Vnesite katero koli absolutno pot, da odprete mapo drugje na Ryzen AI Halo. AMD Sync jo samo *odpre* — map zunaj `AMD_Sync` ne bo ustvaril, poti po meri pa se med sejami ne shranijo.

Če pot po meri ne deluje, AMD Sync pojasni razlog: neveljavna sintaksa, mapa ne obstaja ali pot kaže na datoteko.

---

## Live Metrics in JupyterLab

- **Live Metrics** — Živi nadzorni zaslon za izkoriščenost GPU, pomnilnika in CPU. Najhitrejši način za potrditev, da oddaljeno učenje dejansko obremenjuje strojno opremo.
- **JupyterLab** — Celoten projekt z zvezki, povezan prek SSH z Ryzen AI Halo, z lastnim integriranim terminalom za mešanje celic zvezkov in ukazov lupine brez zapuščanja vmesnika.

---

## Nastavitve in več naprav

Meni **Settings** ima tri zavihke:

| Zavihek | Kaj pokriva |
|---------|-------------|
| **Devices** | Navaja vse Ryzen AI Halo naprave, s katerimi ste se uspešno povezali. Znova se povežite, uredite poverilnice ali dodajte novo napravo. |
| **Information** | Povezave do dokumentacije in podpore na forumu. |
| **Customize** | Prestavite aplikacijo na namizju, preklopite vrsto terminala (samo Windows) in preverite posodobitve AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Vrsta terminala (Windows)** — Izberite med **PowerShell** (privzeto) in **Windows Command Prompt**.
- **Vrsta terminala (Linux)** — Na voljo je samo privzeti sistemski terminal.
- **Posodobitve aplikacije** — Ta zavihek je pravo mesto za preverjanje in namestitev novih različic AMD Sync znotraj vmesnika; ločen program za posodabljanje ni potreben.

> Naprava se pod **Devices** prikaže šele po uspešni prvi povezavi, zato neuspeli poskusi ne bodo obremenjevali seznama.

---

## Odpravljanje težav

- **Povezava takoj odpove** — Preverite, ali je strežnik SSH omogočen na zavihku **Remote** v Developer Center na Ryzen AI Halo.
- **Napaka napačnega gesla** — Uporabite **geslo za prijavo v OS** na Ryzen AI Halo, ne gesel iz Developer Center.
- **Gumb VS Code ne naredi ničesar** — Namestite VS Code na odjemalski računalnik s [code.visualstudio.com](https://code.visualstudio.com).
- **Ikona AMD Sync v sistemski vrstici manjka (Linux/GNOME)** — Namestite in omogočite razširitev AppIndicator.
- **`.deb` se ne odpre iz upravitelja datotek** — Uporabite `sudo apt install ./AMDSyncInstaller.deb` iz terminala.

---