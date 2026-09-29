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

# การทำคลัสเตอร์ Ryzen™ AI Halo สองเครื่องด้วย RPC

## ภาพรวม

Ryzen™ AI Halo ของคุณสามารถรันโมเดลภาษาขนาดใหญ่ในเครื่องได้อยู่แล้ว การทำคลัสเตอร์จะขยายขีดความสามารถนี้ไปอีกขั้น ด้วยการรวมหน่วยความจำ GPU ของหลายระบบเข้าด้วยกันผ่านเครือข่ายภายใน ทำให้คุณสามารถเข้าถึงโมเดลที่ใหญ่ขึ้น มีความสามารถในการให้เหตุผลที่แข็งแกร่งขึ้น สร้างโค้ดได้ดีขึ้น และเข้าใจภาษาต่าง ๆ ได้ลึกซึ้งยิ่งขึ้น ทั้งหมดนี้ทำงานอยู่บนฮาร์ดแวร์ของคุณเองทั้งสิ้น

คู่มือนี้จะสอนวิธีการทำคลัสเตอร์ระบบ Ryzen AI Halo สองเครื่องโดยใช้ RPC engine ของ llama.cpp และรัน GLM 4.7 ซึ่งเป็นโมเดลขนาด 358B พารามิเตอร์ ข้ามทั้งสองเครื่องด้วยการเร่งความเร็วของ AMD ROCm™

## สิ่งที่คุณจะได้เรียนรู้

- วิธีขยายการจัดสรร VRAM บนระบบ Ryzen AI Halo
- การติดตั้ง llama.cpp พร้อมการรองรับ ROCm และ RPC
- การกำหนดค่า RPC worker และการเริ่มรันการอนุมานแบบกระจายข้ามสองโหนด
- การรันโมเดลขนาด 358B พารามิเตอร์ข้ามระบบ Ryzen AI Halo สองเครื่องที่เชื่อมต่อผ่านเครือข่าย

## การตั้งค่าหน่วยความจำ

> **หมายเหตุ**: ทำขั้นตอนนี้ทั้งบน Machine 1 และ Machine 2

<!-- @os:windows -->
บน Windows หากต้องการรันโมเดลขนาดใหญ่ที่ต้องใช้หน่วยความจำมากขึ้น เราจำเป็นต้องใช้การจัดสรร AMD Variable Graphics Memory (iGPU VRAM)

สามารถทำได้โดยเปิดแผงควบคุม AMD Software: Adrenalin Edition และไปที่: `Performance > Tuning > AMD Variable Graphics Memory` ตั้งค่าเป็น **96 GB** จากนั้นรีบูตระบบเพื่อให้การเปลี่ยนแปลงมีผล

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
บน Linux, ROCm ใช้พูลหน่วยความจำระบบร่วมกัน (shared system memory pool) และพูลนี้ถูกกำหนดค่าเริ่มต้นไว้ที่ครึ่งหนึ่งของหน่วยความจำระบบ

สามารถเพิ่มปริมาณนี้ได้โดยการเปลี่ยนการตั้งค่าหน้า Translation Table Manager (TTM) ของ kernel ตามคำแนะนำต่อไปนี้ AMD แนะนำให้ตั้งค่า VRAM ที่จัดสรรขั้นต่ำใน BIOS (0.5 GB)

* ติดตั้งยูทิลิตี pipx และเพิ่มพาธสำหรับ wheel ที่ติดตั้งด้วย pipx ลงในพาธค้นหาของระบบ

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* ติดตั้ง wheel ของ amd-debug-tools จาก PyPI
  ```bash
  pipx install amd-debug-tools
  ```

* รันเครื่องมือ amd-ttm เพื่อตรวจสอบการตั้งค่าปัจจุบันของหน่วยความจำที่ใช้ร่วมกัน
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

