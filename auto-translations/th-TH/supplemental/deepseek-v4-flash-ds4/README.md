<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **การแปลด้วยเครื่อง.** หน้านี้ได้รับการแปลโดยอัตโนมัติจากภาษาอังกฤษ และยังไม่ได้รับการตรวจสอบโดยมนุษย์ อาจมีข้อผิดพลาด และคำแนะนำ คำสั่ง การดาวน์โหลด ความพร้อมใช้งานของผลิตภัณฑ์ หรือเนื้อหาอื่นๆ บางส่วนอาจแตกต่างกันไปตามภาษาหรือภูมิภาค ในกรณีที่มีความไม่สอดคล้องหรือความคลาดเคลื่อนใดๆ ให้ถือว่าเวอร์ชันภาษาอังกฤษต้นฉบับของ playbook เป็นฉบับที่มีผลบังคับใช้และมีอำนาจเหนือกว่า
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## ภาพรวม

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) คือรุ่นที่เน้นประสิทธิภาพของตระกูล DeepSeek V4 — โมเดล Mixture of Experts ขนาด 284 พันล้านพารามิเตอร์ที่มีพารามิเตอร์ที่ทำงานอยู่ 13 พันล้านพารามิเตอร์ ตามรายงานทางเทคนิคของ [DeepSeek](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) ระบุว่าทำคะแนนได้ 79% บน SWE-bench Verified และ 91.6% บน LiveCodeBench

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) คือเอนจินอนุมาน (inference engine) เฉพาะที่สร้างขึ้นสำหรับสถาปัตยกรรมโมเดลนี้โดยเฉพาะ แทนที่จะเป็นรันไทม์เอนกประสงค์ ds4 มุ่งเป้าไปที่ตระกูล DeepSeek V4 โดยตรงด้วยการปรับแต่งเคอร์เนลเฉพาะสถาปัตยกรรมสำหรับซอฟต์แวร์ AMD ROCm™ ปัจจุบันถือเป็นหนึ่งในการใช้งาน DeepSeek V4 Flash ที่มีประสิทธิภาพดีที่สุดบน Strix Halo

บทช่วยสอนนี้แสดงวิธีใช้ `ai-toolbox-cockpit` ซึ่งเป็น terminal UI เพื่อตั้งค่า ds4 ดาวน์โหลดน้ำหนักโมเดล และเริ่มให้บริการ DeepSeek V4 Flash ในเครื่องบน AMD Ryzen™ AI Halo Developer Platform

## สิ่งที่คุณจะได้เรียนรู้

- วิธีติดตั้งและเปิดใช้งาน terminal UI ของ `ai-toolbox-cockpit`
- วิธีสร้าง ds4 ROCm toolbox container
- การดาวน์โหลดการควอนไทซ์ (quantization) ที่แนะนำสำหรับโหนด Halo เดี่ยว
- การเริ่มเซิร์ฟเวอร์อนุมาน ds4 และเปิดใช้งาน endpoint ที่ใช้งานร่วมกันได้กับ OpenAI
- การเชื่อมต่อ Web UI หรือตัวแทนการเขียนโค้ด (coding agent) เข้ากับเซิร์ฟเวอร์ในเครื่อง

## การตั้งค่าหน่วยความจำ

<!-- @require:memory-config -->

## การติดตั้งซอฟต์แวร์ที่จำเป็น

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @prereq:podman,distrobox,ds4-cockpit,ds4-toolbox-image -->

> **ข้อกำหนดระบบสำหรับการกำหนดค่านี้ (IQ2_XXS โหนดเดียวที่บริบท 126k):**
> - ระบบ Strix Halo ที่มี **หน่วยความจำรวม (unified memory) อย่างน้อย 128 GB**
> - **ตั้งค่า BIOS dedicated VRAM (UMA frame buffer) ไว้ที่ค่าต่ำสุด** เพื่อให้พูลหน่วยความจำที่ใช้ร่วมกันมีขนาดใหญ่ที่สุดเท่าที่จะเป็นไปได้
> - ตั้งค่า **พูลหน่วยความจำที่ใช้ร่วมกันของ GPU ให้มีอย่างน้อย 110 GB**: รันคำสั่ง `amd-ttm --set 110` (ดูขั้นตอนการตั้งค่าหน่วยความจำด้านบน) แล้วรีบูต ค่าที่ต่ำกว่านี้อาจทำให้เกิดข้อผิดพลาดหน่วยความจำไม่เพียงพอเมื่อโหลดโมเดลที่บริบท 126k หากระบบของคุณมีหน่วยความจำว่างน้อยกว่านี้ ให้ลดค่า **Context** ใน Server Mode แทน
>
> **หมายเหตุ:** ลองตั้งค่า **พูลหน่วยความจำที่ใช้ร่วมกันของ GPU** เป็น **110 GB** เป็นจุดเริ่มต้น หากพบข้อผิดพลาดหน่วยความจำไม่เพียงพอ ให้เพิ่มพูลหน่วยความจำที่ใช้ร่วมกันหรือลดขนาดบริบทลง

