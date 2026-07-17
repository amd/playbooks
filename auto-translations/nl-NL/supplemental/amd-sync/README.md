<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Externe ontwikkeling met AMD Sync

## Overzicht

**AMD Sync** maakt van uw laptop een externe cockpit voor de AMD Ryzen™ AI Halo. Sla de handmatige SSH-, sleutel- en IDE-configuratie over — installeer AMD Sync en krijg met één klik toegang tot een externe terminal, VS Code, JupyterLab en een live GPU/CPU/geheugen-dashboard op de Ryzen AI Halo.

Uw lokale machine blijft vertrouwd; elke opdracht, notebook en elk model wordt uitgevoerd op de Ryzen AI Halo.

> **Tip**: Deze pagina bevat alle nieuwe updates voor AMDSync.

## Wat u leert

- SSH inschakelen op de Ryzen AI Halo en er verbinding mee maken vanuit AMD Sync
- VS Code, Terminal, JupyterLab en Live Metrics starten op de Ryzen AI Halo met één klik
- Extern werk organiseren met behulp van de beheerde projectmappen van AMD Sync

---

## Kernconcepten

AMD Sync heeft twee kanten: een **client** (uw laptop, waarop de AMD Sync-app wordt uitgevoerd) en een **server** (de Ryzen AI Halo, waarop een SSH-server wordt uitgevoerd waarnaar AMD Sync een tunnel opzet). Alles wat u vanuit AMD Sync start — VS Code, een terminal, een notebook — wordt lokaal geopend maar uitgevoerd op de Ryzen AI Halo.

> **Ondersteunde clients:** Windows 11 en Linux. macOS wordt niet ondersteund.

---

## Stap 1 — SSH inschakelen op de Ryzen AI Halo


> **Opmerking:** Op Windows wordt de Ryzen AI Halo geleverd met de SSH-server *standaard uitgeschakeld*. Op Linux wordt deze geleverd met de SSH-server *standaard ingeschakeld*.

1. Open op de Ryzen AI Halo het **AMD Ryzen™ AI Developer Center**.
2. Ga naar het tabblad **Remote**.
3. Zet **SSH Server** aan.
4. Noteer het **IP-adres**, de **poort** en de **gebruikersnaam** die worden weergegeven onder **Serverinformatie** — u plakt deze in AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Opmerking:** Dit is het AMD Developer Center voor Windows. De Linux-versie kan een andere gebruikersinterface hebben, maar vergelijkbare externe functionaliteit.

> **Tip:** AMD Sync vraagt om het **OS-aanmeldwachtwoord** van die gebruiker, niet een wachtwoord uit het Developer Center.

---

## Stap 2 — AMD Sync installeren op uw client

AMD Sync werkt op Windows 11 en Linux. Download het installatieprogramma voor uw besturingssysteem en volg de onderstaande stappen. Klik na de installatie op **Accept & Install** op het scherm **Aan de slag** — AMD Sync wordt automatisch gestart wanneer dit is voltooid.

### Windows

