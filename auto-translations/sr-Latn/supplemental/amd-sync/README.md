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

# Daljinski razvoj pomoću AMD Sync

## Pregled

**AMD Sync** pretvara vaš laptop u daljinsku komandnu tablu za AMD Ryzen™ AI Halo. Preskočite ručno podešavanje SSH-a, ključeva i IDE-a — instalirajte AMD Sync i dobijte pristup jednim klikom do daljinskog terminala, VS Code-a, JupyterLab-a i uživo prikazanog GPU/CPU/memorijskog panela na Ryzen AI Halo uređaju.

Vaš lokalni računar ostaje poznat; svaka komanda, beležnica i model se izvršavaju na Ryzen AI Halo uređaju.

> **Savet**: Ova stranica će sadržati sva nova ažuriranja za AMDSync. 

## Šta ćete naučiti

- Kako da omogućite SSH na Ryzen AI Halo uređaju i povežete se sa njim iz AMD Sync-a
- Kako da pokrenete VS Code, Terminal, JupyterLab i Live Metrics za Ryzen AI Halo jednim klikom
- Kako da organizujete daljinski rad koristeći fascikle projekata kojima upravlja AMD Sync

---

## Osnovni koncepti

AMD Sync ima dve strane: **klijent** (vaš laptop, na kome radi AMD Sync aplikacija) i **server** (Ryzen AI Halo, na kome radi SSH server kroz koji AMD Sync tunelira). Sve što pokrenete iz AMD Sync-a — VS Code, terminal, beležnicu — otvara se lokalno, ali se izvršava na Ryzen AI Halo uređaju.

> **Podržani klijenti:** Windows 11 i Linux. macOS nije podržan.

---

## Korak 1 — Omogućite SSH na Ryzen AI Halo uređaju


> **Napomena:** Na Windows-u, Ryzen AI Halo se isporučuje sa SSH serverom *podrazumevano isključenim*. Na Linux-u, dolazi sa SSH serverom *podrazumevano uključenim*.

1. Na Ryzen AI Halo uređaju otvorite **AMD Ryzen™ AI Developer Center**.
2. Idite na karticu **Remote**.
3. Uključite **SSH Server**.
4. Zabeležite **IP Address**, **Port** i **Username** prikazane pod **Server Information** — ubaci ćete ih u AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Napomena:** Ovo je AMD Developer Center za Windows. Verzija za Linux može imati drugačiji izgled, ali sličnu funkcionalnost za daljinski pristup.

> **Savet:** AMD Sync traži **lozinku za prijavu na operativni sistem** tog korisnika, a ne lozinku iz Developer Center-a.

---

## Korak 2 — Instalirajte AMD Sync na svom klijentu

AMD Sync radi na Windows 11 i Linux-u. Preuzmite instalacioni program za svoj operativni sistem, a zatim pratite dole navedene korake. Nakon instalacije, kliknite na **Accept & Install** na ekranu **Get Started** — AMD Sync se automatski pokreće nakon završetka.

### Windows

