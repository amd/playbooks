<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduction automatique.** Cette page a été traduite automatiquement depuis l'anglais et n'a pas été relue par un traducteur humain. Elle peut contenir des erreurs, et certaines instructions, commandes, téléchargements, disponibilités de produits ou autres contenus peuvent varier selon la langue ou la région. En cas d'incohérence ou de divergence, la version originale en anglais du playbook fait foi et prévaut.
<!-- auto-translated-disclaimer:end -->

Voici la traduction du document :

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Aperçu

[OpenHands](https://github.com/All-Hands-AI/OpenHands) est un agent logiciel IA
capable d'écrire du code, d'exécuter des commandes, de naviguer sur le web et de modifier des fichiers dans un espace
de travail réel. Au lieu de copier des suggestions depuis une fenêtre de chat, vous pointez
l'agent vers un dossier de projet et le laissez faire le travail : implémenter une fonctionnalité, corriger un
bug, écrire des tests ou expliquer une base de code.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) est l'interface utilisateur web
recommandée pour exécuter OpenHands. Une seule commande `agent-canvas` démarre le
serveur de l'agent, le backend d'automatisation et le frontend web ensemble, afin que vous puissiez
mener une conversation avec l'agent depuis votre navigateur.

Pour que tout reste sur votre système AMD, l'agent communique avec un modèle local servi
par Lemonade Server. Lemonade expose ce modèle via une API compatible OpenAI,
de sorte qu'Agent Canvas puisse le configurer comme n'importe quel autre point de terminaison de type OpenAI
tandis que le modèle, votre code et le contexte de la conversation restent tous sur votre
machine.

Dans ce playbook, vous allez démarrer un modèle local, lancer Agent Canvas, le pointer
vers ce modèle, et exécuter votre première tâche de codage sur un véritable dossier de projet.

## Ce que vous allez apprendre

- Comment démarrer Lemonade Server et vérifier qu'un modèle local répond aux requêtes de chat
- Comment installer et lancer Agent Canvas à partir du paquet npm
- Comment configurer Agent Canvas pour utiliser un modèle Lemonade local comme LLM
- Comment démarrer une conversation OpenHands et observer l'agent modifier des fichiers et exécuter des
  commandes dans un espace de travail
- Comment examiner les modifications apportées par l'agent et le guider avec des messages de suivi

## Concepts fondamentaux

| Concept | Ce que c'est | Sa place dans ce playbook |
| --- | --- | --- |
| Lemonade Server | Une plateforme locale de service de LLM conçue pour le matériel AMD qui expose une API compatible OpenAI. Vos données ne quittent jamais votre machine. | Exécute le modèle qui alimente l'agent. |
| OpenHands | Un agent logiciel IA qui lit et modifie des fichiers, exécute des commandes shell et navigue sur le web dans un espace de travail. | L'agent que vous pilotez depuis le chat. |
| Agent Canvas | L'interface utilisateur web et le backend qui exécutent les conversations OpenHands et affichent les appels d'outils et les modifications de fichiers. | Lance la pile logicielle et héberge votre conversation. |
| Espace de travail | Le dossier de projet que l'agent est autorisé à lire et à modifier. | La cible des modifications et commandes de l'agent. |

<!-- @device:stx,krk -->
> [!NOTE]
> Les workflows d'agents de codage bénéficient d'un modèle et d'une fenêtre de contexte plus grands. Utilisez au
> moins 32 Go de mémoire système, et privilégiez 64 Go ou plus pour les modèles GGUF plus volumineux.
<!-- @device:end -->

## Prérequis

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Vous avez besoin de :

