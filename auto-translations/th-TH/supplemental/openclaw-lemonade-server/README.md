<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# เรียกใช้ OpenClaw โดยใช้ Lemonade Server เป็น backend

## ภาพรวม

[**OpenClaw**](https://openclaw.ai/) คือ AI agent อัตโนมัติที่สามารถเขียนและรันโค้ด จัดการไฟล์ และดำเนินงานที่มีหลายขั้นตอนซับซ้อนแทนคุณได้ ต่างจาก chat assistant ที่แค่ตอบคำถาม OpenClaw ดำเนินการจริงบนระบบของคุณ ซึ่งหมายความว่าต้องการ AI backend ที่รวดเร็วและมีความสามารถเพียงพอที่จะรองรับ agent loop ที่ต้องการประสิทธิภาพสูง

[**Lemonade Server**](https://lemonade-server.ai/) คือ backend นั้น เป็น local inference server แบบ open-source ที่รัน GenAI model โดยตรงบนฮาร์ดแวร์ของคุณ และเปิดให้ใช้งานผ่าน OpenAI API มาตรฐานอุตสาหกรรม

เมื่อใช้ร่วมกัน ทั้งสองจะก่อตัวเป็น AI agent stack แบบ local อย่างสมบูรณ์: Lemonade จัดการการ inference ของ model และ OpenClaw ให้ agent loop ที่แปลง output ของ model ให้กลายเป็นการกระทำจริง

> **ก่อนดำเนินการต่อ:** OpenClaw เป็น AI agent ที่มีความอัตโนมัติสูง การให้ AI agent ใดๆ เข้าถึงระบบของคุณอาจส่งผลให้เกิดผลลัพธ์ที่คาดเดาไม่ได้หรือไม่ตั้งใจ ดำเนินการต่อเฉพาะเมื่อคุณเข้าใจความเสี่ยงและพร้อมรับผิดชอบต่อซอฟต์แวร์อัตโนมัติที่กระทำการแทนคุณ

---

## สิ่งที่คุณจะได้เรียนรู้

เมื่อสิ้นสุด playbook นี้ คุณจะสามารถ:

- เรียนรู้เกี่ยวกับ **Lemonade Server**
- **ติดตั้ง OpenClaw** และ **ชี้ไปที่ Lemonade Server** ในฐานะ AI backend
- **เริ่ม OpenClaw gateway** และยืนยันว่า agent ของคุณพร้อมทำงาน
- **เชื่อมต่อช่องทางการสื่อสาร** (Discord หรือ Telegram) เพื่อให้คุณสามารถสนทนากับ agent จากอุปกรณ์ใดก็ได้

---

## การตั้งค่า Memory Configuration

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งซอฟต์แวร์ที่จำเป็น

<!-- @os:linux -->
- PC ที่รัน **Ubuntu 24.04+** หรือ Linux distribution ที่ใช้ Debian เป็นฐานและรองรับ `apt-get`
- RAM อย่างน้อย **12 GB** (แนะนำ 64 GB+ สำหรับ model ขนาดใหญ่)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (ไม่บังคับ สำหรับการ sandbox OpenClaw)

- **พื้นที่ดิสก์ว่างประมาณ 10–30 GB** สำหรับ model weights
<!-- @os:end -->
<!-- @os:windows -->
- PC ที่รัน **Windows 10/11**
- RAM อย่างน้อย **12 GB** (แนะนำ 64 GB+ สำหรับ model ขนาดใหญ่)
- **พื้นที่ดิสก์ว่างประมาณ 10–30 GB** สำหรับ model weights
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (ไม่บังคับ สำหรับการ sandbox OpenClaw)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## ดึงและโหลด Model ที่แนะนำ

model ที่แนะนำสำหรับ playbook นี้คือ **Qwen3.6-35B-A3B-GGUF** จาก Unsloth ซึ่งเป็น MoE model ที่แข็งแกร่งพร้อม context window ขนาด 263k token ที่เหมาะสมกับงาน agent เป็นอย่างดี model นี้ใช้ quantization แบบ UD-Q4_K_XL ดึงมาได้เลย:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

จากนั้นโหลดด้วย context window ขนาดใหญ่และบันทึกการตั้งค่านั้นสำหรับการรันครั้งต่อไป:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end -->

model มี context length เริ่มต้นที่ 262,144 token หากพบข้อผิดพลาด out-of-memory (OOM) ให้พิจารณาลด context window ลง อย่างไรก็ตาม เนื่องจาก Qwen3.6 ใช้ประโยชน์จาก extended context สำหรับงานที่ซับซ้อน เราแนะนำให้คงค่า context length ไว้ที่อย่างน้อย 128K token เพื่อรักษาความสามารถในการคิด

> **เคล็ดลับ: ปิดการคิดเพื่อให้ agent ตอบสนองเร็วขึ้น:** Qwen3.6-35B-A3B รันในโหมด thinking โดยค่าเริ่มต้น ซึ่งเพิ่ม latency ก่อนแต่ละการตอบสนอง สำหรับ agent loop ค่าใช้จ่ายนี้สะสมอย่างรวดเร็ว repository [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) มี config สำเร็จรูปที่ปิดการคิด หากต้องการใช้งาน ให้ดาวน์โหลดไฟล์และ import:
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
$entry = $parsed.data | Where-Object { $_.id -eq "${openclaw_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${openclaw_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${openclaw_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${openclaw_model} model is downloaded in Lemonade"

if ($entry.recipe_options.ctx_size -ne 262144) {
  throw "Model ${openclaw_model} is not saved with ctx_size=262144. Run: lemonade load ${openclaw_model} --ctx-size 262144 --save-options"
}
Write-Host "OK: ${openclaw_model} is saved with ctx_size=262144"

$body = @{
  model = "${openclaw_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "openclaw-lemonade-chat-body.json"
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
model_id = "${openclaw_model}"

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
  "model": "${openclaw_model}",
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

## ตั้งค่า WSL

เรารัน OpenClaw ภายใน WSL (แนะนำ) และเชื่อมต่อกับ Lemonade ที่รันแบบ native บน Windows วิธีนี้ให้สภาพแวดล้อม Linux shell สำหรับ OpenClaw ในขณะที่คง GPU acceleration ของ Lemonade ไว้ฝั่ง Windows

### ติดตั้ง WSL และ Ubuntu

เปิด PowerShell ในฐานะ Administrator และติดตั้ง WSL kernel:

```powershell
wsl --install --no-distribution
```

จากนั้นติดตั้ง Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### เปิดใช้งาน systemd ใน WSL

รันคำสั่งนี้ภายใน Ubuntu terminal:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

รีสตาร์ท WSL:

```powershell
wsl --shutdown
wsl
```

### เชื่อมต่อ Lemonade จาก Windows เข้าสู่ WSL

WSL2 รันในเครือข่ายเสมือน Lemonade บน Windows ผูกกับ `127.0.0.1` ซึ่ง WSL ไม่สามารถเข้าถึงได้โดยตรง Windows port proxy จะส่งต่อ traffic จาก WSL gateway IP ไปยัง Windows localhost

**ค้นหา WSL gateway IP ของคุณ** (รันภายใน WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**เพิ่ม port proxy** (รันใน PowerShell ในฐานะ Administrator โดยแทนที่ `<WSL-Gateway-IP>` ด้วย WSL gateway IP ของคุณ):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**เพิ่ม firewall rule** (ใน elevated PowerShell เดิม):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**ยืนยันจาก WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

หากคุณโหลด model Qwen3.6-35B-A3B-GGUF ในขั้นตอนก่อนหน้าแล้ว คุณควรเห็น JSON output แบบนี้:

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

> กฎ `netsh portproxy` จะคงอยู่หลังรีบูต แต่ WSL gateway IP อาจเปลี่ยนแปลงหลังจาก `wsl --shutdown` หาก Lemonade ไม่สามารถเข้าถึงได้จาก WSL หลังรีสตาร์ท ให้รับ gateway IP ที่อัปเดตแล้วและอัปเดต proxy ด้วย IP ใหม่นี้

<!-- @test:id=wsl-lemonade-bridge-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
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

## ติดตั้งและกำหนดค่า OpenClaw

### ติดตั้ง OpenClaw
<!-- @os:windows -->
> รันคำสั่งในส่วนนี้ภายใน **WSL terminal** ของคุณ
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

flag `--no-onboard` จะข้ามตัวช่วยการตั้งค่าแบบ interactive คุณจะกำหนดค่า model backend ด้วยตนเองในขั้นตอนถัดไป ซึ่งให้การควบคุมที่แม่นยำว่าจะใช้ model และ server ใด

เปิด terminal ใหม่และยืนยันการติดตั้ง:

```bash
openclaw --version
```

> **เคล็ดลับ:** หากเห็น `command not found` หลังการติดตั้ง ให้เพิ่ม global bin directory ของ npm เข้าไปใน PATH ของคุณ:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> เพื่อให้การตั้งค่านี้ถาวร ให้เพิ่มบรรทัดข้างต้นลงในไฟล์ `~/.bashrc` หรือ `~/.zshrc` ของคุณ

<!-- @os:linux -->
<!-- @test:id=openclaw-version-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-version-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-version-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw version check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->
### กำหนดค่า OpenClaw ให้ใช้งาน Lemonade

เรียกใช้การเริ่มต้นแบบไม่โต้ตอบของ OpenClaw
<!-- @os:linux -->
```bash
openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->
<!-- @os:windows -->
```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->

คำสั่งนี้จะเขียนการกำหนดค่าของ OpenClaw ไปยัง `~/.openclaw/openclaw.json`

> **การกำหนดขนาด context window ของ OpenClaw:** การบีบอัดของ OpenClaw จะทำงานเมื่อ `contextTokens > contextWindow − reserveTokens` ค่าเริ่มต้น `reserveTokensFloor` คือ 20,000 tokens ซึ่งเป็นค่าขั้นต่ำที่จะแทนที่ `reserveTokens` เมื่อต่ำกว่า ดังนั้น context ของโมเดลที่ต่ำกว่า ~37k จะทำให้เกิดการวนซ้ำการบีบอัดแบบไม่สิ้นสุด ตั้งค่า reserve ต่ำและปิดใช้งาน floor ในการกำหนดค่าของคุณครั้งเดียว แล้วจะมีผลกับทุกโมเดล โดยไม่ต้องปรับแต่งแยกตามโมเดล:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` คือ *ค่าขั้นต่ำ* (minimum guard) ไม่ใช่ตัว reserve เอง การตั้งค่าเฉพาะ floor ไม่มีผลใดๆ `reserveTokensFloor: 0` จะปิดใช้งาน guard เพื่อให้ `reserveTokens` ที่ต่ำกว่าถูกยอมรับ
>
> **เมื่อใดควรใช้การกำหนดค่านี้:** ใช้การกำหนดค่านี้หาก context window ที่ใช้งานได้จริงของโมเดลต่ำกว่า ~37k ไม่ว่าจะเป็นเพราะโมเดลมีขนาดเล็ก (เช่น 8k, 16k, 32k) หรือเพราะคุณตั้งใจจำกัดไว้ที่ค่าต่ำกว่า (เช่น โหลดโมเดล 128k แต่ตั้ง context เป็น 16k ใน Lemonade) หากไม่ทำ OpenClaw จะเข้าสู่การวนซ้ำการบีบอัดแบบไม่สิ้นสุดเมื่อเริ่มต้น
>
> **โมเดลที่มี context ขนาดใหญ่ที่ใช้ context เต็ม:** คุณสามารถข้ามส่วนนี้ได้ทั้งหมด ค่าเริ่มต้นทำงานได้ดี การบีบอัดจะเริ่มทำงานก่อนที่ window จะเต็มและโมเดลมีพื้นที่เพียงพอสำหรับการสร้างคำตอบที่ยาว หากคุณนำไปใช้ โปรดทราบว่า `reserveTokens: 4096` จะจำกัดความยาวของคำตอบไว้ที่ ~4k tokens ซึ่งอาจตัดการสร้างไฟล์ขนาดใหญ่หรือแผนงานที่มีรายละเอียดออก
>
> **ตำแหน่งที่ควรเพิ่ม:** วาง block `compaction` ไว้ภายใน `agents.defaults` ใน `openclaw.json` ของคุณ (โดยปกติอยู่ที่ `~/.openclaw/openclaw.json`):
>
> ```json
> {
>   "agents": {
>     "defaults": {
>       "workspace": "/home/<you>/.openclaw/workspace",
>       "model": {
>         "primary": "lemonade/<your-model-id>"
>       },
>       "compaction": {
>         "reserveTokens": 4096,
>         "reserveTokensFloor": 0
>       }
>     }
>   }
> }
> ```
>
> ส่วนที่เหลือของการกำหนดค่า (gateway, channels, models ฯลฯ) ยังคงไม่เปลี่ยนแปลง เพียงแค่ต้องเพิ่ม key `compaction` เท่านั้น

### (แนะนำ) เปิดใช้งาน Docker Sandboxing

OpenClaw สามารถส่งต่อการดำเนินการไฟล์และโค้ดทั้งหมดของ agent ผ่าน Docker container ที่แยกออกมา แทนที่จะรันโดยตรงบนเครื่องของคุณ ซึ่งจะจำกัดผลกระทบจากการกระทำที่ไม่ตั้งใจให้อยู่ภายใน sandbox โดยไม่กระทบต่อ filesystem และเครือข่ายของเครื่องหลัก

สร้าง sandbox image ครั้งเดียว (ต้องติดตั้ง Docker ก่อน):

```bash
docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
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

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-image-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
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

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-image-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
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

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-sandbox-image-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox image build failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

รันคำสั่งนี้เพื่อเพิ่ม key `sandbox` ภายใน block `agents.defaults` ที่มีอยู่แล้วใน `~/.openclaw/openclaw.json`:

```bash
cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5
openclaw config patch --file ./sandbox.patch.json5
```

Sandbox containers จะ**ไม่มีการเข้าถึงเครือข่าย**โดยค่าเริ่มต้น ดูที่ [เอกสารอ้างอิง sandboxing](https://docs.openclaw.ai/gateway/sandboxing) สำหรับ bind mounts และการแทนที่การตั้งค่าเครือข่าย

> #### การแก้ไขปัญหา: Docker Permission Denied
> 
> หากคุณได้รับข้อความ "permission denied" เมื่อรันคำสั่ง Docker:
> 
> **ขั้นตอนที่ 1: เพิ่มผู้ใช้ของคุณเข้าในกลุ่ม docker**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **ขั้นตอนที่ 2: หากข้อผิดพลาดยังคงอยู่ ให้ใช้การแก้ไขถาวร**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> จากนั้น**รีบูต**ระบบของคุณ
> 
> **การแก้ไขชั่วคราวอย่างรวดเร็ว** (จะรีเซ็ตหลังรีบูต):
> ```bash
> sudo chmod 666 /var/run/docker.sock
> ```

<!-- @os:linux -->
<!-- @test:id=openclaw-onboard-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "127.0.0.1:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written"
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-onboard-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "$WINDOWS_HOST:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-onboard-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw onboarding failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written inside WSL"
'@

$script = $script -replace "`r`n", "`n"
$tmp = Join-Path $env:TEMP "openclaw-sandbox-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox config patch failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

### เริ่มต้น OpenClaw Gateway

gateway คือกระบวนการของ OpenClaw ที่จัดการ agent loop และให้บริการ dashboard:

```bash
openclaw gateway run --bind loopback --port 18789
```

<!-- @os:linux -->
<!-- @test:id=openclaw-gateway-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-gateway-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-gateway-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw gateway test failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

หากต้องการเปิด dashboard ให้รันคำสั่งนี้ในเทอร์มินัลที่สองในขณะที่ gateway ยังคงทำงานอยู่:

```bash
openclaw dashboard
```

เนื่องจาก gateway ผูกกับ loopback dashboard จะยืนยันตัวตนโดยอัตโนมัติเมื่อเปิดจากเครื่องเดียวกัน โดยไม่ต้องกรอก token หรืออนุมัติอุปกรณ์สำหรับการเข้าถึงในเครื่อง คุณควรเห็น dashboard ของ OpenClaw พร้อมโมเดล Lemonade ของคุณที่แสดงเป็น backend ที่ใช้งานอยู่

> หากคุณเปิดใช้งาน sandboxing คุณสามารถตรวจสอบได้โดยขอให้ agent `run hostname` จาก dashboard หากคุณเห็น container ID สั้นๆ แทนที่จะเป็น hostname ของเครื่องคุณ แสดงว่า sandbox ทำงานอยู่

**ขอแสดงความยินดี คุณได้สร้าง AI agent stack แบบ local ทั้งหมดตั้งแต่ต้นแล้ว**

> **ต้องการ gateway token หรือไม่?** รัน `openclaw dashboard --no-open` เพื่อพิมพ์ URL ของ dashboard พร้อม token ที่ฝังอยู่ (และยังพยายามคัดลอกไปยัง clipboard ของคุณด้วย) หรืออีกทางหนึ่ง token อยู่ที่ `gateway.auth.token` ใน `~/.openclaw/openclaw.json`
>
> **การอนุมัติอุปกรณ์ระยะไกล:** เมื่อคุณเปิด dashboard จากเครื่องที่สองหรือโทรศัพท์ เบราว์เซอร์จะแสดง request ID กลับไปที่เครื่องที่รัน gateway แล้วรัน:
> ```bash
> openclaw devices approve <requestId>
> ```
> ขั้นตอนนี้จำเป็นเฉพาะสำหรับอุปกรณ์ระยะไกลหรืออุปกรณ์รอง การเข้าถึงผ่าน loopback จากเครื่องเดียวกันจะยืนยันตัวตนโดยอัตโนมัติ

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## ตัวเลือกเสริม: เชื่อมต่อช่องทางการสื่อสาร

เมื่อ gateway ทำงานแล้ว คุณสามารถเข้าถึง agent ในเครื่องของคุณได้จากอุปกรณ์ใดก็ได้ เลือกตัวเลือกที่เหมาะกับการตั้งค่าของคุณ OpenClaw รองรับ [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) และช่องทางอื่นๆ ดูรายการทั้งหมดได้ที่ [docs.openclaw.ai](https://docs.openclaw.ai)

---

### ตัวเลือก A: Discord

Discord ต้องการเซิร์ฟเวอร์ที่**คุณมีสิทธิ์ผู้ดูแลระบบ**เพื่อเพิ่ม bot หากคุณใช้เซิร์ฟเวอร์ร่วมกับผู้อื่นแต่ไม่ได้เป็นเจ้าของ ให้ใช้ตัวเลือก B (Telegram) แทน
#### สร้างบัญชีและเซิร์ฟเวอร์ Discord

หากคุณยังไม่มีบัญชี Discord ให้สมัครได้ที่ [discord.com](https://discord.com) คุณยังต้องมีเซิร์ฟเวอร์ที่คุณเป็นผู้ดูแลระบบ สร้างได้โดยคลิกไอคอน **+** ในแถบด้านข้างของ Discord แล้วเลือก **Create My Own** เซิร์ฟเวอร์ส่วนตัวก็ใช้ได้

#### สร้างแอปพลิเคชันและบอท Discord

1. ไปที่ [Discord Developer Portal](https://discord.com/developers/applications) แล้วคลิก **New Application** ตั้งชื่อให้กับมัน (เช่น "openclaw-bot")
2. ในแถบด้านข้าง คลิก **Bot** แล้วตั้งชื่อผู้ใช้สำหรับบอท
3. ยังอยู่ในหน้า Bot เลื่อนไปที่ **Privileged Gateway Intents** แล้วเปิดใช้งาน:
   - **Message Content Intent** (จำเป็น)
   - **Server Members Intent** (แนะนำ)
4. เลื่อนกลับขึ้นไปด้านบนแล้วคลิก **Reset Token** เพื่อสร้างโทเค็นบอทของคุณ คัดลอกไว้

#### เพิ่มบอทเข้าสู่เซิร์ฟเวอร์ของคุณ

1. ในแถบด้านข้าง คลิก **OAuth2/ URL Generator**
2. ใต้ **Scopes** เปิดใช้งาน `bot` และ `applications.commands`
3. ใต้ **Bot Permissions** เปิดใช้งาน: View Channels, Send Messages, Read Message History, Embed Links, Attach Files
4. คัดลอก URL ที่สร้างขึ้น วางในเบราว์เซอร์ของคุณ เลือกเซิร์ฟเวอร์ของคุณ แล้วยืนยัน บอทควรปรากฏในรายชื่อสมาชิกของเซิร์ฟเวอร์คุณแล้ว

#### รวบรวม ID ของคุณ

เปิดใช้งาน Developer Mode ใน Discord (**User Settings/ Advanced/ Developer Mode**) จากนั้น:
- คลิกขวาที่ไอคอนเซิร์ฟเวอร์ของคุณ: **Copy Server ID**
- คลิกขวาที่อวาตาร์ของคุณเอง: **Copy User ID**

#### อนุญาตให้รับ DM จากสมาชิกเซิร์ฟเวอร์

คลิกขวาที่ไอคอนเซิร์ฟเวอร์ของคุณ/ **Privacy Settings**/ สลับเปิด **Direct Messages** ซึ่งจะอนุญาตให้บอทส่ง DM ถึงคุณ ซึ่งจำเป็นสำหรับขั้นตอนการจับคู่

#### กำหนดค่า OpenClaw สำหรับ Discord

จัดเก็บโทเค็นบอทของคุณเป็นตัวแปรสภาพแวดล้อม จากนั้นสร้างไฟล์แพตช์เดียวที่เปิดใช้งาน Discord อ้างอิงโทเค็น และอนุญาตเซิร์ฟเวอร์ของคุณ แทนที่ `<server_id>` และ `<user_id>` ด้วย ID ที่รวบรวมไว้ข้างต้น

```bash
export DISCORD_BOT_TOKEN="YOUR_BOT_TOKEN"

cat > discord.patch.json5 <<JSON5
{
  channels: {
    discord: {
      enabled: true,
      token: { source: "env", provider: "default", id: "DISCORD_BOT_TOKEN" },
      dmPolicy: "pairing",
      groupPolicy: "allowlist",
      guilds: {
        "<server_id>": {
          requireMention: false,
          users: ["<user_id>"],
        },
      },
    },
  },
}
JSON5
openclaw config patch --file ./discord.patch.json5
```

> **อย่าพึ่งพาการขอให้เอเจนต์กำหนดค่านี้** เมื่อเปิดใช้งาน sandboxing เอเจนต์ไม่สามารถเขียนไปยัง `~/.openclaw/openclaw.json` จากภายใน sandbox ได้ ให้ใช้คำสั่ง CLI ข้างต้นบนโฮสต์แทน

รีสตาร์ทเกตเวย์เพื่อให้รับการกำหนดค่าช่องทางใหม่:

```bash
openclaw gateway run --bind loopback --port 18789
```

คุณควรเห็น `logged in to discord as <bot-name>` ในเอาต์พุตของเกตเวย์ภายในไม่กี่วินาที

#### จับคู่บัญชี Discord ของคุณ

ส่ง DM ถึงบอทใน Discord มันจะตอบกลับด้วยรหัสการจับคู่สั้นๆ

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

อนุมัติบนเครื่องที่รัน OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> รหัสการจับคู่จะหมดอายุหลังจากหนึ่งชั่วโมง

ตอนนี้คุณสามารถสนทนากับเอเจนต์ของคุณโดยตรงจาก Discord และมอบหมายงานให้กับฮาร์ดแวร์ในเครื่องของคุณได้แล้ว

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### ตัวเลือก B: Telegram

Telegram นั้นง่ายกว่า Discord สำหรับผู้ใช้ส่วนใหญ่ ไม่ต้องใช้เซิร์ฟเวอร์และไม่ต้องมีสิทธิ์ผู้ดูแลระบบ

#### สร้างบอท Telegram

1. เปิด Telegram แล้วส่งข้อความถึง **@BotFather**
2. ส่ง `/newbot` แล้วทำตามคำแนะนำ บันทึกโทเค็นบอทที่ได้รับ

#### กำหนดค่า OpenClaw สำหรับ Telegram

จัดเก็บโทเค็นเป็นตัวแปรสภาพแวดล้อม:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

เพิ่มการกำหนดค่าช่องทางไปยัง `~/.openclaw/openclaw.json` (หรือแพตช์ผ่านแดชบอร์ด):

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "YOUR_BOT_TOKEN",
      "dmPolicy": "pairing"
    }
  }
}
```

รีสตาร์ทเกตเวย์ จากนั้นส่งข้อความใดก็ได้ถึงบอทของคุณใน Telegram อนุมัติการจับคู่:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

รหัสการจับคู่จะหมดอายุหลังจากหนึ่งชั่วโมง ตอนนี้คุณสามารถสนทนากับเอเจนต์ของคุณผ่าน Telegram DM ได้แล้ว

---

## ขั้นตอนถัดไป

ตอนนี้ที่เอเจนต์ของคุณสามารถรับคำสั่งจากโทรศัพท์และดำเนินการบนเครื่องในเครื่องของคุณได้แล้ว ต่อไปนี้คือสามทิศทางที่ควรค่าแก่การสำรวจ:

1. **ตัวสรุปตลาดหุ้น**: กำหนดเวลาให้ OpenClaw ดึงข้อมูลจาก API ทางการเงินในช่วงเวลาที่กำหนด สรุปความเคลื่อนไหวของวันด้วยโมเดลในเครื่องของคุณ และส่งสรุปไปยังโทรศัพท์ของคุณทุกเช้าผ่านช่องทางที่คุณเลือก

2. **ตัวตรวจสอบการ Fine-tuning**: เริ่มงานการฝึกอบรมจากระยะไกลผ่าน Telegram หรือ Discord จากนั้นให้เอเจนต์ติดตามล็อกการฝึกอบรมและรายงานค่า loss เป็นระยะ การใช้งาน GPU และการใช้งานดิสก์กลับมายังโทรศัพท์ของคุณ หากการรันหยุดชะงักหรือ VRAM พุ่งสูง คุณจะทราบทันทีโดยไม่ต้องอยู่ที่เครื่อง

3. **IOT ด้วย VLM ในเครื่อง**: ชี้กล้องไปที่ประตูหน้าบ้านของคุณ รันโมเดล vision บน Lemonade และให้ OpenClaw วิเคราะห์เฟรมตามต้องการหรือตามทริกเกอร์ ถามว่า "มีพัสดุมาส่งวันนี้ไหม?" จากโทรศัพท์ของคุณและรับคำตอบตรงๆ จากฮาร์ดแวร์ของคุณเอง