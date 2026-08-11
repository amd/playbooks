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
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Vue d'ensemble

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Ce guide nécessite un minimum de **32 Go** de mémoire système.
<!-- @device:end -->

n8n est une plateforme d'automatisation de workflows qui vous permet de connecter des applications et des services à l'aide d'un éditeur visuel basé sur des nœuds.

Ce guide vous apprend à configurer un résumé de l'actualité financière assisté par IA qui extrait la section économique d'AP News, en tire les titres clés, et utilise un LLM local exécuté sur votre système pour générer un résumé destiné aux investisseurs.

## Ce que vous allez apprendre

- Comment installer et lancer n8n
- Importer et configurer un workflow prédéfini
- Se connecter à Lemonade à l'aide de l'intégration native n8n
- Comprendre les nœuds de workflow et le flux de données

## Qu'est-ce que Lemonade ?

[Lemonade](https://lemonade-server.ai) est une plateforme de service de LLM local conçue pour le matériel AMD. Elle fournit une API compatible OpenAI qui s'exécute entièrement sur votre machine : vos données ne quittent jamais votre appareil.

Dans ce guide, nous utilisons Lemonade pour servir un LLM local auquel n8n se connecte pour des tâches assistées par IA. 

n8n inclut un **nœud Lemonade natif** (`Lemonade Chat Model`) qui offre une intégration de premier ordre, sans nécessiter de configuration manuelle. Cela simplifie la connexion de votre LLM local aux workflows d'automatisation.

## Configuration de la mémoire

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Vérifier les mises à jour logicielles

<!-- @require:software-update -->
<!-- @device:end -->

## Installation des prérequis logiciels
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @require:lemonade,podman -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @var:id=lemonade_model value="gpt-oss-120b-mxfp-GGUF" -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="gpt-oss-20b-mxfp4-GGUF" -->
<!-- @device:end -->


<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade (robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1
if (-not $entry) { throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "${lemonade_model}"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
  -H "Content-Type: application/json" `
  --data-binary "@$tmpBody"
  if (-not $out) { throw "Empty response from Lemonade chat/completions" }
}
finally {
  Remove-Item  $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->


<!-- @os:linux -->
<!-- @test:id=lemonade-chat-linux timeout=1200 hidden=True -->
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
    if item.get("id") == "${lemonade_model}":
        entry = item
        break

if entry is None:
    print("Model ${lemonade_model} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: ${lemonade_model} model is downloaded in Lemonade")
PY

body='{
  "model": "${lemonade_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->

## Installation de n8n
<!-- @os:windows -->
Installez n8n globalement à l'aide de npm.

> **Remarque** : Vous pourriez voir des avertissements npm. C'est normal.

```bash
npm install -g n8n
```

<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **Astuce** : Les utilisateurs Windows devront peut-être modifier leur politique d'exécution PowerShell (par exemple,
> en la définissant sur RemoteSigned ou Unrestricted) avant d'exécuter certaines commandes PowerShell.
<!-- @os:end -->


<!-- @os:windows -->
> **Problème de PATH** : Si `n8n --version` indique que la commande est introuvable, assurez-vous que le répertoire bin global npm figure dans le `PATH` de l'utilisateur. Le chemin d'installation habituel est `C:\Users\<username>\AppData\Roaming\npm`. 
> Ajoutez-le au chemin utilisateur (Modifier les variables d'environnement système > Variables d'environnement > Modifier le chemin utilisateur) et rechargez le terminal. 

<!-- @os:end -->

<!-- @os:linux -->
Nous allons maintenant utiliser le service Podman pour conteneuriser notre installation de n8n.

Veuillez télécharger le fichier suivant dans un répertoire de votre choix : [compose.yml](assets/compose.yml)

Dans ce répertoire, exécutez la commande suivante :
```bash
podman compose up -d
```

Cela devrait installer n8n et écrire dans un stockage persistant.

Lancez n8n en saisissant `localhost:5678` dans la barre d'adresse de votre navigateur.
<!-- @os:end -->

<!-- @os:windows -->
## Lancement de n8n

Démarrez n8n depuis le terminal :

```bash
n8n start
```

<!-- @test:id=n8n-start-windows timeout=300 hidden=True -->
```powershell
$N8N_CMD = "$env:APPDATA\npm\n8n.cmd"
$p = Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$N8N_CMD`" start" -NoNewWindow -PassThru
try {
  $ok = $false
  for ($i=0; $i -lt 120; $i++) {
    # Check HTTP status code only (body may be empty)
    $code = curl.exe -s -o NUL -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz
    if ($LASTEXITCODE -eq 0 -and $code -eq "200") { $ok = $true; break }
    Start-Sleep -Seconds 1
  }
  if (-not $ok) { throw "n8n not ready on http://127.0.0.1:5678/healthz" }
  Write-Host "OK: n8n server is responding"
} finally {
  # Kill the process actually listening on 5678
  $conn = Get-NetTCPConnection -LocalPort 5678 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($conn) { Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue }
  # Also kill wrapper pid just in case
  if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=n8n-start-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
p=""
cleanup() {
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

n8n start >/tmp/n8n-test.log 2>&1 &
p=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "n8n not ready on http://127.0.0.1:5678/healthz"
  exit 1
fi

echo "OK: n8n server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
n8n démarre un serveur web local. Appuyez sur `'o'` ou ouvrez votre navigateur à l'adresse `http://localhost:5678` pour accéder à l'éditeur.
<!-- @os:end -->


> **Astuce** : Gardez la fenêtre du terminal ouverte pendant l'utilisation de n8n. La fermer pourrait arrêter le serveur.

## Lancement de Lemonade

Lemonade est le serveur local qui exécutera un modèle et se connectera à n8n. 

<!-- @os:linux -->
Ouvrez l'interface graphique de Lemonade en cliquant sur l'icône Lemonade dans la barre des tâches. Vous pouvez y parcourir les modèles, les backends, et charger les modèles préinstallés.
<!-- @os:end -->

<!-- @os:windows -->
Ouvrez l'interface graphique de Lemonade en cliquant sur l'icône Lemonade. Faites un clic droit sur l'icône dans la barre système pour ouvrir l'application. Vous pouvez ensuite ajouter des modèles, des backends, et charger les modèles préinstallés.
<!-- @os:end -->

>**Astuce** : Une fois en cours d'exécution, l'interface graphique de Lemonade est également accessible à l'adresse http://localhost:13305

Vous pouvez également ouvrir un terminal et exécuter `lemonade list` pour voir les modèles installés. Ensuite, exécutez :

<!-- @device:halo_box -->
<!-- @os:linux -->
```bash
lemonade run gpt-oss-120b-Q4_K_M --llamacpp vulkan
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo -->
```bash
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
```bash
lemonade run gpt-oss-20b-GGUF --llamacpp vulkan
```
<!-- @device:end -->


## Configuration du workflow

### Étape 1 : S'inscrire ou se connecter à n8n

Lorsque vous ouvrez n8n pour la première fois, il vous sera demandé de créer un compte ou de vous connecter :

1. Ouvrez `http://localhost:5678` dans votre navigateur
2. Créez un nouveau compte local avec votre adresse e-mail, ou connectez-vous si vous en avez déjà un
3. Une fois connecté, vous verrez le tableau de bord n8n

> **Astuce** : Si vous êtes bloqué hors de votre compte, essayez `n8n user-management:reset`

### Étape 2 : Importer le workflow

Nous avons fourni un workflow prédéfini que vous pouvez importer directement :

1. Téléchargez le fichier de workflow suivant : [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Cliquez sur **Start from Scratch** pour ouvrir l'éditeur de workflow. Vous pouvez aussi cliquer sur le bouton + en haut à gauche, puis sur **Add workflow**.
3. Cliquez sur le menu **...** (trois points) dans la barre supérieure droite et sélectionnez **Import from file**
4. Sélectionnez le fichier `financial-news-workflow.json` téléchargé
5. Le workflow apparaîtra sur le canevas
### Étape 3 : Comprendre le workflow

Le workflow importé contient 9 nœuds connectés :

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Nœud | Objectif |
|------|---------|
| **When clicking 'Execute workflow'** | Déclencheur manuel pour démarrer le workflow |
| **Fetch Financial News Webpage** | Requête HTTP GET vers `https://apnews.com/business` |
| **Delay to Ensure Page Load** | Nœud d'attente pour s'assurer que le contenu de la page est entièrement chargé |
| **Extract News Headlines & Text** | Nœud HTML qui extrait les titres, les sélections de la rédaction, les principales actualités et les actualités régionales à l'aide de sélecteurs CSS |
| **Clean Extracted News Data** | Nœud Set qui combine toutes les données extraites en un seul champ texte |
| **AI Financial News Summarizer** | Agent IA qui traite les actualités avec une invite système d'analyste financier |
| **Lemonade Chat Model** | Se connecte à votre serveur Lemonade local exécutant le LLM |
| **Structured Output Parser** | Formate la sortie de l'IA en JSON structuré |
| **Convert to File** | Convertit le résumé en un fichier téléchargeable |

### Étape 4 : Configurer les identifiants Lemonade

Avant d'exécuter le workflow, vous devez le connecter à votre serveur Lemonade local :

1. Double-cliquez sur le nœud **Lemonade Chat Model** dans n8n
2. Dans le menu déroulant **Credential to connect with**, sélectionnez **Create New Credential**
3. Saisissez les valeurs du tableau ci-dessous et cliquez sur enregistrer.
4. Choisissez le modèle pertinent que vous avez chargé dans Lemonade Server.

  | Champ | Valeur |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Remarque** : Avant de tester, exécutez `lemonade status` dans un terminal pour confirmer que le serveur Lemonade est en cours d'exécution.
<!-- @device:halo_box -->
> Ce workflow utilise GPT-OSS-120B, préinstallé dans Lemonade. Vous pouvez le remplacer par d'autres modèles chargés dans les paramètres du nœud Lemonade Chat Model.
<!-- @device:end -->

### Étape 5 : Tester le workflow

1. Assurez-vous que Lemonade est en cours d'exécution avec un modèle chargé
2. Cliquez sur **Execute workflow** en bas au centre du canevas
3. Observez chaque nœud s'exécuter de gauche à droite : ils passent au vert une fois terminés
4. Double-cliquez sur le nœud **AI Financial News Summarizer** pour voir le résumé généré dans le panneau du bas.
5. Double-cliquez sur le nœud **Convert to File** pour télécharger le fichier texte correspondant dans le panneau du bas.

## Comprendre l'agent IA

Le AI Financial News Summarizer utilise une invite système conçue pour l'analyse financière :

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

L'agent reçoit les données d'actualités nettoyées et produit un résumé structuré avec le sentiment du marché.

### Enregistrer votre workflow

Cliquez sur le nom du workflow en haut et renommez-le si vous le souhaitez. Les workflows s'enregistrent automatiquement au fur et à mesure.

## Étapes suivantes

- **Planifier l'automatisation** : Remplacez le déclencheur manuel par un **Schedule Trigger** pour une exécution quotidienne
- **Envoyer des notifications** : Ajoutez un nœud **Discord**, **Slack** ou **Email** pour recevoir les résumés
- **Essayer différents modèles** : Modifiez le modèle dans le nœud Lemonade Chat Model pour expérimenter avec différents LLM
- **Personnaliser l'extraction** : Modifiez les sélecteurs CSS du nœud HTML Extract pour cibler différentes sections d'actualités
- **Essayer différents backends** : n8n prend également en charge [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio et d'autres backends de LLM locaux

### Explorer les modèles n8n

n8n propose des centaines de modèles de workflows préconstruits. Parcourez la bibliothèque officielle de modèles à l'adresse :

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Recherchez « AI », « LLM » ou « automation » pour trouver des workflows que vous pouvez importer et personnaliser.

Pour plus d'informations, consultez la [documentation n8n](https://docs.n8n.io/).

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