ai-toolbox-cockpit ใช้ container toolbox เพื่อรันเอนจิน ds4 ติดตั้ง `podman`, `distrobox`, และ `pipx`:

```bash
sudo apt update
sudo apt install -y podman distrobox pipx
```

<!-- @test:id=ds4-prereqs-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
podman --version
distrobox version 2>/dev/null || distrobox --version
pipx --version
echo "OK: podman, distrobox, and pipx are installed"
```
<!-- @test:end -->

## การควอนไทซ์ที่มีให้เลือกใช้

ผู้พัฒนา ds4 มีโมเดล DeepSeek V4 Flash ที่ผ่านการควอนไทซ์หลายรูปแบบในฟอร์แมต GGUF โมเดลทั้งหมดด้านล่างใช้การปรับเทียบ importance matrix (imatrix) ซึ่งรักษาความแม่นยำที่สูงขึ้นสำหรับส่วนต่าง ๆ ของโมเดลที่สำคัญที่สุดต่องานด้านการเขียนโค้ดและการให้เหตุผล

| การควอนไทซ์ | ขนาด | คำอธิบาย |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80.8 GB | แนะนำสำหรับโหนดเดียวขนาด 128 GB |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | รักษาเลเยอร์ 37–42 ไว้ที่ความแม่นยำ Q4 เพื่อความแม่นยำที่ดีขึ้น รองรับใน 128 GB แต่เหลือพื้นที่สำหรับบริบทน้อยลง |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | คุณภาพสูงขึ้น ต้องใช้โหนด Halo สองโหนดผ่านการทำคลัสเตอร์แบบหลายโหนด |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3.6 GB | ส่วนเสริมที่เป็นตัวเลือกสำหรับ speculative decoding เพื่อเพิ่มความเร็วในการสร้างข้อความ |

โมเดล **IQ2_XXS imatrix** เป็นจุดเริ่มต้นที่ดี มันรองรับได้อย่างสบายบนโหนดเดียวและเหลือหน่วยความจำเพียงพอสำหรับหน้าต่างบริบทที่เหมาะสม

## การติดตั้ง ai-toolbox-cockpit

[ai-toolbox-cockpit](https://github.com/kyuz0/ai-toolbox-cockpit) คือ terminal UI ที่เบาและใช้งานง่ายสำหรับการติดตั้งแบ็กเอนด์ AI ต่าง ๆ เราจะใช้มันเพื่อจัดการการสร้าง container ds4 ของเรา ดาวน์โหลดน้ำหนักโมเดล และเริ่มเซิร์ฟเวอร์ ติดตั้งด้วย `pipx`:

<!-- @test:id=ds4-cockpit-install-linux timeout=300 -->
```bash
pipx install git+https://github.com/kyuz0/ai-toolbox-cockpit.git
```
<!-- @test:end -->

เปิดใช้งาน cockpit:
```bash
ai-toolbox-cockpit
```

<!-- @test:id=ds4-cockpit-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
# Verify the pipx-installed cockpit entry point is on PATH (do NOT launch the TUI).
command -v ai-toolbox-cockpit
echo "OK: ai-toolbox-cockpit is installed and on PATH"
```
<!-- @test:end -->

## ขั้นตอนที่ 1: การสร้าง Toolbox

ในแท็บ **Interactive Toolboxes** เลือก toolbox ล่าสุดที่มีให้ใช้งาน/เสถียรสำหรับ ds4 (เช่น `ds4-rocm-10.0`) และคลิก **Create/Update** ซึ่งจะดึง container image และสร้างสภาพแวดล้อม toolbox


<p align="center">
  <img src="assets/ai-toolbox-cockpit-toolboxes.png" alt="Selecting the ds4 toolbox in ai-toolbox-cockpit" width="800"/>
</p>

<!-- @test:id=ds4-toolbox-image-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# The toolbox version changes over time, so match the image family, not a fixed tag.
if ! podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ai-toolbox-cockpit (Interactive Toolboxes tab) first."
  exit 1
