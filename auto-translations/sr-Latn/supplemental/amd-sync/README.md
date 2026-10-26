<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Mašinski prevod.** Ova stranica je automatski prevedena sa engleskog jezika i nije proveravana od strane čoveka. Može sadržati greške, a određena uputstva, komande, preuzimanja, dostupnost proizvoda ili drugi sadržaj mogu se razlikovati u zavisnosti od jezika ili regiona. U slučaju bilo kakve nedoslednosti ili neslaganja, merodavna je originalna verzija playbook-a na engleskom jeziku.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Udaljeni razvoj pomoću AMD Sync

## Pregled

**AMD Sync** pretvara vaš laptop u udaljenu komandnu kabinu za AMD Ryzen™ AI Halo. Zaobiđite ručno podešavanje SSH-a, ključeva i IDE-a — instalirajte AMD Sync i dobijte pristup udaljenom terminalu, VS Code-u, JupyterLab-u i uživo prikazanoj GPU/CPU/memorijskoj komandnoj tabli na Ryzen AI Halo uz jedan klik.

Vaš lokalni računar ostaje poznat; svaka komanda, beležnica i model se izvršavaju na Ryzen AI Halo.

> **Savet**: Ova stranica će sadržati sva nova ažuriranja za AMDSync. 

## Šta ćete naučiti

- Omogućiti SSH na Ryzen AI Halo i povezati se sa njim iz AMD Sync
- Pokrenuti VS Code, Terminal, JupyterLab i Live Metrics na Ryzen AI Halo jednim klikom
- Organizovati udaljeni rad koristeći fascikle projekata kojima upravlja AMD Sync

---

## Osnovni koncepti

AMD Sync ima dve strane: **klijenta** (vaš laptop, na kom se izvršava aplikacija AMD Sync) i **server** (Ryzen AI Halo, na kom se izvršava SSH server kroz koji se AMD Sync tunelira). Sve što pokrenete iz AMD Sync — VS Code, terminal, beležnicu — otvara se lokalno, ali se izvršava na Ryzen AI Halo.

> **Podržani klijenti:** Windows 11 i Linux. macOS nije podržan.

---

## Korak 1 — Omogućite SSH na Ryzen AI Halo


> **Napomena:** Na Windows-u, Ryzen AI Halo dolazi sa SSH serverom *podrazumevano isključenim*. Na Linux-u, dolazi sa SSH serverom *podrazumevano uključenim*.

1. Na Ryzen AI Halo, otvorite **AMD Ryzen™ AI Developer Center**.
2. Idite na karticu **Remote**.
3. Uključite **SSH Server**.
4. Zabeležite **IP Address**, **Port** i **Username** prikazane pod **Server Information** — unećete ih u AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Napomena:** Ovo je AMD Developer Center za Windows. Linux verzija može imati drugačiji korisnički interfejs, ali sličnu funkcionalnost za udaljeni rad.

> **Savet:** AMD Sync traži **lozinku za prijavu na operativni sistem** tog korisnika, a ne lozinku iz Developer Center-a.

---

## Korak 2 — Instalirajte AMD Sync na svom klijentu

AMD Sync radi na Windows 11 i Linux-u. Preuzmite instalacioni program za svoj operativni sistem, a zatim pratite korake ispod. Nakon instalacije, kliknite **Accept & Install** na ekranu **Get Started** — AMD Sync se automatski pokreće kada se instalacija završi.

### Windows

