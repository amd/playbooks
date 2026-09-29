<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduction automatique.** Cette page a été traduite automatiquement de l'anglais et n'a pas été révisée par un humain. Elle peut contenir des erreurs, et certaines instructions, commandes, options de téléchargement, disponibilités de produits ou autres contenus peuvent varier selon la langue ou la région. En cas d'incompatibilité ou de divergence, la version originale anglaise du playbook fait foi.
<!-- auto-translated-disclaimer:end -->

# Exécution locale de l'agent Hermes avec Lemonade Server

## Aperçu

[**Hermes Agent**](https://hermes-agent.nousresearch.com/) est un agent d'IA auto-améliorant conçu par Nous Research. Il possède une boucle d'apprentissage intégrée, crée des compétences à partir de l'expérience, construit une mémoire persistante de qui vous êtes d'une session à l'autre, et peut exécuter des automatisations planifiées en votre nom. Contrairement à un simple assistant conversationnel, Hermes entreprend de véritables actions : exécuter des commandes shell, écrire des fichiers, naviguer sur le Web et déléguer des flux de travail parallèles à des sous-agents.

[**Lemonade Server**](https://lemonade-server.ai/) est le moteur d'inférence local qui l'alimente. Il s'agit d'un serveur open source qui exécute des modèles d'IA générative directement sur votre matériel AMD et les expose par l'entremise de l'API standard OpenAI.

Ensemble, ils forment une pile d'agent IA entièrement locale : Lemonade prend en charge l'inférence des modèles sur votre GPU, et Hermes fournit la boucle d'agent, la mémoire, les compétences et la passerelle de messagerie.

> **Avant de continuer :** Hermes Agent est un agent d'IA hautement autonome. Accorder à un agent d'IA quel qu'il soit l'accès à votre système peut entraîner des résultats imprévisibles ou involontaires. Ne poursuivez que si vous comprenez les risques et êtes à l'aise avec l'idée qu'un logiciel autonome agisse en votre nom.

---

## Ce que vous allez apprendre

À la fin de ce guide pratique, vous serez en mesure de :

- **Installer Hermes Agent** et le configurer pour utiliser **Lemonade Server** comme moteur d'IA.
- **(Recommandé) Activer l'isolation Docker/Podman** afin d'isoler les actions de l'agent de votre système hôte.
- **Démarrer la passerelle Hermes** et confirmer que votre agent est prêt.
- **Connecter un canal de communication** (Discord ou Telegram) afin de pouvoir discuter avec votre agent depuis n'importe quel appareil.

---

<!-- @device:halo_box,halo,stx,krk -->
## Configuration de la mémoire

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Vérifier les mises à jour logicielles

<!-- @require:software-update -->
<!-- @device:end -->

## Installation des prérequis logiciels

<!-- @os:linux -->
- Un PC exécutant **Ubuntu 24.04+** ou une distribution Linux compatible basée sur Debian avec `apt-get`
- Au moins **12 Go de RAM** (64 Go+ recommandés pour les modèles plus volumineux)
- **~10 à 30 Go d'espace disque libre** pour les poids du modèle
- [Podman](https://podman.io/docs/installation) (facultatif, pour l'isolation de Hermes Agent)
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @os:windows -->
- Un PC exécutant **Windows 10/11**
- Au moins **12 Go de RAM** (64 Go+ recommandés pour les modèles plus volumineux)
- **~10 à 30 Go d'espace disque libre** pour les poids du modèle
- Podman (facultatif, pour l'isolation de Hermes Agent). Installez-le dans WSL :
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @device:halo_box -->
> Podman est préinstallé sur Halo Box, aucune configuration n'est nécessaire
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Récupérer et charger le modèle recommandé

Le modèle recommandé pour ce guide pratique est **Qwen3.6-35B-A3B-GGUF** d'Unsloth, un modèle MoE performant doté d'une fenêtre de contexte de 263 k jetons, particulièrement adapté aux charges de travail d'agent. Ce modèle utilise la quantification UD-Q4_K_XL. Récupérez-le maintenant :

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Chargez-le ensuite avec une grande fenêtre de contexte et enregistrez ce paramètre pour les prochaines exécutions :

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end -->

Le modèle a une longueur de contexte par défaut de 262 144 jetons. Si vous rencontrez des erreurs de dépassement de mémoire (OOM), envisagez de réduire la fenêtre de contexte.

> **Astuce : désactiver le mode réflexion pour des réponses d'agent plus rapides :** Qwen3.6-35B-A3B fonctionne par défaut en mode réflexion, ce qui ajoute une latence avant chaque réponse. Pour les boucles d'agent, cette surcharge s'accumule rapidement. Le dépôt [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) propose une configuration prête à l'emploi qui désactive le mode réflexion. Pour l'utiliser, téléchargez le fichier et importez-le :
>
> ```bash
> curl -LO https://raw.githubusercontent.com/lemonade-sdk/recipes/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json
> lemonade import Qwen3.6-35B-A3B-NoThinking.json
> ```

---

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$modelsJson = $null
for ($i = 0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}

if (-not $modelsJson) {throw "Lemonade server not ready on http://127.0.0.1:13305"}
Write-Host "OK: Lemonade server is responding"

$parsed = $modelsJson | ConvertFrom-Json
$entry = $parsed.data | Where-Object { $_.id -eq "${hermes_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${hermes_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${hermes_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${hermes_model} model is downloaded in Lemonade"

if ($entry.recipe_options.ctx_size -ne 262144) {
  throw "Model ${hermes_model} is not saved with ctx_size=262144. Run: lemonade load ${hermes_model} --ctx-size 262144 --save-options"
}
Write-Host "OK: ${hermes_model} is saved with ctx_size=262144"

$body = @{
  model = "${hermes_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "hermes-lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpBody"
  if (-not $out) {throw "Empty response from Lemonade chat/completions"}
  Write-Host "OK: Lemonade chat/completions returned a response"
}
finally {
  Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue
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
model_id = "${hermes_model}"

entry = None
for item in data.get("data", []):
    if item.get("id") == model_id:
        entry = item
        break

if entry is None:
    print(f"Model {model_id} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print(f"Model {model_id} is present but not downloaded in Lemonade. Please download it before running CI.")
    sys.exit(1)

print(f"OK: {model_id} model is downloaded in Lemonade")

ctx_size = entry.get("recipe_options", {}).get("ctx_size")
if ctx_size != 262144:
    print(f"Model {model_id} is not saved with ctx_size=262144. Run: lemonade load {model_id} --ctx-size 262144 --save-options")
    sys.exit(1)
print(f"OK: {model_id} is saved with ctx_size=262144")
PY

body='{
  "model": "${hermes_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body")"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Lemonade chat/completions returned a response"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->

## Configurer WSL

Nous exécutons Hermes Agent dans WSL et le connectons à Lemonade s'exécutant nativement sous Windows. Cela vous offre un environnement shell Linux pour Hermes tout en conservant l'accélération GPU de Lemonade du côté Windows.

### Installer WSL et Ubuntu

Ouvrez PowerShell en tant qu'administrateur et installez le noyau WSL :

```powershell
wsl --install --no-distribution
```

Installez ensuite Ubuntu :

```powershell
wsl --install -d Ubuntu-24.04
```

### Activer systemd dans WSL

Exécutez ceci dans le terminal Ubuntu :

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Redémarrez WSL :

```powershell
wsl --shutdown
wsl
```

### Établir un pont entre Lemonade sous Windows et WSL

WSL2 s'exécute dans un réseau virtuel. Lemonade sous Windows se lie à `127.0.0.1`, que WSL ne peut pas atteindre directement. Un proxy de port Windows achemine le trafic depuis l'adresse IP de la passerelle WSL vers l'hôte local Windows.

**Trouvez l'adresse IP de la passerelle WSL** (exécutez ceci dans WSL) :

```bash
ip route show default | awk '{print $3}' | head -1
```

**Ajoutez le proxy de port** (exécutez ceci dans PowerShell en tant qu'administrateur, en remplaçant `<WSL-Gateway-IP>` par l'adresse IP de votre passerelle WSL) :

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Ajoutez une règle de pare-feu** (dans la même fenêtre PowerShell avec droits élevés) :

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Vérifiez depuis WSL** :

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Si vous avez déjà chargé le modèle Qwen3.6-35B-A3B-GGUF à l'étape précédente, vous devriez voir une sortie JSON répertoriant votre modèle chargé.

```json
{
  "data": [
    {
      "checkpoint": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL",
      "checkpoints": {
        "main": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL"
      },
      "mmproj": "unsloth/Qwen3.6-35B-A3B-GGUF:mmproj-F16.gguf",
      ....
    }
  ],
  "object": "list"
}
```

> La règle `netsh portproxy` persiste après un redémarrage, mais l'adresse IP de la passerelle WSL peut changer après un `wsl --shutdown`. Si Lemonade devient inaccessible depuis WSL après un redémarrage, obtenez l'adresse IP de passerelle mise à jour et mettez à jour le proxy avec cette nouvelle adresse.

<!-- @test:id=wsl-lemonade-bridge-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

echo "WSL gateway IP: $WINDOWS_HOST"

models_json="$(curl -fsS --max-time 5 "http://$WINDOWS_HOST:13305/api/v1/models")"

if [ -z "$models_json" ]; then
  echo "Could not reach Lemonade from WSL at http://$WINDOWS_HOST:13305/api/v1/models"
  echo "Check the Windows netsh portproxy and firewall rule from the README."
  exit 1
fi

echo "$models_json" | python3 -m json.tool >/dev/null
echo "OK: WSL can reach native Windows Lemonade through the bridge"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "wsl-lemonade-bridge-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "WSL Lemonade bridge test failed"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->

---
<!-- @os:end -->

## Installer Hermes Agent

<!-- @os:windows -->
> Exécutez les commandes de cette section dans votre **terminal WSL**, sauf indication contraire.
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

L'option `--skip-setup` ignore l'assistant de configuration interactif afin que vous puissiez configurer manuellement le moteur de modèle à l'étape suivante.

Rechargez votre shell :

```bash
source ~/.bashrc
```

Confirmez l'installation :

```bash
hermes --version
```

Exécutez un auto-diagnostic pour vérifier toutes les dépendances :

```bash
hermes doctor
```

> **Astuce :** Si vous voyez `command not found` après l'installation, ajoutez Hermes à votre PATH :
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> Pour rendre ce changement permanent, ajoutez la ligne ci-dessus à votre fichier `~/.bashrc` ou `~/.zshrc`.

<!-- @os:linux -->
<!-- @test:id=hermes-version-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
hermes --version
# hermes doctor is a self-diagnostic; run it for the logs but don't gate CI on it (it can probe live model/runtime state that varies on the runner).
hermes doctor || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-version-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
hermes --version
# hermes doctor is a self-diagnostic; run it for the logs but don't gate CI on it (it can probe live model/runtime state that varies on the runner).
hermes doctor || true
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-version-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes version check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

---
## Configurer Hermes pour utiliser Lemonade

Hermes stocke sa configuration de modèle dans `~/.hermes/config.yaml`. Vous pouvez soit utiliser le sélecteur interactif `hermes model`, soit rédiger la configuration directement.

### Option 1 : sélecteur interactif

<!-- @os:windows -->
> Exécutez la commande suivante dans votre **terminal WSL**.
<!-- @os:end -->

<!-- @os:linux -->
```bash
hermes model
```
<!-- @os:end -->

<!-- @os:windows -->
```bash
hermes model
```
<!-- @os:end -->

Lorsque vous y êtes invité :

1. Sélectionnez **Custom endpoint (enter URL manually)**
<!-- @os:linux -->
2. **API base URL :** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **API base URL :** utilisez l'adresse IP de la passerelle WSL : exécutez `ip route show default | awk '{print $3}' | head -1` dans WSL pour l'obtenir, puis saisissez `http://<WSL-Gateway-IP>:13305/api/v1`
<!-- @os:end -->
3. **Clé API :** `lemonade`
4. **Mode de compatibilité API :** `1` (détection automatique)
5. **Sélectionner le modèle :** choisissez `Qwen3.6-35B-A3B-GGUF` dans la liste
6. **Longueur de contexte en jetons :** `262144`
7. **Nom d'affichage :** `local-lemonade` (ou tout autre nom de votre choix)

`hermes model` enregistre à la fois la sélection du modèle actif et une entrée nommée `custom_providers` qui stocke la longueur de contexte avec le point de terminaison. Le résultat dans `~/.hermes/config.yaml` ressemble à ceci :

```yaml
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
```

### Option 2 : rédiger la configuration directement

<!-- @os:linux -->

```bash
mkdir -p ~/.hermes
cat >> ~/.hermes/config.yaml <<'EOF'
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF
```

<!-- @test:id=hermes-lemonade-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# Write the model config fresh so the test is idempotent across CI runs.
# (An append would create duplicate YAML keys and later break the gateway test.)
mkdir -p "$HOME/.hermes"
rm -f "$HOME/.hermes/config.yaml"
cat > "$HOME/.hermes/config.yaml" <<'EOF'
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF

config="$HOME/.hermes/config.yaml"

grep -q "provider: custom" "$config"
grep -q "Qwen3.6-35B-A3B-GGUF" "$config"
grep -q "13305" "$config"
grep -q "context_length: 262144" "$config"

echo "OK: Hermes config.yaml contains Lemonade model configuration"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->

Dans votre terminal WSL, obtenez l'adresse IP de l'hôte Windows et rédigez la configuration :

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)

mkdir -p ~/.hermes
cat >> ~/.hermes/config.yaml <<EOF
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://$WINDOWS_HOST:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://$WINDOWS_HOST:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF
```

<!-- @test:id=hermes-lemonade-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"
if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

# Write the model config fresh so the test is idempotent across CI runs.
# (An append would create duplicate YAML keys and later break the gateway test.)
mkdir -p "$HOME/.hermes"
rm -f "$HOME/.hermes/config.yaml"
cat > "$HOME/.hermes/config.yaml" <<EOF
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://$WINDOWS_HOST:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://$WINDOWS_HOST:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF

config="$HOME/.hermes/config.yaml"

grep -q "provider: custom" "$config"
grep -q "Qwen3.6-35B-A3B-GGUF" "$config"
grep -q "13305" "$config"
grep -q "context_length: 262144" "$config"

echo "OK: Hermes config.yaml contains Lemonade model configuration (Windows host)"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-lemonade-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes Lemonade config check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

---

## (Recommandé) Activer le bac à sable Podman

Hermes Agent peut acheminer toutes les opérations de shell et de fichiers de l'agent par l'intermédiaire d'un conteneur isolé plutôt que de les exécuter directement sur votre hôte. Cela limite le rayon d'action de toute action non intentionnelle au bac à sable, laissant intacts le système de fichiers et le réseau de votre hôte.

Créez une image de bac à sable légère :

<!-- @os:linux -->
```bash
podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE
```

<!-- @test:id=hermes-sandbox-image-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

podman version

podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

echo "OK: Hermes sandbox Podman image is available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
Ouvrez votre terminal WSL :

```powershell
wsl -d Ubuntu-24.04
```

Ensuite, créez une image de bac à sable légère :

```bash
podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE
```

<!-- @test:id=hermes-sandbox-image-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

podman version

podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

echo "OK: Hermes sandbox Podman image is available inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-sandbox-image-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "Hermes sandbox image build failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

Configurez ensuite Hermes pour utiliser Podman comme environnement d'exécution de conteneurs et définissez le moteur de terminal :

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> Le `terminal.backend` demeure `docker`.
> `HERMES_DOCKER_BINARY` indique à Hermes d'utiliser Podman comme environnement d'exécution plutôt que Docker.

<!-- @os:linux -->
<!-- @test:id=hermes-sandbox-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config test first."
  exit 1
fi

# The sandbox image must exist before Hermes can use it as the terminal backend.
podman image inspect hermes-sandbox:bookworm-slim >/dev/null

# Point Hermes at Podman as the container runtime (idempotent: drop any prior line first).
mkdir -p "$HOME/.hermes"
touch "$HOME/.hermes/.env"
grep -v '^HERMES_DOCKER_BINARY=' "$HOME/.hermes/.env" > "$HOME/.hermes/.env.tmp" || true
mv "$HOME/.hermes/.env.tmp" "$HOME/.hermes/.env"
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> "$HOME/.hermes/.env"

# Append the terminal backend block (config.yaml is rewritten fresh by the model-config test each run, so this appends exactly once per run).
cat >> "$config" <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF

grep -q "HERMES_DOCKER_BINARY=/usr/bin/podman" "$HOME/.hermes/.env"
grep -q "backend: docker" "$config"
grep -q "docker_image: hermes-sandbox:bookworm-slim" "$config"

echo "OK: Hermes sandbox (Podman) configuration was written"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-sandbox-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config test first."
  exit 1
fi

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

mkdir -p "$HOME/.hermes"
touch "$HOME/.hermes/.env"
grep -v '^HERMES_DOCKER_BINARY=' "$HOME/.hermes/.env" > "$HOME/.hermes/.env.tmp" || true
mv "$HOME/.hermes/.env.tmp" "$HOME/.hermes/.env"
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> "$HOME/.hermes/.env"

cat >> "$config" <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF

grep -q "HERMES_DOCKER_BINARY=/usr/bin/podman" "$HOME/.hermes/.env"
grep -q "backend: docker" "$config"
grep -q "docker_image: hermes-sandbox:bookworm-slim" "$config"

echo "OK: Hermes sandbox (Podman) configuration was written inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-sandbox-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "Hermes sandbox config failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

Hermes va maintenant démarrer un conteneur de bac à sable persistant et acheminer tous les appels d'outils `terminal` et de fichiers par son intermédiaire. Le conteneur partage le cycle de vie du processus Hermes, est réutilisé pour tous les appels d'outils, et est détruit lorsque Hermes se ferme.

> **Vérifier que le bac à sable fonctionne :** démarrez Hermes (`hermes`) et demandez-lui d'exécuter `run hostname` — vous devriez voir un court identifiant de conteneur au lieu du nom d'hôte de votre machine. Vous pouvez également lui demander d'exécuter `rm -rf <path-to-a-dummy-file/folder>` : Hermes confirmera la suppression, mais le dossier restera présent sur votre hôte. La commande s'est exécutée à l'intérieur du répertoire `$HOME` isolé du conteneur, et non le vôtre.

> **Besoin d'une isolation plus poussée?** Hermes propose également une image Docker officielle (`nousresearch/hermes-agent`) qui exécute l'ensemble du processus de l'agent à l'intérieur d'un conteneur — passerelle, outils, et le reste. Consultez la [documentation Docker de Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/docker) pour les détails de configuration.

---

<!-- @os:linux -->
## (Recommandé) Intégration de Hermes avec les services Firecrawl

Hermes peut naviguer sur des sites Web et en extraire du contenu à l'aide de ses outils Web intégrés. Cependant, de nombreux sites Web modernes utilisent des systèmes de détection de robots, qui bloquent les simples requêtes HTTP et renvoient des pages de vérification au lieu du contenu réel. Par conséquent, Hermes peut être incapable d'extraire de manière fiable des informations de ces sites.

Pour surmonter cette limitation, [Firecrawl](https://docs.firecrawl.dev/introduction) offre un service auto-hébergé d'exploration Web et d'extraction de contenu capable de contourner ces vérifications et de libérer tout le potentiel de l'automatisation de Hermes.

Dans cette configuration, Firecrawl s'exécute sous la forme d'un ensemble de conteneurs Docker gérés avec Podman. Pour simplifier la gestion du cycle de vie et le démarrage automatique, nous enregistrons Firecrawl comme service `systemd` au niveau utilisateur qui orchestre la pile Podman Compose sous-jacente. Cela permet à Hermes de démarrer, d'arrêter et de vérifier le service Firecrawl à l'aide des commandes standards `systemctl --user`, plutôt que d'interagir directement avec les conteneurs.

Pour simplifier les choses, nous avons divisé l'ensemble du processus en quatre étapes :

---

### 1. Enregistrer le service système
Accédez au répertoire de configuration utilisateur de systemd :
```bash
cd ~/.config/systemd/user
```
Créez et ouvrez un nouveau fichier nommé `firecrawl.service`.
```bash
nano firecrawl.service
```
Copiez et collez la configuration suivante :
```bash
[Unit]
Description=Firecrawl
After=podman.service
Requires=podman.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${HOME}/firecrawl

# Optional: Validate config before starting
ExecStartPre=/usr/bin/podman -f hermes-compose.yaml config --quiet

# Start containers in detached mode
ExecStart=/usr/bin/podman compose -f hermes-compose.yaml up -d --remove-orphans

# Stop containers when the service stops
ExecStop=/usr/bin/podman compose -f hermes-compose.yaml down

[Install]
WantedBy=default.target

```
À ce stade, le service a été défini, mais n'est pas encore enregistré auprès de `systemd`.
Assurez-vous que le nom de fichier correspond exactement à celui que vous avez créé ci-dessus, puis exécutez :
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Si l'opération réussit, vous devriez voir la sortie suivante :

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` contient des liens symboliques vers les services configurés pour démarrer automatiquement.

### 2. Configurer Firecrawl pour votre service

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) convient parfaitement à ceux qui ont besoin d'un contrôle total sur leurs environnements d'extraction de données et de traitement, mais implique en contrepartie des efforts supplémentaires de maintenance et de configuration.

Commencez par cloner le dépôt :
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Créez le fichier `.env` dans le répertoire racine `/firecrawl` :
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY=""

# ===== Proxy =====
# PROXY_SERVER can be a full URL (e.g. http://0.1.2.3:1234) or just an IP and port combo (e.g. 0.1.2.3:1234)
# Do not uncomment PROXY_USERNAME and PROXY_PASSWORD if your proxy is unauthenticated
# PROXY_SERVER=
# PROXY_USERNAME=
# PROXY_PASSWORD=

# This key lets you access the queue admin panel. Change this if your deployment is publicly accessible.
BULL_AUTH_KEY=CHANGEME

# ===== System Resource Configuration =====
# Maximum CPU usage threshold (0.0-1.0). Worker will reject new jobs when CPU usage exceeds this value.
# Default: 0.8 (80%)
# MAX_CPU=0.8

# Maximum RAM usage threshold (0.0-1.0). Worker will reject new jobs when memory usage exceeds this value.
# Default: 0.8 (80%)
# MAX_RAM=0.8
```
> Attribuez à `BULL_AUTH_KEY` un secret robuste, en particulier pour tout déploiement accessible depuis des réseaux non fiables.
### 3. Déploiement de Hermes via Compose

Avant de continuer, assurez-vous d'avoir récupéré la dernière image Docker de Hermes :
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
Une fois cela fait, téléchargez le fichier Compose de Hermes [hermes-compose.yaml](assets/hermes-compose.yaml) et placez-le dans le répertoire racine `/firecrawl` :

> Cette convention est requise pour que `systemd` puisse localiser et démarrer le service correctement, comme spécifié dans `WorkingDirectory=${HOME}/firecrawl`.

> Vous pouvez toujours étendre la pile en ajoutant d'autres services Firecrawl au besoin. La liste complète des services disponibles se trouve dans le fichier officiel [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Lancement du service Hermes via Firecrawl 

Avant de céder le contrôle à `systemd`, validez que tout fonctionne correctement en exécutant la pile manuellement :
```bash
podman compose -f hermes-compose.yaml up -d
```
Si tout est configuré correctement, vous devriez voir le conteneur Hermes démarrer et la sortie de votre ligne de commande devrait ressembler à ceci :
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

Une fois la validation effectuée, arrêtez la pile avant de continuer :
```bash
podman compose -f hermes-compose.yaml down
```
Maintenant que tout est validé, démarrez le service via `systemd` :
```bash
systemctl --user start firecrawl.service
```
[L'API de Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints) est accessible depuis le conteneur interactif, et le tableau de bord Web est disponible sur le même hôte et le même port à l'adresse http://127.0.0.1:9119.
<p align="center">
  <img src="assets/System_Service_launch.png" width="500" height="500" />
</p>

Pour arrêter le service, exécutez :
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Hermes natif

Démarrez directement une session CLI interactive : 

```bash
hermes
```

<!-- @os:linux -->
<!-- @test:id=hermes-gateway-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config step first."
  exit 1
fi

log="/tmp/hermes-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

hermes gateway run >"$log" 2>&1 &
gateway_pid=$!

# `hermes gateway run` is a long-running message bridge + cron scheduler with no
# HTTP health endpoint, so we detect a successful boot by (1) a known startup
# marker appearing in the log and (2) the process still being alive afterwards
# (i.e. it parsed config.yaml and did not crash). "No messaging platforms
# enabled" is expected in CI (no channel token) and is not a failure.
ok=false
for i in $(seq 1 60); do
  if grep -qE "Hermes Gateway Starting|gateway\.run|cron scheduler" "$log" 2>/dev/null; then
    ok=true
    break
  fi
  if ! kill -0 "$gateway_pid" 2>/dev/null; then
    echo "Hermes gateway process exited before it finished starting"
    break
  fi
  sleep 1
done

# Give it a moment to surface any immediate post-banner crash, then confirm it is still running.
sleep 3

if [ "$ok" = "true" ] && kill -0 "$gateway_pid" 2>/dev/null; then
  echo "OK: Hermes gateway started successfully"
else
  echo "Hermes gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-gateway-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config step first."
  exit 1
fi

log="/tmp/hermes-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

hermes gateway run >"$log" 2>&1 &
gateway_pid=$!

# `hermes gateway run` is a long-running message bridge + cron scheduler with no
# HTTP health endpoint, so we detect a successful boot by (1) a known startup
# marker appearing in the log and (2) the process still being alive afterwards
# (i.e. it parsed config.yaml and did not crash). "No messaging platforms
# enabled" is expected in CI (no channel token) and is not a failure.
ok=false
for i in $(seq 1 60); do
  if grep -qE "Hermes Gateway Starting|gateway\.run|cron scheduler" "$log" 2>/dev/null; then
    ok=true
    break
  fi
  if ! kill -0 "$gateway_pid" 2>/dev/null; then
    echo "Hermes gateway process exited before it finished starting"
    break
  fi
  sleep 1
done

# Give it a moment to surface any immediate post-banner crash, then confirm it is still running.
sleep 3

if [ "$ok" = "true" ] && kill -0 "$gateway_pid" 2>/dev/null; then
  echo "OK: Hermes gateway started inside WSL"
else
  echo "Hermes gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-gateway-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes gateway test failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

**Félicitations, vous avez créé une pile d'agent IA entièrement locale.**

### Tableau de bord Web

Hermes inclut une interface Web pour gérer la configuration, les clés API, les modèles, les sessions, la mémoire et les tâches planifiées (cron). Ouvrez un deuxième terminal pendant que la passerelle ou la CLI est en cours d'exécution, puis lancez-le avec :

```bash
hermes dashboard
```

Cela démarre un serveur local et ouvre `http://127.0.0.1:9119` dans votre navigateur. Consultez la [documentation du tableau de bord](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard) pour la référence complète des fonctionnalités.
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## Facultatif : Connecter un canal de communication

Une fois la passerelle en cours d'exécution, vous pouvez atteindre votre agent local à partir de n'importe quel appareil. Hermes prend en charge [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord), [Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram), et d'autres

---

### Discord

Discord nécessite un serveur où **vous avez un accès administrateur** pour ajouter un robot (bot). Si vous partagez des serveurs sans en posséder, utilisez plutôt Telegram.

#### Créer une application et un robot Discord

1. Accédez au [portail des développeurs Discord](https://discord.com/developers/applications) et cliquez sur **New Application**. Donnez-lui un nom (p. ex. « hermes-bot »).
2. Dans la barre latérale, cliquez sur **Bot**. Définissez un nom d'utilisateur pour le robot.
3. Toujours sur la page Bot, faites défiler jusqu'à **Privileged Gateway Intents** et activez :
   - **Message Content Intent** (obligatoire)
   - **Server Members Intent** (recommandé)
4. Remontez et cliquez sur **Reset Token** pour générer votre jeton de robot. Copiez-le.

#### Ajouter le robot à votre serveur

1. Dans la barre latérale, cliquez sur **OAuth2 / URL Generator**.
2. Sous **Scopes**, activez `bot` et `applications.commands`.
3. Sous **Bot Permissions**, activez : View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Copiez l'URL générée, collez-la dans votre navigateur, sélectionnez votre serveur et confirmez.

#### Recueillir vos identifiants et autoriser les messages privés

Activez le mode développeur dans Discord (**User Settings / Advanced / Developer Mode**), puis :
- Faites un clic droit sur l'icône de votre serveur : **Copy Server ID**
- Faites un clic droit sur votre propre avatar : **Copy User ID**

Faites un clic droit sur l'icône de votre serveur / **Privacy Settings** / activez **Direct Messages**. Ceci est requis pour l'étape de jumelage.

#### Configurer Hermes pour Discord

Ajoutez ce qui suit à `~/.hermes/.env` :

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-discord-user-id
```

Puis démarrez la passerelle :

```bash
hermes gateway
```

Le robot devrait se connecter dans Discord en quelques secondes. Envoyez-lui un message, que ce soit en message privé ou dans un canal qu'il peut voir.

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### Créer un robot Telegram

1. Ouvrez Telegram et envoyez un message à **@BotFather**.
2. Envoyez `/newbot` et suivez les instructions. Enregistrez le jeton de robot fourni.

#### Configurer Hermes pour Telegram

Ajoutez ce qui suit à `~/.hermes/.env` :

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **Vous ne connaissez pas votre identifiant d'utilisateur Telegram?** Envoyez un message à [@userinfobot](https://t.me/userinfobot) sur Telegram, il vous répondra avec votre identifiant numérique.

Puis démarrez la passerelle :

```bash
hermes gateway
```

Envoyez un message quelconque à votre robot sur Telegram pour tester. Vous pouvez maintenant discuter avec votre agent via message privé Telegram. Consultez le [guide complet de configuration Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) pour le mode webhook et les options avancées.

---

## Prochaines étapes

Maintenant que votre agent peut recevoir des commandes depuis votre téléphone et agir sur votre machine locale, voici trois pistes intéressantes à explorer :

1. **Résumé de recherche automatisé** : Planifiez Hermes pour qu'il effectue une recherche Web sur des sujets qui vous intéressent chaque matin, résume les résultats avec votre modèle local, puis envoie un résumé à votre téléphone via Telegram ou Discord, le tout fonctionnant sur votre propre matériel, sans coûts d'infonuagique.

2. **Révision de code à la demande** : Pointez Hermes vers un dépôt GitHub, demandez-lui de réviser les demandes de tirage (pull requests) ouvertes, puis faites-lui publier des commentaires ou un résumé dans votre clavardage. Grâce au moteur de terminal Docker, toutes les opérations git s'exécutent dans le bac à sable, ce qui garde votre hôte propre.

3. **Assistant de fichiers local** : Donnez à Hermes accès à un répertoire de travail et demandez-lui d'organiser, de renommer, de résumer ou de transformer des fichiers à la demande depuis votre téléphone. Comme le moteur de terminal Docker confine toutes les écritures à l'espace de travail du bac à sable, les opérations destructrices accidentelles sont contenues.