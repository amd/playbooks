<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ce playbook utilise des balises spéciales que GitHub ne peut pas afficher. Veuillez visiter [amd.com/playbooks](https://amd.com/playbooks) pour prévisualiser correctement ce contenu.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Ce playbook nécessite un minimum de **32 Go** de mémoire système.
<!-- @device:end -->

## Vue d'ensemble

Les agents de codage sont des outils puissants qui permettent aux développeurs de collaborer avec des agents IA s'appuyant sur des grands modèles de langage (LLM). Ils peuvent être intégrés dans l'environnement de développement, comme le terminal ou VS Code, permettant une intégration transparente dans le flux de travail d'un développeur.

Ce tutoriel montre comment utiliser Cline, VS Code et LM Studio pour exécuter un agent de codage entièrement sur votre machine locale.

## Ce que vous apprendrez

* Comment exécuter VS Code avec l'agent de codage Cline pour faciliter les tâches de génie logiciel.
* Comment configurer Cline pour communiquer avec LM Studio pour l'inférence locale des agents de codage.
* Comment utiliser des agents de codage locaux pour résoudre des tâches réelles de génie logiciel.

## Configuration de la mémoire

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Vérifier les mises à jour logicielles
> **Remarque** : Si VS Code n'est pas installé, vous pouvez l'installer avec le Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installation des prérequis logiciels

<!-- @require:lmstudio,vscode -->

## Lancer et configurer LM Studio

Nous utiliserons LM Studio pour servir le LLM qui alimente l'agent de codage.

- Dans la barre de recherche, recherchez `LM Studio` et lancez l'application. Vous serez accueilli par la page suivante.

![Écran initial de LM Studio](assets/initial-lm-studio.png)

Ensuite, nous devons charger le LLM sur le système. Nous allons utiliser le modèle `Qwen3-Coder-30B-A3B` avec une grande longueur de contexte. (Utilisez l'onglet Modèle pour l'installer si ce n'est pas déjà fait).
- Cliquez sur la barre de recherche en haut de la fenêtre LM Studio ou appuyez sur `CTRL+L`. Cliquez sur le commutateur `Manually choose model load parameters` puis cliquez sur le modèle Qwen3-Coder-30B-A3B.
- Changez la longueur de contexte de `4096` à `32768`, et assurez-vous que `GPU Offload` est au maximum. Ensuite, cliquez sur `Load Model`.

![Sélection du modèle](assets/model-list-zoomed.png)

Nous utilisons une grande longueur de contexte afin que l'agent puisse traiter de grandes bases de code et mémoriser les modifications apportées.

![Configuration du modèle](assets/selecting-model-zoomed.png)

Ensuite, nous devons activer le serveur LM Studio.
- Cliquez sur l'onglet Developer ou appuyez sur `CTRL+2` dans LM Studio sur la gauche.
- Vérifiez le bouton de statut et assurez-vous qu'il est réglé sur `Running`.

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-up-windows timeout=120 hidden=True -->
```powershell
lms server start --port 1234
curl.exe -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-up-linux timeout=120 hidden=True -->
```bash
lms server start --port 1234
curl -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end -->
<!-- @os:end -->

![Statut du serveur](assets/lm-studio-server-status.png)

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-load-qwen3-coder-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="qwen3coder-32k-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## Lancer et configurer VS Code

Nous allons installer l'extension Cline dans VS Code et la connecter au serveur LM Studio que nous venons de créer.
- Dans la barre de recherche, recherchez `VS Code` et lancez l'application.
- Cliquez sur l'icône `Extensions` dans la colonne de gauche de VS Code et recherchez `Cline`. Ensuite, cliquez sur le bouton `Install`.

![Installation de l'extension Cline](assets/installing-cline-vscode-extension.png)

- Une icône Cline devrait apparaître sur la gauche. Cliquez dessus pour ouvrir Cline. Une fenêtre vous demandera `How will you use Cline?` Comme nous allons utiliser un LLM local fonctionnant via LM Studio, sélectionnez `Bring my own API Key` et cliquez sur `Continue`.

<!-- @os:windows -->
<!-- @test:id=cline-install-and-verify-windows timeout=300 hidden=True -->
```powershell
code --install-extension saoudrizwan.claude-dev
code --list-extensions | Select-String -Pattern "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=cline-install-and-verify-linux timeout=300 hidden=True -->
```bash
code --install-extension saoudrizwan.claude-dev
code --list-extensions | grep -i "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

![Création de compte](assets/cline-how-will-you-use-cline-zoomed.png)

Ensuite, nous devons configurer Cline pour communiquer avec le serveur LM Studio que nous avons mis en place.
- Définissez le fournisseur d'API sur `LM Studio` et le modèle sur `Qwen3-Coder-30B-A3B-GGUF`.

>**Conseil** : Des modèles plus récents peuvent être disponibles. Envisagez de télécharger et de passer aux modèles Qwen3.6 si vous le souhaitez.


![Configuration du modèle](assets/cline-model-configuration-zoomed.png)

## Créer votre premier projet

Utilisons notre agent local pour créer un site web ! Ouvrez VSCode dans un répertoire de votre choix où Cline créera les fichiers.
- Pour ce faire, allez dans `File -> Open Folder` en haut à gauche de VS Code et choisissez un dossier comme `Documents`.

![Dossier vide VS Code](assets/open-cline-test.png)

Nous sommes maintenant prêts à soumettre une invite à l'agent de codage local.
- Cliquez sur l'extension Cline dans la colonne de gauche et entrez une invite pour démarrer l'agent. À titre d'exemple, utilisons l'invite suivante :
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

L'agent commencera alors à créer des fichiers selon l'invite. En tant qu'utilisateur, vous pouvez observer la génération du code dans VS Code comme indiqué ci-dessous. Vous devrez peut-être cliquer sur `Save` chaque fois que Cline souhaite créer un fichier.

![Génération de code Cline](assets/cline-code-generation.png)

Après avoir généré le logiciel, l'agent a terminé et vous pouvez exécuter l'application. Dans ce cas, l'agent a écrit dans trois fichiers : `index.html`, `script.js` et `styles.css`. En double-cliquant simplement sur le fichier HTML, nous pouvons charger et interagir avec le site web généré.

<!-- @os:windows -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "lmstudio_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
        "temperature": 0,
        "max_tokens": 500
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
    print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request
with open("/tmp/lmstudio_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()
req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
        "temperature": 0,
        "max_tokens": 500
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
    print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-stop-windows timeout=300 hidden=True -->
```powershell
$ID = Get-Content "$env:TEMP\lmstudio_model_id.txt" -Raw
$ID = $ID.Trim()
lms unload "$ID"
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-stop-linux timeout=300 hidden=True -->
```bash
ID="$(cat /tmp/lmstudio_model_id.txt)"
lms unload "$ID" || true
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

## Étapes suivantes

Après avoir généré le site web, vous pouvez continuer à travailler avec Cline pour l'améliorer. Deux améliorations possibles sont :

- **Documentation** : Soumettre l'invite `Add a README` à l'agent suffit pour que celui-ci génère un fichier `README.md` documentant le site web.
- **Animation** : Soumettez au modèle l'invite `Add an animation that visually represents a large language model running on a laptop.` pour générer une animation sur le site web.

Nous encourageons le lecteur à essayer de générer d'autres applications avec cette configuration. Voici quelques exemples amusants que nous avons testés :

- **Jeux d'arcade rétro** : Essayez d'autres invites. Il peut aussi être amusant de demander à l'agent de créer des jeux de style rétro en Python en utilisant le package `PyGame` avec l'invite suivante :

```code
Create a simple pong game using the PyGame python package.
```

- **Analyse de données** : Les agents de codage sont particulièrement utiles pour les scripts et l'analyse de données. Voici une invite pour illustrer la capacité du modèle local à générer des logiciels d'analyse de données pour la visualisation des cours boursiers :

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Ressources

Voici quelques ressources supplémentaires pour en savoir plus sur les agents de codage, Cline et l'exécution de charges de travail sur

* Plus d'informations sur le partenariat et l'intégration AMD LM Studio : https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* Blog AMD expliquant comment exécuter Cline sur AMD Ryzen™ AI et les cartes graphiques Radeon™ : https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Blog Cline sur l'exécution d'agents de codage localement sur des PC IA : https://cline.bot/blog/local-models-amd