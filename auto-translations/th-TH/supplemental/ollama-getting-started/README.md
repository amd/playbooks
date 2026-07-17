<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## ภาพรวม

Ollama เป็นเครื่องมือขนาดเบาที่ได้รับความนิยมสำหรับการรัน large language models ในเครื่องของคุณ โดยจัดการการดาวน์โหลดโมเดล การ quantization และการให้บริการผ่านอินเทอร์เฟซบรรทัดคำสั่งและแอปเดสก์ท็อปที่เรียบง่าย ทำให้คุณสามารถเริ่มต้นสนทนากับ LLM ได้ภายในไม่กี่นาที

Playbook นี้จะแนะนำคุณตลอดขั้นตอนการติดตั้ง Ollama การดึงโมเดล GPT-OSS 20B และการสนทนากับโมเดลดังกล่าว ทั้งผ่านเทอร์มินัลและแอปเดสก์ท็อป

## สิ่งที่คุณจะได้เรียนรู้

- วิธีติดตั้งและเปิดใช้งาน Ollama บนระบบของคุณ
- ดึงและรันโมเดล GPT-OSS 20B ในเครื่อง
- สนทนากับโมเดลโดยใช้ CLI
- เรียกใช้โมเดลผ่านโปรแกรมด้วย REST API

## การตั้งค่าการกำหนดค่าหน่วยความจำ

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์
> **หมายเหตุ**: หากไม่ได้ติดตั้ง VS Code คุณสามารถติดตั้งได้ผ่าน Ryzen AI Developer Center

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งซอฟต์แวร์ที่จำเป็น

<!-- @require:driver -->

### การติดตั้ง Ollama

<!-- @os:windows -->

