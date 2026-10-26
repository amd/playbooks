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

# การสร้างคลัสเตอร์ Ryzen™ AI Halo สองเครื่องด้วย RPC

## ภาพรวม

Ryzen™ AI Halo ของคุณมีความสามารถในการรันโมเดลภาษาขนาดใหญ่ได้ในเครื่องอยู่แล้ว การสร้างคลัสเตอร์จะพาสิ่งนี้ไปอีกขั้น โดยการรวมหน่วยความจำ GPU ของหลายระบบเข้าด้วยกันผ่านเครือข่ายท้องถิ่น ทำให้คุณสามารถเข้าถึงโมเดลขนาดใหญ่ขึ้นที่มีความสามารถในการให้เหตุผลที่แข็งแกร่งขึ้น สร้างโค้ดได้ดีขึ้น และเข้าใจภาษาต่าง ๆ ได้ลึกซึ้งยิ่งขึ้น ทั้งหมดนี้ทำได้บนฮาร์ดแวร์ของคุณเองอย่างสมบูรณ์

เอกสารนี้จะสอนวิธีการสร้างคลัสเตอร์ของระบบ Ryzen AI Halo สองเครื่องโดยใช้ RPC engine ของ llama.cpp และรัน GLM 4.7 ซึ่งเป็นโมเดลขนาด 358B พารามิเตอร์ ข้ามทั้งสองเครื่องด้วยการเร่งความเร็วของ AMD ROCm™

## สิ่งที่คุณจะได้เรียนรู้

- วิธีขยายการจัดสรร VRAM บนระบบ Ryzen AI Halo
- การติดตั้ง llama.cpp พร้อมการรองรับ ROCm และ RPC
- การกำหนดค่า RPC worker และเริ่มการอนุมานแบบกระจายข้ามสองโหนด
- การรันโมเดลขนาด 358B พารามิเตอร์ข้ามระบบ Ryzen AI Halo สองเครื่องที่เชื่อมต่อผ่านเครือข่าย

## การตั้งค่าหน่วยความจำ

> **หมายเหตุ**: ทำขั้นตอนนี้ให้ครบทั้งบน Machine 1 และ Machine 2

