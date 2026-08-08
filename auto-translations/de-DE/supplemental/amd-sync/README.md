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

# Remote-Entwicklung mit AMD Sync

## Übersicht

**AMD Sync** verwandelt Ihren Laptop in ein Remote-Cockpit für den AMD Ryzen™ AI Halo. Überspringen Sie das manuelle SSH-, Schlüssel- und IDE-Setup — installieren Sie AMD Sync und erhalten Sie mit einem Klick Zugriff auf ein Remote-Terminal, VS Code, JupyterLab und ein Live-Dashboard für GPU/CPU/Arbeitsspeicher auf dem Ryzen AI Halo.

Ihr lokaler Rechner bleibt vertraut; jeder Befehl, jedes Notebook und jedes Modell läuft auf dem Ryzen AI Halo.

> **Tipp**: Diese Seite enthält alle neuen Aktualisierungen zu AMDSync.

## Was Sie lernen werden

- SSH auf dem Ryzen AI Halo aktivieren und sich von AMD Sync aus damit verbinden
- VS Code, Terminal, JupyterLab und Live-Metriken mit einem Klick für den Ryzen AI Halo starten
- Remote-Arbeit mithilfe der verwalteten Projektordner von AMD Sync organisieren

---

## Grundlegende Konzepte

AMD Sync besteht aus zwei Seiten: einem **Client** (Ihr Laptop, auf dem die AMD Sync-App läuft) und einem **Server** (der Ryzen AI Halo, auf dem ein SSH-Server läuft, in den sich AMD Sync tunnelt). Alles, was Sie von AMD Sync aus starten — VS Code, ein Terminal, ein Notebook — öffnet sich lokal, wird aber auf dem Ryzen AI Halo ausgeführt.

> **Unterstützte Clients:** Windows 11 und Linux. macOS wird nicht unterstützt.

---

## Schritt 1 — SSH auf dem Ryzen AI Halo aktivieren


> **Hinweis:** Unter Windows wird der Ryzen AI Halo mit dem SSH-Server *standardmäßig deaktiviert* ausgeliefert. Unter Linux ist der SSH-Server *standardmäßig aktiviert*.

1. Öffnen Sie auf dem Ryzen AI Halo das **AMD Ryzen™ AI Developer Center**.
2. Gehen Sie zur Registerkarte **Remote**.
3. Schalten Sie **SSH Server** ein.
4. Notieren Sie sich **IP Address**, **Port** und **Username**, die unter **Server Information** angezeigt werden — Sie werden diese in AMD Sync einfügen.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Hinweis:** Dies ist das AMD Developer Center für Windows. Das für Linux kann eine andere Benutzeroberfläche haben, bietet aber eine ähnliche Remote-Funktionalität.

> **Tipp:** AMD Sync fragt nach dem **Betriebssystem-Anmeldepasswort** dieses Benutzers, nicht nach einem Passwort aus dem Developer Center.

---

## Schritt 2 — AMD Sync auf Ihrem Client installieren

AMD Sync läuft unter Windows 11 und Linux. Laden Sie das Installationsprogramm für Ihr Betriebssystem herunter und folgen Sie den nachstehenden Schritten. Klicken Sie nach der Installation auf dem Bildschirm **Get Started** auf **Accept & Install** — AMD Sync startet nach Abschluss automatisch.

### Windows

