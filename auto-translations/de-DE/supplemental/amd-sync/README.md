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

## Überblick

**AMD Sync** verwandelt Ihren Laptop in ein Remote-Cockpit für die AMD Ryzen™ AI Halo. Überspringen Sie die manuelle SSH-, Schlüssel- und IDE-Einrichtung – installieren Sie AMD Sync und erhalten Sie per Klick Zugriff auf ein Remote-Terminal, VS Code, JupyterLab und ein Live-Dashboard für GPU/CPU/Speicher auf der Ryzen AI Halo.

Ihr lokaler Rechner bleibt vertraut; jeder Befehl, jedes Notebook und jedes Modell läuft auf der Ryzen AI Halo.

> **Tipp**: Diese Seite enthält alle neuen Aktualisierungen zu AMDSync. 

## Was Sie lernen werden

- Aktivieren von SSH auf der Ryzen AI Halo und Verbinden damit über AMD Sync
- Starten von VS Code, Terminal, JupyterLab und Live Metrics gegen die Ryzen AI Halo mit einem Klick
- Organisieren der Remote-Arbeit mithilfe der verwalteten Projektordner von AMD Sync

---

## Kernkonzepte

AMD Sync besteht aus zwei Seiten: einem **Client** (Ihr Laptop, auf dem die AMD Sync App läuft) und einem **Server** (die Ryzen AI Halo, auf der ein SSH-Server läuft, in den sich AMD Sync tunnelt). Alles, was Sie von AMD Sync aus starten – VS Code, ein Terminal, ein Notebook – öffnet sich lokal, wird aber auf der Ryzen AI Halo ausgeführt.

> **Unterstützte Clients:** Windows 11 und Linux. macOS wird nicht unterstützt.

---

## Schritt 1 — SSH auf der Ryzen AI Halo aktivieren


> **Hinweis:** Unter Windows wird die Ryzen AI Halo mit *standardmäßig deaktiviertem* SSH-Server ausgeliefert. Unter Linux ist der SSH-Server *standardmäßig aktiviert*.

1. Öffnen Sie auf der Ryzen AI Halo das **AMD Ryzen™ AI Developer Center**.
2. Wechseln Sie zum Tab **Remote**.
3. Schalten Sie **SSH Server** ein.
4. Notieren Sie sich die unter **Server Information** angezeigten Werte für **IP Address**, **Port** und **Username** — diese fügen Sie gleich in AMD Sync ein.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Hinweis:** Dies ist das AMD Developer Center für Windows. Das für Linux kann eine abweichende Benutzeroberfläche haben, bietet jedoch ähnliche Remote-Funktionalität.

> **Tipp:** AMD Sync fragt nach dem **Betriebssystem-Anmeldepasswort** dieses Benutzers, nicht nach einem Passwort aus dem Developer Center.

---

## Schritt 2 — AMD Sync auf Ihrem Client installieren

AMD Sync läuft unter Windows 11 und Linux. Laden Sie das Installationsprogramm für Ihr Betriebssystem herunter und folgen Sie anschließend den unten stehenden Schritten. Klicken Sie nach der Installation auf **Accept & Install** im Bildschirm **Get Started** — AMD Sync startet nach Abschluss automatisch.

### Windows

