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

Entwickler verbringen viel Zeit mit kleinen, wiederkehrenden Aufgabenschleifen:
das Überprüfen von markierten Pull Requests, das Beantworten von GitHub-Kommentaren,
das Sichten neuer Issues, das Umwandeln von Slack-Threads in Standup-Notizen oder
Incident-Follow-ups sowie das Verfolgen von Release- oder Forschungssignalen.
Jede dieser Schleifen ist vertraut, erfordert aber dennoch Urteilsvermögen: den
richtigen Kontext sammeln, entscheiden, was wichtig ist, und ein klares Update
dort veröffentlichen, wo das Team bereits arbeitet.

[OpenHands-Automatisierungen](https://docs.openhands.dev/openhands/usage/automations/overview)
verwandeln diese Schleifen in zeitgesteuerte oder ereignisgesteuerte
Agent-Konversationen: Durchläufe, bei denen ein KI-Softwareagent Kontext lesen,
Tools aufrufen und ein Update erstellen kann. Die gemeinsam genutzten
Automatisierungsvorlagen im OpenHands-Erweiterungskatalog folgen diesem Muster
für die Überprüfung von GitHub-Pull-Requests, die Überwachung von Repositories,
die Linear-Issue-Triage, Incident-Retrospektiven, Slack-Standup-Digests und
Forschungsberichte: Eine Automatisierung wird aktiviert, verwendet konfigurierte
Integrationen wie GitHub oder Slack, um Kontext abzurufen, wertet diesen Kontext
mit einem Large Language Model (LLM) aus und schreibt ein Ergebnis zurück.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) ist die lokale
Steuerungsebene zum Erstellen und Testen dieser Automatisierungen. In diesem
Playbook betreibt es einen OpenHands Agent Server, den Backend-Prozess, der
Agent-Konversationen ausführt, und verbindet den Agenten mit externen Diensten
wie GitHub und Slack.

Um den Workflow auf Ihrem AMD-System zu halten, kommuniziert der Agent mit
einem lokalen Modell, das von Lemonade Server bereitgestellt wird. Lemonade
stellt dieses Modell über eine OpenAI-kompatible API zur Verfügung, sodass
Agent Canvas es wie einen entfernten OpenAI-artigen Endpunkt konfigurieren
kann, während Modell, Prompt und Workflow-Kontext lokal bleiben.

In diesem Playbook erstellen Sie eine konkrete Automatisierung: einen
zeitgesteuerten GitHub-zu-Slack-Entwicklungsdigest. Er verwendet GitHub, um
aktuelle Repository-Aktivitäten zu prüfen, Slack, um den Digest zu
veröffentlichen, Agent Canvas API-Aufrufe, um die Automatisierung zu
konfigurieren und zu testen, sowie Lemonade, um das LLM lokal auszuführen.

![Architekturdiagramm mit GitHub MCP, OpenHands-Automatisierung, Lemonade Server und Slack MCP](assets/00-architecture-overview.png)

## Was Sie lernen werden

- Wie Sie Lemonade Server starten und überprüfen, ob ein lokales Modell auf Chat-Anfragen antwortet
- Wie Sie Agent Canvas starten und dessen Agent Server auf ein lokales LLM ausrichten
- Wie Sie GitHub- und Slack-MCP-Server (Model Context Protocol) über die Agent Server API installieren
- Wie Sie eine zeitgesteuerte OpenHands-Automatisierung erstellen und auslösen, die einen Entwicklungsdigest an Slack sendet
- Wie Sie die häufigsten Fehler bei lokalen Modellen und Automatisierungen beheben

## Kernkonzepte

