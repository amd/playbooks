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

**AMD Sync** transformă laptopul tău într-un cockpit la distanță pentru AMD Ryzen™ AI Halo. Renunță la configurarea manuală SSH, la chei și la IDE — instalează AMD Sync și obții acces cu un singur clic la un terminal la distanță, VS Code, JupyterLab și un tablou de bord live pentru GPU/CPU/memorie pe Ryzen AI Halo.

Computerul tău local rămâne familiar; fiecare comandă, notebook și model rulează pe Ryzen AI Halo.

> **Sfat**: Această pagină va conține orice actualizări noi ale AMDSync.

## Ce vei învăța

- Să activezi SSH pe Ryzen AI Halo și să te conectezi la acesta din AMD Sync
- Să lansezi VS Code, Terminal, JupyterLab și Live Metrics pentru Ryzen AI Halo cu un singur clic
- Să organizezi lucrul la distanță folosind folderele de proiect gestionate de AMD Sync

---

## Concepte de bază

AMD Sync are două părți: un **client** (laptopul tău, pe care rulează aplicația AMD Sync) și un **server** (Ryzen AI Halo, pe care rulează un server SSH în care AMD Sync creează un tunel). Tot ce lansezi din AMD Sync — VS Code, un terminal, un notebook — se deschide local, dar se execută pe Ryzen AI Halo.

> **Clienți compatibili:** Windows 11 și Linux. macOS nu este compatibil.

---

## Pasul 1 — Activează SSH pe Ryzen AI Halo


> **Notă:** Pe Windows, Ryzen AI Halo vine cu serverul SSH *dezactivat implicit*. Pe Linux, vine cu serverul SSH *activat implicit*.

1. Pe Ryzen AI Halo, deschide **AMD Ryzen™ AI Developer Center**.
2. Mergi la fila **Remote**.
3. Activează **SSH Server**.
4. Notează **IP Address**, **Port** și **Username** afișate sub **Server Information** — le vei introduce în AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Notă:** Acesta este AMD Developer Center pentru Windows. Cel pentru Linux poate avea o interfață diferită, dar o funcționalitate la distanță similară.

> **Sfat:** AMD Sync solicită **parola de autentificare a sistemului de operare** a acelui utilizator, nu o parolă din Developer Center.

---

## Pasul 2 — Instalează AMD Sync pe clientul tău

AMD Sync rulează pe Windows 11 și Linux. Descarcă programul de instalare pentru sistemul tău de operare, apoi urmează pașii de mai jos. După instalare, apasă pe **Accept & Install** din ecranul **Get Started** — AMD Sync se lansează automat la finalizare.

### Windows