<!-- @device:halo_box -->
<!-- @os:windows -->
> **การรันโมเดลที่มีขนาดใกล้เคียงหรือมากกว่า 128 GB:** บนระบบ AMD Ryzen™ AI Max 400 Series (Gorgon Halo) ที่รัน Windows โมเดลที่มีขนาดใกล้เคียงหรือเกิน 128 GB ของหน่วยความจำต้องการการกำหนดค่าเพิ่มเติมเพื่อให้รันได้โดยไม่มีข้อผิดพลาด โปรดทำตาม [แนวทางปฏิบัติสำหรับระบบปฏิบัติการ Windows ของ AMD Ryzen AI Max PRO 400 Series](https://docs.amd.com/v/u/en-US/73342_1.00_AMD_Ryzen_AI_Max_PRO_400_Series_Windows_OS_Guidelines) ก่อนโหลดโมเดล
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:windows -->
บน Windows เพื่อรันโมเดลขนาดใหญ่ที่ต้องการหน่วยความจำสูงขึ้น เราจำเป็นต้องใช้การจัดสรร AMD Variable Graphics Memory (iGPU VRAM)

สามารถทำได้โดยเปิดแผงควบคุม AMD Software: Adrenalin Edition และไปที่: `Performance > Tuning > AMD Variable Graphics Memory` ตั้งค่าเป็น **96 GB** โปรดรีบูตระบบเพื่อให้การเปลี่ยนแปลงมีผล

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
บน Linux ROCm ใช้พูลหน่วยความจำระบบร่วมกัน (shared system memory pool) และพูลนี้ถูกกำหนดค่าเริ่มต้นไว้ที่ครึ่งหนึ่งของหน่วยความจำระบบ

ปริมาณนี้สามารถเพิ่มได้โดยการเปลี่ยนการตั้งค่าหน้า Translation Table Manager (TTM) ของเคอร์เนล ตามคำแนะนำต่อไปนี้ AMD แนะนำให้ตั้งค่า VRAM เฉพาะขั้นต่ำใน BIOS (0.5 GB)

* ติดตั้งยูทิลิตี้ pipx และเพิ่มเส้นทางสำหรับ wheels ที่ติดตั้งโดย pipx เข้าไปในเส้นทางการค้นหาของระบบ

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

เอกสารนี้ต้องการ Ryzen AI Halo สองเครื่องและสวิตช์อีเทอร์เน็ตหนึ่งตัว เชื่อมต่อในแบบโทโพโลยีดาว (star topology) โดยแต่ละเครื่องเชื่อมต่อโดยตรงกับสวิตช์

| ส่วนประกอบ | จำนวน | คำอธิบาย |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | โหนดประมวลผลที่ประกอบกันเป็นคลัสเตอร์ |
| สวิตช์อีเทอร์เน็ต 10Gbps | 1 | สวิตช์ส่วนกลางเพื่อให้การสื่อสารแบบหลายโหนดของ Ryzen AI Halo เป็นไปได้ (อย่างน้อย 2 พอร์ต) |
| สายเคเบิลอีเทอร์เน็ต | 2 | เชื่อมต่อแต่ละเครื่อง Halo เข้ากับสวิตช์ (แนะนำ Cat 7 ขึ้นไป) |

> **หมายเหตุ**: ต้องใช้พอร์ตสวิตช์อีเทอร์เน็ตสองพอร์ตเพื่อเชื่อมต่อเครื่อง Ryzen AI Halo สองเครื่อง จำเป็นต้องมีพอร์ตที่สามหากคุณเข้าถึงโมเดลจากเครื่องไคลเอนต์แยกต่างหากแทนที่จะเข้าถึงจากหนึ่งในเครื่อง Halo

### ซอฟต์แวร์
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
โปรดติดตั้ง:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) พร้อมกับชุดการทำงาน **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## การติดตั้งฮาร์ดแวร์ทางกายภาพ

> **หมายเหตุ**: ทำขั้นตอนนี้ให้ครบทั้งบน Machine 1 และ Machine 2

เชื่อมต่อเครื่อง Ryzen AI Halo แต่ละเครื่องเข้ากับสวิตช์อีเทอร์เน็ตโดยใช้สายเคเบิล Cat 7 (หรือสูงกว่า) ซึ่งจะสร้างลิงก์ 10Gbps ที่ใช้สำหรับการสื่อสารความเร็วสูงระหว่างโหนด
<!-- @os:linux -->
### 1. กำหนดอินเทอร์เฟซเครือข่าย

บนแต่ละเครื่อง ให้หาชื่ออินเทอร์เฟซเครือข่ายของเครื่องนั้นและจดไว้ (จะถูกอ้างอิงด้านล่างว่า `IFNAME`) รัน:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

คำสั่งนี้จะแสดงชื่ออินเทอร์เฟซโดยตรง ตัวอย่างเช่น:

```bash
enp191s0
```

### 2. ตรวจสอบความเร็วลิงก์เครือข่าย

