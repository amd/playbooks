<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# เรียกใช้ OpenClaw โดยใช้ Lemonade Server เป็นแบ็กเอนด์

## ภาพรวม

[**OpenClaw**](https://openclaw.ai/) คือเอเจนต์ AI ที่ทำงานได้อย่างอิสระ ซึ่งสามารถเขียนและรันโค้ด จัดการไฟล์ และทำงานที่ซับซ้อนหลายขั้นตอนแทนคุณได้ ต่างจากแชทแอสซิสแทนต์ที่เพียงแค่ตอบคำถาม OpenClaw จะลงมือทำงานจริงบนระบบของคุณ ซึ่งหมายความว่ามันต้องการแบ็กเอนด์ AI ที่รวดเร็วและมีความสามารถเพียงพอที่จะตามทันลูปการทำงานของเอเจนต์ที่มีความต้องการสูง

[**Lemonade Server**](https://lemonade-server.ai/) คือแบ็กเอนด์นั้น มันเป็นเซิร์ฟเวอร์อนุมาน (inference) ในเครื่องแบบโอเพนซอร์สที่รันโมเดล GenAI โดยตรงบนฮาร์ดแวร์ของคุณ และเปิดให้ใช้งานผ่าน OpenAI API ซึ่งเป็นมาตรฐานในอุตสาหกรรม

เมื่อนำมารวมกัน ทั้งสองจะกลายเป็นสแต็กเอเจนต์ AI ที่ทำงานในเครื่องอย่างสมบูรณ์ โดย Lemonade จัดการการอนุมานโมเดล ส่วน OpenClaw จัดเตรียมลูปของเอเจนต์ที่แปลงผลลัพธ์จากโมเดลให้กลายเป็นการกระทำจริง

> **ก่อนที่คุณจะดำเนินการต่อ:** OpenClaw เป็นเอเจนต์ AI ที่มีความเป็นอิสระในการทำงานสูง การให้เอเจนต์ AI ใดๆ เข้าถึงระบบของคุณอาจส่งผลให้เกิดผลลัพธ์ที่คาดเดาไม่ได้หรือไม่ได้ตั้งใจ โปรดดำเนินการต่อก็ต่อเมื่อคุณเข้าใจความเสี่ยงและยอมรับได้ที่ซอฟต์แวร์อิสระจะทำงานแทนคุณ

---

## สิ่งที่คุณจะได้เรียนรู้

เมื่อจบเพลย์บุ๊กนี้ คุณจะสามารถ:

- เรียนรู้เกี่ยวกับ **Lemonade Server**
- **ติดตั้ง OpenClaw** และ **ตั้งค่าให้ชี้ไปที่ Lemonade Server** เป็นแบ็กเอนด์ AI
- **เริ่มต้น OpenClaw gateway** และยืนยันว่าเอเจนต์ของคุณพร้อมทำงาน
- **เชื่อมต่อช่องทางการสื่อสาร** (Discord หรือ Telegram) เพื่อให้คุณสามารถแชทกับเอเจนต์ของคุณได้จากอุปกรณ์ใดก็ได้

---

## การตั้งค่าหน่วยความจำ (Memory Configuration)

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งซอฟต์แวร์ที่จำเป็น

<!-- @os:linux -->
- พีซีที่รัน **Ubuntu 24.04+** หรือดิสทริบิวชัน Linux ที่ใช้ Debian เป็นฐานและใช้งานร่วมกันได้ พร้อม `apt-get`
- แรม (RAM) อย่างน้อย **12 GB** (แนะนำ 64 GB ขึ้นไปสำหรับโมเดลขนาดใหญ่)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (ไม่บังคับ สำหรับการรัน OpenClaw ในสภาพแวดล้อมแซนด์บ็อกซ์)

- พื้นที่ดิสก์ว่าง **~10–30 GB** สำหรับน้ำหนักโมเดล
<!-- @os:end -->
<!-- @os:windows -->
- พีซีที่รัน **Windows 10/11**
- แรม (RAM) อย่างน้อย **12 GB** (แนะนำ 64 GB ขึ้นไปสำหรับโมเดลขนาดใหญ่)
- พื้นที่ดิสก์ว่าง **~10–30 GB** สำหรับน้ำหนักโมเดล
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (ไม่บังคับ สำหรับการรัน OpenClaw ในสภาพแวดล้อมแซนด์บ็อกซ์)
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

โมเดลที่แนะนำสำหรับเพลย์บุ๊กนี้คือ **Qwen3.6-35B-A3B-GGUF** จาก Unsloth ซึ่งเป็นโมเดล MoE ที่มีประสิทธิภาพสูงพร้อมหน้าต่างบริบท (context window) ขนาด 263,000 โทเคน ซึ่งเหมาะกับภาระงานของเอเจนต์เป็นอย่างมาก โมเดลนี้ใช้การควอนไทซ์แบบ UD-Q4_K_XL ดึงโมเดลนี้ได้เลยตอนนี้:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

จากนั้นโหลดโมเดลด้วยหน้าต่างบริบทขนาดใหญ่ และบันทึกการตั้งค่านี้ไว้สำหรับการรันครั้งต่อไป:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

โมเดลนี้มีความยาวบริบทเริ่มต้นที่ 262,144 โทเคน หากคุณพบข้อผิดพลาดหน่วยความจำไม่เพียงพอ (OOM) ให้พิจารณาลดขนาดหน้าต่างบริบทลง อย่างไรก็ตาม เนื่องจาก Qwen3.6 ใช้ประโยชน์จากบริบทที่ขยายออกไปสำหรับงานที่ซับซ้อน เราจึงแนะนำให้คงความยาวบริบทไว้อย่างน้อย 128K โทเคน เพื่อรักษาความสามารถในการคิด (thinking capabilities)

> **เคล็ดลับ: ปิดโหมดการคิดเพื่อให้เอเจนต์ตอบสนองได้เร็วขึ้น:** Qwen3.6-35B-A3B รันในโหมดการคิด (thinking mode) ตามค่าเริ่มต้น ซึ่งเพิ่มความหน่วงก่อนการตอบสนองแต่ละครั้ง สำหรับลูปของเอเจนต์แล้ว ค่าใช้จ่ายส่วนนี้จะสะสมขึ้นอย่างรวดเร็ว รีโพซิทอรี [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) มีคอนฟิกที่พร้อมใช้งานซึ่งปิดโหมดการคิดไว้ให้แล้ว หากต้องการใช้งาน ให้ดาวน์โหลดไฟล์และนำเข้า:
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

เรารัน OpenClaw ภายใน WSL (แนะนำ) และเชื่อมต่อกับ Lemonade ที่รันอยู่บน Windows โดยตรง วิธีนี้ทำให้คุณได้สภาพแวดล้อมเชลล์แบบ Linux สำหรับ OpenClaw ในขณะที่ยังคงใช้การเร่งความเร็วด้วย GPU ของ Lemonade บนฝั่ง Windows

### ติดตั้ง WSL และ Ubuntu

เปิด PowerShell ในฐานะผู้ดูแลระบบ (Administrator) และติดตั้งเคอร์เนล WSL:

```powershell
wsl --install --no-distribution
```

จากนั้นติดตั้ง Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### เปิดใช้งาน systemd ใน WSL

รันคำสั่งนี้ภายในเทอร์มินัล Ubuntu:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

รีสตาร์ต WSL:

```powershell
wsl --shutdown
wsl
```

### เชื่อมต่อ Lemonade จาก Windows เข้าสู่ WSL

WSL2 รันอยู่ในเครือข่ายเสมือน Lemonade บน Windows จะผูกกับ `127.0.0.1` ซึ่ง WSL ไม่สามารถเข้าถึงได้โดยตรง Windows port proxy จะช่วยส่งต่อทราฟฟิกจาก WSL gateway IP ไปยัง Windows localhost

**ค้นหา WSL gateway IP ของคุณ** (รันภายใน WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**เพิ่ม port proxy** (รันใน PowerShell ในฐานะผู้ดูแลระบบ โดยแทนที่ `<WSL-Gateway-IP>` ด้วย WSL gateway IP ของคุณ):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**เพิ่มกฎไฟร์วอลล์** (ใช้ PowerShell ที่ยกระดับสิทธิ์เดียวกัน):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**ตรวจสอบจาก WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

หากคุณได้โหลดโมเดล Qwen3.6-35B-A3B-GGUF ไว้แล้วในขั้นตอนก่อนหน้า คุณควรจะเห็นผลลัพธ์ JSON แบบนี้:

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

> กฎ `netsh portproxy` จะคงอยู่หลังรีบูต แต่ WSL gateway IP อาจเปลี่ยนแปลงหลังจากรัน `wsl --shutdown` หาก Lemonade ไม่สามารถเข้าถึงได้จาก WSL หลังจากรีสตาร์ต ให้รับ gateway IP ที่อัปเดตแล้วและปรับปรุง proxy ด้วย IP ใหม่นี้

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

แฟล็ก `--no-onboard` จะข้ามตัวช่วยตั้งค่าแบบโต้ตอบ (interactive setup wizard) ซึ่งคุณจะกำหนดค่าแบ็กเอนด์ของโมเดลด้วยตนเองในขั้นตอนถัดไป วิธีนี้ทำให้คุณควบคุมได้อย่างแม่นยำว่าโมเดลและเซิร์ฟเวอร์ใดจะถูกใช้งาน

เปิดเทอร์มินัลใหม่และยืนยันการติดตั้ง:

```bash
openclaw --version
```

> **เคล็ดลับ:** หากคุณพบข้อความ `command not found` หลังจากการติดตั้ง ให้เพิ่มไดเรกทอรี global bin ของ npm เข้าไปใน PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> เพื่อให้การตั้งค่านี้คงอยู่ถาวร ให้เพิ่มบรรทัดด้านบนลงในไฟล์ `~/.bashrc` หรือ `~/.zshrc` ของคุณ

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

รันกระบวนการตั้งค่าเริ่มต้นแบบ non-interactive ของ OpenClaw
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

> **การกำหนดขนาด context window ของ OpenClaw:** การบีบอัด (compaction) ของ OpenClaw จะเริ่มทำงานเมื่อ `contextTokens > contextWindow − reserveTokens` ค่าเริ่มต้นของ `reserveTokensFloor` คือ 20,000 โทเคน ซึ่งเป็นค่าขั้นต่ำที่จะแทนที่ `reserveTokens` เมื่อมีค่าต่ำกว่า ดังนั้นโมเดลใดก็ตามที่มี context ต่ำกว่าประมาณ 37,000 โทเคนจะทำให้เกิดลูปการบีบอัดไม่รู้จบ ให้ตั้งค่า reserve ให้ต่ำและปิดการใช้งานค่าขั้นต่ำนี้เพียงครั้งเดียวในไฟล์กำหนดค่าของคุณ และจะมีผลกับทุกโมเดล โดยไม่ต้องปรับแต่งแยกตามโมเดล:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` เป็น *ค่าขั้นต่ำ* (การป้องกันขั้นต่ำสุด) ไม่ใช่ค่า reserve เอง การตั้งค่าเฉพาะค่าขั้นต่ำนี้จะไม่มีผลใด ๆ การตั้งค่า `reserveTokensFloor: 0` จะปิดการป้องกันนี้ เพื่อให้ค่า `reserveTokens` ที่ต่ำกว่าถูกนำไปใช้ได้
>
> **เมื่อใดควรใช้การตั้งค่านี้:** ใช้การกำหนดค่านี้หาก context window ที่ใช้งานได้จริงของโมเดลของคุณต่ำกว่าประมาณ 37,000 โทเคน ไม่ว่าจะเป็นเพราะโมเดลมีขนาดเล็ก (เช่น 8k, 16k, 32k) หรือเพราะคุณตั้งใจจำกัดค่าให้ต่ำลง (เช่น โหลดโมเดลขนาด 128k แต่ตั้งค่า context เป็น 16k ใน Lemonade) หากไม่ตั้งค่านี้ OpenClaw จะเข้าสู่ลูปการบีบอัดไม่รู้จบเมื่อเริ่มทำงาน
>
> **สำหรับโมเดลที่มี context ขนาดใหญ่และใช้งานเต็มขนาด:** คุณสามารถข้ามการตั้งค่านี้ได้เลย ค่าเริ่มต้นจะทำงานได้ดีอยู่แล้ว การบีบอัดจะเริ่มทำงานก่อนที่ window จะเต็ม และโมเดลจะมีพื้นที่เพียงพอสำหรับสร้างคำตอบยาว ๆ หากคุณยังต้องการใช้การตั้งค่านี้ โปรดทราบว่า `reserveTokens: 4096` จะจำกัดความยาวของคำตอบไว้ที่ประมาณ 4,000 โทเคน ซึ่งอาจตัดการสร้างไฟล์ยาว ๆ หรือแผนงานที่ละเอียดให้สั้นลง
>
> **ตำแหน่งที่ควรเพิ่มการตั้งค่านี้:** ให้วางบล็อก `compaction` ไว้ภายใน `agents.defaults` ในไฟล์ `openclaw.json` ของคุณ (โดยปกติอยู่ที่ `~/.openclaw/openclaw.json`):
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
> ส่วนที่เหลือของการกำหนดค่าของคุณ (gateway, channels, models เป็นต้น) จะไม่เปลี่ยนแปลง โดยต้องเพิ่มเฉพาะคีย์ `compaction` เท่านั้น

### (แนะนำ) เปิดใช้งานการแยกสภาพแวดล้อมด้วย Docker Sandboxing

OpenClaw สามารถส่งต่อการดำเนินการไฟล์และโค้ดทั้งหมดของ agent ผ่านคอนเทนเนอร์ Docker ที่ถูกแยกออกจากระบบ แทนที่จะรันโดยตรงบนเครื่องของคุณ วิธีนี้จะจำกัดผลกระทบของการกระทำที่ไม่ตั้งใจให้อยู่ในขอบเขตของ sandbox เท่านั้น โดยไม่กระทบต่อระบบไฟล์และเครือข่ายของเครื่องหลักของคุณ

สร้างอิมเมจของ sandbox หนึ่งครั้ง (ต้องติดตั้ง Docker ไว้ก่อน):

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

รันคำสั่งนี้เพื่อเพิ่มคีย์ `sandbox` ภายในบล็อก `agents.defaults` ที่มีอยู่แล้วในไฟล์ `~/.openclaw/openclaw.json`:

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

คอนเทนเนอร์ sandbox จะ **ไม่มีการเข้าถึงเครือข่าย** โดยค่าเริ่มต้น ดูข้อมูลเพิ่มเติมเกี่ยวกับการ bind mount และการปรับแต่งเครือข่ายได้ที่ [เอกสารอ้างอิงการแยกสภาพแวดล้อม (sandboxing)](https://docs.openclaw.ai/gateway/sandboxing)

> #### การแก้ไขปัญหา: Docker Permission Denied
> 
> หากคุณได้รับข้อความ "permission denied" เมื่อรันคำสั่ง Docker:
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
> **ขั้นตอนที่ 2: หากยังคงพบข้อผิดพลาด ให้แก้ไขแบบถาวร**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> จากนั้น **รีบูต** ระบบของคุณ
> 
> **วิธีแก้ไขชั่วคราวแบบรวดเร็ว** (จะรีเซ็ตหลังรีบูต):
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

<!-- @os:linux -->
## (แนะนำ) การผสานรวม OpenClaw กับบริการ Firecrawl

[Firecrawl](https://docs.firecrawl.dev/introduction) เป็นบริการรวบรวมข้อมูลเว็บและดึงเนื้อหาแบบโฮสต์เองที่สามารถหลีกเลี่ยงข้อจำกัดเหล่านี้ และปลดล็อกศักยภาพเต็มรูปแบบของการทำงานอัตโนมัติของ OpenClaw

ในการตั้งค่านี้ OpenClaw จะทำงานเป็นชุดคอนเทนเนอร์ Docker ที่จัดการด้วย Podman เพื่อให้การจัดการวงจรชีวิตและการเริ่มทำงานอัตโนมัติเป็นเรื่องง่าย เราจะลงทะเบียน Firecrawl เป็นบริการ `systemd` ระดับผู้ใช้ (user-level) ที่ทำหน้าที่ควบคุมชุด Podman Compose ที่อยู่เบื้องหลัง วิธีนี้ทำให้ OpenClaw สามารถเริ่ม gateway หยุด และตรวจสอบบริการ Firecrawl ได้ด้วยคำสั่ง `systemctl --user` มาตรฐาน แทนที่จะต้องโต้ตอบกับคอนเทนเนอร์โดยตรง

เพื่อให้เข้าใจง่าย เราได้แบ่งกระบวนการทั้งหมดออกเป็นสี่ขั้นตอน:

---

### 1. ลงทะเบียนบริการระบบ
ไปยังไดเรกทอรีการกำหนดค่าผู้ใช้ของ systemd:
```bash
cd ~/.config/systemd/user
```
สร้างและเปิดไฟล์ใหม่ชื่อ `firecrawl.service`
```bash
nano firecrawl.service
```
คัดลอกและวางการกำหนดค่าต่อไปนี้:
```bash
[Unit]
Description=OpenClaw Firecrawl Service
After=podman.service
Requires=podman.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=%h/firecrawl

# Optional: Validate config before starting
ExecStartPre=/usr/bin/podman compose -f openclaw-compose.yaml config --quiet

# Generate token and write to .env file
ExecStartPre=/bin/bash -c 'chmod 644 %h/firecrawl/.env && echo "OPENCLAW_GATEWAY_TOKEN=$(openssl rand -hex 32)" > %h/firecrawl/.env'

# Step 1: Start containers in detached mode
ExecStart=/usr/bin/podman compose -f openclaw-compose.yaml up -d --remove-orphans

# Step 2: Wait for container to be healthy/ready
ExecStartPost=/bin/sleep 5

# Step 3: Run onboarding inside container in detached mode
ExecStartPost=/usr/bin/podman exec -d openclaw_gateway /bin/bash -c "openclaw onboard \
    --non-interactive \
    --accept-risk \
    --mode local \
    --auth-choice skip \
    --gateway-auth token \
    --gateway-token "$OPENCLAW_GATEWAY_TOKEN" "

# Stop containers when the service stops
ExecStop=/usr/bin/podman compose -f openclaw-compose.yaml down

[Install]
WantedBy=default.target
```
ณ จุดนี้ บริการดังกล่าวได้ถูกกำหนดไว้แล้ว แต่ยังไม่ได้ลงทะเบียนกับ `systemd`
ตรวจสอบให้แน่ใจว่าชื่อไฟล์ตรงกับที่คุณสร้างไว้ข้างต้นทุกประการ จากนั้นรัน:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
หากสำเร็จ คุณจะเห็นผลลัพธ์ดังต่อไปนี้:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` มีลิงก์สัญลักษณ์ (symbolic links) ไปยังบริการที่ถูกกำหนดค่าให้เริ่มทำงานโดยอัตโนมัติ
### 2. กำหนดค่า Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) เหมาะสำหรับผู้ที่ต้องการควบคุมสภาพแวดล้อมการ scraping และการประมวลผลข้อมูลอย่างเต็มที่ แต่ก็ต้องแลกมาด้วยความพยายามในการดูแลรักษาและกำหนดค่าที่เพิ่มขึ้น

เริ่มต้นด้วยการโคลนรีพอสิทอรี:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
สร้าง `.env` ในไดเรกทอรีราก `/firecrawl`: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. ปรับใช้ OpenClaw ด้วย Podman Compose

ก่อนดำเนินการต่อ ตรวจสอบให้แน่ใจว่าคุณได้ pull อิมเมจ Docker ของ OpenClaw เวอร์ชันล่าสุดแล้ว:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
เมื่อเสร็จแล้ว ให้ดาวน์โหลดไฟล์ Compose ของ OpenClaw [openclaw-compose.yaml](assets/openclaw-compose.yaml) และวางไว้ในไดเรกทอรีราก `/firecrawl`:

> ข้อกำหนดนี้จำเป็นเพื่อให้ `systemd` สามารถค้นหาและเริ่มบริการได้อย่างถูกต้องตามที่ระบุไว้ใน `WorkingDirectory=${HOME}/firecrawl`

> คุณสามารถขยายสแตกได้เสมอโดยเพิ่มบริการ Firecrawl เพิ่มเติมตามต้องการ รายการบริการทั้งหมดที่มีให้ใช้งานสามารถดูได้ใน [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) ฉบับทางการ

### 4. เปิดใช้งานบริการ OpenClaw ผ่าน Firecrawl 

ก่อนที่จะส่งมอบการควบคุมให้กับ `systemd` ให้ตรวจสอบว่าทุกอย่างทำงานได้อย่างถูกต้องโดยการรันสแตกด้วยตนเอง:
```bash
podman compose -f openclaw-compose.yaml up -d
```
หากทุกอย่างถูกกำหนดค่าอย่างถูกต้อง คุณควรเห็นคอนเทนเนอร์ OpenClaw ทำงานขึ้นมา และผลลัพธ์บรรทัดคำสั่งของคุณควรมีลักษณะคล้ายกับนี้:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

เมื่อตรวจสอบยืนยันแล้ว ให้ปิดสแตกก่อนดำเนินการต่อ:
```bash
podman compose -f openclaw-compose.yaml down
```
ก่อนเริ่มบริการ คุณต้องตรวจสอบให้แน่ใจว่าได้ตั้งค่าความเป็นเจ้าของและสิทธิ์ที่ถูกต้องบนไดเรกทอรี `firecrawl` และไฟล์ `.env` ของไดเรกทอรีนั้น
ซึ่งจำเป็นอย่างยิ่งเพื่อให้บริการสามารถเขียนข้อมูลรับรอง (credentials) ของคุณได้ในระหว่างการเริ่มทำงาน
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
เมื่อทุกอย่างได้รับการตรวจสอบยืนยันแล้ว ให้เริ่มบริการผ่าน `systemd`:
```bash
systemctl --user start firecrawl.service
```
[The OpenClaw Actions](https://docs.openclaw.ai/) สามารถเข้าถึงได้จากภายในคอนเทนเนอร์แบบโต้ตอบ และ Web Dashboard สามารถใช้งานได้บนโฮสต์และพอร์ตเดียวกันที่ http://127.0.0.1:18789
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### การรับ `OPENCLAW_GATEWAY_TOKEN` ของคุณ

เมื่อบริการทำงานขึ้นมาแล้ว คุณจะสังเกตเห็นไดเรกทอรี `.openclaw` ใหม่ถูกสร้างขึ้นในโฟลเดอร์ home ของคุณ (~/.openclaw) ไดเรกทอรีนี้ถูกล็อกไว้ตามค่าเริ่มต้น ดังนั้นคุณจะต้องปลดล็อกเพื่อดึงโทเค็นเกตเวย์ของคุณ

1. ให้สิทธิ์การเข้าถึงไดเรกทอรี:
```bash
sudo chmod 777 ~/.openclaw/
```
2. อ่านโทเค็นเกตเวย์ของคุณ:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
ค้นหาค่า `OPENCLAW_GATEWAY_TOKEN` ในผลลัพธ์

3. เปิดแดชบอร์ดเกตเวย์ในเบราว์เซอร์ของคุณที่ http://127.0.0.1:18789 วางโทเค็นของคุณเมื่อมีการถามเพื่อยืนยันตัวตน

หากต้องการหยุดบริการ ให้รัน:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## เริ่มต้น OpenClaw Gateway

เกตเวย์คือกระบวนการ OpenClaw ที่จัดการวงจรของ agent และให้บริการแดชบอร์ด:

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

หากต้องการเปิดแดชบอร์ด ให้รันคำสั่งนี้ในเทอร์มินัลที่สองในขณะที่เกตเวย์ยังทำงานอยู่:

```bash
openclaw dashboard
```

เนื่องจากเกตเวย์เชื่อมต่อกับ loopback แดชบอร์ดจะยืนยันตัวตนโดยอัตโนมัติเมื่อเปิดจากเครื่องเดียวกัน ไม่จำเป็นต้องป้อนโทเค็นหรืออนุมัติอุปกรณ์สำหรับการเข้าถึงในเครื่อง คุณควรเห็นแดชบอร์ด OpenClaw พร้อมกับโมเดล Lemonade ของคุณแสดงเป็นแบ็กเอนด์ที่ทำงานอยู่

> หากคุณเปิดใช้งาน sandboxing แล้ว คุณสามารถตรวจสอบได้โดยขอให้ agent `run hostname` จากแดชบอร์ด หากคุณเห็น container ID สั้นๆ แทนที่จะเป็น hostname ของเครื่อง แสดงว่า sandbox กำลังทำงาน

**ยินดีด้วย คุณได้สร้างสแตก AI agent ที่ทำงานในเครื่องทั้งหมดขึ้นมาจากศูนย์แล้ว**

> **ต้องการโทเค็นเกตเวย์หรือไม่?** รัน `openclaw dashboard --no-open` เพื่อแสดง URL ของแดชบอร์ดพร้อมกับโทเค็นที่ฝังอยู่ (คำสั่งนี้ยังพยายามคัดลอกไปยังคลิปบอร์ดของคุณด้วย) หรืออีกทางหนึ่ง โทเค็นจะอยู่ที่ `gateway.auth.token` ใน `~/.openclaw/openclaw.json`
>
> **การอนุมัติอุปกรณ์ระยะไกล:** เมื่อคุณเปิดแดชบอร์ดจากเครื่องที่สองหรือโทรศัพท์ เบราว์เซอร์จะแสดงหมายเลขคำขอ (request ID) กลับไปที่เครื่องที่รันเกตเวย์แล้วรัน:
> ```bash
> openclaw devices approve <requestId>
> ```
> ขั้นตอนนี้จำเป็นเฉพาะสำหรับอุปกรณ์ระยะไกลหรืออุปกรณ์รองเท่านั้น การเข้าถึงแบบ loopback จากเครื่องเดียวกันจะยืนยันตัวตนโดยอัตโนมัติ

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## ทางเลือกเสริม: เชื่อมต่อช่องทางการสื่อสาร

เมื่อเกตเวย์ทำงานอยู่ คุณสามารถเข้าถึง agent ในเครื่องของคุณได้จากอุปกรณ์ใดก็ได้ เลือกตัวเลือกที่เหมาะกับการตั้งค่าของคุณ OpenClaw รองรับ [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) และช่องทางอื่นๆ ดูรายการทั้งหมดได้ที่ [docs.openclaw.ai](https://docs.openclaw.ai)

---

### ตัวเลือก A: Discord

Discord ต้องการเซิร์ฟเวอร์ที่**คุณมีสิทธิ์ผู้ดูแลระบบ**เพื่อเพิ่มบอท หากคุณใช้เซิร์ฟเวอร์ร่วมกับผู้อื่นแต่ไม่ได้เป็นเจ้าของ ให้ใช้ตัวเลือก B (Telegram) แทน

#### สร้างบัญชีและเซิร์ฟเวอร์ Discord

หากคุณยังไม่มีบัญชี Discord ให้สมัครที่ [discord.com](https://discord.com) คุณยังต้องมีเซิร์ฟเวอร์ที่คุณเป็นผู้ดูแลระบบด้วย โดยสร้างเซิร์ฟเวอร์ได้โดยคลิกที่ไอคอน **+** ในแถบด้านข้างของ Discord แล้วเลือก **Create My Own** เซิร์ฟเวอร์ส่วนตัวก็ใช้ได้

#### สร้างแอปพลิเคชันและบอท Discord

1. ไปที่ [Discord Developer Portal](https://discord.com/developers/applications) และคลิก **New Application** ตั้งชื่อ (เช่น "openclaw-bot")
2. ในแถบด้านข้าง คลิก **Bot** ตั้งชื่อผู้ใช้สำหรับบอท
3. ยังอยู่ที่หน้า Bot เลื่อนไปที่ **Privileged Gateway Intents** และเปิดใช้งาน:
   - **Message Content Intent** (จำเป็น)
   - **Server Members Intent** (แนะนำ)
4. เลื่อนกลับขึ้นไปด้านบนและคลิก **Reset Token** เพื่อสร้างโทเค็นบอทของคุณ คัดลอกไว้

#### เพิ่มบอทลงในเซิร์ฟเวอร์ของคุณ

1. ในแถบด้านข้าง คลิก **OAuth2/ URL Generator**
2. ภายใต้ **Scopes** เปิดใช้งาน `bot` และ `applications.commands`
3. ภายใต้ **Bot Permissions** เปิดใช้งาน: View Channels, Send Messages, Read Message History, Embed Links, Attach Files
4. คัดลอก URL ที่สร้างขึ้น วางในเบราว์เซอร์ของคุณ เลือกเซิร์ฟเวอร์ของคุณ และยืนยัน บอทควรปรากฏในรายชื่อสมาชิกของเซิร์ฟเวอร์คุณแล้ว
#### รวบรวม ID ของคุณ

เปิดใช้งาน Developer Mode ใน Discord (**User Settings/ Advanced/ Developer Mode**) จากนั้น:
- คลิกขวาที่ไอคอนเซิร์ฟเวอร์ของคุณ: **Copy Server ID**
- คลิกขวาที่อวาตาร์ของคุณเอง: **Copy User ID**

#### อนุญาตให้สมาชิกในเซิร์ฟเวอร์ส่ง DM ถึงคุณได้

คลิกขวาที่ไอคอนเซิร์ฟเวอร์ของคุณ/ **Privacy Settings**/ เปิดใช้งาน **Direct Messages** วิธีนี้จะช่วยให้บอทสามารถส่ง DM ถึงคุณได้ ซึ่งจำเป็นสำหรับขั้นตอนการจับคู่ (pairing)

#### กำหนดค่า OpenClaw สำหรับ Discord

เก็บโทเค็นบอทของคุณไว้เป็นตัวแปรสภาพแวดล้อม จากนั้นสร้างไฟล์แพตช์ไฟล์เดียวที่เปิดใช้งาน Discord อ้างอิงถึงโทเค็น และอนุญาตเซิร์ฟเวอร์ของคุณในรายการที่อนุญาต (allowlist) แทนที่ `<server_id>` และ `<user_id>` ด้วย ID ที่รวบรวมไว้ข้างต้น

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

> **อย่าพึ่งพาการขอให้เอเจนต์กำหนดค่าสิ่งนี้ให้** เมื่อเปิดใช้งาน sandbox เอเจนต์จะไม่สามารถเขียนไปยัง `~/.openclaw/openclaw.json` จากภายใน sandbox ได้ ให้ใช้คำสั่ง CLI ข้างต้นบนโฮสต์แทน

รีสตาร์ตเกตเวย์เพื่อให้โหลดการกำหนดค่าช่องทางใหม่:

```bash
openclaw gateway run --bind loopback --port 18789
```

คุณควรจะเห็นข้อความ `logged in to discord as <bot-name>` ในเอาต์พุตของเกตเวย์ภายในเวลาไม่กี่วินาที

#### จับคู่บัญชี Discord ของคุณ

ส่ง DM ถึงบอทใน Discord บอทจะตอบกลับด้วยรหัสจับคู่สั้น ๆ

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

อนุมัติรหัสดังกล่าวบนเครื่องที่รัน OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> รหัสจับคู่จะหมดอายุหลังจากผ่านไปหนึ่งชั่วโมง

ตอนนี้คุณสามารถแชทกับเอเจนต์ของคุณได้โดยตรงจาก Discord และมอบหมายงานให้ฮาร์ดแวร์ในเครื่องของคุณประมวลผล

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### ตัวเลือก B: Telegram

Telegram ใช้งานง่ายกว่า Discord สำหรับผู้ใช้ส่วนใหญ่ ไม่ต้องใช้เซิร์ฟเวอร์และไม่ต้องมีสิทธิ์แอดมิน

#### สร้างบอท Telegram

1. เปิด Telegram และส่งข้อความถึง **@BotFather**
2. ส่งคำสั่ง `/newbot` และทำตามขั้นตอนที่แจ้ง บันทึกโทเค็นบอทที่ได้รับไว้

#### กำหนดค่า OpenClaw สำหรับ Telegram

เก็บโทเค็นไว้เป็นตัวแปรสภาพแวดล้อม:

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

รีสตาร์ตเกตเวย์ จากนั้นส่งข้อความใด ๆ ถึงบอทของคุณใน Telegram อนุมัติการจับคู่:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

รหัสจับคู่จะหมดอายุหลังจากผ่านไปหนึ่งชั่วโมง ตอนนี้คุณสามารถแชทกับเอเจนต์ของคุณผ่าน Telegram DM ได้แล้ว

---

## ขั้นตอนถัดไป

เมื่อเอเจนต์ของคุณสามารถรับคำสั่งจากโทรศัพท์และดำเนินการบนเครื่องในเครื่องของคุณได้แล้ว ต่อไปนี้คือสามแนวทางที่น่าลองสำรวจเพิ่มเติม:

1. **เครื่องมือสรุปตลาดหุ้น**: ตั้งเวลาให้ OpenClaw ดึงข้อมูลจาก API ทางการเงินตามช่วงเวลาที่กำหนดไว้ สรุปความเคลื่อนไหวของวันด้วยโมเดลในเครื่องของคุณ และส่งบทสรุปไปยังโทรศัพท์ของคุณทุกเช้าผ่านช่องทางที่คุณเลือก

2. **ตัวติดตามการ Fine-tuning**: เริ่มงานฝึกโมเดล (training job) จากระยะไกลผ่าน Telegram หรือ Discord จากนั้นให้เอเจนต์ติดตามล็อกการฝึก (training log) แบบเรียลไทม์ และรายงานค่า loss เป็นระยะ การใช้งาน GPU และการใช้พื้นที่ดิสก์กลับมายังโทรศัพท์ของคุณ หากการรันหยุดชะงักหรือ VRAM พุ่งสูงขึ้น คุณจะทราบได้ทันทีโดยไม่จำเป็นต้องอยู่หน้าเครื่อง

3. **IOT ด้วย VLM ในเครื่อง**: ตั้งกล้องไว้ที่หน้าประตูบ้าน รันโมเดลวิชันบน Lemonade และให้ OpenClaw วิเคราะห์เฟรมภาพตามคำขอหรือตามทริกเกอร์ ถามว่า "วันนี้มีพัสดุมาส่งไหม" จากโทรศัพท์ของคุณ แล้วรับคำตอบที่ตรงประเด็นจากฮาร์ดแวร์ของคุณเอง

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