fi
echo "OK: ds4 toolbox container image is present"
```
<!-- @test:end -->

## ขั้นตอนที่ 2: การดาวน์โหลดโมเดล

ไปที่แท็บ **Models** ก่อนอื่น เลือกแบ็กเอนด์ (ds4) จากนั้นเลือก **IQ2_XXS imatrix (~80.8 GB)** จากดรอปดาวน์และคลิก **Download** ไฟล์โมเดลจะถูกบันทึกไว้ที่ `~/ds4` โดยค่าเริ่มต้น (คุณสามารถเปลี่ยนพาธการจัดเก็บได้)

> **หมายเหตุ:** โมเดล IQ2_XXS มีขนาดประมาณ 80 GB ดังนั้นการดาวน์โหลดอาจใช้เวลานานขึ้นอยู่กับการเชื่อมต่อของคุณ คุณสามารถดำเนินการต่อได้เมื่อเสร็จสิ้น

<p align="center">
  <img src="assets/ai-toolbox-cockpit-models.png" alt="Selecting and downloading the IQ2_XXS model" width="800"/>
</p>

<!-- @test:id=ds4-model-downloaded-linux timeout=60 hidden=True -->
```bash
set -euo pipefail

# ai-toolbox-cockpit saves model weights to ~/ds4 by default
model_dir="$HOME/ds4"

if [ ! -d "$model_dir" ]; then
  echo "Model directory $model_dir does not exist. Download the model in ai-toolbox-cockpit (Model Manager tab) first."
  exit 1
fi

if ! find "$model_dir" -maxdepth 2 -iname '*.gguf' | grep -q .; then
  echo "No .gguf model files found under $model_dir. Download the IQ2_XXS imatrix model in ai-toolbox-cockpit first."
  exit 1
fi

# Prefer to confirm the recommended IQ2_XXS imatrix quantization is present.
if find "$model_dir" -maxdepth 2 -iname '*IQ2*imatrix*.gguf' | grep -q .; then
  echo "OK: IQ2_XXS imatrix model is downloaded"
else
  echo "OK: a GGUF model is present (recommended IQ2_XXS imatrix file not detected by name)"
fi
```
<!-- @test:end -->

## ขั้นตอนที่ 3: การเริ่มเซิร์ฟเวอร์

ไปที่แท็บ **Server Mode** เลือกโมเดลที่ดาวน์โหลดไว้และ toolbox จากนั้นกำหนดค่าขนาดบริบท โฮสต์ และพอร์ต เมื่อพร้อมแล้ว คลิก **Start ds4-server**

> **เคล็ดลับ** ขนาดบริบท `126000` เป็นค่าเริ่มต้นที่เหมาะสมซึ่งควรรองรับได้บนโหนดเดียว — คุณสามารถตั้งค่าให้สูงขึ้นได้หากมีหน่วยความจำเหลือเฟือ หรือลดลงหากพบข้อผิดพลาดหน่วยความจำไม่เพียงพอ พอร์ต (`8000` ในคู่มือนี้) เป็นค่าที่กำหนดเองได้ — เลือกพอร์ตใดก็ได้ที่ว่างอยู่

> **KV Disk Cache (ตัวเลือก)** การเปิดใช้งาน **KV Disk Cache** จะย้าย KV cache ไปยังดิสก์ (ที่ **Host Cache Dir** ค่าเริ่มต้นคือ `~/.cache/ds4-kv`) เพื่อให้พรอมต์ระบบที่ซ้ำกันถูกกู้คืนจาก SSD แทนที่จะถูกคำนวณใหม่ นี่คือการปรับแต่งประสิทธิภาพสำหรับเวิร์กโฟลว์ตัวแทนการเขียนโค้ดที่มีพรอมต์ที่ยาวและซ้ำ ๆ และ **ไม่จำเป็นต้อง** ใช้ในการรันเซิร์ฟเวอร์

<p align="center">
  <img src="assets/ai-toolbox-cockpit-server.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

เซิร์ฟเวอร์จะเริ่มทำงานและรับฟังที่พอร์ต 8000 โดยเปิดใช้งาน endpoint ของ API ที่ใช้งานร่วมกันได้กับ OpenAI ที่ `http://localhost:8000/v1`

**การทดสอบอย่างรวดเร็ว:**
```bash
curl http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "deepseek-v4-flash",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": false
  }'
```

<!-- @test:id=ds4-server-chat-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

