<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# การจัดกลุ่ม Ryzen™ AI Halo สองเครื่องด้วย RPC

## ภาพรวม

Ryzen™ AI Halo ของคุณสามารถรันโมเดลภาษาขนาดใหญ่ในเครื่องได้อยู่แล้ว การจัดกลุ่มช่วยยกระดับความสามารถนี้ด้วยการรวม GPU memory ของหลายระบบผ่านเครือข่ายท้องถิ่น ทำให้คุณเข้าถึงโมเดลขนาดใหญ่ยิ่งขึ้นที่มีความสามารถในการอนุมานที่แข็งแกร่งกว่า สร้างโค้ดได้ดีกว่า และเข้าใจหลายภาษาได้ลึกซึ้งกว่า ทั้งหมดนี้บนฮาร์ดแวร์ของคุณเองทั้งสิ้น

Playbook นี้จะสอนวิธีจัดกลุ่ม Ryzen AI Halo สองระบบโดยใช้ RPC engine ของ llama.cpp และรัน GLM 4.7 ซึ่งเป็นโมเดลที่มีพารามิเตอร์ 358B บนทั้งสองเครื่องพร้อมการเร่งความเร็วด้วย AMD ROCm™

## สิ่งที่คุณจะได้เรียนรู้

- วิธีขยายการจัดสรร VRAM บนระบบ Ryzen AI Halo
- การติดตั้ง llama.cpp พร้อมการรองรับ ROCm และ RPC
- การกำหนดค่า RPC worker และการเปิดใช้งาน distributed inference ข้ามสองโหนด
- การรันโมเดลที่มีพารามิเตอร์ 358B บน Ryzen AI Halo สองเครื่องที่เชื่อมต่อกันผ่านเครือข่าย

## การตั้งค่าการกำหนดค่าหน่วยความจำ

> **หมายเหตุ**: ดำเนินการขั้นตอนนี้บนทั้ง Machine 1 และ Machine 2

<!-- @os:windows -->
บน Windows เพื่อรันโมเดลขนาดใหญ่ที่ต้องการหน่วยความจำสูงกว่า เราจำเป็นต้องใช้การจัดสรร AMD Variable Graphics Memory (iGPU VRAM)

ทำได้โดยเปิดแผงควบคุม AMD Software: Adrenalin Edition และไปที่: `Performance > Tuning > AMD Variable Graphics Memory` ตั้งค่าเป็น **96 GB** กรุณารีบูตระบบเพื่อให้การเปลี่ยนแปลงมีผล

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
บน Linux ROCm ใช้ shared system memory pool และ pool นี้ถูกกำหนดค่าเริ่มต้นไว้ที่ครึ่งหนึ่งของหน่วยความจำระบบ

สามารถเพิ่มปริมาณนี้ได้โดยการเปลี่ยนการตั้งค่า Translation Table Manager (TTM) page ของ kernel ตามคำแนะนำต่อไปนี้ AMD แนะนำให้ตั้งค่า minimum dedicated VRAM ใน BIOS (0.5 GB)

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

* กำหนดค่า shared memory settings ใหม่เป็น **120 GB**:
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

Playbook นี้ต้องการ Ryzen AI Halo สองหน่วยและ Ethernet switch หนึ่งตัว เชื่อมต่อในรูปแบบ star topology โดยแต่ละหน่วยเชื่อมต่อโดยตรงกับ switch

| ส่วนประกอบ | จำนวน | คำอธิบาย |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | โหนดประมวลผลที่ประกอบเป็นกลุ่ม |
| 10Gbps Ethernet switch | 1 | Switch กลางสำหรับการสื่อสารระหว่างโหนด Ryzen AI Halo หลายเครื่อง (อย่างน้อย 2 พอร์ต) |
| สาย Ethernet | 2 | เชื่อมต่อแต่ละหน่วย Halo กับ switch (แนะนำ Cat 7 หรือสูงกว่า) |

> **หมายเหตุ**: ต้องใช้พอร์ต Ethernet switch สองพอร์ตเพื่อเชื่อมต่อ Ryzen AI Halo สองหน่วย ต้องใช้พอร์ตที่สามหากคุณเข้าถึงโมเดลจากเครื่อง client แยกต่างหากแทนที่จะเป็นจากหน่วย Halo หน่วยใดหน่วยหนึ่ง

### ซอฟต์แวร์
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
กรุณาติดตั้ง:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) พร้อม workload **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## การตั้งค่าฮาร์ดแวร์จริง