[AMDSyncInstaller.exe herunterladen](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Doppelklicken Sie auf `AMDSyncInstaller.exe`.
2. Klicken Sie auf **Accept & Install**.

> Wenn die Windows-Firewall eine Aufforderung anzeigt, erlauben Sie AMD Sync den Netzwerkzugriff, damit es den Ryzen AI Halo über SSH erreichen kann.

### Linux

Klicken Sie auf den Link, um Ihr bevorzugtes Format herunterzuladen:

| Format | Download | Installationsbefehl |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Hinweis:** Das Ubuntu App Center kann eine lokal geöffnete `.deb`-Datei als *„Potenziell unsicher"* kennzeichnen. Das ist die übliche Warnung für jedes lokale Installationsprogramm eines Drittanbieters. Wenn das Doppelklicken der `.deb`-Datei fehlschlägt, verwenden Sie den obigen Terminalbefehl.

---

## Schritt 3 — Verbindung zu Ihrem Ryzen AI Halo herstellen

Beim ersten Start zeigt AMD Sync das Formular **Add a Remote Device** an. Füllen Sie es mit den Werten aus der Registerkarte **Remote** des Developer Centers aus.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Feld | Hinweise |
|-------|-------|
| **Device Name** *(optional)* | Eine benutzerfreundliche Bezeichnung wie `Ryzen AI Halo`. Standardmäßig `Device 1`, `Device 2`, … |
| **Hostname or IP** | Aus der Registerkarte Remote |
| **SSH Port** | Aus der Registerkarte Remote (nur Zahlen) |
| **Username** | Ihr Betriebssystem-Kontoname auf dem Ryzen AI Halo |
| **Password** | Ihr Betriebssystem-Anmeldepasswort — wird während der Eingabe maskiert |

Klicken Sie auf **Add Device**. Nach einem kurzen Ladebildschirm sehen Sie **„Connection Successful"** und gelangen zur Startansicht, die sich in Ihrem Systemtray befindet. Klicken Sie außerhalb des Fensters, um es zu schließen; AMD Sync läuft weiter im Hintergrund und ist nur einen Klick entfernt.

> **Wenn die Verbindung fehlschlägt,** kehrt AMD Sync mit Ihren erhaltenen Werten zum Formular zurück. Die üblichen Ursachen sind ein deaktivierter SSH-Dienst auf dem Ryzen AI Halo, ein falsches Passwort oder unterschiedliche Netzwerke der beiden Geräte.

---

## Schritt 4 — Ihr erstes Remote-Tool starten

Die Startansicht bietet fünf Komponenten mit einem Klick — alle verfügbar, unabhängig davon, welches Betriebssystem der Client und der Ryzen AI Halo verwenden.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponente | Was sie tut |
|-----------|--------------|
| **Directory** | Wählt den Ordner auf dem Ryzen AI Halo, in dem VS Code, Terminal und JupyterLab geöffnet werden. Standardmäßig ein verwalteter Arbeitsbereich `Documents/AMD_Sync`. |
| **VS Code** | Öffnet VS Code lokal mit einem SSH-Tunnel in den ausgewählten Ordner. |
| **Terminal** | Öffnet ein lokales, über SSH mit dem Ryzen AI Halo verbundenes Terminal im ausgewählten Ordner. |
| **JupyterLab** | Startet ein über SSH mit dem Ryzen AI Halo verbundenes Notebook-Projekt, beschränkt auf den ausgewählten Ordner. |
| **Live Metrics** | Echtzeitansicht der GPU-, Arbeitsspeicher- und CPU-Auslastung auf dem Ryzen AI Halo. |

### VS Code ausprobieren

Probieren Sie für Ihren ersten Start **VS Code** aus.

1. Belassen Sie **Directory** auf dem Standardwert `~/Documents/AMD_Sync`.
2. Klicken Sie auf **VS Code**.
3. AMD Sync erstellt `Documents/AMD_Sync/Project_1` auf dem Ryzen AI Halo und öffnet VS Code lokal, getunnelt in diesen Ordner.

Sie bearbeiten jetzt Dateien, die auf dem Ryzen AI Halo liegen, mit Ihrer lokalen VS Code-Konfiguration. Erstellen Sie `helloworld.py`, fügen Sie `print("hello world")` hinzu, öffnen Sie das integrierte Terminal (`` Ctrl + ` ``) und führen Sie es aus:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Die Statusleiste zeigt **SSH: Linux** an — der Beweis, dass Ihr Code auf dem Ryzen AI Halo läuft und nicht auf Ihrem Laptop.
### Terminal ausprobieren

Klicken Sie auf **Terminal**, um per SSH ohne Umweg über die Tastatur direkt in denselben Ordner zu gelangen.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Unter Windows ist **PowerShell** das Standardterminal – wechseln Sie bei Bedarf im Einstellungsmenü zu **Windows Command Prompt**. Unter Linux verwendet AMD Sync Ihr systemeigenes Standardterminal.

---

## So funktioniert das Verzeichnis

Das Dropdown-Menü **Directory** ist die wichtigste Steuerungsmöglichkeit in AMD Sync – es bestimmt, wo jedes von Ihnen gestartete Tool auf dem Ryzen AI Halo landet.

- **`~/Documents/AMD_Sync` (Standard)** — Wenn Sie von hier aus VS Code oder JupyterLab starten, wird automatisch ein neuer Projektordner angelegt (`Project_1`, `Project_2`, … für VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … für JupyterLab).
- **Vorhandene Projektordner** — Jeder direkte Unterordner von `AMD_Sync` (einschließlich Ordner, die Sie manuell auf dem Ryzen AI Halo erstellt haben) erscheint im Dropdown-Menü. Der zuletzt verwendete Ordner wird beim nächsten Mal zum Standard.
- **Benutzerdefinierte Pfade** — Geben Sie einen beliebigen absoluten Pfad ein, um einen Ordner an anderer Stelle auf dem Ryzen AI Halo zu öffnen. AMD Sync *öffnet* diesen lediglich – es werden keine Ordner außerhalb von `AMD_Sync` erstellt, und benutzerdefinierte Pfade werden zwischen den Sitzungen nicht gespeichert.

Funktioniert ein benutzerdefinierter Pfad nicht, teilt AMD Sync Ihnen den Grund mit: ungültige Syntax, der Ordner existiert nicht, oder der Pfad verweist auf eine Datei.

---

## Live-Metriken und JupyterLab

- **Live Metrics** — Ein Live-Dashboard für GPU-, Arbeitsspeicher- und CPU-Auslastung. Der schnellste Weg, um zu bestätigen, dass ein Remote-Trainingslauf tatsächlich die Hardware auslastet.
- **JupyterLab** — Ein vollständiges Notebook-Projekt, das per SSH mit dem Ryzen AI Halo verbunden ist und über ein eigenes integriertes Terminal verfügt, um Notebook-Zellen und Shell-Befehle zu kombinieren, ohne die Benutzeroberfläche zu verlassen.

---

## Einstellungen und mehrere Geräte

Das Menü **Settings** enthält drei Registerkarten:

| Registerkarte | Inhalt |
|-----|----------------|
| **Devices** | Listet jeden Ryzen AI Halo auf, mit dem Sie sich bereits erfolgreich verbunden haben. Erneut verbinden, Zugangsdaten bearbeiten oder ein neues Gerät hinzufügen. |
| **Information** | Links zur Dokumentation und zum Forum-Support. |
| **Customize** | Die App auf dem Desktop neu positionieren, den Terminaltyp wechseln (nur Windows) und nach Updates für AMD Sync suchen. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Terminaltyp (Windows)** — Wählen Sie zwischen **PowerShell** (Standard) und **Windows Command Prompt**.
- **Terminaltyp (Linux)** — Nur das Standard-Systemterminal ist verfügbar.
- **App-Updates** — Auf dieser Registerkarte können Sie direkt aus der Benutzeroberfläche heraus nach neuen AMD Sync-Versionen suchen und diese installieren; ein separates Update-Tool ist nicht erforderlich.

> Ein Gerät erscheint erst nach einer erfolgreichen ersten Verbindung unter **Devices**, sodass fehlgeschlagene Verbindungsversuche die Liste nicht überladen.

---

## Fehlerbehebung

- **Verbindung schlägt sofort fehl** — Vergewissern Sie sich, dass der SSH-Server auf der Registerkarte **Remote** im Developer Center des Ryzen AI Halo aktiviert ist.
- **Fehlermeldung „Falsches Passwort“** — Verwenden Sie Ihr **Betriebssystem-Anmeldepasswort** auf dem Ryzen AI Halo, nicht Passwörter aus dem Developer Center.
- **Schaltfläche „VS Code“ reagiert nicht** — Installieren Sie VS Code auf Ihrem Client-Rechner von [code.visualstudio.com](https://code.visualstudio.com).
- **AMD Sync-Symbol im Tray fehlt (Linux/GNOME)** — Installieren und aktivieren Sie die AppIndicator-Erweiterung.
- **`.deb`-Datei lässt sich nicht über den Dateimanager öffnen** — Verwenden Sie `sudo apt install ./AMDSyncInstaller.deb` in einem Terminal.

---