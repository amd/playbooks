<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# การคลัสเตอร์ Ryzen™ AI Halo สองเครื่องด้วย RCCL

## ภาพรวม

Ryzen™ AI Halo ของคุณสามารถรันโมเดลภาษาขนาดใหญ่ในเครื่องได้อยู่แล้ว การคลัสเตอร์จะยกระดับความสามารถนี้ขึ้นไปอีก โดยรวม GPU memory ของหลายระบบเข้าด้วยกันผ่านเครือข่ายท้องถิ่น ทำให้คุณเข้าถึงโมเดลขนาดใหญ่ขึ้นที่มีความสามารถในการอนุมานที่แข็งแกร่งกว่า สร้างโค้ดได้ดีกว่า และเข้าใจหลายภาษาได้ลึกซึ้งกว่า ทั้งหมดนี้บนฮาร์ดแวร์ของคุณเองอย่างสมบูรณ์

Playbook นี้จะสอนวิธีคลัสเตอร์ระบบ Ryzen AI Halo สองเครื่องโดยใช้ RCCL (ROCm Communication Collectives Library) ร่วมกับ vLLM และรัน Qwen3.5-397B ซึ่งเป็นโมเดลที่มีพารามิเตอร์ 397B บนทั้งสองเครื่องพร้อมการเร่งความเร็วด้วย ROCm

## สิ่งที่คุณจะได้เรียนรู้

- วิธีขยายการจัดสรร VRAM บนระบบ Ryzen AI Halo
- การเปิดใช้งาน vLLM พร้อมรองรับ ROCm
- การกำหนดค่า RCCL สำหรับการอนุมานแบบ tensor-parallel หลายโหนดบนระบบ Ryzen AI Halo สองเครื่อง
- การรันโมเดลพารามิเตอร์ 397B บนระบบ Ryzen AI Halo สองเครื่องที่เชื่อมต่อกันผ่านเครือข่าย

## ข้อกำหนดเบื้องต้น

### ฮาร์ดแวร์

Playbook นี้ต้องใช้ Ryzen AI Halo สองหน่วยและ Ethernet switch หนึ่งตัว เชื่อมต่อในรูปแบบ star topology โดยแต่ละหน่วยเชื่อมต่อโดยตรงกับ switch

| ส่วนประกอบ | จำนวน | คำอธิบาย |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | โหนดประมวลผลที่ประกอบเป็นคลัสเตอร์ |
| Ethernet switch 10Gbps | 1 | Switch กลางสำหรับการสื่อสารระหว่างโหนด Ryzen AI Halo หลายเครื่อง (อย่างน้อย 2 พอร์ต) |
| สาย Ethernet | 2 | เชื่อมต่อแต่ละหน่วย Halo กับ switch (แนะนำ Cat 7 หรือสูงกว่า) |

> **หมายเหตุ**: ต้องใช้พอร์ต Ethernet switch สองพอร์ตเพื่อเชื่อมต่อ Ryzen AI Halo สองหน่วย หากคุณเข้าถึงโมเดลจากเครื่อง client แยกต่างหากแทนที่จะเป็นจากหน่วย Halo ใดหน่วยหนึ่ง จะต้องใช้พอร์ตที่สาม

### ซอฟต์แวร์
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## การตั้งค่าฮาร์ดแวร์ทางกายภาพ

> **หมายเหตุ**: ดำเนินการขั้นตอนนี้บนทั้ง Machine 1 และ Machine 2

เชื่อมต่อแต่ละหน่วย Ryzen AI Halo กับ Ethernet switch โดยใช้สาย Cat 7 (หรือสูงกว่า) ซึ่งจะสร้างลิงก์ 10Gbps ที่ใช้สำหรับการสื่อสารความเร็วสูงระหว่างโหนด

### 1. ระบุ Network Interface