> **หมายเหตุ**: ดำเนินการขั้นตอนนี้บนทั้ง Machine 1 และ Machine 2

เชื่อมต่อแต่ละหน่วย Ryzen AI Halo กับ Ethernet switch โดยใช้สาย Cat 7 (หรือสูงกว่า) ซึ่งจะสร้างลิงก์ 10Gbps ที่ใช้สำหรับการสื่อสารความเร็วสูงระหว่างโหนด
<!-- @os:linux -->
### 1. ระบุ Network Interface

บนแต่ละเครื่อง ค้นหาชื่อ network interface และจดบันทึกไว้ (จะถูกอ้างอิงด้านล่างในชื่อ `IFNAME`) รัน:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

คำสั่งนี้จะพิมพ์ชื่อ interface โดยตรง เช่น:

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

> **หมายเหตุ**: หากความเร็วต่ำกว่า `10000Mb/s` หรือลิงก์ไม่ขึ้น ให้ตรวจสอบการเชื่อมต่อสายและยืนยันว่าพอร์ต switch ถูกตั้งค่าเป็น 10Gbps บาง switch ต้องการปิดใช้งาน auto-negotiation และตั้งค่าความเร็วลิงก์ด้วยตนเอง โปรดดูเอกสารประกอบของ switch ของคุณ

<!-- @os:end -->

<!-- @os:windows -->
### ตรวจสอบความเร็วลิงก์เครือข่าย

บนแต่ละเครื่อง ตรวจสอบความเร็วลิงก์ของ network interface ของคุณ:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Ethernet interface ของคุณควรเป็น `Up` และรันที่ `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **หมายเหตุ**: หากความเร็วต่ำกว่า `10 Gbps` หรือลิงก์ไม่ขึ้น ให้ตรวจสอบการเชื่อมต่อสายและยืนยันว่าพอร์ต switch ถูกตั้งค่าเป็น 10Gbps บาง switch ต้องการปิดใช้งาน auto-negotiation และตั้งค่าความเร็วลิงก์ด้วยตนเอง โปรดดูเอกสารประกอบของ switch ของคุณ

<!-- @os:end -->

## การติดตั้ง llama.cpp

> **หมายเหตุ**: ดำเนินการขั้นตอนนี้บนทั้ง Machine 1 และ Machine 2

มีตัวเลือกการติดตั้งสองแบบ:

- [ตัวเลือกที่ 1: Lemonade SDK (แนะนำ)](#option-1-lemonade-sdk-recommended) - ไบนารีที่สร้างไว้ล่วงหน้า ตั้งค่าได้เร็วที่สุด
- [ตัวเลือกที่ 2: การสร้างจาก Source ด้วยตนเอง](#option-2-manual-source-build) - สร้างจาก source พร้อมการควบคุม build flags อย่างเต็มที่

### ตัวเลือกที่ 1: Lemonade SDK (แนะนำ)

Lemonade SDK มี nightly builds ของ llama.cpp พร้อมการเร่งความเร็วด้วย AMD ROCm 7 โดยกำหนดเป้าหมายที่ GPU เช่น gfx1151 (Strix Halo / Ryzen AI Max+ 395) และสถาปัตยกรรม Radeon ล่าสุดอื่นๆ

<!-- @os:windows -->
#### ขั้นตอนที่ 1: ดาวน์โหลดไบนารีที่สร้างไว้ล่วงหน้า

ไปที่หน้าเผยแพร่ล่าสุดและดาวน์โหลดไฟล์เก็บถาวรที่ตรงกับแพลตฟอร์มและเป้าหมาย GPU ของคุณ:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

ดาวน์โหลดไฟล์ชื่อ `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (โดยที่ `xxxx` คือหมายเลขบิลด์)

#### ขั้นตอนที่ 2: แตกไฟล์ไบนารี

แตกไฟล์เก็บถาวรที่ดาวน์โหลดมา:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

ไดเรกทอรีนี้ประกอบด้วยบิลด์ที่เปิดใช้งาน ROCm ของ `llama-cli.exe`, `llama-server.exe` และ `rpc-server.exe` ซึ่งคอมไพล์ไว้ล่วงหน้าสำหรับระบบ Ryzen AI Halo ของคุณ

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

ไปที่หน้าเผยแพร่ล่าสุดและดาวน์โหลดไฟล์เก็บถาวรที่ตรงกับแพลตฟอร์มและเป้าหมาย GPU ของคุณ:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

ดาวน์โหลดไฟล์ชื่อ `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (โดยที่ `xxxx` คือหมายเลขบิลด์)

#### ขั้นตอนที่ 2: แตกไฟล์และเตรียมไบนารี

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

ไดเรกทอรีนี้ประกอบด้วยบิลด์ที่เปิดใช้งาน ROCm ของ `llama-cli`, `llama-server` และ `rpc-server` ซึ่งคอมไพล์ไว้ล่วงหน้าสำหรับระบบ Ryzen AI Halo ของคุณ

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

### ตัวเลือกที่ 2: สร้างจากซอร์สโค้ดด้วยตนเอง

<!-- @os:windows -->
#### ขั้นตอนที่ 1: สร้าง llama.cpp

เปิด **x64 Native Tools Command Prompt** (ติดตั้งพร้อมกับ Visual Studio Build Tools) และโคลนที่เก็บโค้ด:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

เพิ่ม HIP ลงใน path ของคุณและสร้างด้วยการรองรับ ROCm และ RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| แฟล็กการสร้าง | วัตถุประสงค์ |
|-----------|---------|
| `-DGGML_HIP=ON` | เปิดใช้งานซอฟต์แวร์สแตก ROCm/HIP |
| `-DGGML_RPC=ON` | เปิดใช้งาน RPC สำหรับการอนุมานแบบกระจาย |
| `-DGPU_TARGETS=gfx1151` | กำหนดเป้าหมายเป็น GPU Ryzen AI Halo (Radeon 8060s) |
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

#### ขั้นตอนที่ 3: เพิ่ม HIP ลงใน User Path ของคุณ

ขั้นตอนการสร้างข้างต้นตั้งค่า `%HIP_PATH%\bin` สำหรับเซสชันปัจจุบันเท่านั้น เพื่อให้ไลบรารี HIP พร้อมใช้งานในเทอร์มินัลใดก็ได้ (ไม่ใช่แค่ x64 Native Tools Command Prompt) ให้เพิ่มลงใน `PATH` ของผู้ใช้อย่างถาวร:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

เมื่อเตรียม llama.cpp บนแต่ละโหนดเรียบร้อยแล้ว ให้ดำเนินการต่อที่ [การดาวน์โหลดโมเดล](#downloading-the-model)
<!-- @os:end -->

<!-- @os:linux -->
#### ขั้นตอนที่ 1: สร้าง llama.cpp

โคลนที่เก็บโค้ด:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

สร้างด้วยการรองรับ ROCm และ RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| แฟล็กการสร้าง | วัตถุประสงค์ |
|-----------|---------|
| `-DGGML_HIP=ON` | เปิดใช้งานซอฟต์แวร์สแตก ROCm |
| `-DGGML_RPC=ON` | เปิดใช้งาน RPC สำหรับการอนุมานแบบกระจาย |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | เปิดใช้งาน rocWMMA สำหรับ Flash Attention ที่ปรับปรุงแล้วบน GPU ของ AMD |
| `-DAMDGPU_TARGETS="gfx1151"` | กำหนดเป้าหมายเป็น GPU Ryzen AI Halo (Radeon 8060s) |

สำหรับตัวเลือกการสร้างเพิ่มเติม โปรดดูที่ [เอกสารการสร้าง llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md)

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

คู่มือนี้ใช้ [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7) ซึ่งเป็นโมเดลที่มีพารามิเตอร์ 358B ในการควอนไทซ์แบบ `Q4_K_XL` จาก [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL) ที่ระดับการควอนไทซ์นี้ โมเดลต้องการพื้นที่จัดเก็บประมาณ 205GB และพอดีกับหน่วยความจำ GPU รวมของโหนด Ryzen AI Halo สองโหนด

ดาวน์โหลดไฟล์ GGUF โดยใช้ Hugging Face CLI:
<!-- @os:linux -->
```bash
pip install huggingface-hub
hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

> **หมายเหตุ**: การดาวน์โหลดโมเดลต้องดำเนินการให้เสร็จสิ้นบนเครื่องที่ 1 (ตัวควบคุม) โหนดเวิร์กเกอร์ RPC ไม่จำเป็นต้องมีสำเนาไฟล์โมเดลในเครื่อง

## การเปิดใช้งานโมเดลบนคลัสเตอร์

เอนจิน RPC (Remote Procedure Call) ของ llama.cpp ช่วยให้อินสแตนซ์ llama.cpp เดียวสามารถกระจายเลเยอร์โมเดลไปยังเวิร์กเกอร์ระยะไกลผ่านเครือข่ายได้ เครื่องหนึ่งทำหน้าที่เป็น **ตัวควบคุม** (เครื่องที่ 1) จัดการการแปลงโทเค็น การจัดตาราง และการประสานงาน ส่วนอีกเครื่องรัน **เซิร์ฟเวอร์ RPC** แบบเบา (เครื่องที่ 2) ที่เปิดเผยหน่วยความจำ GPU และการประมวลผลให้กับตัวควบคุม

ในขณะโหลด llama.cpp จะแบ่งโมเดลออกระหว่างทั้งสองโหนด เมื่อโหลดเสร็จแล้ว การอนุมานจะดำเนินการเหมือนกับการรันบนตัวเร่งความเร็วเดียว RPC จัดการการถ่ายโอนเทนเซอร์และการซิงโครไนซ์เบื้องหลัง

### ขั้นตอนที่ 1: เริ่มต้นเซิร์ฟเวอร์ RPC (เครื่องที่ 2)

บนเครื่องที่ 2 ให้เริ่มต้นเซิร์ฟเวอร์ RPC เพื่อเปิดเผยทรัพยากร GPU ให้กับตัวควบคุม:
<!-- @os:linux -->
```bash
./rpc-server -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
.\rpc-server.exe -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

| แฟล็ก | วัตถุประสงค์ |
|------|---------|
| `-p` | พอร์ตสำหรับเผยแพร่เซิร์ฟเวอร์ RPC |
| `-c` | เปิดใช้งานแคชในเครื่องสำหรับเทนเซอร์ขนาดใหญ่ เพื่อหลีกเลี่ยงการถ่ายโอนผ่านเครือข่ายซ้ำๆ ระหว่างการโหลดโมเดล |
| `--host` | ที่อยู่ IP สำหรับผูกเซิร์ฟเวอร์ RPC (`0.0.0.0` สำหรับทุกอินเทอร์เฟซ) |

สำหรับตัวเลือกเพิ่มเติม โปรดดูที่ [เอกสาร RPC ของ llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md)

### ขั้นตอนที่ 2: เปิดใช้งานโมเดล (เครื่องที่ 1)

เมื่อเซิร์ฟเวอร์ RPC ทำงานบนเครื่องที่ 2 แล้ว ให้เปิดใช้งานการอนุมานจากเครื่องที่ 1 โดยใช้ `llama-cli` หรือ `llama-server`

#### llama-cli

`llama-cli` มอบอินเทอร์เฟซแบบเทอร์มินัลสำหรับโต้ตอบกับโมเดลโดยตรง เหมาะสำหรับการทดสอบประสิทธิภาพ การดีบัก และการทดลองในระดับต่ำ

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --rpc <RPC_WORKER_IP>:50053
```

> **การค้นหา `<RPC_WORKER_IP>`**: บนเครื่องที่ 2 ให้รัน `hostname -I | awk '{print $1}'` เพื่อค้นหาที่อยู่ IP ในเครือข่ายท้องถิ่น
<!-- @os:end -->

<!-- @os:windows -->
> **หมายเหตุ**: รันคำสั่งนี้ใน Terminal (Powershell)

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **การค้นหา `<RPC_WORKER_IP>`**: บนเครื่องที่ 2 ให้รัน `ipconfig | findstr /C:"IPv4"` ใน Terminal (Powershell) เพื่อค้นหาที่อยู่ IP ในเครือข่ายท้องถิ่น

<!-- @os:end -->

เมื่อทำงานแล้ว `llama-cli` จะแสดงความคืบหน้าการโหลดโมเดลและเข้าสู่พรอมต์แบบโต้ตอบที่คุณสามารถสนทนากับโมเดลได้โดยตรง:

![llama-cli รัน GLM 4.7 บนสองโหนด](assets/llama-cli-example.png)
#### llama-server

`llama-server` เปิดเผย inference engine เดียวกันผ่านกระบวนการเซิร์ฟเวอร์ที่ทำงานต่อเนื่อง พร้อมด้วย web UI ในตัวและ HTTP API ที่เข้ากันได้กับ OpenAI นี่คืออินเทอร์เฟซที่แนะนำสำหรับการใช้งานระยะยาว การเข้าถึงแบบหลายผู้ใช้ และการผสานรวมกับเครื่องมือภายนอก

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_IP>:50053
```

> **การค้นหา `<RPC_WORKER_IP>`**: บน Machine 2 ให้รัน `hostname -I | awk '{print $1}'` เพื่อค้นหา IP address ในเครือข่ายท้องถิ่น
<!-- @os:end -->

<!-- @os:windows -->
> **หมายเหตุ**: รันคำสั่งนี้ใน Terminal (Powershell)

```powershell
.\llama-server.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_IP>:50053
```

> **การค้นหา `<RPC_WORKER_IP>`**: บน Machine 2 ให้รัน `ipconfig | findstr /C:"IPv4"` ใน Terminal (Powershell) เพื่อค้นหา IP address ในเครือข่ายท้องถิ่น
<!-- @os:end -->

เมื่อเริ่มต้นแล้ว ให้เปิด `http://<HOST_IP>:8081` ในเบราว์เซอร์ของคุณเพื่อเข้าถึง web UI ในตัว ซึ่งมีอินเทอร์เฟซแชทบนเบราว์เซอร์สำหรับโต้ตอบกับโมเดล:

![llama-server web UI running GLM 4.7 across two nodes](assets/llama-server-example.png)

<!-- @os:linux -->
> **การค้นหา `<HOST_IP>`**: บน Machine 1 ให้รัน `hostname -I | awk '{print $1}'` เพื่อค้นหา IP address ในเครือข่ายท้องถิ่น
<!-- @os:end -->

<!-- @os:windows -->
> **การค้นหา `<HOST_IP>`**: บน Machine 1 ให้รัน `ipconfig | findstr /C:"IPv4"` ใน Terminal (Powershell) เพื่อค้นหา IP address ในเครือข่ายท้องถิ่น
<!-- @os:end -->

#### ข้อมูลอ้างอิงพารามิเตอร์

| Flag | วัตถุประสงค์ |
|------|---------|
| `-m` | พาธไปยังไฟล์โมเดล GGUF (ใช้ shard แรก `00001-of-00005`) |
| `-c` | ขนาด context เป็น token ค่าที่มากขึ้นจะใช้หน่วยความจำมากขึ้น |
| `-fa on` | เปิดใช้งาน rocWMMA Flash Attention เพื่อประสิทธิภาพที่ดีขึ้นบน AMD GPU |
| `-ngl 999` | โอนถ่าย layer ทั้งหมดของโมเดลไปยัง GPU |
| `--no-mmap` | ปิดใช้งาน memory-mapping ช่วยลดเวลาโหลดเมื่อขนาดโมเดลเกิน RAM ของระบบแต่พอดีกับ VRAM |
| `--host` | IP สำหรับผูก `llama-server` (เฉพาะ `llama-server`) |
| `--port` | พอร์ตสำหรับให้บริการ HTTP API (เฉพาะ `llama-server`) |
| `--rpc` | รายการ RPC worker endpoint (`IP:port`) คั่นด้วยเครื่องหมายจุลภาค |

สำหรับการใช้งานพารามิเตอร์แบบเต็ม โปรดดูที่ [เอกสาร llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) และ [เอกสาร llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)

## ขั้นตอนถัดไป

- **เชื่อมต่อแอปพลิเคชันของบุคคลที่สาม**: `llama-server` เปิดเผย API ที่เข้ากันได้กับ OpenAI ชี้แอปพลิเคชันที่เข้ากันได้กับ OpenAI ใดก็ได้ (เช่น Open WebUI) ไปที่ `http://<HOST_IP>:8081` พร้อม API key ตัวแทนใดก็ได้ (เช่น `none`) เพื่อเชื่อมต่อกับคลัสเตอร์ของคุณ
- **สำรวจโมเดลอื่น ๆ**: เรียกดู GGUF แบบ quantized บน [Hugging Face](https://huggingface.co/models?search=gguf) เพื่อค้นหาโมเดลที่พอดีกับหน่วยความจำ GPU รวมของคลัสเตอร์ของคุณ
- **ขยายเป็นสี่โหนด**: เพิ่มระบบ Ryzen AI Halo อีกสองระบบเป็น RPC worker เพิ่มเติมเพื่อเข้าถึงโมเดลในระดับ 1 ล้านล้านพารามิเตอร์ ส่ง endpoint เพิ่มเติมไปยัง `--rpc` เป็นรายการคั่นด้วยเครื่องหมายจุลภาค (เช่น `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)