[Preuzmite AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Dvaput kliknite na `AMDSyncInstaller.exe`.
2. Kliknite na **Accept & Install**.

> Ako se pojavi upozorenje Windows Firewall-a, dozvolite AMD Sync-u mrežni pristup kako bi mogao da dosegne Ryzen AI Halo preko SSH-a.

### Linux

Kliknite na link da preuzmete željeni format:

| Format | Preuzimanje | Komanda za instalaciju |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Napomena:** Ubuntu App Center može da označi lokalno otvoren `.deb` fajl kao *"Potentially unsafe."* To je standardno upozorenje za bilo koji instalacioni program trećih strana koji se pokreće lokalno. Ako dvoklik na `.deb` fajl ne uspe, koristite terminalsku komandu iznad.

---

## Korak 3 — Povežite se sa svojim Ryzen AI Halo uređajem

Prilikom prvog pokretanja, AMD Sync prikazuje formular **Add a Remote Device**. Popunite ga koristeći vrednosti sa kartice **Remote** u Developer Center-u.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Polje | Napomene |
|-------|-------|
| **Device Name** *(opciono)* | Prijateljski naziv poput `Ryzen AI Halo`. Podrazumevano je `Device 1`, `Device 2`, … |
| **Hostname or IP** | Sa kartice Remote |
| **SSH Port** | Sa kartice Remote (samo brojevi) |
| **Username** | Naziv vašeg naloga na operativnom sistemu na Ryzen AI Halo uređaju |
| **Password** | Vaša lozinka za prijavu na operativni sistem — maskirana dok kucate |

Kliknite na **Add Device**. Nakon kratkog ekrana učitavanja, videćete **"Connection Successful"** i naći ćete se na početnom prikazu, koji se nalazi u vašoj sistemskoj traci. Kliknite van prozora da ga zatvorite; AMD Sync ostaje pokrenut i dostupan je jednim klikom.

> **Ako veza ne uspe,** AMD Sync se vraća na formular sa sačuvanim vrednostima. Uobičajeni uzroci su onemogućen SSH na Ryzen AI Halo uređaju, pogrešna lozinka ili to što se dva uređaja nalaze na različitim mrežama.

---

## Korak 4 — Pokrenite svoj prvi daljinski alat

Početni prikaz vam pruža pet komponenata dostupnih jednim klikom — sve su dostupne bez obzira na to koji operativni sistem koriste klijent i Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponenta | Šta radi |
|-----------|--------------|
| **Directory** | Bira fasciklu na Ryzen AI Halo uređaju u kojoj će se otvoriti VS Code, Terminal i JupyterLab. Podrazumevano je radni prostor `Documents/AMD_Sync` kojim se upravlja. |
| **VS Code** | Otvara VS Code lokalno sa SSH tunelom ka izabranoj fascikli. |
| **Terminal** | Otvara lokalni terminal povezan preko SSH-a sa Ryzen AI Halo uređajem, u izabranoj fascikli. |
| **JupyterLab** | Pokreće projekat sa beležnicom povezan preko SSH-a sa Ryzen AI Halo uređajem, ograničen na izabranu fasciklu. |
| **Live Metrics** | Prikaz u realnom vremenu iskorišćenosti GPU-a, memorije i CPU-a na Ryzen AI Halo uređaju. |

### Isprobajte VS Code

Za svoje prvo pokretanje isprobajte **VS Code**.

1. Ostavite **Directory** na podrazumevanoj vrednosti `~/Documents/AMD_Sync`.
2. Kliknite na **VS Code**.
3. AMD Sync kreira `Documents/AMD_Sync/Project_1` na Ryzen AI Halo uređaju i otvara VS Code lokalno, tunelovan ka njemu.

Sada uređujete fajlove koji se nalaze na Ryzen AI Halo uređaju pomoću vašeg lokalnog VS Code podešavanja. Kreirajte `helloworld.py`, dodajte `print("hello world")`, otvorite ugrađeni terminal (`` Ctrl + ` ``) i pokrenite ga:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Statusna traka prikazuje **SSH: Linux** — dokaz da se vaš kod izvršava na Ryzen AI Halo uređaju, a ne na vašem laptopu.
### Isprobajte Terminal

Kliknite na **Terminal** da biste dospeli u istu fasciklu preko SSH-a bez napuštanja tastature.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Na Windows-u, podrazumevani terminal je **PowerShell** — prebacite se na **Windows Command Prompt** iz menija Settings ako to više volite. Na Linux-u, AMD Sync koristi vaš podrazumevani sistemski terminal.

---

## Kako funkcioniše Directory

Padajući meni **Directory** je najvažnija kontrola u AMD Sync-u — on određuje gde svaki alat koji pokrenete završava na Ryzen AI Halo uređaju.

- **`~/Documents/AMD_Sync` (podrazumevano)** — Pokretanje VS Code-a ili JupyterLab-a odavde automatski kreira novu projektnu fasciklu (`Project_1`, `Project_2`, … za VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … za JupyterLab).
- **Postojeće projektne fascikle** — Svaka neposredna podfascikla `AMD_Sync`-a (uključujući fascikle koje ručno kreirate na Ryzen AI Halo uređaju) prikazuje se u padajućem meniju. Poslednja fascikla koju ste koristili postaje podrazumevana sledeći put.
- **Prilagođene putanje** — Unesite bilo koju apsolutnu putanju da biste otvorili fasciklu negde drugde na Ryzen AI Halo uređaju. AMD Sync samo *otvara* je — neće kreirati fascikle van `AMD_Sync`-a, a prilagođene putanje se ne čuvaju između sesija.

Ako prilagođena putanja ne radi, AMD Sync vam saopštava zašto: neispravna sintaksa, fascikla ne postoji, ili putanja pokazuje na fajl.

---

## Live Metrics i JupyterLab

- **Live Metrics** — Kontrolna tabla uživo za korišćenje GPU-a, memorije i CPU-a. Najbrži način da potvrdite da udaljeni trening zaista opterećuje hardver.
- **JupyterLab** — Kompletan notebook projekat povezan preko SSH-a na Ryzen AI Halo uređaj, sa sopstvenim integrisanim terminalom za mešanje notebook ćelija i shell komandi bez napuštanja korisničkog interfejsa.

---

## Settings i više uređaja

Meni **Settings** ima tri kartice:

| Kartica | Šta pokriva |
|-----|----------------|
| **Devices** | Prikazuje sve Ryzen AI Halo uređaje na koje ste se uspešno povezali. Ponovo se povežite, izmenite akreditive ili dodajte novi uređaj. |
| **Information** | Linkovi ka dokumentaciji i podršci na forumu. |
| **Customize** | Premestite aplikaciju na radnoj površini, promenite tip terminala (samo Windows) i proverite da li postoje AMD Sync ažuriranja. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Tip terminala (Windows)** — Izaberite između **PowerShell** (podrazumevano) i **Windows Command Prompt**.
- **Tip terminala (Linux)** — Dostupan je samo podrazumevani sistemski terminal.
- **Ažuriranja aplikacije** — Ova kartica je pravo mesto da proverite i instalirate nove verzije AMD Sync-a direktno iz korisničkog interfejsa; nije potreban poseban alat za ažuriranje.

> Uređaj se pojavljuje pod **Devices** tek nakon uspešnog prvog povezivanja, tako da neuspeli pokušaji neće zatrpavati listu.

---

## Rešavanje problema

- **Povezivanje odmah ne uspeva** — Potvrdite da je SSH server omogućen na kartici **Remote** u Developer Center-u na Ryzen AI Halo uređaju.
- **Greška pogrešne lozinke** — Koristite vašu **lozinku za prijavu na OS** na Ryzen AI Halo uređaju, a ne lozinke preuzete iz Developer Center-a.
- **Dugme VS Code ne radi ništa** — Instalirajte VS Code na vašem klijentskom računaru sa [code.visualstudio.com](https://code.visualstudio.com).
- **Ikona AMD Sync u traci nedostaje (Linux/GNOME)** — Instalirajte i omogućite ekstenziju AppIndicator.
- **`.deb` fajl se ne otvara iz upravljača fajlovima** — Koristite `sudo apt install ./AMDSyncInstaller.deb` iz terminala.

---