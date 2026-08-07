<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduction automatique.** Cette page a été traduite automatiquement de l'anglais et n'a pas été révisée par un humain. Elle peut contenir des erreurs, et certaines instructions, commandes, options de téléchargement, disponibilités de produits ou autres contenus peuvent varier selon la langue ou la région. En cas d'incompatibilité ou de divergence, la version originale anglaise du playbook fait foi.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Aperçu

Les développeurs consacrent beaucoup de temps à de petites boucles récurrentes : passer en revue des demandes d'extraction (pull requests) étiquetées, répondre à des commentaires sur GitHub, trier de nouveaux problèmes, transformer des fils de discussion Slack en notes de mêlée quotidienne ou en suivis d'incidents, et suivre les signaux de version ou de recherche. Chaque boucle est familière, mais elle exige tout de même du jugement : rassembler le bon contexte, décider de ce qui compte, et publier une mise à jour claire là où l'équipe travaille déjà.

Les [automatisations OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview)
transforment ces boucles en conversations d'agent planifiées ou déclenchées par des événements : des exécutions où un agent logiciel d'IA peut lire le contexte, appeler des outils et produire une mise à jour. Les modèles d'automatisation partagés du catalogue d'extensions OpenHands suivent ce modèle pour la révision des demandes d'extraction GitHub, la surveillance de dépôts, le triage des problèmes Linear, les rétrospectives d'incidents, les résumés quotidiens Slack et les briefs de recherche : une automatisation se déclenche, utilise des intégrations configurées comme GitHub ou Slack pour récupérer le contexte, raisonne sur ce contexte à l'aide d'un grand modèle de langage (LLM), puis inscrit un résultat.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) est le plan de contrôle local pour créer et tester ces automatisations. Dans ce guide pratique, il exécute un serveur d'agent OpenHands (Agent Server), le processus d'arrière-plan qui exécute les conversations d'agent, et connecte l'agent à des services externes comme GitHub et Slack.

Pour que le flux de travail reste sur votre système AMD, l'agent communique avec un modèle local servi par Lemonade Server. Lemonade expose ce modèle par une API compatible OpenAI, ce qui permet à Agent Canvas de le configurer comme un point de terminaison distant de type OpenAI, tandis que le modèle, l'invite et le contexte du flux de travail demeurent locaux.

Dans ce guide pratique, vous allez créer une automatisation concrète : un résumé de développement planifié allant de GitHub à Slack. Il utilise GitHub pour examiner l'activité récente du dépôt, Slack pour publier le résumé, des appels à l'API Agent Canvas pour configurer et tester l'automatisation, et Lemonade pour exécuter le LLM localement.

![Diagramme d'architecture montrant GitHub MCP, l'automatisation OpenHands, Lemonade Server et Slack MCP](assets/00-architecture-overview.png)

## Ce que vous allez apprendre

- Comment démarrer Lemonade Server et vérifier qu'un modèle local répond aux demandes de clavardage
- Comment lancer Agent Canvas et diriger son Agent Server vers un LLM local
- Comment installer les serveurs GitHub et Slack Model Context Protocol (MCP) par l'entremise de l'API Agent Server
- Comment créer et déclencher une automatisation OpenHands planifiée qui publie un résumé de développement sur Slack
- Comment dépanner les défaillances les plus courantes liées au modèle local et à l'automatisation

## Concepts fondamentaux

| Concept | Ce que c'est | Sa place dans ce guide pratique |
| --- | --- | --- |
| Lemonade Server | Une plateforme de service de LLM local conçue pour le matériel AMD qui expose une API compatible OpenAI. Vos données ne quittent jamais votre machine. | Exécute le modèle qui alimente l'agent. |
| OpenHands Agent Server | Le processus d'arrière-plan qui exécute les conversations d'agent OpenHands. | Héberge l'agent, son profil de LLM et ses serveurs MCP. |
| Agent Canvas | Le plan de contrôle local d'OpenHands qui exécute Agent Server et une interface utilisateur pour examiner les exécutions d'agent. | Lance les serveurs d'arrière-plan et fournit l'API que vous appelez. |
| Serveur MCP | Un serveur Model Context Protocol qui fournit à un agent des outils pour un service externe comme GitHub ou Slack. | Permet à l'agent de lire GitHub et d'écrire sur Slack. |
| Automatisation OpenHands | Une conversation d'agent planifiée ou déclenchée par un événement qui récupère le contexte, raisonne sur celui-ci et inscrit un résultat quelque part. | Le résumé GitHub-Slack que vous créez ici. |

