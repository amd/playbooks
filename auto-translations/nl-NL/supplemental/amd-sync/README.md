<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Machinevertaling.** Deze pagina is automatisch vertaald vanuit het Engels en is niet door een mens gecontroleerd. Deze pagina kan fouten bevatten en bepaalde instructies, opdrachten, downloads, productbeschikbaarheid of andere inhoud kan per taal of regio verschillen. In geval van tegenstrijdigheid of discrepantie is de oorspronkelijke Engelse versie van de playbook doorslaggevend en prevaleert deze.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Remote ontwikkelen met AMD Sync

## Overzicht

**AMD Sync** verandert je laptop in een remote cockpit voor de AMD Ryzen™ AI Halo. Sla de handmatige SSH-, sleutel- en IDE-instellingen over — installeer AMD Sync en krijg met één klik toegang tot een remote terminal, VS Code, JupyterLab en een live GPU/CPU/geheugendashboard op de Ryzen AI Halo.

Je lokale machine blijft vertrouwd; elk commando, elke notebook en elk model draait op de Ryzen AI Halo.

> **Tip**: Deze pagina bevat alle nieuwe updates voor AMDSync.

## Wat je gaat leren

- SSH inschakelen op de Ryzen AI Halo en er vanuit AMD Sync verbinding mee maken
- VS Code, Terminal, JupyterLab en Live Metrics met één klik starten tegen de Ryzen AI Halo
- Remote werk organiseren met de beheerde projectmappen van AMD Sync

---

## Kernconcepten

AMD Sync heeft twee kanten: een **client** (je laptop, waarop de AMD Sync-app draait) en een **server** (de Ryzen AI Halo, waarop een SSH-server draait waar AMD Sync een tunnel naartoe maakt). Alles wat je vanuit AMD Sync start — VS Code, een terminal, een notebook — opent lokaal maar wordt uitgevoerd op de Ryzen AI Halo.

> **Ondersteunde clients:** Windows 11 en Linux. macOS wordt niet ondersteund.

---

## Stap 1 — SSH inschakelen op de Ryzen AI Halo


> **Opmerking:** Op Windows wordt de Ryzen AI Halo geleverd met de SSH-server *standaard uitgeschakeld*. Op Linux wordt deze geleverd met de SSH-server *standaard ingeschakeld*.

1. Open op de Ryzen AI Halo het **AMD Ryzen™ AI Developer Center**.
2. Ga naar het tabblad **Remote**.
3. Schakel **SSH Server** in.
4. Noteer het **IP-adres**, de **Poort** en de **Gebruikersnaam** die worden weergegeven onder **Server Information** — je plakt deze straks in AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Opmerking:** Dit is het AMD Developer Center voor Windows. Die voor Linux kan een andere UI hebben, maar met vergelijkbare remote functionaliteit.

> **Tip:** AMD Sync vraagt om het **OS-inlogwachtwoord** van die gebruiker, niet om een wachtwoord uit het Developer Center.

---

## Stap 2 — AMD Sync installeren op je client

AMD Sync draait op Windows 11 en Linux. Download het installatieprogramma voor jouw besturingssysteem en volg de onderstaande stappen. Klik na de installatie op **Accept & Install** op het scherm **Get Started** — AMD Sync wordt automatisch gestart zodra dit klaar is.

### Windows