ยืนยันว่าลิงก์ทำงานอยู่และรันที่ความเร็วเต็มโดยตรวจสอบความเร็วของอินเทอร์เฟซของคุณ:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **หมายเหตุ**: แทนที่ `<IFNAME>` ด้วยชื่ออินเทอร์เฟซผลลัพธ์จาก [1. กำหนดอินเทอร์เฟซเครือข่าย](#1-determine-network-interfaces)

คุณควรเห็นความเร็ว `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **หมายเหตุ**: หากความเร็วต่ำกว่า `10000Mb/s` หรือลิงก์ไม่ขึ้น ให้ตรวจสอบการเชื่อมต่อสายเคเบิลและยืนยันว่าพอร์ตสวิตช์ถูกตั้งค่าเป็น 10Gbps สวิตช์บางตัวต้องการให้ปิดการทำงานของ auto-negotiation และตั้งค่าความเร็วลิงก์ด้วยตนเอง โปรดดูเอกสารของสวิตช์ของคุณ

<!-- @os:end -->

<!-- @os:windows -->
### ตรวจสอบความเร็วลิงก์เครือข่าย

บนแต่ละเครื่อง ให้ตรวจสอบความเร็วลิงก์ของอินเทอร์เฟซเครือข่ายของคุณ:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

อินเทอร์เฟซอีเทอร์เน็ตของคุณควรเป็น `Up` และทำงานที่ `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **หมายเหตุ**: หากความเร็วต่ำกว่า `10 Gbps` หรือลิงก์ไม่ขึ้น ให้ตรวจสอบการเชื่อมต่อสายเคเบิลและยืนยันว่าพอร์ตสวิตช์ถูกตั้งค่าเป็น 10Gbps สวิตช์บางตัวต้องการให้ปิดการทำงานของ auto-negotiation และตั้งค่าความเร็วลิงก์ด้วยตนเอง โปรดดูเอกสารของสวิตช์ของคุณ

<!-- @os:end -->

## การติดตั้ง llama.cpp

> **หมายเหตุ**: ทำขั้นตอนนี้ให้ครบทั้งบน Machine 1 และ Machine 2

มีตัวเลือกการติดตั้งสองแบบ:

- [ตัวเลือกที่ 1: Lemonade SDK (แนะนำ)](#option-1-lemonade-sdk-recommended) - ไบนารีที่สร้างไว้ล่วงหน้า ตั้งค่าได้เร็วที่สุด
- [ตัวเลือกที่ 2: การสร้างจากซอร์สโค้ดด้วยตนเอง](#option-2-manual-source-build) - สร้างจากซอร์สโค้ดโดยควบคุมแฟล็กการสร้างได้อย่างเต็มที่
### ตัวเลือกที่ 1: Lemonade SDK (แนะนำ)

Lemonade SDK มีบิลด์รายคืนของ llama.cpp ที่เร่งความเร็วด้วย AMD ROCm 7 โดยกำหนดเป้าหมายไปยัง GPU อย่างเช่น gfx1151 (Strix Halo / Ryzen AI Max+ 395) และสถาปัตยกรรม Radeon รุ่นล่าสุดอื่น ๆ

<!-- @os:windows -->
#### ขั้นตอนที่ 1: ดาวน์โหลดไบนารีที่สร้างไว้ล่วงหน้า

ไปที่หน้าการเผยแพร่เวอร์ชันล่าสุดและดาวน์โหลดไฟล์เก็บถาวรที่ตรงกับแพลตฟอร์มและ GPU เป้าหมายของคุณ:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

ดาวน์โหลดไฟล์ชื่อ `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (โดยที่ `xxxx` คือหมายเลขบิลด์)

#### ขั้นตอนที่ 2: แตกไฟล์ไบนารี

แตกไฟล์เก็บถาวรที่ดาวน์โหลดมา:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

ไดเรกทอรีนี้จะมีบิลด์ของ `llama-cli.exe`, `llama-server.exe` และ `rpc-server.exe` ที่รองรับ ROCm ซึ่งคอมไพล์ไว้ล่วงหน้าสำหรับระบบ Ryzen AI Halo ของคุณ

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

ไปที่หน้าการเผยแพร่เวอร์ชันล่าสุดและดาวน์โหลดไฟล์เก็บถาวรที่ตรงกับแพลตฟอร์มและ GPU เป้าหมายของคุณ:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

ดาวน์โหลดไฟล์ชื่อ `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (โดยที่ `xxxx` คือหมายเลขบิลด์)

#### ขั้นตอนที่ 2: แตกไฟล์และเตรียมไบนารี

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

ไดเรกทอรีนี้จะมีบิลด์ของ `llama-cli`, `llama-server` และ `rpc-server` ที่รองรับ ROCm ซึ่งคอมไพล์ไว้ล่วงหน้าสำหรับระบบ Ryzen AI Halo ของคุณ

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

### ตัวเลือกที่ 2: การสร้างซอร์สโค้ดด้วยตนเอง

<!-- @os:windows -->
#### ขั้นตอนที่ 1: สร้าง llama.cpp

เปิด **x64 Native Tools Command Prompt** (ติดตั้งมาพร้อมกับ Visual Studio Build Tools) แล้วโคลนที่เก็บข้อมูล:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

เพิ่ม HIP ลงใน path ของคุณและสร้างโดยรองรับ ROCm และ RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Build Flag | วัตถุประสงค์ |
|-----------|---------|
| `-DGGML_HIP=ON` | เปิดใช้งานซอฟต์แวร์สแต็ก ROCm/HIP |
| `-DGGML_RPC=ON` | เปิดใช้งาน RPC สำหรับการอนุมานแบบกระจาย |
| `-DGPU_TARGETS=gfx1151` | กำหนดเป้าหมายไปยัง GPU ของ Ryzen AI Halo (Radeon 8060s) |
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

ขั้นตอนการสร้างบิลด์ด้านบนได้ตั้งค่า `%HIP_PATH%\bin` สำหรับเซสชันปัจจุบันเท่านั้น หากต้องการให้ไลบรารี HIP ใช้งานได้ในเทอร์มินัลใด ๆ (ไม่ใช่แค่ x64 Native Tools Command Prompt) ให้เพิ่มลงใน `PATH` ของผู้ใช้ของคุณอย่างถาวร:

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

สร้างโดยรองรับ ROCm และ RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Build Flag | วัตถุประสงค์ |
|-----------|---------|
| `-DGGML_HIP=ON` | เปิดใช้งานซอฟต์แวร์สแต็ก ROCm |
| `-DGGML_RPC=ON` | เปิดใช้งาน RPC สำหรับการอนุมานแบบกระจาย |
| `-DAMDGPU_TARGETS="gfx1151"` | กำหนดเป้าหมายไปยัง GPU ของ Ryzen AI Halo (Radeon 8060s) |

สำหรับตัวเลือกการสร้างบิลด์เพิ่มเติม โปรดดูที่ [เอกสารการสร้างบิลด์ llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md)

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

เพลย์บุ๊กนี้ใช้ [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7) ซึ่งเป็นโมเดลพารามิเตอร์ 358B ในรูปแบบควอนไทซ์ `Q4_K_XL` จาก [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL) ที่ระดับควอนไทซ์นี้ โมเดลต้องการพื้นที่จัดเก็บข้อมูลประมาณ 205GB และสามารถใส่ลงในหน่วยความจำ GPU รวมของโหนด Ryzen AI Halo สองโหนดได้

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

> **หมายเหตุ**: การดาวน์โหลดโมเดลต้องเสร็จสมบูรณ์บน Machine 1 (ตัวควบคุม) โดยที่โหนดเวิร์กเกอร์ RPC ไม่จำเป็นต้องมีสำเนาไฟล์โมเดลในเครื่อง

## การเปิดใช้งานโมเดลบนคลัสเตอร์

เอนจิน llama.cpp RPC (Remote Procedure Call) ช่วยให้อินสแตนซ์ llama.cpp เดียวสามารถถ่ายโอนเลเยอร์ของโมเดลไปยังเวิร์กเกอร์ระยะไกลผ่านเครือข่ายได้ เครื่องหนึ่งทำหน้าที่เป็น **ตัวควบคุม** (Machine 1) จัดการการแปลงโทเคน การจัดลำดับงาน และการประสานงาน ส่วนอีกเครื่องหนึ่งรัน **RPC server** แบบเบา (Machine 2) ซึ่งเปิดเผยหน่วยความจำ GPU และการประมวลผลให้กับตัวควบคุม

ในขณะโหลด llama.cpp จะแบ่งโมเดลออกเป็นส่วนย่อยไปยังทั้งสองโหนด เมื่อโหลดเสร็จแล้ว การอนุมานจะดำเนินไปราวกับว่ากำลังทำงานบนตัวเร่งความเร็วเพียงตัวเดียว โดย RPC จะจัดการการถ่ายโอนเทนเซอร์และการซิงโครไนซ์ที่อยู่เบื้องหลัง

### ขั้นตอนที่ 1: เริ่ม RPC Server (Machine 2)

บน Machine 2 ให้เริ่ม RPC server เพื่อเปิดเผยทรัพยากร GPU ของเครื่องให้กับตัวควบคุม:
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

| Flag | วัตถุประสงค์ |
|------|---------|
| `-p` | พอร์ตสำหรับการกระจายสัญญาณของ RPC server |
| `-c` | เปิดใช้งานแคชในเครื่องสำหรับเทนเซอร์ขนาดใหญ่ เพื่อหลีกเลี่ยงการถ่ายโอนข้อมูลผ่านเครือข่ายซ้ำ ๆ ระหว่างการโหลดโมเดล |
| `--host` | ที่อยู่ IP สำหรับผูก RPC server (`0.0.0.0` สำหรับทุกอินเทอร์เฟซ) |

สำหรับตัวเลือกเพิ่มเติม โปรดดูที่ [เอกสาร llama.cpp RPC](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md)

### ขั้นตอนที่ 2: เปิดใช้งานโมเดล (Machine 1)

เมื่อ RPC server ทำงานอยู่บน Machine 2 แล้ว ให้เปิดใช้งานการอนุมานจาก Machine 1 โดยใช้ `llama-cli` หรือ `llama-server`
#### llama-cli

`llama-cli` มีอินเทอร์เฟซแบบเทอร์มินัลสำหรับการโต้ตอบกับโมเดลโดยตรง เหมาะสำหรับการเปรียบเทียบประสิทธิภาพ การดีบัก และการทดลองระดับล่าง

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

> **การค้นหา `<RPC_WORKER_IP>`**: บนเครื่องที่ 2 ให้รันคำสั่ง `hostname -I | awk '{print $1}'` เพื่อค้นหาที่อยู่ IP ภายในของเครื่อง
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

> **การค้นหา `<RPC_WORKER_IP>`**: บนเครื่องที่ 2 ให้รันคำสั่ง `ipconfig | findstr /C:"IPv4"` ใน Terminal (Powershell) เพื่อค้นหาที่อยู่ IP ภายในของเครื่อง

<!-- @os:end -->

เมื่อรันแล้ว `llama-cli` จะแสดงความคืบหน้าในการโหลดโมเดล และเข้าสู่พรอมต์แบบโต้ตอบที่คุณสามารถสนทนากับโมเดลได้โดยตรง:

![llama-cli ทำงานกับ GLM 4.7 บนสองโหนด](assets/llama-cli-example.png)

#### llama-server

`llama-server` เปิดให้ใช้งานเอนจินการอนุมานเดียวกันผ่านกระบวนการเซิร์ฟเวอร์แบบถาวร พร้อมเว็บ UI ในตัวและ HTTP API ที่เข้ากันได้กับ OpenAI นี่เป็นอินเทอร์เฟซที่เหมาะสมที่สุดสำหรับการใช้งานระยะยาว การเข้าถึงโดยผู้ใช้หลายคน และการผสานรวมกับเครื่องมือภายนอก

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

> **การค้นหา `<RPC_WORKER_IP>`**: บนเครื่องที่ 2 ให้รันคำสั่ง `hostname -I | awk '{print $1}'` เพื่อค้นหาที่อยู่ IP ภายในของเครื่อง
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

> **การค้นหา `<RPC_WORKER_IP>`**: บนเครื่องที่ 2 ให้รันคำสั่ง `ipconfig | findstr /C:"IPv4"` ใน Terminal (Powershell) เพื่อค้นหาที่อยู่ IP ภายในของเครื่อง
<!-- @os:end -->

เมื่อเริ่มต้นแล้ว ให้เปิด `http://<HOST_IP>:8081` ในเบราว์เซอร์ของคุณเพื่อเข้าถึงเว็บ UI ในตัว ซึ่งให้อินเทอร์เฟซแชทผ่านเบราว์เซอร์สำหรับการโต้ตอบกับโมเดล:

![เว็บ UI ของ llama-server ทำงานกับ GLM 4.7 บนสองโหนด](assets/llama-server-example.png)

<!-- @os:linux -->
> **การค้นหา `<HOST_IP>`**: บนเครื่องที่ 1 ให้รันคำสั่ง `hostname -I | awk '{print $1}'` เพื่อค้นหาที่อยู่ IP ภายในของเครื่อง
<!-- @os:end -->

<!-- @os:windows -->
> **การค้นหา `<HOST_IP>`**: บนเครื่องที่ 1 ให้รันคำสั่ง `ipconfig | findstr /C:"IPv4"` ใน Terminal (Powershell) เพื่อค้นหาที่อยู่ IP ภายในของเครื่อง
<!-- @os:end -->

#### ข้อมูลอ้างอิงพารามิเตอร์

| แฟล็ก | วัตถุประสงค์ |
|------|---------|
| `-m` | พาธไปยังไฟล์โมเดล GGUF (ใช้ชาร์ดแรก `00001-of-00005`) |
| `-c` | ขนาดบริบทเป็นโทเคน ค่าที่มากขึ้นจะใช้หน่วยความจำมากขึ้น |
| `-fa on` | เปิดใช้งาน rocWMMA Flash Attention เพื่อประสิทธิภาพที่ดีขึ้นบน AMD GPU |
| `-ngl 999` | ถ่ายโอนเลเยอร์ทั้งหมดของโมเดลไปยัง GPU |
| `-lm none` | ตั้งค่าโหมดการโหลดโมเดลเป็น `none` ปิดใช้งานการแมปหน่วยความจำ (memory-mapping) เพื่อลดเวลาการโหลดเมื่อขนาดโมเดลเกิน RAM ของระบบแต่พอดีกับ VRAM |
| `--host` | IP สำหรับผูก `llama-server` (เฉพาะ `llama-server` เท่านั้น) |
| `--port` | พอร์ตสำหรับให้บริการ HTTP API (เฉพาะ `llama-server` เท่านั้น) |
| `--rpc` | รายการจุดสิ้นสุด RPC worker ที่คั่นด้วยเครื่องหมายจุลภาค (`IP:port`) |

สำหรับการใช้งานพารามิเตอร์แบบเต็ม โปรดดูที่ [เอกสาร llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) และ [เอกสาร llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)

## ขั้นตอนถัดไป

- **เชื่อมต่อแอปพลิเคชันจากบุคคลที่สาม**: `llama-server` เปิดให้ใช้งาน API ที่เข้ากันได้กับ OpenAI ชี้แอปพลิเคชันที่เข้ากันได้กับ OpenAI ใด ๆ (เช่น Open WebUI) ไปที่ `http://<HOST_IP>:8081` พร้อมคีย์ API ตัวแทน (เช่น `none`) เพื่อเชื่อมต่อกับคลัสเตอร์ของคุณ
- **สำรวจโมเดลอื่น ๆ**: เรียกดู GGUF ที่ผ่านการควอนไทซ์บน [Hugging Face](https://huggingface.co/models?search=gguf) เพื่อค้นหาโมเดลที่พอดีกับหน่วยความจำ GPU รวมของคลัสเตอร์ของคุณ
- **ขยายไปยังสี่โหนด**: เพิ่มระบบ Ryzen AI Halo อีกสองเครื่องเป็น RPC worker เพิ่มเติม เพื่อเข้าถึงโมเดลขนาดหนึ่งล้านล้านพารามิเตอร์ ส่งจุดสิ้นสุดเพิ่มเติมไปยัง `--rpc` เป็นรายการที่คั่นด้วยเครื่องหมายจุลภาค (เช่น `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)