<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maschinelle Übersetzung.** Diese Seite wurde automatisch aus dem Englischen übersetzt und nicht von einem Menschen überprüft. Sie kann Fehler enthalten, und bestimmte Anweisungen, Befehle, Downloads, Produktverfügbarkeiten oder andere Inhalte können je nach Sprache oder Region abweichen. Im Falle von Unstimmigkeiten oder Widersprüchen ist die englische Originalversion des playbook maßgeblich und hat Vorrang.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Remoteentwicklung mit AMD Sync

## Überblick

**AMD Sync** verwandelt Ihren Laptop in ein Remote-Cockpit für den AMD Ryzen™ AI Halo. Überspringen Sie die manuelle SSH-, Schlüssel- und IDE-Einrichtung — installieren Sie AMD Sync und erhalten Sie mit einem Klick Zugriff auf ein Remote-Terminal, VS Code, JupyterLab und ein Live-GPU-/CPU-/Speicher-Dashboard auf dem Ryzen AI Halo.

Ihr lokaler Computer bleibt vertraut; jeder Befehl, jedes Notebook und jedes Modell läuft auf dem Ryzen AI Halo.

> **Tipp**: Diese Seite enthält alle neuen Updates zu AMDSync. 

## Was Sie lernen werden

- Aktivieren von SSH auf dem Ryzen AI Halo und Verbinden von AMD Sync aus
- Starten von VS Code, Terminal, JupyterLab und Live Metrics gegen den Ryzen AI Halo mit einem Klick
- Organisieren der Remote-Arbeit mithilfe der verwalteten Projektordner von AMD Sync

---

## Grundkonzepte

AMD Sync hat zwei Seiten: einen **Client** (Ihr Laptop, auf dem die AMD Sync-App läuft) und einen **Server** (den Ryzen AI Halo, auf dem ein SSH-Server läuft, in den sich AMD Sync einklinkt). Alles, was Sie von AMD Sync aus starten — VS Code, ein Terminal, ein Notebook — öffnet sich lokal, wird aber auf dem Ryzen AI Halo ausgeführt.

> **Unterstützte Clients:** Windows 11 und Linux. macOS wird nicht unterstützt.

---

## Schritt 1 — SSH auf dem Ryzen AI Halo aktivieren


> **Hinweis:** Unter Windows wird der Ryzen AI Halo mit standardmäßig *deaktiviertem* SSH-Server ausgeliefert. Unter Linux ist der SSH-Server standardmäßig *aktiviert*.

1. Öffnen Sie auf dem Ryzen AI Halo das **AMD Ryzen™ AI Developer Center**.
2. Gehen Sie zur Registerkarte **Remote**.
3. Aktivieren Sie **SSH Server**.
4. Notieren Sie sich **IP Address**, **Port** und **Username**, die unter **Server Information** angezeigt werden — Sie fügen sie später in AMD Sync ein.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Hinweis:** Dies ist das AMD Developer Center für Windows. Das Linux-Pendant kann eine andere Benutzeroberfläche haben, bietet aber ähnliche Remote-Funktionalität.

> **Tipp:** AMD Sync fragt nach dem **Betriebssystem-Anmeldepasswort** dieses Benutzers, nicht nach einem Passwort aus dem Developer Center.

---

## Schritt 2 — AMD Sync auf Ihrem Client installieren

AMD Sync läuft unter Windows 11 und Linux. Laden Sie das Installationsprogramm für Ihr Betriebssystem herunter und folgen Sie den nachstehenden Schritten. Klicken Sie nach der Installation auf dem Bildschirm **Get Started** auf **Accept & Install** — AMD Sync startet nach Abschluss automatisch.

### Windows

