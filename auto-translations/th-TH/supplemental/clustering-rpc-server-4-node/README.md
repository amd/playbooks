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

Ryzen™ AI Halo ของคุณมีความสามารถในการรันโมเดลภาษาขนาดใหญ่ในเครื่องได้อยู่แล้ว การทำคลัสเตอร์จะก้าวไปอีกขั้นด้วยการรวมหน่วยความจำ GPU ของหลายระบบเข้าด้วยกันผ่านเครือข่ายภายใน ทำให้คุณสามารถเข้าถึงโมเดลที่มีขนาดใหญ่ขึ้นได้ ซึ่งมีความสามารถในการให้เหตุผลที่แข็งแกร่งกว่า การสร้างโค้ดที่ดีกว่า และความเข้าใจหลายภาษาที่ลึกซึ้งยิ่งขึ้น ทั้งหมดนี้ทำงานบนฮาร์ดแวร์ของคุณเองอย่างสมบูรณ์

เอกสารนี้จะสอนวิธีการรวมคลัสเตอร์ระบบ Ryzen AI Halo สี่เครื่องโดยใช้เอนจิน RPC ของ llama.cpp และรัน Kimi K2.6 ซึ่งเป็นโมเดลแบบ mixture-of-experts ขนาดใหญ่ บนเครื่องทั้งสี่พร้อมการเร่งความเร็วด้วย AMD ROCm™

## สิ่งที่คุณจะได้เรียนรู้

- วิธีขยายการจัดสรร VRAM บนระบบ Ryzen AI Halo
- การติดตั้ง llama.cpp พร้อมรองรับ ROCm และ RPC
- การกำหนดค่า RPC worker และเริ่มต้นการอนุมานแบบกระจายบนสี่โหนด
- การรันโมเดลที่มีพารามิเตอร์ 1 ล้านล้าน (1T) บนระบบ Ryzen AI Halo สี่เครื่องที่เชื่อมต่อผ่านเครือข่าย

## การตั้งค่าหน่วยความจำ

> **หมายเหตุ**: ทำขั้นตอนนี้บนเครื่องทั้งสี่เครื่อง (เครื่องที่ 1 ถึงเครื่องที่ 4)

<!-- @device:halo_box -->
<!-- @os:windows -->
> **การรันโมเดลที่มีขนาดใกล้เคียงหรือมากกว่า 128 GB:** บนระบบ AMD Ryzen™ AI Max 400 Series (Gorgon Halo) ที่รันบน Windows โมเดลที่มีขนาดใกล้เคียงหรือมากกว่า 128 GB ของหน่วยความจำต้องมีการกำหนดค่าเพิ่มเติมเพื่อให้สามารถทำงานได้โดยไม่มีข้อผิดพลาด โปรดทำตาม [AMD Ryzen AI Max PRO 400 Series Windows OS Guidelines](https://docs.amd.com/v/u/en-US/73342_1.00_AMD_Ryzen_AI_Max_PRO_400_Series_Windows_OS_Guidelines) ก่อนโหลดโมเดล
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:windows -->
บน Windows หากต้องการรันโมเดลขนาดใหญ่ที่ต้องการหน่วยความจำมากขึ้น เราจำเป็นต้องใช้การจัดสรร AMD Variable Graphics Memory (iGPU VRAM)

สามารถทำได้โดยเปิดแผงควบคุม AMD Software: Adrenalin Edition แล้วไปที่: `Performance > Tuning > AMD Variable Graphics Memory` ตั้งค่าเป็น **96 GB** จากนั้นรีบูตระบบเพื่อให้การเปลี่ยนแปลงมีผล

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
บน Linux ROCm ใช้พูลหน่วยความจำระบบร่วมกัน (shared system memory pool) ซึ่งตามค่าเริ่มต้นจะถูกตั้งค่าให้เป็นครึ่งหนึ่งของหน่วยความจำระบบ

สามารถเพิ่มจำนวนนี้ได้โดยการเปลี่ยนการตั้งค่าหน้า Translation Table Manager (TTM) ของเคอร์เนล ตามคำแนะนำต่อไปนี้ AMD แนะนำให้ตั้งค่าหน่วยความจำ VRAM เฉพาะขั้นต่ำใน BIOS (0.5 GB)

* ติดตั้งยูทิลิตี pipx และเพิ่มพาธสำหรับ wheel ที่ติดตั้งผ่าน pipx ลงใน search path ของระบบ

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* ติดตั้ง wheel ของ amd-debug-tools จาก PyPI

  ```bash
  pipx install amd-debug-tools
  ```

* รันเครื่องมือ amd-ttm เพื่อตรวจสอบการตั้งค่าหน่วยความจำร่วมปัจจุบัน

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
## ข้อกำหนดเบื้องต้น

### ฮาร์ดแวร์

เอกสารนี้ต้องการ Ryzen AI Halo สี่เครื่องและสวิตช์ Ethernet หนึ่งตัว เชื่อมต่อในลักษณะโทโพโลยีแบบดาว (star topology) โดยแต่ละเครื่องเชื่อมต่อโดยตรงกับสวิตช์

| ส่วนประกอบ | จำนวน | คำอธิบาย |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | โหนดประมวลผลที่ประกอบกันเป็นคลัสเตอร์ |
| สวิตช์ Ethernet 10Gbps | 1 | สวิตช์กลางที่ช่วยให้ Ryzen AI Halo หลายโหนดสื่อสารกันได้ (อย่างน้อย 4 พอร์ต) |
| สายเคเบิล Ethernet | 4 | เชื่อมต่อแต่ละเครื่อง Halo เข้ากับสวิตช์ (แนะนำให้ใช้ Cat 7 หรือสูงกว่า) |

> **หมายเหตุ**: ต้องใช้พอร์ตสวิตช์ Ethernet สี่พอร์ตเพื่อเชื่อมต่อเครื่อง Ryzen AI Halo สี่เครื่อง และต้องใช้พอร์ตที่ห้าหากคุณต้องการเข้าถึงโมเดลจากเครื่องไคลเอ็นต์แยกต่างหากแทนที่จะเป็นจากเครื่อง Halo เครื่องใดเครื่องหนึ่ง

### ซอฟต์แวร์
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
โปรดติดตั้ง:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) พร้อมเวิร์กโหลด **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## การตั้งค่าฮาร์ดแวร์ทางกายภาพ

