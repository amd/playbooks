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

# Externe ontwikkeling met AMD Sync

## Overzicht

**AMD Sync** verandert je laptop in een externe cockpit voor de AMD Ryzen™ AI Halo. Sla de handmatige SSH-, sleutel- en IDE-configuratie over — installeer AMD Sync en krijg met één klik toegang tot een externe terminal, VS Code, JupyterLab en een live GPU/CPU/geheugendashboard op de Ryzen AI Halo.

Je lokale machine blijft vertrouwd; elk commando, elke notebook en elk model draait op de Ryzen AI Halo.

> **Tip**: Deze pagina zal alle nieuwe updates voor AMDSync bevatten. 

## Wat je zult leren

- SSH inschakelen op de Ryzen AI Halo en er verbinding mee maken vanuit AMD Sync
- VS Code, Terminal, JupyterLab en Live Metrics met één klik starten tegen de Ryzen AI Halo
- Extern werk organiseren met de beheerde projectmappen van AMD Sync

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
4. Noteer het **IP-adres**, de **poort** en de **gebruikersnaam** die worden weergegeven onder **Server Information** — je plakt deze zo in AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Opmerking:** Dit is het AMD Developer Center voor Windows. Het Linux-exemplaar kan een andere interface hebben, maar biedt vergelijkbare externe functionaliteit.

> **Tip:** AMD Sync vraagt om het **besturingssysteem-inlogwachtwoord** van die gebruiker, niet om een wachtwoord uit het Developer Center.

---

## Stap 2 — AMD Sync installeren op je client

AMD Sync draait op Windows 11 en Linux. Download het installatieprogramma voor jouw besturingssysteem en volg de onderstaande stappen. Klik na de installatie op **Accept & Install** op het scherm **Get Started** — AMD Sync start automatisch zodra dit is voltooid.

### Windows

