<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversettelse.** Denne siden ble automatisk oversatt fra engelsk og har ikke blitt gjennomgått av et menneske. Den kan inneholde feil, og enkelte instruksjoner, kommandoer, nedlastinger, produkttilgjengelighet eller annet innhold kan variere etter språk eller region. Ved eventuelle uoverensstemmelser eller avvik er den opprinnelige engelske versjonen av playbook-en gjeldende.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Fjernutvikling med AMD Sync

## Oversikt

**AMD Sync** gjør bærbar PC-en din om til en fjernstyrt kontrollsentral for AMD Ryzen™ AI Halo. Hopp over manuell SSH-, nøkkel- og IDE-oppsett — installer AMD Sync og få ett-klikks tilgang til en fjernterminal, VS Code, JupyterLab og et live dashbord for GPU/CPU/minne på Ryzen AI Halo.

Den lokale maskinen din forblir kjent; hver kommando, notatbok og modell kjører på Ryzen AI Halo.

> **Tips**: Denne siden vil inneholde eventuelle nye oppdateringer til AMDSync. 

## Hva du vil lære

- Aktivere SSH på Ryzen AI Halo og koble til den fra AMD Sync
- Starte VS Code, Terminal, JupyterLab og Live Metrics mot Ryzen AI Halo med ett klikk
- Organisere fjernarbeid ved hjelp av AMD Syncs administrerte prosjektmapper

---

## Kjernebegreper

AMD Sync har to sider: en **klient** (din bærbare PC, som kjører AMD Sync-appen) og en **server** (Ryzen AI Halo, som kjører en SSH-server som AMD Sync tunnelerer inn i). Alt du starter fra AMD Sync — VS Code, en terminal, en notatbok — åpnes lokalt, men kjøres på Ryzen AI Halo.

> **Støttede klienter:** Windows 11 og Linux. macOS støttes ikke.

---

## Trinn 1 — Aktiver SSH på Ryzen AI Halo


> **Merk:** På Windows leveres Ryzen AI Halo med SSH-serveren *avslått som standard*. På Linux leveres den med SSH-serveren *på som standard*.

1. Åpne **AMD Ryzen™ AI Developer Center** på Ryzen AI Halo.
2. Gå til fanen **Remote**.
3. Slå på **SSH Server**.
4. Noter **IP Address**, **Port** og **Username** som vises under **Server Information** — du limer disse inn i AMD Sync senere.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Merk:** Dette er AMD Developer Center for Windows. Linux-versjonen kan ha et annet brukergrensesnitt, men lignende fjernstyringsfunksjonalitet.

> **Tips:** AMD Sync spør etter **OS-innloggingspassordet** til brukeren, ikke et passord fra Developer Center.

---

## Trinn 2 — Installer AMD Sync på klienten din

AMD Sync kjører på Windows 11 og Linux. Last ned installasjonsprogrammet for ditt operativsystem, og følg deretter trinnene nedenfor. Etter installasjonen klikker du på **Accept & Install** på skjermbildet **Get Started** — AMD Sync starter automatisk når det er ferdig.

### Windows

