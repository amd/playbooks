<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Remote-Entwicklung mit AMD Sync

## Übersicht

**AMD Sync** verwandelt Ihren Laptop in ein Remote-Cockpit für den AMD Ryzen™ AI Halo. Überspringen Sie die manuelle SSH-, Schlüssel- und IDE-Einrichtung — installieren Sie AMD Sync und erhalten Sie per Mausklick Zugriff auf ein Remote-Terminal, VS Code, JupyterLab und ein Live-Dashboard für GPU/CPU/Arbeitsspeicher auf dem Ryzen AI Halo.

Ihr lokaler Rechner bleibt vertraut; jeder Befehl, jedes Notebook und jedes Modell wird auf dem Ryzen AI Halo ausgeführt.

> **Tipp**: Diese Seite enthält alle neuen Updates zu AMDSync.

## Was Sie lernen werden

- SSH auf dem Ryzen AI Halo aktivieren und von AMD Sync aus eine Verbindung herstellen
- VS Code, Terminal, JupyterLab und Live-Metriken mit einem Klick gegen den Ryzen AI Halo starten
- Remote-Arbeit mithilfe der verwalteten Projektordner von AMD Sync organisieren

---

## Grundlegende Konzepte

AMD Sync hat zwei Seiten: einen **Client** (Ihr Laptop, auf dem die AMD Sync-App läuft) und einen **Server** (den Ryzen AI Halo, auf dem ein SSH-Server läuft, in den AMD Sync einen Tunnel aufbaut). Alles, was Sie von AMD Sync aus starten — VS Code, ein Terminal, ein Notebook — öffnet sich lokal, wird aber auf dem Ryzen AI Halo ausgeführt.

> **Unterstützte Clients:** Windows 11 und Linux. macOS wird nicht unterstützt.

---

## Schritt 1 — SSH auf dem Ryzen AI Halo aktivieren


> **Hinweis:** Unter Windows wird der Ryzen AI Halo mit dem SSH-Server *standardmäßig deaktiviert* ausgeliefert. Unter Linux wird er mit dem SSH-Server *standardmäßig aktiviert* ausgeliefert.

1. Öffnen Sie auf dem Ryzen AI Halo das **AMD Ryzen™ AI Developer Center**.
2. Wechseln Sie zur Registerkarte **Remote**.
3. Aktivieren Sie den **SSH-Server**.
4. Notieren Sie die **IP-Adresse**, den **Port** und den **Benutzernamen**, die unter **Serverinformationen** angezeigt werden — Sie werden diese in AMD Sync einfügen.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Hinweis:** Dies ist das AMD Developer Center für Windows. Das Linux-Pendant kann eine andere Benutzeroberfläche haben, bietet aber ähnliche Remote-Funktionen.

> **Tipp:** AMD Sync fragt nach dem **Betriebssystem-Anmeldepasswort** dieses Benutzers, nicht nach einem Passwort aus dem Developer Center.

---

## Schritt 2 — AMD Sync auf Ihrem Client installieren

AMD Sync läuft auf Windows 11 und Linux. Laden Sie das Installationsprogramm für Ihr Betriebssystem herunter und folgen Sie dann den nachstehenden Schritten. Klicken Sie nach der Installation auf dem **Erste Schritte**-Bildschirm auf **Akzeptieren & Installieren** — AMD Sync startet nach Abschluss automatisch.

### Windows

[AMDSyncInstaller.exe herunterladen](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Doppelklicken Sie auf `AMDSyncInstaller.exe`.
2. Klicken Sie auf **Akzeptieren & Installieren**.

> Wenn die Windows-Firewall Sie dazu auffordert, erlauben Sie AMD Sync den Netzwerkzugriff, damit es den Ryzen AI Halo über SSH erreichen kann.

### Linux

Klicken Sie auf den Link, um Ihr bevorzugtes Format herunterzuladen:

| Format | Download | Installationsbefehl |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Hinweis:** Das Ubuntu App Center kann eine lokal geöffnete `.deb`-Datei als *„Möglicherweise unsicher"* kennzeichnen. Dies ist die Standardwarnung für alle lokalen Drittanbieter-Installationsprogramme. Wenn ein Doppelklick auf die `.deb`-Datei fehlschlägt, verwenden Sie den obigen Terminal-Befehl.

---

## Schritt 3 — Mit Ihrem Ryzen AI Halo verbinden

Beim ersten Start zeigt AMD Sync das Formular **Remote-Gerät hinzufügen**. Füllen Sie es mit den Werten aus der Registerkarte **Remote** des Developer Centers aus.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Feld | Hinweise |
|-------|-------|
| **Gerätename** *(optional)* | Eine aussagekräftige Bezeichnung wie `Ryzen AI Halo`. Standardmäßig `Device 1`, `Device 2`, … |
| **Hostname oder IP** | Aus der Registerkarte „Remote" |
| **SSH-Port** | Aus der Registerkarte „Remote" (nur Zahlen) |
| **Benutzername** | Ihr Betriebssystem-Kontoname auf dem Ryzen AI Halo |
| **Passwort** | Ihr Betriebssystem-Anmeldepasswort — bei der Eingabe maskiert |

Klicken Sie auf **Gerät hinzufügen**. Nach einem kurzen Ladebildschirm sehen Sie **„Verbindung erfolgreich"** und gelangen zur Startansicht, die in Ihrem Systemtray angezeigt wird. Klicken Sie außerhalb des Fensters, um es zu schließen; AMD Sync läuft weiter und ist per Mausklick erreichbar.

> **Wenn die Verbindung fehlschlägt,** kehrt AMD Sync mit Ihren gespeicherten Werten zum Formular zurück. Die häufigsten Ursachen sind ein deaktivierter SSH-Server auf dem Ryzen AI Halo, ein falsches Passwort oder zwei Geräte in unterschiedlichen Netzwerken.

---

## Schritt 4 — Ihr erstes Remote-Tool starten

Die Startansicht bietet Ihnen fünf Komponenten per Mausklick — alle verfügbar, unabhängig davon, welches Betriebssystem Client und Ryzen AI Halo verwenden.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponente | Funktion |
|-----------|--------------|
| **Verzeichnis** | Wählt den Ordner auf dem Ryzen AI Halo aus, in dem VS Code, Terminal und JupyterLab geöffnet werden. Standardmäßig ein verwalteter `Documents/AMD_Sync`-Arbeitsbereich. |
| **VS Code** | Öffnet VS Code lokal mit einem SSH-Tunnel in den ausgewählten Ordner. |
| **Terminal** | Öffnet ein lokales Terminal, das per SSH mit dem Ryzen AI Halo verbunden ist, im ausgewählten Ordner. |
| **JupyterLab** | Startet ein Notebook-Projekt, das per SSH mit dem Ryzen AI Halo verbunden ist und auf den ausgewählten Ordner beschränkt ist. |
| **Live-Metriken** | Echtzeit-Ansicht der GPU-, Arbeitsspeicher- und CPU-Auslastung auf dem Ryzen AI Halo. |

### VS Code ausprobieren

Probieren Sie für Ihren ersten Start **VS Code** aus.

1. Lassen Sie **Verzeichnis** auf dem Standard `~/Documents/AMD_Sync`.
2. Klicken Sie auf **VS Code**.
3. AMD Sync erstellt `Documents/AMD_Sync/Project_1` auf dem Ryzen AI Halo und öffnet VS Code lokal, mit einem Tunnel dorthin.

Sie bearbeiten jetzt Dateien, die auf dem Ryzen AI Halo gespeichert sind, mit Ihrer lokalen VS Code-Einrichtung. Erstellen Sie `helloworld.py`, fügen Sie `print("hello world")` hinzu, öffnen Sie das integrierte Terminal (`` Ctrl + ` ``), und führen Sie es aus:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Die Statusleiste zeigt **SSH: Linux** — der Beweis, dass Ihr Code auf dem Ryzen AI Halo und nicht auf Ihrem Laptop ausgeführt wird.

### Das Terminal ausprobieren

Klicken Sie auf **Terminal**, um ohne Verlassen der Tastatur per SSH in denselben Ordner zu wechseln.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Unter Windows ist das Standardterminal **PowerShell** — wechseln Sie im Einstellungsmenü zur **Windows-Eingabeaufforderung**, wenn Sie diese bevorzugen. Unter Linux verwendet AMD Sync Ihr Standard-Systemterminal.

---

## Funktionsweise des Verzeichnisses

Das **Verzeichnis**-Dropdown ist die wichtigste Steuerung in AMD Sync — es legt fest, wo jedes von Ihnen gestartete Tool auf dem Ryzen AI Halo landet.

- **`~/Documents/AMD_Sync` (Standard)** — Wenn Sie VS Code oder JupyterLab von hier aus starten, wird automatisch ein neuer Projektordner erstellt (`Project_1`, `Project_2`, … für VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … für JupyterLab).
- **Vorhandene Projektordner** — Jeder direkte Unterordner von `AMD_Sync` (einschließlich Ordner, die Sie manuell auf dem Ryzen AI Halo erstellen) erscheint im Dropdown. Der zuletzt verwendete Ordner wird beim nächsten Mal zum Standard.
- **Benutzerdefinierte Pfade** — Geben Sie einen absoluten Pfad ein, um einen Ordner an anderer Stelle auf dem Ryzen AI Halo zu öffnen. AMD Sync *öffnet* ihn nur — es erstellt keine Ordner außerhalb von `AMD_Sync`, und benutzerdefinierte Pfade werden nicht zwischen Sitzungen gespeichert.

Wenn ein benutzerdefinierter Pfad nicht funktioniert, teilt Ihnen AMD Sync den Grund mit: ungültige Syntax, Ordner existiert nicht oder der Pfad verweist auf eine Datei.

---

## Live-Metriken und JupyterLab

- **Live-Metriken** — Ein Live-Dashboard zur GPU-, Arbeitsspeicher- und CPU-Auslastung. Der schnellste Weg, um zu bestätigen, dass ein Remote-Trainingslauf tatsächlich die Hardware beansprucht.
- **JupyterLab** — Ein vollständiges Notebook-Projekt, das per SSH mit dem Ryzen AI Halo verbunden ist, mit einem eigenen integrierten Terminal zum Kombinieren von Notebook-Zellen und Shell-Befehlen, ohne die Benutzeroberfläche zu verlassen.

---

## Einstellungen und mehrere Geräte

Das **Einstellungen**-Menü hat drei Registerkarten:

| Registerkarte | Inhalt |
|-----|----------------|
| **Geräte** | Listet alle Ryzen AI Halo-Geräte auf, mit denen Sie sich erfolgreich verbunden haben. Erneut verbinden, Anmeldedaten bearbeiten oder ein neues Gerät hinzufügen. |
| **Informationen** | Links zur Dokumentation und zum Forum-Support. |
| **Anpassen** | App auf Ihrem Desktop neu positionieren, Terminaltyp wechseln (nur Windows) und nach AMD Sync-Updates suchen. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Terminaltyp (Windows)** — Wählen Sie zwischen **PowerShell** (Standard) und **Windows-Eingabeaufforderung**.
- **Terminaltyp (Linux)** — Nur das Standard-Systemterminal ist verfügbar.
- **App-Updates** — Diese Registerkarte ist der richtige Ort, um neue AMD Sync-Versionen direkt in der Benutzeroberfläche zu suchen und zu installieren; kein separates Aktualisierungsprogramm ist erforderlich.

> Ein Gerät erscheint unter **Geräte** erst nach einer erfolgreichen ersten Verbindung, sodass fehlgeschlagene Versuche die Liste nicht überfüllen.

---

## Fehlerbehebung

- **Verbindung schlägt sofort fehl** — Vergewissern Sie sich, dass der SSH-Server auf der Registerkarte **Remote** des Ryzen AI Halo im Developer Center aktiviert ist.
- **Fehler „Falsches Passwort"** — Verwenden Sie Ihr **Betriebssystem-Anmeldepasswort** auf dem Ryzen AI Halo, nicht Passwörter aus dem Developer Center.
- **VS Code-Schaltfläche reagiert nicht** — Installieren Sie VS Code auf Ihrem Client-Rechner von [code.visualstudio.com](https://code.visualstudio.com).
- **AMD Sync-Tray-Symbol fehlt (Linux/GNOME)** — Installieren und aktivieren Sie die AppIndicator-Erweiterung.
- **`.deb` lässt sich nicht vom Dateimanager öffnen** — Verwenden Sie `sudo apt install ./AMDSyncInstaller.deb` in einem Terminal.

---