[AMDSyncInstaller.exe herunterladen](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Doppelklicken Sie auf `AMDSyncInstaller.exe`.
2. Klicken Sie auf **Accept & Install**.

> Falls die Windows-Firewall eine Meldung anzeigt, erlauben Sie AMD Sync den Netzwerkzugriff, damit es die Ryzen AI Halo über SSH erreichen kann.

### Linux

Klicken Sie auf den Link, um Ihr bevorzugtes Format herunterzuladen:

| Format | Download | Installationsbefehl |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Hinweis:** Das Ubuntu App Center markiert eine lokal geöffnete `.deb`-Datei möglicherweise als *„Potenziell unsicher“*. Dies ist die übliche Warnung für jedes lokal installierte Programm von Drittanbietern. Falls das Doppelklicken der `.deb`-Datei fehlschlägt, verwenden Sie den oben genannten Terminalbefehl.

---

## Schritt 3 — Verbindung mit Ihrer Ryzen AI Halo herstellen

Beim ersten Start zeigt AMD Sync das Formular **Add a Remote Device** an. Füllen Sie es mit den Werten aus dem Tab **Remote** des Developer Centers aus.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Feld | Hinweise |
|-------|-------|
| **Device Name** *(optional)* | Eine aussagekräftige Bezeichnung wie `Ryzen AI Halo`. Standardmäßig `Device 1`, `Device 2`, … |
| **Hostname or IP** | Aus dem Tab Remote |
| **SSH Port** | Aus dem Tab Remote (nur Zahlen) |
| **Username** | Ihr Benutzerkontoname auf der Ryzen AI Halo |
| **Password** | Ihr Betriebssystem-Anmeldepasswort — wird während der Eingabe maskiert |

Klicken Sie auf **Add Device**. Nach einem kurzen Ladebildschirm sehen Sie **„Connection Successful“** und gelangen zur Startansicht, die sich in Ihrem Systemtray befindet. Klicken Sie außerhalb des Fensters, um es zu schließen; AMD Sync läuft weiter im Hintergrund und ist nur einen Klick entfernt.

> **Falls die Verbindung fehlschlägt,** kehrt AMD Sync mit den erhaltenen Werten zum Formular zurück. Die üblichen Ursachen sind ein deaktivierter SSH-Dienst auf der Ryzen AI Halo, ein falsches Passwort oder dass sich die beiden Geräte in unterschiedlichen Netzwerken befinden.

---

## Schritt 4 — Ihr erstes Remote-Tool starten

Die Startansicht bietet Ihnen fünf Komponenten per Klick — alle verfügbar, unabhängig davon, welches Betriebssystem Client und Ryzen AI Halo verwenden.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponente | Funktion |
|-----------|--------------|
| **Directory** | Wählt den Ordner auf der Ryzen AI Halo aus, in dem VS Code, Terminal und JupyterLab geöffnet werden. Standardmäßig ein verwalteter Arbeitsbereich `Documents/AMD_Sync`. |
| **VS Code** | Öffnet VS Code lokal mit einem SSH-Tunnel in den ausgewählten Ordner. |
| **Terminal** | Öffnet ein lokales Terminal, das per SSH mit der Ryzen AI Halo verbunden ist, im ausgewählten Ordner. |
| **JupyterLab** | Startet ein Notebook-Projekt, das per SSH mit der Ryzen AI Halo verbunden ist, beschränkt auf den ausgewählten Ordner. |
| **Live Metrics** | Echtzeitansicht der GPU-, Speicher- und CPU-Auslastung auf der Ryzen AI Halo. |

### VS Code ausprobieren

Probieren Sie für Ihren ersten Start **VS Code** aus. Die folgenden Anweisungen gelten für Linux, aber die Windows-Erfahrung ist ähnlich.

1. Belassen Sie **Directory** auf dem Standardwert `~/Documents/AMD_Sync`.
2. Klicken Sie auf **VS Code**.
3. AMD Sync erstellt `Documents/AMD_Sync/Project_1` auf der Ryzen AI Halo und öffnet VS Code lokal, getunnelt in diesen Ordner.

Sie bearbeiten nun Dateien, die auf der Ryzen AI Halo liegen, mit Ihrer lokalen VS Code-Einrichtung. Erstellen Sie `helloworld.py`, fügen Sie `print("hello world")` hinzu, öffnen Sie das integrierte Terminal (`` Ctrl + ` ``) und führen Sie es aus:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Die Statusleiste zeigt **SSH: Linux** — der Beweis, dass Ihr Code auf der Ryzen AI Halo läuft und nicht auf Ihrem Laptop.
### Terminal ausprobieren

Klicken Sie auf **Terminal**, um per SSH direkt in denselben Ordner zu gelangen, ohne die Tastatur zu verlassen.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Unter Windows ist **PowerShell** das Standardterminal — wechseln Sie bei Bedarf im Einstellungsmenü zu **Windows Command Prompt**. Unter Linux verwendet AMD Sync Ihr systemweites Standardterminal.

---

## So funktioniert das Verzeichnis

Das Dropdown-Menü **Directory** ist die wichtigste Steuerung in AMD Sync — es entscheidet, wo jedes von Ihnen gestartete Tool auf dem Ryzen AI Halo landet.

- **`~/Documents/AMD_Sync` (Standard)** — Wenn Sie VS Code oder JupyterLab von hier aus starten, wird automatisch ein neuer Projektordner erstellt (`Project_1`, `Project_2`, … für VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … für JupyterLab).
- **Vorhandene Projektordner** — Jedes unmittelbare Unterverzeichnis von `AMD_Sync` (einschließlich Ordner, die Sie manuell auf dem Ryzen AI Halo erstellt haben) erscheint im Dropdown-Menü. Der zuletzt verwendete Ordner wird beim nächsten Mal zum Standard.
- **Benutzerdefinierte Pfade** — Geben Sie einen beliebigen absoluten Pfad ein, um einen Ordner an anderer Stelle auf dem Ryzen AI Halo zu öffnen. AMD Sync *öffnet* ihn nur — es werden keine Ordner außerhalb von `AMD_Sync` erstellt, und benutzerdefinierte Pfade werden nicht zwischen Sitzungen gespeichert.

Wenn ein benutzerdefinierter Pfad nicht funktioniert, teilt AMD Sync Ihnen den Grund mit: ungültige Syntax, der Ordner existiert nicht, oder der Pfad verweist auf eine Datei.

---

## Live-Metriken und JupyterLab

- **Live Metrics** — Ein Live-Dashboard für GPU-, Speicher- und CPU-Auslastung. Der schnellste Weg, um zu bestätigen, dass ein entfernter Trainingslauf die Hardware tatsächlich auslastet.
- **JupyterLab** — Ein vollständiges Notebook-Projekt, das per SSH mit dem Ryzen AI Halo verbunden ist, mit einem eigenen integrierten Terminal, um Notebook-Zellen und Shell-Befehle zu mischen, ohne die Benutzeroberfläche zu verlassen.

---

## Einstellungen und mehrere Geräte

Das Menü **Settings** verfügt über drei Registerkarten:

| Registerkarte | Was sie abdeckt |
|-----|----------------|
| **Devices** | Listet jeden Ryzen AI Halo auf, mit dem Sie sich erfolgreich verbunden haben. Verbindung wiederherstellen, Anmeldedaten bearbeiten oder ein neues Gerät hinzufügen. |
| **Information** | Links zur Dokumentation und zum Forum-Support. |
| **Customize** | Positionieren Sie die App auf Ihrem Desktop neu, wechseln Sie den Terminaltyp (nur Windows) und suchen Sie nach AMD Sync-Updates. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Terminaltyp (Windows)** — Wählen Sie zwischen **PowerShell** (Standard) und **Windows Command Prompt**.
- **Terminaltyp (Linux)** — Es ist nur das systemweite Standardterminal verfügbar.
- **App-Updates** — Auf dieser Registerkarte können Sie direkt in der Benutzeroberfläche nach neuen AMD Sync-Versionen suchen und sie installieren; ein separates Update-Tool ist nicht erforderlich.

> Ein Gerät erscheint erst nach einer erfolgreichen ersten Verbindung unter **Devices**, sodass fehlgeschlagene Versuche die Liste nicht überladen.

---

## Fehlerbehebung

- **Verbindung schlägt sofort fehl** — Vergewissern Sie sich, dass der SSH-Server auf der Registerkarte **Remote** im Developer Center des Ryzen AI Halo aktiviert ist.
- **Fehler „Falsches Passwort“** — Verwenden Sie Ihr **Betriebssystem-Anmeldepasswort** auf dem Ryzen AI Halo, nicht Passwörter aus dem Developer Center.
- **Die Schaltfläche VS Code reagiert nicht** — Installieren Sie VS Code auf Ihrem Client-Rechner von [code.visualstudio.com](https://code.visualstudio.com).
- **AMD Sync-Taskleistensymbol fehlt (Linux/GNOME)** — Installieren und aktivieren Sie die AppIndicator-Erweiterung.
- **Die `.deb`-Datei lässt sich nicht über den Dateimanager öffnen** — Verwenden Sie `sudo apt install ./AMDSyncInstaller.deb` in einem Terminal.
- **Das Setup erscheint bei jedem Start erneut (Linux)**: Entsperren Sie Ihren Login-Schlüsselbund oder starten Sie mit `--password-store=gnome-libsecret` und führen Sie das Setup anschließend einmal erneut durch.

---