[Last ned AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Dobbeltklikk på `AMDSyncInstaller.exe`.
2. Klikk på **Accept & Install**.

> Hvis Windows-brannmuren spør deg om tillatelse, gi AMD Sync nettverkstilgang slik at den kan nå Ryzen AI Halo over SSH.

### Linux

Klikk på lenken for å laste ned ønsket format:

| Format | Nedlasting | Installasjonskommando |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Merk:** Ubuntu App Center kan flagge en lokalt åpnet `.deb`-fil som *"Potentially unsafe."* Dette er den vanlige advarselen for enhver tredjeparts lokal installasjonsfil. Hvis det ikke fungerer å dobbeltklikke på `.deb`-filen, kan du bruke terminalkommandoen ovenfor.

---

## Trinn 3 — Koble til Ryzen AI Halo

Ved første oppstart viser AMD Sync skjemaet **Add a Remote Device**. Fyll det ut med verdiene fra fanen **Remote** i Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Felt | Merknader |
|-------|-------|
| **Device Name** *(valgfritt)* | En brukervennlig etikett som `Ryzen AI Halo`. Standard er `Device 1`, `Device 2`, … |
| **Hostname or IP** | Fra fanen Remote |
| **SSH Port** | Fra fanen Remote (kun tall) |
| **Username** | Din OS-kontobrukernavn på Ryzen AI Halo |
| **Password** | Ditt OS-innloggingspassord — maskert mens du skriver |

Klikk på **Add Device**. Etter en kort lasteskjerm ser du **"Connection Successful"** og havner på hjemmevisningen, som ligger i systemstatusfeltet. Klikk utenfor vinduet for å lukke det; AMD Sync fortsetter å kjøre og er ett klikk unna.

> **Hvis tilkoblingen mislykkes,** går AMD Sync tilbake til skjemaet med verdiene dine bevart. De vanlige årsakene er at SSH er deaktivert på Ryzen AI Halo, feil passord, eller at de to enhetene er på ulike nettverk.

---

## Trinn 4 — Start ditt første fjernverktøy

Hjemmevisningen gir deg fem ett-klikks komponenter — alle tilgjengelige uansett hvilket operativsystem klienten og Ryzen AI Halo kjører.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponent | Hva den gjør |
|-----------|--------------|
| **Directory** | Velger mappen på Ryzen AI Halo som VS Code, Terminal og JupyterLab åpnes i. Standard er en administrert `Documents/AMD_Sync`-arbeidsplass. |
| **VS Code** | Åpner VS Code lokalt med en SSH-tunnel inn i den valgte mappen. |
| **Terminal** | Åpner en lokal terminal SSH-tilkoblet til Ryzen AI Halo, i den valgte mappen. |
| **JupyterLab** | Starter et notatbokprosjekt SSH-tilkoblet til Ryzen AI Halo, begrenset til den valgte mappen. |
| **Live Metrics** | Sanntidsvisning av GPU-, minne- og CPU-bruk på Ryzen AI Halo. |

### Prøv VS Code

For din første oppstart, prøv **VS Code**.

1. La **Directory** stå på standardverdien `~/Documents/AMD_Sync`.
2. Klikk på **VS Code**.
3. AMD Sync oppretter `Documents/AMD_Sync/Project_1` på Ryzen AI Halo og åpner VS Code lokalt, tunnelert inn i den.

Du redigerer nå filer som ligger på Ryzen AI Halo med ditt lokale VS Code-oppsett. Opprett `helloworld.py`, legg til `print("hello world")`, åpne den integrerte terminalen (`` Ctrl + ` ``), og kjør den:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Statuslinjen viser **SSH: Linux** — beviset på at koden din kjører på Ryzen AI Halo, ikke på din bærbare PC.
### Prøv Terminalen

Klikk på **Terminal** for å komme inn i samme mappe over SSH uten å forlate tastaturet.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

På Windows er standardterminalen **PowerShell** — bytt til **Windows Command Prompt** fra Innstillinger-menyen hvis du foretrekker det. På Linux bruker AMD Sync systemets standardterminal.

---

## Slik fungerer Katalogen

**Katalog**-nedtrekksmenyen er den viktigste enkeltkontrollen i AMD Sync — den avgjør hvor alle verktøy du starter havner på Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (standard)** — Å starte VS Code eller JupyterLab herfra oppretter automatisk en ny prosjektmappe (`Project_1`, `Project_2`, … for VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … for JupyterLab).
- **Eksisterende prosjektmapper** — Enhver umiddelbar undermappe av `AMD_Sync` (inkludert mapper du oppretter manuelt på Ryzen AI Halo) vises i nedtrekksmenyen. Den siste mappen du brukte blir standardvalget neste gang.
- **Egendefinerte stier** — Skriv inn en hvilken som helst absolutt sti for å åpne en mappe et annet sted på Ryzen AI Halo. AMD Sync *åpner* den kun — det opprettes ikke mapper utenfor `AMD_Sync`, og egendefinerte stier lagres ikke mellom økter.

Hvis en egendefinert sti ikke fungerer, forteller AMD Sync deg hvorfor: ugyldig syntaks, mappen finnes ikke, eller stien peker til en fil.

---

## Live-målinger og JupyterLab

- **Live-målinger** — Et live-dashbord over GPU-, minne- og CPU-bruk. Den raskeste måten å bekrefte at en ekstern treningskjøring faktisk belaster maskinvaren.
- **JupyterLab** — Et fullstendig notatbokprosjekt SSH-tilkoblet til Ryzen AI Halo, med sin egen integrerte terminal for å blande notatbokceller og skallkommandoer uten å forlate brukergrensesnittet.

---

## Innstillinger og flere enheter

**Innstillinger**-menyen har tre faner:

| Fane | Hva den dekker |
|-----|----------------|
| **Enheter** | Viser hver Ryzen AI Halo du har koblet til med hell. Koble til på nytt, rediger legitimasjon, eller legg til en ny enhet. |
| **Informasjon** | Lenker til dokumentasjon og forumstøtte. |
| **Tilpass** | Flytt appen på skrivebordet, bytt terminaltype (kun Windows), og se etter oppdateringer for AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Terminaltype (Windows)** — Velg mellom **PowerShell** (standard) og **Windows Command Prompt**.
- **Terminaltype (Linux)** — Kun standard systemterminal er tilgjengelig.
- **App-oppdateringer** — Denne fanen er riktig sted for å se etter og installere nye AMD Sync-versjoner fra brukergrensesnittet; ingen separat oppdaterer er nødvendig.

> En enhet vises kun under **Enheter** etter en vellykket første tilkobling, slik at mislykkede forsøk ikke fyller opp listen.

---

## Feilsøking

- **Tilkobling mislykkes umiddelbart** — Bekreft at SSH-serveren er aktivert på **Fjernstyring**-fanen i Developer Center på Ryzen AI Halo.
- **Feil passord-feil** — Bruk ditt **OS-innloggingspassord** på Ryzen AI Halo, ikke passord hentet fra Developer Center.
- **VS Code-knappen gjør ingenting** — Installer VS Code på klientmaskinen din fra [code.visualstudio.com](https://code.visualstudio.com).
- **AMD Sync-ikonet i systemstatusfeltet mangler (Linux/GNOME)** — Installer og aktiver AppIndicator-utvidelsen.
- **`.deb` vil ikke åpnes fra filbehandleren** — Bruk `sudo apt install ./AMDSyncInstaller.deb` fra en terminal.

---