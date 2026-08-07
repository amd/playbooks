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
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->
## Aperçu

🍋 **Lemonade** est un serveur d'IA locale à code source ouvert qui vous permet d'exécuter des grands modèles de langage (LLM), des générateurs d'images et des modèles audio directement sur votre propre matériel. Il expose les modèles par l'entremise de l'**API OpenAI**, une norme reconnue dans l'industrie, de sorte que toute application compatible avec OpenAI peut fonctionner instantanément avec Lemonade. À la fin de ce guide pratique, vous utiliserez Lemonade pour exécuter des modèles localement sur votre machine.

## Ce que vous apprendrez

À la fin de ce guide pratique, vous serez en mesure de :

* **Installer Lemonade Server** et vérifier qu'il fonctionne correctement.
* **Télécharger un LLM et discuter avec celui-ci** à l'aide d'une seule commande.
* **Explorer l'interface Web** et essayer différentes modalités comme la vision, la reconnaissance vocale et la génération d'images.
* **Changer de moteur GPU** entre Vulkan et le logiciel AMD ROCm™.
* **Créer une application Python** propulsée par un LLM local à l'aide de l'API compatible avec OpenAI.
<!-- @device:halo_box,halo,stx,krk -->
* **Exécuter des modèles sur l'unité de traitement neuronal (NPU) AMD** à l'aide des modes d'exécution Hybrid et FLM sur le matériel AMD Ryzen™ AI.
<!-- @device:end -->
# Configuration de la mémoire
<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Vérifier les mises à jour logicielles
<!-- @require:software-update -->
<!-- @device:end -->
## Installation des prérequis logiciels

Avant de commencer, assurez-vous d'avoir :

