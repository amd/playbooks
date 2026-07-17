<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Fjärrutveckling med AMD Sync

## Översikt

**AMD Sync** förvandlar din bärbara dator till en fjärrkontroll för AMD Ryzen™ AI Halo. Hoppa över manuell SSH-, nyckel- och IDE-konfiguration — installera AMD Sync och få enklicksåtkomst till en fjärrterminal, VS Code, JupyterLab och en live-instrumentpanel för GPU/CPU/minne på Ryzen AI Halo.

Din lokala maskin förblir bekant; varje kommando, anteckningsbok och modell körs på Ryzen AI Halo.

> **Tips**: Den här sidan kommer att innehålla alla nya uppdateringar till AMDSync.

## Vad du kommer att lära dig

- Aktivera SSH på Ryzen AI Halo och ansluta till den från AMD Sync
- Starta VS Code, Terminal, JupyterLab och Live Metrics mot Ryzen AI Halo med ett klick
- Organisera fjärrarbete med AMD Syncs hanterade projektmappar

---

## Grundläggande begrepp

AMD Sync har två sidor: en **klient** (din bärbara dator, som kör AMD Sync-appen) och en **server** (Ryzen AI Halo, som kör en SSH-server som AMD Sync tunnlar in i). Allt du startar från AMD Sync — VS Code, en terminal, en anteckningsbok — öppnas lokalt men körs på Ryzen AI Halo.

> **Klienter som stöds:** Windows 11 och Linux. macOS stöds inte.

---

## Steg 1 — Aktivera SSH på Ryzen AI Halo


> **Obs:** På Windows levereras Ryzen AI Halo med SSH-servern *avstängd som standard*. På Linux levereras den med SSH-servern *påslagen som standard*.

1. På Ryzen AI Halo, öppna **AMD Ryzen™ AI Developer Center**.
2. Gå till fliken **Remote**.
3. Slå på **SSH Server**.
4. Notera **IP-adressen**, **porten** och **användarnamnet** som visas under **Server Information** — du klistrar in dem i AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Obs:** Detta är AMD Developer Center för Windows. Linux-versionen kan ha ett annat gränssnitt, men liknande fjärrfunktionalitet.

> **Tips:** AMD Sync frågar efter **OS-inloggningslösenordet** för den användaren, inte ett lösenord från Developer Center.

---

## Steg 2 — Installera AMD Sync på din klient

AMD Sync körs på Windows 11 och Linux. Ladda ned installationsprogrammet för ditt operativsystem och följ sedan stegen nedan. Efter installationen klickar du på **Accept & Install** på skärmen **Get Started** — AMD Sync startar automatiskt när det är klart.

### Windows