<!-- @device:stx,krk -->
> [!NOTE]
> Les flux de travail des agents de codage bénéficient d'un modèle plus grand et d'une fenêtre de contexte plus étendue. Utilisez au moins 32 Go de mémoire système et privilégiez 64 Go ou plus pour les modèles GGUF plus volumineux.
<!-- @device:end -->

## Conditions préalables

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Vous avez besoin de :

- Lemonade Server installé en suivant le
  [guide d'installation standard de Lemonade](https://lemonade-server.ai/docs/guide/install/).
- Node.js 22.12 ou une version ultérieure et `npm`, utilisés pour installer l'interface de ligne de commande (CLI) publiée d'Agent Canvas et exécuter des serveurs MCP avec `npx`.
- Un paquet `@openhands/agent-canvas` publié récent, avec
  des paramètres d'agent basés sur un schéma, `LLMSummarizingCondenserSettings.max_tokens`,
  et la prise en charge de `custom_tokenizer` pour le LLM.
- Le paquet Python `transformers` disponible dans l'environnement Agent Server.
  Il est requis pour le comptage de jetons de modèle de clavardage lorsque `custom_tokenizer` est
  défini.
- Un jeton GitHub avec un accès en lecture au dépôt que vous voulez résumer.
- Un jeton de robot Slack (`xoxb-...`) avec l'accès `chat:write` et un accès en lecture aux canaux.
- Un ID d'équipe Slack (`T...`).
- Un ID de canal Slack (`C...`) où le résumé doit être publié.

Invitez l'application Slack au canal cible avant de tester l'automatisation.

## Variables utilisées dans ce guide pratique

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

Les valeurs suivantes sont saisies dans l'interface utilisateur d'Agent Canvas dans les étapes suivantes. Définissez-les ici afin de pouvoir les copier plus tard :

```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```

Utilisez une valeur explicite `owner/repo` pour `GITHUB_REPO_FILTER`. Les caractères génériques d'organisation trop larges peuvent renvoyer trop de contexte MCP pour les modèles locaux.

## 1. Démarrer Lemonade Server

Démarrez le modèle à partir de la CLI Lemonade :

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```

Lemonade expose une API compatible OpenAI à l'adresse suivante :

```text
http://127.0.0.1:13305/api/v1
```

Facultatif : si Agent Canvas ou l'exécuteur d'automatisation ne se trouve pas sur la même machine, publiez le point de terminaison Lemonade par l'entremise d'un tunnel sécurisé et utilisez l'URL HTTPS comme URL de base du LLM :

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Vérifier le modèle local

Confirmez que Lemonade peut servir le modèle sélectionné :

```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Envoyez ensuite une petite demande de clavardage :

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

Si un tableau `choices` est renvoyé, Lemonade est prêt pour Agent Canvas.
## 3. Démarrer Agent Canvas

Installez le paquet Agent Canvas publié et démarrez la pile complète :

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Si l'installation globale de npm échoue avec une erreur de permissions, consultez
la section de dépannage des permissions npm ci-dessous.

Par défaut, Agent Canvas démarre sur `http://localhost:8000`. Ouvrez cette URL
dans votre navigateur. Le backend local par défaut devrait apparaître comme
sain sur l'écran d'accueil.

La commande `agent-canvas` démarre le serveur d'agent, le backend
d'automatisation et le frontend web ensemble. Vous n'avez besoin que de cette
seule commande pour exécuter OpenHands localement. Le reste de ce guide
configure tout par l'entremise de l'interface utilisateur d'Agent Canvas dans
votre navigateur.

## 4. Configurer le LLM local dans l'interface utilisateur

Au premier lancement, Agent Canvas ouvre un flux d'intégration. Dans ce flux :

1. Gardez **OpenHands** sélectionné comme agent et cliquez sur **Next**.
2. Sur **Set up your LLM**, sélectionnez **Advanced**.
3. Gardez **Authentication** réglé sur **API key**.
4. Réglez **Custom Model** à la valeur de `OPENHANDS_LLM_MODEL`,
   `openai/Qwen3.6-35B-A3B-GGUF`.
5. Réglez **Base URL** à `http://127.0.0.1:13305/api/v1`.
6. Pour **API Key**, entrez un espace réservé non vide, comme
   `lemonade-local`. Lemonade n'exige pas de véritable clé, mais le client
   OpenHands a besoin d'une valeur à envoyer.

Les champs de connexion devraient ressembler à ceci. Le champ de clé API est
masqué par l'interface utilisateur.

![Paramètres avancés du LLM d'Agent Canvas à la première utilisation avec le modèle Lemonade et l'URL de base locale](assets/01-llm-advanced-settings.png)

Ensuite, sélectionnez **All** et réglez les champs supplémentaires pour le
modèle local :

1. Faites défiler jusqu'à **Custom Tokenizer** et réglez-le à
   `Qwen/Qwen3.6-35B-A3B`.
2. Faites défiler jusqu'à **LiteLLM Extra Body** et réglez-le à
   `{"enable_thinking": true}`.
3. Cliquez sur **Next**.

![Onglet All des paramètres du LLM d'Agent Canvas à la première utilisation avec le tokenizer personnalisé Qwen](assets/02-llm-all-tokenizer-settings.png)

![Onglet All des paramètres du LLM d'Agent Canvas à la première utilisation avec le corps supplémentaire LiteLLM configuré](assets/03-llm-all-extra-body-settings.png)

Les paramètres du LLM devraient afficher :

| Champ | Valeur |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Le préfixe `openai/` indique à LiteLLM d'utiliser le formatage de requête
compatible OpenAI par rapport au point de terminaison Lemonade. Le tokenizer
personnalisé est le tokenizer Hugging Face original du modèle GGUF; il permet
à OpenHands de compter les mêmes jetons de gabarit de conversation que ceux
que voit le serveur de modèle local. Le formulaire actuel du LLM à la
première utilisation n'affiche pas les paramètres de condenseur. Si votre
version d'Agent Canvas expose ultérieurement des paramètres de condenseur sous
**Settings > LLM**, utilisez `llm_summarizing` et réglez le nombre maximal de
jetons sous la fenêtre de contexte de Lemonade, par exemple `56000`.

## 5. Installer les serveurs MCP GitHub et Slack

Dans l'interface utilisateur d'Agent Canvas, ouvrez **Customize** (ou
**Settings > MCP**) pour ajouter les serveurs MCP qui donnent à l'agent des
outils pour GitHub et Slack. Les valeurs de jeton sont envoyées uniquement à
votre serveur d'agent local et sont conservées sous forme de paramètres
chiffrés.

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
| Env | `SLACK_CHANNEL_IDS` = l'ID de votre canal de résumé |

Réglez `SLACK_CHANNEL_IDS` à l'ID du canal de résumé (la même valeur que
`SLACK_DIGEST_CHANNEL`) afin que l'agent n'ait pas besoin de parcourir tous
les canaux Slack.

Après avoir ajouté les deux serveurs, utilisez le bouton **Test** sur chacun
pour confirmer qu'il se connecte et annonce des outils. Le serveur GitHub
devrait lister des outils GitHub, et le serveur Slack devrait lister des
outils Slack.

![Page MCP d'Agent Canvas avec les serveurs GitHub et Slack installés](assets/04-mcp-servers-installed.png)

## 6. Créer l'automatisation de résumé

Dans l'interface utilisateur d'Agent Canvas, ouvrez la page **Automations** et
créez une nouvelle automatisation :

1. Choisissez **Create automation** et sélectionnez le type **Prompt
   preset**.
2. Réglez **Name** à `GitHub Development Digest to Slack`.
3. Réglez **Prompt** au texte suivant, en remplaçant les espaces réservés du
   dépôt et du canal par vos valeurs :

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

4. Réglez **Trigger** à **Cron** avec l'horaire `0 9 * * 1-5` (9 h les jours
   de semaine) et réglez **Timezone** à votre fuseau horaire, par exemple
   `America/New_York`.
5. Réglez **Timeout** à `900` secondes.
6. Enregistrez l'automatisation.

La page de détails de l'automatisation affiche la nouvelle automatisation avec
son déclencheur cron et le point d'entrée du prompt preset généré.

![Page de détails de l'automatisation d'Agent Canvas après la création](assets/05-automation-created.png)
## 7. Tester l'automatisation

À partir de la page de détails de l'automatisation dans l'interface Agent Canvas UI :

1. Cliquez sur **Run now** (ou **Dispatch**) pour exécuter l'automatisation une fois immédiatement.
2. Observez la liste des exécutions sur la même page. La dernière exécution devrait passer à
   l'état `COMPLETED`.
3. Ouvrez votre canal Slack cible. Il devrait contenir le résumé généré.

Vous n'avez pas besoin d'attendre le déclenchement de la planification cron : **Run now** déclenche une
exécution à la demande afin que vous puissiez confirmer que le prompt, les connexions MCP et la publication
sur Slack fonctionnent tous avant de vous fier à la planification.

![Exécution de l'automatisation Agent Canvas terminée avec succès](assets/06-automation-run-completed.png)

![Canal Slack affichant le résumé OpenHands généré](assets/07-slackbot-message.png)

## Dépannage

- **Lemonade est arrêté :** redémarrez-le avec la commande
  `lemonade run "${LEMONADE_MODEL}"` de l'étape 1, puis relancez le contrôle
  de santé.
- **`npm install -g` échoue avec une erreur de permissions :** sur Linux ou WSL,
  configurez un répertoire npm global appartenant à l'utilisateur, ajoutez-le à votre fichier
  de démarrage du shell, puis réinstallez Agent Canvas :

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

  Si vous utilisez `zsh`, ajoutez la même ligne `export PATH=...` à `~/.zshrc` plutôt qu'à
  `~/.bashrc`.
- **Agent Canvas rejette les paramètres LLM après la configuration de `custom_tokenizer` :**
  installez `transformers` dans l'environnement Python du serveur d'agent, redémarrez Agent
  Canvas si nécessaire, puis réessayez d'enregistrer les paramètres LLM. OpenHands nécessite
  Transformers pour charger le gabarit de conversation du tokenizer lorsque `custom_tokenizer`
  est défini.
- **Agent Canvas ne peut pas joindre Lemonade :** vérifiez avec
  `curl -fsS "${LEMONADE_BASE_URL}/health"` et confirmez que l'URL de base saisie dans
  le formulaire LLM de première utilisation ou dans **Settings > LLM** correspond au point de terminaison
  local en cours d'exécution ou au tunnel HTTPS.
- **Les paramètres LLM n'ont pas été enregistrés :** assurez-vous d'avoir cliqué sur **Next** après
  avoir saisi les valeurs. Rouvrez **Settings > LLM** pour confirmer que les valeurs
  ont bien été conservées.
- **GitHub MCP ne peut pas voir les dépôts privés :** confirmez que le jeton GitHub dispose d'un
  accès en lecture au dépôt cible et que le bouton **Test** du MCP dans
  **Customize** annonce bien les outils GitHub.
- **Slack peut lire les canaux mais ne peut pas y publier :** invitez l'application Slack dans le
  canal cible et confirmez que le bot dispose de l'autorisation `chat:write`.
- **L'automatisation liste trop de canaux Slack :** utilisez un identifiant de canal Slack et
  définissez `SLACK_CHANNEL_IDS` sur le serveur MCP Slack dans **Customize**.
- **L'exécution de l'automatisation échoue ou dépasse le contexte :** confirmez que Lemonade a été
  démarré avec `ctx_size=65536`, confirmez que le LLM OpenHands a `custom_tokenizer` défini,
  et utilisez un dépôt explicite avec des ensembles de résultats GitHub plafonnés à 3 à 5
  éléments. Si votre version d'Agent Canvas expose les paramètres de condenseur, réglez le nombre maximal
  de jetons du condenseur en dessous de la fenêtre de contexte de Lemonade.

## Prochaines étapes

- Ajouter un résumé hebdomadaire limité aux versions publiées (release).
- Ajouter une automatisation déclenchée par un événement GitHub pour des alertes plus rapides
  sur les PR ou les push.
- Acheminer le même résumé vers Notion, Linear ou un autre outil pris en charge par MCP.

## Ressources

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Documentation du serveur Lemonade](https://lemonade-server.ai/docs)
- [Dépôt d'extensions OpenHands](https://github.com/OpenHands/extensions)
- [Serveurs du protocole Model Context Protocol](https://github.com/modelcontextprotocol/servers)
- [Package MCP Slack](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)