# This runner is shared with other playbooks, and ds4 at a 126k context consumes almost the entire GPU memory pool.
# So rather than keeping ds4 resident, CI starts the server, verifies a chat completion, then stops it again.
# This frees the memory for the next job.
# ds4 has no separate "unload"; stopping the server process is what releases the ~80 GB model.

CONTAINER="ds4-ci-server"
MODEL_DIR="$HOME/ds4"

# Locate the downloaded model (prefer the recommended IQ2_XXS imatrix file).
model_file="$(find "$MODEL_DIR" -maxdepth 2 -iname '*IQ2*imatrix*.gguf' 2>/dev/null | head -1)"
if [ -z "$model_file" ]; then
  model_file="$(find "$MODEL_DIR" -maxdepth 2 -iname '*.gguf' 2>/dev/null | head -1)"
fi
if [ -z "$model_file" ]; then
  echo "No .gguf model found under $MODEL_DIR. Download it in ai-toolbox-cockpit first."
  exit 1
fi
model_name="$(basename "$model_file")"

# Pick the toolbox image (version-agnostic).
image="$(podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox' | head -1)"
if [ -z "$image" ]; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ai-toolbox-cockpit first."
  exit 1
fi

# Always stop/remove the server on exit so it never holds GPU memory afterwards.
cleanup() {
  podman stop -t 10 "$CONTAINER" >/dev/null 2>&1 || true
  podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# keep-id maps the calling user into the container. Root does not need it, and as root it cannot
# be combined with --ipc=host (crun fails to mount /dev/mqueue), so root keeps the host user namespace.
userns=keep-id
if [ "$(id -u)" -eq 0 ]; then
  userns=host
fi

# Remove any stale instance, then start ds4-server detached (same flags ai-toolbox-cockpit uses, with -d instead of -it).
podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
podman run -d --name "$CONTAINER" \
  --device /dev/dri --device /dev/kfd \
  --group-add keep-groups \
  --security-opt seccomp=unconfined \
  --ipc=host \
  --cap-add=SYS_PTRACE \
  --security-opt label=disable \
  --userns="$userns" \
  -p 127.0.0.1:8000:8000 \
  -v "$MODEL_DIR":/models:ro \
  "$image" \
  ds4-server -m "/models/$model_name" --ctx 126000 --host 0.0.0.0 --port 8000

# Wait for readiness; the ~80 GB model can take a few minutes to load.
up=false
for i in $(seq 1 240); do
  code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 3 http://127.0.0.1:8000/v1/models || true)"
  if [ -n "$code" ] && [ "$code" != "000" ]; then
    up=true
    break
  fi
  if ! podman inspect -f '{{.State.Running}}' "$CONTAINER" 2>/dev/null | grep -q true; then
    echo "ds4-server container exited during startup:"
    podman logs "$CONTAINER" 2>&1 | tail -40 || true
    exit 1
  fi
  sleep 2
done

if [ "$up" != "true" ]; then
  echo "ds4 server did not become ready on http://127.0.0.1:8000"
  podman logs "$CONTAINER" 2>&1 | tail -40 || true
  exit 1
fi
echo "OK: ds4 server is responding on :8000"

body='{
  "model": "deepseek-v4-flash",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32,
  "stream": false
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d "$body")"

if [ -z "$out" ]; then
  echo "Empty response from ds4 /v1/chat/completions"
  exit 1
fi

export DS4_OUT="$out"
python3 - <<'PY'
import json, os, sys

data = json.loads(os.environ["DS4_OUT"])
choices = data.get("choices")
if not choices:
    print("Response has no 'choices':")
    print(json.dumps(data, indent=2)[:2000])
    sys.exit(1)

message = choices[0].get("message", {}) or {}
content = message.get("content") or message.get("reasoning_content")
if not content:
    print("Response choice has empty content:")
    print(json.dumps(data, indent=2)[:2000])
    sys.exit(1)

print("OK: ds4 chat/completions returned content")
PY

echo "OK: ds4 server test complete; server stopped and GPU memory released"
```
<!-- @test:end -->
## การเชื่อมต่อ Web UI

คุณสามารถเชื่อมต่อส่วนติดต่อแชทใดก็ได้ที่รองรับรูปแบบ OpenAI API ตัวอย่างเช่น การใช้ HuggingFace ChatUI:

```bash
docker run --network=host \
  -e PORT=3000 \
  -e OPENAI_BASE_URL=http://localhost:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

