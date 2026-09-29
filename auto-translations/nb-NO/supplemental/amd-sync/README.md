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

# Ekstern utvikling med AMD Sync

## Oversikt

**AMD Sync** gjør bærbaren din om til en ekstern kommandosentral for AMD Ryzen™ AI Halo. Hopp over manuell SSH-, nøkkel- og IDE-oppsett — installer AMD Sync og få ett-klikks tilgang til en ekstern terminal, VS Code, JupyterLab og et sanntids GPU-/CPU-/minne-dashbord på Ryzen AI Halo.

Den lokale maskinen din forblir kjent; hver kommando, notatbok og modell kjører på Ryzen AI Halo.

> **Tips**: Denne siden vil inneholde eventuelle nye oppdateringer til AMDSync. 

## Hva du vil lære

- Aktivere SSH på Ryzen AI Halo og koble til den fra AMD Sync
- Starte VS Code, Terminal, JupyterLab og Live Metrics mot Ryzen AI Halo med ett klikk
- Organisere eksternt arbeid ved hjelp av AMD Syncs administrerte prosjektmapper

---

## Kjernebegreper

AMD Sync har to sider: en **klient** (den bærbare maskinen din, som kjører AMD Sync-appen) og en **server** (Ryzen AI Halo, som kjører en SSH-server som AMD Sync tunnellerer inn i). Alt du starter fra AMD Sync — VS Code, en terminal, en notatbok — åpnes lokalt, men kjøres på Ryzen AI Halo.

> **Støttede klienter:** Windows 11 og Linux. macOS støttes ikke.

---

## Trinn 1 — Aktiver SSH på Ryzen AI Halo


> **Merk:** På Windows leveres Ryzen AI Halo med SSH-serveren *avslått som standard*. På Linux leveres den med SSH-serveren *påslått som standard*.

1. Åpne **AMD Ryzen™ AI Developer Center** på Ryzen AI Halo.
2. Gå til fanen **Remote**.
3. Slå på **SSH Server**.
4. Noter **IP Address**, **Port** og **Username** som vises under **Server Information** — du limer disse inn i AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Merk:** Dette er AMD Developer Center for Windows. Linux-versjonen kan ha et annet brukergrensesnitt, men lignende ekstern funksjonalitet.

> **Tips:** AMD Sync ber om **OS-innloggingspassordet** for denne brukeren, ikke et passord fra Developer Center.

---

## Trinn 2 — Installer AMD Sync på klienten din

AMD Sync kjører på Windows 11 og Linux. Last ned installasjonsprogrammet for operativsystemet ditt, og følg trinnene nedenfor. Etter installasjonen klikker du på **Accept & Install** på **Get Started**-skjermen — AMD Sync starter automatisk når den er ferdig.

### Windows

