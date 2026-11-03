<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducere automată.** Această pagină a fost tradusă automat din limba engleză și nu a fost revizuită de o persoană. Aceasta poate conține erori, iar anumite instrucțiuni, comenzi, descărcări, disponibilitatea produselor sau alt conținut pot varia în funcție de limbă sau regiune. În cazul oricărei neconcordanțe sau discrepanțe, versiunea originală în limba engleză a playbook-ului prevalează.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Dezvoltare la distanță cu AMD Sync

## Prezentare generală

**AMD Sync** transformă laptopul dvs. într-un cockpit la distanță pentru AMD Ryzen™ AI Halo. Săriți peste configurarea manuală SSH, chei și IDE — instalați AMD Sync și obțineți acces cu un singur clic la un terminal la distanță, VS Code, JupyterLab și un dashboard live pentru GPU/CPU/memorie pe Ryzen AI Halo.

Mașina dvs. locală rămâne familiară; fiecare comandă, notebook și model rulează pe Ryzen AI Halo.

> **Sfat**: Această pagină va conține orice actualizare nouă pentru AMDSync.

## Ce veți învăța

- Activarea SSH pe Ryzen AI Halo și conectarea la acesta din AMD Sync
- Lansarea VS Code, Terminal, JupyterLab și Live Metrics pentru Ryzen AI Halo cu un singur clic
- Organizarea muncii la distanță folosind folderele de proiect gestionate de AMD Sync

---

## Concepte de bază

AMD Sync are două părți: un **client** (laptopul dvs., pe care rulează aplicația AMD Sync) și un **server** (Ryzen AI Halo, pe care rulează un server SSH prin care AMD Sync creează un tunel). Tot ce lansați din AMD Sync — VS Code, un terminal, un notebook — se deschide local, dar se execută pe Ryzen AI Halo.

> **Clienți acceptați:** Windows 11 și Linux. macOS nu este acceptat.

---

## Pasul 1 — Activați SSH pe Ryzen AI Halo


> **Notă:** Pe Windows, Ryzen AI Halo este livrat cu serverul SSH *dezactivat implicit*. Pe Linux, vine cu serverul SSH *activat implicit*.

1. Pe Ryzen AI Halo, deschideți **AMD Ryzen™ AI Developer Center**.
2. Accesați fila **Remote**.
3. Comutați **SSH Server** pe activat.
4. Notați **IP Address**, **Port** și **Username** afișate sub **Server Information** — le veți lipi în AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Notă:** Acesta este AMD Developer Center pentru Windows. Cel pentru Linux poate avea o interfață diferită, dar o funcționalitate la distanță similară.

> **Sfat:** AMD Sync solicită **parola de conectare a sistemului de operare** a utilizatorului respectiv, nu o parolă din Developer Center.

---

## Pasul 2 — Instalați AMD Sync pe clientul dvs.

AMD Sync rulează pe Windows 11 și Linux. Descărcați programul de instalare pentru sistemul dvs. de operare, apoi urmați pașii de mai jos. După instalare, faceți clic pe **Accept & Install** pe ecranul **Get Started** — AMD Sync se lansează automat la finalizare.

### Windows

