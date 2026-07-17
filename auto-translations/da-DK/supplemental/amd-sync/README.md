<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Fjernudvikling med AMD Sync

## Oversigt

**AMD Sync** gør din bærbare computer til et fjernstyret cockpit for AMD Ryzen™ AI Halo. Spring manuel SSH-, nøgle- og IDE-opsætning over — installer AMD Sync og få ét-klik-adgang til en fjernterminale, VS Code, JupyterLab og et live GPU/CPU/hukommelsesdashboard på Ryzen AI Halo.

Din lokale maskine forbliver velkendt; alle kommandoer, notebooks og modeller kører på Ryzen AI Halo.

> **Tip**: Denne side vil indeholde eventuelle nye opdateringer til AMDSync.

## Hvad du vil lære

- Aktivér SSH på Ryzen AI Halo og opret forbindelse til den fra AMD Sync
- Start VS Code, Terminal, JupyterLab og Live Metrics mod Ryzen AI Halo med ét klik
- Organiser fjernarbejde ved hjælp af AMD Syncs administrerede projektmapper

---

## Kernebegreber

AMD Sync har to sider: en **klient** (din bærbare computer, der kører AMD Sync-appen) og en **server** (Ryzen AI Halo, der kører en SSH-server, som AMD Sync tunnelerer ind i). Alt, hvad du starter fra AMD Sync — VS Code, en terminal, en notebook — åbner lokalt, men udføres på Ryzen AI Halo.

> **Understøttede klienter:** Windows 11 og Linux. macOS understøttes ikke.

---

## Trin 1 — Aktivér SSH på Ryzen AI Halo


> **Bemærk:** På Windows leveres Ryzen AI Halo med SSH-serveren *slået fra som standard*. På Linux leveres den med SSH-serveren *slået til som standard*.

1. På Ryzen AI Halo skal du åbne **AMD Ryzen™ AI Developer Center**.
2. Gå til fanen **Remote**.
3. Slå **SSH Server** til.
4. Notér **IP-adressen**, **porten** og **brugernavnet** vist under **Server Information** — du skal indsætte dem i AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Bemærk:** Dette er AMD Developer Center til Windows. Linux-versionen kan have en anden brugergrænseflade, men lignende fjernfunktionalitet.

> **Tip:** AMD Sync beder om **OS-loginadgangskoden** for den pågældende bruger, ikke en adgangskode fra Developer Center.

---

## Trin 2 — Installer AMD Sync på din klient

AMD Sync kører på Windows 11 og Linux. Download installationsprogrammet til dit operativsystem, og følg derefter trinene nedenfor. Efter installationen skal du klikke på **Accept & Install** på skærmen **Get Started** — AMD Sync starter automatisk, når det er færdigt.

### Windows

