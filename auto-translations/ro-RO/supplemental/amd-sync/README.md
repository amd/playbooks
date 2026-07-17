<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Dezvoltare la Distanță cu AMD Sync

## Prezentare Generală

**AMD Sync** transformă laptopul tău într-un cockpit de control de la distanță pentru AMD Ryzen™ AI Halo. Renunță la configurarea manuală SSH, a cheilor și a mediului IDE — instalează AMD Sync și obții acces cu un singur clic la un terminal de la distanță, VS Code, JupyterLab și un panou de monitorizare live GPU/CPU/memorie pe Ryzen AI Halo.

Mașina ta locală rămâne familiară; fiecare comandă, notebook și model rulează pe Ryzen AI Halo.

> **Sfat**: Această pagină va conține orice actualizări noi ale AMDSync.

## Ce Vei Învăța

- Activarea SSH pe Ryzen AI Halo și conectarea la acesta din AMD Sync
- Lansarea VS Code, Terminal, JupyterLab și Live Metrics pe Ryzen AI Halo cu un singur clic
- Organizarea lucrului de la distanță folosind folderele de proiect gestionate de AMD Sync

---

## Concepte de Bază

AMD Sync are două componente: un **client** (laptopul tău, care rulează aplicația AMD Sync) și un **server** (Ryzen AI Halo, care rulează un server SSH prin care AMD Sync creează un tunel). Tot ce lansezi din AMD Sync — VS Code, un terminal, un notebook — se deschide local, dar se execută pe Ryzen AI Halo.

> **Clienți suportați:** Windows 11 și Linux. macOS nu este suportat.

---

## Pasul 1 — Activarea SSH pe Ryzen AI Halo


> **Notă:** Pe Windows, Ryzen AI Halo vine cu serverul SSH *dezactivat implicit*. Pe Linux, vine cu serverul SSH *activat implicit*.

1. Pe Ryzen AI Halo, deschide **AMD Ryzen™ AI Developer Center**.
2. Mergi la fila **Remote**.
3. Activează **SSH Server**.
4. Notează **Adresa IP**, **Portul** și **Numele de utilizator** afișate sub **Server Information** — le vei introduce în AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Notă:** Acesta este AMD Developer Center pentru Windows. Cel pentru Linux poate avea o interfață diferită, dar funcționalitate similară de acces de la distanță.

> **Sfat:** AMD Sync solicită **parola de autentificare OS** a acelui utilizator, nu o parolă din Developer Center.

---

## Pasul 2 — Instalarea AMD Sync pe Clientul Tău

AMD Sync rulează pe Windows 11 și Linux. Descarcă programul de instalare pentru sistemul tău de operare, apoi urmează pașii de mai jos. După instalare, fă clic pe **Accept & Install** pe ecranul **Get Started** — AMD Sync pornește automat când finalizează.

### Windows