[Descarcă AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Dă dublu clic pe `AMDSyncInstaller.exe`.
2. Apasă pe **Accept & Install**.

> Dacă Windows Firewall îți solicită confirmare, permite accesul la rețea pentru AMD Sync, astfel încât acesta să poată comunica cu Ryzen AI Halo prin SSH.

### Linux

Dă clic pe link pentru a descărca formatul preferat:

| Format | Descărcare | Comandă de instalare |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Notă:** Ubuntu App Center poate marca un fișier `.deb` deschis local ca fiind *"Potențial nesigur."* Acesta este avertismentul standard pentru orice program de instalare local de la terți. Dacă dublul clic pe `.deb` eșuează, folosește comanda de terminal de mai sus.

---

## Pasul 3 — Conectează-te la Ryzen AI Halo

La prima lansare, AMD Sync afișează formularul **Add a Remote Device**. Completează-l folosind valorile din fila **Remote** a Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Câmp | Note |
|-------|-------|
| **Device Name** *(opțional)* | O etichetă prietenoasă precum `Ryzen AI Halo`. Implicit `Device 1`, `Device 2`, … |
| **Hostname or IP** | Din fila Remote |
| **SSH Port** | Din fila Remote (doar cifre) |
| **Username** | Numele contului tău de sistem de operare pe Ryzen AI Halo |
| **Password** | Parola ta de autentificare a sistemului de operare — mascată pe măsură ce o tastezi |

Apasă pe **Add Device**. După un scurt ecran de încărcare, vei vedea **„Connection Successful"** și vei ajunge la vizualizarea de pornire, care se află în bara de sistem (system tray). Dă clic în afara ferestrei pentru a o închide; AMD Sync rămâne activ și este la un clic distanță.

> **Dacă conexiunea eșuează,** AMD Sync revine la formular cu valorile tale păstrate. Cauzele obișnuite sunt dezactivarea SSH pe Ryzen AI Halo, parola greșită sau faptul că cele două dispozitive se află în rețele diferite.

---

## Pasul 4 — Lansează primul tău instrument la distanță

Vizualizarea de pornire îți oferă cinci componente accesibile cu un singur clic — toate disponibile indiferent de sistemul de operare pe care rulează clientul și Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Componentă | Ce face |
|-----------|--------------|
| **Directory** | Alege folderul de pe Ryzen AI Halo în care se vor deschide VS Code, Terminal și JupyterLab. Implicit, un spațiu de lucru gestionat `Documents/AMD_Sync`. |
| **VS Code** | Deschide VS Code local, cu un tunel SSH către folderul selectat. |
| **Terminal** | Deschide un terminal local conectat prin SSH la Ryzen AI Halo, în folderul selectat. |
| **JupyterLab** | Lansează un proiect de tip notebook conectat prin SSH la Ryzen AI Halo, limitat la folderul selectat. |
| **Live Metrics** | Vizualizare în timp real a utilizării GPU, memoriei și CPU pe Ryzen AI Halo. |

### Încearcă VS Code

Pentru prima lansare, încearcă **VS Code**. Instrucțiunile următoare sunt pentru Linux, dar experiența pe Windows este similară.

1. Lasă **Directory** pe valoarea implicită `~/Documents/AMD_Sync`.
2. Dă clic pe **VS Code**.
3. AMD Sync creează `Documents/AMD_Sync/Project_1` pe Ryzen AI Halo și deschide VS Code local, conectat prin tunel la acesta.

Acum editezi fișiere care se află pe Ryzen AI Halo folosind configurația ta locală de VS Code. Creează `helloworld.py`, adaugă `print("hello world")`, deschide terminalul integrat (`` Ctrl + ` ``) și rulează-l:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Bara de stare afișează **SSH: Linux** — dovada că rulezi codul pe Ryzen AI Halo, nu pe laptopul tău.
### Încearcă Terminal

Click pe **Terminal** pentru a intra în același folder prin SSH fără a părăsi tastatura.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Pe Windows, terminalul implicit este **PowerShell** — comută la **Windows Command Prompt** din meniul Settings dacă preferi. Pe Linux, AMD Sync folosește terminalul implicit al sistemului tău.

---

## Cum funcționează Directory

Meniul derulant **Directory** este cel mai important control din AMD Sync — acesta decide unde ajunge fiecare instrument pe care îl lansezi pe Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (implicit)** — Lansarea VS Code sau JupyterLab de aici creează automat un folder de proiect nou (`Project_1`, `Project_2`, … pentru VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … pentru JupyterLab).
- **Foldere de proiect existente** — Orice subfolder direct al `AMD_Sync` (inclusiv folderele pe care le creezi manual pe Ryzen AI Halo) apare în meniul derulant. Ultimul folder folosit devine implicit data viitoare.
- **Căi personalizate** — Introdu orice cale absolută pentru a deschide un folder din altă parte de pe Ryzen AI Halo. AMD Sync doar *deschide* folderul — nu va crea foldere în afara `AMD_Sync`, iar căile personalizate nu sunt salvate între sesiuni.

Dacă o cale personalizată nu funcționează, AMD Sync îți spune motivul: sintaxă invalidă, folderul nu există, sau calea indică spre un fișier.

---

## Live Metrics și JupyterLab

- **Live Metrics** — Un tablou de bord live cu utilizarea GPU, memorie și CPU. Cea mai rapidă modalitate de a confirma că o rulare de antrenare la distanță chiar folosește hardware-ul.
- **JupyterLab** — Un proiect notebook complet conectat prin SSH la Ryzen AI Halo, cu propriul terminal integrat pentru a combina celule de notebook și comenzi shell fără a părăsi interfața.

---

## Settings și dispozitive multiple

Meniul **Settings** are trei file:

| Filă | Ce acoperă |
|-----|----------------|
| **Devices** | Listează fiecare Ryzen AI Halo la care te-ai conectat cu succes. Reconectează-te, editează credențialele sau adaugă un nou dispozitiv. |
| **Information** | Linkuri către documentație și suport pe forum. |
| **Customize** | Repoziționează aplicația pe desktop, schimbă tipul de terminal (doar Windows) și verifică actualizările AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Tip terminal (Windows)** — Alege între **PowerShell** (implicit) și **Windows Command Prompt**.
- **Tip terminal (Linux)** — Este disponibil doar terminalul implicit al sistemului.
- **Actualizări aplicație** — Această filă este locul potrivit pentru a verifica și instala noi versiuni AMD Sync direct din interfață; nu este necesar un program separat de actualizare.

> Un dispozitiv apare sub **Devices** doar după o primă conectare reușită, astfel încât încercările eșuate nu vor aglomera lista.

---

## Depanare

- **Conexiunea eșuează imediat** — Confirmă că serverul SSH este activat în fila **Remote** din Developer Center de pe Ryzen AI Halo.
- **Eroare de parolă greșită** — Folosește **parola de login a sistemului de operare** de pe Ryzen AI Halo, nu parole preluate din Developer Center.
- **Butonul VS Code nu face nimic** — Instalează VS Code pe mașina ta client de la [code.visualstudio.com](https://code.visualstudio.com).
- **Lipsește pictograma AMD Sync din tray (Linux/GNOME)** — Instalează și activează extensia AppIndicator.
- **Fișierul `.deb` nu se deschide din managerul de fișiere** — Folosește `sudo apt install ./AMDSyncInstaller.deb` dintr-un terminal.
- **Configurarea reapare la fiecare lansare (Linux)**: deblochează-ți inelul de chei (keyring) de login, sau lansează cu `--password-store=gnome-libsecret`, apoi refă configurarea o singură dată.

---