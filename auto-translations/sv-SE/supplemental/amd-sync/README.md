<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinöversättning.** Den här sidan har automatiskt översatts från engelska och har inte granskats av en människa. Den kan innehålla fel, och vissa instruktioner, kommandon, nedladdningar, produkttillgänglighet eller annat innehåll kan variera beroende på språk eller region. Vid eventuella motsägelser eller avvikelser är det den ursprungliga engelska versionen av playbook som gäller och har företräde.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Fjärrutveckling med AMD Sync

## Översikt

**AMD Sync** förvandlar din bärbara dator till en fjärrstyrningscentral för AMD Ryzen™ AI Halo. Slipp manuell SSH-, nyckel- och IDE-konfiguration — installera AMD Sync och få åtkomst med ett klick till en fjärrterminal, VS Code, JupyterLab och en instrumentpanel i realtid för GPU/CPU/minne på Ryzen AI Halo.

Din lokala dator förblir bekant; varje kommando, notebook och modell körs på Ryzen AI Halo.

> **Tips**: Den här sidan kommer att innehålla alla nya uppdateringar för AMDSync.

## Vad du kommer att lära dig

- Aktivera SSH på Ryzen AI Halo och ansluta till den från AMD Sync
- Starta VS Code, Terminal, JupyterLab och Live Metrics mot Ryzen AI Halo med ett klick
- Organisera fjärrarbete med hjälp av AMD Syncs hanterade projektmappar

---

## Grundläggande koncept

AMD Sync har två sidor: en **klient** (din bärbara dator, som kör AMD Sync-appen) och en **server** (Ryzen AI Halo, som kör en SSH-server som AMD Sync tunnlar in i). Allt du startar från AMD Sync — VS Code, en terminal, en notebook — öppnas lokalt men körs på Ryzen AI Halo.

> **Klienter som stöds:** Windows 11 och Linux. macOS stöds inte.

---

## Steg 1 — Aktivera SSH på Ryzen AI Halo


> **Obs:** På Windows levereras Ryzen AI Halo med SSH-servern *avstängd som standard*. På Linux levereras den med SSH-servern *påslagen som standard*.

1. Öppna **AMD Ryzen™ AI Developer Center** på Ryzen AI Halo.
2. Gå till fliken **Remote**.
3. Slå på **SSH Server**.
4. Notera **IP Address**, **Port** och **Username** som visas under **Server Information** — du kommer att klistra in dessa i AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Obs:** Detta är AMD Developer Center för Windows. Linux-versionen kan ha ett annat användargränssnitt, men liknande fjärrfunktionalitet.

> **Tips:** AMD Sync frågar efter användarens **OS-inloggningslösenord**, inte ett lösenord från Developer Center.

---

## Steg 2 — Installera AMD Sync på din klient

AMD Sync körs på Windows 11 och Linux. Ladda ner installationsprogrammet för ditt operativsystem och följ stegen nedan. Efter installationen klickar du på **Accept & Install** på skärmen **Get Started** — AMD Sync startar automatiskt när det är klart.

### Windows

