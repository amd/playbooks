<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Vue d'ensemble

LM Studio est un wrapper graphique puissant pour [llama.cpp](https://github.com/ggml-org/llama.cpp) et fournit également un [point de terminaison compatible OpenAI](https://lmstudio.ai/docs/developer/openai-compat) pour le déploiement de modèles en local. LM Studio offre une interface simple mais puissante pour télécharger et déployer facilement des modèles. LM Studio propose à la fois des backends (appelés runtimes) Vulkan et AMD ROCm™ pour les utilisateurs AMD.


## Ce que vous apprendrez
- Comment configurer et utiliser LM Studio pour exploiter votre matériel local
- Tester et gérer des LLM dans un environnement entièrement hors ligne
- Servir des modèles via une API compatible OpenAI pour alimenter des workflows et des applications personnalisés


## Configurer la mémoire

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Vérifier les mises à jour logicielles

<!-- @os:linux -->
> **Remarque** : Vous pouvez installer VS Code via le AMD Ryzen™ AI Developer Center. Pour LM Studio, suivez les instructions d'installation ci-dessous.
<!-- @os:end -->

<!-- @os:windows -->
> **Remarque** : Si VS Code ou LM Studio n'est pas installé, vous pouvez les installer depuis le AMD Ryzen™ AI Developer Center.
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## Installation des prérequis logiciels

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->

## Téléchargement des modèles

<!-- @var:id=lms_model device=halo,halo_box value="gpt-oss-120b" -->
<!-- @var:id=lms_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="qwen3.5-9b" -->
<!-- @var:id=model_name device=halo,halo_box value="GPT-OSS 120B" -->
<!-- @var:id=model_name device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen3.5 9B" -->

<!-- @device:halo,halo_box -->
<!-- @require:lmstudio-models-gpt-oss-120b -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @require:lmstudio-models-qwen3-9b -->
<!-- @device:end -->

## Discuter avec un LLM
Apprenez à commencer à discuter avec un LLM de niveau ChatGPT entièrement en local.

1. Ouvrez LMStudio.
2. Appuyez sur `Ctrl + L` pour ouvrir le chargeur de modèle, sélectionnez `Manually choose model load parameters`, puis cliquez sur `${model_name}`
3. Assurez-vous que « show advanced settings » est coché.
4. Modifiez `Context Length` selon vos besoins. Une longueur de contexte plus élevée signifie plus de mémoire pour le modèle, mais une utilisation accrue de la mémoire système. La valeur recommandée pour ce playbook est 4096.
5. Assurez-vous que `GPU Offload` est réglé au maximum et que `Flash Attention` est activé (les quantifications de cache peuvent rester désactivées).
6. Cochez `Remember settings` et cliquez sur `Load Model`.
7. Si vous n'êtes pas dans la fenêtre de chat, appuyez sur `Ctrl + 1` ou cliquez sur le bouton 👾 en haut à gauche de l'écran.
8. Envoyez un message et commencez à interagir avec le modèle !

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-model-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "${lms_model}-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-load-model-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="${lms_model}-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<p align="center">
  <img src="assets/chat.png" alt="Chatting with ${model_name} on LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<p align="center">
  <img src="assets/chat_qwen.png" alt="Chatting with ${model_name} on LM Studio" width="600"/>
</p>
<!-- @device:end -->

> **Conseil** : La longueur de contexte correspond à la mémoire du modèle. L'attention flash améliore la vitesse de traitement tout en réduisant l'utilisation de la mémoire. Le déchargement GPU transfère le calcul vers la carte graphique pour des réponses plus rapides.

## Servir des LLM via un point de terminaison compatible OpenAI

LM Studio propose également un point de terminaison compatible OpenAI sous la forme de LM Studio Server. Cela a déjà été démontré dans un workflow de codage agentique avec Cline [ici](../playbooks/vscode-qwen3-coder). Un autre cas d'usage courant consiste à connecter LM Studio Server à n'importe quelle application web (React, Node.js, Python) en envoyant des requêtes HTTP standard au point de terminaison d'inférence.

Pour configurer LM Studio Server, suivez les instructions ci-dessous :

1. Sur le côté gauche, cliquez sur l'onglet `Developer` (icône de ligne de commande) ou `Ctrl + 2`, puis cliquez sur `Server Settings`.
2. (Optionnel) : Si vous souhaitez servir le modèle sur votre réseau local, cochez `Serve on Local Network`. Si vous souhaitez l'utiliser avec un site web ou des appels intensifs dans VS Code, cochez `Enable CORS`.
3. Dans le coin supérieur gauche, assurez-vous que le serveur est en cours d'exécution en cliquant sur le bouton bascule devant `Status`.
4. Un point de terminaison compatible OpenAI sera alors actif. L'adresse est généralement http://127.0.0.1:1234
5. Si aucun modèle n'est déjà chargé, vous pouvez en charger un en cliquant sur `Load Model` et en suivant les étapes mentionnées précédemment.

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


Ce modèle sera désormais accessible via le point de terminaison LM Studio Server et prendra en charge les points de terminaison OpenAI, notamment :

| Point de terminaison | Méthode | Documentation |
|------------|----------|----------|
| /v1/models | GET | [Modèles](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Réponses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST | [Complétions de chat](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Complétions](https://lmstudio.ai/docs/developer/openai-compat/completions) |


#### Exemple : Tester votre point de terminaison
Maintenant que vous avez créé le point de terminaison compatible OpenAI, voyons comment l'intégrer dans un environnement de développement Python (tel que VSCode) et utiliser votre système comme fournisseur d'API local.

1. Créez un environnement virtuel Python :

<!-- @os:linux -->
<!-- @device:halo_box -->
    Sur Linux, ouvrez un terminal dans le répertoire de votre choix et suivez les commandes pour créer un venv.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Accordez à votre utilisateur l'accès aux périphériques GPU** (déconnectez-vous puis reconnectez-vous pour que cela prenne effet) :

```bash
sudo usermod -aG render,video $LOGNAME
```

    Sur Linux, ouvrez un terminal dans le répertoire de votre choix et suivez les commandes pour créer un venv.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
    Sur Windows, ouvrez un terminal dans le répertoire de votre choix et suivez les commandes pour créer un venv.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **Conseil** : Les utilisateurs Windows devront peut-être modifier leur stratégie d'exécution PowerShell (par exemple,
    > la définir sur RemoteSigned ou Unrestricted) avant d'exécuter certaines commandes Powershell.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    Sur Windows, ouvrez un terminal dans le répertoire de votre choix et suivez les commandes pour créer un venv.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **Conseil** : Les utilisateurs Windows devront peut-être modifier leur stratégie d'exécution PowerShell (par exemple,
    > la définir sur RemoteSigned ou Unrestricted) avant d'exécuter certaines commandes Powershell.

<!-- @device:end -->
<!-- @os:end -->

2. Installez le package OpenAI
    ```bash
    pip install openai
    ```

3. Exécutez le script suivant pour tester le point de terminaison que vous venez de créer.
    ```python
    from openai import OpenAI

    # Initialize the client specifically for your local server
    # The API key is required by the library but ignored by LM Studio
    client = OpenAI(
        base_url="http://localhost:1234/v1", 
        api_key="lm-studio"
    )
    print("Attempting to connect to local LM Studio server...")

    try:
        # Create a simple chat completion request
        completion = client.chat.completions.create(
            model="local-model", # The model identifier is optional in local mode
            messages=[
                {"role": "system", "content": "You are a helpful coding assistant."},
                {"role": "user", "content": "Explain Python decorators in 1 sentence"}
            ],
            temperature=0.7,
        )
        # Print the response
        print("\nConnection Successful! Server Response:\n")
        print(completion.choices[0].message.content)

    except Exception as e:
        print(f"\nConnection Failed: {e}. Ensure LM Studio server is running on port 1234.")
    ```
<!-- @os:windows -->
<!-- @test:id=lmstudio-ping-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "lmstudio_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
 "http://127.0.0.1:1234/v1/chat/completions",
 data=json.dumps({
   "model": model_id,
   "messages": [{"role":"user","content":"What is 2 + 2? Reply with only the number."}],
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
<!-- @test:id=lmstudio-ping-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request

with open("/tmp/lmstudio_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
 "http://127.0.0.1:1234/v1/chat/completions",
 data=json.dumps({
   "model": model_id,
   "messages": [{"role":"user","content":"What is 47 + 42? Reply with only the number in words."}],
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

#### (Optionnel) : Changer de runtime

1. Appuyez sur `Ctrl + Shift + R` sur votre clavier. Vous pouvez également cliquer sur l'onglet `Discover` (loupe) sur le côté gauche, puis cliquer sur `Runtime` dans la fenêtre contextuelle.
2. Vous devriez alors voir `Runtime Selections`, où le menu déroulant peut être utilisé pour changer de runtime.


## Prochaines étapes

- **Intégration d'applications personnalisées** : Intégrez vos propres scripts ou applications Python en utilisant l'API locale compatible OpenAI.
- **Interfaces avancées** : Connectez des interfaces puissantes comme Open WebUI à votre serveur pour la gestion de l'historique de chat et des personas.

Pour plus de documentation, veuillez consulter : https://lmstudio.ai/docs/developer