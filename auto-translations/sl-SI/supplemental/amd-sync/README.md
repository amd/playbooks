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

**AMD Sync** spremeni vaš prenosnik v oddaljeno komandno mesto za AMD Ryzen™ AI Halo. Izognite se ročni nastavitvi SSH, ključev in IDE — namestite AMD Sync in pridobite dostop z enim klikom do oddaljenega terminala, VS Code, JupyterLab in nadzorne plošče GPU/CPU/pomnilnika v živo na Ryzen AI Halo.

Vaš lokalni računalnik ostane znan; vsak ukaz, beležnica in model se izvajajo na Ryzen AI Halo.

> **Nasvet**: Ta stran bo vsebovala vse nove posodobitve za AMDSync. 

## Kaj se boste naučili

- Omogočili SSH na Ryzen AI Halo in se z njim povezali iz AMD Sync
- Zagnali VS Code, Terminal, JupyterLab in Live Metrics proti Ryzen AI Halo z enim klikom
- Organizirali oddaljeno delo z uporabo upravljanih projektnih map v AMD Sync

---

## Osnovni koncepti

AMD Sync ima dve strani: **odjemalca** (vaš prenosnik, na katerem teče aplikacija AMD Sync) in **strežnik** (Ryzen AI Halo, na katerem teče strežnik SSH, v katerega se tunelira AMD Sync). Vse, kar zaženete iz AMD Sync — VS Code, terminal, beležnico — se odpre lokalno, izvaja pa se na Ryzen AI Halo.

> **Podprti odjemalci:** Windows 11 in Linux. macOS ni podprt.

---

## Korak 1 — Omogočite SSH na Ryzen AI Halo


> **Opomba:** V sistemu Windows je Ryzen AI Halo privzeto dobavljen z izklopljenim strežnikom SSH. V sistemu Linux je strežnik SSH privzeto vklopljen.

1. Na Ryzen AI Halo odprite **AMD Ryzen™ AI Developer Center**.
2. Pojdite na zavihek **Remote**.
3. Preklopite **SSH Server** na vklopljeno.
4. Zabeležite si **IP Address**, **Port** in **Username**, prikazane pod **Server Information** — te podatke boste prilepili v AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Opomba:** To je AMD Developer Center za Windows. Različica za Linux ima lahko drugačen uporabniški vmesnik, vendar podobno funkcionalnost za oddaljen dostop.

> **Nasvet:** AMD Sync zahteva **geslo za prijavo v OS** tega uporabnika, ne gesla iz Developer Center.

---

## Korak 2 — Namestite AMD Sync na svojem odjemalcu

AMD Sync deluje na Windows 11 in Linux. Prenesite namestitveni program za svoj OS in nato sledite spodnjim korakom. Po namestitvi kliknite **Accept & Install** na zaslonu **Get Started** — AMD Sync se ob zaključku samodejno zažene.

### Windows

