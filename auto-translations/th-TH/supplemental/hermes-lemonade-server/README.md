<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **การแปลด้วยเครื่อง.** หน้านี้ได้รับการแปลโดยอัตโนมัติจากภาษาอังกฤษ และยังไม่ได้รับการตรวจสอบโดยมนุษย์ อาจมีข้อผิดพลาด และคำแนะนำ คำสั่ง การดาวน์โหลด ความพร้อมใช้งานของผลิตภัณฑ์ หรือเนื้อหาอื่นๆ บางส่วนอาจแตกต่างกันไปตามภาษาหรือภูมิภาค ในกรณีที่มีความไม่สอดคล้องหรือความคลาดเคลื่อนใดๆ ให้ถือว่าเวอร์ชันภาษาอังกฤษต้นฉบับของ playbook เป็นฉบับที่มีผลบังคับใช้และมีอำนาจเหนือกว่า
<!-- auto-translated-disclaimer:end -->

# การรันตัวแทน Hermes ในเครื่องด้วย Lemonade Server

## ภาพรวม

[**Hermes Agent**](https://hermes-agent.nousresearch.com/) คือตัวแทน AI ที่พัฒนาตนเองได้ สร้างขึ้นโดย Nous Research มีลูปการเรียนรู้ในตัว สามารถสร้างทักษะจากประสบการณ์ สร้างหน่วยความจำถาวรเกี่ยวกับตัวคุณในทุกเซสชัน และสามารถรันระบบอัตโนมัติตามกำหนดเวลาแทนคุณได้ ซึ่งแตกต่างจากผู้ช่วยแชททั่วไป Hermes ลงมือทำสิ่งต่าง ๆ จริง เช่น การรันคำสั่งเชลล์ การเขียนไฟล์ การท่องเว็บ และการมอบหมายงานแบบขนานให้กับ subagent

[**Lemonade Server**](https://lemonade-server.ai/) คือแบ็กเอนด์การอนุมาน (inference) ในเครื่องที่ขับเคลื่อนระบบนี้ เป็นเซิร์ฟเวอร์โอเพนซอร์สที่รันโมเดล GenAI โดยตรงบนฮาร์ดแวร์ AMD ของคุณ และเปิดให้ใช้งานผ่าน OpenAI API ซึ่งเป็นมาตรฐานในวงการ

เมื่อนำมารวมกัน ทั้งสองจะกลายเป็นสแตก AI agent ที่ทำงานในเครื่องอย่างสมบูรณ์ โดย Lemonade จัดการการอนุมานโมเดลบน GPU ของคุณ ส่วน Hermes จัดเตรียมลูปของตัวแทน หน่วยความจำ ทักษะ และเกตเวย์การส่งข้อความ

> **ก่อนที่คุณจะดำเนินการต่อ:** Hermes Agent เป็นตัวแทน AI ที่มีความเป็นอิสระสูง การให้ตัวแทน AI ใด ๆ เข้าถึงระบบของคุณอาจส่งผลให้เกิดผลลัพธ์ที่ไม่สามารถคาดเดาได้หรือไม่ได้ตั้งใจ โปรดดำเนินการต่อเฉพาะเมื่อคุณเข้าใจความเสี่ยงและพร้อมรับมือกับซอฟต์แวร์อัตโนมัติที่ทำงานแทนคุณ

---

## สิ่งที่คุณจะได้เรียนรู้

เมื่อจบ playbook นี้ คุณจะสามารถ:

- **ติดตั้ง Hermes Agent** และตั้งค่าให้ชี้ไปที่ **Lemonade Server** เป็นแบ็กเอนด์ AI
- **(แนะนำ) เปิดใช้งานแซนด์บ็อกซ์ Docker/Podman** เพื่อแยกการทำงานของตัวแทนออกจากโฮสต์ของคุณ
- **เริ่มเกตเวย์ Hermes** และยืนยันว่าตัวแทนของคุณพร้อมใช้งาน
- **เชื่อมต่อช่องทางการสื่อสาร** (Discord หรือ Telegram) เพื่อให้คุณสามารถแชทกับตัวแทนของคุณได้จากทุกอุปกรณ์

---

<!-- @device:halo_box,halo,stx,krk -->
## การตั้งค่าหน่วยความจำ (Memory Configuration)

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งซอฟต์แวร์ที่จำเป็น

<!-- @os:linux -->
- พีซีที่รัน **Ubuntu 24.04+** หรือดิสโทร Linux ที่ใช้ Debian ที่เข้ากันได้ซึ่งมี `apt-get`
- RAM อย่างน้อย **12 GB** (แนะนำ 64 GB ขึ้นไปสำหรับโมเดลขนาดใหญ่)
- พื้นที่ว่างบนดิสก์ **~10–30 GB** สำหรับไฟล์น้ำหนักโมเดล
- [Podman](https://podman.io/docs/installation) (ไม่บังคับ สำหรับการทำแซนด์บ็อกซ์ Hermes Agent)
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @os:windows -->
- พีซีที่รัน **Windows 10/11**
- RAM อย่างน้อย **12 GB** (แนะนำ 64 GB ขึ้นไปสำหรับโมเดลขนาดใหญ่)
- พื้นที่ว่างบนดิสก์ **~10–30 GB** สำหรับไฟล์น้ำหนักโมเดล
- Podman (ไม่บังคับ สำหรับการทำแซนด์บ็อกซ์ Hermes Agent) ติดตั้งภายใน WSL:
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @device:halo_box -->
> Podman ถูกติดตั้งไว้ล่วงหน้าแล้วบน Halo Box และไม่จำเป็นต้องตั้งค่าเพิ่มเติม
<!-- @device:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @prereq:hermes,lemonade-models-qwen3-6-35b-a3b,podman,lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## ดึงและโหลดโมเดลที่แนะนำ

โมเดลที่แนะนำสำหรับ playbook นี้คือ **Qwen3.6-35B-A3B-GGUF** จาก Unsloth ซึ่งเป็นโมเดล MoE ที่มีประสิทธิภาพสูงพร้อมหน้าต่างบริบท (context window) ขนาด 263k โทเคน ที่เหมาะสมอย่างยิ่งกับงานประเภทตัวแทน (agent workloads) โมเดลนี้ใช้การควอนไทซ์แบบ UD-Q4_K_XL ดึงโมเดลนี้ได้เลยตอนนี้:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

จากนั้นโหลดโมเดลด้วยหน้าต่างบริบทขนาดใหญ่ และบันทึกการตั้งค่านี้ไว้สำหรับการรันครั้งต่อ ๆ ไป:

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end -->

โมเดลนี้มีความยาวบริบทเริ่มต้นที่ 262,144 โทเคน หากคุณพบข้อผิดพลาดหน่วยความจำไม่เพียงพอ (OOM) ให้พิจารณาลดขนาดหน้าต่างบริบท

> **เคล็ดลับ: ปิดโหมดคิดเพื่อการตอบสนองของตัวแทนที่รวดเร็วขึ้น:** Qwen3.6-35B-A3B ทำงานในโหมดคิด (thinking mode) ตามค่าเริ่มต้น ซึ่งเพิ่มเวลาแฝงก่อนการตอบสนองแต่ละครั้ง สำหรับลูปของตัวแทน ภาระนี้จะสะสมอย่างรวดเร็ว รีโพ [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) มีการตั้งค่าสำเร็จรูปที่ปิดโหมดคิดไว้ให้แล้ว หากต้องการใช้งาน ให้ดาวน์โหลดไฟล์และนำเข้า:
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

## ตั้งค่า WSL

เราจะรัน Hermes Agent ภายใน WSL และเชื่อมต่อกับ Lemonade ที่รันแบบเนทีฟบน Windows วิธีนี้จะทำให้คุณมีสภาพแวดล้อมเชลล์ของ Linux สำหรับ Hermes ในขณะที่ยังคงการเร่งความเร็วด้วย GPU ของ Lemonade ไว้ที่ฝั่ง Windows

### ติดตั้ง WSL และ Ubuntu

เปิด PowerShell ในฐานะผู้ดูแลระบบ (Administrator) แล้วติดตั้งเคอร์เนล WSL:

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

รีสตาร์ท WSL:

```powershell
wsl --shutdown
wsl
```

### เชื่อม Lemonade จาก Windows เข้าสู่ WSL

WSL2 ทำงานในเครือข่ายเสมือน Lemonade บน Windows จะผูกกับ `127.0.0.1` ซึ่ง WSL ไม่สามารถเข้าถึงได้โดยตรง พร็อกซีพอร์ตของ Windows จะส่งต่อทราฟฟิกจาก IP เกตเวย์ของ WSL ไปยัง localhost ของ Windows

**ค้นหา IP เกตเวย์ของ WSL** (รันภายใน WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**เพิ่มพร็อกซีพอร์ต** (รันใน PowerShell ในฐานะผู้ดูแลระบบ แทนที่ `<WSL-Gateway-IP>` ด้วย IP เกตเวย์ WSL ของคุณ):

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

หากคุณได้โหลดโมเดล Qwen3.6-35B-A3B-GGUF ในขั้นตอนก่อนหน้าแล้ว คุณควรเห็นผลลัพธ์ JSON ที่แสดงรายการโมเดลที่โหลดไว้

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

> กฎ `netsh portproxy` จะคงอยู่แม้รีบูตเครื่อง แต่ IP เกตเวย์ของ WSL อาจเปลี่ยนไปหลังจากรัน `wsl --shutdown` หากไม่สามารถเข้าถึง Lemonade จาก WSL ได้หลังจากรีสตาร์ท ให้นำ IP เกตเวย์ที่อัปเดตแล้วมาปรับปรุงพร็อกซีด้วย IP ใหม่นี้

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

## ติดตั้ง Hermes Agent

<!-- @os:windows -->
> รันคำสั่งในส่วนนี้ภายใน **เทอร์มินัล WSL** ของคุณ เว้นแต่จะระบุไว้เป็นอย่างอื่น
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

แฟล็ก `--skip-setup` จะข้ามตัวช่วยการตั้งค่าแบบโต้ตอบ เพื่อให้คุณสามารถกำหนดค่าแบ็กเอนด์โมเดลด้วยตนเองในขั้นตอนถัดไป

โหลดเชลล์ของคุณใหม่:

```bash
source ~/.bashrc
```

ยืนยันการติดตั้ง:

```bash
hermes --version
```

รันการวินิจฉัยตนเองเพื่อตรวจสอบความสัมพันธ์ทั้งหมด:

```bash
hermes doctor
```

> **เคล็ดลับ:** หากคุณเห็น `command not found` หลังจากการติดตั้ง ให้เพิ่ม Hermes ลงใน PATH ของคุณ:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> หากต้องการให้มีผลถาวร ให้เพิ่มบรรทัดด้านบนลงใน `~/.bashrc` หรือ `~/.zshrc` ของคุณ

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
## การกำหนดค่า Hermes ให้ใช้งาน Lemonade

Hermes จัดเก็บการกำหนดค่าโมเดลไว้ที่ `~/.hermes/config.yaml` คุณสามารถใช้ตัวเลือกแบบโต้ตอบ `hermes model` หรือเขียนการกำหนดค่าโดยตรงก็ได้

### ตัวเลือกที่ 1: ตัวเลือกแบบโต้ตอบ

<!-- @os:windows -->
> รันคำสั่งต่อไปนี้ภายใน **WSL terminal** ของคุณ
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

เมื่อมีการแจ้งเตือน:

1. เลือก **Custom endpoint (enter URL manually)**
<!-- @os:linux -->
2. **API base URL:** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **API base URL:** ใช้ WSL gateway IP โดยรันคำสั่ง `ip route show default | awk '{print $3}' | head -1` ภายใน WSL เพื่อนำค่าดังกล่าวมาใช้ จากนั้นป้อน `http://<WSL-Gateway-IP>:13305/api/v1`
<!-- @os:end -->
3. **API key:** `lemonade`
4. **API compatibility mode:** `1` (Auto-detect)
5. **Select model:** เลือก `Qwen3.6-35B-A3B-GGUF` จากรายการ
6. **Context length in tokens:** `262144`
7. **Display name:** `local-lemonade` (หรือชื่อใดก็ได้ที่คุณต้องการ)

`hermes model` จะบันทึกทั้งการเลือกโมเดลที่ใช้งานอยู่และรายการ `custom_providers` ที่มีชื่อ ซึ่งเก็บความยาวของบริบท (context length) ไว้พร้อมกับ endpoint ผลลัพธ์ใน `~/.hermes/config.yaml` จะมีลักษณะดังนี้:

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

### ตัวเลือกที่ 2: เขียนการกำหนดค่าโดยตรง

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

ภายใน WSL terminal ของคุณ ให้นำ IP ของโฮสต์ Windows มาใช้และเขียนการกำหนดค่า:

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

## (แนะนำ) เปิดใช้งาน Podman Sandboxing

Hermes Agent สามารถส่งการดำเนินการ shell และไฟล์ทั้งหมดของ agent ผ่านคอนเทนเนอร์ที่แยกออกมา แทนที่จะรันโดยตรงบนโฮสต์ของคุณ วิธีนี้จะจำกัดขอบเขตผลกระทบของการกระทำที่ไม่ได้ตั้งใจให้อยู่ภายใน sandbox เท่านั้น โดยไม่กระทบต่อระบบไฟล์และเครือข่ายของโฮสต์คุณ

สร้างอิมเมจ sandbox แบบน้ำหนักเบา:

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
เข้าสู่ WSL terminal ของคุณ:

```powershell
wsl -d Ubuntu-24.04
```

จากนั้น สร้างอิมเมจ sandbox แบบน้ำหนักเบา:

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

จากนั้นกำหนดค่า Hermes ให้ใช้ Podman เป็น container runtime และตั้งค่า terminal backend:

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> `terminal.backend` ยังคงเป็น `docker`
> `HERMES_DOCKER_BINARY` คือสิ่งที่บอกให้ Hermes ใช้ Podman เป็น runtime แทน

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

ตอนนี้ Hermes จะเริ่มต้นคอนเทนเนอร์ sandbox แบบถาวร และส่งการเรียกใช้เครื่องมือ `terminal` และไฟล์ทั้งหมดผ่านคอนเทนเนอร์นี้ คอนเทนเนอร์จะมีวงจรชีวิตร่วมกับกระบวนการ Hermes โดยถูกนำกลับมาใช้ซ้ำในทุกการเรียกใช้เครื่องมือ และจะถูกทำลายเมื่อ Hermes ปิดการทำงาน

> **ตรวจสอบว่า sandbox ทำงานได้ถูกต้อง:** เริ่มต้น Hermes (`hermes`) และสั่งให้รัน `run hostname` - คุณควรเห็น container ID สั้น ๆ แทนที่จะเป็นชื่อโฮสต์ของเครื่องคุณ คุณยังสามารถสั่งให้รัน `rm -rf <path-to-a-dummy-file/folder>` ได้ด้วย: Hermes จะยืนยันการลบ แต่โฟลเดอร์นั้นจะยังคงอยู่บนโฮสต์ของคุณ เนื่องจากคำสั่งถูกรันภายใน `$HOME` ที่แยกออกมาของคอนเทนเนอร์ ไม่ใช่ของคุณ

> **ต้องการการแยกส่วนที่แข็งแกร่งกว่านี้หรือไม่?** Hermes ยังมีอิมเมจ Docker อย่างเป็นทางการ (`nousresearch/hermes-agent`) ที่รันกระบวนการ agent ทั้งหมดภายในคอนเทนเนอร์ - ทั้ง gateway, เครื่องมือ และอื่น ๆ ดูรายละเอียดการตั้งค่าได้ที่ [เอกสาร Hermes Docker](https://hermes-agent.nousresearch.com/docs/user-guide/docker)

---

<!-- @os:linux -->
## (แนะนำ) การผสานรวม Hermes กับบริการ Firecrawl

Hermes สามารถเรียกดูและดึงเนื้อหาจากเว็บไซต์โดยใช้เครื่องมือเว็บในตัว อย่างไรก็ตาม เว็บไซต์สมัยใหม่จำนวนมากใช้ระบบตรวจจับบอต ซึ่งจะบล็อกคำขอ HTTP แบบธรรมดาและส่งคืนหน้าท้าทาย (challenge page) แทนที่จะเป็นเนื้อหาจริง ด้วยเหตุนี้ Hermes อาจไม่สามารถดึงข้อมูลจากเว็บไซต์เหล่านี้ได้อย่างน่าเชื่อถือ

เพื่อเอาชนะข้อจำกัดนี้ [Firecrawl](https://docs.firecrawl.dev/introduction) มอบบริการสำหรับการรวบรวมข้อมูลเว็บ (web crawling) และการดึงเนื้อหาแบบโฮสต์ด้วยตนเอง ที่สามารถหลีกเลี่ยงการท้าทายเหล่านี้และปลดล็อกศักยภาพสูงสุดของระบบอัตโนมัติของ Hermes

ในการตั้งค่านี้ Firecrawl ทำงานเป็นชุดคอนเทนเนอร์ Docker ที่จัดการด้วย Podman เพื่อให้การจัดการวงจรชีวิตและการเริ่มต้นอัตโนมัติง่ายขึ้น เราจะลงทะเบียน Firecrawl เป็นบริการ `systemd` ระดับผู้ใช้ ที่ทำหน้าที่ประสานงานชุด Podman Compose ที่อยู่เบื้องหลัง วิธีนี้ช่วยให้ Hermes สามารถเริ่ม หยุด และตรวจสอบบริการ Firecrawl ได้โดยใช้คำสั่ง `systemctl --user` มาตรฐาน แทนที่จะโต้ตอบกับคอนเทนเนอร์โดยตรง

เพื่อให้ง่ายขึ้น เราได้แบ่งกระบวนการทั้งหมดออกเป็นสี่ขั้นตอน:

---

### 1. ลงทะเบียนบริการของระบบ
ไปที่ไดเรกทอรีการกำหนดค่าผู้ใช้ของ systemd:
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
ถึงจุดนี้ บริการได้ถูกกำหนดไว้แล้ว แต่ยังไม่ได้ลงทะเบียนกับ `systemd`
ตรวจสอบให้แน่ใจว่าชื่อไฟล์ตรงกับที่คุณสร้างไว้ด้านบนทุกประการ จากนั้นรัน:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
หากสำเร็จ คุณควรเห็นผลลัพธ์ดังนี้:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` ประกอบด้วยลิงก์สัญลักษณ์ (symbolic links) ไปยังบริการที่ถูกกำหนดค่าให้เริ่มต้นโดยอัตโนมัติ

### 2. กำหนดค่า Firecrawl สำหรับบริการของคุณ

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) เหมาะสำหรับผู้ที่ต้องการควบคุมสภาพแวดล้อมการสครีปและการประมวลผลข้อมูลอย่างเต็มที่ แต่ก็ต้องแลกมากับความพยายามในการบำรุงรักษาและกำหนดค่าเพิ่มเติม

เริ่มต้นด้วยการโคลนที่เก็บข้อมูล (repository):
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
สร้างไฟล์ `.env` ในไดเรกทอรีราก `/firecrawl`:
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
> ตั้งค่า `BULL_AUTH_KEY` ให้เป็นค่าลับที่รัดกุม โดยเฉพาะอย่างยิ่งในการใช้งานใด ๆ ที่สามารถเข้าถึงได้จากเครือข่ายที่ไม่น่าเชื่อถือ
### 3. การปรับใช้ Hermes ผ่าน Compose

ก่อนดำเนินการต่อ โปรดตรวจสอบให้แน่ใจว่าคุณได้ดึงอิมเมจ Docker ของ Hermes เวอร์ชันล่าสุดมาแล้ว:
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
เมื่อเสร็จแล้ว ให้ดาวน์โหลดไฟล์ Compose ของ Hermes [hermes-compose.yaml](assets/hermes-compose.yaml) และวางไว้ในไดเรกทอรีราก `/firecrawl`:

> รูปแบบนี้จำเป็นสำหรับ `systemd` เพื่อให้สามารถค้นหาและเริ่มบริการได้อย่างถูกต้องตามที่ระบุไว้ใน `WorkingDirectory=${HOME}/firecrawl`

> คุณสามารถขยายสแตกได้ตลอดเวลาโดยการเพิ่มบริการ Firecrawl อื่น ๆ ตามต้องการ รายการบริการที่มีทั้งหมดสามารถดูได้ที่ [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) อย่างเป็นทางการ

### 4. เปิดใช้งานบริการ Hermes ผ่าน Firecrawl

ก่อนที่จะส่งมอบการควบคุมให้กับ `systemd` ให้ตรวจสอบว่าทุกอย่างทำงานได้อย่างถูกต้องโดยการรันสแตกด้วยตนเองก่อน:
```bash
podman compose -f hermes-compose.yaml up -d
```
หากทุกอย่างถูกกำหนดค่าอย่างถูกต้อง คุณควรเห็นคอนเทนเนอร์ Hermes ทำงานขึ้นมา และผลลัพธ์บนบรรทัดคำสั่งของคุณควรมีลักษณะคล้ายกับนี้:
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

เมื่อตรวจสอบแล้ว ให้ปิดสแตกลงก่อนดำเนินการต่อ:
```bash
podman compose -f hermes-compose.yaml down
```
เมื่อทุกอย่างได้รับการตรวจสอบแล้ว ให้เริ่มบริการผ่าน `systemd`:
```bash
systemctl --user start firecrawl.service
```
[API ของ Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints) สามารถเข้าถึงได้จากภายในคอนเทนเนอร์แบบโต้ตอบ และแดชบอร์ดบนเว็บสามารถใช้งานได้บนโฮสต์และพอร์ตเดียวกันที่ http://127.0.0.1:9119
<p align="center">
  <img src="assets/System_Service_launch.png" width="500" height="500" />
</p>

หากต้องการหยุดบริการ ให้รัน:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Hermes Native

เริ่มเซสชัน CLI แบบโต้ตอบโดยตรง:

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

**ยินดีด้วย คุณได้สร้างสแตก AI agent ที่ทำงานแบบโลคัลทั้งหมดเรียบร้อยแล้ว**

### แดชบอร์ดบนเว็บ

Hermes มาพร้อมกับ UI บนเบราว์เซอร์สำหรับจัดการการกำหนดค่า คีย์ API โมเดล เซสชัน หน่วยความจำ และงาน cron เปิดเทอร์มินัลที่สองในขณะที่เกตเวย์หรือ CLI กำลังทำงานอยู่ และเปิดใช้งานด้วย:

```bash
hermes dashboard
```

คำสั่งนี้จะเริ่มเซิร์ฟเวอร์โลคัลและเปิด `http://127.0.0.1:9119` ในเบราว์เซอร์ของคุณ ดูข้อมูลอ้างอิงฟีเจอร์ทั้งหมดได้ที่ [เอกสารแดชบอร์ด](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard)
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## ทางเลือกเสริม: เชื่อมต่อช่องทางการสื่อสาร

เมื่อเกตเวย์ทำงานแล้ว คุณสามารถเข้าถึง agent บนเครื่องของคุณได้จากอุปกรณ์ใดก็ได้ Hermes รองรับ [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord), [Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) และอื่น ๆ

---

### Discord

Discord ต้องการเซิร์ฟเวอร์ที่ **คุณมีสิทธิ์ผู้ดูแลระบบ** เพื่อเพิ่มบอท หากคุณใช้เซิร์ฟเวอร์ร่วมกับผู้อื่นแต่ไม่ได้เป็นเจ้าของ ให้ใช้ Telegram แทน

#### สร้างแอปพลิเคชันและบอทของ Discord

1. ไปที่ [Discord Developer Portal](https://discord.com/developers/applications) และคลิก **New Application** ตั้งชื่อ (เช่น "hermes-bot")
2. ในแถบด้านข้าง คลิก **Bot** ตั้งชื่อผู้ใช้สำหรับบอท
3. ที่หน้า Bot เดิม เลื่อนลงไปที่ **Privileged Gateway Intents** และเปิดใช้งาน:
   - **Message Content Intent** (จำเป็น)
   - **Server Members Intent** (แนะนำ)
4. เลื่อนขึ้นไปด้านบนและคลิก **Reset Token** เพื่อสร้างโทเคนบอทของคุณ คัดลอกไว้

#### เพิ่มบอทเข้าไปในเซิร์ฟเวอร์ของคุณ

1. ในแถบด้านข้าง คลิก **OAuth2 / URL Generator**
2. ภายใต้ **Scopes** ให้เปิดใช้งาน `bot` และ `applications.commands`
3. ภายใต้ **Bot Permissions** ให้เปิดใช้งาน: View Channels, Send Messages, Read Message History, Embed Links, Attach Files
4. คัดลอก URL ที่สร้างขึ้น วางลงในเบราว์เซอร์ของคุณ เลือกเซิร์ฟเวอร์ของคุณ และยืนยัน

#### รวบรวม ID ของคุณและอนุญาตให้ส่งข้อความส่วนตัว

เปิดใช้งานโหมดนักพัฒนาใน Discord (**User Settings / Advanced / Developer Mode**) จากนั้น:
- คลิกขวาที่ไอคอนเซิร์ฟเวอร์ของคุณ: **Copy Server ID**
- คลิกขวาที่อวาตาร์ของคุณเอง: **Copy User ID**

คลิกขวาที่ไอคอนเซิร์ฟเวอร์ของคุณ / **Privacy Settings** / เปิดใช้งาน **Direct Messages** ซึ่งจำเป็นสำหรับขั้นตอนการจับคู่

#### กำหนดค่า Hermes สำหรับ Discord

เพิ่มสิ่งต่อไปนี้ลงใน `~/.hermes/.env`:

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-discord-user-id
```

จากนั้นเริ่มเกตเวย์:

```bash
hermes gateway
```

บอทควรจะออนไลน์บน Discord ภายในไม่กี่วินาที ส่งข้อความถึงมัน ไม่ว่าจะเป็นข้อความส่วนตัวหรือในช่องทางที่มันมองเห็นได้

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### สร้างบอท Telegram

1. เปิด Telegram และส่งข้อความถึง **@BotFather**
2. ส่ง `/newbot` และทำตามคำแนะนำ บันทึกโทเคนบอทที่ได้รับ

#### กำหนดค่า Hermes สำหรับ Telegram

เพิ่มสิ่งต่อไปนี้ลงใน `~/.hermes/.env`:

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **ไม่ทราบ ID ผู้ใช้ Telegram ของคุณใช่ไหม?** ส่งข้อความถึง [@userinfobot](https://t.me/userinfobot) ใน Telegram ซึ่งจะตอบกลับด้วย ID ตัวเลขของคุณ

จากนั้นเริ่มเกตเวย์:

```bash
hermes gateway
```

ส่งข้อความใด ๆ ถึงบอทของคุณใน Telegram เพื่อทดสอบ ตอนนี้คุณสามารถแชทกับ agent ของคุณผ่านข้อความส่วนตัวใน Telegram ได้แล้ว ดู [คู่มือการตั้งค่า Telegram ฉบับเต็ม](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) สำหรับโหมด webhook และตัวเลือกขั้นสูง

---

## ขั้นตอนถัดไป

ตอนนี้ agent ของคุณสามารถรับคำสั่งจากโทรศัพท์และดำเนินการบนเครื่องของคุณได้แล้ว ต่อไปนี้คือสามแนวทางที่น่าสำรวจเพิ่มเติม:

1. **สรุปผลการวิจัยอัตโนมัติ**: ตั้งเวลาให้ Hermes ค้นหาข้อมูลบนเว็บเกี่ยวกับหัวข้อที่คุณสนใจในทุกเช้า สรุปผลที่พบด้วยโมเดลโลคัลของคุณ และส่งสรุปไปยังโทรศัพท์ของคุณผ่าน Telegram หรือ Discord ทั้งหมดนี้ทำงานบนฮาร์ดแวร์ของคุณเองโดยไม่มีค่าใช้จ่ายคลาวด์

2. **การตรวจสอบโค้ดตามความต้องการ**: ชี้ Hermes ไปยังรีโพซิทอรี GitHub ขอให้ตรวจสอบ pull request ที่เปิดอยู่ และให้มันโพสต์ความคิดเห็นหรือสรุปกลับไปยังแชทของคุณ ด้วย backend เทอร์มินัลของ Docker การดำเนินการ git ทั้งหมดจะทำงานภายในแซนด์บ็อกซ์ ทำให้โฮสต์ของคุณสะอาด

3. **ผู้ช่วยไฟล์โลคัล**: ให้ Hermes เข้าถึงไดเรกทอรีการทำงาน และขอให้จัดระเบียบ เปลี่ยนชื่อ สรุป หรือแปลงไฟล์ตามความต้องการจากโทรศัพท์ของคุณ เนื่องจาก backend เทอร์มินัลของ Docker จำกัดการเขียนทั้งหมดไว้ในพื้นที่ทำงานของแซนด์บ็อกซ์ การดำเนินการที่สร้างความเสียหายโดยไม่ได้ตั้งใจจึงถูกจำกัดขอบเขตไว้