เปิด `http://localhost:3000` ในเบราว์เซอร์ของคุณเพื่อเริ่มแชท

> **หมายเหตุ:** `--network=host` จะทำให้ Web UI อยู่บนเครือข่ายของโฮสต์ เพื่อให้สามารถเข้าถึงเซิร์ฟเวอร์ ds4 ที่ `localhost` ได้โดยตรง วิธีนี้ยังคงให้เซิร์ฟเวอร์ ds4 ผูกอยู่กับ loopback เท่านั้น (ไม่จำเป็นต้องเปิดเผยบนอินเทอร์เฟซอื่น)

> **เคล็ดลับ:** พอร์ตของ Web UI (`3000` ในที่นี้ ซึ่งตั้งค่าผ่าน `PORT`) เป็นค่าที่เลือกได้ตามใจ — สามารถเลือกพอร์ตว่างใดก็ได้หาก `3000` ถูกใช้งานอยู่แล้ว แล้วเปิดพอร์ตนั้นในเบราว์เซอร์แทน ตรวจสอบให้แน่ใจว่าพอร์ตใน `OPENAI_BASE_URL` ตรงกับพอร์ตที่เซิร์ฟเวอร์ ds4 ของคุณกำลังทำงานอยู่

## การเชื่อมต่อ Coding Agent

เซิร์ฟเวอร์ ds4 เปิดใช้งานทั้งเอนด์พอยต์ที่รองรับ OpenAI และ Anthropic ดังนั้น coding agent ส่วนใหญ่จึงสามารถเชื่อมต่อกับมันได้โดยตรง ตัวอย่างเช่น การเพิ่มเข้าไปใน coding agent ชื่อ `pi` ให้เพิ่มบล็อกต่อไปนี้ลงใน `~/.pi/agent/models.json`:

```json
"ds4": {
  "name": "ds4.c local",
  "baseUrl": "http://localhost:8000/v1",
  "api": "openai-completions",
  "apiKey": "dsv4-local",
  "compat": {
    "supportsStore": false,
    "supportsDeveloperRole": false,
    "supportsReasoningEffort": true,
    "supportsUsageInStreaming": true,
    "maxTokensField": "max_tokens",
    "supportsStrictMode": false,
    "thinkingFormat": "deepseek",
    "requiresReasoningContentOnAssistantMessages": true
  },
  "models": [
    {
      "id": "deepseek-v4-flash",
      "name": "DeepSeek V4 Flash (ds4.c local)",
      "reasoning": true,
      "thinkingLevelMap": {
        "off": null,
        "minimal": "low",
        "low": "low",
        "medium": "medium",
        "high": "high",
        "xhigh": "xhigh"
      },
      "input": ["text"],
      "contextWindow": 131072,
      "maxTokens": 65536,
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 }
    }
  ]
}
```

> **เคล็ดลับ**: หาก coding agent หรือ Web UI ของคุณทำงานอยู่บนเครื่องที่แตกต่างจากแพลตฟอร์ม Halo คุณจะต้องส่งต่อพอร์ตของเซิร์ฟเวอร์ (`8000` ในที่นี้) ผ่าน SSH:
> ```bash
> ssh -L 8000:localhost:8000 <halo-host-ip>
> ```

## ขั้นตอนถัดไป

- **การทำคลัสเตอร์หลายโหนด (Multi-node clustering)**: หากคุณมีอุปกรณ์ Halo สองเครื่อง ds4 รองรับการกระจายโมเดล Q4 (~153 GB) ไปยังทั้งสองเครื่องผ่าน pipeline parallelism ดู[เอกสาร ds4-toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism) สำหรับคำแนะนำในการตั้งค่า
- **การถอดรหัสแบบคาดเดา (Speculative decoding, MTP)**: ดาวน์โหลดไฟล์น้ำหนัก MTP (~3.6 GB) และส่ง `--mtp` ไปยังเซิร์ฟเวอร์เพื่อความเร็วในการสร้างผลลัพธ์ที่เร็วขึ้น
- **การถ่ายโอน KV cache ลงดิสก์**: สำหรับเวิร์กโฟลว์ของ coding agent ให้เปิดใช้งาน `--kv-disk-dir` เพื่อให้ system prompt ที่ซ้ำกันถูกกู้คืนจาก SSD แทนที่จะคำนวณใหม่ทุกครั้ง

สำหรับข้อมูลเพิ่มเติม ดู[ที่เก็บ ds4](https://github.com/antirez/ds4) และ [ds4-cockpit toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox)