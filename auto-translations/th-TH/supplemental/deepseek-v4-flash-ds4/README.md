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

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) เป็นตัวแปรที่เน้นด้านประสิทธิภาพของตระกูล DeepSeek V4 — โมเดล Mixture of Experts ที่มีพารามิเตอร์ 284 พันล้านตัว โดยมีพารามิเตอร์ที่ทำงานจริง 13 พันล้านตัว ตาม[รายงานทางเทคนิคของ DeepSeek](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) โมเดลนี้ทำคะแนนได้ 79% บน SWE-bench Verified และ 91.6% บน LiveCodeBench

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) คือเอนจินอนุมาน (inference engine) เฉพาะทางที่สร้างขึ้นสำหรับสถาปัตยกรรมโมเดลนี้โดยเฉพาะ แทนที่จะเป็นรันไทม์อเนกประสงค์ ds4 มุ่งเป้าไปที่ตระกูล DeepSeek V4 โดยตรง ด้วยการปรับแต่งเคอร์เนลเฉพาะสถาปัตยกรรมสำหรับซอฟต์แวร์ AMD ROCm™ ปัจจุบันถือเป็นหนึ่งในการนำไปใช้งานที่มีประสิทธิภาพดีที่สุดของ DeepSeek V4 Flash บน Strix Halo

บทแนะนำนี้แสดงวิธีใช้ `ds4-cockpit` ซึ่งเป็น terminal UI เพื่อตั้งค่า ds4 ดาวน์โหลดน้ำหนักโมเดล และเริ่มให้บริการ DeepSeek V4 Flash ในเครื่องบน AMD Ryzen™ AI Halo Developer Platform

## สิ่งที่คุณจะได้เรียนรู้

- วิธีติดตั้งและเปิดใช้งาน terminal UI ของ `ds4-cockpit`
- วิธีสร้างคอนเทนเนอร์ toolbox ROCm ของ ds4
- การดาวน์โหลดค่าการควอนไทซ์ที่แนะนำสำหรับโหนด Halo เดียว
- การเริ่มต้นเซิร์ฟเวอร์อนุมาน ds4 และเปิดใช้งานปลายทาง (endpoint) ที่รองรับ OpenAI
- การเชื่อมต่อ Web UI หรือเอเจนต์เขียนโค้ดเข้ากับเซิร์ฟเวอร์ในเครื่อง

## การตั้งค่าหน่วยความจำ

<!-- @require:memory-config -->

## การติดตั้งซอฟต์แวร์ที่จำเป็น

> **ข้อกำหนดของระบบสำหรับการตั้งค่านี้ (IQ2_XXS แบบโหนดเดียว ที่บริบทขนาด 126k):**
> - ระบบ Strix Halo ที่มี**หน่วยความจำรวมอย่างน้อย 128 GB**
> - **ตั้งค่า BIOS dedicated VRAM (UMA frame buffer) ไว้ที่ค่าต่ำสุด** เพื่อให้พูลหน่วยความจำที่ใช้ร่วมกันมีขนาดใหญ่ที่สุดเท่าที่จะเป็นไปได้
> - **ตั้งค่าพูลหน่วยความจำที่ใช้ร่วมกันของ GPU ไว้อย่างน้อย 110 GB**: รันคำสั่ง `amd-ttm --set 110` (ดูขั้นตอนการตั้งค่าหน่วยความจำด้านบน) แล้วรีบูตเครื่อง หากตั้งค่าต่ำกว่านี้อาจเกิดข้อผิดพลาดหน่วยความจำไม่เพียงพอเมื่อโหลดโมเดลที่บริบทขนาด 126k หากระบบของคุณมีหน่วยความจำว่างน้อยกว่านี้ ให้ลดค่า **Context** ใน Server Mode แทน
>
> **หมายเหตุ:** ลองตั้งค่า **พูลหน่วยความจำที่ใช้ร่วมกันของ GPU** เป็น **110 GB** เป็นจุดเริ่มต้น หากพบข้อผิดพลาดหน่วยความจำไม่เพียงพอ ให้เพิ่มพูลหน่วยความจำที่ใช้ร่วมกัน หรือลดขนาดบริบทลง

ds4-cockpit ใช้คอนเทนเนอร์ toolbox ในการรันเอนจิน ds4 ติดตั้ง `podman`, `distrobox`, และ `pipx`:

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

## ค่าการควอนไทซ์ที่มีให้ใช้งาน

ผู้พัฒนา ds4 ได้จัดเตรียมโมเดล DeepSeek V4 Flash ที่ผ่านการควอนไทซ์หลายเวอร์ชันในรูปแบบ GGUF โมเดลทั้งหมดด้านล่างใช้การปรับเทียบ importance matrix (imatrix) ซึ่งช่วยรักษาความแม่นยำที่สูงขึ้นไว้สำหรับส่วนของโมเดลที่สำคัญที่สุดต่อการเขียนโค้ดและงานด้านการให้เหตุผล

