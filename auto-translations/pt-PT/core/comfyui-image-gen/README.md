<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente a partir do inglês e não foi revista por um humano. Pode conter erros, e determinadas instruções, comandos, transferências, disponibilidade de produtos ou outro conteúdo podem variar consoante o idioma ou a região. Em caso de qualquer inconsistência ou discrepância, prevalece a versão original em inglês do playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Visão Geral

O ComfyUI é uma interface poderosa, baseada em nós, para o Stable Diffusion e outros modelos de difusão. Ao contrário das interfaces tradicionais de texto para imagem com caixas de comando simples, o ComfyUI expõe todo o pipeline de geração de imagens como um grafo visual, dando-lhe um controlo detalhado sobre cada passo, desde a codificação de texto até à manipulação do espaço latente e à descodificação final.

Este tutorial ensina-o a utilizar o ComfyUI com o modelo Z Image Turbo na sua GPU para gerar imagens de IA de alta qualidade.

## O Que Vai Aprender

- Como iniciar o ComfyUI e carregar o modelo Z-Image Turbo
- Compreender os componentes do pipeline de difusão
- Gerar imagens e ajustar os parâmetros de geração
- Guardar e partilhar fluxos de trabalho

## Definir a Configuração de Memória

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar Atualizações de Software

<!-- @require:software-update -->
<!-- @device:end -->

## Instalar os Pré-requisitos de Software

<!-- @os:windows -->
<!-- @require:driver,comfyui -->
<!-- @os:end -->

<!-- @os:linux -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Conceda ao seu utilizador acesso aos dispositivos GPU** (termine e volte a iniciar sessão para que isto tenha efeito):

```bash
sudo usermod -aG render,video $LOGNAME
```

#### Criar um Ambiente Virtual
No Linux, abra um terminal no diretório à sua escolha e execute o seguinte comando para criar um venv:

<!-- @test:id=create-venv-linux timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv comfyui-env
source comfyui-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source comfyui-env/bin/activate" -->
<!-- @device:end -->

<!-- @require:driver,pytorch,comfyui -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=comfyui-desktop-workspace-present-windows timeout=60 hidden=True -->
```powershell
# The new Comfy Desktop (since June 2026) installs into %LOCALAPPDATA%\Comfy-Desktop\
# Layout: ComfyUI-Installs\<name>\ComfyUI\ holds main.py + .venv
#         ComfyUI-Shared\ holds the shared model library
$instBase  = Join-Path $env:LOCALAPPDATA "Comfy-Desktop\ComfyUI-Installs\ComfyUI"
$comfyRoot = Join-Path $instBase "ComfyUI"
$py        = Join-Path $comfyRoot ".venv\Scripts\python.exe"
$mainPy    = Join-Path $comfyRoot "main.py"
$sharedModels = Join-Path $env:LOCALAPPDATA "Comfy-Desktop\ComfyUI-Shared\models"

if (-not (Test-Path $instBase))     { throw "Comfy Desktop instance not found at: $instBase" }
if (-not (Test-Path $comfyRoot))    { throw "ComfyUI source not found at: $comfyRoot" }
if (-not (Test-Path $py))           { throw "ComfyUI venv python not found: $py" }
if (-not (Test-Path $mainPy))       { throw "ComfyUI main.py not found: $mainPy" }
if (-not (Test-Path $sharedModels)) { throw "Comfy Desktop shared models dir not found: $sharedModels" }

Write-Host "OK: instance root: $instBase"
Write-Host "OK: ComfyUI source: $comfyRoot"
Write-Host "OK: Python: $py"
Write-Host "OK: main.py: $mainPy"
Write-Host "OK: shared models: $sharedModels"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=comfyui-clone-linux timeout=300 hidden=True -->
```bash
set -euo pipefail
if [ -d "ComfyUI/.git" ]; then
 (cd ComfyUI && git fetch --all && git reset --hard origin/master)
else
 git clone https://github.com/Comfy-Org/ComfyUI.git
fi
cd ComfyUI
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux --> 
<!-- @test:id=comfyui-requirements-linux timeout=600 hidden=True setup=activate-venv -->
```bash
set -euo pipefail
python -m pip install --upgrade pip
python -m pip install -r ./ComfyUI/requirements.txt
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=comfyui-sync-requirements-windows timeout=600 hidden=True -->
```powershell
$comfyRoot = Join-Path $env:LOCALAPPDATA "Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI"
$py  = Join-Path $comfyRoot ".venv\Scripts\python.exe"
$req = Join-Path $comfyRoot "requirements.txt"

