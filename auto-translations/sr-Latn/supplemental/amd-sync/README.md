<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Udaljeni razvoj sa AMD Sync

## Pregled

**AMD Sync** pretvara vaš laptop u udaljenu komandnu stanicu za AMD Ryzen™ AI Halo. Preskočite ručno podešavanje SSH-a, ključeva i IDE-a — instalirajte AMD Sync i dobijte pristup udaljenom terminalu, VS Code, JupyterLab-u i živom GPU/CPU/memorijskom nadzornom panelu na Ryzen AI Halo jednim klikom.

Vaša lokalna mašina ostaje poznata; svaka komanda, sveska i model se izvršavaju na Ryzen AI Halo.

> **Savet**: Ova stranica će sadržati sve nove ispravke za AMDSync.

## Šta ćete naučiti

- Omogućiti SSH na Ryzen AI Halo i povezati se na njega putem AMD Sync
- Pokrenuti VS Code, Terminal, JupyterLab i Live Metrics na Ryzen AI Halo jednim klikom
- Organizovati udaljeni rad koristeći upravljane projektne fascikle AMD Sync-a

---

## Osnovni koncepti

AMD Sync ima dve strane: **klijent** (vaš laptop, koji pokreće AMD Sync aplikaciju) i **server** (Ryzen AI Halo, koji pokreće SSH server kroz koji AMD Sync uspostavlja tunel). Sve što pokrenete iz AMD Sync-a — VS Code, terminal, svesku — otvara se lokalno, ali se izvršava na Ryzen AI Halo.

> **Podržani klijenti:** Windows 11 i Linux. macOS nije podržan.

---

## Korak 1 — Omogućite SSH na Ryzen AI Halo


> **Napomena:** Na Windows-u, Ryzen AI Halo se isporučuje sa SSH serverom *isključenim po podrazumevanoj vrednosti*. Na Linux-u, dolazi sa SSH serverom *uključenim po podrazumevanoj vrednosti*.

1. Na Ryzen AI Halo, otvorite **AMD Ryzen™ AI Developer Center**.
2. Idite na karticu **Remote**.
3. Uključite **SSH Server**.
4. Zabeležite **IP adresu**, **Port** i **Korisničko ime** prikazane pod **Server Information** — nalepićete ih u AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Napomena:** Ovo je AMD Developer Center za Windows. Linux verzija može imati drugačiji korisnički interfejs, ali sličnu funkcionalnost za udaljeni pristup.

> **Savet:** AMD Sync traži **lozinku za prijavu na OS** tog korisnika, a ne lozinku iz Developer Center-a.

---

## Korak 2 — Instalirajte AMD Sync na vašem klijentu

AMD Sync radi na Windows 11 i Linux-u. Preuzmite instalacioni program za vaš OS, a zatim pratite korake u nastavku. Nakon instalacije, kliknite **Accept & Install** na ekranu **Get Started** — AMD Sync se automatski pokreće kada završi.

### Windows

