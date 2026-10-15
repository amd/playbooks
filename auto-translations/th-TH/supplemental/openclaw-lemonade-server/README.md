<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **การแปลด้วยเครื่อง.** หน้านี้ได้รับการแปลโดยอัตโนมัติจากภาษาอังกฤษ และยังไม่ได้รับการตรวจสอบโดยมนุษย์ อาจมีข้อผิดพลาด และคำแนะนำ คำสั่ง การดาวน์โหลด ความพร้อมใช้งานของผลิตภัณฑ์ หรือเนื้อหาอื่นๆ บางส่วนอาจแตกต่างกันไปตามภาษาหรือภูมิภาค ในกรณีที่มีความไม่สอดคล้องหรือความคลาดเคลื่อนใดๆ ให้ถือว่าเวอร์ชันภาษาอังกฤษต้นฉบับของ playbook เป็นฉบับที่มีผลบังคับใช้และมีอำนาจเหนือกว่า
<!-- auto-translated-disclaimer:end -->

# Run OpenClaw with Lemonade Server as the backend

## ภาพรวม

[**OpenClaw**](https://openclaw.ai/) คือเอเจนต์ AI อัตโนมัติที่สามารถเขียนและรันโค้ด จัดการไฟล์ และดำเนินงานที่ซับซ้อนหลายขั้นตอนแทนคุณได้ ต่างจากผู้ช่วยแชทที่เพียงแค่ตอบคำถาม OpenClaw ดำเนินการจริงบนระบบของคุณ ซึ่งหมายความว่ามันต้องการแบ็กเอนด์ AI ที่รวดเร็วและมีความสามารถเพียงพอที่จะรองรับลูปการทำงานของเอเจนต์ที่มีความต้องการสูงได้

[**Lemonade Server**](https://lemonade-server.ai/) คือแบ็กเอนด์นั้น มันเป็นเซิร์ฟเวอร์อนุมาน (inference server) แบบโลคัลแบบโอเพนซอร์สที่รันโมเดล GenAI โดยตรงบนฮาร์ดแวร์ของคุณ และเปิดให้เข้าถึงผ่าน OpenAI API ซึ่งเป็นมาตรฐานในอุตสาหกรรม

เมื่อทำงานร่วมกัน ทั้งสองจะก่อตัวเป็นสแต็ก AI เอเจนต์แบบโลคัลอย่างสมบูรณ์ นั่นคือ Lemonade จัดการการอนุมานโมเดล ในขณะที่ OpenClaw ให้ลูปของเอเจนต์ที่แปลงผลลัพธ์จากโมเดลให้กลายเป็นการกระทำจริง

> **ก่อนที่คุณจะดำเนินการต่อ:** OpenClaw เป็นเอเจนต์ AI ที่มีความเป็นอิสระสูง การให้เอเจนต์ AI ใดๆ เข้าถึงระบบของคุณอาจส่งผลให้เกิดผลลัพธ์ที่ไม่สามารถคาดเดาได้หรือไม่ได้ตั้งใจ โปรดดำเนินการต่อก็ต่อเมื่อคุณเข้าใจความเสี่ยงและรู้สึกสบายใจกับซอฟต์แวร์อัตโนมัติที่ทำงานแทนคุณ

---

## สิ่งที่คุณจะได้เรียนรู้

เมื่อจบคู่มือนี้แล้ว คุณจะสามารถ:

- เรียนรู้เกี่ยวกับ **Lemonade Server**
- **ติดตั้ง OpenClaw** และ **ชี้ให้มันใช้ Lemonade Server** เป็นแบ็กเอนด์ AI
- **เริ่มการทำงานของ OpenClaw gateway** และยืนยันว่าเอเจนต์ของคุณพร้อมทำงานแล้ว
- **เชื่อมต่อช่องทางการสื่อสาร** (Discord หรือ Telegram) เพื่อให้คุณสามารถแชทกับเอเจนต์ของคุณได้จากอุปกรณ์ใดก็ได้

---

<!-- @device:halo_box,halo,stx,krk -->
## การตั้งค่าคอนฟิกหน่วยความจำ

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งซอฟต์แวร์ที่จำเป็น

<!-- @os:linux -->
- พีซีที่รัน **Ubuntu 24.04+** หรือดิสทริบิวชัน Linux ที่ใช้ Debian เป็นฐานที่เข้ากันได้ พร้อม `apt-get`
- แรม (RAM) อย่างน้อย **12 GB** (แนะนำ 64 GB ขึ้นไปสำหรับโมเดลขนาดใหญ่)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (ไม่บังคับ สำหรับการแซนด์บ็อกซ์ OpenClaw)
- พื้นที่ดิสก์ว่าง **ประมาณ 10–30 GB** สำหรับน้ำหนักโมเดล
<!-- @os:end -->

<!-- @os:windows -->
- พีซีที่รัน **Windows 10/11**
- แรม (RAM) อย่างน้อย **12 GB** (แนะนำ 64 GB ขึ้นไปสำหรับโมเดลขนาดใหญ่)
- พื้นที่ดิสก์ว่าง **ประมาณ 10–30 GB** สำหรับน้ำหนักโมเดล
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (ไม่บังคับ สำหรับการแซนด์บ็อกซ์ OpenClaw)
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

โมเดลที่แนะนำสำหรับคู่มือนี้คือ **Qwen3.6-35B-A3B-GGUF** จาก Unsloth ซึ่งเป็นโมเดล MoE ที่มีประสิทธิภาพสูง มีหน้าต่างบริบท (context window) ขนาด 263,000 โทเคน ซึ่งเหมาะสมอย่างยิ่งกับงานของเอเจนต์ โมเดลนี้ใช้การควอนไทซ์แบบ UD-Q4_K_XL ดึงมาได้เลยตอนนี้:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

จากนั้นโหลดด้วยหน้าต่างบริบทขนาดใหญ่ และบันทึกการตั้งค่านั้นไว้ใช้ในการรันครั้งต่อๆ ไป:

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

โมเดลนี้มีความยาวบริบทเริ่มต้นอยู่ที่ 262,144 โทเคน หากคุณพบข้อผิดพลาดหน่วยความจำไม่เพียงพอ (OOM) ให้พิจารณาลดขนาดหน้าต่างบริบทลง อย่างไรก็ตาม เนื่องจาก Qwen3.6 ใช้ประโยชน์จากบริบทที่ขยายออกไปสำหรับงานที่ซับซ้อน เราจึงแนะนำให้คงความยาวบริบทไว้อย่างน้อย 128K โทเคน เพื่อรักษาความสามารถในการคิด (thinking)

> **เคล็ดลับ: ปิดโหมดการคิดเพื่อให้เอเจนต์ตอบสนองเร็วขึ้น:** Qwen3.6-35B-A3B ทำงานในโหมดการคิด (thinking mode) เป็นค่าเริ่มต้น ซึ่งเพิ่มความหน่วงก่อนการตอบสนองแต่ละครั้ง สำหรับลูปของเอเจนต์แล้ว โอเวอร์เฮดนี้จะสะสมขึ้นอย่างรวดเร็ว รีโพซิทอรี [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) มีคอนฟิกสำเร็จรูปที่ปิดการคิดไว้ให้ วิธีใช้งานคือดาวน์โหลดไฟล์แล้วนำเข้า:
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

เราจะรัน OpenClaw ภายใน WSL (แนะนำ) และเชื่อมต่อเข้ากับ Lemonade ที่รันบน Windows โดยตรง วิธีนี้จะทำให้คุณได้สภาพแวดล้อมเชลล์แบบ Linux สำหรับ OpenClaw ในขณะที่ยังคงการเร่งความเร็วด้วย GPU ของ Lemonade ไว้ที่ฝั่ง Windows

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

ออกจาก WSL แล้วเริ่มใหม่:

```powershell
exit
wsl --shutdown
wsl
```

### เชื่อมต่อ Lemonade จาก Windows เข้าสู่ WSL

WSL2 ทำงานอยู่ในเครือข่ายเสมือน Lemonade บน Windows จะผูกไว้กับ `127.0.0.1` ซึ่ง WSL ไม่สามารถเข้าถึงได้โดยตรง พร็อกซีพอร์ตของ Windows จะส่งต่อทราฟฟิกจาก IP เกตเวย์ของ WSL ไปยัง localhost ของ Windows

**ค้นหา IP เกตเวย์ของ WSL** (รันภายใน WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**เพิ่มพร็อกซีพอร์ต** (รันใน PowerShell ในฐานะผู้ดูแลระบบ โดยแทนที่ `<WSL-Gateway-IP>` ด้วย IP เกตเวย์ของ WSL ของคุณ):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> หมายเหตุ: หากคุณพบข้อผิดพลาด `netsh: command not found` โปรดลองใช้ชื่อไฟล์ปฏิบัติการแบบชัดเจนแทน - `netsh.exe`

**เพิ่มกฎไฟร์วอลล์** (ใช้ PowerShell ที่ยกระดับสิทธิ์เดิม):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**ตรวจสอบจาก WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

หากคุณโหลดโมเดล Qwen3.6-35B-A3B-GGUF ในขั้นตอนก่อนหน้านี้ไปแล้ว คุณควรเห็นผลลัพธ์ JSON แบบนี้:

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

#### รักษาให้บริดจ์ทำงานต่อได้หลังรีสตาร์ท

กฎ `netsh portproxy` จะยังคงอยู่หลังรีบูตเครื่อง แต่ IP ของเกตเวย์ WSL อาจเปลี่ยนแปลงได้หลังจากรัน `wsl --shutdown` หรือรีบูตเครื่อง เมื่อเกิดเหตุการณ์นี้ พร็อกซียังคงชี้ไปที่ IP เดิม ทำให้ Lemonade ไม่สามารถเข้าถึงได้จาก WSL หากเกิดกรณีนี้ขึ้น ให้ใช้หนึ่งในตัวเลือกด้านล่าง

**ตัวเลือกที่ 1 (แนะนำ) — ซ่อมแซมบริดจ์โดยอัตโนมัติ** เพื่อหลีกเลี่ยงการทำสิ่งนี้ด้วยตนเองทุกครั้ง ให้ใช้ scheduled task ที่ตรวจสอบบริดจ์ทุกครั้งที่เริ่มระบบและเข้าสู่ระบบ และสร้างใหม่เฉพาะเมื่อ IP ของเกตเวย์เปลี่ยนแปลง ดูที่ [คู่มือการซ่อมแซมบริดจ์ WSL ของ Lemonade โดยอัตโนมัติ](assets/RepairLemonadeWslBridge.md)


**ตัวเลือกที่ 2 — ซ่อมแซมบริดจ์ด้วยตนเอง** ก่อนอื่น ให้ดึงค่า IP ของเกตเวย์ WSL ปัจจุบันโดยรันคำสั่งนี้ภายใน WSL:

```bash
ip route show default | awk '{print $3}' | head -1
```

คัดลอกค่านี้ไว้ คุณจะใช้แทนที่ `<new-WSL-Gateway-IP>` ด้านล่าง

จากนั้น ใน **PowerShell แบบยกระดับสิทธิ์** (เรียกใช้ในฐานะผู้ดูแลระบบ) ให้แสดงรายการกฎที่มีอยู่ ลบเฉพาะกฎ Lemonade ที่ล้าสมัย และเพิ่มกฎใหม่ด้วย IP ปัจจุบัน:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

ในผลลัพธ์ของ `show all` กฎ Lemonade ที่ล้าสมัยคือรายการที่มีที่อยู่การเชื่อมต่อเป็น `127.0.0.1` บนพอร์ต `13305` โดยที่อยู่การรับฟังคือ `<old-WSL-Gateway-IP>` ของคุณ การลบตามที่อยู่นี้จะลบเฉพาะกฎนี้เท่านั้น และไม่กระทบต่อกฎ port-proxy อื่น ๆ บนเครื่องของคุณ

กฎไฟร์วอลล์ที่คุณเพิ่มระหว่างการตั้งค่าถูกผูกไว้กับพอร์ต `13305` (ไม่ใช่ IP) ดังนั้นมันจึงยังคงทำงานได้ และไม่จำเป็นต้องสร้างใหม่

> **ข้อแนะนำ:** เพื่อหลีกเลี่ยงปัญหาเกี่ยวกับเกตเวย์ เราขอแนะนำอย่างยิ่งให้ใช้การกำหนดค่าเชลล์ดังต่อไปนี้:
> - **คำสั่งของ Windows** ควรถูกรันใน **PowerShell**
> - **คำสั่งของ WSL distro** ควรถูกรันใน **Command Prompt** (รันในฐานะ **ผู้ดูแลระบบ**)

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

แฟล็ก `--no-onboard` จะข้ามตัวช่วยตั้งค่าแบบโต้ตอบ คุณจะกำหนดค่าโมเดลแบ็กเอนด์ด้วยตนเองในขั้นตอนถัดไป ซึ่งจะให้คุณควบคุมได้อย่างแม่นยำว่าจะใช้โมเดลและเซิร์ฟเวอร์ใด

เปิดเทอร์มินัลใหม่และยืนยันการติดตั้ง:

```bash
openclaw --version
```

> **เคล็ดลับ:** หากคุณเห็น `command not found` หลังการติดตั้ง ให้เพิ่มไดเรกทอรี global bin ของ npm เข้าไปใน PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> เพื่อทำให้การตั้งค่านี้ถาวร ให้เพิ่มบรรทัดด้านบนลงในไฟล์ `~/.bashrc` หรือ `~/.zshrc` ของคุณ

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

รันการตั้งค่าเริ่มต้นแบบไม่โต้ตอบของ OpenClaw
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

> **การกำหนดขนาดหน้าต่างบริบทของ OpenClaw:** การบีบอัด (compaction) ของ OpenClaw จะเริ่มทำงานเมื่อ `contextTokens > contextWindow − reserveTokens` ค่าเริ่มต้นของ `reserveTokensFloor` คือ 20,000 โทเคน ซึ่งเป็นค่าขั้นต่ำที่จะแทนที่ `reserveTokens` เมื่อมีค่าต่ำกว่า ดังนั้นบริบทของโมเดลใด ๆ ที่ต่ำกว่าประมาณ 37,000 โทเคนจะทำให้เกิดวงจรการบีบอัดไม่รู้จบ ให้ตั้งค่าการสำรอง (reserve) ให้ต่ำและปิดใช้งานค่าขั้นต่ำเพียงครั้งเดียวในการกำหนดค่าของคุณ แล้วมันจะมีผลกับทุกโมเดล โดยไม่ต้องปรับแต่งทีละโมเดล:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` เป็น *ค่าขั้นต่ำ* (ตัวป้องกัน) ไม่ใช่ตัวค่าสำรองเอง การตั้งค่าเฉพาะค่าขั้นต่ำนั้นไม่มีผลใด ๆ การตั้งค่า `reserveTokensFloor: 0` จะปิดใช้งานตัวป้องกันนี้ ทำให้ค่า `reserveTokens` ที่ต่ำกว่าถูกยอมรับได้
>
> **เมื่อใดควรใช้การตั้งค่านี้:** ใช้การกำหนดค่านี้หากหน้าต่างบริบทที่ใช้งานได้จริงของโมเดลของคุณต่ำกว่าประมาณ 37,000 โทเคน ไม่ว่าจะเป็นเพราะโมเดลมีขนาดเล็ก (เช่น 8k, 16k, 32k) หรือเพราะคุณได้จำกัดค่าไว้ที่ระดับต่ำกว่าโดยตั้งใจ (เช่น โหลดโมเดล 128k แต่ตั้งค่าบริบทเป็น 16k ใน Lemonade) หากไม่ตั้งค่านี้ OpenClaw จะเข้าสู่วงจรการบีบอัดไม่รู้จบเมื่อเริ่มทำงาน
>
> **โมเดลที่มีบริบทขนาดใหญ่ที่ใช้บริบทเต็ม:** คุณสามารถข้ามขั้นตอนนี้ไปได้เลย ค่าเริ่มต้นทำงานได้ดีอยู่แล้ว การบีบอัดจะเริ่มทำงานก่อนที่หน้าต่างจะเต็ม และโมเดลยังมีพื้นที่เพียงพอในการสร้างคำตอบยาว ๆ หากคุณยังเลือกที่จะใช้การตั้งค่านี้ โปรดทราบว่า `reserveTokens: 4096` จะจำกัดความยาวของคำตอบไว้ที่ประมาณ 4,000 โทเคน ซึ่งอาจตัดการสร้างไฟล์ยาว ๆ หรือแผนงานที่ละเอียดให้ขาดหายไป
>
> **ควรเพิ่มการตั้งค่านี้ไว้ที่ใด:** วางบล็อก `compaction` ไว้ภายใน `agents.defaults` ในไฟล์ `openclaw.json` ของคุณ (โดยปกติจะอยู่ที่ `~/.openclaw/openclaw.json`):
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
> ส่วนที่เหลือของการกำหนดค่าของคุณ (gateway, channels, models เป็นต้น) จะยังคงเหมือนเดิม โดยต้องเพิ่มเฉพาะคีย์ `compaction` เท่านั้น
### (แนะนำ) เปิดใช้งาน Docker Sandboxing

OpenClaw สามารถส่งการดำเนินการไฟล์และโค้ดของ agent ทั้งหมดผ่านคอนเทนเนอร์ Docker ที่แยกออกจากกัน แทนที่จะรันโดยตรงบนโฮสต์ของคุณ วิธีนี้จะจำกัดขอบเขตความเสียหายของการดำเนินการที่ไม่ได้ตั้งใจให้อยู่แค่ภายใน sandbox โดยไม่กระทบต่อระบบไฟล์และเครือข่ายของโฮสต์ของคุณ

สร้าง sandbox image ครั้งเดียว (ต้องติดตั้ง Docker ไว้ก่อน):

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

# Docker Desktop injects its WSL cli-tools a few seconds after the distro boots.
for i in $(seq 1 30); do
  docker version >/dev/null 2>&1 && break
  sleep 2
done
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

รันคำสั่งนี้เพื่อเพิ่มคีย์ `sandbox` ไว้ภายในบล็อก `agents.defaults` ที่มีอยู่แล้วใน `~/.openclaw/openclaw.json`:

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

คอนเทนเนอร์ sandbox จะ**ไม่มีการเข้าถึงเครือข่าย**ตามค่าเริ่มต้น ดูรายละเอียดเพิ่มเติมเกี่ยวกับ bind mount และการปรับแต่งเครือข่ายได้ที่ [sandboxing reference](https://docs.openclaw.ai/gateway/sandboxing)

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
> **ขั้นตอนที่ 2: หากยังพบข้อผิดพลาดอยู่ ให้แก้ไขแบบถาวร**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> จากนั้น **รีบูต** ระบบของคุณ
> 
> **วิธีแก้ไขชั่วคราวแบบเร็ว** (จะรีเซ็ตหลังรีบูต):
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

[Firecrawl](https://docs.firecrawl.dev/introduction) เป็นบริการรวบรวมและดึงข้อมูลเว็บแบบโฮสต์เอง (self-hosted) ที่สามารถหลีกเลี่ยงข้อจำกัดเหล่านี้และปลดล็อกศักยภาพเต็มที่ของระบบอัตโนมัติของ OpenClaw

ในการตั้งค่านี้ OpenClaw ทำงานเป็นชุดคอนเทนเนอร์ Docker ที่จัดการด้วย Podman เพื่อให้การจัดการวงจรชีวิตและการเริ่มต้นทำงานอัตโนมัติเป็นเรื่องง่าย เราจึงลงทะเบียน Firecrawl เป็นบริการ `systemd` ระดับผู้ใช้ ซึ่งจะควบคุมชุด Podman Compose ที่อยู่เบื้องหลัง วิธีนี้ทำให้ OpenClaw สามารถเริ่มต้น gateway หยุด และตรวจสอบบริการ Firecrawl โดยใช้คำสั่ง `systemctl --user` มาตรฐาน แทนที่จะต้องโต้ตอบกับคอนเทนเนอร์โดยตรง

เพื่อให้เข้าใจง่าย เราได้แบ่งกระบวนการทั้งหมดออกเป็นสี่ขั้นตอน:

---

### 1. ลงทะเบียนบริการระบบ
ไปยังไดเรกทอรีการตั้งค่า systemd ระดับผู้ใช้:
```bash
cd ~/.config/systemd/user
```
สร้างและเปิดไฟล์ใหม่ชื่อ `firecrawl.service`
```bash
nano firecrawl.service
```
คัดลอกและวางการตั้งค่าต่อไปนี้:
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
ณ จุดนี้ บริการได้ถูกกำหนดไว้แล้วแต่ยังไม่ได้ลงทะเบียนกับ `systemd`
ตรวจสอบให้แน่ใจว่าชื่อไฟล์ตรงกับที่คุณสร้างไว้ข้างต้นทุกประการ จากนั้นรัน:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
หากสำเร็จ คุณควรเห็นผลลัพธ์ดังนี้:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` มี symbolic link ไปยังบริการที่ตั้งค่าให้เริ่มทำงานโดยอัตโนมัติ

### 2. ตั้งค่า Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) เหมาะสำหรับผู้ที่ต้องการควบคุมสภาพแวดล้อมการดึงข้อมูลและประมวลผลข้อมูลได้อย่างเต็มที่ แต่ก็ต้องแลกมาด้วยความพยายามในการดูแลรักษาและตั้งค่าเพิ่มเติม

เริ่มต้นด้วยการโคลนรีพอสิทอรี:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
สร้างไฟล์ `.env` ในไดเรกทอรี `/firecrawl`: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. ปรับใช้ OpenClaw ด้วย Podman Compose

ก่อนดำเนินการต่อ ตรวจสอบให้แน่ใจว่าคุณได้ดึง OpenClaw Docker image เวอร์ชันล่าสุดมาแล้ว:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
เมื่อดำเนินการเสร็จแล้ว ให้ดาวน์โหลดไฟล์ OpenClaw Compose [openclaw-compose.yaml](assets/openclaw-compose.yaml) และวางไว้ในไดเรกทอรีราก `/firecrawl`:

> ธรรมเนียมนี้จำเป็นเพื่อให้ `systemd` สามารถค้นหาและเริ่มต้นบริการได้อย่างถูกต้องตามที่ระบุไว้ใน `WorkingDirectory=${HOME}/firecrawl`

> คุณสามารถขยายชุดบริการได้เสมอโดยการเพิ่มบริการ Firecrawl เพิ่มเติมตามต้องการ รายการบริการทั้งหมดที่มีสามารถดูได้จาก [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) ฉบับทางการ

### 4. เปิดใช้งานบริการ OpenClaw ผ่าน Firecrawl 

ก่อนที่จะส่งมอบการควบคุมให้ `systemd` ให้ตรวจสอบว่าทุกอย่างทำงานถูกต้องโดยการรันชุดบริการด้วยตนเอง:
```bash
podman compose -f openclaw-compose.yaml up -d
```
หากทุกอย่างถูกตั้งค่าอย่างถูกต้อง คุณควรเห็นคอนเทนเนอร์ OpenClaw เริ่มทำงาน และผลลัพธ์ในบรรทัดคำสั่งของคุณควรมีลักษณะคล้ายกับนี้:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

เมื่อยืนยันแล้ว ให้นำชุดบริการกลับมาปิดก่อนดำเนินการต่อ:
```bash
podman compose -f openclaw-compose.yaml down
```
ก่อนเริ่มต้นบริการ คุณต้องตรวจสอบให้แน่ใจว่ามีการตั้งค่าความเป็นเจ้าของและสิทธิ์ที่ถูกต้องบนไดเรกทอรี `firecrawl` และไฟล์ `.env` ของมัน
ซึ่งเป็นสิ่งจำเป็นเพื่อให้บริการสามารถเขียนข้อมูลรับรองของคุณได้ในขณะเริ่มทำงาน
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
เมื่อทุกอย่างได้รับการตรวจสอบแล้ว ให้เริ่มบริการผ่าน `systemd`:
```bash
systemctl --user start firecrawl.service
```
[The OpenClaw Actions](https://docs.openclaw.ai/) สามารถเข้าถึงได้จากภายในคอนเทนเนอร์เชิงโต้ตอบ และ Web Dashboard จะพร้อมใช้งานบนโฮสต์และพอร์ตเดียวกันที่ http://127.0.0.1:18789
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### การรับ `OPENCLAW_GATEWAY_TOKEN` ของคุณ

เมื่อบริการเริ่มทำงานแล้ว คุณจะสังเกตเห็นไดเรกทอรี `.openclaw` ใหม่ถูกสร้างขึ้นในโฟลเดอร์โฮมของคุณ (~/.openclaw) ไดเรกทอรีนี้จะถูกล็อกไว้ตามค่าเริ่มต้น ดังนั้นคุณจึงต้องปลดล็อกเพื่อดึง gateway token ของคุณออกมา

1. ให้สิทธิ์การเข้าถึงไดเรกทอรี:
```bash
sudo chmod 777 ~/.openclaw/
```
2. อ่าน gateway token ของคุณ:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
ค้นหาค่า `OPENCLAW_GATEWAY_TOKEN` ในผลลัพธ์

3. เปิด gateway dashboard ในเบราว์เซอร์ของคุณที่ http://127.0.0.1:18789 วางโทเค็นของคุณเมื่อมีการร้องขอเพื่อยืนยันตัวตน

หากต้องการหยุดบริการ ให้รัน:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## เริ่มต้น OpenClaw Gateway

Gateway คือโปรเซส OpenClaw ที่จัดการ agent loop และให้บริการแดชบอร์ด:

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

เนื่องจาก gateway ผูกกับ loopback แดชบอร์ดจะพิสูจน์ตัวตนโดยอัตโนมัติเมื่อเปิดจากเครื่องเดียวกัน ไม่จำเป็นต้องกรอกโทเค็นหรืออนุมัติอุปกรณ์สำหรับการเข้าถึงในเครื่อง คุณควรเห็นแดชบอร์ด OpenClaw พร้อมโมเดล Lemonade ของคุณที่แสดงเป็นแบ็กเอนด์ที่ใช้งานอยู่

> หากคุณเปิดใช้งาน sandboxing แล้ว คุณสามารถตรวจสอบได้โดยขอให้ agent `run hostname` จากแดชบอร์ด หากคุณเห็น container ID สั้น ๆ แทนที่จะเป็น hostname ของเครื่องคุณ แสดงว่า sandbox ทำงานได้ถูกต้อง

**ยินดีด้วย คุณได้สร้าง AI agent stack แบบโลคัลทั้งหมดตั้งแต่ต้นเรียบร้อยแล้ว**

> **ต้องการโทเค็นของ gateway หรือไม่?** รันคำสั่ง `openclaw dashboard --no-open` เพื่อพิมพ์ URL ของแดชบอร์ดพร้อมฝังโทเค็นไว้ (คำสั่งนี้จะพยายามคัดลอกไปยังคลิปบอร์ดของคุณด้วย) หรืออีกทางหนึ่ง โทเค็นจะอยู่ที่ `gateway.auth.token` ใน `~/.openclaw/openclaw.json`

**การเข้าถึงแดชบอร์ดจากอุปกรณ์อื่น (ผ่าน SSH Tunnel)**

หาก OpenClaw ทำงานอยู่บนเครื่องระยะไกล คุณสามารถเข้าถึงแดชบอร์ดของมันจากเครื่องโลคัลของคุณผ่าน SSH tunnel ได้ tunnel จะส่งต่อพอร์ตของ gateway (`18789`) เพื่อให้เบราว์เซอร์โลคัลของคุณสามารถสื่อสารกับ gateway ระยะไกลผ่าน `127.0.0.1`

1. จาก **เครื่องโลคัล** ของคุณ ให้เชื่อมต่อกับเครื่องระยะไกลหนึ่งครั้งและยอมรับ prompt fingerprint เพื่อให้โฮสต์ถูกเพิ่มลงใน known hosts ของคุณ:

   ```bash
   ssh user@<host-ip>
   ```

2. บน **เครื่องโลคัล** ของคุณเช่นเดิม ให้เปิด SSH tunnel:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **หมายเหตุ:** หลังจากคุณใส่รหัสผ่าน เทอร์มินัลจะไม่แสดงผลลัพธ์ใด ๆ และดูเหมือนค้าง นี่เป็นเรื่องปกติ: แฟล็ก `-N` บอกให้ SSH ไม่รันคำสั่งระยะไกลใด ๆ ดังนั้นมันจึงเพียงแค่คง tunnel ให้เปิดอยู่ ปล่อยให้เทอร์มินัลนี้ทำงานต่อไป

3. บน **เครื่องโลคัล** ของคุณ เปิดเบราว์เซอร์และไปที่ `http://127.0.0.1:18789`

4. บน **เครื่องระยะไกล** ให้พิมพ์โทเค็นของ gateway และวางลงในเบราว์เซอร์เพื่อล็อกอิน:

   ```bash
   openclaw dashboard --no-open
   ```

   คำสั่งนี้จะพิมพ์ URL ของแดชบอร์ดพร้อมฝังโทเค็นไว้ ให้คัดลอกโทเค็นเพื่อล็อกอิน (โทเค็นยังถูกเก็บไว้ที่ `gateway.auth.token` ใน `~/.openclaw/openclaw.json` ด้วย)

> **การอนุมัติอุปกรณ์ระยะไกล:** เมื่อคุณเปิดแดชบอร์ดจากเครื่องอื่นหรือโทรศัพท์ เบราว์เซอร์อาจแสดง request ID บน **เครื่องระยะไกล** ให้แสดงรายการคำขอที่รอดำเนินการ:
> ```bash
> openclaw devices list
> ```
> จากนั้นอนุมัติคำขอที่ตรงกัน:
> ```bash
> openclaw devices approve <requestId>
> ```
> ขั้นตอนนี้จำเป็นเฉพาะสำหรับอุปกรณ์ระยะไกลหรืออุปกรณ์รอง เท่านั้น การเข้าถึงผ่าน loopback จากเครื่องเดียวกันจะพิสูจน์ตัวตนโดยอัตโนมัติ ดูรายละเอียดเพิ่มเติมได้ที่เอกสาร [Remote Access](https://docs.openclaw.ai/gateway/remote)

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## ทางเลือกเสริม: เชื่อมต่อช่องทางการสื่อสาร

เมื่อ gateway ทำงานแล้ว คุณสามารถเข้าถึง agent โลคัลของคุณจากอุปกรณ์ใดก็ได้ เลือกตัวเลือกที่เหมาะกับการตั้งค่าของคุณ OpenClaw รองรับ [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) และช่องทางอื่น ๆ ดูรายการทั้งหมดได้ที่ [docs.openclaw.ai](https://docs.openclaw.ai)

---

### ทางเลือก A: Discord

Discord จำเป็นต้องมีเซิร์ฟเวอร์ที่**คุณมีสิทธิ์ผู้ดูแลระบบ (administrator)** เพื่อเพิ่มบอท หากคุณมีเซิร์ฟเวอร์ร่วมกับผู้อื่นแต่ไม่ได้เป็นเจ้าของ ให้ใช้ทางเลือก B (Telegram) แทน

#### สร้างบัญชีและเซิร์ฟเวอร์ Discord

หากคุณยังไม่มีบัญชี Discord ให้สมัครสมาชิกที่ [discord.com](https://discord.com) คุณยังต้องมีเซิร์ฟเวอร์ที่คุณเป็นผู้ดูแลระบบ สร้างหนึ่งเซิร์ฟเวอร์โดยคลิกไอคอน **+** ใน sidebar ของ Discord แล้วเลือก **Create My Own** เซิร์ฟเวอร์ส่วนตัวก็ใช้ได้

#### สร้างแอปพลิเคชันและบอท Discord

1. ไปที่ [Discord Developer Portal](https://discord.com/developers/applications) และคลิก **New Application** ตั้งชื่อ (เช่น "openclaw-bot")
2. ใน sidebar คลิก **Bot** ตั้งชื่อผู้ใช้สำหรับบอท
3. ยังคงอยู่ที่หน้า Bot เลื่อนลงไปที่ **Privileged Gateway Intents** และเปิดใช้งาน:
   - **Message Content Intent** (จำเป็น)
   - **Server Members Intent** (แนะนำ)
4. เลื่อนกลับขึ้นไปด้านบนและคลิก **Reset Token** เพื่อสร้างโทเค็นบอทของคุณ คัดลอกไว้

#### เพิ่มบอทเข้าสู่เซิร์ฟเวอร์ของคุณ

1. ใน sidebar คลิก **OAuth2/ URL Generator**
2. ภายใต้ **Scopes** เปิดใช้งาน `bot` และ `applications.commands`
3. ภายใต้ **Bot Permissions** เปิดใช้งาน: View Channels, Send Messages, Read Message History, Embed Links, Attach Files
4. คัดลอก URL ที่สร้างขึ้น วางลงในเบราว์เซอร์ของคุณ เลือกเซิร์ฟเวอร์ของคุณ และยืนยัน บอทควรปรากฏในรายชื่อสมาชิกของเซิร์ฟเวอร์ของคุณแล้ว

#### รวบรวม ID ของคุณ

เปิดใช้งาน Developer Mode ใน Discord (**User Settings/ Advanced/ Developer Mode**) จากนั้น:
- คลิกขวาที่ไอคอนเซิร์ฟเวอร์ของคุณ: **Copy Server ID**
- คลิกขวาที่อวาตาร์ของคุณเอง: **Copy User ID**

#### อนุญาตให้สมาชิกในเซิร์ฟเวอร์ส่งข้อความส่วนตัว (DM)

คลิกขวาที่ไอคอนเซิร์ฟเวอร์ของคุณ/ **Privacy Settings**/ เปิดสวิตช์ **Direct Messages** วิธีนี้จะทำให้บอทสามารถส่งข้อความส่วนตัวถึงคุณได้ ซึ่งจำเป็นสำหรับขั้นตอนการจับคู่ (pairing)

#### กำหนดค่า OpenClaw สำหรับ Discord

เก็บโทเค็นบอทของคุณเป็นตัวแปรสภาพแวดล้อม จากนั้นสร้างไฟล์ patch เดียวที่เปิดใช้งาน Discord อ้างอิงโทเค็น และอนุญาต allowlist เซิร์ฟเวอร์ของคุณ แทนที่ `<server_id>` และ `<user_id>` ด้วย ID ที่รวบรวมไว้ข้างต้น

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

> **อย่าพึ่งพาการขอให้ agent กำหนดค่านี้** เมื่อเปิดใช้งาน sandboxing agent ไม่สามารถเขียนไปยัง `~/.openclaw/openclaw.json` จากภายใน sandbox ได้ ให้ใช้คำสั่ง CLI ข้างต้นบนโฮสต์แทน

รีสตาร์ท gateway เพื่อให้รับการกำหนดค่าช่องทางใหม่:

```bash
openclaw gateway run --bind loopback --port 18789
```

คุณควรเห็น `logged in to discord as <bot-name>` ในเอาต์พุตของ gateway ภายในไม่กี่วินาที
#### จับคู่บัญชี Discord ของคุณ

DM บอทใน Discord แล้วบอทจะตอบกลับด้วยรหัสจับคู่สั้นๆ

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

อนุมัติบนเครื่องที่รัน OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> รหัสจับคู่จะหมดอายุหลังจากหนึ่งชั่วโมง

ตอนนี้คุณสามารถแชทกับเอเจนต์ของคุณโดยตรงจาก Discord และมอบหมายงานให้กับฮาร์ดแวร์ในเครื่องของคุณได้แล้ว

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### ตัวเลือก B: Telegram

Telegram ใช้งานง่ายกว่า Discord สำหรับผู้ใช้ส่วนใหญ่ ไม่ต้องใช้เซิร์ฟเวอร์และไม่ต้องมีสิทธิ์แอดมิน

#### สร้างบอท Telegram

1. เปิด Telegram แล้วส่งข้อความถึง **@BotFather**
2. ส่ง `/newbot` แล้วทำตามคำแนะนำ บันทึกโทเคนบอทที่ได้รับไว้

#### กำหนดค่า OpenClaw สำหรับ Telegram

จัดเก็บโทเคนเป็นตัวแปรสภาพแวดล้อม:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

เพิ่มการกำหนดค่าช่องทางลงใน `~/.openclaw/openclaw.json` (หรือแก้ไขผ่านแดชบอร์ด):

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

รหัสจับคู่จะหมดอายุหลังจากหนึ่งชั่วโมง ตอนนี้คุณสามารถแชทกับเอเจนต์ของคุณผ่าน DM ของ Telegram ได้แล้ว

---

## ขั้นตอนถัดไป

เมื่อเอเจนต์ของคุณสามารถรับคำสั่งจากโทรศัพท์และดำเนินการบนเครื่องในเครื่องของคุณได้แล้ว นี่คือสามแนวทางที่น่าลองศึกษาเพิ่มเติม:

1. **เครื่องมือสรุปตลาดหุ้น**: ตั้งเวลาให้ OpenClaw ดึงข้อมูลจาก API ทางการเงินตามช่วงเวลาที่กำหนด สรุปความเคลื่อนไหวในแต่ละวันด้วยโมเดลในเครื่องของคุณ และส่งบทสรุปไปยังโทรศัพท์ของคุณทุกเช้าผ่านช่องทางที่คุณเลือก

2. **เครื่องมือตรวจสอบการ fine-tuning**: เริ่มงานเทรนจากระยะไกลผ่าน Telegram หรือ Discord จากนั้นให้เอเจนต์ติดตามล็อกการเทรนและรายงานค่า loss เป็นระยะ การใช้งาน GPU และการใช้พื้นที่ดิสก์กลับไปยังโทรศัพท์ของคุณ หากการรันหยุดชะงักหรือ VRAM พุ่งสูง คุณจะทราบได้ทันทีโดยไม่ต้องอยู่ที่เครื่อง

3. **IOT ด้วย VLM ในเครื่อง**: ตั้งกล้องไว้ที่หน้าประตูบ้านของคุณ รันโมเดลวิชันบน Lemonade และให้ OpenClaw วิเคราะห์เฟรมตามคำขอหรือตามทริกเกอร์ ถามว่า "วันนี้มีพัสดุมาส่งไหม" จากโทรศัพท์ของคุณและรับคำตอบตรงๆ จากฮาร์ดแวร์ของคุณเอง

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