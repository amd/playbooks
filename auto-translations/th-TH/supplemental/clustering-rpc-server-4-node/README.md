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

# การจัดคลัสเตอร์ Ryzen™ AI Halo สี่เครื่องด้วย RPC

## ภาพรวม

Ryzen™ AI Halo ของคุณสามารถรันโมเดลภาษาขนาดใหญ่ในเครื่องได้อยู่แล้ว การจัดคลัสเตอร์จะช่วยขยายขีดความสามารถนี้ไปอีกขั้น ด้วยการรวมหน่วยความจำ GPU ของหลายระบบเข้าด้วยกันผ่านเครือข่ายท้องถิ่น ทำให้คุณสามารถเข้าถึงโมเดลที่ใหญ่ยิ่งขึ้น ซึ่งมีความสามารถในการให้เหตุผลที่แข็งแกร่งขึ้น การสร้างโค้ดที่ดีขึ้น และความเข้าใจหลายภาษาที่ลึกซึ้งยิ่งขึ้น โดยทั้งหมดนี้ทำงานบนฮาร์ดแวร์ของคุณเองอย่างสมบูรณ์

คู่มือนี้จะสอนวิธีการจัดคลัสเตอร์ระบบ Ryzen AI Halo สี่เครื่องโดยใช้ RPC engine ของ llama.cpp และรัน Kimi K2.6 ซึ่งเป็นโมเดล mixture-of-experts ขนาดใหญ่ ข้ามเครื่องทั้งสี่เครื่องพร้อมการเร่งความเร็วด้วย AMD ROCm™

## สิ่งที่คุณจะได้เรียนรู้

- วิธีขยายการจัดสรร VRAM บนระบบ Ryzen AI Halo
- การติดตั้ง llama.cpp พร้อมการรองรับ ROCm และ RPC
- การกำหนดค่า RPC workers และการเรียกใช้การอนุมานแบบกระจายบนสี่โหนด
- การรันโมเดลขนาด 1T พารามิเตอร์บนระบบ Ryzen AI Halo สี่เครื่องที่เชื่อมต่อผ่านเครือข่าย

## การตั้งค่าหน่วยความจำ

> **หมายเหตุ**: ทำขั้นตอนนี้ให้ครบทั้งสี่เครื่อง (เครื่องที่ 1 ถึงเครื่องที่ 4)

<!-- @os:windows -->
บน Windows หากต้องการรันโมเดลขนาดใหญ่ที่ต้องการหน่วยความจำสูงขึ้น เราจำเป็นต้องใช้การจัดสรร AMD Variable Graphics Memory (iGPU VRAM)

สามารถทำได้โดยเปิดแผงควบคุม AMD Software: Adrenalin Edition แล้วไปที่: `Performance > Tuning > AMD Variable Graphics Memory` ตั้งค่าเป็น **96 GB** จากนั้นรีบูตระบบเพื่อให้การเปลี่ยนแปลงมีผล

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
บน Linux นั้น ROCm จะใช้พูลหน่วยความจำระบบร่วมกัน (shared system memory pool) และพูลนี้ถูกกำหนดค่าเริ่มต้นไว้ที่ครึ่งหนึ่งของหน่วยความจำระบบ

สามารถเพิ่มปริมาณนี้ได้โดยการเปลี่ยนการตั้งค่าเพจของ Translation Table Manager (TTM) ของเคอร์เนล ตามคำแนะนำต่อไปนี้ AMD แนะนำให้ตั้งค่า VRAM เฉพาะขั้นต่ำใน BIOS (0.5 GB)

* ติดตั้งยูทิลิตี pipx และเพิ่มพาธสำหรับ wheel ที่ติดตั้งโดย pipx ลงในพาธค้นหาของระบบ

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* ติดตั้ง wheel amd-debug-tools จาก PyPI
  ```bash
  pipx install amd-debug-tools
  ```

* รันเครื่องมือ amd-ttm เพื่อตรวจสอบการตั้งค่าปัจจุบันสำหรับหน่วยความจำที่ใช้ร่วมกัน
  ```bash
  amd-ttm
  ```

* กำหนดค่าการตั้งค่าหน่วยความจำที่ใช้ร่วมกันใหม่เป็น **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* รีบูตระบบเพื่อให้การเปลี่ยนแปลงมีผล


<!-- @os:end -->
<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์

<!-- @require:software-update -->
<!-- @device:end -->
## ข้อกำหนดเบื้องต้น

### ฮาร์ดแวร์

คู่มือนี้ต้องใช้หน่วย Ryzen AI Halo สี่เครื่องและสวิตช์ Ethernet หนึ่งตัว เชื่อมต่อในรูปแบบโทโพโลยีสตาร์ (star topology) โดยแต่ละเครื่องเชื่อมต่อโดยตรงเข้ากับสวิตช์

| ส่วนประกอบ | จำนวน | คำอธิบาย |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | โหนดประมวลผลที่ประกอบกันเป็นคลัสเตอร์ |
| สวิตช์ Ethernet 10Gbps | 1 | สวิตช์ศูนย์กลางเพื่อให้การสื่อสารระหว่างหลายโหนดของ Ryzen AI Halo เป็นไปได้ (อย่างน้อย 4 พอร์ต) |
| สาย Ethernet | 4 | เชื่อมต่อแต่ละหน่วย Halo เข้ากับสวิตช์ (แนะนำ Cat 7 หรือสูงกว่า) |

> **หมายเหตุ**: ต้องใช้พอร์ตสวิตช์ Ethernet สี่พอร์ตเพื่อเชื่อมต่อหน่วย Ryzen AI Halo ทั้งสี่เครื่อง และต้องใช้พอร์ตที่ห้าหากคุณเข้าถึงโมเดลจากเครื่องไคลเอนต์แยกต่างหากแทนที่จะเข้าถึงจากหนึ่งในหน่วย Halo

### ซอฟต์แวร์
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
โปรดติดตั้ง:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) พร้อมชุดงาน **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## การตั้งค่าฮาร์ดแวร์ทางกายภาพ

> **หมายเหตุ**: ทำขั้นตอนนี้ให้ครบทั้งสี่เครื่อง (เครื่องที่ 1 ถึงเครื่องที่ 4)

เชื่อมต่อหน่วย Ryzen AI Halo แต่ละเครื่องเข้ากับสวิตช์ Ethernet โดยใช้สาย Cat 7 (หรือสูงกว่า) ซึ่งจะสร้างลิงก์ 10Gbps ที่ใช้สำหรับการสื่อสารความเร็วสูงระหว่างโหนดต่าง ๆ
<!-- @os:linux -->
### 1. การกำหนดอินเทอร์เฟซเครือข่าย

บนแต่ละเครื่อง ให้ค้นหาชื่ออินเทอร์เฟซเครือข่ายของเครื่องนั้นและจดบันทึกไว้ (จะเรียกว่า `IFNAME` ด้านล่างนี้) รันคำสั่ง:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

คำสั่งนี้จะแสดงชื่ออินเทอร์เฟซโดยตรง ตัวอย่างเช่น:

```bash
enp191s0
```

### 2. ตรวจสอบความเร็วลิงก์เครือข่าย

ยืนยันว่าลิงก์ทำงานอยู่และทำงานที่ความเร็วเต็มที่โดยตรวจสอบความเร็วของอินเทอร์เฟซของคุณ:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **หมายเหตุ**: แทนที่ `<IFNAME>` ด้วยชื่ออินเทอร์เฟซขาออกจาก [1. การกำหนดอินเทอร์เฟซเครือข่าย](#1-determine-network-interfaces)

คุณควรเห็นความเร็วที่ `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **หมายเหตุ**: หากความเร็วต่ำกว่า `10000Mb/s` หรือลิงก์ไม่ขึ้น ให้ตรวจสอบการเชื่อมต่อสายและยืนยันว่าพอร์ตสวิตช์ถูกตั้งค่าเป็น 10Gbps สวิตช์บางรุ่นต้องปิดการต่อรองอัตโนมัติ (auto-negotiation) และตั้งค่าความเร็วลิงก์ด้วยตนเอง โปรดดูเอกสารประกอบของสวิตช์ของคุณ

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

> **หมายเหตุ**: หากความเร็วต่ำกว่า `10 Gbps` หรือลิงก์ไม่ขึ้น ให้ตรวจสอบการเชื่อมต่อสายและยืนยันว่าพอร์ตสวิตช์ถูกตั้งค่าเป็น 10Gbps สวิตช์บางรุ่นต้องปิดการต่อรองอัตโนมัติ (auto-negotiation) และตั้งค่าความเร็วลิงก์ด้วยตนเอง โปรดดูเอกสารประกอบของสวิตช์ของคุณ

<!-- @os:end -->

## การติดตั้ง llama.cpp

> **หมายเหตุ**: ทำขั้นตอนนี้ให้ครบทั้งสี่เครื่อง (เครื่องที่ 1 ถึงเครื่องที่ 4)

มีตัวเลือกการติดตั้งสองแบบให้เลือก:

- [ตัวเลือกที่ 1: Lemonade SDK (แนะนำ)](#option-1-lemonade-sdk-recommended) - ไบนารีที่สร้างไว้ล่วงหน้า ตั้งค่าได้เร็วที่สุด
- [ตัวเลือกที่ 2: สร้างจากซอร์สโค้ดด้วยตนเอง](#option-2-manual-source-build) - สร้างจากซอร์สโค้ดโดยควบคุมแฟล็กการสร้างได้อย่างเต็มที่

### ตัวเลือกที่ 1: Lemonade SDK (แนะนำ)

Lemonade SDK มีการสร้างรุ่นรายคืน (nightly builds) ของ llama.cpp พร้อมการเร่งความเร็วด้วย AMD ROCm 7 โดยรองรับ GPU เช่น gfx1151 (Strix Halo / Ryzen AI Max+ 395) และสถาปัตยกรรม Radeon รุ่นล่าสุดอื่น ๆ

<!-- @os:windows -->
#### ขั้นตอนที่ 1: ดาวน์โหลดไบนารีที่สร้างไว้ล่วงหน้า

ไปที่หน้าเผยแพร่เวอร์ชันล่าสุดและดาวน์โหลดไฟล์เก็บถาวรที่ตรงกับแพลตฟอร์มและเป้าหมาย GPU ของคุณ:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

ดาวน์โหลดไฟล์ชื่อ `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (โดยที่ `xxxx` คือหมายเลขบิลด์)

#### ขั้นตอนที่ 2: แตกไฟล์ไบนารี

แตกไฟล์เก็บถาวรที่ดาวน์โหลดมา:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

ไดเรกทอรีนี้จะมีบิลด์ที่รองรับ ROCm ของ `llama-cli.exe`, `llama-server.exe` และ `ggml-rpc-server.exe` ซึ่งคอมไพล์ไว้ล่วงหน้าสำหรับระบบ Ryzen AI Halo ของคุณ

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

ไปที่หน้าเผยแพร่เวอร์ชันล่าสุดและดาวน์โหลดไฟล์เก็บถาวรที่ตรงกับแพลตฟอร์มและเป้าหมาย GPU ของคุณ:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

ดาวน์โหลดไฟล์ชื่อ `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (โดยที่ `xxxx` คือหมายเลขบิลด์)

#### ขั้นตอนที่ 2: แตกไฟล์และเตรียมไบนารี

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

ไดเรกทอรีนี้จะมีบิลด์ที่รองรับ ROCm ของ `llama-cli`, `llama-server` และ `rpc-server` ซึ่งคอมไพล์ไว้ล่วงหน้าสำหรับระบบ Ryzen AI Halo ของคุณ

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
เมื่อเตรียม llama.cpp ในแต่ละโหนดเรียบร้อยแล้ว ให้ดำเนินการต่อที่ [การดาวน์โหลดโมเดล](#downloading-the-model)

### ตัวเลือกที่ 2: การสร้างซอร์สโค้ดด้วยตนเอง

<!-- @os:windows -->
#### ขั้นตอนที่ 1: สร้าง llama.cpp

เปิด **x64 Native Tools Command Prompt** (ติดตั้งมาพร้อมกับ Visual Studio Build Tools) และโคลนที่เก็บโค้ด:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

เพิ่ม HIP ลงในพาธของคุณและสร้างโดยรองรับ ROCm และ RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| แฟล็กในการสร้าง | วัตถุประสงค์ |
|-----------|---------|
| `-DGGML_HIP=ON` | เปิดใช้งานสแตกซอฟต์แวร์ ROCm/HIP |
| `-DGGML_RPC=ON` | เปิดใช้งาน RPC สำหรับการอนุมานแบบกระจาย |
| `-DGPU_TARGETS=gfx1151` | กำหนดเป้าหมายเป็น GPU ของ Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | ใช้ระบบสร้างโค้ด Ninja |

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

ขั้นตอนการสร้างข้างต้นได้ตั้งค่า `%HIP_PATH%\bin` สำหรับเซสชันปัจจุบันเท่านั้น หากต้องการให้ไลบรารี HIP ใช้งานได้ในเทอร์มินัลใดก็ได้ (ไม่ใช่แค่ x64 Native Tools Command Prompt) ให้เพิ่มลงใน `PATH` ของผู้ใช้ของคุณอย่างถาวร:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

เมื่อเตรียม llama.cpp ในแต่ละโหนดเรียบร้อยแล้ว ให้ดำเนินการต่อที่ [การดาวน์โหลดโมเดล](#downloading-the-model)
<!-- @os:end -->

<!-- @os:linux -->
#### ขั้นตอนที่ 1: สร้าง llama.cpp

โคลนที่เก็บโค้ด:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

สร้างโดยรองรับ ROCm และ RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| แฟล็กในการสร้าง | วัตถุประสงค์ |
|-----------|---------|
| `-DGGML_HIP=ON` | เปิดใช้งานสแตกซอฟต์แวร์ ROCm |
| `-DGGML_RPC=ON` | เปิดใช้งาน RPC สำหรับการอนุมานแบบกระจาย |
| `-DAMDGPU_TARGETS="gfx1151"` | กำหนดเป้าหมายเป็น GPU ของ Ryzen AI Halo (Radeon 8060s) |

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

เมื่อเตรียม llama.cpp ในแต่ละโหนดเรียบร้อยแล้ว ให้ดำเนินการต่อที่ [การดาวน์โหลดโมเดล](#downloading-the-model)
<!-- @os:end -->

## การดาวน์โหลดโมเดล

คู่มือนี้ใช้ [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) ในรูปแบบการควอนไทซ์ `UD-Q2_K_XL` จาก [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL) การควอนไทซ์นี้พอดีกับหน่วยความจำ GPU รวมของโหนด Ryzen AI Halo สี่โหนด

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

> **หมายเหตุ**: การดาวน์โหลดโมเดลจะต้องดำเนินการให้เสร็จสิ้นบนเครื่องที่ 1 (ตัวควบคุม) โหนดผู้ปฏิบัติงาน RPC (เครื่องที่ 2, 3 และ 4) ไม่จำเป็นต้องมีสำเนาไฟล์โมเดลในเครื่อง

## การเรียกใช้โมเดลบนคลัสเตอร์

เอนจิน RPC (Remote Procedure Call) ของ llama.cpp ช่วยให้อินสแตนซ์ llama.cpp เดียวสามารถกระจายเลเยอร์ของโมเดลไปยังผู้ปฏิบัติงานระยะไกลผ่านเครือข่ายได้ เครื่องหนึ่งทำหน้าที่เป็น **ตัวควบคุม** (เครื่องที่ 1) จัดการโทเคไนซ์ การจัดตารางเวลา และการประสานงาน ส่วนอีกสามเครื่องแต่ละเครื่องจะรัน **เซิร์ฟเวอร์ RPC** ที่มีน้ำหนักเบา (เครื่องที่ 2, 3 และ 4) ซึ่งเปิดเผยหน่วยความจำ GPU และการประมวลผลของตนให้กับตัวควบคุม

ในเวลาที่โหลด llama.cpp จะแบ่งโมเดลออกเป็นส่วนๆ ไปยังโหนดทั้งสี่ เมื่อโหลดเสร็จแล้ว การอนุมานจะดำเนินไปราวกับว่ากำลังรันบนตัวเร่งความเร็วเดียว RPC จะจัดการการถ่ายโอนเทนเซอร์และการซิงโครไนซ์เบื้องหลังทั้งหมด

### ขั้นตอนที่ 1: เริ่มเซิร์ฟเวอร์ RPC (เครื่องที่ 2, 3 และ 4)

บนเครื่องที่ 2, 3 และ 4 แต่ละเครื่อง ให้เริ่มเซิร์ฟเวอร์ RPC เพื่อเปิดเผยทรัพยากร GPU ของตนให้กับตัวควบคุม:
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
| `-p` | พอร์ตในการเผยแพร่เซิร์ฟเวอร์ RPC |
| `-c` | เปิดใช้งานแคชในเครื่องสำหรับเทนเซอร์ขนาดใหญ่ เพื่อหลีกเลี่ยงการถ่ายโอนผ่านเครือข่ายซ้ำๆ ระหว่างการโหลดโมเดล |
| `--host` | ที่อยู่ IP ที่จะผูกเซิร์ฟเวอร์ RPC ไว้ (`0.0.0.0` สำหรับทุกอินเทอร์เฟซ) |

สำหรับตัวเลือกเพิ่มเติม โปรดดู [เอกสาร RPC ของ llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md)

### ขั้นตอนที่ 2: เรียกใช้โมเดล (เครื่องที่ 1)

เมื่อเซิร์ฟเวอร์ RPC ทำงานอยู่บนเครื่องที่ 2, 3 และ 4 แล้ว ให้เรียกใช้การอนุมานจากเครื่องที่ 1 โดยใช้ `llama-cli` หรือ `llama-server`
#### llama-cli

`llama-cli` มอบอินเทอร์เฟซแบบเทอร์มินัลสำหรับโต้ตอบกับโมเดลโดยตรง เหมาะอย่างยิ่งสำหรับการทดสอบประสิทธิภาพ การดีบัก และการทดลองในระดับล่าง

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

> **การค้นหา `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: บนแต่ละเครื่อง 2, 3 และ 4 ให้รันคำสั่ง `hostname -I | awk '{print $1}'` เพื่อค้นหาที่อยู่ IP ในเครือข่ายท้องถิ่น
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

> **การค้นหา `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: บนแต่ละเครื่อง 2, 3 และ 4 ให้รันคำสั่ง `ipconfig | findstr /C:"IPv4"` ใน Terminal (Powershell) เพื่อค้นหาที่อยู่ IP ในเครือข่ายท้องถิ่น

<!-- @os:end -->

เมื่อรันแล้ว `llama-cli` จะแสดงความคืบหน้าในการโหลดโมเดลและเข้าสู่พรอมต์แบบโต้ตอบซึ่งคุณสามารถแชทกับโมเดลได้โดยตรง:

![llama-cli กำลังรัน Kimi K2.6 บนสี่โหนด](assets/llama-cli-example.png)

#### llama-server

`llama-server` เปิดใช้งานเอนจินการอนุมานเดียวกันผ่านกระบวนการเซิร์ฟเวอร์ที่ทำงานต่อเนื่อง โดยมีเว็บ UI แบบผสานรวมและ API ผ่าน HTTP ที่เข้ากันได้กับ OpenAI นี่คืออินเทอร์เฟซที่แนะนำสำหรับการใช้งานระยะยาว การเข้าถึงจากผู้ใช้หลายคน และการผสานรวมกับเครื่องมือภายนอก

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

> **การค้นหา `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: บนแต่ละเครื่อง 2, 3 และ 4 ให้รันคำสั่ง `hostname -I | awk '{print $1}'` เพื่อค้นหาที่อยู่ IP ในเครือข่ายท้องถิ่น
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

> **การค้นหา `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: บนแต่ละเครื่อง 2, 3 และ 4 ให้รันคำสั่ง `ipconfig | findstr /C:"IPv4"` ใน Terminal (Powershell) เพื่อค้นหาที่อยู่ IP ในเครือข่ายท้องถิ่น
<!-- @os:end -->

เมื่อเริ่มทำงานแล้ว ให้เปิด `http://<HOST_IP>:8081` ในเบราว์เซอร์ของคุณเพื่อเข้าถึงเว็บ UI ในตัว ซึ่งมอบอินเทอร์เฟซแชทผ่านเบราว์เซอร์สำหรับโต้ตอบกับโมเดล:

![เว็บ UI ของ llama-server กำลังรัน Kimi K2.6 บนสี่โหนด](assets/llama-server-example.png)

<!-- @os:linux -->
> **การค้นหา `<HOST_IP>`**: บนเครื่องที่ 1 ให้รันคำสั่ง `hostname -I | awk '{print $1}'` เพื่อค้นหาที่อยู่ IP ในเครือข่ายท้องถิ่น
<!-- @os:end -->

<!-- @os:windows -->
> **การค้นหา `<HOST_IP>`**: บนเครื่องที่ 1 ให้รันคำสั่ง `ipconfig | findstr /C:"IPv4"` ใน Terminal (Powershell) เพื่อค้นหาที่อยู่ IP ในเครือข่ายท้องถิ่น
<!-- @os:end -->

#### ข้อมูลอ้างอิงพารามิเตอร์

| แฟล็ก | วัตถุประสงค์ |
|------|---------|
| `-m` | เส้นทางไปยังไฟล์โมเดล GGUF (ใช้ชาร์ดแรก `00001-of-00008`) |
| `-c` | ขนาดบริบทเป็นโทเคน ค่าที่มากขึ้นจะใช้หน่วยความจำมากขึ้น |
| `-fa on` | เปิดใช้งาน rocWMMA Flash Attention เพื่อประสิทธิภาพที่ดีขึ้นบน AMD GPU |
| `-ngl 999` | ถ่ายโอนเลเยอร์ทั้งหมดของโมเดลไปยัง GPU |
| `-lm none` | ตั้งค่าโหมดการโหลดโมเดลเป็น `none` ซึ่งจะปิดใช้งานการแมปหน่วยความจำเพื่อลดเวลาในการโหลดเมื่อขนาดโมเดลเกินกว่า RAM ของระบบแต่ยังพอดีกับ VRAM |
| `-b` | ขนาดแบตช์เชิงตรรกะเป็นโทเคน การตั้งค่าเป็น 4096 จะสร้างสมดุลระหว่างปริมาณงานและการใช้หน่วยความจำในโหนดต่างๆ |
| `-ub` | ขนาดแบตช์เชิงกายภาพ (ไมโคร) สำหรับการประมวลผลพรอมต์ การตั้งค่าให้ตรงกับ `-b` จะหลีกเลี่ยงภาระการแบ่งส่วนที่ไม่จำเป็น |
| `--host` | ที่อยู่ IP สำหรับผูก `llama-server` (เฉพาะ `llama-server` เท่านั้น) |
| `--port` | พอร์ตสำหรับให้บริการ HTTP API (เฉพาะ `llama-server` เท่านั้น) |
| `--rpc` | รายการปลายทางของ RPC worker คั่นด้วยจุลภาค (`IP:port`) |

สำหรับการใช้งานพารามิเตอร์ทั้งหมด โปรดดู [เอกสาร llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) และ [เอกสาร llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)

## ขั้นตอนถัดไป

- **เชื่อมต่อแอปพลิเคชันของบุคคลที่สาม**: `llama-server` เปิดใช้งาน API ที่เข้ากันได้กับ OpenAI ให้ชี้แอปพลิเคชันที่เข้ากันได้กับ OpenAI ใดๆ (เช่น Open WebUI) ไปที่ `http://<HOST_IP>:8081` พร้อมด้วยคีย์ API ตัวยึดตำแหน่งใดๆ (เช่น `none`) เพื่อเชื่อมต่อกับคลัสเตอร์ของคุณ
- **สำรวจโมเดลอื่นๆ**: เรียกดู GGUF ที่ถูกควอนไทซ์บน [Hugging Face](https://huggingface.co/models?search=gguf) เพื่อค้นหาโมเดลที่พอดีกับหน่วยความจำ GPU รวมของคลัสเตอร์ของคุณ
- **ขยายเกินสี่โหนด**: เพิ่มระบบ Ryzen AI Halo เพิ่มเติมเป็น RPC worker เพิ่มเติมเพื่อเข้าถึงโมเดลที่มีขนาดเกินระดับหนึ่งล้านล้านพารามิเตอร์ ส่งปลายทางเพิ่มเติมไปยัง `--rpc` เป็นรายการคั่นด้วยจุลภาค (เช่น `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)