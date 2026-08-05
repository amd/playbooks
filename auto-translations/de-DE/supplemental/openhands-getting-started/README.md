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
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Überblick

[OpenHands](https://github.com/All-Hands-AI/OpenHands) ist ein KI-Softwareagent,
der Code schreiben, Befehle ausführen, im Web browsen und Dateien in einem echten
Arbeitsbereich bearbeiten kann. Anstatt Vorschläge aus einem Chatfenster zu kopieren,
verweisen Sie den Agenten auf einen Projektordner und lassen ihn die Arbeit erledigen:
eine Funktion implementieren, einen Fehler beheben, Tests schreiben oder eine
Codebasis erklären.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) ist die empfohlene
Browser-UI zum Ausführen von OpenHands. Ein einzelner `agent-canvas`-Befehl startet
den Agent-Server, das Automatisierungs-Backend und das Web-Frontend zusammen,
sodass Sie eine Konversation mit dem Agenten aus Ihrem Browser führen können.

Damit alles auf Ihrem AMD-System bleibt, kommuniziert der Agent mit einem lokalen
Modell, das von Lemonade Server bereitgestellt wird. Lemonade stellt dieses Modell
über eine OpenAI-kompatible API zur Verfügung, sodass Agent Canvas es wie jeden
anderen OpenAI-artigen Endpunkt konfigurieren kann, während das Modell, Ihr Code
und der Konversationskontext alle auf Ihrem Rechner verbleiben.

In diesem Playbook starten Sie ein lokales Modell, starten Agent Canvas, richten
es auf dieses Modell aus und führen Ihre erste Coding-Aufgabe an einem echten
Projektordner aus.

## Was Sie lernen werden

- Wie Sie Lemonade Server starten und bestätigen, dass ein lokales Modell auf
  Chat-Anfragen antwortet
- Wie Sie Agent Canvas aus dem npm-Paket installieren und starten
- Wie Sie Agent Canvas so konfigurieren, dass es ein lokales Lemonade-Modell als
  LLM verwendet
- Wie Sie eine OpenHands-Konversation starten und beobachten, wie der Agent
  Dateien bearbeitet und Befehle in einem Arbeitsbereich ausführt
- Wie Sie überprüfen, was der Agent geändert hat, und ihn mit Folgenachrichten
  steuern

## Kernkonzepte

| Konzept | Was es ist | Wo es in diesem Playbook einzuordnen ist |
| --- | --- | --- |
| Lemonade Server | Eine lokale LLM-Serving-Plattform, die für AMD-Hardware entwickelt wurde und eine OpenAI-kompatible API bereitstellt. Ihre Daten verlassen niemals Ihren Rechner. | Führt das Modell aus, das den Agenten antreibt. |
| OpenHands | Ein KI-Softwareagent, der Dateien liest und bearbeitet, Shell-Befehle ausführt und innerhalb eines Arbeitsbereichs im Web browst. | Der Agent, den Sie über den Chat steuern. |
| Agent Canvas | Die Browser-UI und das Backend, die OpenHands-Konversationen ausführen und Tool-Aufrufe sowie Dateiänderungen anzeigen. | Startet den Stack und hostet Ihre Konversation. |
| Arbeitsbereich | Der Projektordner, den der Agent lesen und ändern darf. | Das Ziel der Änderungen und Befehle des Agenten. |

<!-- @device:stx,krk -->
> [!NOTE]
> Coding-Agent-Workflows profitieren von einem größeren Modell und Kontextfenster.
> Verwenden Sie mindestens 32 GB Systemspeicher und bevorzugen Sie 64 GB oder mehr
> für größere GGUF-Modelle.
<!-- @device:end -->

## Voraussetzungen

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Sie benötigen:

- Lemonade Server installiert und in der Lage, das unten genannte Modell bereitzustellen.
- Node.js 22.12 oder höher und `npm` (wird von der `agent-canvas`-CLI verwendet).
- `uv`, den Python-Paketmanager, den Agent Canvas zur Verwaltung der Agent-Server-Umgebung
  verwendet. Falls Ihr System dies noch nicht hat, installieren Sie es über den
  [uv-Installationsleitfaden](https://docs.astral.sh/uv/getting-started/installation/),
  bevor Sie Agent Canvas starten.
- Einen Projektordner, in dem gearbeitet werden soll. Dies kann jedes lokale
  Git-Repository oder Code-Verzeichnis sein, an dem der Agent arbeiten soll.

<!-- @device:halo,halo_box,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

## 1. Lemonade Server starten

Starten Sie das Modell über die Lemonade-CLI:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

Lemonade stellt eine OpenAI-kompatible API bereit unter:

```text
http://127.0.0.1:13305/api/v1
```



## 2. Das lokale Modell überprüfen

Bestätigen Sie, dass Lemonade das ausgewählte Modell bereitstellen kann:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Senden Sie dann eine kleine Chat-Anfrage:

```bash
curl -sS "http://127.0.0.1:13305/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.6-35B-A3B-GGUF",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```

Wenn dies ein `choices`-Array zurückgibt, ist Lemonade bereit für Agent Canvas.

## 3. Agent Canvas installieren und starten

Installieren Sie das veröffentlichte Agent Canvas-Paket global:

```bash
npm install -g @openhands/agent-canvas
```

Starten Sie anschließend den vollständigen Stack von einem Terminal aus:

```bash
agent-canvas
```

Standardmäßig startet Agent Canvas unter `http://localhost:8000`. Öffnen Sie
diese URL in Ihrem Browser. Falls Port 8000 bereits belegt ist, übergeben Sie
`--port` (oder `-p`), wenn Sie Agent Canvas starten:

```bash
agent-canvas --port 3000
```

Derselbe Befehl funktioniert auch in PowerShell unter Windows. Öffnen Sie dann
stattdessen `http://localhost:3000`. Das Standard-Local-Backend sollte auf dem
Startbildschirm als „healthy“ angezeigt werden.

Der Befehl `agent-canvas` startet den Agent-Server, das Automatisierungs-Backend
und das Web-Frontend zusammen. Sie benötigen nur diesen einen Befehl, um
OpenHands lokal auszuführen.

## 4. Das lokale LLM konfigurieren

Beim ersten Start öffnet Agent Canvas einen Onboarding-Ablauf. In diesem Ablauf:

1. Belassen Sie **OpenHands** als ausgewählten Agenten und klicken Sie auf **Next**.
2. Wählen Sie unter **Set up your LLM** die Option **Advanced**.
3. Belassen Sie **Authentication** auf **API key**.
4. Setzen Sie **Custom Model** auf `openai/Qwen3.6-35B-A3B-GGUF`.
5. Setzen Sie **Base URL** auf `http://127.0.0.1:13305/api/v1`.
6. Geben Sie bei **API Key** einen beliebigen nicht leeren Platzhalter ein, z. B.
   `lemonade-local`. Lemonade benötigt keinen echten Schlüssel, aber der
   OpenHands-Client benötigt einen Wert zum Senden.
7. Klicken Sie auf **Next**.

Die abgeschlossenen Advanced-Einstellungen sollten wie folgt aussehen. Das
API-Key-Feld wird von der UI maskiert.

![Agent Canvas Erstnutzungs-LLM-Advanced-Einstellungen mit dem Lemonade-Modell und der lokalen Base-URL](assets/01-llm-advanced-settings.png)

Agent Canvas speichert diese Werte als LLM-Profil. Falls Ihre Version Sie
auffordert, dieses Profil zu benennen, verwenden Sie einen Namen ohne
Leerzeichen wie `lemonade-local`. Wenn Sie später Modelle wechseln, öffnen Sie
**Settings > LLM** und aktualisieren Sie dieselben Advanced-Felder. Sie können
gespeicherte Profile über die Chat-Eingabe mit dem Befehl `/model` wechseln.

## 5. Einen Arbeitsbereich öffnen

Der Agent kann nur Dateien innerhalb eines von Ihnen ausgewählten Arbeitsbereichs
lesen und ändern. Bevor Sie eine Aufgabe starten, richten Sie Agent Canvas auf
Ihren Projektordner aus:

1. Wählen Sie auf dem Startbildschirm **Open Workspace**.
2. Wählen Sie den Ordner aus, der Ihr Projekt enthält (zum Beispiel ein
   Git-Repository, an dem der Agent arbeiten soll).
3. Starten Sie eine neue Konversation in diesem Arbeitsbereich.

Alles, was der Agent tut – Dateien lesen, Befehle ausführen, Code bearbeiten –
ist auf diesen Arbeitsbereich beschränkt.

![Agent Canvas Startbildschirm nach dem Onboarding](assets/02-agent-canvas-home.png)
## 6. Führen Sie Ihre erste Coding-Aufgabe aus

Öffnen Sie den Workspace, wählen Sie das lokale LLM aus und geben Sie dann eine konkrete Aufgabe in den Chat ein. Eine gute erste Aufgabe ist klein und überprüfbar, zum Beispiel:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Verfolgen Sie den Ablauf der Unterhaltung. OpenHands wird:

- den Workspace lesen, um die Struktur zu verstehen.
- `hello.py` mit der angeforderten Funktion und einem Testblock erstellen.
- optional `python3 hello.py` ausführen, um die Ausgabe zu überprüfen.
- im Chat berichten, was es getan hat, sowie eventuelle Befehlsausgaben.

Sie sollten sehen, wie die neue Datei im Workspace erscheint, und die abschließende Nachricht des Agenten sollte die vorgenommene Änderung beschreiben. Dies ist der entscheidende Moment: Der Agent hat echten Code in Ihrem Projektordner geschrieben und ausgeführt.

## 7. Überprüfen und steuern Sie den Agenten

Nachdem der Agent einen Schritt abgeschlossen hat, überprüfen Sie seine Arbeit, bevor Sie den nächsten akzeptieren:

- **Dateiänderungen**: Verwenden Sie den Datei-Browser des Workspace oder die Diff-Ansicht des Agenten, um genau zu sehen, was hinzugefügt, geändert oder gelöscht wurde.
- **Befehlsausgabe**: Erweitern Sie einen vom Agenten ausgeführten Befehl, um stdout, stderr und den Exit-Code zu sehen.
- **Rückmeldungen**: Falls das Ergebnis nicht Ihren Erwartungen entspricht, antworten Sie in derselben Unterhaltung mit einer Korrektur. Der Agent behält den bisherigen Kontext bei und arbeitet an denselben Dateien weiter.

Wenn der Test beispielsweise nicht die erwartete Begrüßung ausgibt, antworten Sie:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Der Agent wird die Datei erneut lesen, den Befehl ausführen, das Problem diagnostizieren und die Datei erneut bearbeiten – alles innerhalb derselben Unterhaltung.

## Fehlerbehebung

- **`agent-canvas` ist nicht im PATH:** Installieren Sie es erneut mit
  `npm install -g @openhands/agent-canvas` und stellen Sie sicher, dass das globale npm-Binärverzeichnis
  im PATH enthalten ist. Führen Sie unter Windows `npm config get prefix` aus; das
  zurückgegebene Verzeichnis, häufig `%APPDATA%\npm` oder `%USERPROFILE%\.npm-global`,
  muss im Benutzer-PATH enthalten sein, bevor `agent-canvas` aus einem neuen
  Terminal gestartet werden kann.
- **`npm install -g` schlägt mit einem Berechtigungsfehler fehl:** Richten Sie ein benutzereigenes
  globales npm-Verzeichnis ein, öffnen Sie das Terminal dann erneut und installieren Sie Agent Canvas erneut.

  <!-- @os:linux -->
  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
  <!-- @os:end -->

  <!-- @os:windows -->
  ```powershell
  New-Item -ItemType Directory -Force "$env:USERPROFILE\.npm-global"
  npm config set prefix "$env:USERPROFILE\.npm-global"
  $env:Path = "$env:USERPROFILE\.npm-global;$env:Path"
  npm install -g @openhands/agent-canvas
  ```

  Um die Windows-PATH-Änderung dauerhaft zu machen, fügen Sie `%USERPROFILE%\.npm-global` zu
  Ihrem Benutzer-PATH unter **Einstellungen > System > Info > Erweiterte Systemeinstellungen >
  Umgebungsvariablen** hinzu und öffnen Sie ein neues Terminal.
  <!-- @os:end -->
- **Die Benutzeroberfläche lädt, aber das Backend zeigt „unhealthy“ an:** Warten Sie einige Sekunden, bis der
  Agent-Server den Startvorgang abgeschlossen hat, und aktualisieren Sie dann die Seite. Bleibt der Status weiterhin „unhealthy“, starten Sie
  `agent-canvas` neu und überprüfen Sie die Terminal-Ausgabe auf Fehler.
- **Lemonade-Chat-Anfragen schlagen mit einem Verbindungsfehler fehl:** Stellen Sie sicher, dass
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` erfolgreich ausgeführt wird und dass
  Lemonade das Modell weiterhin bereitstellt, mit `lemonade status`.
- **Der Agent meldet einen Fehler zur Kontextlänge oder zum Token-Limit:** Starten Sie
  Lemonade mit einem größeren `ctx_size` neu (zum Beispiel `ctx_size=65536`), und beginnen Sie eine
  neue Unterhaltung, damit der Agent keinen übermäßig großen Verlauf mitführt.
- **Der Agent liefert minderwertige oder unvollständige Bearbeitungen:** Wechseln Sie zu einem größeren
  Modell in Lemonade oder geben Sie dem Agenten eine kleinere, konkretere Aufgabe und lassen Sie ihn diese
  abschließen, bevor Sie die nächste Änderung anfordern.
- **`uv` fehlt:** Installieren Sie es über
  [den uv-Installationsleitfaden](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas verwendet `uv`, um die Python-Umgebung des Agent-Servers zu verwalten.

## Nächste Schritte

- Probieren Sie eine größere Aufgabe im selben Workspace aus, etwa das Hinzufügen einer Unit-Test-Datei oder
  das Beheben eines bekannten Fehlers, und überprüfen Sie die Diff-Ansicht des Agenten, bevor Sie die Änderung übernehmen.
- Verbinden Sie unter **Customize** einen MCP-Server wie GitHub oder Slack, damit
  der Agent während der Arbeit Issues lesen oder Updates posten kann.
- Speichern Sie mehrere LLM-Profile (ein schnelles, kleines Modell und ein leistungsstärkeres, großes Modell) und
  wechseln Sie mit `/model` mitten in der Unterhaltung zwischen ihnen.
- Fahren Sie fort mit [OpenHands-Automatisierungen](https://docs.openhands.dev/openhands/usage/automations/overview), um
  wiederkehrende Entwicklungsabläufe in geplante oder ereignisgesteuerte Agent-Ausführungen umzuwandeln.

## Ressourcen

- [OpenHands-Dokumentation](https://docs.openhands.dev/)
- [Agent Canvas – Überblick](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Agent Canvas – Einrichtung](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM-Profile und Modellkonfiguration](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Lemonade Server-Dokumentation](https://lemonade-server.ai/docs)