[Prenesite AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Dvokliknite `AMDSyncInstaller.exe`.
2. Kliknite **Accept & Install**.

> Če vas Windows Firewall pozove, dovolite AMD Sync dostop do omrežja, da lahko doseže Ryzen AI Halo prek SSH.

### Linux

Kliknite povezavo za prenos želene oblike:

| Format | Prenos | Ukaz za namestitev |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Opomba:** Ubuntu App Center lahko lokalno odprto datoteko `.deb` označi kot *"Potencialno nevarno."* To je standardno opozorilo za katerikoli lokalni namestitveni program tretje osebe. Če dvoklik na `.deb` ne uspe, uporabite zgornji ukaz v terminalu.

---

## Korak 3 — Povežite se s svojim Ryzen AI Halo

Ob prvem zagonu AMD Sync prikaže obrazec **Add a Remote Device**. Izpolnite ga z vrednostmi iz zavihka **Remote** v Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Polje | Opombe |
|-------|-------|
| **Device Name** *(neobvezno)* | Prijazna oznaka, na primer `Ryzen AI Halo`. Privzeto je `Device 1`, `Device 2`, … |
| **Hostname or IP** | Iz zavihka Remote |
| **SSH Port** | Iz zavihka Remote (samo številke) |
| **Username** | Ime vašega OS računa na Ryzen AI Halo |
| **Password** | Vaše geslo za prijavo v OS — med vnašanjem prikrito |

Kliknite **Add Device**. Po kratkem nalagalnem zaslonu boste videli **"Connection Successful"** in prišli na domači pogled, ki se nahaja v vaši sistemski vrstici (system tray). Kliknite izven okna, da ga zaprete; AMD Sync ostane zagnan in je oddaljen le en klik.

> **Če povezava ne uspe,** se AMD Sync vrne na obrazec z ohranjenimi vrednostmi. Običajni vzroki so izklopljen SSH na Ryzen AI Halo, napačno geslo ali dejstvo, da sta napravi v različnih omrežjih.

---

## Korak 4 — Zaženite svoje prvo oddaljeno orodje

Domači pogled ponuja pet komponent z enim klikom — vse so na voljo ne glede na to, kateri OS uporabljata odjemalec in Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponenta | Kaj počne |
|-----------|--------------|
| **Directory** | Izbere mapo na Ryzen AI Halo, v kateri se bodo odprli VS Code, Terminal in JupyterLab. Privzeto je upravljan delovni prostor `Documents/AMD_Sync`. |
| **VS Code** | Odpre VS Code lokalno s tunelom SSH v izbrano mapo. |
| **Terminal** | Odpre lokalni terminal, povezan prek SSH z Ryzen AI Halo, v izbrani mapi. |
| **JupyterLab** | Zažene projekt beležnice, povezan prek SSH z Ryzen AI Halo, omejen na izbrano mapo. |
| **Live Metrics** | Pogled v realnem času na izkoriščenost GPU, pomnilnika in CPU na Ryzen AI Halo. |

### Preizkusite VS Code

Za svoj prvi zagon preizkusite **VS Code**.

1. Pustite **Directory** na privzeti vrednosti `~/Documents/AMD_Sync`.
2. Kliknite **VS Code**.
3. AMD Sync ustvari `Documents/AMD_Sync/Project_1` na Ryzen AI Halo in lokalno odpre VS Code, tuneliran vanj.

Zdaj urejate datoteke, ki se nahajajo na Ryzen AI Halo, z lokalno nastavitvijo VS Code. Ustvarite `helloworld.py`, dodajte `print("hello world")`, odprite vgrajen terminal (`` Ctrl + ` ``) in ga zaženite:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Vrstica stanja prikazuje **SSH: Linux** — dokaz, da se vaša koda izvaja na Ryzen AI Halo, ne na vašem prenosniku.
### Preizkusite terminal

Kliknite **Terminal**, da se prek SSH prestavite v isto mapo, ne da bi zapustili tipkovnico.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

V sistemu Windows je privzeti terminal **PowerShell** – če želite, ga v meniju Nastavitve zamenjajte za **Windows Command Prompt**. V sistemu Linux AMD Sync uporablja privzeti sistemski terminal.

---

## Kako deluje mapa (Directory)

Spustni meni **Directory** je najpomembnejši element v aplikaciji AMD Sync – določa, kam bo pristalo vsako orodje, ki ga zaženete na napravi Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (privzeto)** – z zagonom VS Code ali JupyterLab iz te mape se samodejno ustvari nova projektna mapa (`Project_1`, `Project_2`, … za VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … za JupyterLab).
- **Obstoječe projektne mape** – v spustnem meniju se prikaže vsaka neposredna podmapa mape `AMD_Sync` (vključno z mapami, ki jih ročno ustvarite na napravi Ryzen AI Halo). Nazadnje uporabljena mapa postane privzeta ob naslednji uporabi.
- **Mape po meri** – vnesite katero koli absolutno pot za odpiranje mape drugje na napravi Ryzen AI Halo. AMD Sync jo le *odpre* – ne ustvarja map zunaj mape `AMD_Sync`, poti po meri pa se med sejami ne shranjujejo.

Če pot po meri ne deluje, vam AMD Sync pove, zakaj: neveljavna sintaksa, mapa ne obstaja ali pot kaže na datoteko.

---

## Metrike v živo in JupyterLab

- **Metrike v živo (Live Metrics)** – nadzorna plošča v živo za spremljanje uporabe GPU, pomnilnika in CPU. Najhitrejši način za potrditev, da oddaljeno učenje dejansko obremenjuje strojno opremo.
- **JupyterLab** – celoten projekt beležnice, povezan prek SSH z napravo Ryzen AI Halo, z lastnim vgrajenim terminalom za kombiniranje celic beležnice in ukazov lupine, ne da bi zapustili uporabniški vmesnik.

---

## Nastavitve in več naprav

Meni **Settings** ima tri zavihke:

| Zavihek | Kaj vsebuje |
|-----|----------------|
| **Devices** | Prikaže vse naprave Ryzen AI Halo, s katerimi ste se uspešno povezali. Omogoča ponovno povezavo, urejanje poverilnic ali dodajanje nove naprave. |
| **Information** | Povezave do dokumentacije in podpore na forumu. |
| **Customize** | Premikanje aplikacije po namizju, preklop vrste terminala (samo Windows) in preverjanje posodobitev za AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Vrsta terminala (Windows)** – izbirate lahko med **PowerShell** (privzeto) in **Windows Command Prompt**.
- **Vrsta terminala (Linux)** – na voljo je samo privzeti sistemski terminal.
- **Posodobitve aplikacije** – ta zavihek je pravo mesto za preverjanje in namestitev novih različic AMD Sync neposredno iz uporabniškega vmesnika; ločen posodabljalnik ni potreben.

> Naprava se v razdelku **Devices** pojavi šele po uspešni prvi povezavi, tako da neuspeli poskusi ne zamašijo seznama.

---

## Odpravljanje težav

- **Povezava takoj spodleti** – preverite, ali je na napravi Ryzen AI Halo v zavihku **Remote** v Developer Center omogočen strežnik SSH.
- **Napaka napačnega gesla** – uporabite svoje **prijavno geslo za operacijski sistem** na napravi Ryzen AI Halo, ne gesel iz Developer Center.
- **Gumb VS Code ne naredi ničesar** – namestite VS Code na svoj odjemalski računalnik s spletnega mesta [code.visualstudio.com](https://code.visualstudio.com).
- **Ikona AMD Sync v pladnju manjka (Linux/GNOME)** – namestite in omogočite razširitev AppIndicator.
- **Datoteka `.deb` se ne odpre iz upravitelja datotek** – uporabite `sudo apt install ./AMDSyncInstaller.deb` v terminalu.
- **Nastavitev se ponovno pojavi ob vsakem zagonu (Linux)**: odklenite svoj prijavni obroč ključev ali zaženite z `--password-store=gnome-libsecret`, nato pa še enkrat izvedite nastavitev.

---