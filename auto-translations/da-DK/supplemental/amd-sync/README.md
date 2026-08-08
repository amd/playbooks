<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversættelse.** Denne side er automatisk oversat fra engelsk og er ikke blevet gennemgået af et menneske. Den kan indeholde fejl, og visse instruktioner, kommandoer, downloads, produkttilgængelighed eller andet indhold kan variere afhængigt af sprog eller region. I tilfælde af uoverensstemmelse eller afvigelse er den oprindelige engelske version af playbook'en gældende og har forrang.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Fjernudvikling med AMD Sync

## Oversigt

**AMD Sync** forvandler din bærbare computer til en fjernstyret cockpit til AMD Ryzen™ AI Halo. Spring den manuelle opsætning af SSH, nøgler og IDE over — installer AMD Sync og få adgang med ét klik til en fjernterminal, VS Code, JupyterLab og et live GPU/CPU/hukommelses-dashboard på Ryzen AI Halo.

Din lokale maskine forbliver velkendt; hver kommando, notebook og model kører på Ryzen AI Halo.

> **Tip**: Denne side vil indeholde eventuelle nye opdateringer til AMDSync.

## Hvad du vil lære

- Aktivere SSH på Ryzen AI Halo og oprette forbindelse til den fra AMD Sync
- Starte VS Code, Terminal, JupyterLab og Live Metrics mod Ryzen AI Halo med ét klik
- Organisere fjernarbejde ved hjælp af AMD Syncs administrerede projektmapper

---

## Grundlæggende koncepter

AMD Sync har to sider: en **klient** (din bærbare computer, der kører AMD Sync-appen) og en **server** (Ryzen AI Halo, der kører en SSH-server, som AMD Sync tunnellerer ind i). Alt, du starter fra AMD Sync — VS Code, en terminal, en notebook — åbnes lokalt, men eksekveres på Ryzen AI Halo.

> **Understøttede klienter:** Windows 11 og Linux. macOS understøttes ikke.

---

## Trin 1 — Aktiver SSH på Ryzen AI Halo


> **Bemærk:** På Windows leveres Ryzen AI Halo med SSH-serveren *slået fra som standard*. På Linux leveres den med SSH-serveren *slået til som standard*.

1. Åbn **AMD Ryzen™ AI Developer Center** på Ryzen AI Halo.
2. Gå til fanen **Remote**.
3. Slå **SSH Server** til.
4. Bemærk **IP-adressen**, **porten** og **brugernavnet**, der vises under **Server Information** — du skal indsætte dem i AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Bemærk:** Dette er AMD Developer Center til Windows. Linux-versionen kan have en anden brugerflade, men lignende fjernstyringsfunktionalitet.

> **Tip:** AMD Sync beder om **OS-loginadgangskoden** for den pågældende bruger, ikke en adgangskode fra Developer Center.

---

## Trin 2 — Installer AMD Sync på din klient

AMD Sync kører på Windows 11 og Linux. Download installationsprogrammet til dit operativsystem, og følg derefter trinnene nedenfor. Efter installationen skal du klikke på **Accept & Install** på skærmen **Get Started** — AMD Sync starter automatisk, når det er færdigt.

### Windows

[Download AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Dobbeltklik på `AMDSyncInstaller.exe`.
2. Klik på **Accept & Install**.

> Hvis Windows Firewall spørger dig, skal du give AMD Sync netværksadgang, så det kan nå Ryzen AI Halo via SSH.

### Linux

Klik på linket for at downloade dit foretrukne format:

| Format | Download | Installationskommando |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Bemærk:** Ubuntu App Center kan markere en lokalt åbnet `.deb`-fil som *"Potentielt usikker."* Dette er den standardadvarsel, der vises for ethvert lokalt installationsprogram fra tredjepart. Hvis det mislykkes at dobbeltklikke på `.deb`-filen, skal du bruge terminalkommandoen ovenfor.

---

## Trin 3 — Opret forbindelse til din Ryzen AI Halo

Ved første opstart viser AMD Sync formularen **Add a Remote Device**. Udfyld den med værdierne fra fanen **Remote** i Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Felt | Bemærkninger |
|-------|-------|
| **Device Name** *(valgfrit)* | Et venligt navn som `Ryzen AI Halo`. Standardværdien er `Device 1`, `Device 2`, … |
| **Hostname or IP** | Fra fanen Remote |
| **SSH Port** | Fra fanen Remote (kun tal) |
| **Username** | Dit OS-kontonavn på Ryzen AI Halo |
| **Password** | Din OS-loginadgangskode — maskeret, mens du skriver |

Klik på **Add Device**. Efter en kort indlæsningsskærm ser du **"Connection Successful"**, og du lander på hjemmevisningen, som ligger i dit systembakke. Klik uden for vinduet for at lukke det; AMD Sync fortsætter med at køre og er kun ét klik væk.

> **Hvis forbindelsen mislykkes,** vender AMD Sync tilbage til formularen med dine værdier bevaret. De typiske årsager er, at SSH er deaktiveret på Ryzen AI Halo, forkert adgangskode, eller at de to enheder er på forskellige netværk.

---

## Trin 4 — Start dit første fjernværktøj

Hjemmevisningen giver dig fem komponenter med ét klik — alle tilgængelige uanset hvilket operativsystem klienten og Ryzen AI Halo kører.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponent | Hvad den gør |
|-----------|--------------|
| **Directory** | Vælger mappen på Ryzen AI Halo, som VS Code, Terminal og JupyterLab åbnes i. Standard er en administreret `Documents/AMD_Sync`-arbejdsmappe. |
| **VS Code** | Åbner VS Code lokalt med en SSH-tunnel ind i den valgte mappe. |
| **Terminal** | Åbner en lokal terminal med SSH-forbindelse til Ryzen AI Halo, i den valgte mappe. |
| **JupyterLab** | Starter et notebook-projekt med SSH-forbindelse til Ryzen AI Halo, afgrænset til den valgte mappe. |
| **Live Metrics** | Realtidsvisning af GPU-, hukommelses- og CPU-udnyttelse på Ryzen AI Halo. |

### Prøv VS Code

Til din første opstart kan du prøve **VS Code**.

1. Lad **Directory** stå på standardværdien `~/Documents/AMD_Sync`.
2. Klik på **VS Code**.
3. AMD Sync opretter `Documents/AMD_Sync/Project_1` på Ryzen AI Halo og åbner VS Code lokalt, tunnelleret ind i den.

Du redigerer nu filer, der ligger på Ryzen AI Halo, med din lokale VS Code-opsætning. Opret `helloworld.py`, tilføj `print("hello world")`, åbn den integrerede terminal (`` Ctrl + ` ``), og kør den:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Statuslinjen viser **SSH: Linux** — beviset på, at din kode kører på Ryzen AI Halo, ikke på din bærbare computer.
### Prøv Terminal

Klik på **Terminal** for at gå ind i den samme mappe via SSH uden at forlade tastaturet.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

På Windows er standardterminalen **PowerShell** — skift til **Windows Command Prompt** fra menuen Indstillinger, hvis du foretrækker det. På Linux bruger AMD Sync din systems standardterminal.

---

## Sådan fungerer mappen

Rullemenuen **Directory** er den enkeltvis vigtigste kontrolelement i AMD Sync — den afgør, hvor ethvert værktøj, du starter, havner på Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (standard)** — Ved at starte VS Code eller JupyterLab herfra oprettes der automatisk en ny projektmappe (`Project_1`, `Project_2`, … til VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … til JupyterLab).
- **Eksisterende projektmapper** — Enhver direkte undermappe af `AMD_Sync` (inklusive mapper, du selv opretter på Ryzen AI Halo) vises i rullemenuen. Den mappe, du sidst brugte, bliver standardvalget næste gang.
- **Brugerdefinerede stier** — Indtast en absolut sti for at åbne en mappe et andet sted på Ryzen AI Halo. AMD Sync *åbner* den blot — den opretter ikke mapper uden for `AMD_Sync`, og brugerdefinerede stier gemmes ikke mellem sessioner.

Hvis en brugerdefineret sti ikke virker, fortæller AMD Sync dig hvorfor: ugyldig syntaks, mappen findes ikke, eller stien peger på en fil.

---

## Live Metrics og JupyterLab

- **Live Metrics** — Et live-dashboard over GPU-, hukommelses- og CPU-forbrug. Den hurtigste måde at bekræfte, at en fjerntræningskørsel rent faktisk belaster hardwaren.
- **JupyterLab** — Et fuldt notebook-projekt forbundet via SSH til Ryzen AI Halo, med sin egen integrerede terminal til at blande notebook-celler og shell-kommandoer uden at forlade brugerfladen.

---

## Indstillinger og flere enheder

Menuen **Settings** har tre faner:

| Fane | Hvad den dækker |
|-----|----------------|
| **Devices** | Viser hver Ryzen AI Halo, du har oprettet forbindelse til med succes. Genopret forbindelse, rediger loginoplysninger, eller tilføj en ny enhed. |
| **Information** | Links til dokumentation og forumsupport. |
| **Customize** | Flyt placeringen af appen på dit skrivebord, skift terminaltype (kun Windows), og tjek for opdateringer til AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Terminaltype (Windows)** — Vælg mellem **PowerShell** (standard) og **Windows Command Prompt**.
- **Terminaltype (Linux)** — Kun systemets standardterminal er tilgængelig.
- **App-opdateringer** — Denne fane er det rette sted at tjekke for og installere nye versioner af AMD Sync direkte fra brugerfladen; der kræves ingen separat opdateringsfunktion.

> En enhed vises først under **Devices**, når der er oprettet forbindelse med succes første gang, så mislykkede forsøg fylder ikke listen op.

---

## Fejlfinding

- **Forbindelsen mislykkes med det samme** — Bekræft, at SSH-serveren er aktiveret på Ryzen AI Halos fane **Remote** i Developer Center.
- **Fejl med forkert adgangskode** — Brug din **login-adgangskode til operativsystemet** på Ryzen AI Halo, ikke adgangskoder fra Developer Center.
- **VS Code-knappen gør ingenting** — Installer VS Code på din klientmaskine fra [code.visualstudio.com](https://code.visualstudio.com).
- **AMD Sync-ikonet mangler i statusfeltet (Linux/GNOME)** — Installer og aktiver AppIndicator-udvidelsen.
- **`.deb`-filen vil ikke åbne fra filhåndteringen** — Brug `sudo apt install ./AMDSyncInstaller.deb` fra en terminal.

---