[Descărcați AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Faceți dublu clic pe `AMDSyncInstaller.exe`.
2. Faceți clic pe **Accept & Install**.

> Dacă Windows Firewall vă solicită, permiteți accesul la rețea pentru AMD Sync, astfel încât să poată ajunge la Ryzen AI Halo prin SSH.

### Linux

Faceți clic pe link pentru a descărca formatul preferat:

| Format | Descărcare | Comandă de instalare |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Notă:** Ubuntu App Center poate semnala un fișier `.deb` deschis local ca fiind *„Potențial nesigur."* Acesta este avertismentul standard pentru orice program de instalare local de la terți. Dacă dublu-clic pe `.deb` eșuează, folosiți comanda din terminal de mai sus.

---

## Pasul 3 — Conectați-vă la Ryzen AI Halo

La prima lansare, AMD Sync afișează formularul **Add a Remote Device**. Completați-l folosind valorile din fila **Remote** a Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Câmp | Note |
|-------|-------|
| **Device Name** *(opțional)* | O etichetă prietenoasă precum `Ryzen AI Halo`. Implicit este `Device 1`, `Device 2`, … |
| **Hostname or IP** | Din fila Remote |
| **SSH Port** | Din fila Remote (doar numere) |
| **Username** | Numele contului dvs. de sistem de operare pe Ryzen AI Halo |
| **Password** | Parola dvs. de conectare la sistemul de operare — mascată pe măsură ce tastați |

Faceți clic pe **Add Device**. După un scurt ecran de încărcare, veți vedea **„Connection Successful"** și veți ajunge pe ecranul principal, care se află în bara de sistem (system tray). Faceți clic în afara ferestrei pentru a o închide; AMD Sync rămâne pornit și este la un clic distanță.

> **Dacă conexiunea eșuează,** AMD Sync revine la formular cu valorile dvs. păstrate. Cauzele obișnuite sunt dezactivarea SSH pe Ryzen AI Halo, parola greșită sau faptul că cele două dispozitive se află în rețele diferite.

---

## Pasul 4 — Lansați primul dvs. instrument la distanță

Ecranul principal vă oferă cinci componente cu un singur clic — toate disponibile indiferent de sistemul de operare pe care rulează clientul și Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Componentă | Ce face |
|-----------|--------------|
| **Directory** | Alege folderul de pe Ryzen AI Halo în care se vor deschide VS Code, Terminal și JupyterLab. Implicit este un spațiu de lucru gestionat `Documents/AMD_Sync`. |
| **VS Code** | Deschide VS Code local cu un tunel SSH către folderul selectat. |
| **Terminal** | Deschide un terminal local conectat prin SSH la Ryzen AI Halo, în folderul selectat. |
| **JupyterLab** | Lansează un proiect notebook conectat prin SSH la Ryzen AI Halo, limitat la folderul selectat. |
| **Live Metrics** | Vizualizare în timp real a utilizării GPU, memorie și CPU pe Ryzen AI Halo. |

### Încercați VS Code

Pentru prima lansare, încercați **VS Code**.

1. Lăsați **Directory** la valoarea implicită `~/Documents/AMD_Sync`.
2. Faceți clic pe **VS Code**.
3. AMD Sync creează `Documents/AMD_Sync/Project_1` pe Ryzen AI Halo și deschide VS Code local, printr-un tunel către acesta.

Acum editați fișiere care se află pe Ryzen AI Halo folosind configurația dvs. locală de VS Code. Creați `helloworld.py`, adăugați `print("hello world")`, deschideți terminalul integrat (`` Ctrl + ` ``) și rulați-l:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Bara de stare afișează **SSH: Linux** — dovada că  codul dvs. rulează pe Ryzen AI Halo, nu pe laptopul dvs.
### Încearcă Terminalul

Fă clic pe **Terminal** pentru a intra în același folder prin SSH fără a părăsi tastatura.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Pe Windows, terminalul implicit este **PowerShell** — comută la **Windows Command Prompt** din meniul Settings dacă preferi. Pe Linux, AMD Sync folosește terminalul implicit al sistemului tău.

---

## Cum funcționează Directorul

Meniul derulant **Directory** este cel mai important control din AMD Sync — acesta decide unde ajunge fiecare instrument pe care îl lansezi pe Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (implicit)** — Lansarea VS Code sau JupyterLab din acest loc creează automat un folder de proiect nou (`Project_1`, `Project_2`, … pentru VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … pentru JupyterLab).
- **Foldere de proiect existente** — Orice folder copil direct al `AMD_Sync` (inclusiv foldere create manual pe Ryzen AI Halo) apare în meniul derulant. Ultimul folder folosit devine cel implicit data următoare.
- **Căi personalizate** — Introdu orice cale absolută pentru a deschide un folder aflat în altă parte pe Ryzen AI Halo. AMD Sync doar *deschide* folderul — nu va crea foldere în afara `AMD_Sync`, iar căile personalizate nu sunt salvate între sesiuni.

Dacă o cale personalizată nu funcționează, AMD Sync îți spune de ce: sintaxă invalidă, folderul nu există sau calea indică spre un fișier.

---

## Metrici în timp real și JupyterLab

- **Live Metrics** — Un tablou de bord în timp real al utilizării GPU, memoriei și CPU. Cel mai rapid mod de a confirma că o rulare de antrenare la distanță chiar folosește hardware-ul.
- **JupyterLab** — Un proiect notebook complet, conectat prin SSH la Ryzen AI Halo, cu propriul terminal integrat pentru a combina celulele notebook și comenzile shell fără a părăsi interfața.

---

## Setări și dispozitive multiple

Meniul **Settings** are trei file:

| Filă | Ce include |
|-----|----------------|
| **Devices** | Listează fiecare Ryzen AI Halo la care te-ai conectat cu succes. Reconectează-te, editează credențialele sau adaugă un dispozitiv nou. |
| **Information** | Linkuri către documentație și suport pe forum. |
| **Customize** | Repoziționează aplicația pe desktop, schimbă tipul de terminal (doar Windows) și verifică actualizările pentru AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Tipul de terminal (Windows)** — Alege între **PowerShell** (implicit) și **Windows Command Prompt**.
- **Tipul de terminal (Linux)** — Este disponibil doar terminalul implicit al sistemului.
- **Actualizări aplicație** — Această filă este locul potrivit pentru a verifica și instala versiuni noi AMD Sync direct din interfață; nu este necesar un instrument separat de actualizare.

> Un dispozitiv apare sub **Devices** doar după o primă conectare reușită, astfel încât încercările eșuate nu vor aglomera lista.

---

## Depanare

- **Conexiunea eșuează imediat** — Confirmă că serverul SSH este activat pe fila **Remote** din Developer Center a Ryzen AI Halo.
- **Eroare de parolă greșită** — Folosește **parola de conectare a sistemului de operare** de pe Ryzen AI Halo, nu parolele preluate din Developer Center.
- **Butonul VS Code nu face nimic** — Instalează VS Code pe mașina client de la [code.visualstudio.com](https://code.visualstudio.com).
- **Pictograma AMD Sync din tray lipsește (Linux/GNOME)** — Instalează și activează extensia AppIndicator.
- **Fișierul `.deb` nu se deschide din managerul de fișiere** — Folosește `sudo apt install ./AMDSyncInstaller.deb` dintr-un terminal.
- **Configurarea reapare la fiecare lansare (Linux)**: deblochează inelul de chei (keyring) de autentificare, sau lansează cu `--password-store=gnome-libsecret`, apoi refă configurarea o singură dată.

---