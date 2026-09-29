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

# การรวมคลัสเตอร์ Ryzen™ AI Halo สี่เครื่องด้วย RPC

## ภาพรวม

Ryzen™ AI Halo ของคุณมีความสามารถในการรัน large language model ในเครื่องอยู่แล้ว การรวมคลัสเตอร์จะช่วยขยายขีดความสามารถนี้ไปอีกขั้น ด้วยการรวมหน่วยความจำ GPU ของหลายระบบเข้าด้วยกันผ่านเครือข่ายท้องถิ่น ทำให้คุณสามารถเข้าถึงโมเดลขนาดใหญ่ยิ่งขึ้นที่มีความสามารถในการให้เหตุผลที่แข็งแกร่งกว่า การสร้างโค้ดที่ดีกว่า และความเข้าใจหลายภาษาที่ลึกซึ้งยิ่งขึ้น ทั้งหมดนี้บนฮาร์ดแวร์ของคุณเองทั้งสิ้น

คู่มือนี้จะสอนวิธีการรวมคลัสเตอร์ระบบ Ryzen AI Halo สี่ระบบโดยใช้ RPC engine ของ llama.cpp และรัน Kimi K2.6 ซึ่งเป็นโมเดล mixture-of-experts ขนาดใหญ่ ข้ามเครื่องทั้งสี่เครื่องด้วยการเร่งความเร็วจาก AMD ROCm™

## สิ่งที่คุณจะได้เรียนรู้

- วิธีขยายการจัดสรร VRAM บนระบบ Ryzen AI Halo
- การติดตั้ง llama.cpp พร้อมการรองรับ ROCm และ RPC
- การกำหนดค่า RPC worker และการเปิดใช้งาน distributed inference ข้ามสี่โหนด
- การรันโมเดลขนาด 1T พารามิเตอร์ข้ามระบบ Ryzen AI Halo สี่ระบบที่เชื่อมต่อผ่านเครือข่าย

## การตั้งค่าหน่วยความจำ

> **หมายเหตุ**: ทำขั้นตอนนี้ให้ครบทั้งสี่เครื่อง (เครื่อง 1 ถึงเครื่อง 4)

<!-- @os:windows -->
บน Windows หากต้องการรันโมเดลขนาดใหญ่ที่ต้องใช้หน่วยความจำมากขึ้น เราจำเป็นต้องใช้การจัดสรร AMD Variable Graphics Memory (iGPU VRAM)

สามารถทำได้โดยเปิดแผงควบคุม AMD Software: Adrenalin Edition และไปที่: `Performance > Tuning > AMD Variable Graphics Memory` ตั้งค่าเป็น **96 GB** โปรดรีบูตระบบเพื่อให้การเปลี่ยนแปลงมีผล

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
บน Linux, ROCm ใช้พูลหน่วยความจำระบบร่วมกัน และพูลนี้ถูกกำหนดค่าเริ่มต้นไว้ที่ครึ่งหนึ่งของหน่วยความจำระบบ

ปริมาณนี้สามารถเพิ่มได้โดยการเปลี่ยนการตั้งค่าหน้า Translation Table Manager (TTM) ของเคอร์เนล ด้วยคำแนะนำต่อไปนี้ AMD แนะนำให้ตั้งค่า VRAM ที่จัดสรรขั้นต่ำใน BIOS (0.5 GB)

* ติดตั้งยูทิลิตี pipx และเพิ่ม path สำหรับ wheel ที่ติดตั้งด้วย pipx เข้าไปใน system search path

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* ติดตั้ง wheel ของ amd-debug-tools จาก PyPI
  ```bash
  pipx install amd-debug-tools
  ```

* รันเครื่องมือ amd-ttm เพื่อสอบถามการตั้งค่าปัจจุบันสำหรับหน่วยความจำที่ใช้ร่วมกัน
  ```bash
  amd-ttm
  ```

* กำหนดค่าการตั้งค่าหน่วยความจำร่วมใหม่เป็น **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* รีบูตระบบเพื่อให้การเปลี่ยนแปลงมีผล


<!-- @os:end -->
<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์

<!-- @require:software-update -->
<!-- @device:end -->
## สิ่งที่ต้องมีก่อน

### ฮาร์ดแวร์

คู่มือนี้ต้องใช้หน่วย Ryzen AI Halo สี่หน่วยและสวิตช์ Ethernet หนึ่งตัว เชื่อมต่อในรูปแบบ star topology โดยแต่ละหน่วยเชื่อมต่อโดยตรงเข้ากับสวิตช์

| ส่วนประกอบ | จำนวน | คำอธิบาย |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | โหนดประมวลผลที่ประกอบเป็นคลัสเตอร์ |
| สวิตช์ Ethernet 10Gbps | 1 | สวิตช์ศูนย์กลางเพื่อให้หน่วย Ryzen AI Halo หลายโหนดสื่อสารกันได้ (อย่างน้อย 4 พอร์ต) |
| สายเคเบิล Ethernet | 4 | เชื่อมต่อหน่วย Halo แต่ละหน่วยเข้ากับสวิตช์ (แนะนำ Cat 7 หรือสูงกว่า) |

> **หมายเหตุ**: ต้องใช้พอร์ตสวิตช์ Ethernet สี่พอร์ตเพื่อเชื่อมต่อหน่วย Ryzen AI Halo สี่หน่วย และต้องมีพอร์ตที่ห้าหากคุณเข้าถึงโมเดลจากเครื่องไคลเอนต์แยกต่างหากแทนที่จะเป็นจากหนึ่งในหน่วย Halo

### ซอฟต์แวร์
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
โปรดติดตั้ง:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) พร้อม workload **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## การตั้งค่าฮาร์ดแวร์ทางกายภาพ

> **หมายเหตุ**: ทำขั้นตอนนี้ให้ครบทั้งสี่เครื่อง (เครื่อง 1 ถึงเครื่อง 4)

เชื่อมต่อหน่วย Ryzen AI Halo แต่ละหน่วยเข้ากับสวิตช์ Ethernet โดยใช้สายเคเบิล Cat 7 (หรือสูงกว่า) การทำเช่นนี้จะสร้างลิงก์ความเร็ว 10Gbps ที่ใช้สำหรับการสื่อสารความเร็วสูงระหว่างโหนดต่างๆ
<!-- @os:linux -->
### 1. กำหนดอินเทอร์เฟซเครือข่าย

บนแต่ละเครื่อง ให้ค้นหาชื่ออินเทอร์เฟซเครือข่ายและจดบันทึกไว้ (จะเรียกว่า `IFNAME` ในเนื้อหาด้านล่าง) รันคำสั่ง:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

คำสั่งนี้จะแสดงชื่ออินเทอร์เฟซโดยตรง ตัวอย่างเช่น:

```bash
enp191s0
```

### 2. ตรวจสอบความเร็วลิงก์เครือข่าย

