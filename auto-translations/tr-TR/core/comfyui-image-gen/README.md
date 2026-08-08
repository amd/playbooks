<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Makine çevirisi.** Bu sayfa İngilizce dilinden otomatik olarak çevrilmiştir ve bir kişi tarafından incelenmemiştir. Sayfa hatalar içerebilir ve belirli talimatlar, komutlar, indirmeler, ürün kullanılabilirliği veya diğer içerikler dile veya bölgeye göre farklılık gösterebilir. Herhangi bir tutarsızlık veya farklılık olması durumunda, playbook'un orijinal İngilizce sürümü geçerli ve bağlayıcı olacaktır.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Genel Bakış

ComfyUI, Stable Diffusion ve diğer difüzyon modelleri için düğüm tabanlı, güçlü bir arayüzdür. Basit istem kutularına sahip geleneksel metinden görüntüye arayüzlerin aksine, ComfyUI tüm görüntü oluşturma iş hattını görsel bir grafik olarak sunar ve metin kodlamadan gizli (latent) uzay manipülasyonuna, nihai kod çözmeye kadar her adım üzerinde ayrıntılı kontrol sağlar.

Bu eğitim, GPU'nuzda yüksek kaliteli yapay zeka görüntüleri oluşturmak için ComfyUI'yi Z Image Turbo modeliyle nasıl kullanacağınızı öğretir.

## Neler Öğreneceksiniz

- ComfyUI'nin nasıl başlatılacağı ve Z-Image Turbo şablonunun nasıl yükleneceği
- Difüzyon iş hattı bileşenlerini anlama
- Görüntü oluşturma ve oluşturma parametrelerini ayarlama
- İş akışlarını kaydetme ve paylaşma

## Bellek Yapılandırmasını Ayarlama

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Yazılım Güncellemelerini Kontrol Etme

<!-- @require:software-update -->
<!-- @device:end -->

## Yazılım Ön Koşullarını Yükleme

<!-- @os:windows -->
<!-- @require:driver,comfyui -->
<!-- @os:end -->

<!-- @os:linux -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Kullanıcınıza GPU cihazlarına erişim izni verin** (bunun etkili olması için oturumu kapatıp yeniden açın):

```bash
sudo usermod -aG render,video $LOGNAME
```

#### Sanal Ortam Oluşturma
Linux'ta, seçtiğiniz dizinde bir terminal açın ve bir venv oluşturmak için aşağıdaki komutu çalıştırın:

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


## ComfyUI'yi Başlatma

<!-- @device:halo_box -->
<!-- @os:windows -->
ComfyUI'yi Windows'ta başlatmak için Masaüstünüzde bulunan ComfyUI Masaüstü Başlatıcısına tıklayın. AMD ile yerel sürümü yüklemek için adımları izleyin.

<p align="center">
  <img src="assets/new_installer.png" alt="ComfyUI Desktop Launcher and Installer" width="600"/>
</p>

Ardından, uygulamanın üst ortasındaki ComfyUI düğmesine tıklayın. Bu, bir ayarlar sekmesi açacaktır. Storage sekmesini açın ve önceden yüklenmiş modellere erişmek için yolların aşağıdaki gibi ayarlandığından emin olun.

<p align="center">
  <img src="assets/models_storage.png" alt="ComfyUI Desktop Menu Storage Tab" width="600"/>
</p>


<!-- @os:end -->

<!-- @os:linux -->
AMD Ryzen™ AI Halo üzerinde, ComfyUI ek Python kurulumu gerektirmeyen önceden oluşturulmuş bir konteynerde çalışır.

ComfyUI'yi Linux'ta başlatmak için görev çubuğundaki ComfyUI kısayoluna tıklayın. Kendiliğinden bir tarayıcı penceresinde açılmalıdır.
>**İpucu**: ComfyUI ve modelleri `~/.local/share/ComfyUI/models` konumunda depolanır. İş akışlarını veya yeni modelleri manuel olarak buradan ekleyebilirsiniz.


<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
ComfyUI'yi Windows'ta başlatmak için Masaüstünüzdeki ComfyUI kısayoluna tıklamanız yeterlidir.
<!-- @os:end -->

<!-- @os:linux -->

ComfyUI'yi başlatmak için:

1. ComfyUI dizininde olduğunuzdan emin olun.
2. `python3 main.py --use-pytorch-cross-attention` komutunu çalıştırın