[Preuzmite AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Dvaput kliknite na `AMDSyncInstaller.exe`.
2. Kliknite **Accept & Install**.

> Ako vas Windows Firewall upita, dozvolite AMD Sync pristup mreži kako bi mogao da dosegne Ryzen AI Halo preko SSH-a.

### Linux

Kliknite na link da preuzmete željeni format:

| Format | Preuzimanje | Komanda za instalaciju |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Napomena:** Ubuntu App Center može označiti lokalno otvoren `.deb` kao *"Potencijalno nebezbedan."* To je standardno upozorenje za bilo koji lokalni instalacioni program trećih strana. Ako dvoklik na `.deb` ne uspe, koristite gorenavedenu komandu u terminalu.

---

## Korak 3 — Povežite se sa svojim Ryzen AI Halo

Prilikom prvog pokretanja, AMD Sync prikazuje formular **Add a Remote Device**. Popunite ga koristeći vrednosti sa kartice **Remote** u Developer Center-u.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Polje | Napomene |
|-------|-------|
| **Device Name** *(opciono)* | Prijateljska oznaka poput `Ryzen AI Halo`. Podrazumevano je `Device 1`, `Device 2`, … |
| **Hostname or IP** | Sa kartice Remote |
| **SSH Port** | Sa kartice Remote (samo brojevi) |
| **Username** | Ime vašeg naloga operativnog sistema na Ryzen AI Halo |
| **Password** | Vaša lozinka za prijavu na operativni sistem — maskirana dok je kucate |

Kliknite **Add Device**. Nakon kratkog ekrana učitavanja, videćete **"Connection Successful"** i stići ćete na početni prikaz, koji se nalazi u vašoj traci sistema. Kliknite van prozora da ga zatvorite; AMD Sync nastavlja da radi i udaljen je jedan klik.

> **Ako veza ne uspe,** AMD Sync se vraća na formular sa sačuvanim vrednostima. Uobičajeni uzroci su isključen SSH na Ryzen AI Halo, pogrešna lozinka ili to što su oba uređaja na različitim mrežama.

---

## Korak 4 — Pokrenite svoj prvi udaljeni alat

Početni prikaz vam pruža pet komponenti koje se pokreću jednim klikom — sve dostupne bez obzira na to koji operativni sistem koriste klijent i Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponenta | Šta radi |
|-----------|--------------|
| **Directory** | Bira fasciklu na Ryzen AI Halo u kojoj će se otvoriti VS Code, Terminal i JupyterLab. Podrazumevano je radni prostor `Documents/AMD_Sync` kojim se upravlja. |
| **VS Code** | Otvara VS Code lokalno sa SSH tunelom ka izabranoj fascikli. |
| **Terminal** | Otvara lokalni terminal povezan preko SSH-a sa Ryzen AI Halo, u izabranoj fascikli. |
| **JupyterLab** | Pokreće projekat beležnice povezan preko SSH-a sa Ryzen AI Halo, ograničen na izabranu fasciklu. |
| **Live Metrics** | Prikaz u realnom vremenu iskorišćenosti GPU-a, memorije i CPU-a na Ryzen AI Halo. |

### Isprobajte VS Code

Za prvo pokretanje, isprobajte **VS Code**. Sledeća uputstva su za Linux, ali je iskustvo na Windows-u slično.

1. Ostavite **Directory** na podrazumevanom `~/Documents/AMD_Sync`.
2. Kliknite **VS Code**.
3. AMD Sync kreira `Documents/AMD_Sync/Project_1` na Ryzen AI Halo i otvara VS Code lokalno, tuneliran ka njemu.

Sada uređujete fajlove koji se nalaze na Ryzen AI Halo koristeći svoje lokalno podešavanje VS Code-a. Kreirajte `helloworld.py`, dodajte `print("hello world")`, otvorite integrisani terminal (`` Ctrl + ` ``) i pokrenite ga:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Statusna traka prikazuje **SSH: Linux** — dokaz da se vaš kôd izvršava na Ryzen AI Halo, a ne na vašem laptopu.
### Probajte terminal

Kliknite na **Terminal** da biste se ubacili u istu fasciklu preko SSH-a, bez napuštanja tastature.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Na Windows sistemu, podrazumevani terminal je **PowerShell** — prebacite se na **Windows Command Prompt** iz menija Settings ako to želite. Na Linux sistemu, AMD Sync koristi vaš podrazumevani sistemski terminal.

---

## Kako funkcioniše direktorijum

Padajući meni **Directory** je pojedinačno najvažnija kontrola u AMD Sync-u — on određuje gde svaki alat koji pokrenete završava na Ryzen AI Halo uređaju.

- **`~/Documents/AMD_Sync` (podrazumevano)** — Pokretanje VS Code ili JupyterLab odavde automatski kreira novu fasciklu projekta (`Project_1`, `Project_2`, … za VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … za JupyterLab).
- **Postojeće fascikle projekata** — Svaka neposredna podfascikla unutar `AMD_Sync` (uključujući fascikle koje ručno kreirate na Ryzen AI Halo uređaju) pojavljuje se u padajućem meniju. Poslednja fascikla koju ste koristili postaje podrazumevana sledeći put.
- **Prilagođene putanje** — Unesite bilo koju apsolutnu putanju da biste otvorili fasciklu negde drugde na Ryzen AI Halo uređaju. AMD Sync je samo *otvara* — neće kreirati fascikle van `AMD_Sync`, a prilagođene putanje se ne čuvaju između sesija.

Ako prilagođena putanja ne radi, AMD Sync vam kaže zašto: nevažeća sintaksa, fascikla ne postoji, ili putanja pokazuje na fajl.

---

## Live Metrics i JupyterLab

- **Live Metrics** — Dinamička kontrolna tabla korišćenja GPU-a, memorije i CPU-a. Najbrži način da potvrdite da udaljeno treniranje zaista opterećuje hardver.
- **JupyterLab** — Pun projekat beležnice povezan preko SSH-a sa Ryzen AI Halo uređajem, sa sopstvenim integrisanim terminalom za mešanje ćelija beležnice i komandi ljuske bez napuštanja korisničkog interfejsa.

---

## Settings i više uređaja

Meni **Settings** ima tri kartice:

| Kartica | Šta pokriva |
|-----|----------------|
| **Devices** | Prikazuje svaki Ryzen AI Halo uređaj sa kojim ste se uspešno povezali. Ponovo se povežite, izmenite akreditive, ili dodajte novi uređaj. |
| **Information** | Linkovi ka dokumentaciji i podršci na forumu. |
| **Customize** | Premestite aplikaciju na radnoj površini, promenite tip terminala (samo Windows), i proverite da li postoje ažuriranja za AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Tip terminala (Windows)** — Birajte između **PowerShell** (podrazumevano) i **Windows Command Prompt**.
- **Tip terminala (Linux)** — Dostupan je samo podrazumevani sistemski terminal.
- **Ažuriranja aplikacije** — Ova kartica je pravo mesto za proveru i instalaciju novih verzija AMD Sync-a iz samog korisničkog interfejsa; nije potreban poseban program za ažuriranje.

> Uređaj se pojavljuje pod **Devices** tek nakon uspešnog prvog povezivanja, tako da neuspeli pokušaji neće zatrpavati listu.

---

## Rešavanje problema

- **Povezivanje odmah ne uspeva** — Potvrdite da je SSH server omogućen na kartici **Remote** u Developer Center-u na Ryzen AI Halo uređaju.
- **Greška pogrešne lozinke** — Koristite svoju **lozinku za prijavu na OS** na Ryzen AI Halo uređaju, a ne lozinke preuzete iz Developer Center-a.
- **Dugme VS Code ne radi** — Instalirajte VS Code na svom klijentskom računaru sa [code.visualstudio.com](https://code.visualstudio.com).
- **Ikona AMD Sync u sistemskoj kaseti nedostaje (Linux/GNOME)** — Instalirajte i omogućite ekstenziju AppIndicator.
- **`.deb` se ne otvara iz menadžera fajlova** — Koristite `sudo apt install ./AMDSyncInstaller.deb` iz terminala.
- **Podešavanje se ponovo pojavljuje pri svakom pokretanju (Linux)**: otključajte svoj keyring za prijavu, ili pokrenite sa `--password-store=gnome-libsecret`, zatim ponovo obavite podešavanje jednom.