1. ดาวน์โหลดตัวติดตั้งจาก [ollama.com/download](https://ollama.com/download)
2. รันตัวติดตั้ง `.exe` และทำตามขั้นตอนที่แสดง
3. เมื่อติดตั้งเสร็จแล้ว Ollama จะทำงานเป็นบริการพื้นหลังและสามารถเข้าถึงได้จากเทอร์มินัล แอปเดสก์ท็อป และ system tray

ตรวจสอบการติดตั้งโดยเปิดเทอร์มินัลและรัน:

```powershell
ollama --version
```

<!-- @test:id=ollama-version-windows timeout=60 hidden=True -->
```powershell
ollama --version
```
<!-- @test:end --> 

คุณควรเห็นหมายเลขเวอร์ชันที่ติดตั้งแสดงออกมาในคอนโซล
<!-- @os:end -->

<!-- @os:linux -->

รันสคริปต์ติดตั้งอย่างเป็นทางการ:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

ตรวจสอบการติดตั้ง:

```bash
ollama --version
```

<!-- @test:id=ollama-version-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end --> 

คุณควรเห็นหมายเลขเวอร์ชันที่ติดตั้งแสดงออกมาในคอนโซล
<!-- @os:end -->

## การดึงโมเดลแรกของคุณ

Ollama จัดการโมเดลผ่าน registry ที่คล้ายกับ container images หากต้องการดาวน์โหลด GPT-OSS 20B:

```bash
ollama pull gpt-oss:20b
```

การดำเนินการนี้จะดาวน์โหลด model weights มายังเครื่องของคุณ (ประมาณ 12 GB) การดาวน์โหลดจะเกิดขึ้นเพียงครั้งเดียว และการรันครั้งต่อไปจะโหลดโมเดลจากดิสก์

คุณสามารถยืนยันว่าโมเดลพร้อมใช้งานด้วย:

```bash
ollama list
```

คุณควรเห็น `gpt-oss:20b` ในผลลัพธ์พร้อมกับขนาดและวันที่แก้ไขล่าสุด

<!-- @os:windows -->
<!-- @test:id=ollama-list-gpt-oss-20b-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"
$list = (ollama list | Out-String)
if (-not $list) { throw "ollama list returned no output" }
if ($list -notmatch 'gpt-oss:20b') { throw "Model gpt-oss:20b is not present in ollama list. Please download it before running this test." }
Write-Host "OK: gpt-oss:20b is present in ollama list"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=ollama-list-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
p=""
started_here="0"

cleanup() {
  if [ "$started_here" = "1" ] && [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

wait_for_ollama_api() {
  local attempts="${1:-120}"
  local out=""
  for i in $(seq 1 "$attempts"); do
    out="$(curl -s --max-time 2 http://127.0.0.1:11434/api/tags || true)"
    if [ -n "$out" ]; then
      echo "$out"
      return 0
    fi
    sleep 1
  done
  return 1
}

tags_json="$(wait_for_ollama_api 5 || true)"
if [ -z "$tags_json" ]; then
  ollama serve >/tmp/ollama-list-test.log 2>&1 &
  p=$!
  started_here="1"
  tags_json="$(wait_for_ollama_api 120 || true)"
fi
if [ -z "$tags_json" ]; then
  echo "Ollama API not ready on http://127.0.0.1:11434"
  exit 1
fi
echo "OK: Ollama API is responding on http://127.0.0.1:11434"

list="$(ollama list)"
if [ -z "$list" ]; then
  echo "ollama list returned no output"
  exit 1
fi
echo "$list" | grep -q 'gpt-oss:20b' || {
  echo "Model gpt-oss:20b is not present in ollama list. Please download it before running this test."
  exit 1
}
echo "OK: gpt-oss:20b is present in ollama list"
```
<!-- @test:end --> 
<!-- @os:end -->

### การตั้งชื่อโมเดล

ชื่อโมเดลของ Ollama ใช้รูปแบบ `name:tag` โดย tag มักระบุจำนวนพารามิเตอร์หรือตัวแปร quantization คำสั่งที่มีประโยชน์สำหรับการจัดการโมเดล:

| คำสั่ง | คำอธิบาย |
|---------|-------------|
| `ollama list` | แสดงโมเดลที่ดาวน์โหลดทั้งหมด |
| `ollama pull <model>` | ดาวน์โหลดโมเดลโดยไม่รัน |
| `ollama rm <model>` | ลบโมเดลเพื่อเพิ่มพื้นที่ดิสก์ |
| `ollama show <model>` | แสดง metadata และพารามิเตอร์ของโมเดล |

## การสนทนาจากเทอร์มินัล

เปิดเซสชันแชทแบบโต้ตอบโดยตรงจากบรรทัดคำสั่ง:

```bash
ollama run gpt-oss:20b
```

Ollama จะโหลดโมเดลเข้าสู่หน่วยความจำและนำคุณเข้าสู่ prompt ลองถามบางอย่าง:

```
>>> What is the capital of France and why is it historically significant?
```

โมเดลจะสตรีมการตอบสนองทีละ token โดยตรงในเทอร์มินัล พิมพ์ `/bye` หรือกด `Ctrl+D` เพื่อออกจากเซสชัน

> **เคล็ดลับ**: การรันครั้งแรกจะใช้เวลาสักครู่เพื่อโหลดโมเดลเข้าสู่หน่วยความจำ การ prompt ครั้งต่อไปภายในเซสชันเดียวกันจะตอบสนองเร็วกว่ามาก เนื่องจากโมเดลยังคงโหลดอยู่

<!-- @os:windows -->
## การสนทนาจากแอปเดสก์ท็อป

Ollama ยังมาพร้อมกับแอปพลิเคชันเดสก์ท็อปที่มีอินเทอร์เฟซแชทที่สะอาดตาสำหรับการโต้ตอบกับโมเดลของคุณ

เปิด **Ollama** จากเมนู Start หรือคลิกไอคอน Ollama ใน system tray แล้วเลือก **Open Ollama**

เมื่อแอปเปิดขึ้น:

1. คลิก **New Chat** ในแถบด้านข้าง
2. เลือก **gpt-oss:20b** จากเมนูดรอปดาวน์โมเดลที่มุมล่างขวาของพื้นที่ป้อนข้อความแชท
3. พิมพ์ข้อความและกด Enter เพื่อเริ่มสนทนา

<p align="center">
  <img src="assets/ollama_app.png" alt="Ollama desktop app chatting with gpt-oss:20b" width="600"/>
</p>

แอปเดสก์ท็อปจะเก็บประวัติการสนทนาของคุณไว้ในแถบด้านข้าง ทำให้ง่ายต่อการกลับมาดูการสนทนาก่อนหน้า
<!-- @os:end -->

## การใช้ REST API

หลังจากติดตั้งแล้ว Ollama จะทำงานเป็นบริการพื้นหลังและเปิดเผย REST API บน `http://localhost:11434` ที่คุณสามารถใช้เพื่อรวมโมเดลเข้ากับแอปพลิเคชันและสคริปต์ของคุณเอง

<!-- @os:windows -->
<!-- @test:id=ollama-smoke-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$p = $null
$startedHere = $false
$tmpShow = $null
$tmpGenerate = $null
$tmpChat = $null
$venv = "$PWD\ollama-env-ci"
$pythonSmoke = "$PWD\ollama_python_smoke.py" 

function Wait-OllamaApi {
  param( [int]$MaxAttempts = 120 )
  $resp = $null
  for ($i = 0; $i -lt $MaxAttempts; $i++) {
    $resp = curl.exe -s --max-time 2 http://127.0.0.1:11434/api/tags
    if ($LASTEXITCODE -eq 0 -and $resp) { return $resp }
    Start-Sleep -Seconds 1
  }
  return $null
}

try {
  # If Ollama API is not already up, start it.
  $tagsJson = Wait-OllamaApi -MaxAttempts 5
  if (-not $tagsJson) {
    $p = Start-Process -FilePath "ollama" -ArgumentList "serve" -NoNewWindow -PassThru
    $startedHere = $true
    $tagsJson = Wait-OllamaApi -MaxAttempts 120
  }
  if (-not $tagsJson) { throw "Ollama API not ready on http://127.0.0.1:11434" }
  Write-Host "OK: Ollama API is responding on http://127.0.0.1:11434"

  # /api/tags must include gpt-oss:20b
  $tags = $tagsJson | ConvertFrom-Json
  $model = $tags.models | Where-Object { $_.name -eq "gpt-oss:20b" } | Select-Object -First 1
  if (-not $model) { throw "Model gpt-oss:20b is not present in /api/tags. Please download it before running this test." }
  Write-Host "OK: gpt-oss:20b is present in /api/tags"

  # /api/show should return model metadata
  $showBody = @{ name = "gpt-oss:20b" } | ConvertTo-Json
  $tmpShow = Join-Path $env:TEMP "ollama-show-body.json"
  [System.IO.File]::WriteAllText($tmpShow, $showBody, [System.Text.UTF8Encoding]::new($false))
  $showOut = curl.exe -sS --fail-with-body --max-time 60 http://127.0.0.1:11434/api/show `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpShow"
  if (-not $showOut) { throw "Empty response from /api/show" }
  $showJson = $showOut | ConvertFrom-Json
  if (-not $showJson.details) { throw "/api/show did not return model details for gpt-oss:20b" }
  Write-Host "OK: /api/show returned model details"

  # CLI inference smoke
  $cliOut = & ollama run gpt-oss:20b "Reply with exactly OK"
  if (-not $cliOut) { throw "ollama run returned empty output" }
  $cliText = ($cliOut | Out-String).Trim()
  if ($cliText -notmatch '(^|\s)OK(\s|$)') { throw "ollama run did not return OK. Output was: $cliText" }
  Write-Host "OK: ollama run inference works"

  # /api/generate smoke
  $generateBody = @{
    model  = "gpt-oss:20b"
    prompt = "Reply with exactly OK"
    stream = $false
  } | ConvertTo-Json
  $tmpGenerate = Join-Path $env:TEMP "ollama-generate-body.json"
  [System.IO.File]::WriteAllText($tmpGenerate, $generateBody, [System.Text.UTF8Encoding]::new($false))
  $generateOut = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:11434/api/generate `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpGenerate"
  if (-not $generateOut) { throw "Empty response from /api/generate" }
  $generateJson = $generateOut | ConvertFrom-Json
  if (-not $generateJson.response) { throw "/api/generate did not return a response field" }
  if ($generateJson.response.Trim() -ne "OK") { throw "/api/generate expected exactly OK but got: $($generateJson.response)" }
  Write-Host "OK: /api/generate works"

  # /api/chat smoke
  $chatBody = @{
    model = "gpt-oss:20b"
    messages = @(
      @{
        role = "user"
        content = "Reply with exactly OK"
      }
    )
    stream = $false
  } | ConvertTo-Json -Depth 5
  $tmpChat = Join-Path $env:TEMP "ollama-chat-body.json"
  [System.IO.File]::WriteAllText($tmpChat, $chatBody, [System.Text.UTF8Encoding]::new($false))
  $chatOut = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:11434/api/chat `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpChat"
  if (-not $chatOut) { throw "Empty response from /api/chat" }
  $chatJson = $chatOut | ConvertFrom-Json
  $chatText = $chatJson.message.content
  if (-not $chatText) { throw "/api/chat did not return message.content" }
  if ($chatText.Trim() -ne "OK") { throw "/api/chat expected exactly OK but got: $chatText" }
  Write-Host "OK: /api/chat works"

  # Python requests smoke
  if (Test-Path $venv) { Remove-Item -Recurse -Force $venv }
  python -m venv $venv
  $py = Join-Path $venv "Scripts\python.exe"
  & $py -m pip install --upgrade pip
  & $py -m pip install requests
@'
import requests
response = requests.post(
    "http://127.0.0.1:11434/api/generate",
    json={
        "model": "gpt-oss:20b",
        "prompt": "Reply with exactly: OK",
        "stream": False,
    },
    timeout=300,
)
response.raise_for_status()
text = response.json()["response"].strip()
if text != "OK":
    raise SystemExit(f"Expected exactly OK, got: {text}")
print("OK: Python requests example works")
'@ | Set-Content -Path $pythonSmoke -Encoding UTF8
  & $py $pythonSmoke
}

finally {
  Remove-Item $tmpShow, $tmpGenerate, $tmpChat, $pythonSmoke -Force -ErrorAction SilentlyContinue
  Remove-Item $venv -Recurse -Force -ErrorAction SilentlyContinue
  if ($startedHere) {
    if ($p -and -not $p.HasExited) {
      Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
    }
  }
}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=ollama-smoke-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail
p=""
started_here="0"
venv="./ollama-env-ci"
python_smoke="./ollama_python_smoke.py" 

cleanup() {
  rm -f "$python_smoke"
  rm -rf "$venv"
  if [ "$started_here" = "1" ] && [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

wait_for_ollama_api() {
  local attempts="${1:-120}"
  local out=""
  for i in $(seq 1 "$attempts"); do
    out="$(curl -s --max-time 2 http://127.0.0.1:11434/api/tags || true)"
    if [ -n "$out" ]; then
      echo "$out"
      return 0
    fi
    sleep 1
  done
  return 1
}

tags_json="$(wait_for_ollama_api 5 || true)"
if [ -z "$tags_json" ]; then
  ollama serve >/tmp/ollama-test.log 2>&1 &
  p=$!
  started_here="1"
  tags_json="$(wait_for_ollama_api 120 || true)"
fi
if [ -z "$tags_json" ]; then
  echo "Ollama API not ready on http://127.0.0.1:11434"
  exit 1
fi
echo "OK: Ollama API is responding on http://127.0.0.1:11434"

export TAGS_JSON="$tags_json"
python3 - <<'PY'
import json
import os
import sys
data = json.loads(os.environ["TAGS_JSON"])
models = data.get("models", [])
for item in models:
    if item.get("name") == "gpt-oss:20b":
        print("OK: gpt-oss:20b is present in /api/tags")
        sys.exit(0)
print("Model gpt-oss:20b is not present in /api/tags. Please download it before running this test.")
sys.exit(1)
PY

show_out="$(curl -s --max-time 60 http://127.0.0.1:11434/api/show \
  -H "Content-Type: application/json" \
  -d '{"name":"gpt-oss:20b"}' || true)"
if [ -z "$show_out" ]; then
  echo "Empty response from /api/show"
  exit 1
fi
export SHOW_OUT="$show_out"
python3 - <<'PY'
import json
import os
import sys
data = json.loads(os.environ["SHOW_OUT"])
if not data.get("details"):
    print("/api/show did not return model details for gpt-oss:20b")
    sys.exit(1)
print("OK: /api/show returned model details")
PY

cli_out="$(ollama run gpt-oss:20b "Reply with exactly OK" || true)"
if [ -z "$cli_out" ]; then
  echo "ollama run returned empty output"
  exit 1
fi
export CLI_OUT="$cli_out"
python3 - <<'PY'
import os
import sys
text = os.environ["CLI_OUT"].strip()
if "OK" not in text.split():
    print(f"ollama run did not return OK. Output was: {text}")
    sys.exit(1)
print("OK: ollama run inference works")
PY

generate_out="$(curl -s --max-time 300 http://127.0.0.1:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-oss:20b","prompt":"Reply with exactly OK","stream":false}' || true)"
if [ -z "$generate_out" ]; then
  echo "Empty response from /api/generate"
  exit 1
fi
export GENERATE_OUT="$generate_out"
python3 - <<'PY'
import json
import os
import sys
data = json.loads(os.environ["GENERATE_OUT"])
text = data.get("response", "")
if not text:
    print("/api/generate did not return a response field")
    sys.exit(1)
if text.strip() != "OK":
    print(f"/api/generate expected exactly OK but got: {text}")
    sys.exit(1)
print("OK: /api/generate works")
PY

chat_out="$(curl -s --max-time 300 http://127.0.0.1:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-oss:20b","messages":[{"role":"user","content":"Reply with exactly OK"}],"stream":false}' || true)"
if [ -z "$chat_out" ]; then
  echo "Empty response from /api/chat"
  exit 1
fi
export CHAT_OUT="$chat_out"
python3 - <<'PY'
import json
import os
import sys
data = json.loads(os.environ["CHAT_OUT"])
msg = data.get("message", {})
text = msg.get("content", "")
if not text:
    print("/api/chat did not return message.content")
    sys.exit(1)
if text.strip() != "OK":
    print(f"/api/chat expected exactly OK but got: {text}")
    sys.exit(1)
print("OK: /api/chat works")
PY

rm -rf "$venv"
python3 -m venv "$venv"
py="$venv/bin/python"
"$py" -m pip install --upgrade pip
"$py" -m pip install requests
cat > "$python_smoke" <<'PY'
import requests
response = requests.post(
    "http://127.0.0.1:11434/api/generate",
    json={
        "model": "gpt-oss:20b",
        "prompt": "Reply with exactly: OK",
        "stream": False,
    },
    timeout=300,
)
response.raise_for_status()
text = response.json()["response"].strip()
if text != "OK":
    raise SystemExit(f"Expected exactly OK, got: {text}")
print("OK: Python requests example works")
PY
"$py" "$python_smoke"
```
<!-- @test:end --> 
<!-- @os:end -->

### สร้างการตอบสนองในเทอร์มินัล

<!-- @os:linux -->
```bash
curl http://localhost:11434/api/generate -d '{"model": "gpt-oss:20b", "prompt": "Explain GPU acceleration in two sentences.", "stream": false}'
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
curl.exe http://localhost:11434/api/generate -d '{"model": "gpt-oss:20b", "prompt": "Explain GPU acceleration in two sentences.", "stream": false}'
```
<!-- @os:end -->

การตอบสนองเป็น JSON object ที่มีผลลัพธ์ของโมเดลในฟิลด์ `response`


### ตัวอย่าง Python
เมื่อเราสามารถเรียกใช้ Ollama API ผ่านโปรแกรมได้แล้ว มาเรียกใช้จาก Python กัน

#### สร้าง Virtual Environment ในเทอร์มินัล

<!-- @os:linux -->
```bash
sudo apt install -y python3-venv
python3 -m venv ollama-env
source ollama-env/bin/activate
pip install requests
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
python -m venv ollama-env
ollama-env\Scripts\activate
pip install requests
```
<!-- @os:end -->
#### สร้างไฟล์ Python
ในไดเรกทอรีเดียวกัน ใช้ VS Code หรือโปรแกรมแก้ไขอื่นเพื่อสร้างไฟล์ .py และคัดลอกโค้ดต่อไปนี้ลงไป จากนั้นรันไฟล์ในสภาพแวดล้อมที่เปิดใช้งานด้วย `python your_file_name.py`

```python
import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "gpt-oss:20b",
        "prompt": "Write a haiku about local AI inference.",
        "stream": False,
    },
)

print(response.json()["response"])
```

### Endpoint หลักของ API

| Endpoint | Method | วัตถุประสงค์ |
|----------|--------|---------|
| `/api/generate` | POST | การสร้างข้อความแบบ single-turn |
| `/api/chat` | POST | การสนทนาแบบ multi-turn พร้อมประวัติข้อความ |
| `/api/tags` | GET | แสดงรายการโมเดลที่มีอยู่ |
| `/api/show` | POST | แสดงรายละเอียดโมเดล |
| `/api/pull` | POST | ดึงโมเดลจาก registry |

สำหรับเอกสารอ้างอิง API ฉบับเต็ม ดูที่ [เอกสาร Ollama API](https://github.com/ollama/ollama/blob/main/docs/api.md)

## ขั้นตอนถัดไป

- **ลองใช้โมเดลต่างๆ**: เรียกดู [คลังโมเดล Ollama](https://ollama.com/library) เพื่อสำรวจโมเดลที่มีอยู่หลายร้อยรายการ ตั้งแต่ผู้ช่วยเขียนโค้ดขนาดเล็กไปจนถึงโมเดลการให้เหตุผลขนาดใหญ่
- **สร้างโมเดลที่กำหนดเอง**: ใช้ [Modelfile](https://github.com/ollama/ollama/blob/main/docs/modelfile.md) เพื่อตั้งค่า system prompts อุณหภูมิ และพารามิเตอร์อื่นๆ ที่กำหนดเองสำหรับประสบการณ์ที่ปรับแต่งได้
- **สร้างด้วย API**: ใช้ไลบรารีไคลเอนต์ [Python](https://github.com/ollama/ollama-python) หรือ [JavaScript](https://github.com/ollama/ollama-js) เพื่อรวม Ollama เข้ากับแอปพลิเคชันของคุณ
- **เชื่อมต่อกับ frontend**: จับคู่ Ollama กับเครื่องมืออย่าง [Open WebUI](https://github.com/open-webui/open-webui) สำหรับอินเทอร์เฟซแชทที่มีฟีเจอร์ครบครัน พร้อมการค้นหา personas และการอัปโหลดเอกสาร

สำหรับข้อมูลเพิ่มเติม ดูที่ [เอกสาร Ollama](https://github.com/ollama/ollama/blob/main/README.md)