[Descarcă AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Fă dublu clic pe `AMDSyncInstaller.exe`.
2. Fă clic pe **Accept & Install**.

> Dacă Windows Firewall te solicită, permite accesul la rețea pentru AMD Sync, astfel încât să poată ajunge la Ryzen AI Halo prin SSH.

### Linux

Fă clic pe link pentru a descărca formatul preferat:

| Format | Descărcare | Comandă de instalare |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Notă:** Ubuntu App Center poate semnala un fișier `.deb` deschis local ca *„Potențial nesigur."* Aceasta este avertizarea standard pentru orice program de instalare local de la terți. Dacă dublu-clicul pe fișierul `.deb` eșuează, folosește comanda din terminal de mai sus.

---

## Pasul 3 — Conectarea la Ryzen AI Halo

La prima lansare, AMD Sync afișează formularul **Add a Remote Device**. Completează-l folosind valorile din fila **Remote** a Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Câmp | Note |
|-------|-------|
| **Device Name** *(opțional)* | O etichetă prietenoasă, precum `Ryzen AI Halo`. Implicit este `Device 1`, `Device 2`, … |
| **Hostname or IP** | Din fila Remote |
| **SSH Port** | Din fila Remote (doar cifre) |
| **Username** | Numele contului tău OS pe Ryzen AI Halo |
| **Password** | Parola ta de autentificare OS — mascată pe măsură ce tastezi |

Fă clic pe **Add Device**. După un scurt ecran de încărcare, vei vedea **„Connection Successful"** și vei ajunge pe ecranul principal, care se află în bara de sistem. Fă clic în afara ferestrei pentru a o închide; AMD Sync rămâne activ și este la un clic distanță.

> **Dacă conexiunea eșuează,** AMD Sync revine la formular cu valorile tale păstrate. Cauzele obișnuite sunt SSH dezactivat pe Ryzen AI Halo, parola greșită sau cele două dispozitive aflate pe rețele diferite.

---

## Pasul 4 — Lansarea Primului Instrument de la Distanță

Ecranul principal îți oferă cinci componente cu un singur clic — toate disponibile indiferent de sistemul de operare al clientului și al Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Componentă | Ce face |
|-----------|--------------|
| **Directory** | Selectează folderul de pe Ryzen AI Halo în care se vor deschide VS Code, Terminal și JupyterLab. Implicit este un spațiu de lucru gestionat `Documents/AMD_Sync`. |
| **VS Code** | Deschide VS Code local cu un tunel SSH în folderul selectat. |
| **Terminal** | Deschide un terminal local conectat prin SSH la Ryzen AI Halo, în folderul selectat. |
| **JupyterLab** | Lansează un proiect de notebook conectat prin SSH la Ryzen AI Halo, limitat la folderul selectat. |
| **Live Metrics** | Vizualizare în timp real a utilizării GPU, memoriei și CPU pe Ryzen AI Halo. |

### Încearcă VS Code

Pentru prima lansare, încearcă **VS Code**.

1. Lasă **Directory** pe valoarea implicită `~/Documents/AMD_Sync`.
2. Fă clic pe **VS Code**.
3. AMD Sync creează `Documents/AMD_Sync/Project_1` pe Ryzen AI Halo și deschide VS Code local, cu tunel în acesta.

Acum editezi fișiere care se află pe Ryzen AI Halo cu configurația ta locală VS Code. Creează `helloworld.py`, adaugă `print("hello world")`, deschide terminalul integrat (`` Ctrl + ` ``), și rulează-l:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Bara de stare afișează **SSH: Linux** — dovadă că codul tău rulează pe Ryzen AI Halo, nu pe laptopul tău.

### Încearcă Terminalul

Fă clic pe **Terminal** pentru a accesa același folder prin SSH fără a părăsi tastatura.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Pe Windows, terminalul implicit este **PowerShell** — comută la **Windows Command Prompt** din meniul Settings dacă preferi. Pe Linux, AMD Sync folosește terminalul implicit al sistemului tău.

---

## Cum Funcționează Directory

Meniul derulant **Directory** este cel mai important control din AMD Sync — el decide unde ajunge pe Ryzen AI Halo fiecare instrument pe care îl lansezi.

- **`~/Documents/AMD_Sync` (implicit)** — Lansarea VS Code sau JupyterLab de aici creează automat un folder de proiect nou (`Project_1`, `Project_2`, … pentru VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … pentru JupyterLab).
- **Foldere de proiect existente** — Orice subfolder direct al `AMD_Sync` (inclusiv folderele create manual pe Ryzen AI Halo) apare în meniul derulant. Ultimul folder folosit devine implicit data viitoare.
- **Căi personalizate** — Tastează orice cale absolută pentru a deschide un folder în altă parte pe Ryzen AI Halo. AMD Sync doar îl *deschide* — nu va crea foldere în afara `AMD_Sync`, iar căile personalizate nu sunt salvate între sesiuni.

Dacă o cale personalizată nu funcționează, AMD Sync îți spune de ce: sintaxă invalidă, folderul nu există sau calea indică un fișier.

---

## Live Metrics și JupyterLab

- **Live Metrics** — Un panou de monitorizare live a utilizării GPU, memoriei și CPU. Cel mai rapid mod de a confirma că o sesiune de antrenament de la distanță utilizează efectiv hardware-ul.
- **JupyterLab** — Un proiect complet de notebook conectat prin SSH la Ryzen AI Halo, cu propriul terminal integrat pentru combinarea celulelor de notebook cu comenzi shell fără a părăsi interfața.

---

## Setări și Dispozitive Multiple

Meniul **Settings** are trei file:

| Filă | Ce acoperă |
|-----|----------------|
| **Devices** | Listează fiecare Ryzen AI Halo la care te-ai conectat cu succes. Reconectează-te, editează credențialele sau adaugă un dispozitiv nou. |
| **Information** | Linkuri către documentație și suport pe forum. |
| **Customize** | Repozitionează aplicația pe desktop, schimbă tipul de terminal (doar Windows) și verifică actualizările AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Tipul de terminal (Windows)** — Alege între **PowerShell** (implicit) și **Windows Command Prompt**.
- **Tipul de terminal (Linux)** — Este disponibil doar terminalul implicit al sistemului.
- **Actualizări aplicație** — Această filă este locul potrivit pentru a verifica și instala versiuni noi de AMD Sync din interfață; nu este necesar un program de actualizare separat.

> Un dispozitiv apare sub **Devices** doar după o primă conexiune reușită, astfel încât tentativele eșuate nu vor aglomera lista.

---

## Depanare

- **Conexiunea eșuează imediat** — Confirmă că serverul SSH este activat în fila **Remote** a Ryzen AI Halo din Developer Center.
- **Eroare de parolă greșită** — Folosește **parola de autentificare OS** de pe Ryzen AI Halo, nu parolele din Developer Center.
- **Butonul VS Code nu face nimic** — Instalează VS Code pe mașina ta client de la [code.visualstudio.com](https://code.visualstudio.com).
- **Pictograma AMD Sync din bara de sistem lipsește (Linux/GNOME)** — Instalează și activează extensia AppIndicator.
- **Fișierul `.deb` nu se deschide din managerul de fișiere** — Folosește `sudo apt install ./AMDSyncInstaller.deb` dintr-un terminal.

---