ยืนยันว่าลิงก์ทำงานและวิ่งด้วยความเร็วเต็มที่โดยการตรวจสอบความเร็วของอินเทอร์เฟซของคุณ:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **หมายเหตุ**: แทนที่ `<IFNAME>` ด้วยชื่ออินเทอร์เฟซเอาต์พุตจาก [1. กำหนดอินเทอร์เฟซเครือข่าย](#1-determine-network-interfaces)

คุณควรเห็นความเร็วเป็น `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **หมายเหตุ**: หากความเร็วต่ำกว่า `10000Mb/s` หรือลิงก์ไม่ขึ้น ให้ตรวจสอบการเชื่อมต่อสายเคเบิลและยืนยันว่าพอร์ตสวิตช์ถูกตั้งค่าเป็น 10Gbps สวิตช์บางรุ่นต้องปิดการทำงาน auto-negotiation และตั้งค่าความเร็วลิงก์ด้วยตนเอง โปรดดูเอกสารประกอบของสวิตช์ของคุณ

<!-- @os:end -->

<!-- @os:windows -->
### ตรวจสอบความเร็วลิงก์เครือข่าย

บนแต่ละเครื่อง ให้ตรวจสอบความเร็วลิงก์ของอินเทอร์เฟซเครือข่ายของคุณ:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

อินเทอร์เฟซ Ethernet ของคุณควรอยู่ในสถานะ `Up` และทำงานที่ `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **หมายเหตุ**: หากความเร็วต่ำกว่า `10 Gbps` หรือลิงก์ไม่ขึ้น ให้ตรวจสอบการเชื่อมต่อสายเคเบิลและยืนยันว่าพอร์ตสวิตช์ถูกตั้งค่าเป็น 10Gbps สวิตช์บางรุ่นต้องปิดการทำงาน auto-negotiation และตั้งค่าความเร็วลิงก์ด้วยตนเอง โปรดดูเอกสารประกอบของสวิตช์ของคุณ

<!-- @os:end -->

## การติดตั้ง llama.cpp

> **หมายเหตุ**: ทำขั้นตอนนี้ให้ครบทั้งสี่เครื่อง (เครื่อง 1 ถึงเครื่อง 4)

มีตัวเลือกการติดตั้งสองแบบ:

- [ตัวเลือกที่ 1: Lemonade SDK (แนะนำ)](#option-1-lemonade-sdk-recommended) - ไบนารีที่สร้างไว้ล่วงหน้า ตั้งค่าได้เร็วที่สุด
- [ตัวเลือกที่ 2: การสร้างจากซอร์สโค้ดด้วยตนเอง](#option-2-manual-source-build) - สร้างจากซอร์สโค้ดโดยควบคุม build flags ได้อย่างเต็มที่

### ตัวเลือกที่ 1: Lemonade SDK (แนะนำ)

Lemonade SDK มอบ nightly build ของ llama.cpp พร้อมการเร่งความเร็ว AMD ROCm 7 ที่มุ่งเป้าไปยัง GPU เช่น gfx1151 (Strix Halo / Ryzen AI Max+ 395) และสถาปัตยกรรม Radeon รุ่นล่าสุดอื่นๆ

<!-- @os:windows -->
#### ขั้นตอนที่ 1: ดาวน์โหลดไบนารีที่สร้างไว้ล่วงหน้า

ไปที่หน้าเผยแพร่เวอร์ชันล่าสุดและดาวน์โหลดไฟล์ที่ตรงกับแพลตฟอร์มและเป้าหมาย GPU ของคุณ:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

ดาวน์โหลดไฟล์ชื่อ `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (โดยที่ `xxxx` คือหมายเลขบิลด์)

#### ขั้นตอนที่ 2: แตกไฟล์ไบนารี

แตกไฟล์ที่ดาวน์โหลดมา:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

ไดเรกทอรีนี้ตอนนี้มีไบนารีที่รองรับ ROCm ของ `llama-cli.exe`, `llama-server.exe` และ `ggml-rpc-server.exe` ที่คอมไพล์ไว้ล่วงหน้าสำหรับระบบ Ryzen AI Halo ของคุณ

#### ขั้นตอนที่ 3: ตรวจสอบการตรวจจับ GPU

```bash
.\llama-cli.exe --list-devices
```

ผลลัพธ์ที่คาดหวัง:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### ขั้นตอนที่ 1: ดาวน์โหลดไบนารีที่สร้างไว้ล่วงหน้า

ไปที่หน้าเผยแพร่เวอร์ชันล่าสุดและดาวน์โหลดไฟล์ที่ตรงกับแพลตฟอร์มและเป้าหมาย GPU ของคุณ:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

ดาวน์โหลดไฟล์ชื่อ `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (โดยที่ `xxxx` คือหมายเลขบิลด์)

#### ขั้นตอนที่ 2: แตกไฟล์และเตรียมไบนารี

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

ไดเรกทอรีนี้ตอนนี้มีไบนารีที่รองรับ ROCm ของ `llama-cli`, `llama-server` และ `rpc-server` ที่คอมไพล์ไว้ล่วงหน้าสำหรับระบบ Ryzen AI Halo ของคุณ

#### ขั้นตอนที่ 3: ตรวจสอบการตรวจจับ GPU

```bash
./llama-cli --list-devices
```

ผลลัพธ์ที่คาดหวัง:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
เมื่อเตรียม llama.cpp บนแต่ละโหนดเรียบร้อยแล้ว ให้ดำเนินการต่อที่ [การดาวน์โหลดโมเดล](#downloading-the-model)

### ตัวเลือกที่ 2: การสร้างจากซอร์สโค้ดด้วยตนเอง

<!-- @os:windows -->
#### ขั้นตอนที่ 1: สร้าง llama.cpp

เปิด **x64 Native Tools Command Prompt** (ที่ติดตั้งมาพร้อมกับ Visual Studio Build Tools) แล้วโคลนที่เก็บข้อมูล:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

เพิ่ม HIP ลงในพาธของคุณและสร้างด้วยการรองรับ ROCm และ RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| แฟล็กในการสร้าง | วัตถุประสงค์ |
|-----------|---------|
| `-DGGML_HIP=ON` | เปิดใช้งานสแตกซอฟต์แวร์ ROCm/HIP |
| `-DGGML_RPC=ON` | เปิดใช้งาน RPC สำหรับการอนุมานแบบกระจาย |
| `-DGPU_TARGETS=gfx1151` | กำหนดเป้าหมายไปที่ GPU ของ Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | ใช้ระบบสร้าง Ninja |

#### ขั้นตอนที่ 2: ตรวจสอบการตรวจจับ GPU

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

ผลลัพธ์ที่คาดหวัง:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### ขั้นตอนที่ 3: เพิ่ม HIP ลงในพาธผู้ใช้ของคุณ

ขั้นตอนการสร้างข้างต้นตั้งค่า `%HIP_PATH%\bin` สำหรับเซสชันปัจจุบันเท่านั้น เพื่อให้ไลบรารี HIP พร้อมใช้งานในเทอร์มินัลใด ๆ (ไม่ใช่เฉพาะ x64 Native Tools Command Prompt) ให้เพิ่มไว้ใน `PATH` ผู้ใช้ของคุณอย่างถาวร:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

เมื่อเตรียม llama.cpp บนแต่ละโหนดเรียบร้อยแล้ว ให้ดำเนินการต่อที่ [การดาวน์โหลดโมเดล](#downloading-the-model)
<!-- @os:end -->

<!-- @os:linux -->
#### ขั้นตอนที่ 1: สร้าง llama.cpp

โคลนที่เก็บข้อมูล:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

สร้างด้วยการรองรับ ROCm และ RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| แฟล็กในการสร้าง | วัตถุประสงค์ |
|-----------|---------|
| `-DGGML_HIP=ON` | เปิดใช้งานสแตกซอฟต์แวร์ ROCm |
| `-DGGML_RPC=ON` | เปิดใช้งาน RPC สำหรับการอนุมานแบบกระจาย |
| `-DAMDGPU_TARGETS="gfx1151"` | กำหนดเป้าหมายไปที่ GPU ของ Ryzen AI Halo (Radeon 8060s) |

สำหรับตัวเลือกการสร้างเพิ่มเติม โปรดดู [เอกสารการสร้าง llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md)

#### ขั้นตอนที่ 2: ตรวจสอบการตรวจจับ GPU

```bash
cd rocm/bin
./llama-cli --list-devices
```

ผลลัพธ์ที่คาดหวัง:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

เมื่อเตรียม llama.cpp บนแต่ละโหนดเรียบร้อยแล้ว ให้ดำเนินการต่อที่ [การดาวน์โหลดโมเดล](#downloading-the-model)
<!-- @os:end -->

## การดาวน์โหลดโมเดล

คู่มือนี้ใช้ [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) ในควอนไทเซชัน `UD-Q2_K_XL` จาก [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL) ควอนไทเซชันนี้พอดีกับหน่วยความจำ GPU รวมของโหนด Ryzen AI Halo ทั้งสี่โหนด

ดาวน์โหลดไฟล์ GGUF โดยใช้ Hugging Face CLI:
<!-- @os:linux -->
```bash
pip install huggingface-hub
hf download unsloth/Kimi-K2.6-GGUF --include "UD-Q2_K_XL/*" --local-dir Kimi-K2.6-GGUF
```
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/Kimi-K2.6-GGUF --include "UD-Q2_K_XL/*" --local-dir Kimi-K2.6-GGUF
```
<!-- @os:end -->

> **หมายเหตุ**: การดาวน์โหลดโมเดลต้องดำเนินการให้เสร็จสิ้นบนเครื่องที่ 1 (ตัวควบคุม) โหนดผู้ปฏิบัติงาน RPC (เครื่องที่ 2, 3 และ 4) ไม่จำเป็นต้องมีสำเนาไฟล์โมเดลในเครื่อง

## การเปิดใช้งานโมเดลบนคลัสเตอร์

เอนจิน RPC (Remote Procedure Call) ของ llama.cpp ช่วยให้อินสแตนซ์ llama.cpp เดียวสามารถถ่ายโอนเลเยอร์ของโมเดลไปยังผู้ปฏิบัติงานระยะไกลผ่านเครือข่ายได้ เครื่องหนึ่งทำหน้าที่เป็น **ตัวควบคุม** (เครื่องที่ 1) ซึ่งจัดการการแปลงเป็นโทเค็น การจัดตารางเวลา และการประสานงาน ส่วนอีกสามเครื่องแต่ละเครื่องจะรัน **RPC server** แบบเบา (เครื่องที่ 2, 3 และ 4) ที่เปิดเผยหน่วยความจำ GPU และการประมวลผลให้กับตัวควบคุม

ในเวลาโหลด llama.cpp จะแบ่งโมเดลออกเป็นส่วน ๆ ข้ามทั้งสี่โหนด เมื่อโหลดเสร็จแล้ว การอนุมานจะดำเนินไปราวกับว่ากำลังรันบนตัวเร่งความเร็วเดียว RPC จะจัดการการถ่ายโอนเทนเซอร์และการซิงโครไนซ์อยู่เบื้องหลัง

### ขั้นตอนที่ 1: เริ่มต้น RPC Servers (เครื่องที่ 2, 3 และ 4)

บนแต่ละเครื่องในเครื่องที่ 2, 3 และ 4 ให้เริ่มต้น RPC server เพื่อเปิดเผยทรัพยากร GPU ของตนให้กับตัวควบคุม:
<!-- @os:linux -->
```bash
./ggml-rpc-server -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
.\ggml-rpc-server.exe -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

| แฟล็ก | วัตถุประสงค์ |
|------|---------|
| `-p` | พอร์ตที่จะใช้กระจายสัญญาณ RPC server |
| `-c` | เปิดใช้งานแคชในเครื่องสำหรับเทนเซอร์ขนาดใหญ่ เพื่อหลีกเลี่ยงการถ่ายโอนผ่านเครือข่ายซ้ำ ๆ ระหว่างการโหลดโมเดล |
| `--host` | ที่อยู่ IP ที่จะผูก RPC server ไว้ด้วย (`0.0.0.0` สำหรับทุกอินเทอร์เฟซ) |

สำหรับตัวเลือกเพิ่มเติม โปรดดู [เอกสาร RPC ของ llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md)

### ขั้นตอนที่ 2: เปิดใช้งานโมเดล (เครื่องที่ 1)

เมื่อ RPC server กำลังทำงานอยู่บนเครื่องที่ 2, 3 และ 4 แล้ว ให้เปิดใช้งานการอนุมานจากเครื่องที่ 1 โดยใช้ `llama-cli` หรือ `llama-server` อย่างใดอย่างหนึ่ง
#### llama-cli

`llama-cli` มอบอินเทอร์เฟซแบบเทอร์มินัลสำหรับโต้ตอบกับโมเดลโดยตรง เหมาะอย่างยิ่งสำหรับการทำเบนช์มาร์ก การดีบัก และการทดลองในระดับล่าง

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/Kimi-K2.6-GGUF/UD-Q2_K_XL/Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  -b 4096 \
  -ub 4096 \
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **การหา `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: บนเครื่อง Machine 2, 3 และ 4 แต่ละเครื่อง ให้รันคำสั่ง `hostname -I | awk '{print $1}'` เพื่อหาที่อยู่ IP ภายในของเครื่องนั้น
<!-- @os:end -->

<!-- @os:windows -->
> **หมายเหตุ**: รันคำสั่งนี้ใน Terminal (Powershell)

```powershell
.\llama-cli.exe `
  -m C:\path\to\Kimi-K2.6-GGUF\UD-Q2_K_XL\Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  -b 4096 `
  -ub 4096 `
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **การหา `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: บนเครื่อง Machine 2, 3 และ 4 แต่ละเครื่อง ให้รันคำสั่ง `ipconfig | findstr /C:"IPv4"` ใน Terminal (Powershell) เพื่อหาที่อยู่ IP ภายในของเครื่องนั้น

<!-- @os:end -->

เมื่อทำงานแล้ว `llama-cli` จะแสดงความคืบหน้าในการโหลดโมเดล และเข้าสู่พรอมป์แบบโต้ตอบซึ่งคุณสามารถแชทกับโมเดลได้โดยตรง:

![llama-cli กำลังรัน Kimi K2.6 ข้ามสี่โหนด](assets/llama-cli-example.png)

#### llama-server

`llama-server` เปิดให้ใช้งานเอนจินการอนุมานตัวเดียวกันผ่านกระบวนการเซิร์ฟเวอร์ที่ทำงานต่อเนื่อง พร้อมทั้งมีเว็บ UI ในตัวและ HTTP API ที่รองรับ OpenAI นี่คืออินเทอร์เฟซที่แนะนำสำหรับการใช้งานระยะยาว การเข้าถึงแบบหลายผู้ใช้ และการผสานรวมกับเครื่องมือภายนอก

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/Kimi-K2.6-GGUF/UD-Q2_K_XL/Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  -b 4096 \
  -ub 4096 \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **การหา `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: บนเครื่อง Machine 2, 3 และ 4 แต่ละเครื่อง ให้รันคำสั่ง `hostname -I | awk '{print $1}'` เพื่อหาที่อยู่ IP ภายในของเครื่องนั้น
<!-- @os:end -->

<!-- @os:windows -->
> **หมายเหตุ**: รันคำสั่งนี้ใน Terminal (Powershell)

```powershell
.\llama-server.exe `
  -m C:\path\to\Kimi-K2.6-GGUF\UD-Q2_K_XL\Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  -b 4096 `
  -ub 4096 `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **การหา `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: บนเครื่อง Machine 2, 3 และ 4 แต่ละเครื่อง ให้รันคำสั่ง `ipconfig | findstr /C:"IPv4"` ใน Terminal (Powershell) เพื่อหาที่อยู่ IP ภายในของเครื่องนั้น
<!-- @os:end -->

เมื่อเริ่มทำงานแล้ว ให้เปิด `http://<HOST_IP>:8081` ในเบราว์เซอร์ของคุณเพื่อเข้าถึงเว็บ UI ในตัว ซึ่งให้อินเทอร์เฟซแชทผ่านเบราว์เซอร์สำหรับโต้ตอบกับโมเดล:

![เว็บ UI ของ llama-server กำลังรัน Kimi K2.6 ข้ามสี่โหนด](assets/llama-server-example.png)

<!-- @os:linux -->
> **การหา `<HOST_IP>`**: บน Machine 1 ให้รันคำสั่ง `hostname -I | awk '{print $1}'` เพื่อหาที่อยู่ IP ภายในของเครื่องนั้น
<!-- @os:end -->

<!-- @os:windows -->
> **การหา `<HOST_IP>`**: บน Machine 1 ให้รันคำสั่ง `ipconfig | findstr /C:"IPv4"` ใน Terminal (Powershell) เพื่อหาที่อยู่ IP ภายในของเครื่องนั้น
<!-- @os:end -->

#### รายการอ้างอิงพารามิเตอร์

| แฟล็ก | วัตถุประสงค์ |
|------|---------|
| `-m` | เส้นทางไปยังไฟล์โมเดล GGUF (ใช้ชาร์ดแรก `00001-of-00008`) |
| `-c` | ขนาดคอนเท็กซ์เป็นโทเค็น ค่ายิ่งมากยิ่งใช้หน่วยความจำมากขึ้น |
| `-fa on` | เปิดใช้งาน rocWMMA Flash Attention เพื่อประสิทธิภาพที่ดีขึ้นบน AMD GPU |
| `-ngl 999` | ถ่ายโอนเลเยอร์ทั้งหมดของโมเดลไปยัง GPU |
| `-lm none` | ตั้งค่าโหมดการโหลดโมเดลเป็น `none` ปิดใช้งานการทำ memory-mapping เพื่อลดเวลาโหลดเมื่อขนาดโมเดลเกิน RAM ของระบบแต่ยังพอดีกับ VRAM |
| `-b` | ขนาดแบตช์เชิงตรรกะเป็นโทเค็น การตั้งค่าเป็น 4096 ช่วยปรับสมดุลระหว่างปริมาณงานและการใช้หน่วยความจำในแต่ละโหนด |
| `-ub` | ขนาดแบตช์ทางกายภาพ (ไมโครแบตช์) สำหรับการประมวลผลพรอมป์ การตั้งค่าให้ตรงกับ `-b` จะช่วยหลีกเลี่ยงโอเวอร์เฮดจากการแบ่งชิ้นที่ไม่จำเป็น |
| `--host` | IP ที่จะผูก `llama-server` เข้าไว้ด้วย (สำหรับ `llama-server` เท่านั้น) |
| `--port` | พอร์ตที่จะใช้ให้บริการ HTTP API (สำหรับ `llama-server` เท่านั้น) |
| `--rpc` | รายการเอนด์พอยต์ของ RPC worker คั่นด้วยจุลภาค (`IP:port`) |

สำหรับการใช้งานพารามิเตอร์แบบเต็ม โปรดดู [เอกสารประกอบ llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) และ [เอกสารประกอบ llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)

## ขั้นตอนถัดไป

- **เชื่อมต่อแอปพลิเคชันของบุคคลที่สาม**: `llama-server` เปิดให้ใช้งาน API ที่รองรับ OpenAI ชี้แอปพลิเคชันที่รองรับ OpenAI ใด ๆ (เช่น Open WebUI) ไปที่ `http://<HOST_IP>:8081` พร้อมด้วยคีย์ API สำหรับใส่แทนตัวใด ๆ (เช่น `none`) เพื่อเชื่อมต่อกับคลัสเตอร์ของคุณ
- **สำรวจโมเดลอื่น ๆ**: เรียกดู GGUF แบบควอนไทซ์บน [Hugging Face](https://huggingface.co/models?search=gguf) เพื่อค้นหาโมเดลที่มีขนาดพอดีกับหน่วยความจำ GPU รวมของคลัสเตอร์ของคุณ
- **ขยายขนาดเกินกว่าสี่โหนด**: เพิ่มระบบ Ryzen AI Halo เพิ่มเติมในฐานะ RPC worker เพิ่มเติมเพื่อเข้าถึงโมเดลที่มีขนาดเกินกว่า 1 ล้านล้านพารามิเตอร์ ส่งเอนด์พอยต์เพิ่มเติมไปยัง `--rpc` เป็นรายการคั่นด้วยจุลภาค (เช่น `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)