คู่มือนี้ต้องใช้หน่วย Ryzen AI Halo สองเครื่องและสวิตช์ Ethernet หนึ่งตัว เชื่อมต่อในรูปแบบโทโพโลยีดาว (star topology) โดยแต่ละหน่วยเชื่อมต่อโดยตรงกับสวิตช์

| องค์ประกอบ | จำนวน | คำอธิบาย |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | โหนดประมวลผลที่ประกอบขึ้นเป็นคลัสเตอร์ |
| สวิตช์ Ethernet 10Gbps | 1 | สวิตช์ส่วนกลางที่ช่วยให้ Ryzen AI Halo หลายโหนดสื่อสารกันได้ (อย่างน้อย 2 พอร์ต) |
| สาย Ethernet | 2 | เชื่อมต่อแต่ละหน่วย Halo เข้ากับสวิตช์ (แนะนำ Cat 7 หรือสูงกว่า) |

> **หมายเหตุ**: ต้องใช้พอร์ตสวิตช์ Ethernet สองพอร์ตเพื่อเชื่อมต่อหน่วย Ryzen AI Halo ทั้งสองเครื่อง และต้องใช้พอร์ตที่สามหากคุณเข้าถึงโมเดลจากเครื่องไคลเอนต์แยกต่างหาก แทนที่จะเข้าถึงจากหน่วย Halo เครื่องใดเครื่องหนึ่ง

### ซอฟต์แวร์
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
กรุณาติดตั้ง:
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

> **หมายเหตุ**: ทำขั้นตอนนี้ทั้งบน Machine 1 และ Machine 2

เชื่อมต่อหน่วย Ryzen AI Halo แต่ละเครื่องเข้ากับสวิตช์ Ethernet โดยใช้สาย Cat 7 (หรือสูงกว่า) การเชื่อมต่อนี้จะสร้างลิงก์ 10Gbps ที่ใช้สำหรับการสื่อสารความเร็วสูงระหว่างโหนดต่าง ๆ
<!-- @os:linux -->
### 1. กำหนดอินเทอร์เฟซเครือข่าย

บนแต่ละเครื่อง ให้ค้นหาชื่ออินเทอร์เฟซเครือข่ายและจดบันทึกไว้ (จะถูกเรียกว่า `IFNAME` ในส่วนถัดไป) รันคำสั่ง:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

คำสั่งนี้จะแสดงชื่ออินเทอร์เฟซโดยตรง ตัวอย่างเช่น:

```bash
enp191s0
```

### 2. ตรวจสอบความเร็วลิงก์เครือข่าย

ยืนยันว่าลิงก์กำลังทำงานอยู่และวิ่งด้วยความเร็วเต็มที่ โดยตรวจสอบความเร็วของอินเทอร์เฟซของคุณ:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **หมายเหตุ**: แทนที่ `<IFNAME>` ด้วยชื่ออินเทอร์เฟซผลลัพธ์จาก [1. กำหนดอินเทอร์เฟซเครือข่าย](#1-determine-network-interfaces)

คุณควรเห็นความเร็วที่ `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **หมายเหตุ**: หากความเร็วต่ำกว่า `10000Mb/s` หรือลิงก์ไม่ขึ้น ให้ตรวจสอบการเชื่อมต่อสายและยืนยันว่าพอร์ตสวิตช์ตั้งค่าไว้ที่ 10Gbps สวิตช์บางรุ่นต้องปิดการเจรจาความเร็วอัตโนมัติ (auto-negotiation) และตั้งค่าความเร็วลิงก์ด้วยตนเอง โปรดดูเอกสารประกอบของสวิตช์ของคุณ

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

> **หมายเหตุ**: หากความเร็วต่ำกว่า `10 Gbps` หรือลิงก์ไม่ขึ้น ให้ตรวจสอบการเชื่อมต่อสายและยืนยันว่าพอร์ตสวิตช์ตั้งค่าไว้ที่ 10Gbps สวิตช์บางรุ่นต้องปิดการเจรจาความเร็วอัตโนมัติ (auto-negotiation) และตั้งค่าความเร็วลิงก์ด้วยตนเอง โปรดดูเอกสารประกอบของสวิตช์ของคุณ

<!-- @os:end -->

## การติดตั้ง llama.cpp

> **หมายเหตุ**: ทำขั้นตอนนี้ทั้งบน Machine 1 และ Machine 2

มีตัวเลือกการติดตั้งสองแบบ:

- [ตัวเลือกที่ 1: Lemonade SDK (แนะนำ)](#option-1-lemonade-sdk-recommended) - ไบนารีที่สร้างไว้ล่วงหน้า ตั้งค่าได้เร็วที่สุด
- [ตัวเลือกที่ 2: การสร้างซอร์สโค้ดด้วยตนเอง](#option-2-manual-source-build) - สร้างจากซอร์สโค้ดพร้อมควบคุมแฟล็กการสร้างได้อย่างเต็มที่

### ตัวเลือกที่ 1: Lemonade SDK (แนะนำ)

Lemonade SDK มีบิลด์รายคืนของ llama.cpp พร้อมการเร่งความเร็วด้วย AMD ROCm 7 ที่กำหนดเป้าหมายไปยัง GPU เช่น gfx1151 (Strix Halo / Ryzen AI Max+ 395) และสถาปัตยกรรม Radeon รุ่นล่าสุดอื่น ๆ

<!-- @os:windows -->
#### ขั้นตอนที่ 1: ดาวน์โหลดไบนารีที่สร้างไว้ล่วงหน้า

ไปที่หน้ารุ่นล่าสุดและดาวน์โหลดไฟล์เก็บถาวรที่ตรงกับแพลตฟอร์มและเป้าหมาย GPU ของคุณ:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

ดาวน์โหลดไฟล์ชื่อ `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (โดยที่ `xxxx` คือหมายเลขบิลด์)

#### ขั้นตอนที่ 2: แตกไฟล์ไบนารี

แตกไฟล์เก็บถาวรที่ดาวน์โหลดมา:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

ไดเรกทอรีนี้จะมีบิลด์ที่รองรับ ROCm ของ `llama-cli.exe`, `llama-server.exe` และ `rpc-server.exe` ที่คอมไพล์ไว้ล่วงหน้าสำหรับระบบ Ryzen AI Halo ของคุณ

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

ไปที่หน้ารุ่นล่าสุดและดาวน์โหลดไฟล์เก็บถาวรที่ตรงกับแพลตฟอร์มและเป้าหมาย GPU ของคุณ:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

ดาวน์โหลดไฟล์ชื่อ `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (โดยที่ `xxxx` คือหมายเลขบิลด์)

#### ขั้นตอนที่ 2: แตกไฟล์และเตรียมไบนารี

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

ไดเรกทอรีนี้จะมีบิลด์ที่รองรับ ROCm ของ `llama-cli`, `llama-server` และ `rpc-server` ที่คอมไพล์ไว้ล่วงหน้าสำหรับระบบ Ryzen AI Halo ของคุณ

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
เมื่อเตรียม llama.cpp บนแต่ละโหนดเรียบร้อยแล้ว ให้ดำเนินการต่อที่ [Downloading the Model](#downloading-the-model)

### ตัวเลือกที่ 2: การสร้างจากซอร์สโค้ดด้วยตนเอง

<!-- @os:windows -->
#### ขั้นตอนที่ 1: สร้าง llama.cpp

เปิด **x64 Native Tools Command Prompt** (ที่ติดตั้งมาพร้อมกับ Visual Studio Build Tools) แล้วโคลนที่เก็บข้อมูล:

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
| `-DGGML_HIP=ON` | เปิดใช้งานสแต็กซอฟต์แวร์ ROCm/HIP |
| `-DGGML_RPC=ON` | เปิดใช้งาน RPC สำหรับการอนุมานแบบกระจาย |
| `-DGPU_TARGETS=gfx1151` | กำหนดเป้าหมายเป็น GPU ของ Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | ใช้ระบบสร้างบิลด์ Ninja |

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

ขั้นตอนการสร้างข้างต้นได้ตั้งค่า `%HIP_PATH%\bin` สำหรับเซสชันปัจจุบันเท่านั้น หากต้องการให้ไลบรารี HIP พร้อมใช้งานในเทอร์มินัลใด ๆ (ไม่ใช่แค่ x64 Native Tools Command Prompt) ให้เพิ่มลงใน `PATH` ของผู้ใช้แบบถาวร:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

เมื่อเตรียม llama.cpp บนแต่ละโหนดเรียบร้อยแล้ว ให้ดำเนินการต่อที่ [Downloading the Model](#downloading-the-model)
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

| แฟล็กการสร้าง | วัตถุประสงค์ |
|-----------|---------|
| `-DGGML_HIP=ON` | เปิดใช้งานสแต็กซอฟต์แวร์ ROCm |
| `-DGGML_RPC=ON` | เปิดใช้งาน RPC สำหรับการอนุมานแบบกระจาย |
| `-DAMDGPU_TARGETS="gfx1151"` | กำหนดเป้าหมายเป็น GPU ของ Ryzen AI Halo (Radeon 8060s) |

สำหรับตัวเลือกการสร้างเพิ่มเติม โปรดดู [llama.cpp build documentation](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md)

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

เมื่อเตรียม llama.cpp บนแต่ละโหนดเรียบร้อยแล้ว ให้ดำเนินการต่อที่ [Downloading the Model](#downloading-the-model)
<!-- @os:end -->

## การดาวน์โหลดโมเดล

คู่มือนี้ใช้ [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7) ซึ่งเป็นโมเดลที่มีพารามิเตอร์ 358B ในการควอนไทซ์แบบ `Q4_K_XL` จาก [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL) ที่การควอนไทซ์นี้ โมเดลต้องการพื้นที่จัดเก็บประมาณ 205GB และสามารถรองรับได้ภายในหน่วยความจำ GPU รวมของสองโหนด Ryzen AI Halo

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

> **หมายเหตุ**: การดาวน์โหลดโมเดลต้องดำเนินการให้เสร็จสิ้นบน Machine 1 (ตัวควบคุม) โหนดผู้ปฏิบัติงาน RPC ไม่จำเป็นต้องมีสำเนาไฟล์โมเดลในเครื่อง

## การเปิดใช้โมเดลบนคลัสเตอร์

เอนจิน llama.cpp RPC (Remote Procedure Call) อนุญาตให้อินสแตนซ์ llama.cpp เดียวสามารถถ่ายโอนเลเยอร์ของโมเดลไปยังผู้ปฏิบัติงานระยะไกลผ่านเครือข่ายได้ เครื่องหนึ่งทำหน้าที่เป็น **ตัวควบคุม** (Machine 1) จัดการโทเคไนซ์ การจัดตารางเวลา และการประสานงาน ส่วนอีกเครื่องหนึ่งรัน **RPC server** แบบเบา (Machine 2) ที่เปิดเผยหน่วยความจำ GPU และการประมวลผลของตนให้กับตัวควบคุม

ในเวลาที่โหลด llama.cpp จะแบ่งโมเดลออกเป็นส่วน ๆ (shard) ข้ามทั้งสองโหนด เมื่อโหลดเสร็จแล้ว การอนุมานจะดำเนินไปราวกับว่ากำลังทำงานบนตัวเร่งความเร็วเดียว RPC จะจัดการการถ่ายโอนเทนเซอร์และการประสานเวลาโดยอัตโนมัติเบื้องหลัง

### ขั้นตอนที่ 1: เริ่ม RPC Server (Machine 2)

บน Machine 2 ให้เริ่ม RPC server เพื่อเปิดเผยทรัพยากร GPU ให้กับตัวควบคุม:
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
| `-p` | พอร์ตสำหรับกระจายสัญญาณ RPC server |
| `-c` | เปิดใช้งานแคชในเครื่องสำหรับเทนเซอร์ขนาดใหญ่ เพื่อหลีกเลี่ยงการถ่ายโอนผ่านเครือข่ายซ้ำ ๆ ระหว่างการโหลดโมเดล |
| `--host` | ที่อยู่ IP ที่จะผูก RPC server ไว้ (`0.0.0.0` สำหรับทุกอินเทอร์เฟซ) |

สำหรับตัวเลือกเพิ่มเติม โปรดดู [llama.cpp RPC documentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md)

### ขั้นตอนที่ 2: เปิดใช้โมเดล (Machine 1)

เมื่อ RPC server ทำงานอยู่บน Machine 2 แล้ว ให้เปิดใช้การอนุมานจาก Machine 1 โดยใช้ `llama-cli` หรือ `llama-server`

#### llama-cli

`llama-cli` มอบอินเทอร์เฟซแบบเทอร์มินัลสำหรับโต้ตอบกับโมเดลโดยตรง เหมาะสำหรับการวัดประสิทธิภาพ การดีบัก และการทดลองระดับล่าง

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  --rpc <RPC_WORKER_IP>:50053
```

> **การค้นหา `<RPC_WORKER_IP>`**: บน Machine 2 ให้รัน `hostname -I | awk '{print $1}'` เพื่อค้นหาที่อยู่ IP ในเครื่องของตัวเอง
<!-- @os:end -->

<!-- @os:windows -->
> **หมายเหตุ**: รันคำสั่งนี้ใน Terminal (Powershell)

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --rpc <RPC_WORKER_IP>:50053
```

> **การค้นหา `<RPC_WORKER_IP>`**: บน Machine 2 ให้รัน `ipconfig | findstr /C:"IPv4"` ใน Terminal (Powershell) เพื่อค้นหาที่อยู่ IP ในเครื่องของตัวเอง

<!-- @os:end -->

เมื่อทำงานแล้ว `llama-cli` จะแสดงความคืบหน้าในการโหลดโมเดล และเข้าสู่พรอมป์แบบโต้ตอบซึ่งคุณสามารถสนทนากับโมเดลได้โดยตรง:

![llama-cli running GLM 4.7 across two nodes](assets/llama-cli-example.png)
#### llama-server

`llama-server` เปิดให้ใช้งานเอนจินการอนุมานเดียวกันผ่านกระบวนการเซิร์ฟเวอร์แบบถาวรที่มาพร้อมกับ web UI แบบในตัวและ HTTP API ที่เข้ากันได้กับ OpenAI นี่คืออินเทอร์เฟซที่แนะนำสำหรับการใช้งานระยะยาว การเข้าถึงแบบผู้ใช้หลายคน และการผสานรวมกับเครื่องมือภายนอก

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_IP>:50053
```

> **การค้นหา `<RPC_WORKER_IP>`**: บนเครื่องที่ 2 ให้รัน `hostname -I | awk '{print $1}'` เพื่อค้นหาที่อยู่ IP ในเครือข่ายท้องถิ่น
<!-- @os:end -->

<!-- @os:windows -->
> **หมายเหตุ**: รันคำสั่งนี้ใน Terminal (Powershell)

```powershell
.\llama-server.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_IP>:50053
```

> **การค้นหา `<RPC_WORKER_IP>`**: บนเครื่องที่ 2 ให้รัน `ipconfig | findstr /C:"IPv4"` ใน Terminal (Powershell) เพื่อค้นหาที่อยู่ IP ในเครือข่ายท้องถิ่น
<!-- @os:end -->

เมื่อเริ่มต้นแล้ว ให้เปิด `http://<HOST_IP>:8081` ในเบราว์เซอร์ของคุณเพื่อเข้าถึง web UI ในตัว ซึ่งจะให้อินเทอร์เฟซแชทผ่านเบราว์เซอร์สำหรับโต้ตอบกับโมเดล:

![llama-server web UI ที่กำลังรัน GLM 4.7 บนสองโหนด](assets/llama-server-example.png)

<!-- @os:linux -->
> **การค้นหา `<HOST_IP>`**: บนเครื่องที่ 1 ให้รัน `hostname -I | awk '{print $1}'` เพื่อค้นหาที่อยู่ IP ในเครือข่ายท้องถิ่น
<!-- @os:end -->

<!-- @os:windows -->
> **การค้นหา `<HOST_IP>`**: บนเครื่องที่ 1 ให้รัน `ipconfig | findstr /C:"IPv4"` ใน Terminal (Powershell) เพื่อค้นหาที่อยู่ IP ในเครือข่ายท้องถิ่น
<!-- @os:end -->

#### ข้อมูลอ้างอิงพารามิเตอร์

| แฟล็ก | วัตถุประสงค์ |
|------|---------|
| `-m` | เส้นทางไปยังไฟล์โมเดล GGUF (ใช้ shard แรก `00001-of-00005`) |
| `-c` | ขนาดบริบทเป็นโทเค็น ค่าที่มากขึ้นจะใช้หน่วยความจำมากขึ้น |
| `-fa on` | เปิดใช้งาน rocWMMA Flash Attention เพื่อประสิทธิภาพที่ดีขึ้นบน GPU ของ AMD |
| `-ngl 999` | ถ่ายโอนเลเยอร์ทั้งหมดของโมเดลไปยัง GPU |
| `-lm none` | ตั้งค่าโหมดการโหลดโมเดลเป็น `none` ปิดใช้งานการแมปหน่วยความจำ (memory-mapping) เพื่อลดเวลาการโหลดเมื่อขนาดโมเดลเกินกว่า RAM ของระบบแต่ยังพอดีกับ VRAM |
| `--host` | IP ที่จะผูก `llama-server` (เฉพาะ `llama-server` เท่านั้น) |
| `--port` | พอร์ตที่จะให้บริการ HTTP API (เฉพาะ `llama-server` เท่านั้น) |
| `--rpc` | รายการ endpoint ของ RPC worker คั่นด้วยจุลภาค (`IP:port`) |

สำหรับการใช้งานพารามิเตอร์แบบเต็ม โปรดดูที่ [เอกสาร llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) และ [เอกสาร llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)

## ขั้นตอนถัดไป

- **เชื่อมต่อแอปพลิเคชันของบุคคลที่สาม**: `llama-server` เปิดให้ใช้งาน API ที่เข้ากันได้กับ OpenAI ให้ชี้แอปพลิเคชันที่เข้ากันได้กับ OpenAI ใด ๆ (เช่น Open WebUI) ไปที่ `http://<HOST_IP>:8081` พร้อมกับคีย์ API ตัวยึดตำแหน่งใด ๆ (เช่น `none`) เพื่อเชื่อมต่อกับคลัสเตอร์ของคุณ
- **สำรวจโมเดลอื่น ๆ**: เรียกดู GGUF ที่ผ่านการควอนไทซ์บน [Hugging Face](https://huggingface.co/models?search=gguf) เพื่อค้นหาโมเดลที่พอดีกับหน่วยความจำ GPU รวมของคลัสเตอร์ของคุณ
- **ขยายไปยังสี่โหนด**: เพิ่มระบบ Ryzen AI Halo อีกสองระบบเป็น RPC worker เพิ่มเติมเพื่อเข้าถึงโมเดลในระดับหนึ่งล้านล้านพารามิเตอร์ ส่ง endpoint เพิ่มเติมไปยัง `--rpc` เป็นรายการคั่นด้วยจุลภาค (เช่น `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)