| ค่าการควอนไทซ์ | ขนาด | คำอธิบาย |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80.8 GB | แนะนำสำหรับโหนดเดียวขนาด 128 GB |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | คงเลเยอร์ 37–42 ไว้ที่ความแม่นยำระดับ Q4 เพื่อความแม่นยำที่ดีขึ้น พอดีกับหน่วยความจำ 128 GB แต่เหลือพื้นที่สำหรับบริบทน้อยลง |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | คุณภาพสูงกว่า ต้องใช้โหนด Halo สองโหนดผ่านการทำคลัสเตอร์แบบหลายโหนด |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3.6 GB | ส่วนเสริมทางเลือกสำหรับการถอดรหัสแบบคาดเดา (speculative decoding) เพื่อเพิ่มความเร็วในการสร้างข้อความ |

โมเดล **IQ2_XXS imatrix** เป็นจุดเริ่มต้นที่ดี เนื่องจากสามารถทำงานได้อย่างสบายบนโหนดเดียวและยังเหลือหน่วยความจำเพียงพอสำหรับหน้าต่างบริบทที่เหมาะสม

## การติดตั้ง ds4-cockpit

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) เป็น terminal UI ที่มีน้ำหนักเบาเพื่อให้การเริ่มต้นใช้งาน ds4 บน Strix Halo เป็นเรื่องง่าย โดยจะจัดการการสร้างคอนเทนเนอร์ toolbox การดาวน์โหลดน้ำหนักโมเดล และการเริ่มเซิร์ฟเวอร์ ติดตั้งด้วย `pipx`:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

เปิดใช้งาน cockpit:
```bash
ds4-cockpit
```

<!-- @test:id=ds4-cockpit-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
# Verify the pipx-installed cockpit entry point is on PATH (do NOT launch the TUI).
command -v ds4-cockpit
echo "OK: ds4-cockpit is installed and on PATH"
```
<!-- @test:end -->

## การสร้าง Toolbox

ในแท็บ **Interactive Toolboxes** ให้เลือก toolbox เวอร์ชันล่าสุดที่เสถียร (เช่น `ds4-rocm-7.2.4`) แล้วคลิก **Create/Update** ขั้นตอนนี้จะดึงอิมเมจคอนเทนเนอร์และสร้างสภาพแวดล้อม toolbox


<p align="center">
  <img src="assets/ds4-cockpit-toolboxes.png" alt="Selecting the ds4 toolbox in ds4-cockpit" width="800"/>
</p>

<!-- @test:id=ds4-toolbox-image-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# The toolbox version changes over time, so match the image family, not a fixed tag.
if ! podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ds4-cockpit (Interactive Toolboxes tab) first."
  exit 1
fi
echo "OK: ds4 toolbox container image is present"
```
<!-- @test:end -->

## การดาวน์โหลดโมเดล

ไปที่แท็บ **Model Manager** เลือก **IQ2_XXS imatrix (~80.8 GB)** จากเมนูแบบดรอปดาวน์ แล้วคลิก **Download** ไฟล์โมเดลจะถูกบันทึกไปที่ `~/ds4` โดยค่าเริ่มต้น (คุณสามารถเปลี่ยนเส้นทางการจัดเก็บได้)

> **หมายเหตุ:** โมเดล IQ2_XXS มีขนาดประมาณ 80 GB ดังนั้นการดาวน์โหลดอาจใช้เวลานานขึ้นอยู่กับการเชื่อมต่อของคุณ คุณสามารถดำเนินการต่อได้เมื่อดาวน์โหลดเสร็จสิ้น

<p align="center">
  <img src="assets/ds4-cockpit-model-manager.png" alt="Selecting and downloading the IQ2_XXS model" width="800"/>
</p>

<!-- @test:id=ds4-model-downloaded-linux timeout=60 hidden=True -->
```bash
set -euo pipefail

# ds4-cockpit saves model weights to ~/ds4 by default
model_dir="$HOME/ds4"

if [ ! -d "$model_dir" ]; then
  echo "Model directory $model_dir does not exist. Download the model in ds4-cockpit (Model Manager tab) first."
  exit 1
fi

if ! find "$model_dir" -maxdepth 2 -iname '*.gguf' | grep -q .; then
  echo "No .gguf model files found under $model_dir. Download the IQ2_XXS imatrix model in ds4-cockpit first."
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

## การเริ่มต้นเซิร์ฟเวอร์

ไปที่แท็บ **Server Mode** เลือกโมเดลที่ดาวน์โหลดไว้และ toolbox จากนั้นตั้งค่าขนาดบริบท โฮสต์ และพอร์ต เมื่อพร้อมแล้ว คลิก **Start ds4-server**

> **เคล็ดลับ** ขนาดบริบท `126000` เป็นค่าเริ่มต้นที่เหมาะสมซึ่งควรพอดีกับโหนดเดียว — คุณสามารถตั้งค่าให้สูงขึ้นได้หากมีหน่วยความจำเหลือเฟือ หรือลดลงหากพบข้อผิดพลาดหน่วยความจำไม่เพียงพอ พอร์ต (`8000` ในคู่มือนี้) เป็นค่าตามอำเภอใจ สามารถเลือกพอร์ตว่างใดก็ได้

> **KV Disk Cache (ทางเลือก)** การเปิดใช้งาน **KV Disk Cache** จะถ่ายโอน KV cache ไปยังดิสก์ (ที่ **Host Cache Dir** ค่าเริ่มต้นคือ `~/.cache/ds4-kv`) เพื่อให้พรอมต์ระบบที่ซ้ำกันถูกเรียกคืนจาก SSD แทนที่จะคำนวณใหม่ นี่เป็นการปรับแต่งประสิทธิภาพสำหรับเวิร์กโฟลว์เอเจนต์เขียนโค้ดที่มีพรอมต์ยาวและซ้ำกัน และ**ไม่จำเป็น**สำหรับการรันเซิร์ฟเวอร์

<p align="center">
  <img src="assets/ds4-cockpit-server-mode.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

เซิร์ฟเวอร์จะเริ่มทำงานและรับฟังที่พอร์ต 8000 โดยเปิดใช้งานปลายทาง API ที่รองรับ OpenAI ที่ `http://localhost:8000/v1`