> **หมายเหตุ**: ทำขั้นตอนนี้บนเครื่องทั้งสี่เครื่อง (เครื่องที่ 1 ถึงเครื่องที่ 4)

เชื่อมต่อเครื่อง Ryzen AI Halo แต่ละเครื่องเข้ากับสวิตช์ Ethernet โดยใช้สาย Cat 7 (หรือสูงกว่า) การเชื่อมต่อนี้จะสร้างลิงก์ 10Gbps ที่ใช้สำหรับการสื่อสารความเร็วสูงระหว่างโหนด
<!-- @os:linux -->
### 1. กำหนดอินเทอร์เฟซเครือข่าย

บนแต่ละเครื่อง ให้ค้นหาชื่ออินเทอร์เฟซเครือข่ายของเครื่องนั้นและจดบันทึกไว้ (จะถูกเรียกว่า `IFNAME` ในส่วนต่อไปนี้) รันคำสั่ง:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

คำสั่งนี้จะแสดงชื่ออินเทอร์เฟซโดยตรง ตัวอย่างเช่น:

```bash
enp191s0
```

### 2. ตรวจสอบความเร็วลิงก์เครือข่าย

ยืนยันว่าลิงก์กำลังทำงานอยู่และทำงานด้วยความเร็วเต็มที่โดยตรวจสอบความเร็วของอินเทอร์เฟซของคุณ:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **หมายเหตุ**: แทนที่ `<IFNAME>` ด้วยชื่ออินเทอร์เฟซที่แสดงผลลัพธ์จาก [1. กำหนดอินเทอร์เฟซเครือข่าย](#1-determine-network-interfaces)

คุณควรเห็นความเร็วที่ `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **หมายเหตุ**: หากความเร็วต่ำกว่า `10000Mb/s` หรือลิงก์ไม่ทำงาน ให้ตรวจสอบการเชื่อมต่อสายเคเบิลและยืนยันว่าพอร์ตสวิตช์ถูกตั้งค่าเป็น 10Gbps สวิตช์บางรุ่นต้องปิดการใช้งานการเจรจาอัตโนมัติ (auto-negotiation) และตั้งค่าความเร็วลิงก์ด้วยตนเอง โปรดดูเอกสารของสวิตช์ของคุณ

<!-- @os:end -->

<!-- @os:windows -->
### ตรวจสอบความเร็วลิงก์เครือข่าย

บนแต่ละเครื่อง ให้ตรวจสอบความเร็วลิงก์ของอินเทอร์เฟซเครือข่ายของคุณ:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

อินเทอร์เฟซ Ethernet ของคุณควรแสดงสถานะ `Up` และทำงานที่ `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **หมายเหตุ**: หากความเร็วต่ำกว่า `10 Gbps` หรือลิงก์ไม่ทำงาน ให้ตรวจสอบการเชื่อมต่อสายเคเบิลและยืนยันว่าพอร์ตสวิตช์ถูกตั้งค่าเป็น 10Gbps สวิตช์บางรุ่นต้องปิดการใช้งานการเจรจาอัตโนมัติ (auto-negotiation) และตั้งค่าความเร็วลิงก์ด้วยตนเอง โปรดดูเอกสารของสวิตช์ของคุณ

<!-- @os:end -->

## การติดตั้ง llama.cpp

> **หมายเหตุ**: ทำขั้นตอนนี้บนเครื่องทั้งสี่เครื่อง (เครื่องที่ 1 ถึงเครื่องที่ 4)

มีตัวเลือกการติดตั้งให้เลือกสองแบบ:

- [ตัวเลือกที่ 1: Lemonade SDK (แนะนำ)](#option-1-lemonade-sdk-recommended) - ไบนารีที่สร้างไว้ล่วงหน้า ตั้งค่าได้เร็วที่สุด
- [ตัวเลือกที่ 2: การสร้างจากซอร์สโค้ดด้วยตนเอง](#option-2-manual-source-build) - สร้างจากซอร์สโค้ดโดยสามารถควบคุมแฟล็กการสร้างได้อย่างเต็มที่
### ตัวเลือกที่ 1: Lemonade SDK (แนะนำ)

Lemonade SDK มีบิลด์รายคืนของ llama.cpp พร้อมการเร่งความเร็วด้วย AMD ROCm 7 โดยรองรับ GPU เช่น gfx1151 (Strix Halo / Ryzen AI Max+ 395) และสถาปัตยกรรม Radeon รุ่นล่าสุดอื่น ๆ

<!-- @os:windows -->
#### ขั้นตอนที่ 1: ดาวน์โหลดไบนารีที่สร้างไว้ล่วงหน้า

ไปที่หน้าเวอร์ชันล่าสุดและดาวน์โหลดไฟล์เก็บถาวรที่ตรงกับแพลตฟอร์มและ GPU เป้าหมายของคุณ:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

ดาวน์โหลดไฟล์ชื่อ `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (โดยที่ `xxxx` คือหมายเลขบิลด์)

#### ขั้นตอนที่ 2: แตกไฟล์ไบนารี

แตกไฟล์เก็บถาวรที่ดาวน์โหลดมา:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

ไดเรกทอรีนี้ตอนนี้มีบิลด์ของ `llama-cli.exe`, `llama-server.exe` และ `ggml-rpc-server.exe` ที่รองรับ ROCm ซึ่งคอมไพล์ไว้ล่วงหน้าสำหรับระบบ Ryzen AI Halo ของคุณ

#### ขั้นตอนที่ 3: ยืนยันการตรวจพบ GPU

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

ไปที่หน้าเวอร์ชันล่าสุดและดาวน์โหลดไฟล์เก็บถาวรที่ตรงกับแพลตฟอร์มและ GPU เป้าหมายของคุณ:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

ดาวน์โหลดไฟล์ชื่อ `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (โดยที่ `xxxx` คือหมายเลขบิลด์)

#### ขั้นตอนที่ 2: แตกไฟล์และเตรียมไบนารี

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

ไดเรกทอรีนี้ตอนนี้มีบิลด์ของ `llama-cli`, `llama-server` และ `rpc-server` ที่รองรับ ROCm ซึ่งคอมไพล์ไว้ล่วงหน้าสำหรับระบบ Ryzen AI Halo ของคุณ

#### ขั้นตอนที่ 3: ยืนยันการตรวจพบ GPU

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
เมื่อเตรียม llama.cpp บนแต่ละโหนดเรียบร้อยแล้ว ให้ไปที่ [การดาวน์โหลดโมเดล](#downloading-the-model)

### ตัวเลือกที่ 2: การคอมไพล์ซอร์สโค้ดด้วยตนเอง

<!-- @os:windows -->
#### ขั้นตอนที่ 1: คอมไพล์ llama.cpp

เปิด **x64 Native Tools Command Prompt** (ติดตั้งมาพร้อมกับ Visual Studio Build Tools) แล้วโคลนรีพอสิทอรี:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

เพิ่ม HIP ลงใน path ของคุณและคอมไพล์พร้อมรองรับ ROCm และ RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| แฟล็กการคอมไพล์ | วัตถุประสงค์ |
|-----------|---------|
| `-DGGML_HIP=ON` | เปิดใช้งานสแตกซอฟต์แวร์ ROCm/HIP |
| `-DGGML_RPC=ON` | เปิดใช้งาน RPC สำหรับการอนุมานแบบกระจาย |
| `-DGPU_TARGETS=gfx1151` | กำหนดเป้าหมายไปที่ GPU ของ Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | ใช้ระบบคอมไพล์ Ninja |

#### ขั้นตอนที่ 2: ยืนยันการตรวจพบ GPU

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

ขั้นตอนการคอมไพล์ด้านบนได้ตั้งค่า `%HIP_PATH%\bin` สำหรับเซสชันปัจจุบันเท่านั้น หากต้องการให้ไลบรารี HIP ใช้งานได้ในเทอร์มินัลใด ๆ (ไม่ใช่แค่ x64 Native Tools Command Prompt) ให้เพิ่มลงใน `PATH` ของผู้ใช้อย่างถาวร:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

เมื่อเตรียม llama.cpp บนแต่ละโหนดเรียบร้อยแล้ว ให้ไปที่ [การดาวน์โหลดโมเดล](#downloading-the-model)
<!-- @os:end -->

<!-- @os:linux -->
#### ขั้นตอนที่ 1: คอมไพล์ llama.cpp

โคลนรีพอสิทอรี:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

คอมไพล์พร้อมรองรับ ROCm และ RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| แฟล็กการคอมไพล์ | วัตถุประสงค์ |
|-----------|---------|
| `-DGGML_HIP=ON` | เปิดใช้งานสแตกซอฟต์แวร์ ROCm |
| `-DGGML_RPC=ON` | เปิดใช้งาน RPC สำหรับการอนุมานแบบกระจาย |
| `-DAMDGPU_TARGETS="gfx1151"` | กำหนดเป้าหมายไปที่ GPU ของ Ryzen AI Halo (Radeon 8060s) |

สำหรับตัวเลือกการคอมไพล์เพิ่มเติม โปรดดู [เอกสารการคอมไพล์ llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md)

#### ขั้นตอนที่ 2: ยืนยันการตรวจพบ GPU

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

เมื่อเตรียม llama.cpp บนแต่ละโหนดเรียบร้อยแล้ว ให้ไปที่ [การดาวน์โหลดโมเดล](#downloading-the-model)
<!-- @os:end -->

## การดาวน์โหลดโมเดล

คู่มือนี้ใช้ [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) ในรูปแบบการควอนไทซ์ `UD-Q2_K_XL` จาก [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL) การควอนไทซ์นี้พอดีกับหน่วยความจำ GPU รวมของโหนด Ryzen AI Halo ทั้งสี่

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

> **หมายเหตุ**: การดาวน์โหลดโมเดลต้องดำเนินการให้เสร็จสิ้นบน Machine 1 (คอนโทรลเลอร์) โหนดเวิร์กเกอร์ RPC (Machines 2, 3 และ 4) ไม่จำเป็นต้องมีสำเนาไฟล์โมเดลในเครื่อง

## การเปิดใช้งานโมเดลบนคลัสเตอร์

เอนจิน llama.cpp RPC (Remote Procedure Call) ช่วยให้อินสแตนซ์ llama.cpp หนึ่งตัวสามารถถ่ายโอนเลเยอร์ของโมเดลไปยังเวิร์กเกอร์ระยะไกลผ่านเครือข่ายได้ เครื่องหนึ่งทำหน้าที่เป็น **คอนโทรลเลอร์** (Machine 1) จัดการการแปลงโทเคน การจัดลำดับงาน และการประสานงาน ส่วนเครื่องอีกสามเครื่องแต่ละเครื่องรัน **RPC server** แบบน้ำหนักเบา (Machines 2, 3 และ 4) ซึ่งเปิดเผยหน่วยความจำและการประมวลผลของ GPU ให้กับคอนโทรลเลอร์

ในขณะโหลด llama.cpp จะแบ่งโมเดลออกเป็นส่วน ๆ ไปยังทั้งสี่โหนด เมื่อโหลดเสร็จแล้ว การอนุมานจะดำเนินไปราวกับว่ากำลังรันอยู่บนตัวเร่งความเร็วเพียงตัวเดียว โดย RPC จะจัดการการถ่ายโอนเทนเซอร์และการซิงโครไนซ์อยู่เบื้องหลัง

### ขั้นตอนที่ 1: เริ่มการทำงานของ RPC Servers (Machines 2, 3 และ 4)

บนแต่ละเครื่องในจำนวน Machines 2, 3 และ 4 ให้เริ่มการทำงานของ RPC server เพื่อเปิดเผยทรัพยากร GPU ของเครื่องนั้นให้กับคอนโทรลเลอร์:
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
| `-p` | พอร์ตที่ใช้กระจายสัญญาณ RPC server |
| `-c` | เปิดใช้งานแคชในเครื่องสำหรับเทนเซอร์ขนาดใหญ่ ช่วยหลีกเลี่ยงการถ่ายโอนข้อมูลผ่านเครือข่ายซ้ำ ๆ ระหว่างการโหลดโมเดล |
| `--host` | ที่อยู่ IP ที่ใช้ผูก RPC server (`0.0.0.0` สำหรับทุกอินเทอร์เฟซ) |

สำหรับตัวเลือกเพิ่มเติม โปรดดู [เอกสาร llama.cpp RPC](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md)

### ขั้นตอนที่ 2: เปิดใช้งานโมเดล (Machine 1)

เมื่อ RPC servers กำลังทำงานอยู่บน Machines 2, 3 และ 4 แล้ว ให้เปิดใช้งานการอนุมานจาก Machine 1 โดยใช้ `llama-cli` หรือ `llama-server` อย่างใดอย่างหนึ่ง
#### llama-cli

`llama-cli` มอบอินเทอร์เฟซแบบเทอร์มินัลสำหรับโต้ตอบกับโมเดลโดยตรง เหมาะสำหรับการทำเบนช์มาร์ก การดีบัก และการทดลองในระดับต่ำ

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

> **การหา `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: บนเครื่องที่ 2, 3 และ 4 แต่ละเครื่อง ให้รัน `hostname -I | awk '{print $1}'` เพื่อหาที่อยู่ IP ภายในของเครื่องนั้น
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

> **การหา `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: บนเครื่องที่ 2, 3 และ 4 แต่ละเครื่อง ให้รัน `ipconfig | findstr /C:"IPv4"` ใน Terminal (Powershell) เพื่อหาที่อยู่ IP ภายในของเครื่องนั้น

<!-- @os:end -->

เมื่อเริ่มทำงานแล้ว `llama-cli` จะแสดงความคืบหน้าในการโหลดโมเดล และเข้าสู่พรอมต์แบบโต้ตอบที่คุณสามารถสนทนากับโมเดลได้โดยตรง:

![llama-cli ทำงานกับ Kimi K2.6 บนสี่โหนด](assets/llama-cli-example.png)

#### llama-server

`llama-server` เปิดให้ใช้งานเอนจิน inference ตัวเดียวกันผ่านกระบวนการเซิร์ฟเวอร์แบบถาวร พร้อมเว็บ UI ในตัวและ API แบบ HTTP ที่เข้ากันได้กับ OpenAI นี่คืออินเทอร์เฟซที่แนะนำสำหรับการใช้งานระยะยาว การเข้าถึงโดยผู้ใช้หลายคน และการผสานรวมกับเครื่องมือภายนอก

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

> **การหา `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: บนเครื่องที่ 2, 3 และ 4 แต่ละเครื่อง ให้รัน `hostname -I | awk '{print $1}'` เพื่อหาที่อยู่ IP ภายในของเครื่องนั้น
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

> **การหา `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: บนเครื่องที่ 2, 3 และ 4 แต่ละเครื่อง ให้รัน `ipconfig | findstr /C:"IPv4"` ใน Terminal (Powershell) เพื่อหาที่อยู่ IP ภายในของเครื่องนั้น
<!-- @os:end -->

เมื่อเริ่มทำงานแล้ว ให้เปิด `http://<HOST_IP>:8081` ในเบราว์เซอร์ของคุณเพื่อเข้าถึงเว็บ UI ในตัว ซึ่งให้อินเทอร์เฟซแชทแบบเบราว์เซอร์สำหรับโต้ตอบกับโมเดล:

![เว็บ UI ของ llama-server ทำงานกับ Kimi K2.6 บนสี่โหนด](assets/llama-server-example.png)

<!-- @os:linux -->
> **การหา `<HOST_IP>`**: บนเครื่องที่ 1 ให้รัน `hostname -I | awk '{print $1}'` เพื่อหาที่อยู่ IP ภายในของเครื่องนั้น
<!-- @os:end -->

<!-- @os:windows -->
> **การหา `<HOST_IP>`**: บนเครื่องที่ 1 ให้รัน `ipconfig | findstr /C:"IPv4"` ใน Terminal (Powershell) เพื่อหาที่อยู่ IP ภายในของเครื่องนั้น
<!-- @os:end -->

#### ข้อมูลอ้างอิงพารามิเตอร์

| แฟล็ก | วัตถุประสงค์ |
|------|---------|
| `-m` | พาธไปยังไฟล์โมเดล GGUF (ใช้ชาร์ดแรก `00001-of-00008`) |
| `-c` | ขนาดบริบทเป็นโทเคน ค่าที่มากขึ้นจะใช้หน่วยความจำมากขึ้น |
| `-fa on` | เปิดใช้งาน rocWMMA Flash Attention เพื่อประสิทธิภาพที่ดีขึ้นบน AMD GPU |
| `-ngl 999` | ถ่ายโอนเลเยอร์โมเดลทั้งหมดไปยัง GPU |
| `-lm none` | ตั้งค่าโหมดการโหลดโมเดลเป็น `none` ซึ่งปิดการใช้ memory-mapping เพื่อลดเวลาในการโหลดเมื่อขนาดโมเดลเกิน RAM ของระบบแต่ยังพอดีกับ VRAM |
| `-b` | ขนาดแบตช์เชิงตรรกะเป็นโทเคน การตั้งค่าเป็น 4096 จะสร้างสมดุลระหว่างปริมาณงานและการใช้หน่วยความจำข้ามโหนด |
| `-ub` | ขนาดแบตช์ (ไมโคร) เชิงกายภาพสำหรับการประมวลผลพรอมต์ การตั้งค่าให้ตรงกับ `-b` จะช่วยหลีกเลี่ยงค่าใช้จ่ายในการแบ่งส่วนที่ไม่จำเป็น |
| `--host` | IP สำหรับผูก `llama-server` (เฉพาะ `llama-server` เท่านั้น) |
| `--port` | พอร์ตสำหรับให้บริการ HTTP API (เฉพาะ `llama-server` เท่านั้น) |
| `--rpc` | รายการจุดสิ้นสุดของ RPC worker ที่คั่นด้วยเครื่องหมายจุลภาค (`IP:port`) |

สำหรับการใช้งานพารามิเตอร์แบบเต็ม โปรดดู [เอกสาร llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) และ [เอกสาร llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)

## ขั้นตอนถัดไป

- **เชื่อมต่อแอปพลิเคชันของบุคคลที่สาม**: `llama-server` เปิดให้ใช้งาน API ที่เข้ากันได้กับ OpenAI ชี้แอปพลิเคชันที่เข้ากันได้กับ OpenAI ใดๆ (เช่น Open WebUI) ไปที่ `http://<HOST_IP>:8081` พร้อมด้วยคีย์ API ตัวแทนใดๆ (เช่น `none`) เพื่อเชื่อมต่อกับคลัสเตอร์ของคุณ
- **สำรวจโมเดลอื่นๆ**: เรียกดู GGUF ที่ผ่านการ quantize บน [Hugging Face](https://huggingface.co/models?search=gguf) เพื่อค้นหาโมเดลที่พอดีกับหน่วยความจำ GPU รวมของคลัสเตอร์ของคุณ
- **ขยายขนาดเกินกว่าสี่โหนด**: เพิ่มระบบ Ryzen AI Halo เพิ่มเติมเป็น RPC worker เพิ่มเติม เพื่อเข้าถึงโมเดลที่มีขนาดเกินกว่า 1 ล้านล้านพารามิเตอร์ ส่งจุดสิ้นสุดเพิ่มเติมไปยัง `--rpc` เป็นรายการที่คั่นด้วยเครื่องหมายจุลภาค (เช่น `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)