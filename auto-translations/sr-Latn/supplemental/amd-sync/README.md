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

# Udaljeni razvoj sa AMD Sync

## Pregled

**AMD Sync** pretvara vaš laptop u udaljenu komandnu tablu za AMD Ryzen™ AI Halo. Preskočite ručno podešavanje SSH-a, ključeva i IDE-a — instalirajte AMD Sync i dobijte pristup jednim klikom udaljenom terminalu, VS Code-u, JupyterLab-u i prikazu uživo GPU/CPU/memorije na Ryzen AI Halo uređaju.

Vaš lokalni računar ostaje poznat; svaka komanda, beležnica i model se izvršavaju na Ryzen AI Halo uređaju.

> **Savet**: Ova stranica će sadržati sve nove izmene za AMDSync. 

## Šta ćete naučiti

- Omogućiti SSH na Ryzen AI Halo uređaju i povezati se sa njim iz AMD Sync-a
- Pokrenuti VS Code, Terminal, JupyterLab i Live Metrics prema Ryzen AI Halo uređaju jednim klikom
- Organizovati udaljeni rad koristeći fascikle projekata kojima upravlja AMD Sync

---

## Osnovni koncepti

AMD Sync ima dve strane: **klijenta** (vaš laptop, na kom se izvršava AMD Sync aplikacija) i **server** (Ryzen AI Halo uređaj, na kom se izvršava SSH server u koji se AMD Sync tunelira). Sve što pokrenete iz AMD Sync-a — VS Code, terminal, beležnicu — otvara se lokalno, ali se izvršava na Ryzen AI Halo uređaju.

> **Podržani klijenti:** Windows 11 i Linux. macOS nije podržan.

---

## Korak 1 — Omogućavanje SSH-a na Ryzen AI Halo uređaju


> **Napomena:** Na Windows sistemu, Ryzen AI Halo uređaj dolazi sa SSH serverom *podrazumevano isključenim*. Na Linux sistemu, dolazi sa SSH serverom *podrazumevano uključenim*.

1. Na Ryzen AI Halo uređaju, otvorite **AMD Ryzen™ AI Developer Center**.
2. Idite na karticu **Remote**.
3. Uključite **SSH Server**.
4. Zabeležite **IP Address**, **Port** i **Username** prikazane pod **Server Information** — nalepićete ih u AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Napomena:** Ovo je AMD Developer Center za Windows. Linux verzija može imati drugačiji izgled interfejsa, ali sličnu udaljenu funkcionalnost.

> **Savet:** AMD Sync traži **lozinku za prijavu u operativni sistem** tog korisnika, a ne lozinku iz Developer Center-a.

---

## Korak 2 — Instaliranje AMD Sync-a na vašem klijentu

AMD Sync radi na Windows 11 i Linux sistemima. Preuzmite instalater za vaš operativni sistem, a zatim pratite korake ispod. Nakon instalacije, kliknite na **Accept & Install** na ekranu **Get Started** — AMD Sync se automatski pokreće kada se instalacija završi.

### Windows