[Ladda ned AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Dubbelklicka på `AMDSyncInstaller.exe`.
2. Klicka på **Accept & Install**.

> Om Windows-brandväggen uppmanar dig, tillåt AMD Sync nätverksåtkomst så att det kan nå Ryzen AI Halo via SSH.

### Linux

Klicka på länken för att ladda ned ditt föredragna format:

| Format | Nedladdning | Installationskommando |
|--------|-------------|----------------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Obs:** Ubuntu App Center kan flagga en lokalt öppnad `.deb`-fil som *"Potentiellt osäker."* Det är standardvarningen för alla tredjepartsinstallationsprogram. Om ett dubbelklick på `.deb`-filen misslyckas, använd terminalkommandot ovan.

---

## Steg 3 — Anslut till din Ryzen AI Halo

Vid första start visar AMD Sync formuläret **Add a Remote Device**. Fyll i det med värdena från Developer Centers flik **Remote**.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Fält | Anteckningar |
|------|--------------|
| **Device Name** *(valfritt)* | En beskrivande etikett som `Ryzen AI Halo`. Standardvärdet är `Device 1`, `Device 2`, … |
| **Hostname or IP** | Från fliken Remote |
| **SSH Port** | Från fliken Remote (endast siffror) |
| **Username** | Ditt OS-kontonamn på Ryzen AI Halo |
| **Password** | Ditt OS-inloggningslösenord — maskerat när du skriver |

Klicka på **Add Device**. Efter en kort laddningsskärm ser du **"Connection Successful"** och hamnar i hemvyn, som finns i systemfältet. Klicka utanför fönstret för att stänga det; AMD Sync fortsätter att köra och är ett klick bort.

> **Om anslutningen misslyckas** återgår AMD Sync till formuläret med dina värden bevarade. De vanligaste orsakerna är att SSH är inaktiverat på Ryzen AI Halo, fel lösenord, eller att de två enheterna befinner sig på olika nätverk.

---

## Steg 4 — Starta ditt första fjärrverktyg

Hemvyn ger dig fem enklickskomponenter — alla tillgängliga oavsett vilket operativsystem klienten och Ryzen AI Halo kör.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponent | Vad den gör |
|-----------|-------------|
| **Directory** | Väljer mappen på Ryzen AI Halo som VS Code, Terminal och JupyterLab öppnas i. Standardvärdet är en hanterad `Documents/AMD_Sync`-arbetsyta. |
| **VS Code** | Öppnar VS Code lokalt med en SSH-tunnel till den valda mappen. |
| **Terminal** | Öppnar en lokal terminal SSH-ansluten till Ryzen AI Halo, i den valda mappen. |
| **JupyterLab** | Startar ett anteckningsboksprojekt SSH-anslutet till Ryzen AI Halo, begränsat till den valda mappen. |
| **Live Metrics** | Realtidsvy av GPU-, minnes- och CPU-användning på Ryzen AI Halo. |

### Prova VS Code

För din första start, prova **VS Code**.

1. Lämna **Directory** på standardvärdet `~/Documents/AMD_Sync`.
2. Klicka på **VS Code**.
3. AMD Sync skapar `Documents/AMD_Sync/Project_1` på Ryzen AI Halo och öppnar VS Code lokalt, tunnlat in i det.

Du redigerar nu filer som finns på Ryzen AI Halo med din lokala VS Code-installation. Skapa `helloworld.py`, lägg till `print("hello world")`, öppna den integrerade terminalen (`` Ctrl + ` ``), och kör den:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Statusfältet visar **SSH: Linux** — bevis på att din kod körs på Ryzen AI Halo, inte på din bärbara dator.

### Prova terminalen

Klicka på **Terminal** för att hamna i samma mapp via SSH utan att lämna tangentbordet.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

På Windows är standardterminalen **PowerShell** — byt till **Windows Command Prompt** från inställningsmenyn om du föredrar det. På Linux använder AMD Sync din standardsystemterminal.

---

## Hur Directory fungerar

Rullgardinsmenyn **Directory** är den viktigaste kontrollen i AMD Sync — den avgör var varje verktyg du startar hamnar på Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (standard)** — Att starta VS Code eller JupyterLab härifrån skapar automatiskt en ny projektmapp (`Project_1`, `Project_2`, … för VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … för JupyterLab).
- **Befintliga projektmappar** — Alla direkta undermappar till `AMD_Sync` (inklusive mappar du skapar manuellt på Ryzen AI Halo) visas i rullgardinsmenyn. Den senast använda mappen blir standard nästa gång.
- **Anpassade sökvägar** — Skriv in en absolut sökväg för att öppna en mapp någon annanstans på Ryzen AI Halo. AMD Sync *öppnar* den bara — det skapar inte mappar utanför `AMD_Sync`, och anpassade sökvägar sparas inte mellan sessioner.

Om en anpassad sökväg inte fungerar berättar AMD Sync varför: ogiltig syntax, mappen finns inte, eller sökvägen pekar på en fil.

---

## Live Metrics och JupyterLab

- **Live Metrics** — En live-instrumentpanel för GPU-, minnes- och CPU-användning. Det snabbaste sättet att bekräfta att en fjärrträningskörning faktiskt når hårdvaran.
- **JupyterLab** — Ett fullständigt anteckningsboksprojekt SSH-anslutet till Ryzen AI Halo, med en egen integrerad terminal för att blanda anteckningsboksceller och skalkommandon utan att lämna gränssnittet.

---

## Inställningar och flera enheter

Menyn **Settings** har tre flikar:

| Flik | Vad den täcker |
|------|----------------|
| **Devices** | Listar alla Ryzen AI Halo du har anslutit till framgångsrikt. Återanslut, redigera inloggningsuppgifter eller lägg till en ny enhet. |
| **Information** | Länkar till dokumentation och forumstöd. |
| **Customize** | Flytta appen på skrivbordet, byt terminaltyp (endast Windows) och sök efter AMD Sync-uppdateringar. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Terminaltyp (Windows)** — Välj mellan **PowerShell** (standard) och **Windows Command Prompt**.
- **Terminaltyp (Linux)** — Endast standardsystemterminalen är tillgänglig.
- **Appuppdateringar** — Den här fliken är rätt ställe för att söka efter och installera nya AMD Sync-versioner inifrån gränssnittet; inget separat uppdateringsprogram behövs.

> En enhet visas bara under **Devices** efter en lyckad första anslutning, så misslyckade försök fyller inte listan.

---

## Felsökning

- **Anslutningen misslyckas omedelbart** — Bekräfta att SSH-servern är aktiverad på Ryzen AI Halos flik **Remote** i Developer Center.
- **Fel lösenordsfel** — Använd ditt **OS-inloggningslösenord** på Ryzen AI Halo, inte lösenord från Developer Center.
- **VS Code-knappen gör ingenting** — Installera VS Code på din klientmaskin från [code.visualstudio.com](https://code.visualstudio.com).
- **AMD Sync-systemfältsikonen saknas (Linux/GNOME)** — Installera och aktivera AppIndicator-tillägget.
- **`.deb`-filen öppnas inte från filhanteraren** — Använd `sudo apt install ./AMDSyncInstaller.deb` från en terminal.

---