[Ladda ner AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Dubbelklicka på `AMDSyncInstaller.exe`.
2. Klicka på **Accept & Install**.

> Om Windows-brandväggen frågar dig, tillåt AMD Sync nätverksåtkomst så att det kan nå Ryzen AI Halo via SSH.

### Linux

Klicka på länken för att ladda ner önskat format:

| Format | Nedladdning | Installationskommando |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Obs:** Ubuntu App Center kan flagga en lokalt öppnad `.deb`-fil som *"Potentiellt osäker."* Det är den vanliga varningen för alla lokala installationsprogram från tredje part. Om det inte går att dubbelklicka på `.deb`-filen, använd terminalkommandot ovan.

---

## Steg 3 — Anslut till din Ryzen AI Halo

Vid första start visar AMD Sync formuläret **Add a Remote Device**. Fyll i det med värdena från fliken **Remote** i Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Fält | Anteckningar |
|-------|-------|
| **Device Name** *(valfritt)* | En vänlig etikett som `Ryzen AI Halo`. Standardvärde är `Device 1`, `Device 2`, … |
| **Hostname or IP** | Från fliken Remote |
| **SSH Port** | Från fliken Remote (endast siffror) |
| **Username** | Ditt OS-kontonamn på Ryzen AI Halo |
| **Password** | Ditt OS-inloggningslösenord — maskeras när du skriver |

Klicka på **Add Device**. Efter en kort laddningsskärm ser du **"Connection Successful"** och kommer till startvyn, som finns i systemfältet. Klicka utanför fönstret för att stänga det; AMD Sync fortsätter att köras och är ett klick bort.

> **Om anslutningen misslyckas** återgår AMD Sync till formuläret med dina värden bevarade. De vanligaste orsakerna är att SSH är inaktiverat på Ryzen AI Halo, fel lösenord, eller att de två enheterna befinner sig på olika nätverk.

---

## Steg 4 — Starta ditt första fjärrverktyg

Startvyn ger dig fem komponenter med ett klick — alla tillgängliga oavsett vilket operativsystem klienten och Ryzen AI Halo kör.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponent | Vad den gör |
|-----------|--------------|
| **Directory** | Väljer mappen på Ryzen AI Halo som VS Code, Terminal och JupyterLab kommer att öppnas i. Standard är en hanterad `Documents/AMD_Sync`-arbetsyta. |
| **VS Code** | Öppnar VS Code lokalt med en SSH-tunnel in i den valda mappen. |
| **Terminal** | Öppnar en lokal terminal SSH-ansluten till Ryzen AI Halo, i den valda mappen. |
| **JupyterLab** | Startar ett notebook-projekt SSH-anslutet till Ryzen AI Halo, avgränsat till den valda mappen. |
| **Live Metrics** | Realtidsvy av GPU-, minnes- och CPU-användning på Ryzen AI Halo. |

### Testa VS Code

För din första start, prova **VS Code**.

1. Lämna **Directory** på standardvärdet `~/Documents/AMD_Sync`.
2. Klicka på **VS Code**.
3. AMD Sync skapar `Documents/AMD_Sync/Project_1` på Ryzen AI Halo och öppnar VS Code lokalt, tunnlat in i den.

Du redigerar nu filer som finns på Ryzen AI Halo med din lokala VS Code-konfiguration. Skapa `helloworld.py`, lägg till `print("hello world")`, öppna den integrerade terminalen (`` Ctrl + ` ``), och kör den:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Statusfältet visar **SSH: Linux** — ett bevis på att din kod körs på Ryzen AI Halo, inte på din bärbara dator.
### Prova terminalen

Klicka på **Terminal** för att hamna i samma mapp via SSH utan att lämna tangentbordet.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

I Windows är standardterminalen **PowerShell** — byt till **Windows Command Prompt** från inställningsmenyn om du föredrar det. På Linux använder AMD Sync systemets standardterminal.

---

## Så här fungerar katalogen

Rullgardinsmenyn **Directory** är den enskilt viktigaste kontrollen i AMD Sync — den avgör var varje verktyg du startar hamnar på Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (standard)** — Om du startar VS Code eller JupyterLab härifrån skapas automatiskt en ny projektmapp (`Project_1`, `Project_2`, … för VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … för JupyterLab).
- **Befintliga projektmappar** — Varje direkt undermapp till `AMD_Sync` (inklusive mappar du skapar manuellt på Ryzen AI Halo) visas i rullgardinsmenyn. Den senast använda mappen blir standardval nästa gång.
- **Anpassade sökvägar** — Skriv in en absolut sökväg för att öppna en mapp någon annanstans på Ryzen AI Halo. AMD Sync *öppnar* den bara — den skapar inte mappar utanför `AMD_Sync`, och anpassade sökvägar sparas inte mellan sessioner.

Om en anpassad sökväg inte fungerar talar AMD Sync om varför: ogiltig syntax, mappen finns inte, eller sökvägen pekar på en fil.

---

## Live Metrics och JupyterLab

- **Live Metrics** — En instrumentpanel i realtid för GPU-, minnes- och CPU-användning. Det snabbaste sättet att bekräfta att en fjärrkörd träningskörning verkligen belastar hårdvaran.
- **JupyterLab** — Ett fullständigt notebook-projekt som är SSH-anslutet till Ryzen AI Halo, med en egen integrerad terminal för att blanda notebook-celler och skalkommandon utan att lämna gränssnittet.

---

## Inställningar och flera enheter

Menyn **Settings** har tre flikar:

| Flik | Vad den omfattar |
|-----|----------------|
| **Devices** | Listar varje Ryzen AI Halo du har anslutit till framgångsrikt. Återanslut, redigera autentiseringsuppgifter eller lägg till en ny enhet. |
| **Information** | Länkar till dokumentation och forumsupport. |
| **Customize** | Flytta appen på skrivbordet, byt terminaltyp (endast Windows) och sök efter uppdateringar för AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Terminaltyp (Windows)** — Välj mellan **PowerShell** (standard) och **Windows Command Prompt**.
- **Terminaltyp (Linux)** — Endast systemets standardterminal är tillgänglig.
- **Appuppdateringar** — Denna flik är rätt ställe för att söka efter och installera nya versioner av AMD Sync direkt i gränssnittet; ingen separat uppdaterare behövs.

> En enhet visas endast under **Devices** efter en lyckad första anslutning, så misslyckade försök belamrar inte listan.

---

## Felsökning

- **Anslutningen misslyckas direkt** — Bekräfta att SSH-servern är aktiverad på fliken **Remote** i Developer Center på Ryzen AI Halo.
- **Felaktigt lösenord** — Använd ditt **OS-inloggningslösenord** på Ryzen AI Halo, inte lösenord hämtade från Developer Center.
- **VS Code-knappen gör ingenting** — Installera VS Code på din klientdator från [code.visualstudio.com](https://code.visualstudio.com).
- **AMD Sync-ikonen i systemfältet saknas (Linux/GNOME)** — Installera och aktivera tillägget AppIndicator.
- **`.deb`-filen går inte att öppna från filhanteraren** — Använd `sudo apt install ./AMDSyncInstaller.deb` från en terminal.

---