[AMDSyncInstaller.exe herunterladen](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Doppelklicken Sie auf `AMDSyncInstaller.exe`.
2. Klicken Sie auf **Accept & Install**.

> Wenn die Windows-Firewall Sie dazu auffordert, erlauben Sie AMD Sync den Netzwerkzugriff, damit die App den Ryzen AI Halo über SSH erreichen kann.

### Linux

Klicken Sie auf den Link, um Ihr bevorzugtes Format herunterzuladen:

| Format | Download | Installationsbefehl |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Hinweis:** Das Ubuntu App Center kann eine lokal geöffnete `.deb`-Datei als *„Potentially unsafe“* kennzeichnen. Dies ist die Standardwarnung für jedes lokal installierte Programm eines Drittanbieters. Falls das Doppelklicken auf die `.deb`-Datei fehlschlägt, verwenden Sie den obigen Terminalbefehl.

---

## Schritt 3 — Verbindung zu Ihrem Ryzen AI Halo herstellen

Beim ersten Start zeigt AMD Sync das Formular **Add a Remote Device** an. Füllen Sie es mit den Werten aus der Registerkarte **Remote** des Developer Centers aus.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Feld | Hinweise |
|-------|-------|
| **Device Name** *(optional)* | Eine freundliche Bezeichnung wie `Ryzen AI Halo`. Standardmäßig `Device 1`, `Device 2`, … |
| **Hostname or IP** | Von der Registerkarte Remote |
| **SSH Port** | Von der Registerkarte Remote (nur Zahlen) |
| **Username** | Ihr Betriebssystem-Kontoname auf dem Ryzen AI Halo |
| **Password** | Ihr Betriebssystem-Anmeldepasswort — wird beim Eingeben maskiert |

Klicken Sie auf **Add Device**. Nach einem kurzen Ladebildschirm sehen Sie **„Connection Successful“** und gelangen zur Startansicht, die sich in Ihrer Systemablage befindet. Klicken Sie außerhalb des Fensters, um es zu schließen; AMD Sync läuft weiter im Hintergrund und ist nur einen Klick entfernt.

> **Wenn die Verbindung fehlschlägt,** kehrt AMD Sync zum Formular zurück, wobei Ihre Werte erhalten bleiben. Die üblichen Ursachen sind ein deaktivierter SSH-Server auf dem Ryzen AI Halo, ein falsches Passwort oder dass sich die beiden Geräte in unterschiedlichen Netzwerken befinden.

---

## Schritt 4 — Starten Sie Ihr erstes Remote-Tool

Die Startansicht bietet Ihnen fünf Ein-Klick-Komponenten — alle verfügbar, unabhängig davon, welches Betriebssystem der Client und der Ryzen AI Halo verwenden.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponente | Funktion |
|-----------|--------------|
| **Directory** | Wählt den Ordner auf dem Ryzen AI Halo aus, in dem VS Code, Terminal und JupyterLab geöffnet werden. Standardmäßig ein verwalteter `Documents/AMD_Sync`-Arbeitsbereich. |
| **VS Code** | Öffnet VS Code lokal mit einem SSH-Tunnel in den ausgewählten Ordner. |
| **Terminal** | Öffnet ein lokales Terminal mit SSH-Verbindung zum Ryzen AI Halo im ausgewählten Ordner. |
| **JupyterLab** | Startet ein Notebook-Projekt mit SSH-Verbindung zum Ryzen AI Halo, beschränkt auf den ausgewählten Ordner. |
| **Live Metrics** | Echtzeitansicht der GPU-, Speicher- und CPU-Auslastung auf dem Ryzen AI Halo. |

### VS Code ausprobieren

Probieren Sie für Ihren ersten Start **VS Code** aus.

1. Belassen Sie **Directory** auf dem Standardwert `~/Documents/AMD_Sync`.
2. Klicken Sie auf **VS Code**.
3. AMD Sync erstellt `Documents/AMD_Sync/Project_1` auf dem Ryzen AI Halo und öffnet VS Code lokal, per Tunnel damit verbunden.

Sie bearbeiten jetzt Dateien, die sich auf dem Ryzen AI Halo befinden, mit Ihrer lokalen VS Code-Einrichtung. Erstellen Sie `helloworld.py`, fügen Sie `print("hello world")` hinzu, öffnen Sie das integrierte Terminal (`` Ctrl + ` ``) und führen Sie es aus:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

In der Statusleiste steht **SSH: Linux** — der Beweis, dass Ihr Code auf dem Ryzen AI Halo läuft, nicht auf Ihrem Laptop.
### Terminal ausprobieren

Klicken Sie auf **Terminal**, um über SSH in denselben Ordner zu wechseln, ohne die Tastatur zu verlassen.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Unter Windows ist das Standardterminal **PowerShell** – wechseln Sie im Einstellungsmenü zur **Windows-Eingabeaufforderung**, wenn Sie diese bevorzugen. Unter Linux verwendet AMD Sync Ihr systemeigenes Standardterminal.

---

## So funktioniert das Verzeichnis

Das Dropdown-Menü **Verzeichnis** ist das mit Abstand wichtigste Steuerelement in AMD Sync – es legt fest, wo jedes von Ihnen gestartete Tool auf dem Ryzen AI Halo landet.

- **`~/Documents/AMD_Sync` (Standard)** – Wenn Sie VS Code oder JupyterLab von hier aus starten, wird automatisch ein neuer Projektordner erstellt (`Project_1`, `Project_2`, … für VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … für JupyterLab).
- **Vorhandene Projektordner** – Jeder direkte Unterordner von `AMD_Sync` (einschließlich Ordnern, die Sie manuell auf dem Ryzen AI Halo erstellen) erscheint im Dropdown-Menü. Der zuletzt verwendete Ordner wird beim nächsten Mal zum Standard.
- **Benutzerdefinierte Pfade** – Geben Sie einen beliebigen absoluten Pfad ein, um einen Ordner an anderer Stelle auf dem Ryzen AI Halo zu öffnen. AMD Sync *öffnet* ihn nur – es erstellt keine Ordner außerhalb von `AMD_Sync`, und benutzerdefinierte Pfade werden nicht zwischen den Sitzungen gespeichert.

Wenn ein benutzerdefinierter Pfad nicht funktioniert, teilt AMD Sync Ihnen den Grund mit: ungültige Syntax, Ordner existiert nicht, oder der Pfad verweist auf eine Datei.

---

## Live-Metriken und JupyterLab

- **Live-Metriken** – Ein Live-Dashboard zur GPU-, Speicher- und CPU-Auslastung. Der schnellste Weg, um zu bestätigen, dass ein Remote-Trainingslauf tatsächlich die Hardware beansprucht.
- **JupyterLab** – Ein vollständiges Notebook-Projekt, das über SSH mit dem Ryzen AI Halo verbunden ist, mit einem eigenen integrierten Terminal, um Notebook-Zellen und Shell-Befehle zu kombinieren, ohne die Benutzeroberfläche zu verlassen.

---

## Einstellungen und mehrere Geräte

Das Menü **Einstellungen** hat drei Registerkarten:

| Registerkarte | Was sie umfasst |
|-----|----------------|
| **Geräte** | Listet jeden Ryzen AI Halo auf, mit dem Sie sich erfolgreich verbunden haben. Erneut verbinden, Anmeldedaten bearbeiten oder ein neues Gerät hinzufügen. |
| **Informationen** | Links zur Dokumentation und zum Forum-Support. |
| **Anpassen** | Positionieren Sie die App auf Ihrem Desktop neu, wechseln Sie den Terminaltyp (nur Windows) und suchen Sie nach AMD Sync-Updates. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Terminaltyp (Windows)** – Wählen Sie zwischen **PowerShell** (Standard) und **Windows-Eingabeaufforderung**.
- **Terminaltyp (Linux)** – Nur das systemeigene Standardterminal ist verfügbar.
- **App-Updates** – Diese Registerkarte ist der richtige Ort, um innerhalb der Benutzeroberfläche nach neuen AMD Sync-Versionen zu suchen und diese zu installieren; ein separates Update-Tool ist nicht erforderlich.

> Ein Gerät erscheint erst nach einer erfolgreichen ersten Verbindung unter **Geräte**, sodass fehlgeschlagene Versuche die Liste nicht überladen.

---

## Problembehandlung

- **Verbindung schlägt sofort fehl** – Vergewissern Sie sich, dass der SSH-Server auf der Registerkarte **Remote** des Ryzen AI Halo im Developer Center aktiviert ist.
- **Fehler „Falsches Passwort“** – Verwenden Sie Ihr **Betriebssystem-Anmeldepasswort** auf dem Ryzen AI Halo, nicht Passwörter aus dem Developer Center.
- **VS Code-Schaltfläche reagiert nicht** – Installieren Sie VS Code auf Ihrem Client-Computer über [code.visualstudio.com](https://code.visualstudio.com).
- **AMD Sync-Taskleistensymbol fehlt (Linux/GNOME)** – Installieren und aktivieren Sie die AppIndicator-Erweiterung.
- **`.deb`-Datei lässt sich nicht über den Dateimanager öffnen** – Verwenden Sie `sudo apt install ./AMDSyncInstaller.deb` in einem Terminal.
- **Einrichtung erscheint bei jedem Start erneut (Linux)**: Entsperren Sie Ihren Anmelde-Schlüsselbund oder starten Sie mit `--password-store=gnome-libsecret` und wiederholen Sie die Einrichtung einmalig.

---