ComfyUI yerel bir web sunucusu başlatır. Arayüze erişmek için tarayıcınızı `http://127.0.0.1:8188` adresine açın.

> **İpucu**: ComfyUI'yi kullanırken terminal penceresini açık tutun. Kapatmanız sunucuyu durduracaktır.
<!-- @os:end -->
<!-- @device:end -->


## Z-Image Turbo Şablonunu Bulma

Görüntü oluşturmadan önce, Z-Image Turbo şablonunu yüklemeniz gerekir. İşte nasıl bulacağınız:

1. **Ekranın en sol kenarına bakın**—uygulamanın en solunda, üstten alta uzanan dikey bir araç çubuğu vardır.

2. **Klasör simgesini bulun**—o sol araç çubuğunda, klasöre benzeyen bir simge arayın. Üzerine geldiğinizde "Templates" olarak etiketlenmiştir.

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **Klasör simgesine tıklayın**—bu, Templates panelini açar.

4. **"Z-Image Turbo" için arama yapın**—Z-Image Turbo Text To Image iş akışını bulmak için arama çubuğunu kullanın veya mevcut şablonlar arasında gezinin, ardından yüklemek için tıklayın.

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z-Image Turbo template" width="600"/>
</p>

## Modelleri İndirme

<!-- @require:comfyui-models -->

## Arayüzü Anlama

Z-Image Turbo şablonu yüklendiğinde, 2 ana düğüme sahip bir tuval göreceksiniz. İlk düğüm 'Text to Image (Z-Image-Turbo)' olarak adlandırılır ve ikinci düğüm görüntüyü görüntülemek içindir.

<p align="center">
  <img src="assets/zimagenode.png" alt="ComfyUI Main Node" width="600"/>
</p>


Z-Image düğümünde, Düğümü genişletmek ve alt grafiği görmek için sağ üst düğmeye tıklayın.

<p align="center">
  <img src="assets/subgraph_good.png" alt="ComfyUI Node Subgraph" width="600"/>
</p>

### İş Hattı Bileşenleri

Z-Image Turbo iş akışı, birlikte çalışan dört temel model bileşeni kullanır:

| Bileşen | Rol |
|-----------|------|
| **Metin Kodlayıcı (Text Encoder)** (Qwen 3 4B) | Metin isteminizi, difüzyon modelinin anladığı gömme (embedding) vektörlerine dönüştürür |
| **Difüzyon Modeli** (Z-Image Turbo) | Gizli (latent) temsilleri yinelemeli olarak arındırarak görüntülere dönüştüren temel sinir ağı |
| **VAE** (Varyasyonel Otokodlayıcı) | Görüntüleri gizli uzaya/gizli uzaydan kodlar (nihai gizli değerleri piksellere çözer) |
| **LoRA** (isteğe bağlı) | Temel modeli yeniden eğitmeden stili veya konuyu değiştiren hafif adaptörler |

İş akışındaki her düğüm bu bileşenlerden birine karşılık gelir. Veri soldan sağa akar: metin → gömme vektörleri → yönlendirilmiş arındırma → gizli değerler → nihai görüntü.
## İlk Görüntünüzü Oluşturma

Z-Image Turbo modeli zaten yüklendi. Bir görüntü oluşturmak için:

1. **İsteminizi (prompt) girin** ana Z-Image Node içinde. Açıklayıcı olun. İşte bir örnek:
   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```
2. **(İsteğe bağlı)**: Subgraph içindeki diğer belirli ayarları onaylayın veya ince ayar yapın.
3. Sağ köşedeki **mavi "Run Workflow"** düğmesine tıklayın (veya `Ctrl+Enter` tuşlarına basın)
4. Her adım çalıştırıldıkça node'ların vurgulandığını izleyin

Tüm iş akışının çalışması 30 saniyeden kısa sürede tamamlanmalıdır. Oluşturulan görüntünüz **Save Image** node'unda görünür ve `output/` klasörüne kaydedilir.

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


## Oluşturma Parametrelerini Ayarlama

### KSampler Ayarları

KSampler node'u temel difüzyon sürecini kontrol eder:

| Parametre | Ne Kontrol Eder | Z-Image Turbo İçin Önerilen |
|-----------|------------------|-------------------------------|
| **steps** | Gürültü giderme (denoising) yinelemelerinin sayısı | 4–10 (turbo modeller daha az adım için distile edilmiştir) |
| **cfg** | Sınıflandırıcısız yönlendirme ölçeği (classifier-free guidance)—istemin ne kadar yakından takip edileceği | 1.0–2.0 (turbo modeller çok düşük yönlendirme kullanır) |
| **sampler_name** | Gürültü giderme algoritması | `euler` ve `res_multistep` turbo modeller için iyi çalışır |
| **scheduler** | Gürültü zamanlama eğrisi | `normal` veya `simple` |
| **seed** | Yeniden üretilebilirlik için rastgele tohum değeri | Bir kompozisyon üzerinde yineleme yapmak için sabit değerler ayarlayın |

### Görüntü Boyutu

Çıktı boyutlarını ayarlamak için **Empty Latent Image** node'unu bulun ve **width** ile **height** değerlerini değiştirin. En iyi kalite için boyutları en uzun kenarda 1024 piksel veya altında tutun.

### ModelSamplingAuraFlow

**ModelSamplingAuraFlow** node'u, difüzyon sürecinin gürültü zamanlamasını nasıl ele aldığını ayarlayan özel bir örnekleme değiştiricisidir. Z-Image Turbo iş akışında bu node'un model çıktısına bağlı olduğunu göreceksiniz.

| Parametre | Ne Kontrol Eder | Önerilen Değerler |
|-----------|------------------|-------------------|
| **shift** | Gürültü zamanlamasını ayarlar—daha yüksek değerler daha fazla detay iyileştirmesini sonraki adımlara iter | 1.0–4.0 (varsayılan 3.0'dır) |

**shift** ne zaman ayarlanmalı:

- **Düşük değerler (1.0–2.0)**: Daha hızlı yakınsama, basit kompozisyonlar için iyi
- **Yüksek değerler (3.0–4.0)**: Daha kademeli iyileştirme, karmaşık sahnelerde ince detayları geliştirebilir

AuraFlow örnekleme yöntemi, özellikle Z-Image Turbo gibi akış eşleştirmeli (flow-matching) modeller için tasarlanmıştır ve oluşturma süreci boyunca uygun gürültü dağılımını sağlar.

## İş Akışlarıyla Çalışma

### İş Akışlarını Kaydetme

İş akışınızı JSON dosyası olarak dışa aktarmak için menüdeki **Save** düğmesine tıklayın. Bu işlem şunları kaydeder:

- Tüm node'lar ve parametreleri
- Node'lar arasındaki tüm bağlantılar
- Geçerli istem metni

### İş Akışlarını Yükleme

Bir iş akışı JSON dosyasını tuvale (canvas) sürükleyin veya menüden **Load** seçeneğini kullanın. Varsayılan olarak gördüğünüz Z-Image Turbo iş akışı, kaydedilmiş bir iş akışı dosyasından yüklenir.

### İş Akışlarını Paylaşma

İş akışları kendi kendine yeterlidir—JSON dosyasını meslektaşlarınızla paylaşın, böylece tam olarak sizin kurulumunuzu yeniden oluşturabilirler. Bu, ComfyUI'yi işbirlikçi deneyler için mükemmel kılar.

## Sonraki Adımlar

- **LoRA node'larını keşfedin**: Yeniden eğitim yapmadan stil veya konu adaptörleri uygulayın
- **Negatif istemler ekleyin**: KSampler'ın **negative** koşullandırma girişine ikinci bir CLIP Text Encode node'u bağlayarak modeli bulanıklık, artefaktlar veya filigranlar gibi istenmeyen özelliklerden uzaklaştırın
- **Özel iş akışları oluşturun**: Birden fazla oluşturmayı zincirleyin, yükseltme (upscaling) ekleyin veya görüntü varyasyonları oluşturun
- **Topluluk iş akışlarına göz atın**: [ComfyUI Examples](https://github.com/comfyanonymous/ComfyUI_examples) kullanıma hazır birçok iş akışı içerir

ComfyUI'nin gücü deneyselliktir: node'ları farklı şekillerde bağlayın, parametreleri ayarlayın ve her değişikliğin çıktıyı nasıl etkilediğini gözlemleyin. Bu uygulamalı keşif, difüzyon modellerinin nasıl çalıştığına dair sezgi geliştirir.

Daha fazla bilgi için [ComfyUI Documentation](https://docs.comfy.org/) sayfasına göz atın.