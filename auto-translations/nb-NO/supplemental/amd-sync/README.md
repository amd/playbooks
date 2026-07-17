<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Fjernutviklng med AMD Sync

## Oversikt

**AMD Sync** gjør laptopen din om til et fjernstyrt cockpit for AMD Ryzen™ AI Halo. Hopp over manuell oppsett av SSH, nøkler og IDE — installer AMD Sync og få ett-klikks tilgang til en ekstern terminal, VS Code, JupyterLab og et sanntids GPU/CPU/minne-dashbord på Ryzen AI Halo.

Din lokale maskin forblir kjent; alle kommandoer, notatbøker og modeller kjøres på Ryzen AI Halo.

> **Tips**: Denne siden vil inneholde alle nye oppdateringer til AMDSync.

## Hva du vil lære

- Aktivere SSH på Ryzen AI Halo og koble til den fra AMD Sync
- Starte VS Code, Terminal, JupyterLab og Live Metrics mot Ryzen AI Halo med ett klikk
- Organisere eksternt arbeid ved hjelp av AMD Syncs administrerte prosjektmapper

---

## Kjernekonsepter

AMD Sync har to sider: en **klient** (laptopen din, som kjører AMD Sync-appen) og en **server** (Ryzen AI Halo, som kjører en SSH-server som AMD Sync tunnelerer inn i). Alt du starter fra AMD Sync — VS Code, en terminal, en notatbok — åpnes lokalt, men kjøres på Ryzen AI Halo.

> **Støttede klienter:** Windows 11 og Linux. macOS støttes ikke.

---

## Trinn 1 — Aktiver SSH på Ryzen AI Halo


> **Merk:** På Windows leveres Ryzen AI Halo med SSH-serveren *av som standard*. På Linux leveres den med SSH-serveren *på som standard*.

1. På Ryzen AI Halo, åpne **AMD Ryzen™ AI Developer Center**.
2. Gå til fanen **Remote**.
3. Slå **SSH Server** på.
4. Noter **IP-adressen**, **porten** og **brukernavnet** som vises under **Server Information** — du vil lime dem inn i AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Merk:** Dette er AMD Developer Center for Windows. Linux-versjonen kan ha et annet brukergrensesnitt, men lignende ekstern funksjonalitet.

> **Tips:** AMD Sync ber om **OS-innloggingspassordet** til den brukeren, ikke et passord fra Developer Center.

---

## Trinn 2 — Installer AMD Sync på klienten din

AMD Sync kjører på Windows 11 og Linux. Last ned installasjonsprogrammet for ditt OS, og følg deretter trinnene nedenfor. Etter installasjonen klikker du **Accept & Install** på **Get Started**-skjermen — AMD Sync starter automatisk når det er ferdig.

### Windows