if (-not (Test-Path $py))  { throw "ComfyUI venv python not found: $py" }
if (-not (Test-Path $req)) { throw "ComfyUI requirements.txt not found: $req" }

& $py -m pip install --upgrade --force-reinstall --no-cache-dir comfyui-frontend-package
if ($LASTEXITCODE -ne 0) { throw "Failed to install comfyui-frontend-package into workspace venv." }

& $py -c "import importlib.metadata as m; print(m.version('comfyui-frontend-package'))"
if ($LASTEXITCODE -ne 0) { throw "comfyui-frontend-package metadata still missing after install." }
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows --> 
<!-- @test:id=comfyui-backend-usable-windows timeout=120 hidden=True -->
```powershell
$py = Join-Path $env:LOCALAPPDATA "Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) { throw "Missing ComfyUI venv python: $py" }

& $py -c "import torch; print('torch', torch.__version__); print('cuda_available', torch.cuda.is_available()); print('hip', getattr(torch.version,'hip',None));"
if ($LASTEXITCODE -ne 0) { throw "Torch import/check failed in ComfyUI venv." }
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=comfyui-install-rocm-torch-linux timeout=900 hidden=True setup=activate-venv -->
```bash
set -euo pipefail

python - <<'PY'
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"ROCm/HIP version: {getattr(torch.version, 'hip', None)}")
print(f"CUDA/ROCm available: {torch.cuda.is_available()}")
print("PASS: All imports successful")
PY
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux --> 
<!-- @test:id=comfyui-verify-torch-linux timeout=120 hidden=True setup=activate-venv -->
```bash
set -euo pipefail
export LD_LIBRARY_PATH=/opt/rocm/lib:${LD_LIBRARY_PATH:-}
python -c "import torch; print('torch', torch.__version__); print('cuda_available', torch.cuda.is_available()); print('hip', getattr(torch.version,'hip',None));"
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows --> 
<!-- @test:id=comfyui-populate-models-from-cache-windows timeout=600 hidden=True -->
```powershell
# The new Comfy Desktop (since June 2026) uses a shared model library separate from the ComfyUI source.
# Models are served from %LOCALAPPDATA%\Comfy-Desktop\ComfyUI-Shared\models\
# as configured in shared_model_paths.yaml.
$modelsRoot = Join-Path $env:LOCALAPPDATA "Comfy-Desktop\ComfyUI-Shared\models"
if (-not (Test-Path $modelsRoot)) { throw "Comfy Desktop shared models dir not found: $modelsRoot" }

$cacheDiff = "C:\ModelCache\ComfyUI\models\diffusion_models\z_image_turbo_bf16.safetensors"
$cacheTE   = "C:\ModelCache\ComfyUI\models\text_encoders\qwen_3_4b.safetensors"
$cacheVAE  = "C:\ModelCache\ComfyUI\models\vae\ae.safetensors"

if (-not (Test-Path $cacheDiff)) { throw "models missing on runner: $cacheDiff" }
if (-not (Test-Path $cacheTE))   { throw "models missing on runner: $cacheTE" }
if (-not (Test-Path $cacheVAE))  { throw "models missing on runner: $cacheVAE" }

New-Item -ItemType Directory -Force -Path (Join-Path $modelsRoot "diffusion_models")
New-Item -ItemType Directory -Force -Path (Join-Path $modelsRoot "text_encoders")
New-Item -ItemType Directory -Force -Path (Join-Path $modelsRoot "vae")

Copy-Item -Force $cacheDiff (Join-Path $modelsRoot "diffusion_models\z_image_turbo_bf16.safetensors")
Copy-Item -Force $cacheTE   (Join-Path $modelsRoot "text_encoders\qwen_3_4b.safetensors")
Copy-Item -Force $cacheVAE  (Join-Path $modelsRoot "vae\ae.safetensors")