- Un PC exécutant **Windows 11** ou une distribution **Linux** prise en charge (Ubuntu 24.04+, Fedora, Debian)
- **16 Go de RAM** sont recommandés pour le modèle d'exécution utilisé aux étapes 1 à 7 (`Gemma-4-E2B-it-GGUF`, environ 3 Go). **32 Go et plus** sont recommandés si vous souhaitez utiliser le modèle de génération de code plus volumineux à l'étape 6 (`Qwen3.5-35B-A3B-GGUF`, environ 20 Go).
- **Environ 4 à 30 Go d'espace disque libre**, selon les modèles que vous téléchargez. Le modèle le plus volumineux de ce guide fait environ 20 Go.
- **Python 3.10–3.13** (utilisé dans la section sur l'application Python)
- Une connexion Internet (filaire ou sans fil)
<!-- @device:halo_box,halo,stx,krk -->
- [Facultatif] Un NPU AMD XDNA 2 (série Ryzen AI 300/400/Max 300 ou Z2 Extreme) avec le pilote le plus récent installé à partir des [Instructions d'installation du logiciel Ryzen AI](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) si vous souhaitez exécuter un modèle sur le NPU.
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-update-windows timeout=120 hidden=True -->
```bash
winget upgrade -e --id AMD.LemonadeServer
lemonade --version
```
<!-- @test:end -->

<!-- @test:id=lemonade-chat-gemma-windows timeout=1200 hidden=True -->
```powershell

# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade(robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "Gemma-4-E2B-it-GGUF" } | Select-Object -First 1
if (-not $entry) { throw "Model Gemma-4-E2B-it-GGUF is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model Gemma-4-E2B-it-GGUF is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: Gemma-4-E2B-it-GGUF model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "Gemma-4-E2B-it-GGUF"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 500
} | ConvertTo-Json -Depth 5
$out = curl.exe -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions -H "Content-Type: application/json" -d $body
if (-not $out) { throw "Empty response from Lemonade chat/completions" }
Write-Host "OK: Model Gemma-4-E2B-it-GGUF responded"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-update-linux timeout=120 hidden=True -->
```bash
sudo apt update
sudo apt install --only-upgrade lemonade-server
lemonade --version
```
<!-- @test:end -->

<!-- @test:id=lemonade-chat-gemma-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

models_json=""
for i in $(seq 1 120); do
  models_json="$(curl -s --max-time 2 http://127.0.0.1:13305/api/v1/models || true)"
  if [ -n "$models_json" ]; then
    break
  fi
  sleep 1
done

if [ -z "$models_json" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:13305"
  exit 1
fi
echo "OK: Lemonade server is responding"

export MODELS_JSON="$models_json"
python3 - <<'PY'
import json
import os
import sys

data = json.loads(os.environ["MODELS_JSON"])
entry = None
for item in data.get("data", []):
    if item.get("id") == "Gemma-4-E2B-it-GGUF":
        entry = item
        break

if entry is None:
    print("Model Gemma-4-E2B-it-GGUF is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model Gemma-4-E2B-it-GGUF is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: Gemma-4-E2B-it-GGUF model is downloaded in Lemonade")
PY

body='{
  "model": "Gemma-4-E2B-it-GGUF",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 500
}'

out="$(curl -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Model Gemma-4-E2B-it-GGUF responded"
```
<!-- @test:end -->
<!-- @os:end -->
## Concepts fondamentaux — Fonctionnement des serveurs d'IA locaux

Avant d'exécuter un modèle, il vaut la peine de comprendre *pourquoi* les choses sont configurées ainsi. Lemonade est un **serveur de modèle local**, un processus qui charge des modèles d'IA en mémoire et les expose aux applications par HTTP, tout comme le ferait un service d'IA infonuagique.

### Pourquoi un serveur?

| Avantage | Ce que cela signifie pour vous |
|---------|----------------------|
| **Intégration simplifiée** | Les applications communiquent avec une seule API HTTP au lieu de composer avec des bibliothèques C++ ou Python propres au matériel. |
| **Modèles partagés** | Un seul modèle chargé peut servir plusieurs applications à la fois, sans copies en double qui accaparent votre RAM. |
| **Portabilité infonuagique vers local** | Un code écrit pour l'API infonuagique d'OpenAI fonctionne avec Lemonade en changeant simplement une URL. |
| **Séparation des responsabilités** | La gestion des modèles, la diffusion en continu et la tolérance aux pannes sont prises en charge par le serveur, ce qui permet aux développeurs de se concentrer sur leur application. |

### La norme API d'OpenAI

Lemonade implémente l'**API OpenAI**, la même interface utilisée par ChatGPT, Azure OpenAI et des dizaines d'autres services. Le modèle de conversation est simple :

| Rôle | Qui parle |
|------|---------------|
| **system** | Instructions données au modèle (personnalité, contraintes, outils disponibles) |
| **user** | Messages de l'humain (ou de l'application) destinés au modèle |
| **assistant** | Réponses générées par le modèle |

Cela signifie que toute bibliothèque ou application prenant en charge OpenAI peut communiquer avec Lemonade en la pointant vers `http://localhost:13305/api/v1` pendant que Lemonade Server est en cours d'exécution.

## Activité principale — Votre première discussion avec une IA locale

Téléchargeons un LLM et engageons une conversation avec lui, en exécutant l'IA entièrement sur votre propre machine.

### Étape 1 : Télécharger et exécuter un modèle

Lemonade est livré avec une bibliothèque de modèles sélectionnés. Commençons avec **Gemma-4-E2B-it**, un modèle performant et compact qui prend en charge la vision. Ouvrez un terminal et exécutez :

```
lemonade run Gemma-4-E2B-it-GGUF
```

Cette commande unique fait trois choses :

1. **Télécharge** le modèle (~3 Go) depuis Hugging Face, s'il n'est pas déjà téléchargé. (Peut prendre un certain temps)
2. **Démarre** le processus Lemonade Server sur le port 13305.
3. **Ouvre Lemonade App** afin que vous puissiez commencer à clavarder avec le modèle.
<!-- @os:windows -->
Sous Windows, l'application Lemonade se lance automatiquement et vous pouvez commencer à clavarder immédiatement. Si vous avez installé le paquet `minimal.msi`, l'application n'est pas incluse. Pour commencer à clavarder, ouvrez votre navigateur Web et accédez à `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
Sous Linux, ouvrez votre navigateur et accédez à `http://localhost:13305` pour accéder à l'application Web.
<!-- @os:end -->
Essayez de saisir une question :

```
What are three fun facts about lemons?
```

Le modèle répondra directement dans la fenêtre de clavardage. **Félicitations! Vous exécutez maintenant un grand modèle de langage localement.**

![Application Lemonade avec journaux affichés](../../dependencies/assets/ChatwithLogs.png)

Dans le panneau des journaux du serveur (Server Logs) de l'application Lemonade, vous pouvez trouver des données de télémétrie sur la performance du modèle après chaque réponse. Par exemple :

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### Étape 2 : Explorer l'interface Web et les différentes modalités

Lemonade comprend une interface Web intégrée qui vous permet :

- d'**interagir** avec le modèle chargé dans une fenêtre de clavardage familière;
- de **parcourir les modèles** dans l'onglet Model Manager;
- de **télécharger de nouveaux modèles** en un clic.

Essayez de passer d'une modalité à l'autre à l'aide de l'onglet **Model Manager** dans l'interface Web, où vous pouvez parcourir les modèles par Recipe (recette) ou par Category (catégorie) :

1. **Vision :** le modèle `Gemma-4-E2B-it-GGUF` déjà chargé prend en charge la vision. Collez une image dans la zone de clavardage et demandez au modèle de la décrire.
2. **Génération d'images :** dans la catégorie Image, téléchargez un modèle d'image comme `SDXL-Turbo` à partir du Model Manager, puis utilisez le Lemonade Image Generator pour saisir une invite et générer une image localement.
3. **Audio :** dans la catégorie Audio, téléchargez un modèle audio comme `Whisper-Tiny`, capable de convertir la parole en texte. Fournissez un enregistrement audio pour le transcrire localement. Pour la synthèse vocale, essayez l'un des modèles de la catégorie Speech, comme `kokoro-v1`.

![Multi-Modality with Lemonade](../../dependencies/assets/multi_modality.png)

### Étape 3 : Essayer un modèle avec un moteur d'exécution différent

Si vous survolez un modèle dans l'application Lemonade, une icône d'engrenage apparaît. En cliquant dessus, vous pouvez sélectionner des options pour le modèle, y compris le choix du moteur d'exécution souhaité.

Par défaut, Lemonade utilise Vulkan pour l'accélération GPU. Si vous disposez d'un GPU discret AMD pris en charge, vous pouvez passer à ROCm.

![Lemonade Select Backend](../../dependencies/assets/lemonademodeloptions.png)

Pour gérer vos moteurs d'exécution installés, cliquez sur le bouton de moteur d'exécution dans la colonne la plus à gauche.

Vous pouvez également préciser le moteur d'exécution à l'aide de la commande suivante :

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Vous pouvez également définir votre moteur d'exécution par défaut à l'aide de la variable d'environnement `LEMONADE_LLAMACPP` avec les valeurs suivantes : `vulkan`, `rocm` ou `cpu`.

---

## Aller plus loin — Créer une application propulsée par l'IA avec Python

La véritable puissance d'un serveur d'IA local, c'est que n'importe quelle application peut s'y connecter avec seulement quelques lignes de code. Pour le démontrer, créons une petite application, mais fonctionnelle : un **générateur de fiches d'étude** auquel vous donnez un sujet, qui génère des fiches, et avec lequel vous pouvez vous quizzer de façon interactive.

### Étape 4 : Démarrer le serveur

Vérifiez que le serveur Lemonade est en cours d'exécution. Il démarre généralement automatiquement en arrière-plan après l'installation. Pour le vérifier, exécutez :

```
lemonade status
```

Vous devriez voir un message semblable à : `Server is running on port 13305`.

Si le serveur n'est pas en cours d'exécution, démarrez-le en ouvrant l'application Lemonade. Utilisez le port par défaut **13305** (vous pouvez le confirmer ou le sélectionner à partir de l'icône de la barre d'état système).

### Étape 5 : Installer le client Python OpenAI

Dans un terminal, créez un venv et installez le client Python OpenAI à l'aide des commandes suivantes :
<!-- @os:linux -->
```bash
# Your specific version of Linux may have different commands
sudo apt update
sudo apt install -y python3-venv
python3 -m venv lemonade-env
source lemonade-env/bin/activate
pip install openai
```
<!-- @os:end -->
<!-- @os:windows -->
```powershell
python -m venv lemonade-env
lemonade-env\Scripts\activate
pip install openai
```
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=env-check-windows timeout=300 hidden=True -->
```powershell
python --version
where.exe python
where.exe pip
python -c "import sys; print(sys.executable)"
python -m pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=env-check-linux timeout=300 hidden=True -->
```bash
python3 --version
which python3
which pip3
python3 -c "import sys; print(sys.executable)"
python3 -m pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=pip-install-openai-windows timeout=300 hidden=True -->
```powershell
python -m pip install openai
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=pip-install-openai-linux timeout=300 hidden=True -->
```bash
python3 -m pip install openai
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=python-openai-import-windows timeout=120 hidden=True -->
```powershell
python -m pip show openai
python -c "from openai import OpenAI; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=python-openai-import-linux timeout=120 hidden=True -->
```bash
python3 -m pip show openai
python3 -c "from openai import OpenAI; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

### Étape 6 : Créer l'application de fiches d'étude

Téléchargeons un modèle différent pour générer du code : `Qwen3.5-35B-A3B-GGUF`. Il s'agit d'un modèle volumineux (~20 Go) et performant, mieux adapté aux systèmes disposant de 32 Go de RAM ou plus. Si vous disposez de moins de RAM, essayez plutôt `Qwen3.5-9B-GGUF` (~6 Go).

Vous pouvez le télécharger à partir de l'interface utilisateur ou exécuter ce qui suit :
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Saisissez l'invite suivante dans l'interface de clavardage Lemonade pour générer le code d'une application simple de fiches d'étude.

Nous utiliserons Qwen3.5-35B-A3B-GGUF (un modèle plus volumineux, plus habile pour écrire du code) pour générer notre application Python, et l'application elle-même appellera Gemma-4-E2B-it-GGUF (le modèle plus petit que vous avez déjà téléchargé) au moment de l'exécution. Le code peut ensuite être copié dans le fichier de votre choix pour être exécuté avec Python.

```
Generate a Python script that uses the OpenAI Python library to call a local LLM and create an interactive flashcard study tool.

Connection details:
- Base URL: http://localhost:13305/api/v1
- API key: "lemonade"
- Model to use: "Gemma-4-E2B-it-GGUF"

Structure:

1. A `generate_flashcards(topic, count=5)` function that:
   - Sends a system message instructing the LLM to return ONLY a JSON array of objects with "question" and "answer" fields.
   - Handles malformed JSON gracefully.
   - Returns the parsed list of cards, or an empty list if parsing fails.

2. A `quiz(cards)` function that shuffles the cards and, for each card:
   - Prints `--- Card i/N ---`.
   - Prints `Q: <question>`.
   - Waits for the user to press Enter ("Press Enter to reveal the answer...").
   - Prints `A: <answer>`.
   - Asks "Did you get it right? (y/n): " and tracks the score.
   - At the end, prints `🏆 Score: <score>/<total>`.

3. A main loop that:
   - Prints a `🍋 Lemonade Flashcard Generator` banner on startup.
   - Asks the user for a topic (typing "quit" exits).
   - Prints `✨ Generating N flashcards on: <topic>`.
   - Calls `generate_flashcards` and lists the generated questions as an indented numbered list (`  1. ...`).
   - Offers to start the quiz.
```

> **Astuce** : nous avons suivi les pratiques d'ingénierie standard grâce à une création d'invite rigoureuse et à l'utilisation d'un système à deux modèles pour optimiser les ressources et la vitesse.

Pour votre commodité, nous avons fourni un exemple de résultat dans [`flashcards.py`](assets/flashcards.py). N'hésitez pas à le télécharger dans votre répertoire. Dans un cas comme dans l'autre, vous devriez maintenant disposer d'un fichier Python prêt à être exécuté.

<!-- @os:windows -->
<!-- @test:id=lemonade-python-smoke-windows timeout=900 hidden=True -->
```powershell
# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

Start-Sleep -Seconds 5
python lemonade_python_smoke.py
```
<!-- @test:end -->
<!-- @os:end -->


<!-- @os:linux -->
<!-- @test:id=lemonade-python-smoke-linux timeout=600 hidden=True -->
```bash
set -euo pipefail

models_json=""
for i in $(seq 1 120); do
  models_json="$(curl -s --max-time 2 http://127.0.0.1:13305/api/v1/models || true)"
  if [ -n "$models_json" ]; then
    break
  fi
  sleep 1
done

if [ -z "$models_json" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:13305"
  exit 1
fi
echo "OK: Lemonade server is responding"

sleep 5
python3 lemonade_python_smoke.py
```
<!-- @test:end -->
<!-- @os:end -->


### Étape 7 : Exécuter le code généré

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**Voici ce que vous devriez voir :**

```
🍋 Lemonade Flashcard Generator
================================
Powered by a local LLM running on your own hardware.

Enter a topic (or "quit" to exit): the solar system

✨ Generating 5 flashcards on: the solar system

Generated 5 cards!

  1. Which planet is closest to the Sun?
  2. What is the largest planet in our solar system?
  3. Which planet is known as the "Red Planet"?
  4. How many moons does Earth have?
  5. What separates the inner planets from the outer planets?

Start quiz? (y/n): y

--- Card 1/5 ---
Q: What is the largest planet in our solar system?

Press Enter to reveal the answer...
A: Jupiter is the largest planet, with a diameter of about 139,820 km.

Did you get it right? (y/n): y

...

🏆 Score: 4/5
```

En environ 150 lignes de code, vous avez créé un outil d'étude entièrement fonctionnel propulsé par un LLM local. Il n'y a aucune clé API à gérer, aucun coût d'utilisation, et aucune donnée ne quitte jamais votre machine.

> **Point clé :** remarquez que la ligne `client = OpenAI(base_url=...) ` est la *seule* chose qui relie cette application à Lemonade plutôt qu'au nuage d'OpenAI. Le reste du code est identique à ce que vous écririez pour n'importe quel service compatible avec OpenAI. Si vous avez déjà utilisé la bibliothèque Python OpenAI, vous savez déjà comment créer des applications avec Lemonade.

### Ce que cela démontre

Cette petite application met en œuvre plusieurs modèles d'intégration concrets :

| Modèle | Où il apparaît |
|---------|-----------------|
| **Invites système** | Le message `"system"` indique au LLM de produire un JSON structuré |
| **Sortie structurée** | L'application analyse la réponse du LLM en tant que JSON pour créer les fiches |
| **Requêtes sans état** | Chaque appel à `generate_flashcards()` est indépendant |
| **Gestion des erreurs** | Le bloc `try/except` gère avec élégance les cas où la sortie du LLM n'est pas un JSON valide |

Ces mêmes modèles s'appliquent à toute application, comme les agents conversationnels, les assistants de code, les générateurs de contenu ou les outils d'automatisation.

#### Défi bonus

* Pour un défi supplémentaire, essayez de modifier l'application pour faire lire les fiches à l'utilisateur en vous référant à l'exemple fourni [ici](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py).

---

<!-- @device:halo_box,halo,stx,krk -->
## Exécution de modèles sur le NPU (facultatif)

Si vous possédez un Ryzen AI de série 300/400/Max 300 ou un Z2 Extreme, votre appareil dispose d'un **processeur de traitement neuronal (NPU)** intégré, une puce dédiée conçue spécifiquement pour les charges de travail d'IA. L'exécution de modèles sur le NPU est plus économe en énergie que l'utilisation du GPU, ce qui en fait un choix idéal pour les tâches d'IA en arrière-plan, les sessions prolongées et l'utilisation sur batterie.

Lemonade prend en charge trois modes d'exécution NPU, tous transparents derrière la même API OpenAI :

| Mode | Fonctionnement | Recette | Exemples de modèles |
|------|-------------|--------|----------------|
| **Hybride (NPU + iGPU)** | Le NPU traite l'invite, l'iGPU génère les jetons | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **NPU uniquement** | L'ensemble de l'inférence s'exécute sur le NPU | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | Utilise le moteur FastFlowLM sur le NPU, optimisé pour AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### Exigences

- Processeur **AMD Ryzen AI série 300/400 ou série Z2**
- Pour les modèles **FLM** : l'environnement d'exécution FLM peut être installé depuis l'application Lemonade, ou Lemonade installera automatiquement l'environnement d'exécution FLM lors de l'exécution d'un modèle FLM. Pour en savoir plus sur FastFlowLM, consultez [ce lien](https://fastflowlm.com/docs/).


### Étape 8 : Exécuter un modèle hybride

Les modèles hybrides répartissent le travail entre le NPU et l'iGPU pour offrir un bon équilibre entre vitesse et efficacité. Dans l'application Lemonade, sélectionnez un modèle dans la liste `Ryzen AI LLM`, par exemple `Qwen3-4B-Hybrid`, ou exécutez-le à l'aide de la commande suivante :

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade détecte automatiquement votre NPU et installe le moteur **Ryzen AI LLM**.

> **Que se passe-t-il en coulisses?** Lorsque vous envoyez un message, le NPU traite l'intégralité de votre invite en parallèle (c'est ce qu'on appelle le « préremplissage »). Ensuite, l'iGPU prend le relais pour générer la réponse un jeton à la fois (c'est ce qu'on appelle le « décodage »). Cette approche hybride tire parti des forces de chaque puce.

### Étape 9 : Exécuter un modèle FLM

Les modèles FastFlowLM (FLM) sont spécifiquement optimisés pour l'architecture NPU XDNA2 d'AMD et peuvent être très rapides pour leur taille. Par exemple, sélectionnez `qwen3.5-4b-FLM` dans la liste `FastFlowLM NPU` ou utilisez la commande suivante :

<!-- @os:windows -->
Pour activer `FastFlowLM` sous Windows :

* Ouvrez le menu `Backends Manager`.
* Repérez la catégorie de moteur `FastFlowLM NPU`.
* Cliquez sur Install NPU.
* Une fois l'installation terminée, environ 36 modèles par défaut seront disponibles dans le menu déroulant FFLM.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
Lorsque l'application `Lemonade` est lancée pour la première fois, le moteur `FastFlowNPU` n'est pas activé par défaut. 
L'application locale ouvrira la page d'installation pour vous guider dans la configuration.

Pour activer `FastFlowLM` sous Linux :

* Ouvrez l'application `Lemonade`.
* Consultez la documentation [officielle FLM](https://lemonade-server.ai/flm_npu_linux.html) et suivez les étapes d'installation pour FLM en sélectionnant votre distribution Linux.
* Activez les rétroportages (« backports ») comme indiqué sur la page d'installation.
* Téléchargez la dernière version `v0.9.x` depuis la [page des étiquettes](https://github.com/FastFlowLM/FastFlowLM/tags).'
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
Pour la plateforme de développement AMD Halo, assurez-vous de choisir Debian 13.
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* Installez le paquet `.deb` téléchargé.
* Recommandé : quittez l'application `Lemonade App` et rouvrez-la afin que les changements soient détectés.
* Recommandé : ouvrez `Backends Manager` et cliquez sur Install `FastFlowNPU` Backend.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
Après une installation réussie, vous devriez voir que `flm:npu` est terminé dans le **gestionnaire de téléchargements** de l'**application de bureau Lemonade**.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Vous pouvez ensuite sélectionner l'un des modèles FFLM disponibles et commencer à utiliser le moteur NPU.

Pour un modèle spécifique, téléchargez le modèle souhaité depuis la [page des modèles](https://fastflowlm.com/docs/models/qwen/) et validez-le à l'aide de la commande Shell fournie dans la documentation.
```
flm run qwen3.5-4b-FLM
```
ou via 
```
lemonade run qwen3.5-4b-FLM
```

Les modèles FLM comprennent certaines des architectures les plus populaires (Gemma 3, Qwen 3, Llama 3 et DeepSeek R1) et vont de moins de 1 Go à plus de 13 Go.
Lemonade détecte automatiquement votre NPU et installe le moteur **FastFlowLM NPU**.

<!-- @os:windows -->
> **Astuce :** Pour une performance NPU optimale, activez le mode turbo :
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Changer de modèle

L'application de cartes mémoire de l'étape 6 fonctionne aussi avec les modèles NPU, il suffit de changer le nom du modèle :

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Prochaines étapes

Vous disposez maintenant d'un serveur d'IA local fonctionnant sur votre propre matériel; voici les prochaines étapes possibles :

1. **Connectez vos applications préférées** : Lemonade fonctionne d'emblée avec [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/) et [bien d'autres](https://lemonade-server.ai/marketplace).

2. **Explorez d'autres modèles** : Parcourez la [bibliothèque de modèles](https://lemonade-server.ai/docs/server/server_models/) complète pour trouver des modèles optimisés pour la programmation, le raisonnement, la vision et plus encore. Utilisez l'application Lemonade ou `lemonade list` pour voir ce qui est disponible.

3. **Débloquez l'accélération GPU ROCm** : Si vous possédez un GPU AMD pris en charge, passez au moteur ROCm : `lemonade config set llamacpp.backend=rocm`. Consultez la liste des [GPU AMD pris en charge](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Consultez la spécification complète de l'API** : Lemonade prend en charge les complétions de conversation, les plongements (« embeddings »), la transcription audio, la génération d'images, la synthèse vocale et plus encore. Consultez la [spécification du serveur](https://lemonade-server.ai/docs/server/server_spec/) pour tous les points de terminaison.

5. **Contribuez** : Lemonade est un projet à code source ouvert. Consultez le [guide de contribution](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) et repérez les [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

<!-- @os:linux -->
<!-- @test:id=lemonade-unload-linux timeout=60 hidden=True -->
```bash
# CI cleanup: unload the model so the GPU pool is free
lemonade unload || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-unload-windows timeout=60 hidden=True -->
```powershell
# CI cleanup: unload the model so the GPU pool is free
lemonade unload
exit 0
```
<!-- @test:end -->
<!-- @os:end -->