บนแต่ละเครื่อง ให้ค้นหาชื่อ network interface และจดบันทึกไว้ (จะถูกอ้างอิงในคำแนะนำที่เหลือในชื่อ `IFNAME`) รันคำสั่ง:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

คำสั่งนี้จะพิมพ์ชื่อ interface โดยตรง ตัวอย่างเช่น:

```bash
enp191s0
```

### 2. ตรวจสอบความเร็วลิงก์เครือข่าย

ยืนยันว่าลิงก์ทำงานอยู่และรันด้วยความเร็วเต็มโดยตรวจสอบความเร็วของ interface ของคุณ:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **หมายเหตุ**: แทนที่ `<IFNAME>` ด้วยชื่อ interface ที่ได้จาก [1. ระบุ Network Interface](#1-determine-network-interfaces)

คุณควรเห็นความเร็ว `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **หมายเหตุ**: หากความเร็วต่ำกว่า `10000Mb/s` หรือลิงก์ไม่ขึ้นมา ให้ตรวจสอบการเชื่อมต่อสายและยืนยันว่าพอร์ต switch ถูกตั้งค่าเป็น 10Gbps บาง switch อาจต้องปิดการใช้งาน auto-negotiation และตั้งค่าความเร็วลิงก์ด้วยตนเอง โปรดดูเอกสารประกอบของ switch ของคุณ

## การขยายการจัดสรร VRAM

> **หมายเหตุ**: ดำเนินการขั้นตอนนี้บนทั้ง Machine 1 และ Machine 2

### การกำหนดค่าหน่วยความจำสำหรับการรันโมเดลขนาดใหญ่

บน Linux, ROCm ใช้ shared system memory pool และ pool นี้ถูกกำหนดค่าเริ่มต้นที่ครึ่งหนึ่งของหน่วยความจำระบบ

ปริมาณนี้สามารถเพิ่มได้โดยการเปลี่ยนการตั้งค่า Translation Table Manager (TTM) page ของ kernel ตามคำแนะนำต่อไปนี้ AMD แนะนำให้ตั้งค่า minimum dedicated VRAM ใน BIOS (0.5 GB)

* ติดตั้ง pipx utility และเพิ่ม path สำหรับ wheels ที่ติดตั้งโดย pipx เข้าไปใน system search path

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* ติดตั้ง amd-debug-tools wheel จาก PyPI
  ```bash
  pipx install amd-debug-tools
  ```

* รัน amd-ttm tool เพื่อตรวจสอบการตั้งค่าปัจจุบันของ shared memory
  ```bash
  amd-ttm
  ```

* กำหนดค่า shared memory ใหม่เป็น **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* รีบูตระบบเพื่อให้การเปลี่ยนแปลงมีผล

## การเริ่มต้น vLLM Container

> **หมายเหตุ**: ดำเนินการขั้นตอนนี้บนทั้ง Machine 1 และ Machine 2

Ryzen AI Halo ของคุณมาพร้อมกับ vLLM ที่บรรจุอยู่ใน container image ที่สร้างไว้ล่วงหน้า ซึ่งคุณรันโดยใช้ Podman ซึ่งเป็นเครื่องมือ container แบบฟรีและโอเพนซอร์ส

### 1. สร้างไดเรกทอรีดาวน์โหลดโมเดล

เมื่อคุณ serve โมเดล Qwen3.5-397B ใน playbook นี้ vLLM จะดาวน์โหลด model weights ไปยังระบบของคุณโดยอัตโนมัติ เพื่อให้แน่ใจว่า weights เหล่านั้นสามารถเข้าถึงได้จากภายใน container ให้สร้างไดเรกทอรี models ที่ container สามารถ mount ได้ก่อน:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. เปิดใช้งาน vLLM Container

คำสั่งด้านล่างจะเปิดใช้งาน container และนำคุณเข้าสู่ interactive shell โดยจะ mount ไดเรกทอรี models ที่คุณเพิ่งสร้างและส่ง `IFNAME` ของคุณไปยัง `NCCL_SOCKET_IFNAME` และ `GLOO_SOCKET_IFNAME` เพื่อบอก RCCL (ไลบรารีที่ vLLM ใช้ในการประสานงาน GPU ทั่วทั้งคลัสเตอร์) ว่าจะใช้ interface ใด

เริ่มต้น container ด้วย:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **หมายเหตุ**: แทนที่ `<IFNAME>` ด้วยชื่อ interface ที่ได้จาก [1. ระบุ Network Interface](#1-determine-network-interfaces)

## การรันโมเดลบนคลัสเตอร์

vLLM ใช้ Ray ในการจัดการคลัสเตอร์และ RCCL ในการจัดการการสื่อสาร GPU-to-GPU ระหว่างโหนด เครื่องหนึ่งทำหน้าที่เป็น **head node** (Machine 1) ซึ่งประสานงานการอนุมาน อีกเครื่องเข้าร่วมเป็น **worker node** (Machine 2) โดยสนับสนุน GPU memory และการประมวลผล

> **หมายเหตุ**: Ray เป็น optional dependency สำหรับ vLLM และใช้งานได้เฉพาะจากภายใน Podman container ที่กำหนดค่าไว้ล่วงหน้าเท่านั้น

เมื่อเริ่มต้น vLLM จะแบ่งโมเดลระหว่างทั้งสองโหนดโดยใช้ tensor parallelism เมื่อโหลดแล้ว การอนุมานจะดำเนินการเหมือนกับการรันบน accelerator เดียว

### ขั้นตอนที่ 1: เริ่มต้น Ray Head Node (Machine 1)

บน Machine 1 ให้เริ่มต้น Ray head node เพื่อเริ่มต้นคลัสเตอร์:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **การค้นหา `<MACHINE_1_IP>`**: บน Machine 1 รัน `hostname -I | awk '{print $1}'` เพื่อค้นหา IP address ในเครื่องของมัน

### ขั้นตอนที่ 2: เข้าร่วมคลัสเตอร์ (Machine 2)

บน Machine 2 ให้เชื่อมต่อกับ head node เพื่อสร้างคลัสเตอร์:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **การค้นหา `<MACHINE_2_IP>`**: บน Machine 2 รัน `hostname -I | awk '{print $1}'` เพื่อค้นหา IP address ในเครื่องของมัน

### ขั้นตอนที่ 3: Serve โมเดล (Machine 1)

บน Machine 1 ให้เปิดใช้งาน vLLM server ซึ่งจะดาวน์โหลดโมเดลโดยอัตโนมัติและเริ่ม serve บนทั้งสองโหนด:

```bash
vllm serve Qwen/Qwen3.5-397B-A17B-GPTQ-Int4 \
  --port 7000 \
  --host 0.0.0.0 \
  --max-model-len 32768 \
  --gpu-memory-utilization 0.9 \
  --dtype float16 \
  --tensor-parallel-size 2 \
  --distributed-executor-backend ray \
  --enforce-eager \
  --language-model-only \
  --reasoning-parser qwen3
```

#### อ้างอิงพารามิเตอร์

| Flag | วัตถุประสงค์ |
|------|---------|
| `--port` | พอร์ตสำหรับ serve HTTP API |
| `--host` | IP address ที่จะผูก server ไว้ (`0.0.0.0` สำหรับทุก interface) |
| `--max-model-len` | ความยาว context สูงสุดในหน่วย token |
| `--gpu-memory-utilization` | สัดส่วนของ GPU memory ที่จะจัดสรร (0.0–1.0) |
| `--dtype` | ประเภทข้อมูลสำหรับ model weights |
| `--tensor-parallel-size` | จำนวน GPU ที่จะแบ่งโมเดลออก (ตั้งค่าเป็นจำนวน GPU ทั้งหมดในคลัสเตอร์) |
| `--distributed-executor-backend` | Backend สำหรับการรันแบบหลายโหนด (`ray` สำหรับการ deploy คลัสเตอร์) |
| `--enforce-eager` | ปิดใช้งานการคอมไพล์ CUDA graph เพื่อความเข้ากันได้ |
| `--language-model-only` | ข้ามการโหลด auxiliary model components (เช่น vision encoder) |
| `--reasoning-parser` | เปิดใช้งานการแยกวิเคราะห์ผลลัพธ์การอนุมานแบบมีโครงสร้างสำหรับโมเดล |

สำหรับการใช้งานพารามิเตอร์แบบเต็ม โปรดดู [เอกสาร vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/)

## การเข้าถึงโมเดล

vLLM เปิดเผย API ที่เข้ากันได้กับ OpenAI ดังนั้นคุณสามารถเชื่อมต่อ client หรือ interface ที่เข้ากันได้กับคลัสเตอร์ของคุณ ตัวเลือกยอดนิยมหนึ่งคือ [Open WebUI](https://github.com/open-webui/open-webui) ซึ่งมี chat interface แบบใช้เบราว์เซอร์

เพื่อเชื่อมต่อ Open WebUI กับ vLLM endpoint ของคุณ:

1. เปิด **Settings** > **Admin Panel** > **Connections**
2. คลิก **+** บน **Manage OpenAI API Connections**
3. ตั้งค่า **Connection Type** เป็น **External**
4. ตั้งค่า **URL** เป็น `http://<MACHINE_1_IP>:7000/v1`
5. ใต้ **Auth** ให้เลือก **None** จาก dropdown
6. ปล่อย **Model IDs** ว่างไว้เพื่อค้นพบโมเดลทั้งหมดจาก endpoint โดยอัตโนมัติ

> **การค้นหา `<MACHINE_1_IP>`**: บน Machine 1 รัน `hostname -I | awk '{print $1}'` เพื่อค้นหา IP address ในเครื่องของมัน หากเข้าถึง Open WebUI จาก Machine 1 เอง คุณสามารถใช้ `http://localhost:7000/v1`

![การตั้งค่าการเชื่อมต่อ Open WebUI สำหรับ vLLM endpoint](assets/openwebui-connection.png)

เมื่อเชื่อมต่อแล้ว ให้เลือกโมเดลจาก model dropdown ใน Open WebUI และเริ่มสนทนา โมเดลกำลังรันอยู่บนโหนด Ryzen AI Halo ทั้งสองของคุณ:

![การสนทนากับ Qwen3.5-397B ใน Open WebUI](assets/openwebui-chat.png)

## ขั้นตอนถัดไป

- **สำรวจโมเดลอื่น**: ค้นพบโมเดลใหม่บน [Hugging Face](https://huggingface.co/models?&sort=trending) ที่พอดีกับ GPU memory รวมของคลัสเตอร์ของคุณ
- **ขยายเป็นสี่โหนด**: เพิ่มระบบ Ryzen AI Halo อีกสองเครื่องเป็น Ray worker เพิ่มเติมเพื่อแบ่งโมเดลบน GPU จำนวนมากขึ้น ซึ่งต้องใช้ Ethernet switch ที่มีอย่างน้อยสี่พอร์ต หนึ่งพอร์ตต่อโหนด ทำตาม [ขั้นตอนที่ 2: เข้าร่วมคลัสเตอร์](#step-2-join-the-cluster-machine-2) บน worker เพิ่มเติมแต่ละเครื่องและเพิ่ม `--tensor-parallel-size` ตามความเหมาะสม
- **ลองกลยุทธ์ parallelism อื่น**: vLLM รองรับ [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) สำหรับโมเดล mixture-of-experts และ [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) สำหรับ throughput ที่สูงขึ้น ทดลองกับ `--enable-expert-parallel` และ `--data-parallel-size` เพื่อค้นหาการกำหนดค่าที่ดีที่สุดสำหรับ workload ของคุณ