Write-Host "OK: models copied into $modelsRoot"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=comfyui-populate-models-from-cache-linux timeout=600 hidden=True -->
```bash
cd ComfyUI
cache_diff="/opt/model_cache/ComfyUI/models/diffusion_models/z_image_turbo_bf16.safetensors"
cache_te="/opt/model_cache/ComfyUI/models/text_encoders/qwen_3_4b.safetensors"
cache_vae="/opt/model_cache/ComfyUI/models/vae/ae.safetensors"
test -f "$cache_diff" || (echo "models missing on runner: $cache_diff" && exit 1)
test -f "$cache_te" || (echo "models missing on runner: $cache_te" && exit 1)
test -f "$cache_vae" || (echo "models missing on runner: $cache_vae" && exit 1)
mkdir -p models/diffusion_models models/text_encoders models/vae
cp -f "$cache_diff" models/diffusion_models/z_image_turbo_bf16.safetensors
cp -f "$cache_te" models/text_encoders/qwen_3_4b.safetensors
cp -f "$cache_vae" models/vae/ae.safetensors
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=comfyui-server-up-windows timeout=300 hidden=True -->
```powershell
$comfyRoot   = Join-Path $env:LOCALAPPDATA "Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI"
$py          = Join-Path $comfyRoot ".venv\Scripts\python.exe"
$mainPy      = Join-Path $comfyRoot "main.py"
$sharedPaths = Join-Path $env:APPDATA "Comfy Desktop\shared_model_paths.yaml"

$proc = Start-Process -FilePath $py `
 -ArgumentList "`"$mainPy`" --listen 127.0.0.1 --port 8188 --extra-model-paths-config `"$sharedPaths`"" `
 -WorkingDirectory $comfyRoot `
 -NoNewWindow -PassThru