| Konzept | Was es ist | Wo es in diesem Playbook eingesetzt wird |
| --- | --- | --- |
| Lemonade Server | Eine lokale LLM-Serving-Plattform für AMD-Hardware, die eine OpenAI-kompatible API bereitstellt. Ihre Daten verlassen niemals Ihren Rechner. | Betreibt das Modell, das den Agenten antreibt. |
| OpenHands Agent Server | Der Backend-Prozess, der OpenHands-Agent-Konversationen ausführt. | Hostet den Agenten, sein LLM-Profil und seine MCP-Server. |
| Agent Canvas | Die lokale Steuerungsebene für OpenHands, die den Agent Server sowie eine Benutzeroberfläche zur Überprüfung von Agent-Durchläufen betreibt. | Startet die Backends und stellt die API bereit, die Sie aufrufen. |
| MCP-Server | Ein Model-Context-Protocol-Server, der einem Agenten Tools für einen externen Dienst wie GitHub oder Slack bereitstellt. | Ermöglicht dem Agenten, GitHub zu lesen und in Slack zu schreiben. |
| OpenHands-Automatisierung | Eine zeitgesteuerte oder ereignisgesteuerte Agent-Konversation, die Kontext abruft, darüber nachdenkt und irgendwo ein Ergebnis schreibt. | Der GitHub-zu-Slack-Digest, den Sie hier erstellen. |

<!-- @device:stx,krk -->
> [!NOTE]
> Coding-Agent-Workflows profitieren von einem größeren Modell und Kontextfenster.
> Verwenden Sie mindestens 32 GB Systemspeicher, für größere GGUF-Modelle
> werden 64 GB oder mehr bevorzugt.
<!-- @device:end -->

## Voraussetzungen

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Sie benötigen:

- Lemonade Server, installiert gemäß der Standard-
  [Lemonade-Installationsanleitung](https://lemonade-server.ai/docs/guide/install/).
- Node.js 22.12 oder höher sowie `npm`, um das veröffentlichte Agent Canvas
  CLI zu installieren und MCP-Server mit `npx` auszuführen.
- Ein aktuelles veröffentlichtes `@openhands/agent-canvas`-Paket mit
  schemagesteuerten Agent-Einstellungen, `LLMSummarizingCondenserSettings.max_tokens`
  und Unterstützung für LLM-`custom_tokenizer`.
- Das Python-Paket `transformers`, verfügbar in der Agent-Server-Umgebung.
  Es wird für die Chat-Template-Token-Zählung benötigt, wenn `custom_tokenizer`
  gesetzt ist.
- Ein GitHub-Token mit Lesezugriff auf das Repository, das zusammengefasst werden soll.
- Ein Slack-Bot-Token (`xoxb-...`) mit `chat:write`- und Kanal-Lesezugriff.
- Eine Slack-Team-ID (`T...`).
- Eine Slack-Kanal-ID (`C...`), in der der Digest gepostet werden soll.

Laden Sie die Slack-App in den Zielkanal ein, bevor Sie die Automatisierung testen.

## In diesem Playbook verwendete Variablen

<!-- @device:halo,halo_box,stx,krk -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

```bash
export LEMONADE_BASE_URL="http://127.0.0.1:13305/api/v1"
export LEMONADE_MODEL="Qwen3.6-35B-A3B-GGUF"
export OPENHANDS_LLM_MODEL="openai/${LEMONADE_MODEL}"
export QWEN_CUSTOM_TOKENIZER="Qwen/Qwen3.6-35B-A3B"
export CONDENSER_MAX_TOKENS="56000"
```

Die folgenden Werte werden in späteren Schritten in die Agent Canvas UI
eingegeben. Legen Sie sie hier fest, damit Sie sie dort einfügen können:

```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```

Verwenden Sie für `GITHUB_REPO_FILTER` einen expliziten `owner/repo`-Wert.
Breite Organisations-Wildcards können zu viel MCP-Kontext für lokale Modelle liefern.

## 1. Lemonade Server starten

Starten Sie das Modell über die Lemonade-CLI:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```

Lemonade stellt eine OpenAI-kompatible API bereit unter:

```text
http://127.0.0.1:13305/api/v1
```

Optional: Wenn Agent Canvas oder der Automatisierungs-Runner nicht auf demselben
Rechner laufen, veröffentlichen Sie den Lemonade-Endpunkt über einen sicheren
Tunnel und verwenden Sie die HTTPS-URL als LLM-Basis-URL:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Das lokale Modell überprüfen

Bestätigen Sie, dass Lemonade das ausgewählte Modell bereitstellen kann:

```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Senden Sie dann eine kleine Chat-Anfrage:

```bash
curl -sS "${LEMONADE_BASE_URL}/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"${LEMONADE_MODEL}"'",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```

Wenn dies ein `choices`-Array zurückgibt, ist Lemonade bereit für Agent Canvas.
## 3. Agent Canvas starten

Installieren Sie das veröffentlichte Agent-Canvas-Paket und starten Sie den vollständigen Stack:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Wenn die globale npm-Installation mit einem Berechtigungsfehler fehlschlägt, lesen Sie den Eintrag zur Fehlerbehebung bei npm-Berechtigungen weiter unten.

Standardmäßig startet Agent Canvas unter `http://localhost:8000`. Öffnen Sie diese URL in Ihrem Browser. Das lokale Standard-Backend sollte auf dem Startbildschirm als „healthy“ angezeigt werden.

Der Befehl `agent-canvas` startet den Agent-Server, das Automatisierungs-Backend und das Web-Frontend gemeinsam. Sie benötigen nur diesen einen Befehl, um OpenHands lokal auszuführen. Der Rest dieses Playbooks konfiguriert alles über die Agent-Canvas-Benutzeroberfläche in Ihrem Browser.

## 4. Konfigurieren des lokalen LLM in der Benutzeroberfläche

Beim ersten Start öffnet Agent Canvas einen Onboarding-Ablauf. In diesem Ablauf:

1. Behalten Sie **OpenHands** als ausgewählten Agenten bei und klicken Sie auf **Next**.
2. Wählen Sie unter **Set up your LLM** die Option **Advanced** aus.
3. Belassen Sie **Authentication** auf **API key**.
4. Setzen Sie **Custom Model** auf den Wert von `OPENHANDS_LLM_MODEL`,
   `openai/Qwen3.6-35B-A3B-GGUF`.
5. Setzen Sie **Base URL** auf `http://127.0.0.1:13305/api/v1`.
6. Geben Sie bei **API Key** einen beliebigen nicht leeren Platzhalter ein, z. B. `lemonade-local`.
   Lemonade benötigt keinen echten Schlüssel, aber der OpenHands-Client benötigt
   einen Wert, um ihn zu senden.

Die Verbindungsfelder sollten wie folgt aussehen. Das Feld für den API-Schlüssel wird von der Benutzeroberfläche maskiert.

![Erweiterte LLM-Einstellungen von Agent Canvas beim ersten Start mit dem Lemonade-Modell und der lokalen Basis-URL](assets/01-llm-advanced-settings.png)

Wählen Sie dann **All** aus und legen Sie die zusätzlichen Felder für das lokale Modell fest:

1. Scrollen Sie zu **Custom Tokenizer** und setzen Sie es auf `Qwen/Qwen3.6-35B-A3B`.
2. Scrollen Sie zu **LiteLLM Extra Body** und setzen Sie es auf
   `{"enable_thinking": true}`.
3. Klicken Sie auf **Next**.

![Registerkarte „All“ der LLM-Einstellungen von Agent Canvas beim ersten Start mit dem benutzerdefinierten Qwen-Tokenizer](assets/02-llm-all-tokenizer-settings.png)

![Registerkarte „All“ der LLM-Einstellungen von Agent Canvas beim ersten Start mit konfiguriertem LiteLLM Extra Body](assets/03-llm-all-extra-body-settings.png)

Die LLM-Einstellungen sollten Folgendes zeigen:

| Feld | Wert |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Das Präfix `openai/` weist LiteLLM an, gegenüber dem Lemonade-Endpunkt eine OpenAI-kompatible Anfrageformatierung zu verwenden. Der benutzerdefinierte Tokenizer ist der ursprüngliche Hugging-Face-Tokenizer für das GGUF-Modell; er ermöglicht es OpenHands, dieselben Chat-Vorlagen-Token zu zählen, die der lokale Modellserver sieht. Das aktuelle Formular für die LLM-Ersteinrichtung zeigt keine Condenser-Einstellungen an. Falls Ihre Agent-Canvas-Version Condenser-Einstellungen später unter **Settings > LLM** anzeigt, verwenden Sie `llm_summarizing` und setzen Sie die maximale Token-Anzahl unterhalb des Lemonade-Kontextfensters, zum Beispiel `56000`.

## 5. Installation der GitHub- und Slack-MCP-Server

Öffnen Sie in der Agent-Canvas-Benutzeroberfläche **Customize** (oder **Settings > MCP**), um die MCP-Server hinzuzufügen, die dem Agenten Werkzeuge für GitHub und Slack bereitstellen. Token-Werte werden nur an Ihren lokalen Agent Server gesendet und als verschlüsselte Einstellungen gespeichert.

### GitHub-MCP-Server

Fügen Sie einen neuen MCP-Server mit folgenden Einstellungen hinzu:

| Feld | Wert |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = Ihr GitHub-Token |

Verwenden Sie ein GitHub-Token mit Lesezugriff auf das Repository, das zusammengefasst werden soll.

### Slack-MCP-Server

Fügen Sie einen zweiten MCP-Server mit folgenden Einstellungen hinzu:

| Feld | Wert |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = Ihre Digest-Kanal-ID |

Setzen Sie `SLACK_CHANNEL_IDS` auf die Digest-Kanal-ID (denselben Wert wie `SLACK_DIGEST_CHANNEL`), damit der Agent nicht jeden Slack-Kanal durchblättern muss.

Nachdem Sie beide Server hinzugefügt haben, verwenden Sie die Schaltfläche **Test** bei jedem, um zu bestätigen, dass er sich verbindet und Werkzeuge bereitstellt. Der GitHub-Server sollte GitHub-Werkzeuge auflisten, und der Slack-Server sollte Slack-Werkzeuge auflisten.

![MCP-Seite von Agent Canvas mit installierten GitHub- und Slack-Servern](assets/04-mcp-servers-installed.png)

## 6. Erstellen der Digest-Automatisierung

Öffnen Sie in der Agent-Canvas-Benutzeroberfläche die Seite **Automations** und erstellen Sie eine neue Automatisierung:

1. Wählen Sie **Create automation** und den Typ **Prompt preset** aus.
2. Setzen Sie den **Name** auf `GitHub Development Digest to Slack`.
3. Setzen Sie den **Prompt** auf den folgenden Text und ersetzen Sie die Platzhalter für Repository und Kanal durch Ihre eigenen Werte:

   ```text
   Use the GitHub MCP server for exactly one repository: your-org/your-repo.
   Inspect recent development activity since the previous weekday, including
   merged pull requests, newly opened or reopened pull requests, notable
   commits pushed to main or release branches, new issues, important issue
   updates, releases, risks, blockers, and review requests. Keep GitHub
   lookups small: inspect the latest 3 to 5 commits, pull requests, issues,
   and releases. Use the Slack MCP server to post directly to channel ID
   C0123456789. Keep the Slack message concise: title with date range, 3 to 7
   bullets, links back to GitHub, and a Needs attention section only if
   needed. End with: This digest was generated by an AI agent (OpenHands) on
   behalf of the user. Do not include secrets, raw tokens, private
   environment variables, or unrelated Slack messages.
   ```

4. Setzen Sie den **Trigger** auf **Cron** mit dem Zeitplan `0 9 * * 1-5` (9 Uhr an Wochentagen) und setzen Sie die **Timezone** auf Ihre Zeitzone, zum Beispiel `America/New_York`.
5. Setzen Sie das **Timeout** auf `900` Sekunden.
6. Speichern Sie die Automatisierung.

Die Detailseite der Automatisierung zeigt die neue Automatisierung mit ihrem Cron-Trigger und dem generierten Prompt-Preset-Einstiegspunkt.

![Detailseite der Agent-Canvas-Automatisierung nach der Erstellung](assets/05-automation-created.png)
## 7. Testen der Automatisierung

Öffnen Sie auf der Detailseite der Automatisierung in der Agent Canvas UI:

1. Klicken Sie auf **Run now** (oder **Dispatch**), um die Automatisierung sofort einmal auszuführen.
2. Beobachten Sie die Ausführungsliste auf derselben Seite. Der neueste Lauf sollte in den Status
   `COMPLETED` wechseln.
3. Öffnen Sie Ihren Ziel-Slack-Kanal. Er sollte den generierten Digest enthalten.

Sie müssen nicht auf den Cron-Zeitplan warten – **Run now** löst eine
Ausführung auf Abruf aus, sodass Sie den Prompt, die MCP-Verbindungen und das
Posten in Slack überprüfen können, bevor Sie sich auf den Zeitplan verlassen.

![Erfolgreich abgeschlossener Automatisierungslauf in Agent Canvas](assets/06-automation-run-completed.png)

![Slack-Kanal mit dem generierten OpenHands-Digest](assets/07-slackbot-message.png)

## Fehlerbehebung

- **Lemonade ist nicht erreichbar:** Starten Sie es mit dem Befehl
  `lemonade run "${LEMONADE_MODEL}"` aus Schritt 1 neu und führen Sie
  anschließend die Zustandsprüfung erneut aus.
- **`npm install -g` schlägt mit einem Berechtigungsfehler fehl:** Richten Sie
  unter Linux oder WSL ein benutzereigenes globales npm-Verzeichnis ein, fügen
  Sie es Ihrer Shell-Startdatei hinzu und installieren Sie Agent Canvas
  anschließend erneut:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

  Wenn Sie `zsh` verwenden, fügen Sie dieselbe Zeile `export PATH=...`
  stattdessen zu `~/.zshrc` hinzu.
- **Agent Canvas lehnt die LLM-Einstellungen nach dem Setzen von
  `custom_tokenizer` ab:** Installieren Sie `transformers` in der
  Python-Umgebung des Agent Server, starten Sie Agent Canvas bei Bedarf neu
  und versuchen Sie erneut, die LLM-Einstellungen zu speichern. OpenHands
  benötigt Transformers, um die Tokenizer-Chat-Vorlage zu laden, wenn
  `custom_tokenizer` gesetzt ist.
- **Agent Canvas kann Lemonade nicht erreichen:** Überprüfen Sie
  `curl -fsS "${LEMONADE_BASE_URL}/health"` und stellen Sie sicher, dass die
  im Ersteinrichtungs-LLM-Formular oder unter **Settings > LLM** eingegebene
  Basis-URL mit dem laufenden lokalen Endpunkt oder dem HTTPS-Tunnel
  übereinstimmt.
- **Die LLM-Einstellungen wurden nicht gespeichert:** Stellen Sie sicher, dass
  Sie nach der Eingabe der Werte auf **Next** geklickt haben. Öffnen Sie
  **Settings > LLM** erneut, um zu prüfen, ob die Werte übernommen wurden.
- **GitHub MCP kann private Repositories nicht sehen:** Stellen Sie sicher,
  dass das GitHub-Token Lesezugriff auf das Ziel-Repository hat und dass die
  Schaltfläche **Test** von MCP unter **Customize** GitHub-Tools anzeigt.
- **Slack kann Kanäle lesen, aber nicht posten:** Laden Sie die Slack-App in
  den Ziel-Kanal ein und stellen Sie sicher, dass der Bot über `chat:write`
  verfügt.
- **Die Automatisierung listet zu viele Slack-Kanäle auf:** Verwenden Sie eine
  Slack-Kanal-ID und setzen Sie `SLACK_CHANNEL_IDS` auf dem Slack-MCP-Server
  unter **Customize**.
- **Der Automatisierungslauf schlägt fehl oder überschreitet den Kontext:**
  Stellen Sie sicher, dass Lemonade mit `ctx_size=65536` gestartet wurde,
  dass für das OpenHands-LLM `custom_tokenizer` gesetzt ist, und verwenden Sie
  ein explizites Repository mit GitHub-Ergebnismengen, die auf 3 bis 5
  Einträge begrenzt sind. Wenn Ihre Agent-Canvas-Version
  Condenser-Einstellungen bietet, setzen Sie die maximale Token-Anzahl des
  Condensers unterhalb des Lemonade-Kontextfensters.

## Nächste Schritte

- Fügen Sie einen wöchentlichen, nur release-bezogenen Digest hinzu.
- Fügen Sie eine durch GitHub-Ereignisse ausgelöste Automatisierung für
  schnellere PR- oder Push-Benachrichtigungen hinzu.
- Leiten Sie denselben Digest an Notion, Linear oder ein anderes
  MCP-basiertes Tool weiter.

## Ressourcen

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Lemonade Server-Dokumentation](https://lemonade-server.ai/docs)
- [OpenHands-Erweiterungs-Repository](https://github.com/OpenHands/extensions)
- [Model Context Protocol-Server](https://github.com/modelcontextprotocol/servers)
- [Slack-MCP-Paket](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)