[Preuzmite AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Dvaput kliknite na `AMDSyncInstaller.exe`.
2. Kliknite na **Accept & Install**.

> Ako se Windows Firewall oglasi, dozvolite AMD Sync-u pristup mreži kako bi mogao da se poveže sa Ryzen AI Halo uređajem preko SSH-a.

### Linux

Kliknite na link da preuzmete željeni format:

| Format | Preuzimanje | Komanda za instalaciju |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Napomena:** Ubuntu App Center može označiti lokalno otvoren `.deb` fajl kao *"Potencijalno nebezbedan."* To je standardno upozorenje za bilo koji lokalni instalater trećih strana. Ako dvaput kliknuti na `.deb` fajl ne uspe, koristite komandu terminala navedenu iznad.

---

## Korak 3 — Povezivanje sa vašim Ryzen AI Halo uređajem

Prilikom prvog pokretanja, AMD Sync prikazuje formular **Add a Remote Device**. Popunite ga koristeći vrednosti sa kartice **Remote** u Developer Center-u.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Polje | Napomene |
|-------|-------|
| **Device Name** *(opcionalno)* | Prijateljska oznaka poput `Ryzen AI Halo`. Podrazumevano je `Device 1`, `Device 2`, … |
| **Hostname or IP** | Sa kartice Remote |
| **SSH Port** | Sa kartice Remote (samo brojevi) |
| **Username** | Naziv vašeg korisničkog naloga u operativnom sistemu na Ryzen AI Halo uređaju |
| **Password** | Vaša lozinka za prijavu u operativni sistem — maskirana dok kucate |

Kliknite na **Add Device**. Nakon kratkog ekrana učitavanja, videćete poruku **"Connection Successful"** i doći ćete do početnog prikaza, koji se nalazi u sistemskoj traci. Kliknite van prozora da ga zatvorite; AMD Sync ostaje pokrenut i udaljen je jedan klik.

> **Ako povezivanje ne uspe,** AMD Sync se vraća na formular sa sačuvanim vrednostima. Uobičajeni uzroci su onemogućen SSH na Ryzen AI Halo uređaju, pogrešna lozinka ili to što su oba uređaja na različitim mrežama.

---

## Korak 4 — Pokretanje prvog udaljenog alata

Početni prikaz vam daje pet komponenti dostupnih jednim klikom — sve dostupne bez obzira na to koji operativni sistem koriste klijent i Ryzen AI Halo uređaj.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponenta | Šta radi |
|-----------|--------------|
| **Directory** | Bira fasciklu na Ryzen AI Halo uređaju u kojoj će se otvoriti VS Code, Terminal i JupyterLab. Podrazumevano se koristi upravljani radni prostor `Documents/AMD_Sync`. |
| **VS Code** | Otvara VS Code lokalno sa SSH tunelom u izabranu fasciklu. |
| **Terminal** | Otvara lokalni terminal povezan preko SSH-a sa Ryzen AI Halo uređajem, u izabranoj fascikli. |
| **JupyterLab** | Pokreće projekat beležnice povezan preko SSH-a sa Ryzen AI Halo uređajem, ograničen na izabranu fasciklu. |
| **Live Metrics** | Prikaz u realnom vremenu iskorišćenosti GPU-a, memorije i CPU-a na Ryzen AI Halo uređaju. |

### Isprobajte VS Code

Za vaše prvo pokretanje, isprobajte **VS Code**.

1. Ostavite **Directory** na podrazumevanoj vrednosti `~/Documents/AMD_Sync`.
2. Kliknite na **VS Code**.
3. AMD Sync kreira `Documents/AMD_Sync/Project_1` na Ryzen AI Halo uređaju i otvara VS Code lokalno, tunelovan u nju.

Sada uređujete fajlove koji se nalaze na Ryzen AI Halo uređaju koristeći vaš lokalni VS Code. Kreirajte `helloworld.py`, dodajte `print("hello world")`, otvorite integrisani terminal (`` Ctrl + ` ``), i pokrenite ga:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Statusna traka prikazuje **SSH: Linux** — dokaz da se vaš kod izvršava na Ryzen AI Halo uređaju, a ne na vašem laptopu.
### Isprobajte terminal

Kliknite na **Terminal** da biste se preko SSH-a prebacili u istu fasciklu bez napuštanja tastature.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Na Windows sistemu, podrazumevani terminal je **PowerShell** — prebacite se na **Windows Command Prompt** iz menija Settings ako to više volite. Na Linux sistemu, AMD Sync koristi vaš podrazumevani sistemski terminal.

---

## Kako funkcioniše Directory

Padajući meni **Directory** je najvažnija kontrola u AMD Sync-u — on određuje gde svaki alat koji pokrenete završava na Ryzen AI Halo uređaju.

- **`~/Documents/AMD_Sync` (podrazumevano)** — Pokretanjem VS Code ili JupyterLab iz ove fascikle automatski se kreira nova projektna fascikla (`Project_1`, `Project_2`, … za VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … za JupyterLab).
- **Postojeće projektne fascikle** — Svaka direktna podfascikla unutar `AMD_Sync` (uključujući fascikle koje ručno kreirate na Ryzen AI Halo uređaju) pojavljuje se u padajućem meniju. Poslednja fascikla koju ste koristili postaje podrazumevana sledeći put.
- **Prilagođene putanje** — Unesite bilo koju apsolutnu putanju da biste otvorili fasciklu negde drugde na Ryzen AI Halo uređaju. AMD Sync je samo *otvara* — neće kreirati fascikle van `AMD_Sync`, a prilagođene putanje se ne čuvaju između sesija.

Ako prilagođena putanja ne radi, AMD Sync vam govori zašto: nevažeća sintaksa, fascikla ne postoji ili putanja ukazuje na fajl.

---

## Live Metrics i JupyterLab

- **Live Metrics** — Kontrolna tabla uživo za praćenje iskorišćenosti GPU-a, memorije i CPU-a. Najbrži način da potvrdite da udaljeni trening zaista koristi hardver.
- **JupyterLab** — Kompletan notebook projekat povezan preko SSH-a sa Ryzen AI Halo uređajem, sa sopstvenim integrisanim terminalom za kombinovanje notebook ćelija i komandi ljuske bez napuštanja korisničkog interfejsa.

---

## Settings i više uređaja

Meni **Settings** ima tri kartice:

| Kartica | Šta obuhvata |
|-----|----------------|
| **Devices** | Prikazuje svaki Ryzen AI Halo uređaj sa kojim ste se uspešno povezali. Ponovo se povežite, izmenite kredencijale ili dodajte novi uređaj. |
| **Information** | Linkovi ka dokumentaciji i podršci na forumu. |
| **Customize** | Premestite aplikaciju na desktopu, promenite tip terminala (samo na Windows sistemu) i proverite da li postoje nove verzije AMD Sync-a. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Tip terminala (Windows)** — Birajte između **PowerShell** (podrazumevano) i **Windows Command Prompt**.
- **Tip terminala (Linux)** — Dostupan je samo podrazumevani sistemski terminal.
- **Ažuriranja aplikacije** — Ova kartica je pravo mesto za proveru i instalaciju novih verzija AMD Sync-a direktno iz korisničkog interfejsa; nije potreban poseban alat za ažuriranje.

> Uređaj se pojavljuje pod **Devices** tek nakon uspešnog prvog povezivanja, tako da neuspeli pokušaji neće zatrpavati listu.

---

## Rešavanje problema

- **Povezivanje odmah ne uspeva** — Proverite da li je SSH server omogućen na kartici **Remote** u Developer Center-u na Ryzen AI Halo uređaju.
- **Greška pogrešne lozinke** — Koristite svoju **lozinku za prijavljivanje na OS** na Ryzen AI Halo uređaju, a ne lozinke preuzete iz Developer Center-a.
- **Dugme VS Code ne radi** — Instalirajte VS Code na vašem klijentskom računaru sa [code.visualstudio.com](https://code.visualstudio.com).
- **Ikonica AMD Sync u traci sistema nedostaje (Linux/GNOME)** — Instalirajte i omogućite ekstenziju AppIndicator.
- **Fajl `.deb` se ne otvara iz upravljača fajlovima** — Koristite `sudo apt install ./AMDSyncInstaller.deb` u terminalu.
- **Podešavanje se ponovo pojavljuje pri svakom pokretanju (Linux)**: otključajte svoj login keyring ili pokrenite sa `--password-store=gnome-libsecret`, pa ponovite podešavanje još jednom.

---