- Lemonade Server installé et capable de servir le modèle ci-dessous.
- Node.js 22.12 ou version ultérieure ainsi que `npm` (utilisé par la CLI `agent-canvas`).
- `uv`, le gestionnaire de paquets Python qu'Agent Canvas utilise pour gérer l'environnement du serveur
  de l'agent. Si votre système ne l'a pas déjà, installez-le depuis le
  [guide d'installation uv](https://docs.astral.sh/uv/getting-started/installation/)
  avant de lancer Agent Canvas.
- Un dossier de projet dans lequel travailler. Il peut s'agir de n'importe quel dépôt git local ou d'un
  répertoire de code sur lequel vous souhaitez que l'agent travaille.

<!-- @device:halo,halo_box,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

## 1. Démarrer Lemonade Server

Démarrez le modèle depuis la CLI Lemonade :

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

Lemonade expose une API compatible OpenAI à l'adresse :

```text
http://127.0.0.1:13305/api/v1
```



## 2. Vérifier le modèle local

Vérifiez que Lemonade peut servir le modèle sélectionné :

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Envoyez ensuite une petite requête de chat :

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

Si cela renvoie un tableau `choices`, Lemonade est prêt pour Agent Canvas.

## 3. Installer et lancer Agent Canvas

Installez le paquet Agent Canvas publié de manière globale :

```bash
npm install -g @openhands/agent-canvas
```

Démarrez ensuite la pile complète depuis un terminal :

```bash
agent-canvas
```

Par défaut, Agent Canvas démarre sur `http://localhost:8000`. Ouvrez cette URL dans
votre navigateur. Si le port 8000 est déjà utilisé, passez `--port` (ou `-p`) au moment de
lancer Agent Canvas :

```bash
agent-canvas --port 3000
```

La même commande fonctionne dans PowerShell sous Windows. Ouvrez ensuite
`http://localhost:3000` à la place. Le backend local par défaut devrait apparaître comme
sain sur l'écran d'accueil.

La commande `agent-canvas` démarre le serveur de l'agent, le backend d'automatisation et
le frontend web ensemble. Vous n'avez besoin que de cette seule commande pour exécuter OpenHands
en local.

## 4. Configurer le LLM local

Au premier lancement, Agent Canvas ouvre un flux d'intégration. Dans ce flux :

1. Laissez **OpenHands** sélectionné comme agent et cliquez sur **Next**.
2. Sur **Set up your LLM**, sélectionnez **Advanced**.
3. Laissez **Authentication** réglé sur **API key**.
4. Définissez **Custom Model** sur `openai/Qwen3.6-35B-A3B-GGUF`.
5. Définissez **Base URL** sur `http://127.0.0.1:13305/api/v1`.
6. Pour **API Key**, saisissez n'importe quelle valeur de remplacement non vide, telle que `lemonade-local`.
   Lemonade ne nécessite pas de véritable clé, mais le client OpenHands a besoin d'une valeur
   à envoyer.
7. Cliquez sur **Next**.

Les paramètres Advanced complétés devraient ressembler à ceci. Le champ de clé API est
masqué par l'interface utilisateur.

![Paramètres Advanced du LLM à la première utilisation d'Agent Canvas avec le modèle Lemonade et l'URL de base locale](assets/01-llm-advanced-settings.png)

Agent Canvas enregistre ces valeurs en tant que profil LLM. Si votre version vous demande de
nommer ce profil, utilisez un nom sans espace tel que `lemonade-local`. Si vous changez
de modèles plus tard, ouvrez **Settings > LLM** et mettez à jour les mêmes champs Advanced. Vous
pouvez basculer entre les profils enregistrés depuis le champ de saisie du chat avec la commande `/model`.

## 5. Ouvrir un espace de travail

L'agent ne peut lire et modifier des fichiers qu'à l'intérieur d'un espace de travail que vous choisissez. Avant
de démarrer une tâche, pointez Agent Canvas vers votre dossier de projet :

1. Depuis l'écran d'accueil, choisissez **Open Workspace**.
2. Sélectionnez le dossier qui contient votre projet (par exemple, un dépôt git
   sur lequel vous souhaitez que l'agent travaille).
3. Démarrez une nouvelle conversation dans cet espace de travail.

Tout ce que fait l'agent — lire des fichiers, exécuter des commandes, modifier du code — est
limité à cet espace de travail.

![Accueil d'Agent Canvas après l'intégration](assets/02-agent-canvas-home.png)
## 6. Exécutez votre première tâche de codage

Une fois l'espace de travail ouvert et le LLM local sélectionné, saisissez une tâche concrète dans
le chat. Une bonne première tâche est petite et vérifiable, par exemple :

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Observez la chronologie de la conversation. OpenHands va :

- Lire l'espace de travail pour comprendre sa structure.
- Créer `hello.py` avec la fonction demandée et un bloc de test.
- Éventuellement exécuter `python3 hello.py` pour vérifier le résultat.
- Rendre compte de ce qu'il a fait et de toute sortie de commande dans le chat.

Vous devriez voir le nouveau fichier apparaître dans l'espace de travail, et le message final de
l'agent devrait décrire la modification effectuée. C'est le moment clé : l'agent a écrit et exécuté
du code réel dans votre dossier de projet.

## 7. Examinez et orientez l'agent

Une fois que l'agent a terminé une étape, examinez son travail avant d'accepter la suivante :

- **Modifications de fichiers** : utilisez le navigateur de fichiers de l'espace de travail ou la
  vue de différences de l'agent pour voir exactement ce qui a été ajouté, modifié ou supprimé.
- **Sortie des commandes** : développez toute commande exécutée par l'agent pour voir stdout, stderr
  et le code de sortie.
- **Suivis** : si le résultat n'est pas celui que vous vouliez, répondez dans la même
  conversation avec une correction. L'agent conserve le contexte précédent et
  itère sur les mêmes fichiers.

Par exemple, si le test n'a pas affiché le message attendu, répondez :

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

L'agent relira le fichier, exécutera la commande, diagnostiquera le problème et modifiera de nouveau
le fichier, le tout dans la même conversation.

## Dépannage

- **`agent-canvas` n'est pas dans le PATH :** réinstallez avec
  `npm install -g @openhands/agent-canvas` et vérifiez que le répertoire binaire global npm
  se trouve dans votre PATH. Sous Windows, exécutez `npm config get prefix` ; le
  répertoire retourné, souvent `%APPDATA%\npm` ou `%USERPROFILE%\.npm-global`,
  doit figurer dans le PATH utilisateur avant que `agent-canvas` puisse être lancé depuis un nouveau
  terminal.
- **`npm install -g` échoue avec une erreur de permissions :** configurez un répertoire npm
  global appartenant à l'utilisateur, puis rouvrez le terminal et réinstallez Agent Canvas.

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

  Pour rendre la modification du PATH Windows permanente, ajoutez `%USERPROFILE%\.npm-global` à
  votre PATH utilisateur depuis **Paramètres > Système > À propos > Paramètres système avancés >
  Variables d'environnement**, puis ouvrez un nouveau terminal.
  <!-- @os:end -->
- **L'interface se charge mais le backend indique un état non sain :** attendez quelques secondes
  que le serveur agent termine son démarrage, puis actualisez. S'il reste non sain, redémarrez
  `agent-canvas` et vérifiez la sortie du terminal pour détecter d'éventuelles erreurs.
- **Les requêtes de chat Lemonade échouent avec une erreur de connexion :** vérifiez que
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` réussit et que
  Lemonade sert toujours le modèle avec `lemonade status`.
- **L'agent renvoie une erreur de longueur de contexte ou de limite de tokens :** redémarrez
  Lemonade avec une valeur `ctx_size` plus élevée (par exemple `ctx_size=65536`), et démarrez une
  nouvelle conversation pour que l'agent ne conserve pas un historique trop volumineux.
- **L'agent produit des modifications de mauvaise qualité ou incomplètes :** passez à un modèle
  plus grand dans Lemonade, ou donnez à l'agent une tâche plus petite et plus concrète et laissez-le
  la terminer avant de demander la modification suivante.
- **`uv` est manquant :** installez-le depuis
  [le guide d'installation d'uv](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas utilise `uv` pour gérer l'environnement Python du serveur agent.

## Étapes suivantes

- Essayez une tâche plus importante dans le même espace de travail, comme l'ajout d'un fichier de
  test unitaire ou la correction d'un bug connu, et examinez les différences de l'agent avant de
  conserver la modification.
- Connectez un serveur MCP tel que GitHub ou Slack sous **Customize** afin que
  l'agent puisse lire des issues ou publier des mises à jour pendant qu'il travaille.
- Enregistrez plusieurs profils LLM (un petit modèle rapide et un grand modèle plus performant) et
  basculez entre eux avec `/model` en cours de conversation.
- Passez aux [automatisations OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) pour
  transformer les boucles de développement récurrentes en exécutions d'agent planifiées ou déclenchées par des événements.

## Ressources

- [Documentation OpenHands](https://docs.openhands.dev/)
- [Présentation d'Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Configuration d'Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [Profils LLM et configuration des modèles](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Documentation de Lemonade Server](https://lemonade-server.ai/docs)