[Last ned AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Dobbeltklikk på `AMDSyncInstaller.exe`.
2. Klikk på **Accept & Install**.

> Hvis Windows-brannmuren spør deg, tillat nettverkstilgang for AMD Sync slik at den kan nå Ryzen AI Halo over SSH.

### Linux

Klikk på lenken for å laste ned foretrukket format:

| Format | Nedlasting | Installasjonskommando |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Merk:** Ubuntu App Center kan flagge en lokalt åpnet `.deb`-fil som *"Potentielt utrygg."* Dette er standardadvarselen for ethvert tredjeparts lokalt installasjonsprogram. Hvis dobbeltklikk på `.deb`-filen mislykkes, bruk terminalkommandoen ovenfor.

---

## Trinn 3 — Koble til Ryzen AI Halo

Ved første oppstart viser AMD Sync skjemaet **Add a Remote Device**. Fyll det ut med verdiene fra fanen **Remote** i Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Felt | Merknader |
|-------|-------|
| **Device Name** *(valgfritt)* | En vennlig etikett som `Ryzen AI Halo`. Standard er `Device 1`, `Device 2`, … |
| **Hostname or IP** | Fra Remote-fanen |
| **SSH Port** | Fra Remote-fanen (kun tall) |
| **Username** | Din OS-kontonavn på Ryzen AI Halo |
| **Password** | Ditt OS-innloggingspassord — maskert mens du skriver |

Klikk på **Add Device**. Etter en kort lastskjerm ser du **"Connection Successful"** og havner på hjemvisningen, som ligger i systemstatusfeltet ditt. Klikk utenfor vinduet for å lukke det; AMD Sync fortsetter å kjøre og er ett klikk unna.

> **Hvis tilkoblingen mislykkes,** går AMD Sync tilbake til skjemaet med verdiene dine bevart. De vanlige årsakene er at SSH er deaktivert på Ryzen AI Halo, feil passord, eller at de to enhetene er på forskjellige nettverk.

---

## Trinn 4 — Start ditt første eksterne verktøy

Hjemvisningen gir deg fem ett-klikks-komponenter — alle tilgjengelige uavhengig av hvilket operativsystem klienten og Ryzen AI Halo kjører.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponent | Hva den gjør |
|-----------|--------------|
| **Directory** | Velger mappen på Ryzen AI Halo som VS Code, Terminal og JupyterLab vil åpnes i. Standard er en administrert `Documents/AMD_Sync`-arbeidsflate. |
| **VS Code** | Åpner VS Code lokalt med en SSH-tunnel inn i den valgte mappen. |
| **Terminal** | Åpner en lokal terminal SSH-tilkoblet til Ryzen AI Halo, i den valgte mappen. |
| **JupyterLab** | Starter et notatbokprosjekt SSH-tilkoblet til Ryzen AI Halo, begrenset til den valgte mappen. |
| **Live Metrics** | Sanntidsvisning av GPU-, minne- og CPU-utnyttelse på Ryzen AI Halo. |

### Prøv VS Code

For din første oppstart, prøv **VS Code**.

1. La **Directory** stå på standardverdien `~/Documents/AMD_Sync`.
2. Klikk på **VS Code**.
3. AMD Sync oppretter `Documents/AMD_Sync/Project_1` på Ryzen AI Halo og åpner VS Code lokalt, tunnellert inn i den.

Du redigerer nå filer som ligger på Ryzen AI Halo med ditt lokale VS Code-oppsett. Opprett `helloworld.py`, legg til `print("hello world")`, åpne den integrerte terminalen (`` Ctrl + ` ``), og kjør den:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Statuslinjen viser **SSH: Linux** — beviset på at koden din kjører på Ryzen AI Halo, ikke på den bærbare maskinen din.
### Prøv terminalen

Klikk på **Terminal** for å gå inn i den samme mappen over SSH uten å forlate tastaturet.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

På Windows er standardterminalen **PowerShell** — bytt til **Windows Command Prompt** fra Innstillinger-menyen hvis du foretrekker det. På Linux bruker AMD Sync systemets standardterminal.

---

## Slik fungerer katalogen

Nedtrekksmenyen **Directory** er den viktigste enkeltkontrollen i AMD Sync — den bestemmer hvor hvert verktøy du starter, havner på Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (standard)** — Å starte VS Code eller JupyterLab herfra oppretter automatisk en ny prosjektmappe (`Project_1`, `Project_2`, … for VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … for JupyterLab).
- **Eksisterende prosjektmapper** — Enhver direkte undermappe av `AMD_Sync` (inkludert mapper du oppretter manuelt på Ryzen AI Halo) vises i nedtrekksmenyen. Den sist brukte mappen blir standardvalget neste gang.
- **Egendefinerte stier** — Skriv inn en absolutt sti for å åpne en mappe et annet sted på Ryzen AI Halo. AMD Sync *åpner* den bare — den vil ikke opprette mapper utenfor `AMD_Sync`, og egendefinerte stier lagres ikke mellom økter.

Hvis en egendefinert sti ikke fungerer, forteller AMD Sync deg hvorfor: ugyldig syntaks, mappen finnes ikke, eller stien peker til en fil.

---

## Live Metrics og JupyterLab

- **Live Metrics** — Et sanntidsdashbord for GPU-, minne- og CPU-bruk. Den raskeste måten å bekrefte at en ekstern treningskjøring faktisk belaster maskinvaren.
- **JupyterLab** — Et fullt notebook-prosjekt SSH-tilkoblet til Ryzen AI Halo, med sin egen integrerte terminal for å blande notebook-celler og skallkommandoer uten å forlate brukergrensesnittet.

---

## Innstillinger og flere enheter

Menyen **Settings** har tre faner:

| Fane | Hva den dekker |
|-----|----------------|
| **Devices** | Viser alle Ryzen AI Halo-enheter du har koblet til med suksess. Koble til på nytt, rediger legitimasjon, eller legg til en ny enhet. |
| **Information** | Lenker til dokumentasjon og forumstøtte. |
| **Customize** | Flytt appen på skrivebordet, bytt terminaltype (kun Windows), og se etter oppdateringer til AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Terminaltype (Windows)** — Velg mellom **PowerShell** (standard) og **Windows Command Prompt**.
- **Terminaltype (Linux)** — Kun systemets standardterminal er tilgjengelig.
- **Appoppdateringer** — Denne fanen er rett sted for å se etter og installere nye versjoner av AMD Sync fra selve grensesnittet; ingen separat oppdateringsverktøy trengs.

> En enhet vises kun under **Devices** etter en vellykket første tilkobling, så mislykkede forsøk vil ikke rote til listen.

---

## Feilsøking

- **Tilkoblingen mislykkes umiddelbart** — Bekreft at SSH-serveren er aktivert på **Remote**-fanen i Developer Center på Ryzen AI Halo.
- **Feil passord-feil** — Bruk ditt **OS-innloggingspassord** på Ryzen AI Halo, ikke passord hentet fra Developer Center.
- **VS Code-knappen gjør ingenting** — Installer VS Code på klientmaskinen din fra [code.visualstudio.com](https://code.visualstudio.com).
- **AMD Sync-ikonet i systemstatusfeltet mangler (Linux/GNOME)** — Installer og aktiver AppIndicator-utvidelsen.
- **`.deb`-filen åpnes ikke fra filbehandleren** — Bruk `sudo apt install ./AMDSyncInstaller.deb` fra en terminal.
- **Oppsettet dukker opp igjen ved hver oppstart (Linux)**: lås opp innloggingsnøkkelringen din, eller start med `--password-store=gnome-libsecret`, og gjør deretter oppsettet på nytt én gang.

---