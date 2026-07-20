<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# เรียกใช้งาน OpenClaw โดยใช้ Lemonade Server เป็นแบ็กเอนด์

## ภาพรวม

[**OpenClaw**](https://openclaw.ai/) เป็นเอเจนต์ AI ที่ทำงานได้ด้วยตนเอง สามารถเขียนและรันโค้ด จัดการไฟล์ และดำเนินงานที่มีหลายขั้นตอนซับซ้อนแทนคุณได้ ต่างจากผู้ช่วยแชทที่เพียงตอบคำถาม OpenClaw จะลงมือปฏิบัติจริงบนระบบของคุณ ซึ่งหมายความว่ามันต้องการแบ็กเอนด์ AI ที่รวดเร็วและมีความสามารถเพียงพอที่จะตามทันวงรอบการทำงานของเอเจนต์ที่ต้องการความเข้มข้นสูง

[**Lemonade Server**](https://lemonade-server.ai/) คือแบ็กเอนด์นั้น มันคือเซิร์ฟเวอร์อนุมาน (inference) แบบโลคัลที่เป็นโอเพนซอร์ส ซึ่งรันโมเดล GenAI โดยตรงบนฮาร์ดแวร์ของคุณ และเปิดให้ใช้งานผ่าน OpenAI API ซึ่งเป็นมาตรฐานอุตสาหกรรม

เมื่อนำมาใช้ร่วมกัน ทั้งสองจะประกอบกันเป็นสแต็ก AI เอเจนต์แบบโลคัลอย่างสมบูรณ์: Lemonade จัดการการอนุมานโมเดล ส่วน OpenClaw จัดเตรียมวงรอบของเอเจนต์ที่แปลงผลลัพธ์จากโมเดลให้กลายเป็นการกระทำจริง

> **ก่อนที่คุณจะดำเนินการต่อ:** OpenClaw เป็นเอเจนต์ AI ที่มีความเป็นอิสระสูง การให้เอเจนต์ AI ใด ๆ เข้าถึงระบบของคุณอาจส่งผลให้เกิดผลลัพธ์ที่คาดเดาไม่ได้หรือไม่พึงประสงค์ โปรดดำเนินการต่อก็ต่อเมื่อคุณเข้าใจความเสี่ยงและยอมรับได้ที่จะให้ซอฟต์แวร์ที่ทำงานอย่างอิสระกระทำการแทนคุณ

---

## สิ่งที่คุณจะได้เรียนรู้

เมื่อจบคู่มือนี้ คุณจะสามารถ:

- เรียนรู้เกี่ยวกับ **Lemonade Server**
- **ติดตั้ง OpenClaw** และ **ตั้งค่าให้ชี้ไปที่ Lemonade Server** เป็นแบ็กเอนด์ AI
- **เริ่มการทำงานของ OpenClaw gateway** และยืนยันว่าเอเจนต์ของคุณพร้อมทำงาน
- **เชื่อมต่อช่องทางการสื่อสาร** (Discord หรือ Telegram) เพื่อให้คุณสามารถแชทกับเอเจนต์ของคุณได้จากอุปกรณ์ใดก็ตาม

---

## การตั้งค่าหน่วยความจำ (Memory Configuration)

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งซอฟต์แวร์ที่จำเป็นล่วงหน้า

<!-- @os:linux -->
- เครื่อง PC ที่รัน **Ubuntu 24.04+** หรือดิสโทร Linux ที่ใช้ Debian เป็นฐานและเข้ากันได้ พร้อมกับ `apt-get`
- แรม (RAM) อย่างน้อย **12 GB** (แนะนำ 64 GB ขึ้นไปสำหรับโมเดลขนาดใหญ่)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (ทางเลือกเสริม สำหรับการแซนด์บ็อกซ์ OpenClaw)

- **พื้นที่ดิสก์ว่างประมาณ 10–30 GB** สำหรับน้ำหนักโมเดล
<!-- @os:end -->
<!-- @os:windows -->
- เครื่อง PC ที่รัน **Windows 10/11**
- แรม (RAM) อย่างน้อย **12 GB** (แนะนำ 64 GB ขึ้นไปสำหรับโมเดลขนาดใหญ่)
- **พื้นที่ดิสก์ว่างประมาณ 10–30 GB** สำหรับน้ำหนักโมเดล
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (ทางเลือกเสริม สำหรับการแซนด์บ็อกซ์ OpenClaw)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## ดึงและโหลดโมเดลที่แนะนำ

โมเดลที่แนะนำสำหรับคู่มือนี้คือ **Qwen3.6-35B-A3B-GGUF** จาก Unsloth ซึ่งเป็นโมเดล MoE ที่มีประสิทธิภาพสูง มีหน้าต่างบริบท (context window) ขนาด 263,000 โทเคน ซึ่งเหมาะสมอย่างยิ่งกับงานประเภทเอเจนต์ โมเดลนี้ใช้การควอนไทซ์แบบ UD-Q4_K_XL ดึงโมเดลนี้ได้เลยตอนนี้:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

จากนั้นโหลดโมเดลด้วยหน้าต่างบริบทขนาดใหญ่ และบันทึกการตั้งค่านี้ไว้สำหรับการใช้งานในครั้งต่อไป:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

โมเดลนี้มีความยาวบริบทเริ่มต้นที่ 262,144 โทเคน หากคุณพบข้อผิดพลาดหน่วยความจำไม่เพียงพอ (OOM) ให้ลองพิจารณาลดขนาดหน้าต่างบริบทลง อย่างไรก็ตาม เนื่องจาก Qwen3.6 ใช้ประโยชน์จากบริบทที่ขยายออกไปสำหรับงานที่ซับซ้อน เราจึงแนะนำให้คงความยาวบริบทไว้อย่างน้อย 128K โทเคน เพื่อรักษาความสามารถในการคิดวิเคราะห์ไว้

> **เคล็ดลับ: ปิดโหมดคิดวิเคราะห์เพื่อให้เอเจนต์ตอบสนองได้เร็วขึ้น:** Qwen3.6-35B-A3B จะรันในโหมดคิดวิเคราะห์ (thinking mode) เป็นค่าเริ่มต้น ซึ่งเพิ่มความหน่วง (latency) ก่อนแต่ละการตอบสนอง สำหรับวงรอบของเอเจนต์แล้ว ค่าใช้จ่ายส่วนนี้จะสะสมขึ้นอย่างรวดเร็ว รีโพซิทอรี [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) มีไฟล์การตั้งค่าสำเร็จรูปที่ปิดโหมดคิดวิเคราะห์ไว้ให้แล้ว ในการใช้งาน ให้ดาวน์โหลดไฟล์และนำเข้า:
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

เราจะรัน OpenClaw ภายใน WSL (แนะนำ) และเชื่อมต่อกับ Lemonade ที่รันโดยตรงบน Windows วิธีนี้ทำให้คุณได้สภาพแวดล้อมเชลล์แบบ Linux สำหรับ OpenClaw ในขณะที่ยังคงให้ Lemonade เร่งความเร็วด้วย GPU อยู่ฝั่ง Windows

### ติดตั้ง WSL และ Ubuntu

เปิด PowerShell ในโหมดผู้ดูแลระบบ (Administrator) และติดตั้งเคอร์เนล WSL:

```powershell
wsl --install --no-distribution
```

จากนั้นติดตั้ง Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### เปิดใช้งาน systemd ใน WSL

รันคำสั่งนี้ภายในเทอร์มินัลของ Ubuntu:

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

WSL2 ทำงานอยู่ในเครือข่ายเสมือน Lemonade บน Windows จะผูก (bind) กับ `127.0.0.1` ซึ่ง WSL ไม่สามารถเข้าถึงได้โดยตรง การใช้ Windows port proxy จะช่วยส่งต่อทราฟฟิกจาก IP เกตเวย์ของ WSL ไปยัง localhost ของ Windows

**ค้นหา IP เกตเวย์ของ WSL** (รันภายใน WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**เพิ่ม port proxy** (รันใน PowerShell ในโหมดผู้ดูแลระบบ โดยแทนที่ `<WSL-Gateway-IP>` ด้วย IP เกตเวย์ของ WSL ของคุณ):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**เพิ่มกฎไฟร์วอลล์** (ใช้ PowerShell แบบยกระดับสิทธิ์เดิม):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**ตรวจสอบยืนยันจาก WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

หากคุณได้โหลดโมเดล Qwen3.6-35B-A3B-GGUF ไว้แล้วในขั้นตอนก่อนหน้านี้ คุณควรจะเห็นผลลัพธ์ JSON แบบนี้:

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

> กฎ `netsh portproxy` จะยังคงอยู่หลังรีบูตเครื่อง แต่ IP เกตเวย์ของ WSL อาจเปลี่ยนแปลงได้หลังจากรัน `wsl --shutdown` หาก Lemonade ไม่สามารถเข้าถึงได้จาก WSL หลังรีสตาร์ท ให้ดึง IP เกตเวย์ที่อัปเดตแล้วมาและอัปเดต proxy ด้วย IP ใหม่นี้

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
> รันคำสั่งในส่วนนี้ภายใน **เทอร์มินัล WSL** ของคุณ
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

แฟล็ก `--no-onboard` จะข้ามตัวช่วยตั้งค่าแบบโต้ตอบ (interactive setup wizard) คุณจะกำหนดค่าแบ็กเอนด์ของโมเดลด้วยตนเองในขั้นตอนถัดไป ซึ่งจะทำให้คุณสามารถควบคุมได้อย่างแม่นยำว่าจะใช้โมเดลและเซิร์ฟเวอร์ใด

เปิดเทอร์มินัลใหม่และยืนยันการติดตั้ง:

```bash
openclaw --version
```

> **เคล็ดลับ:** หากคุณพบข้อความ `command not found` หลังการติดตั้ง ให้เพิ่มไดเรกทอรี bin แบบ global ของ npm ลงใน PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> เพื่อให้การตั้งค่านี้มีผลถาวร ให้เพิ่มบรรทัดข้างต้นลงในไฟล์ `~/.bashrc` หรือ `~/.zshrc` ของคุณ

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
### กำหนดค่า OpenClaw ให้ใช้ Lemonade

รันการตั้งค่าเริ่มต้นแบบ non-interactive ของ OpenClaw
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

คำสั่งนี้จะเขียนไฟล์การกำหนดค่าของ OpenClaw ไปยัง `~/.openclaw/openclaw.json`

> **การกำหนดขนาดหน้าต่างบริบทของ OpenClaw:** การบีบอัด (compaction) ของ OpenClaw จะเริ่มทำงานเมื่อ `contextTokens > contextWindow − reserveTokens` ค่าเริ่มต้นของ `reserveTokensFloor` คือ 20,000 โทเคน ซึ่งเป็นค่าขั้นต่ำ (floor) ที่จะแทนที่ `reserveTokens` เมื่อค่านั้นต่ำกว่า ดังนั้นหน้าต่างบริบทของโมเดลใดๆ ที่ต่ำกว่าประมาณ 37k จะทำให้เกิดลูปการบีบอัดแบบไม่รู้จบ ให้ตั้งค่า reserve ให้ต่ำและปิดใช้งาน floor เพียงครั้งเดียวในไฟล์กำหนดค่าของคุณ แล้วมันจะมีผลกับทุกโมเดล ไม่ต้องปรับแต่งเป็นรายโมเดล:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` คือค่า *ขั้นต่ำ* (การ์ดป้องกัน) ไม่ใช่ตัว reserve เอง การตั้งค่าเฉพาะ floor เพียงอย่างเดียวจะไม่มีผลใดๆ การตั้ง `reserveTokensFloor: 0` จะปิดใช้งานการ์ดป้องกันนี้ เพื่อให้ค่า `reserveTokens` ที่ต่ำกว่าถูกยอมรับ
>
> **เมื่อไรควรใช้การตั้งค่านี้:** ใช้การกำหนดค่านี้หากหน้าต่างบริบทที่ใช้งานได้จริงของโมเดลของคุณต่ำกว่าประมาณ 37k ไม่ว่าจะเป็นเพราะโมเดลมีขนาดเล็ก (เช่น 8k, 16k, 32k) หรือเพราะคุณตั้งใจจำกัดค่าให้ต่ำลง (เช่น โหลดโมเดล 128k แต่ตั้งค่าบริบทเป็น 16k ใน Lemonade) หากไม่ทำเช่นนี้ OpenClaw จะเข้าสู่ลูปการบีบอัดแบบไม่รู้จบเมื่อเริ่มทำงาน
>
> **โมเดลที่มีบริบทขนาดใหญ่ที่ใช้บริบทเต็ม:** คุณสามารถข้ามขั้นตอนนี้ไปได้เลย ค่าเริ่มต้นทำงานได้ดีอยู่แล้ว การบีบอัดจะเริ่มทำงานก่อนที่หน้าต่างจะเต็มมาก และโมเดลก็มีพื้นที่เพียงพอสำหรับสร้างคำตอบยาวๆ หากคุณยังต้องการใช้การตั้งค่านี้ โปรดทราบว่า `reserveTokens: 4096` จะจำกัดความยาวของคำตอบไว้ที่ประมาณ 4k โทเคน ซึ่งอาจตัดการสร้างไฟล์ยาวๆ หรือแผนงานที่มีรายละเอียดมากออกไป
>
> **ตำแหน่งที่ควรเพิ่มการตั้งค่านี้:** วางบล็อก `compaction` ไว้ภายใน `agents.defaults` ในไฟล์ `openclaw.json` ของคุณ (โดยปกติจะอยู่ที่ `~/.openclaw/openclaw.json`):
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
> ส่วนที่เหลือของการกำหนดค่าของคุณ (gateway, channels, models เป็นต้น) จะยังคงเหมือนเดิม เพียงแค่ต้องเพิ่มคีย์ `compaction` เข้าไปเท่านั้น

### (แนะนำ) เปิดใช้งาน Docker Sandboxing

OpenClaw สามารถส่งการทำงานเกี่ยวกับไฟล์และโค้ดของ agent ทั้งหมดผ่านคอนเทนเนอร์ Docker ที่แยกออกมาต่างหาก แทนที่จะรันโดยตรงบนเครื่องโฮสต์ของคุณ วิธีนี้จะจำกัดผลกระทบของการกระทำที่ไม่ตั้งใจใดๆ ให้อยู่แค่ภายใน sandbox โดยไม่กระทบต่อระบบไฟล์และเครือข่ายของเครื่องโฮสต์

สร้างอิมเมจสำหรับ sandbox เพียงครั้งเดียว (ต้องติดตั้ง Docker ไว้ก่อน):

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

รันคำสั่งนี้เพื่อเพิ่มคีย์ `sandbox` ไว้ภายในบล็อก `agents.defaults` ที่มีอยู่แล้วในไฟล์ `~/.openclaw/openclaw.json`:

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

คอนเทนเนอร์ sandbox จะ**ไม่มีการเข้าถึงเครือข่าย**โดยค่าเริ่มต้น ดูรายละเอียดเพิ่มเติมเกี่ยวกับการเชื่อมต่อ bind mount และการปรับแต่งเครือข่ายได้ที่ [เอกสารอ้างอิงเรื่อง sandboxing](https://docs.openclaw.ai/gateway/sandboxing)

> #### การแก้ไขปัญหา: Docker Permission Denied
> 
> หากคุณพบข้อความ "permission denied" เมื่อรันคำสั่ง Docker:
> 
> **ขั้นตอนที่ 1: เพิ่มผู้ใช้ของคุณเข้าไปในกลุ่ม docker**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **ขั้นตอนที่ 2: หากข้อผิดพลาดยังคงอยู่ ให้ใช้วิธีแก้ไขแบบถาวร**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> จากนั้น**รีบูต**ระบบของคุณ
> 
> **วิธีแก้ไขชั่วคราวแบบด่วน** (จะรีเซ็ตหลังรีบูต):
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

### เริ่มการทำงานของ OpenClaw Gateway

Gateway คือโปรเซสของ OpenClaw ที่จัดการลูปการทำงานของ agent และให้บริการแดชบอร์ด:

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

หากต้องการเปิดแดชบอร์ด ให้รันคำสั่งนี้ในเทอร์มินัลที่สองในขณะที่ gateway ยังทำงานอยู่:

```bash
openclaw dashboard
```

เนื่องจาก gateway ผูกกับ loopback แดชบอร์ดจะยืนยันตัวตนโดยอัตโนมัติเมื่อเปิดจากเครื่องเดียวกัน ไม่จำเป็นต้องกรอกโทเคนหรือทำการอนุมัติอุปกรณ์สำหรับการเข้าถึงในเครื่องเดียวกัน คุณควรเห็นแดชบอร์ดของ OpenClaw พร้อมกับโมเดล Lemonade ของคุณแสดงเป็น backend ที่ใช้งานอยู่

> หากคุณเปิดใช้งาน sandboxing แล้ว คุณสามารถตรวจสอบได้โดยขอให้ agent `run hostname` จากแดชบอร์ด หากคุณเห็นรหัสคอนเทนเนอร์สั้นๆ แทนที่จะเป็นชื่อโฮสต์ของเครื่องคุณ แสดงว่า sandbox ทำงานอยู่

**ยินดีด้วย คุณได้สร้างสแต็ก AI agent ที่ทำงานแบบโลคัลทั้งหมดตั้งแต่ต้นเรียบร้อยแล้ว**

> **ต้องการโทเคนของ gateway?** รันคำสั่ง `openclaw dashboard --no-open` เพื่อแสดง URL ของแดชบอร์ดพร้อมโทเคนที่ฝังอยู่ (คำสั่งนี้จะพยายามคัดลอกโทเคนไปยังคลิปบอร์ดของคุณด้วย) หรืออีกวิธีหนึ่งคือ โทเคนอยู่ที่ `gateway.auth.token` ในไฟล์ `~/.openclaw/openclaw.json`
>
> **การอนุมัติอุปกรณ์ระยะไกล:** เมื่อคุณเปิดแดชบอร์ดจากเครื่องที่สองหรือโทรศัพท์ เบราว์เซอร์จะแสดงรหัสคำขอ (request ID) กลับไปที่เครื่องที่รัน gateway แล้วรันคำสั่ง:
> ```bash
> openclaw devices approve <requestId>
> ```
> ขั้นตอนนี้จำเป็นเฉพาะสำหรับอุปกรณ์ระยะไกลหรืออุปกรณ์รอง เท่านั้น การเข้าถึงผ่าน loopback จากเครื่องเดียวกันจะยืนยันตัวตนโดยอัตโนมัติ

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## ทางเลือกเสริม: เชื่อมต่อช่องทางการสื่อสาร

เมื่อ gateway ทำงานแล้ว คุณสามารถเข้าถึง agent ในเครื่องของคุณได้จากอุปกรณ์ใดก็ได้ เลือกตัวเลือกที่เหมาะกับการตั้งค่าของคุณ OpenClaw รองรับ [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) และช่องทางอื่นๆ ดูรายการทั้งหมดได้ที่ [docs.openclaw.ai](https://docs.openclaw.ai)

---

### ตัวเลือก A: Discord

Discord ต้องมีเซิร์ฟเวอร์ที่**คุณมีสิทธิ์ผู้ดูแลระบบ (administrator access)** เพื่อเพิ่มบอท หากคุณใช้เซิร์ฟเวอร์ร่วมกับผู้อื่นแต่ไม่ได้เป็นเจ้าของ ให้ใช้ตัวเลือก B (Telegram) แทน
#### สร้างบัญชี Discord และเซิร์ฟเวอร์

หากคุณยังไม่มีบัญชี Discord ให้สมัครที่ [discord.com](https://discord.com) นอกจากนี้คุณยังต้องมีเซิร์ฟเวอร์ที่คุณเป็นผู้ดูแลระบบ โดยสร้างเซิร์ฟเวอร์ได้ด้วยการคลิกไอคอน **+** ในแถบด้านข้างของ Discord แล้วเลือก **Create My Own** เซิร์ฟเวอร์ส่วนตัวก็ใช้ได้

#### สร้างแอปพลิเคชันและบอทของ Discord

1. ไปที่ [Discord Developer Portal](https://discord.com/developers/applications) แล้วคลิก **New Application** ตั้งชื่อให้แอป (เช่น "openclaw-bot")
2. ในแถบด้านข้าง คลิก **Bot** ตั้งชื่อผู้ใช้ให้บอท
3. ในหน้า Bot เดิม เลื่อนลงไปที่ **Privileged Gateway Intents** แล้วเปิดใช้งาน:
   - **Message Content Intent** (จำเป็น)
   - **Server Members Intent** (แนะนำ)
4. เลื่อนกลับขึ้นไปด้านบนแล้วคลิก **Reset Token** เพื่อสร้างโทเค็นบอทของคุณ คัดลอกไว้

#### เพิ่มบอทเข้าเซิร์ฟเวอร์ของคุณ

1. ในแถบด้านข้าง คลิก **OAuth2/ URL Generator**
2. ในส่วน **Scopes** ให้เปิดใช้งาน `bot` และ `applications.commands`
3. ในส่วน **Bot Permissions** ให้เปิดใช้งาน: View Channels, Send Messages, Read Message History, Embed Links, Attach Files
4. คัดลอก URL ที่สร้างขึ้น วางลงในเบราว์เซอร์ของคุณ เลือกเซิร์ฟเวอร์ของคุณ แล้วยืนยัน บอทควรจะปรากฏในรายชื่อสมาชิกของเซิร์ฟเวอร์คุณแล้ว

#### รวบรวม ID ของคุณ

เปิดใช้งาน Developer Mode ใน Discord (**User Settings/ Advanced/ Developer Mode**) จากนั้น:
- คลิกขวาที่ไอคอนเซิร์ฟเวอร์ของคุณ: **Copy Server ID**
- คลิกขวาที่อวาตาร์ของคุณเอง: **Copy User ID**

#### อนุญาตให้สมาชิกเซิร์ฟเวอร์ส่งข้อความส่วนตัวถึงคุณได้

คลิกขวาที่ไอคอนเซิร์ฟเวอร์ของคุณ/ **Privacy Settings**/ เปิดใช้งาน **Direct Messages** วิธีนี้จะทำให้บอทสามารถส่งข้อความส่วนตัวถึงคุณได้ ซึ่งจำเป็นสำหรับขั้นตอนการจับคู่อุปกรณ์

#### กำหนดค่า OpenClaw สำหรับ Discord

จัดเก็บโทเค็นบอทของคุณเป็นตัวแปรสภาพแวดล้อม จากนั้นสร้างไฟล์แพตช์เดียวที่เปิดใช้งาน Discord อ้างอิงถึงโทเค็น และเพิ่มเซิร์ฟเวอร์ของคุณลงใน allowlist แทนที่ `<server_id>` และ `<user_id>` ด้วย ID ที่รวบรวมไว้ข้างต้น

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

> **อย่าพึ่งพาการขอให้ตัวเอเจนต์กำหนดค่าส่วนนี้ให้** เมื่อเปิดใช้งาน sandboxing แล้ว ตัวเอเจนต์จะไม่สามารถเขียนไปยัง `~/.openclaw/openclaw.json` จากภายใน sandbox ได้ ให้ใช้คำสั่ง CLI ข้างต้นบนโฮสต์แทน

รีสตาร์ตเกตเวย์เพื่อให้รับการตั้งค่าช่องทางใหม่:

```bash
openclaw gateway run --bind loopback --port 18789
```

คุณควรเห็นข้อความ `logged in to discord as <bot-name>` ในผลลัพธ์ของเกตเวย์ภายในไม่กี่วินาที

#### จับคู่บัญชี Discord ของคุณ

ส่งข้อความส่วนตัวถึงบอทใน Discord บอทจะตอบกลับด้วยรหัสจับคู่สั้นๆ

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

อนุมัติรหัสบนเครื่องที่รัน OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> รหัสจับคู่จะหมดอายุหลังจากผ่านไปหนึ่งชั่วโมง

ตอนนี้คุณสามารถสนทนากับเอเจนต์ของคุณได้โดยตรงจาก Discord และมอบหมายงานให้ฮาร์ดแวร์ในเครื่องของคุณทำได้แล้ว

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### ตัวเลือก B: Telegram

Telegram นั้นใช้งานง่ายกว่า Discord สำหรับผู้ใช้ส่วนใหญ่ ไม่ต้องใช้เซิร์ฟเวอร์และไม่ต้องมีสิทธิ์ผู้ดูแลระบบ

#### สร้างบอท Telegram

1. เปิด Telegram แล้วส่งข้อความถึง **@BotFather**
2. ส่ง `/newbot` แล้วทำตามคำแนะนำ บันทึกโทเค็นบอทที่ได้รับไว้

#### กำหนดค่า OpenClaw สำหรับ Telegram

จัดเก็บโทเค็นเป็นตัวแปรสภาพแวดล้อม:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

เพิ่มการกำหนดค่าช่องทางลงใน `~/.openclaw/openclaw.json` (หรือแพตช์ผ่านแดชบอร์ด):

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

รีสตาร์ตเกตเวย์ จากนั้นส่งข้อความใดก็ได้ถึงบอทของคุณใน Telegram อนุมัติการจับคู่:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

รหัสจับคู่จะหมดอายุหลังจากผ่านไปหนึ่งชั่วโมง ตอนนี้คุณสามารถสนทนากับเอเจนต์ของคุณผ่านข้อความส่วนตัวใน Telegram ได้แล้ว

---

## ขั้นตอนถัดไป

เมื่อเอเจนต์ของคุณสามารถรับคำสั่งจากโทรศัพท์และดำเนินการบนเครื่องในเครื่องของคุณได้แล้ว ต่อไปนี้คือแนวทางที่น่าสนใจสามแนวทางที่ควรลองสำรวจ:

1. **เครื่องมือสรุปตลาดหุ้น**: ตั้งเวลาให้ OpenClaw ดึงข้อมูลจาก financial API ตามช่วงเวลาที่กำหนดไว้ สรุปความเคลื่อนไหวของวันนั้นด้วยโมเดลในเครื่องของคุณ แล้วส่งสรุปประจำวันไปยังโทรศัพท์ของคุณทุกเช้าผ่านช่องทางที่คุณเลือก

2. **ตัวติดตามการปรับแต่งโมเดล (Fine-tuning)**: เริ่มงาน training จากระยะไกลผ่าน Telegram หรือ Discord จากนั้นให้เอเจนต์ติดตามล็อกการ training และรายงานค่า loss, การใช้งาน GPU และการใช้พื้นที่ดิสก์กลับมายังโทรศัพท์ของคุณเป็นระยะ หากการรันหยุดชะงักหรือ VRAM พุ่งสูงขึ้น คุณจะทราบได้ทันทีโดยไม่ต้องอยู่ที่เครื่องนั้น

3. **IOT ด้วย VLM ในเครื่อง**: ตั้งกล้องไว้ที่หน้าประตูบ้าน รันโมเดลวิชันบน Lemonade แล้วให้ OpenClaw วิเคราะห์เฟรมภาพตามคำขอหรือเมื่อมีการทริกเกอร์ ถามคำถาม "วันนี้มีพัสดุมาส่งไหม" จากโทรศัพท์ของคุณ แล้วรับคำตอบตรงๆ จากฮาร์ดแวร์ของคุณเอง