try {
 $ok = $false
 for ($i=0; $i -lt 60; $i++) {
   $resp = curl.exe -s --max-time 2 http://127.0.0.1:8188/
   if ($LASTEXITCODE -eq 0 -and $resp) { $ok = $true; break }
   Start-Sleep -Seconds 1
 }
 if (-not $ok) { throw "ComfyUI server not reachable at http://127.0.0.1:8188/" }
 Write-Host "OK: ComfyUI server is reachable!"
} finally {
 Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux --> 
<!-- @test:id=comfyui-server-up-linux timeout=300 hidden=True setup=activate-venv -->
```bash
set -euo pipefail
export LD_LIBRARY_PATH=/opt/rocm/lib:${LD_LIBRARY_PATH:-}
python ./ComfyUI/main.py --listen 127.0.0.1 --port 8188 >/tmp/comfyui.log 2>&1 &
PID=$!

cleanup() {
 kill -9 "$PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT

ok=0
for i in $(seq 1 60); do
 resp="$(curl -s --max-time 2 http://127.0.0.1:8188/ || true)"
 if [ -n "$resp" ]; then ok=1; break; fi
 sleep 1
done

if [ "$ok" -ne 1 ]; then
 echo "ComfyUI server not reachable at http://127.0.0.1:8188/"
 tail -n 200 /tmp/comfyui.log || true
 exit 1
fi

echo "OK: ComfyUI server is reachable!"
```
<!-- @test:end --> 
<!-- @os:end -->


## Iniciar o ComfyUI

<!-- @device:halo_box -->
<!-- @os:windows -->
Para iniciar o ComfyUI no Windows, clique no Iniciador do ComfyUI Desktop que se encontra no seu Ambiente de Trabalho. Siga os passos para instalar a versão local com a AMD.

<p align="center">
  <img src="assets/new_installer.png" alt="ComfyUI Desktop Launcher and Installer" width="600"/>
</p>

Em seguida, clique no botão ComfyUI na parte superior central da aplicação. Isto abrirá um separador de definições. Abra o separador Storage e certifique-se de que os caminhos estão definidos da seguinte forma para aceder aos modelos pré-instalados.

<p align="center">
  <img src="assets/models_storage.png" alt="ComfyUI Desktop Menu Storage Tab" width="600"/>
</p>


<!-- @os:end -->

<!-- @os:linux -->
No AMD Ryzen™ AI Halo, o ComfyUI é executado num contentor pré-criado que não requer qualquer configuração adicional do Python.

Para iniciar o ComfyUI no Linux, clique no atalho do ComfyUI na barra de tarefas. Deverá abrir-se automaticamente numa janela do browser.
>**Dica**: O ComfyUI e os seus modelos estão armazenados em `~/.local/share/ComfyUI/models`. É aqui que pode adicionar manualmente fluxos de trabalho ou novos modelos.


<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
Para iniciar o ComfyUI no Windows, basta clicar no atalho do ComfyUI no seu Ambiente de Trabalho.
<!-- @os:end -->

<!-- @os:linux -->

Para iniciar o ComfyUI:

1. Certifique-se de que está dentro do diretório do ComfyUI. 
2. Execute `python3 main.py --use-pytorch-cross-attention`

O ComfyUI inicia um servidor web local. Abra o seu browser em `http://127.0.0.1:8188` para aceder à interface.

> **Dica**: Mantenha a janela do terminal aberta enquanto utiliza o ComfyUI. Se a fechar, o servidor será interrompido.
<!-- @os:end -->
<!-- @device:end -->


## Encontrar o Modelo Z-Image Turbo

Antes de gerar imagens, precisa de carregar o modelo Z-Image Turbo. Veja como o encontrar:

1. **Olhe para a extremidade esquerda do ecrã**—existe uma barra de ferramentas vertical que percorre a aplicação de cima a baixo, no lado mais à esquerda.

2. **Encontre o ícone de pasta**—nessa barra de ferramentas à esquerda, procure um ícone que se assemelha a uma pasta. Ao passar o rato sobre ele, verá a etiqueta "Templates".

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **Clique no ícone de pasta**—isto abre o painel de Templates.

4. **Procure por "Z-Image Turbo"**—utilize a barra de pesquisa ou percorra os modelos disponíveis para encontrar o fluxo de trabalho Z-Image Turbo Text To Image e, em seguida, clique para o carregar.

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z-Image Turbo template" width="600"/>
</p>

## Transferir Modelos

<!-- @require:comfyui-models -->

## Compreender a Interface

Quando o modelo Z-Image Turbo é carregado, verá uma tela com 2 nós principais. O primeiro nó chama-se "Text to Image (Z-Image-Turbo)" e o segundo nó serve para visualizar a imagem. 

<p align="center">
  <img src="assets/zimagenode.png" alt="ComfyUI Main Node" width="600"/>
</p>


No nó Z-Image, clique no botão no canto superior direito para expandir o nó e ver o subgrafo.

<p align="center">
  <img src="assets/subgraph_good.png" alt="ComfyUI Node Subgraph" width="600"/>
</p>

### Componentes do Pipeline

O fluxo de trabalho Z-Image Turbo utiliza quatro componentes de modelo essenciais que funcionam em conjunto:

| Componente | Função |
|-----------|------|
| **Codificador de Texto** (Qwen 3 4B) | Converte o seu prompt de texto em embeddings que o modelo de difusão compreende |
| **Modelo de Difusão** (Z-Image Turbo) | A rede neuronal central que remove iterativamente o ruído das representações latentes, transformando-as em imagens |
| **VAE** (Autoencoder Variacional) | Codifica imagens de/para o espaço latente (descodifica os latentes finais em píxeis) |
| **LoRA** (opcional) | Adaptadores leves que modificam o estilo ou o sujeito sem ser necessário treinar novamente o modelo base |

Cada nó no fluxo de trabalho corresponde a um destes componentes. Os dados fluem da esquerda para a direita: texto → embeddings → remoção de ruído guiada → latentes → imagem final.
## Gerar a Primeira Imagem

O modelo Z-Image Turbo já está carregado. Para gerar uma imagem:

1. **Introduza o seu prompt** no Nó Z-Image principal. Seja descritivo. Aqui está um exemplo:
   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```
2. **(Opcional)**: Confirme ou ajuste quaisquer outras definições específicas dentro do subgrafo.
3. **Clique no botão azul "Run Workflow"** no canto direito (ou prima `Ctrl+Enter`)
4. Observe os nós a destacarem-se à medida que cada passo é executado

A execução completa do workflow deve concluir-se em menos de 30 segundos. A imagem gerada aparece no nó **Save Image** e é guardada na pasta `output/`.

<!-- @os:windows -->
<!-- @test:id=comfyui-generate-zimage-windows timeout=1200 hidden=True -->
```powershell
$comfyRoot      = Join-Path $env:LOCALAPPDATA "Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI"
$py             = Join-Path $comfyRoot ".venv\Scripts\python.exe"
$mainPy         = Join-Path $comfyRoot "main.py"
$sharedPaths    = Join-Path $env:APPDATA "Comfy Desktop\shared_model_paths.yaml"

$proc = Start-Process -FilePath $py `
 -ArgumentList "`"$mainPy`" --listen 127.0.0.1 --port 8188 --extra-model-paths-config `"$sharedPaths`"" `
 -WorkingDirectory $comfyRoot `
 -NoNewWindow -PassThru

try {
 $ok = $false
 for ($i=0; $i -lt 60; $i++) {
   $resp = curl.exe -s --max-time 2 http://127.0.0.1:8188/
   if ($LASTEXITCODE -eq 0 -and $resp) { $ok = $true; break }
   Start-Sleep -Seconds 1
 }
 if (-not $ok) { throw "ComfyUI server not ready on http://127.0.0.1:8188/" }

 # run submit script from assets working dir (where image_z_image_turbo.json should exist)
 @'
import json, time, urllib.request, urllib.error, sys, os
wf_path = "image_z_image_turbo.json"
if not os.path.exists(wf_path):
 raise SystemExit(f"Missing workflow json in working dir: {os.getcwd()} -> {wf_path}")
with open(wf_path, "r", encoding="utf-8") as f:
 workflow = json.load(f)
data = json.dumps({"prompt": workflow}).encode("utf-8")
req = urllib.request.Request(
 "http://127.0.0.1:8188/prompt",
 data=data,
 headers={"Content-Type":"application/json"},
 method="POST",
)
try:
 with urllib.request.urlopen(req, timeout=60) as r:
   prompt_id = json.load(r)["prompt_id"]
except urllib.error.HTTPError as e:
 body = e.read().decode("utf-8", "replace")
 print("HTTPError", e.code, e.reason)
 print(body)
 sys.exit(1)
except Exception as e:
  print("Request failed:", repr(e))
  sys.exit(1)

for _ in range(600):
 with urllib.request.urlopen(f"http://127.0.0.1:8188/history/{prompt_id}", timeout=60) as r:
   hist = json.load(r)
 entry = hist.get(prompt_id, {})
 if entry.get("outputs"):
   print("OK, output image generated!")
   sys.exit(0)
 time.sleep(1)

print("No outputs after waiting.")
print("history status:", json.dumps(entry.get("status", {})))  # surfaces the ComfyUI node/execution error
sys.exit(1)
'@ | & $py -
 if ($LASTEXITCODE -ne 0) { throw "Workflow submit/generation failed" }

} finally {
 Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:linux --> 
<!-- @test:id=comfyui-generate-zimage-linux timeout=1200 hidden=True setup=activate-venv -->
```bash
set -euo pipefail
export LD_LIBRARY_PATH=/opt/rocm/lib:${LD_LIBRARY_PATH:-}
# start server
python ./ComfyUI/main.py --listen 127.0.0.1 --port 8188 >/tmp/comfyui.log 2>&1 &
PID=$!

cleanup() {
 kill -9 "$PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# wait ready
ok=0
for i in $(seq 1 60); do
 resp="$(curl -s --max-time 2 http://127.0.0.1:8188/ || true)"
 if [ -n "$resp" ]; then ok=1; break; fi
 sleep 1
done

if [ "$ok" -ne 1 ]; then
 echo "ComfyUI server not ready"
 tail -n 200 /tmp/comfyui.log || true
 exit 1
fi

# submit workflow json from assets folder (one level up from ComfyUI)
python - <<'PY'
import json, time, urllib.request, urllib.error, sys, os

wf_path = "image_z_image_turbo.json"
if not os.path.exists(wf_path):
 raise SystemExit(f"Missing workflow json in working dir: {os.getcwd()} -> {wf_path}")

with open(wf_path, "r", encoding="utf-8") as f:
 workflow = json.load(f)

data = json.dumps({"prompt": workflow}).encode("utf-8")
req = urllib.request.Request(
 "http://127.0.0.1:8188/prompt",
 data=data,
 headers={"Content-Type":"application/json"},
 method="POST",
)

try:
 with urllib.request.urlopen(req, timeout=60) as r:
   prompt_id = json.load(r)["prompt_id"]
except urllib.error.HTTPError as e:
 body = e.read().decode("utf-8", "replace")
 print("HTTPError", e.code, e.reason)
 print(body)
 sys.exit(1)

for _ in range(600):
 with urllib.request.urlopen(f"http://127.0.0.1:8188/history/{prompt_id}", timeout=60) as r:
   hist = json.load(r)
 entry = hist.get(prompt_id, {})
 if entry.get("outputs"):
   print("OK, output image generated!")
   sys.exit(0)
 time.sleep(1)

print("No outputs after waiting.")
print("history status:", json.dumps(entry.get("status", {})))  # surfaces the ComfyUI node/execution error
sys.exit(1)
PY
```
<!-- @test:end --> 
<!-- @os:end --> 


<!-- @os:windows -->
<!-- @test:id=comfyui-output-exists-windows timeout=60 hidden=True -->
```powershell
$outDir = Join-Path $env:LOCALAPPDATA "Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\output"

# ComfyUI saves into date-stamped subdirectories, so recurse to find PNGs
$files = Get-ChildItem -Path $outDir -Filter *.png -File -Recurse -ErrorAction SilentlyContinue
if (-not $files) {
 throw "No PNG files found under: $outDir"
}
$files | Sort-Object LastWriteTime -Descending | Select-Object -First 5 | ForEach-Object { $_.FullName }
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux --> 
<!-- @test:id=comfyui-output-exists-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
ls -1 ComfyUI/output/*.png >/dev/null 2>&1 || (echo "No PNG files found in ComfyUI/output" && exit 1)
ls -1t ComfyUI/output/*.png | head -n 5
```
<!-- @test:end --> 
<!-- @os:end -->


## Ajustar os Parâmetros de Geração

### Definições do KSampler

O nó KSampler controla o processo de difusão principal:

| Parâmetro | O Que Controla | Recomendado para o Z-Image Turbo |
|-----------|------------------|-------------------------------|
| **steps** | Número de iterações de remoção de ruído | 4–10 (os modelos turbo são destilados para menos passos) |
| **cfg** | Escala de orientação sem classificador — o grau de fidelidade ao prompt | 1.0–2.0 (os modelos turbo usam uma orientação muito baixa) |
| **sampler_name** | Algoritmo de remoção de ruído | `euler` e `res_multistep` funcionam bem para modelos turbo |
| **scheduler** | Curva do plano de ruído | `normal` ou `simple` |
| **seed** | Semente aleatória para reprodutibilidade | Defina valores fixos para iterar sobre uma composição |

### Tamanho da Imagem

Para ajustar as dimensões de saída, encontre o nó **Empty Latent Image** e modifique **width** e **height**. Mantenha as dimensões iguais ou inferiores a 1024 píxeis no lado mais longo para uma qualidade ótima.

### ModelSamplingAuraFlow

O nó **ModelSamplingAuraFlow** é um modificador de amostragem especializado que ajusta a forma como o processo de difusão trata o plano de ruído. Verá este nó ligado à saída do modelo no workflow do Z-Image Turbo.

| Parâmetro | O Que Controla | Valores Recomendados |
|-----------|------------------|-------------------|
| **shift** | Ajusta o momento do plano de ruído — valores mais elevados transferem mais refinamento de detalhe para passos posteriores | 1.0–4.0 (o valor predefinido é 3.0) |

Quando ajustar o **shift**:

- **Valores mais baixos (1.0–2.0)**: Convergência mais rápida, bom para composições simples
- **Valores mais elevados (3.0–4.0)**: Refinamento mais gradual, pode melhorar detalhes finos em cenas complexas

O método de amostragem AuraFlow foi especificamente concebido para modelos de correspondência de fluxo (flow-matching) como o Z-Image Turbo, garantindo uma distribuição de ruído adequada ao longo de todo o processo de geração.

## Trabalhar com Workflows

### Guardar Workflows

Clique no botão **Save** no menu para exportar o seu workflow como um ficheiro JSON. Isto captura:

- Todos os nós e os respetivos parâmetros
- Todas as ligações entre nós
- O texto do prompt atual

### Carregar Workflows

Arraste um ficheiro JSON de workflow para a tela, ou utilize **Load** no menu. O workflow do Z-Image Turbo que vê por predefinição é carregado a partir de um ficheiro de workflow guardado.

### Partilhar Workflows

Os workflows são autónomos — partilhe o ficheiro JSON com colegas e estes poderão reproduzir exatamente a sua configuração. Isto torna o ComfyUI excelente para experimentação colaborativa.

## Próximos Passos

- **Explorar nós LoRA**: Aplique adaptadores de estilo ou de sujeito sem necessidade de retreino
- **Adicionar prompts negativos**: Ligue um segundo nó CLIP Text Encode à entrada de condicionamento **negative** do KSampler para orientar o modelo a evitar características indesejadas, como desfoque, artefactos ou marcas de água
- **Construir workflows personalizados**: Encadeie múltiplas gerações, adicione upscaling ou crie variações de imagem
- **Explorar workflows da comunidade**: [ComfyUI Examples](https://github.com/comfyanonymous/ComfyUI_examples) tem muitos workflows prontos a utilizar

O ponto forte do ComfyUI é a experimentação: ligue os nós de formas diferentes, ajuste parâmetros e observe como cada alteração afeta o resultado. Esta exploração prática desenvolve a intuição sobre o funcionamento dos modelos de difusão.

Para mais informações, consulte a [Documentação do ComfyUI](https://docs.comfy.org/).