[Last ned AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Dobbeltklikk på `AMDSyncInstaller.exe`.
2. Klikk **Accept & Install**.

> Hvis Windows Firewall spør deg, tillat AMD Sync nettverkstilgang slik at den kan nå Ryzen AI Halo over SSH.

### Linux

Klikk på lenken for å laste ned ønsket format:

| Format | Nedlasting | Installasjonskommando |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Merk:** Ubuntu App Center kan flagge en lokalt åpnet `.deb` som *«Potensielt utrygg.»* Det er standardadvarselen for alle tredjeparts lokale installasjonsprogrammer. Hvis dobbeltklikk på `.deb` mislykkes, bruk terminalkommandoen ovenfor.

---

## Trinn 3 — Koble til Ryzen AI Halo

Ved første oppstart viser AMD Sync skjemaet **Add a Remote Device**. Fyll det ut med verdiene fra Developer Centers **Remote**-fane.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Felt | Merknader |
|-------|-------|
| **Device Name** *(valgfritt)* | En vennlig etikett som `Ryzen AI Halo`. Standard er `Device 1`, `Device 2`, … |
| **Hostname or IP** | Fra Remote-fanen |
| **SSH Port** | Fra Remote-fanen (kun tall) |
| **Username** | Ditt OS-kontonavn på Ryzen AI Halo |
| **Password** | Ditt OS-innloggingspassord — maskert mens du skriver |

Klikk **Add Device**. Etter en kort lasteskjerm vil du se **«Connection Successful»** og lande på hjemvisningen, som ligger i systemstatusfeltet. Klikk utenfor vinduet for å lukke det; AMD Sync fortsetter å kjøre og er ett klikk unna.

> **Hvis tilkoblingen mislykkes,** returnerer AMD Sync til skjemaet med verdiene dine bevart. De vanlige årsakene er at SSH er deaktivert på Ryzen AI Halo, feil passord, eller at de to enhetene er på forskjellige nettverk.

---

## Trinn 4 — Start ditt første eksterne verktøy

Hjemvisningen gir deg fem ett-klikks-komponenter — alle tilgjengelige uavhengig av hvilket OS klienten og Ryzen AI Halo kjører.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponent | Hva den gjør |
|-----------|--------------|
| **Directory** | Velger mappen på Ryzen AI Halo som VS Code, Terminal og JupyterLab vil åpne i. Standard er et administrert `Documents/AMD_Sync`-arbeidsområde. |
| **VS Code** | Åpner VS Code lokalt med en SSH-tunnel inn i den valgte mappen. |
| **Terminal** | Åpner en lokal terminal SSH-tilkoblet til Ryzen AI Halo, i den valgte mappen. |
| **JupyterLab** | Starter et notatbokprosjekt SSH-tilkoblet til Ryzen AI Halo, avgrenset til den valgte mappen. |
| **Live Metrics** | Sanntidsvisning av GPU-, minne- og CPU-utnyttelse på Ryzen AI Halo. |

### Prøv VS Code

For din første oppstart, prøv **VS Code**.

1. La **Directory** stå på standard `~/Documents/AMD_Sync`.
2. Klikk **VS Code**.
3. AMD Sync oppretter `Documents/AMD_Sync/Project_1` på Ryzen AI Halo og åpner VS Code lokalt, tunnelert inn i den.

Du redigerer nå filer som ligger på Ryzen AI Halo med ditt lokale VS Code-oppsett. Opprett `helloworld.py`, legg til `print("hello world")`, åpne den integrerte terminalen (`` Ctrl + ` ``), og kjør den:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Statuslinjen viser **SSH: Linux** — bevis på at koden din kjøres på Ryzen AI Halo, ikke laptopen din.

### Prøv terminalen

Klikk **Terminal** for å gå direkte inn i samme mappe over SSH uten å forlate tastaturet.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

På Windows er standardterminalen **PowerShell** — bytt til **Windows Command Prompt** fra Innstillinger-menyen hvis du foretrekker det. På Linux bruker AMD Sync din standard systemterminal.

---

## Slik fungerer Directory

**Directory**-nedtrekkslisten er den viktigste kontrollen i AMD Sync — den bestemmer hvor hvert verktøy du starter lander på Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (standard)** — Å starte VS Code eller JupyterLab herfra oppretter automatisk en ny prosjektmappe (`Project_1`, `Project_2`, … for VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … for JupyterLab).
- **Eksisterende prosjektmapper** — Alle direkte undermapper av `AMD_Sync` (inkludert mapper du oppretter manuelt på Ryzen AI Halo) vises i nedtrekkslisten. Den siste mappen du brukte blir standard neste gang.
- **Egendefinerte stier** — Skriv inn en absolutt sti for å åpne en mappe et annet sted på Ryzen AI Halo. AMD Sync *åpner* den bare — den vil ikke opprette mapper utenfor `AMD_Sync`, og egendefinerte stier lagres ikke mellom økter.

Hvis en egendefinert sti ikke fungerer, forteller AMD Sync deg hvorfor: ugyldig syntaks, mappen finnes ikke, eller stien peker til en fil.

---

## Live Metrics og JupyterLab

- **Live Metrics** — Et sanntids dashbord over GPU-, minne- og CPU-bruk. Den raskeste måten å bekrefte at en ekstern treningskjøring faktisk treffer maskinvaren.
- **JupyterLab** — Et fullstendig notatbokprosjekt SSH-tilkoblet til Ryzen AI Halo, med sin egen integrerte terminal for å blande notatbokceller og skallkommandoer uten å forlate brukergrensesnittet.

---

## Innstillinger og flere enheter

**Innstillinger**-menyen har tre faner:

| Fane | Hva den dekker |
|-----|----------------|
| **Devices** | Viser alle Ryzen AI Halo-enheter du har koblet til. Koble til igjen, rediger legitimasjon, eller legg til en ny enhet. |
| **Information** | Lenker til dokumentasjon og forumsupport. |
| **Customize** | Flytt appen på skrivebordet, bytt terminaltype (kun Windows), og se etter AMD Sync-oppdateringer. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Terminaltype (Windows)** — Velg mellom **PowerShell** (standard) og **Windows Command Prompt**.
- **Terminaltype (Linux)** — Kun standard systemterminal er tilgjengelig.
- **App-oppdateringer** — Denne fanen er rett sted for å se etter og installere nye AMD Sync-versjoner fra innsiden av brukergrensesnittet; ingen separat oppdateringsprogram er nødvendig.

> En enhet vises bare under **Devices** etter en vellykket første tilkobling, slik at mislykkede forsøk ikke roter til listen.

---

## Feilsøking

- **Tilkoblingen mislykkes umiddelbart** — Bekreft at SSH-serveren er aktivert på Ryzen AI Halos **Remote**-fane i Developer Center.
- **Feil passord-feil** — Bruk ditt **OS-innloggingspassord** på Ryzen AI Halo, ikke passord fra Developer Center.
- **VS Code-knappen gjør ingenting** — Installer VS Code på klientmaskinen din fra [code.visualstudio.com](https://code.visualstudio.com).
- **AMD Sync-ikonet i systemstatusfeltet mangler (Linux/GNOME)** — Installer og aktiver AppIndicator-utvidelsen.
- **`.deb` vil ikke åpne fra filbehandleren** — Bruk `sudo apt install ./AMDSyncInstaller.deb` fra en terminal.

---