[Download AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Dubbelklik op `AMDSyncInstaller.exe`.
2. Klik op **Accept & Install**.

> Als de Windows Firewall om toestemming vraagt, sta dan netwerktoegang toe voor AMD Sync zodat het via SSH de Ryzen AI Halo kan bereiken.

### Linux

Klik op de link om je gewenste formaat te downloaden:

| Formaat | Download | Installatiecommando |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Opmerking:** Ubuntu App Center kan een lokaal geopend `.deb`-bestand markeren als *"Potentieel onveilig."* Dit is de standaardwaarschuwing voor elk lokaal installatieprogramma van derden. Als dubbelklikken op het `.deb`-bestand niet werkt, gebruik dan het bovenstaande terminalcommando.

---

## Stap 3 — Verbinding maken met je Ryzen AI Halo

Bij het eerste opstarten toont AMD Sync het formulier **Add a Remote Device**. Vul dit in met de waarden van het tabblad **Remote** in het Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Veld | Opmerkingen |
|-------|-------|
| **Apparaatnaam** *(optioneel)* | Een herkenbaar label zoals `Ryzen AI Halo`. Standaard is `Device 1`, `Device 2`, … |
| **Hostnaam of IP** | Van het tabblad Remote |
| **SSH-poort** | Van het tabblad Remote (alleen cijfers) |
| **Gebruikersnaam** | Je besturingssysteemaccountnaam op de Ryzen AI Halo |
| **Wachtwoord** | Je besturingssysteem-inlogwachtwoord — gemaskeerd tijdens het typen |

Klik op **Add Device**. Na een kort laadscherm zie je **"Connection Successful"** en kom je op het startscherm terecht, dat zich in je systeemvak bevindt. Klik naast het venster om het te sluiten; AMD Sync blijft actief en is één klik verwijderd.

> **Als de verbinding mislukt,** keert AMD Sync terug naar het formulier met je waarden bewaard. De gebruikelijke oorzaken zijn dat SSH is uitgeschakeld op de Ryzen AI Halo, een verkeerd wachtwoord, of dat de twee apparaten zich op verschillende netwerken bevinden.

---

## Stap 4 — Start je eerste externe tool

Het startscherm biedt vijf componenten met één klik — allemaal beschikbaar ongeacht welk besturingssysteem de client en de Ryzen AI Halo draaien.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Component | Wat het doet |
|-----------|--------------|
| **Directory** | Kiest de map op de Ryzen AI Halo waarin VS Code, Terminal en JupyterLab zullen openen. Standaard is een beheerde `Documents/AMD_Sync`-werkruimte. |
| **VS Code** | Opent VS Code lokaal met een SSH-tunnel naar de geselecteerde map. |
| **Terminal** | Opent een lokale terminal met een SSH-verbinding naar de Ryzen AI Halo, in de geselecteerde map. |
| **JupyterLab** | Start een notebookproject met een SSH-verbinding naar de Ryzen AI Halo, beperkt tot de geselecteerde map. |
| **Live Metrics** | Weergave in real time van GPU-, geheugen- en CPU-gebruik op de Ryzen AI Halo. |

### Probeer VS Code

Probeer voor je eerste keer opstarten **VS Code**.

1. Laat **Directory** op de standaardwaarde `~/Documents/AMD_Sync` staan.
2. Klik op **VS Code**.
3. AMD Sync maakt `Documents/AMD_Sync/Project_1` aan op de Ryzen AI Halo en opent VS Code lokaal, getunneld daarheen.

Je bewerkt nu bestanden die zich op de Ryzen AI Halo bevinden met je lokale VS Code-installatie. Maak `helloworld.py` aan, voeg `print("hello world")` toe, open de geïntegreerde terminal (`` Ctrl + ` ``) en voer het uit:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

De statusbalk toont **SSH: Linux** — het bewijs dat je code op de Ryzen AI Halo draait, niet op je laptop.
### Probeer de Terminal

Klik op **Terminal** om via SSH in dezelfde map te komen zonder het toetsenbord los te laten.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Op Windows is de standaardterminal **PowerShell** — schakel over naar **Windows Command Prompt** vanuit het Instellingenmenu als u dat liever heeft. Op Linux gebruikt AMD Sync uw standaard systeemterminal.

---

## Hoe de Directory werkt

De vervolgkeuzelijst **Directory** is de belangrijkste besturingselement in AMD Sync — deze bepaalt waar elke tool die u start terechtkomt op de Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (standaard)** — Het starten van VS Code of JupyterLab vanaf hier maakt automatisch een nieuwe projectmap aan (`Project_1`, `Project_2`, … voor VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … voor JupyterLab).
- **Bestaande projectmappen** — Elke directe submap van `AMD_Sync` (inclusief mappen die u handmatig aanmaakt op de Ryzen AI Halo) verschijnt in de vervolgkeuzelijst. De laatst gebruikte map wordt de volgende keer de standaardwaarde.
- **Aangepaste paden** — Typ een absoluut pad om een map elders op de Ryzen AI Halo te openen. AMD Sync *opent* deze alleen — het maakt geen mappen aan buiten `AMD_Sync`, en aangepaste paden worden niet bewaard tussen sessies.

Als een aangepast pad niet werkt, vertelt AMD Sync u waarom: ongeldige syntaxis, de map bestaat niet, of het pad verwijst naar een bestand.

---

## Live Metrics en JupyterLab

- **Live Metrics** — Een live dashboard van GPU-, geheugen- en CPU-gebruik. De snelste manier om te bevestigen dat een externe trainingsrun daadwerkelijk gebruikmaakt van de hardware.
- **JupyterLab** — Een volledig notebookproject dat via SSH is verbonden met de Ryzen AI Halo, met een eigen geïntegreerde terminal om notebookcellen en shellcommando's te combineren zonder de UI te verlaten.

---

## Instellingen en meerdere apparaten

Het menu **Instellingen** heeft drie tabbladen:

| Tabblad | Wat het bevat |
|-----|----------------|
| **Devices** | Toont elke Ryzen AI Halo waarmee u succesvol verbinding heeft gemaakt. Opnieuw verbinden, inloggegevens bewerken of een nieuw apparaat toevoegen. |
| **Information** | Links naar documentatie en forumondersteuning. |
| **Customize** | Verplaats de app op uw bureaublad, wissel het terminaltype (alleen Windows), en controleer op updates voor AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Terminaltype (Windows)** — Kies tussen **PowerShell** (standaard) en **Windows Command Prompt**.
- **Terminaltype (Linux)** — Alleen de standaard systeemterminal is beschikbaar.
- **App-updates** — Dit tabblad is de juiste plek om te controleren op en nieuwe versies van AMD Sync te installeren vanuit de UI; er is geen aparte updater nodig.

> Een apparaat verschijnt pas onder **Devices** na een succesvolle eerste verbinding, zodat mislukte pogingen de lijst niet vervuilen.

---

## Probleemoplossing

- **Verbinding mislukt onmiddellijk** — Controleer of de SSH-server is ingeschakeld op het tabblad **Remote** van de Ryzen AI Halo in het Developer Center.
- **Foutmelding verkeerd wachtwoord** — Gebruik uw **OS-inlogwachtwoord** op de Ryzen AI Halo, niet wachtwoorden uit het Developer Center.
- **VS Code-knop doet niets** — Installeer VS Code op uw clientmachine vanaf [code.visualstudio.com](https://code.visualstudio.com).
- **AMD Sync-taakbalkpictogram ontbreekt (Linux/GNOME)** — Installeer en schakel de AppIndicator-extensie in.
- **`.deb` opent niet vanuit de bestandsbeheerder** — Gebruik `sudo apt install ./AMDSyncInstaller.deb` vanuit een terminal.
- **Installatie verschijnt telkens opnieuw bij het opstarten (Linux)**: ontgrendel uw inlog-sleutelbos, of start op met `--password-store=gnome-libsecret`, en voer de installatie daarna eenmalig opnieuw uit.

---