[Download AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Dubbelklik op `AMDSyncInstaller.exe`.
2. Klik op **Accept & Install**.

> Als Windows Firewall om toestemming vraagt, sta dan netwerktoegang voor AMD Sync toe, zodat het de Ryzen AI Halo via SSH kan bereiken.

### Linux

Klik op de link om je gewenste formaat te downloaden:

| Formaat | Download | Installatiecommando |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Opmerking:** Het Ubuntu App Center kan een lokaal geopend `.deb`-bestand markeren als *"Potentially unsafe."* Dit is de standaardwaarschuwing voor elk lokaal installatieprogramma van derden. Als dubbelklikken op het `.deb`-bestand niet werkt, gebruik dan het bovenstaande terminalcommando.

---

## Stap 3 — Verbinding maken met je Ryzen AI Halo

Bij de eerste keer opstarten toont AMD Sync het formulier **Add a Remote Device**. Vul dit in met de waarden van het tabblad **Remote** in het Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Veld | Opmerkingen |
|-------|-------|
| **Device Name** *(optioneel)* | Een herkenbaar label zoals `Ryzen AI Halo`. Standaard `Device 1`, `Device 2`, … |
| **Hostname or IP** | Van het tabblad Remote |
| **SSH Port** | Van het tabblad Remote (alleen cijfers) |
| **Username** | Je OS-accountnaam op de Ryzen AI Halo |
| **Password** | Je OS-inlogwachtwoord — gemaskeerd terwijl je typt |

Klik op **Add Device**. Na een kort laadscherm zie je **"Connection Successful"** en kom je terecht op de startweergave, die zich in je systeemvak bevindt. Klik buiten het venster om het te sluiten; AMD Sync blijft actief en is één klik verwijderd.

> **Als de verbinding mislukt,** keert AMD Sync terug naar het formulier met je waarden behouden. De gebruikelijke oorzaken zijn dat SSH is uitgeschakeld op de Ryzen AI Halo, een verkeerd wachtwoord, of de twee apparaten die zich op verschillende netwerken bevinden.

---

## Stap 4 — Je eerste remote tool starten

De startweergave biedt je vijf onderdelen die met één klik te starten zijn — allemaal beschikbaar, ongeacht op welk besturingssysteem de client en de Ryzen AI Halo draaien.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Onderdeel | Wat het doet |
|-----------|--------------|
| **Directory** | Kiest de map op de Ryzen AI Halo waarin VS Code, Terminal en JupyterLab worden geopend. Standaard een beheerde `Documents/AMD_Sync`-werkruimte. |
| **VS Code** | Opent VS Code lokaal met een SSH-tunnel naar de geselecteerde map. |
| **Terminal** | Opent een lokale terminal die via SSH is verbonden met de Ryzen AI Halo, in de geselecteerde map. |
| **JupyterLab** | Start een notebookproject dat via SSH is verbonden met de Ryzen AI Halo, beperkt tot de geselecteerde map. |
| **Live Metrics** | Realtime overzicht van GPU-, geheugen- en CPU-gebruik op de Ryzen AI Halo. |

### Probeer VS Code

Probeer voor je eerste keer starten **VS Code**.

1. Laat **Directory** op de standaardwaarde `~/Documents/AMD_Sync` staan.
2. Klik op **VS Code**.
3. AMD Sync maakt `Documents/AMD_Sync/Project_1` aan op de Ryzen AI Halo en opent VS Code lokaal, getunneld daarnaartoe.

Je bewerkt nu bestanden die op de Ryzen AI Halo staan met je lokale VS Code-instellingen. Maak `helloworld.py` aan, voeg `print("hello world")` toe, open de geïntegreerde terminal (`` Ctrl + ` ``) en voer het uit:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

De statusbalk toont **SSH: Linux** — het bewijs dat je code draait op de Ryzen AI Halo, niet op je laptop.
### Probeer de Terminal

Klik op **Terminal** om via SSH naar dezelfde map te gaan, zonder het toetsenbord los te laten.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Op Windows is de standaardterminal **PowerShell** — schakel over naar **Windows Command Prompt** via het Instellingenmenu als je dat liever hebt. Op Linux gebruikt AMD Sync je standaard systeemterminal.

---

## Hoe de Directory werkt

De vervolgkeuzelijst **Directory** is het belangrijkste bedieningselement in AMD Sync — deze bepaalt waar elke tool die je start, terechtkomt op de Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (standaard)** — Het starten van VS Code of JupyterLab vanuit deze map maakt automatisch een nieuwe projectmap aan (`Project_1`, `Project_2`, … voor VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … voor JupyterLab).
- **Bestaande projectmappen** — Elke directe submap van `AMD_Sync` (inclusief mappen die je handmatig aanmaakt op de Ryzen AI Halo) verschijnt in de vervolgkeuzelijst. De laatst gebruikte map wordt de volgende keer de standaardmap.
- **Aangepaste paden** — Typ een absoluut pad om een map elders op de Ryzen AI Halo te openen. AMD Sync *opent* deze map alleen — het maakt geen mappen aan buiten `AMD_Sync`, en aangepaste paden worden niet tussen sessies onthouden.

Als een aangepast pad niet werkt, vertelt AMD Sync je waarom: ongeldige syntax, de map bestaat niet, of het pad verwijst naar een bestand.

---

## Live-metingen en JupyterLab

- **Live-metingen** — Een live-dashboard van GPU-, geheugen- en CPU-gebruik. De snelste manier om te bevestigen dat een externe trainingsrun daadwerkelijk gebruikmaakt van de hardware.
- **JupyterLab** — Een volledig notebookproject dat via SSH is verbonden met de Ryzen AI Halo, met een eigen geïntegreerde terminal om notebookcellen en shellopdrachten te combineren zonder de UI te verlaten.

---

## Instellingen en meerdere apparaten

Het menu **Instellingen** heeft drie tabbladen:

| Tabblad | Wat het omvat |
|-----|----------------|
| **Apparaten** | Toont elke Ryzen AI Halo waarmee je succesvol verbinding hebt gemaakt. Opnieuw verbinden, inloggegevens bewerken of een nieuw apparaat toevoegen. |
| **Informatie** | Links naar documentatie en forumondersteuning. |
| **Aanpassen** | Verplaats de app op je bureaublad, wissel het terminaltype (alleen Windows) en controleer op AMD Sync-updates. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Terminaltype (Windows)** — Kies tussen **PowerShell** (standaard) en **Windows Command Prompt**.
- **Terminaltype (Linux)** — Alleen de standaard systeemterminal is beschikbaar.
- **App-updates** — Dit tabblad is de juiste plek om vanuit de UI te controleren op en nieuwe AMD Sync-versies te installeren; er is geen aparte updater nodig.

> Een apparaat verschijnt pas onder **Apparaten** na een succesvolle eerste verbinding, zodat mislukte pogingen de lijst niet vervuilen.

---

## Probleemoplossing

- **Verbinding mislukt onmiddellijk** — Controleer of de SSH-server is ingeschakeld op het tabblad **Remote** van de Ryzen AI Halo in het Developer Center.
- **Foutmelding verkeerd wachtwoord** — Gebruik je **OS-inlogwachtwoord** op de Ryzen AI Halo, niet wachtwoorden uit het Developer Center.
- **VS Code-knop doet niets** — Installeer VS Code op je clientcomputer via [code.visualstudio.com](https://code.visualstudio.com).
- **AMD Sync-systeemvakpictogram ontbreekt (Linux/GNOME)** — Installeer en schakel de AppIndicator-extensie in.
- **`.deb` opent niet vanuit de bestandsbeheerder** — Gebruik `sudo apt install ./AMDSyncInstaller.deb` vanuit een terminal.

---