[Download AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Dobbeltklik på `AMDSyncInstaller.exe`.
2. Klik på **Accept & Install**.

> Hvis Windows Firewall beder dig om det, skal du give AMD Sync netværksadgang, så den kan nå Ryzen AI Halo via SSH.

### Linux

Klik på linket for at downloade dit foretrukne format:

| Format | Download | Installationskommando |
|--------|----------|-----------------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Bemærk:** Ubuntu App Center kan markere en lokalt åbnet `.deb` som *"Potentielt usikker."* Det er standardadvarslen for ethvert tredjeparts lokalt installationsprogram. Hvis dobbeltklik på `.deb` mislykkes, skal du bruge terminalkommandoen ovenfor.

---

## Trin 3 — Opret forbindelse til din Ryzen AI Halo

Ved første start viser AMD Sync formularen **Add a Remote Device**. Udfyld den med værdierne fra Developer Centers fane **Remote**.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Felt | Bemærkninger |
|------|--------------|
| **Device Name** *(valgfrit)* | En venlig betegnelse som `Ryzen AI Halo`. Standardværdi er `Device 1`, `Device 2`, … |
| **Hostname or IP** | Fra fanen Remote |
| **SSH Port** | Fra fanen Remote (kun tal) |
| **Username** | Dit OS-kontonavn på Ryzen AI Halo |
| **Password** | Din OS-loginadgangskode — maskeret mens du skriver |

Klik på **Add Device**. Efter en kort indlæsningsskærm vil du se **"Connection Successful"** og lande på hjemmevisningen, som lever i din systembakke. Klik uden for vinduet for at lukke det; AMD Sync fortsætter med at køre og er ét klik væk.

> **Hvis forbindelsen mislykkes,** vender AMD Sync tilbage til formularen med dine værdier bevaret. De sædvanlige årsager er, at SSH er deaktiveret på Ryzen AI Halo, den forkerte adgangskode, eller at de to enheder er på forskellige netværk.

---

## Trin 4 — Start dit første fjernværktøj

Hjemmevisningen giver dig fem ét-klik-komponenter — alle tilgængelige uanset hvilket operativsystem klienten og Ryzen AI Halo kører.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponent | Hvad den gør |
|-----------|--------------|
| **Directory** | Vælger mappen på Ryzen AI Halo, som VS Code, Terminal og JupyterLab åbner i. Standardværdi er et administreret `Documents/AMD_Sync`-arbejdsområde. |
| **VS Code** | Åbner VS Code lokalt med en SSH-tunnel ind i den valgte mappe. |
| **Terminal** | Åbner en lokal terminal SSH-forbundet til Ryzen AI Halo i den valgte mappe. |
| **JupyterLab** | Starter et notebook-projekt SSH-forbundet til Ryzen AI Halo, afgrænset til den valgte mappe. |
| **Live Metrics** | Realtidsvisning af GPU-, hukommelses- og CPU-udnyttelse på Ryzen AI Halo. |

### Prøv VS Code

Til din første start skal du prøve **VS Code**.

1. Lad **Directory** stå på standardværdien `~/Documents/AMD_Sync`.
2. Klik på **VS Code**.
3. AMD Sync opretter `Documents/AMD_Sync/Project_1` på Ryzen AI Halo og åbner VS Code lokalt, tunneleret ind i den.

Du redigerer nu filer, der befinder sig på Ryzen AI Halo, med din lokale VS Code-opsætning. Opret `helloworld.py`, tilføj `print("hello world")`, åbn den integrerede terminal (`` Ctrl + ` ``), og kør den:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Statuslinjen viser **SSH: Linux** — bevis på, at din kode kører på Ryzen AI Halo og ikke på din bærbare computer.

### Prøv terminalen

Klik på **Terminal** for at lande i den samme mappe via SSH uden at forlade tastaturet.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

På Windows er standardterminalen **PowerShell** — skift til **Windows Command Prompt** fra menuen Indstillinger, hvis du foretrækker det. På Linux bruger AMD Sync din standard systemterminal.

---

## Sådan fungerer Directory

Rullemenuen **Directory** er den vigtigste kontrol i AMD Sync — den bestemmer, hvor hvert værktøj, du starter, lander på Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (standard)** — Når du starter VS Code eller JupyterLab herfra, oprettes der automatisk en ny projektmappe (`Project_1`, `Project_2`, … for VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … for JupyterLab).
- **Eksisterende projektmapper** — Enhver direkte undermappe af `AMD_Sync` (herunder mapper du opretter manuelt på Ryzen AI Halo) vises i rullemenuen. Den senest brugte mappe bliver standard næste gang.
- **Brugerdefinerede stier** — Skriv en absolut sti for at åbne en mappe et andet sted på Ryzen AI Halo. AMD Sync *åbner* den kun — den opretter ikke mapper uden for `AMD_Sync`, og brugerdefinerede stier gemmes ikke mellem sessioner.

Hvis en brugerdefineret sti ikke virker, fortæller AMD Sync dig hvorfor: ugyldig syntaks, mappen eksisterer ikke, eller stien peger på en fil.

---

## Live Metrics og JupyterLab

- **Live Metrics** — Et live dashboard over GPU-, hukommelses- og CPU-forbrug. Den hurtigste måde at bekræfte, at en fjerntræningstask faktisk rammer hardwaren.
- **JupyterLab** — Et fuldt notebook-projekt SSH-forbundet til Ryzen AI Halo med sin egen integrerede terminal til at blande notebook-celler og shell-kommandoer uden at forlade brugergrænsefladen.

---

## Indstillinger og flere enheder

Menuen **Settings** har tre faner:

| Fane | Hvad den dækker |
|------|-----------------|
| **Devices** | Viser alle Ryzen AI Halo-enheder, du har oprettet forbindelse til. Genopret forbindelse, rediger legitimationsoplysninger, eller tilføj en ny enhed. |
| **Information** | Links til dokumentation og forum-support. |
| **Customize** | Flyt appen på dit skrivebord, skift terminaltype (kun Windows), og søg efter AMD Sync-opdateringer. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Terminaltype (Windows)** — Vælg mellem **PowerShell** (standard) og **Windows Command Prompt**.
- **Terminaltype (Linux)** — Kun den standard systemterminal er tilgængelig.
- **App-opdateringer** — Denne fane er det rette sted at søge efter og installere nye AMD Sync-versioner fra brugergrænsefladen; der er ikke behov for et separat opdateringsprogram.

> En enhed vises kun under **Devices** efter en vellykket første forbindelse, så mislykkede forsøg vil ikke fylde listen.

---

## Fejlfinding

- **Forbindelsen mislykkes øjeblikkeligt** — Bekræft, at SSH-serveren er aktiveret på Ryzen AI Halos fane **Remote** i Developer Center.
- **Forkert adgangskode-fejl** — Brug din **OS-loginadgangskode** på Ryzen AI Halo, ikke adgangskoder fra Developer Center.
- **VS Code-knappen gør ingenting** — Installer VS Code på din klientmaskine fra [code.visualstudio.com](https://code.visualstudio.com).
- **AMD Sync-bakkeikon mangler (Linux/GNOME)** — Installer og aktivér AppIndicator-udvidelsen.
- **`.deb` åbner ikke fra filhåndteringen** — Brug `sudo apt install ./AMDSyncInstaller.deb` fra en terminal.

---