[Preuzmite AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Dvaput kliknite na `AMDSyncInstaller.exe`.
2. Kliknite **Accept & Install**.

> Ako vas Windows Firewall upita, dozvolite AMD Sync mrežni pristup kako bi mogao da dosegne Ryzen AI Halo putem SSH-a.

### Linux

Kliknite na link da preuzmete željeni format:

| Format | Preuzimanje | Komanda za instalaciju |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Napomena:** Ubuntu App Center može označiti lokalno otvorenu `.deb` datoteku kao *"Potencijalno nesigurnu."* To je standardno upozorenje za svaki lokalni instalacioni program treće strane. Ako dvostruki klik na `.deb` ne uspe, koristite terminalsku komandu navedenu iznad.

---

## Korak 3 — Povežite se na vaš Ryzen AI Halo

Pri prvom pokretanju, AMD Sync prikazuje obrazac **Add a Remote Device**. Popunite ga koristeći vrednosti sa kartice **Remote** u Developer Center-u.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Polje | Napomene |
|-------|-------|
| **Device Name** *(opciono)* | Prijateljska oznaka poput `Ryzen AI Halo`. Podrazumevano je `Device 1`, `Device 2`, … |
| **Hostname or IP** | Sa kartice Remote |
| **SSH Port** | Sa kartice Remote (samo brojevi) |
| **Username** | Naziv vašeg OS naloga na Ryzen AI Halo |
| **Password** | Vaša lozinka za prijavu na OS — maskirana dok kucate |

Kliknite **Add Device**. Nakon kratkog ekrana učitavanja, videćete **"Connection Successful"** i naći se na početnom prikazu koji se nalazi u sistemskoj traci. Kliknite van prozora da ga zatvorite; AMD Sync ostaje pokrenut i dostupan jednim klikom.

> **Ako veza ne uspe,** AMD Sync se vraća na obrazac sa sačuvanim vrednostima. Uobičajeni uzroci su: SSH je onemogućen na Ryzen AI Halo, pogrešna lozinka, ili su dva uređaja na različitim mrežama.

---

## Korak 4 — Pokrenite vaš prvi udaljeni alat

Početni prikaz vam daje pet komponenti dostupnih jednim klikom — sve su dostupne bez obzira na to koji OS koriste klijent i Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponenta | Šta radi |
|-----------|--------------|
| **Directory** | Bira fasciklu na Ryzen AI Halo u kojoj će se VS Code, Terminal i JupyterLab otvoriti. Podrazumevano je upravljani radni prostor `Documents/AMD_Sync`. |
| **VS Code** | Otvara VS Code lokalno sa SSH tunelom u izabranu fasciklu. |
| **Terminal** | Otvara lokalni terminal SSH-povezan sa Ryzen AI Halo, u izabranoj fascikli. |
| **JupyterLab** | Pokreće projekat sveske SSH-povezan sa Ryzen AI Halo, ograničen na izabranu fasciklu. |
| **Live Metrics** | Prikaz u realnom vremenu korišćenja GPU, memorije i CPU na Ryzen AI Halo. |

### Isprobajte VS Code

Za vaše prvo pokretanje, isprobajte **VS Code**.

1. Ostavite **Directory** na podrazumevanom `~/Documents/AMD_Sync`.
2. Kliknite **VS Code**.
3. AMD Sync kreira `Documents/AMD_Sync/Project_1` na Ryzen AI Halo i otvara VS Code lokalno, sa tunelom u njega.

Sada uređujete datoteke koje se nalaze na Ryzen AI Halo koristeći vaše lokalno VS Code podešavanje. Kreirajte `helloworld.py`, dodajte `print("hello world")`, otvorite integrisani terminal (`` Ctrl + ` ``), i pokrenite ga:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Statusna traka prikazuje **SSH: Linux** — dokaz da se vaš kod izvršava na Ryzen AI Halo, a ne na vašem laptopu.

### Isprobajte Terminal

Kliknite **Terminal** da se spustite u istu fasciklu putem SSH-a bez napuštanja tastature.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Na Windows-u, podrazumevani terminal je **PowerShell** — prebacite se na **Windows Command Prompt** iz menija Podešavanja ako preferirate. Na Linux-u, AMD Sync koristi vaš podrazumevani sistemski terminal.

---

## Kako Directory funkcioniše

Padajući meni **Directory** je najvažnija kontrola u AMD Sync-u — on odlučuje gde svaki alat koji pokrenete završava na Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (podrazumevano)** — Pokretanje VS Code ili JupyterLab odavde automatski kreira novu projektnu fasciklu (`Project_1`, `Project_2`, … za VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … za JupyterLab).
- **Postojeće projektne fascikle** — Svako neposredno dete `AMD_Sync` (uključujući fascikle koje ručno kreirate na Ryzen AI Halo) pojavljuje se u padajućem meniju. Poslednja fascikla koju ste koristili postaje podrazumevana sledeći put.
- **Prilagođene putanje** — Unesite bilo koju apsolutnu putanju da otvorite fasciklu negde drugde na Ryzen AI Halo. AMD Sync je samo *otvara* — neće kreirati fascikle van `AMD_Sync`, a prilagođene putanje se ne čuvaju između sesija.

Ako prilagođena putanja ne radi, AMD Sync vam govori zašto: nevažeća sintaksa, fascikla ne postoji, ili putanja pokazuje na datoteku.

---

## Live Metrics i JupyterLab

- **Live Metrics** — Živi nadzorni panel korišćenja GPU, memorije i CPU. Najbrži način da potvrdite da udaljeno treniranje zaista koristi hardver.
- **JupyterLab** — Potpuni projekat sveske SSH-povezan sa Ryzen AI Halo, sa sopstvenim integrisanim terminalom za mešanje ćelija sveske i komandi ljuske bez napuštanja korisničkog interfejsa.

---

## Podešavanja i više uređaja

Meni **Settings** ima tri kartice:

| Kartica | Šta pokriva |
|-----|----------------|
| **Devices** | Navodi svaki Ryzen AI Halo na koji ste se uspešno povezali. Ponovo se povežite, uredite akreditive ili dodajte novi uređaj. |
| **Information** | Linkovi ka dokumentaciji i podršci na forumu. |
| **Customize** | Repozicionirajte aplikaciju na radnoj površini, promenite tip terminala (samo Windows) i proverite ispravke za AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Tip terminala (Windows)** — Birajte između **PowerShell** (podrazumevano) i **Windows Command Prompt**.
- **Tip terminala (Linux)** — Dostupan je samo podrazumevani sistemski terminal.
- **Ispravke aplikacije** — Ova kartica je pravo mesto za proveru i instalaciju novih verzija AMD Sync-a unutar korisničkog interfejsa; nije potreban poseban program za ažuriranje.

> Uređaj se pojavljuje pod **Devices** samo nakon uspešne prve veze, tako da neuspeli pokušaji neće zagušiti listu.

---

## Rešavanje problema

- **Veza odmah ne uspe** — Potvrdite da je SSH server omogućen na kartici **Remote** Ryzen AI Halo u Developer Center-u.
- **Greška pogrešne lozinke** — Koristite vašu **lozinku za prijavu na OS** na Ryzen AI Halo, a ne lozinke preuzete iz Developer Center-a.
- **Dugme VS Code ne radi ništa** — Instalirajte VS Code na vašoj klijentskoj mašini sa [code.visualstudio.com](https://code.visualstudio.com).
- **Ikona AMD Sync u traci nedostaje (Linux/GNOME)** — Instalirajte i omogućite AppIndicator ekstenziju.
- **`.deb` se ne otvara iz menadžera datoteka** — Koristite `sudo apt install ./AMDSyncInstaller.deb` iz terminala.

---