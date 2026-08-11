<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduction automatique.** Cette page a été traduite automatiquement depuis l'anglais et n'a pas été relue par un traducteur humain. Elle peut contenir des erreurs, et certaines instructions, commandes, téléchargements, disponibilités de produits ou autres contenus peuvent varier selon la langue ou la région. En cas d'incohérence ou de divergence, la version originale en anglais du playbook fait foi et prévaut.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Vue d'ensemble

Les développeurs passent beaucoup de temps sur de petites boucles récurrentes : examiner
les pull requests étiquetées, répondre aux commentaires GitHub, trier les nouveaux problèmes, transformer les
fils de discussion Slack en notes de standup ou en suivis d'incidents, et suivre les signaux de version ou de
recherche. Chaque boucle est familière, mais elle nécessite tout de même du jugement :
rassembler le bon contexte, décider de ce qui compte, et publier une mise à jour claire là où
l'équipe travaille déjà.

Les [automatisations OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview)
transforment ces boucles en conversations d'agent planifiées ou déclenchées par des événements : des exécutions
où un agent logiciel IA peut lire le contexte, appeler des outils et produire une mise à jour.
Les modèles d'automatisation partagés dans le catalogue d'extensions OpenHands suivent
ce schéma pour la revue de pull request GitHub, la surveillance de dépôt, le triage des
issues Linear, les rétrospectives d'incidents, les digests de standup Slack et les briefs de
recherche : une automatisation se déclenche, utilise des intégrations configurées telles que GitHub ou
Slack pour récupérer le contexte, raisonne sur ce contexte avec un grand modèle de langage
(LLM), et rédige un résultat.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) est le plan de contrôle
local pour créer et tester ces automatisations. Dans ce playbook, il exécute un
OpenHands Agent Server, le processus backend qui exécute les conversations d'agent,
et connecte l'agent à des services externes tels que GitHub et Slack.

Pour conserver le workflow sur votre système AMD, l'agent communique avec un modèle
local servi par Lemonade Server. Lemonade expose ce modèle via une
API compatible OpenAI, de sorte qu'Agent Canvas peut le configurer comme un point de terminaison distant de type
OpenAI, tandis que le modèle, l'invite et le contexte du workflow restent locaux.

Dans ce playbook, vous allez créer une automatisation concrète : un digest de développement planifié
allant de GitHub à Slack. Il utilise GitHub pour inspecter l'activité récente du dépôt,
Slack pour publier le digest, des appels à l'API Agent Canvas pour configurer et
tester l'automatisation, et Lemonade pour exécuter le LLM localement.

![Diagramme d'architecture montrant GitHub MCP, l'automatisation OpenHands, Lemonade Server et Slack MCP](assets/00-architecture-overview.png)

## Ce que vous allez apprendre

- Comment démarrer Lemonade Server et vérifier qu'un modèle local répond aux requêtes de chat
- Comment lancer Agent Canvas et faire pointer son Agent Server vers un LLM local
- Comment installer les serveurs Model Context Protocol (MCP) GitHub et Slack via
  l'API de l'Agent Server
- Comment créer et déclencher une automatisation OpenHands planifiée qui publie une
  digest de développement sur Slack
- Comment résoudre les problèmes les plus courants liés au modèle local et à l'automatisation

## Concepts clés

| Concept | Ce que c'est | Où cela s'intègre dans ce playbook |
| --- | --- | --- |
| Lemonade Server | Une plateforme locale de service de LLM conçue pour le matériel AMD qui expose une API compatible OpenAI. Vos données ne quittent jamais votre machine. | Exécute le modèle qui alimente l'agent. |
| OpenHands Agent Server | Le processus backend qui exécute les conversations d'agent OpenHands. | Héberge l'agent, son profil LLM et ses serveurs MCP. |
| Agent Canvas | Le plan de contrôle local pour OpenHands qui exécute Agent Server et une interface utilisateur pour inspecter les exécutions de l'agent. | Lance les backends et fournit l'API que vous appelez. |
| Serveur MCP | Un serveur Model Context Protocol qui donne à un agent des outils pour un service externe tel que GitHub ou Slack. | Permet à l'agent de lire GitHub et d'écrire sur Slack. |
| Automatisation OpenHands | Une conversation d'agent planifiée ou déclenchée par un événement qui récupère le contexte, raisonne dessus et écrit un résultat quelque part. | Le digest GitHub-vers-Slack que vous créez ici. |

<!-- @device:stx,krk -->
> [!NOTE]
> Les workflows d'agent de codage bénéficient d'un modèle et d'une fenêtre de contexte plus grands. Utilisez au
> moins 32 Go de mémoire système, et privilégiez 64 Go ou plus pour les modèles GGUF plus grands.
<!-- @device:end -->

## Prérequis

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Vous avez besoin de :

- Lemonade Server installé en suivant le guide standard
  [d'installation de Lemonade](https://lemonade-server.ai/docs/guide/install/).
- Node.js 22.12 ou une version ultérieure et `npm`, utilisés pour installer le CLI Agent Canvas
  publié et exécuter des serveurs MCP avec `npx`.
- Un package `@openhands/agent-canvas` publié récent avec
  des paramètres d'agent pilotés par schéma, `LLMSummarizingCondenserSettings.max_tokens`,
  et la prise en charge de `custom_tokenizer` pour le LLM.
- Le package Python `transformers` disponible dans l'environnement de l'Agent Server.
  Il est requis pour le comptage de tokens du modèle de chat lorsque `custom_tokenizer` est
  défini.
- Un jeton GitHub avec un accès en lecture au dépôt que vous souhaitez résumer.
- Un jeton de bot Slack (`xoxb-...`) avec un accès `chat:write` et un accès en lecture aux canaux.
- Un ID d'équipe Slack (`T...`).
- Un ID de canal Slack (`C...`) où le digest doit être publié.

Invitez l'application Slack dans le canal cible avant de tester l'automatisation.

## Variables utilisées dans ce playbook

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

Les valeurs suivantes sont saisies dans l'interface utilisateur d'Agent Canvas lors des étapes suivantes. Définissez-les
ici afin de pouvoir les copier :

```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```

Utilisez une valeur explicite `owner/repo` pour `GITHUB_REPO_FILTER`. Des caractères génériques
d'organisation trop larges peuvent renvoyer trop de contexte MCP pour les modèles locaux.

## 1. Démarrer Lemonade Server

Démarrez le modèle depuis le CLI Lemonade :

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```

Lemonade expose une API compatible OpenAI à l'adresse :

```text
http://127.0.0.1:13305/api/v1
```

Facultatif : si Agent Canvas ou l'exécuteur d'automatisation ne se trouve pas sur la même machine,
publiez le point de terminaison Lemonade via un tunnel sécurisé et utilisez l'URL HTTPS comme
URL de base du LLM :

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Vérifier le modèle local

Confirmez que Lemonade peut servir le modèle sélectionné :

```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Envoyez ensuite une petite requête de chat :

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

Si cela renvoie un tableau `choices`, Lemonade est prêt pour Agent Canvas.
## 3. Démarrer Agent Canvas

Installez le package Agent Canvas publié et démarrez la pile complète :

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Si l'installation globale via npm échoue avec une erreur de permissions,
consultez l'entrée de dépannage des permissions npm ci-dessous.

Par défaut, Agent Canvas démarre sur `http://localhost:8000`. Ouvrez cette URL
dans votre navigateur. Le backend local par défaut devrait s'afficher comme
sain sur l'écran d'accueil.

La commande `agent-canvas` démarre le serveur d'agent, le backend
d'automatisation et le frontend web ensemble. Vous n'avez besoin que de cette
seule commande pour exécuter OpenHands localement. Le reste de ce guide
configure tout via l'interface Agent Canvas dans votre navigateur.

## 4. Configurer le LLM local dans l'interface

Au premier lancement, Agent Canvas ouvre un flux d'intégration. Dans ce flux :

1. Gardez **OpenHands** sélectionné comme agent et cliquez sur **Next**.
2. Sur **Set up your LLM**, sélectionnez **Advanced**.
3. Gardez **Authentication** défini sur **API key**.
4. Définissez **Custom Model** sur la valeur de `OPENHANDS_LLM_MODEL`,
   `openai/Qwen3.6-35B-A3B-GGUF`.
5. Définissez **Base URL** sur `http://127.0.0.1:13305/api/v1`.
6. Pour **API Key**, saisissez un espace réservé non vide tel que
   `lemonade-local`. Lemonade ne nécessite pas de vraie clé, mais le client
   OpenHands a besoin d'une valeur à envoyer.

Les champs de connexion devraient ressembler à ceci. Le champ de la clé API
est masqué par l'interface.

![Paramètres avancés du LLM Agent Canvas à la première utilisation avec le modèle Lemonade et l'URL de base locale](assets/01-llm-advanced-settings.png)

Puis sélectionnez **All** et définissez les champs supplémentaires pour le
modèle local :

1. Faites défiler jusqu'à **Custom Tokenizer** et définissez-le sur
   `Qwen/Qwen3.6-35B-A3B`.
2. Faites défiler jusqu'à **LiteLLM Extra Body** et définissez-le sur
   `{"enable_thinking": true}`.
3. Cliquez sur **Next**.

![Onglet All du LLM Agent Canvas à la première utilisation avec le tokenizer personnalisé Qwen](assets/02-llm-all-tokenizer-settings.png)

![Onglet All du LLM Agent Canvas à la première utilisation avec le corps supplémentaire LiteLLM configuré](assets/03-llm-all-extra-body-settings.png)

Les paramètres du LLM devraient afficher :

| Champ | Valeur |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Le préfixe `openai/` indique à LiteLLM d'utiliser le formatage de requête
compatible OpenAI vis-à-vis du point de terminaison Lemonade. Le tokenizer
personnalisé est le tokenizer Hugging Face d'origine pour le modèle GGUF ; il
permet à OpenHands de compter les mêmes tokens de modèle de conversation que
ceux vus par le serveur de modèle local. Le formulaire actuel de LLM de
première utilisation n'affiche pas les paramètres du condenseur. Si votre
version d'Agent Canvas expose ultérieurement des paramètres de condenseur sous
**Settings > LLM**, utilisez `llm_summarizing` et définissez le nombre maximal
de tokens en dessous de la fenêtre de contexte de Lemonade, par exemple
`56000`.

## 5. Installer les serveurs MCP GitHub et Slack

Dans l'interface Agent Canvas, ouvrez **Customize** (ou **Settings > MCP**)
pour ajouter les serveurs MCP qui donnent à l'agent des outils pour GitHub et
Slack. Les valeurs de jeton sont envoyées uniquement à votre serveur d'agent
local et sont conservées sous forme de paramètres chiffrés.

### Serveur MCP GitHub

Ajoutez un nouveau serveur MCP avec ces paramètres :

| Champ | Valeur |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = votre jeton GitHub |

Utilisez un jeton GitHub avec un accès en lecture au dépôt que vous souhaitez
résumer.

### Serveur MCP Slack

Ajoutez un second serveur MCP avec ces paramètres :

| Champ | Valeur |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = l'ID de votre canal de synthèse |

Définissez `SLACK_CHANNEL_IDS` sur l'ID du canal de synthèse (la même valeur
que `SLACK_DIGEST_CHANNEL`) afin que l'agent n'ait pas besoin de parcourir
chaque canal Slack.

Après avoir ajouté les deux serveurs, utilisez le bouton **Test** sur chacun
pour confirmer qu'il se connecte et annonce des outils. Le serveur GitHub
devrait lister des outils GitHub, et le serveur Slack devrait lister des
outils Slack.

![Page MCP d'Agent Canvas avec les serveurs GitHub et Slack installés](assets/04-mcp-servers-installed.png)

## 6. Créer l'automatisation de synthèse

Dans l'interface Agent Canvas, ouvrez la page **Automations** et créez une
nouvelle automatisation :

1. Choisissez **Create automation** et sélectionnez le type **Prompt preset**.
2. Définissez **Name** sur `GitHub Development Digest to Slack`.
3. Définissez **Prompt** sur le texte suivant, en remplaçant les espaces
   réservés du dépôt et du canal par vos valeurs :

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

4. Définissez **Trigger** sur **Cron** avec la planification `0 9 * * 1-5`
   (9 h en semaine) et définissez **Timezone** sur votre fuseau horaire, par
   exemple `America/New_York`.
5. Définissez **Timeout** sur `900` secondes.
6. Enregistrez l'automatisation.

La page de détail de l'automatisation affiche la nouvelle automatisation avec
son déclencheur cron et le point d'entrée prompt-preset généré.

![Page de détail de l'automatisation Agent Canvas après création](assets/05-automation-created.png)
## 7. Tester l'automatisation

Depuis la page de détail de l'automatisation dans l'interface Agent Canvas UI :

1. Cliquez sur **Run now** (ou **Dispatch**) pour exécuter l'automatisation une fois immédiatement.
2. Observez la liste des exécutions sur la même page. La dernière exécution devrait passer à
   `COMPLETED`.
3. Ouvrez votre canal Slack cible. Il devrait contenir le digest généré.

Vous n'avez pas besoin d'attendre le déclenchement de la planification cron — **Run now** déclenche
une exécution à la demande afin que vous puissiez vérifier que le prompt, les connexions MCP et la publication
Slack fonctionnent tous avant de vous fier à la planification.

![Exécution d'automatisation Agent Canvas terminée avec succès](assets/06-automation-run-completed.png)

![Canal Slack affichant le digest OpenHands généré](assets/07-slackbot-message.png)

## Dépannage

- **Lemonade est arrêté :** redémarrez-le avec la commande
  `lemonade run "${LEMONADE_MODEL}"` de l'étape 1, puis relancez la vérification
  d'état.
- **`npm install -g` échoue avec une erreur de permissions :** sous Linux ou WSL,
  configurez un répertoire npm global appartenant à l'utilisateur, ajoutez-le à votre
  fichier de démarrage du shell, puis réinstallez Agent Canvas :

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

  Si vous utilisez `zsh`, ajoutez la même ligne `export PATH=...` à `~/.zshrc` à la place
  de `~/.bashrc`.
- **Agent Canvas rejette les paramètres LLM après la définition de `custom_tokenizer` :**
  installez `transformers` dans l'environnement Python de l'Agent Server, redémarrez Agent
  Canvas si nécessaire, puis essayez à nouveau d'enregistrer les paramètres LLM. OpenHands
  nécessite Transformers pour charger le modèle de chat du tokenizer lorsque `custom_tokenizer`
  est défini.
- **Agent Canvas ne parvient pas à joindre Lemonade :** vérifiez avec
  `curl -fsS "${LEMONADE_BASE_URL}/health"` et confirmez que l'URL de base saisie dans
  le formulaire LLM de première utilisation ou dans **Settings > LLM** correspond au
  point de terminaison local ou au tunnel HTTPS en cours d'exécution.
- **Les paramètres LLM n'ont pas été enregistrés :** assurez-vous d'avoir cliqué sur **Next** après
  avoir saisi les valeurs. Rouvrez **Settings > LLM** pour confirmer que les valeurs
  ont bien été conservées.
- **GitHub MCP ne voit pas les dépôts privés :** confirmez que le jeton GitHub dispose
  d'un accès en lecture au dépôt cible et que le bouton **Test** de MCP dans
  **Customize** annonce bien les outils GitHub.
- **Slack peut lire les canaux mais ne peut pas publier :** invitez l'application Slack dans le
  canal cible et confirmez que le bot dispose de `chat:write`.
- **L'automatisation liste trop de canaux Slack :** utilisez un ID de canal Slack et
  définissez `SLACK_CHANNEL_IDS` sur le serveur MCP Slack dans **Customize**.
- **L'exécution de l'automatisation échoue ou dépasse le contexte :** confirmez que Lemonade a été démarré
  avec `ctx_size=65536`, confirmez que le LLM OpenHands a bien `custom_tokenizer` défini,
  et utilisez un dépôt explicite avec des ensembles de résultats GitHub limités à 3 à 5
  éléments. Si votre version d'Agent Canvas expose les paramètres du condenser, définissez le nombre
  maximal de tokens du condenser en dessous de la fenêtre de contexte de Lemonade.

## Étapes suivantes

- Ajouter un digest hebdomadaire dédié aux releases uniquement.
- Ajouter une automatisation déclenchée par un événement GitHub pour des alertes plus rapides sur les PR ou les push.
- Router le même digest vers Notion, Linear, ou un autre outil basé sur MCP.

## Ressources

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Documentation du serveur Lemonade](https://lemonade-server.ai/docs)
- [Dépôt d'extensions OpenHands](https://github.com/OpenHands/extensions)
- [Serveurs Model Context Protocol](https://github.com/modelcontextprotocol/servers)
- [Paquet Slack MCP](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)