[Download AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Dubbelklik op `AMDSyncInstaller.exe`.
2. Klik op **Accept & Install**.

> Als Windows Firewall u een melding geeft, sta AMD Sync netwerktoegang toe zodat het de Ryzen AI Halo via SSH kan bereiken.

### Linux

Klik op de koppeling om uw gewenste indeling te downloaden:

| Indeling | Download | Installatieopdracht |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Opmerking:** Ubuntu App Center kan een lokaal geopend `.deb`-bestand markeren als *"Mogelijk onveilig."* Dit is de standaardwaarschuwing voor elk lokaal installatieprogramma van derden. Als dubbelklikken op het `.deb`-bestand mislukt, gebruik dan de terminalopdracht hierboven.

---

## Stap 3 — Verbinding maken met uw Ryzen AI Halo

Bij de eerste keer opstarten toont AMD Sync het formulier **Een extern apparaat toevoegen**. Vul dit in met de waarden van het tabblad **Remote** in het Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Veld | Opmerkingen |
|-------|-------|
| **Apparaatnaam** *(optioneel)* | Een herkenbaar label zoals `Ryzen AI Halo`. Standaard `Device 1`, `Device 2`, … |
| **Hostnaam of IP** | Uit het tabblad Remote |
| **SSH-poort** | Uit het tabblad Remote (alleen cijfers) |
| **Gebruikersnaam** | Uw OS-accountnaam op de Ryzen AI Halo |
| **Wachtwoord** | Uw OS-aanmeldwachtwoord — gemaskeerd terwijl u typt |

Klik op **Add Device**. Na een kort laadscherm ziet u **"Connection Successful"** en komt u terecht in de startweergave, die in uw systeemvak staat. Klik buiten het venster om het te sluiten; AMD Sync blijft actief en is met één klik bereikbaar.

> **Als de verbinding mislukt,** keert AMD Sync terug naar het formulier met uw ingevulde waarden. De gebruikelijke oorzaken zijn: SSH is uitgeschakeld op de Ryzen AI Halo, het verkeerde wachtwoord, of de twee apparaten bevinden zich op verschillende netwerken.

---

## Stap 4 — Uw eerste externe tool starten

De startweergave biedt vijf componenten die met één klik te starten zijn — allemaal beschikbaar ongeacht welk besturingssysteem de client en de Ryzen AI Halo gebruiken.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Component | Wat het doet |
|-----------|--------------|
| **Directory** | Kiest de map op de Ryzen AI Halo waarin VS Code, Terminal en JupyterLab worden geopend. Standaard een beheerde `Documents/AMD_Sync`-werkruimte. |
| **VS Code** | Opent VS Code lokaal met een SSH-tunnel naar de geselecteerde map. |
| **Terminal** | Opent een lokale terminal die via SSH is verbonden met de Ryzen AI Halo, in de geselecteerde map. |
| **JupyterLab** | Start een notebookproject dat via SSH is verbonden met de Ryzen AI Halo, beperkt tot de geselecteerde map. |
| **Live Metrics** | Realtime weergave van GPU-, geheugen- en CPU-gebruik op de Ryzen AI Halo. |

### VS Code uitproberen

Probeer voor uw eerste keer **VS Code**.

1. Laat **Directory** op de standaardwaarde `~/Documents/AMD_Sync` staan.
2. Klik op **VS Code**.
3. AMD Sync maakt `Documents/AMD_Sync/Project_1` aan op de Ryzen AI Halo en opent VS Code lokaal, getunneld daarnaar toe.

U bewerkt nu bestanden die op de Ryzen AI Halo staan met uw lokale VS Code-configuratie. Maak `helloworld.py` aan, voeg `print("hello world")` toe, open de geïntegreerde terminal (`` Ctrl + ` ``), en voer het uit:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

De statusbalk toont **SSH: Linux** — bewijs dat uw code wordt uitgevoerd op de Ryzen AI Halo, niet op uw laptop.

### De Terminal uitproberen

Klik op **Terminal** om via SSH in dezelfde map te komen zonder het toetsenbord te verlaten.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Op Windows is de standaardterminal **PowerShell** — schakel over naar **Windows Command Prompt** via het menu Instellingen als u dat prefereert. Op Linux gebruikt AMD Sync uw standaard systeemterminal.

---

## Hoe de Directory werkt

Het **Directory**-vervolgkeuzemenu is de belangrijkste instelling in AMD Sync — het bepaalt waar elke tool die u start terechtkomt op de Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (standaard)** — Als u VS Code of JupyterLab van hieruit start, wordt automatisch een nieuwe projectmap aangemaakt (`Project_1`, `Project_2`, … voor VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … voor JupyterLab).
- **Bestaande projectmappen** — Elke directe onderliggende map van `AMD_Sync` (inclusief mappen die u handmatig op de Ryzen AI Halo aanmaakt) verschijnt in het vervolgkeuzemenu. De laatste map die u hebt gebruikt, wordt de volgende keer de standaard.
- **Aangepaste paden** — Typ een absoluut pad om een map elders op de Ryzen AI Halo te openen. AMD Sync *opent* deze alleen — het maakt geen mappen aan buiten `AMD_Sync`, en aangepaste paden worden niet opgeslagen tussen sessies.

Als een aangepast pad niet werkt, vertelt AMD Sync u waarom: ongeldige syntaxis, map bestaat niet, of het pad verwijst naar een bestand.

---

## Live Metrics en JupyterLab

- **Live Metrics** — Een live dashboard van GPU-, geheugen- en CPU-gebruik. De snelste manier om te bevestigen dat een externe trainingsrun daadwerkelijk de hardware gebruikt.
- **JupyterLab** — Een volledig notebookproject dat via SSH is verbonden met de Ryzen AI Halo, met een eigen geïntegreerde terminal voor het combineren van notebookcellen en shell-opdrachten zonder de gebruikersinterface te verlaten.

---

## Instellingen en meerdere apparaten

Het menu **Instellingen** heeft drie tabbladen:

| Tabblad | Wat het omvat |
|-----|----------------|
| **Devices** | Toont elke Ryzen AI Halo waarmee u succesvol verbinding hebt gemaakt. Opnieuw verbinden, inloggegevens bewerken of een nieuw apparaat toevoegen. |
| **Information** | Koppelingen naar documentatie en forumondersteuning. |
| **Customize** | De app herpositioneren op uw bureaublad, het terminaltype wijzigen (alleen Windows) en controleren op AMD Sync-updates. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Terminaltype (Windows)** — Kies tussen **PowerShell** (standaard) en **Windows Command Prompt**.
- **Terminaltype (Linux)** — Alleen de standaard systeemterminal is beschikbaar.
- **App-updates** — Dit tabblad is de juiste plek om nieuwe AMD Sync-versies te controleren en te installeren vanuit de gebruikersinterface; er is geen afzonderlijk updateprogramma nodig.

> Een apparaat verschijnt pas onder **Devices** na een succesvolle eerste verbinding, zodat mislukte pogingen de lijst niet vervuilen.

---

## Probleemoplossing

- **Verbinding mislukt onmiddellijk** — Controleer of de SSH-server is ingeschakeld op het tabblad **Remote** van de Ryzen AI Halo in het Developer Center.
- **Fout: verkeerd wachtwoord** — Gebruik uw **OS-aanmeldwachtwoord** op de Ryzen AI Halo, niet wachtwoorden uit het Developer Center.
- **VS Code-knop doet niets** — Installeer VS Code op uw clientmachine via [code.visualstudio.com](https://code.visualstudio.com).
- **AMD Sync-systeemvakpictogram ontbreekt (Linux/GNOME)** — Installeer en schakel de AppIndicator-extensie in.
- **`.deb` wordt niet geopend vanuit de bestandsbeheerder** — Gebruik `sudo apt install ./AMDSyncInstaller.deb` vanuit een terminal.

---