**ทดสอบอย่างรวดเร็ว:**
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
  echo "No .gguf model found under $MODEL_DIR. Download it in ds4-cockpit first."
  exit 1
fi
model_name="$(basename "$model_file")"

# Pick the toolbox image (version-agnostic).
image="$(podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox' | head -1)"
if [ -z "$image" ]; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ds4-cockpit first."
  exit 1
fi

# Always stop/remove the server on exit so it never holds GPU memory afterwards.
cleanup() {
  podman stop -t 10 "$CONTAINER" >/dev/null 2>&1 || true
  podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# Remove any stale instance, then start ds4-server detached (same flags ds4-cockpit uses, with -d instead of -it).
podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
podman run -d --name "$CONTAINER" \
  --device /dev/dri --device /dev/kfd \
  --group-add keep-groups \
  --security-opt seccomp=unconfined \
  --ipc=host \
  --cap-add=SYS_PTRACE \
  --security-opt label=disable \
  --userns=keep-id \
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

คุณสามารถเชื่อมต่อกับอินเทอร์เฟซแชทใดก็ได้ที่รองรับรูปแบบ OpenAI API ตัวอย่างเช่น การใช้ HuggingFace ChatUI:

```bash
docker run -p 3000:3000 \
  --add-host=host.docker.internal:host-gateway \
  -e OPENAI_BASE_URL=http://host.docker.internal:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

เปิด `http://localhost:3000` ในเบราว์เซอร์ของคุณเพื่อเริ่มการสนทนา
## การเชื่อมต่อ Coding Agent

เซิร์ฟเวอร์ ds4 เปิดให้ใช้งานทั้ง endpoint ที่รองรับ OpenAI และ Anthropic ดังนั้น coding agent ส่วนใหญ่จึงสามารถเชื่อมต่อกับมันได้โดยตรง ตัวอย่างเช่น หากต้องการเพิ่มลงใน coding agent ชื่อ `pi` ให้เพิ่มบล็อกต่อไปนี้ลงใน `~/.pi/agent/models.json`:

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

> **เคล็ดลับ**: หากเครื่องที่รัน coding agent หรือ Web UI ของคุณเป็นคนละเครื่องกับแพลตฟอร์ม Halo คุณจะต้องส่งต่อพอร์ต 8000 ผ่าน SSH:
> ```bash
> ssh -L 0.0.0.0:8000:localhost:8000 <halo-host-ip>
> ```

## ขั้นตอนถัดไป

- **การทำคลัสเตอร์แบบหลายโหนด (Multi-node clustering)**: หากคุณมีอุปกรณ์ Halo สองเครื่อง ds4 รองรับการกระจายโมเดล Q4 (~153 GB) ไปยังทั้งสองเครื่องผ่าน pipeline parallelism ดูคำแนะนำการตั้งค่าได้ที่ [เอกสารประกอบของ ds4-toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism)
- **การถอดรหัสเชิงคาดการณ์ (Speculative decoding, MTP)**: ดาวน์โหลดน้ำหนัก MTP (~3.6 GB) และส่ง `--mtp` ให้กับเซิร์ฟเวอร์เพื่อเพิ่มความเร็วในการสร้างผลลัพธ์
- **การถ่ายโอน KV cache ไปยังดิสก์ (KV cache disk offloading)**: สำหรับเวิร์กโฟลว์ของ coding agent ให้เปิดใช้งาน `--kv-disk-dir` เพื่อให้ระบบพรอมต์ที่ใช้ซ้ำถูกกู้คืนจาก SSD แทนที่จะคำนวณใหม่ทุกครั้ง

สำหรับข้อมูลเพิ่มเติม โปรดดูที่ [ds4 repository](https://github.com/antirez/ds4) และ [ds4-cockpit toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox)