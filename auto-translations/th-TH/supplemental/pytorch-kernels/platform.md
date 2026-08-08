<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **การแปลด้วยเครื่อง.** หน้านี้ได้รับการแปลโดยอัตโนมัติจากภาษาอังกฤษ และยังไม่ได้รับการตรวจสอบโดยมนุษย์ อาจมีข้อผิดพลาด และคำแนะนำ คำสั่ง การดาวน์โหลด ความพร้อมใช้งานของผลิตภัณฑ์ หรือเนื้อหาอื่นๆ บางส่วนอาจแตกต่างกันไปตามภาษาหรือภูมิภาค ในกรณีที่มีความไม่สอดคล้องหรือความคลาดเคลื่อนใดๆ ให้ถือว่าเวอร์ชันภาษาอังกฤษต้นฉบับของ playbook เป็นฉบับที่มีผลบังคับใช้และมีอำนาจเหนือกว่า
<!-- auto-translated-disclaimer:end -->

# การกำหนดค่าแพลตฟอร์ม

เอกสารนี้อธิบายการกำหนดค่าแพลตฟอร์มที่คาดหวังสำหรับการรันเพลย์บุ๊กนี้

## แอปพลิเคชัน/เฟรมเวิร์กที่จำเป็น

| คอมโพเนนต์       | การกำหนดค่าที่คาดหวัง               | หมายเหตุ                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python ที่รองรับ `venv`         | ใช้เพื่อสร้างและเปิดใช้งาน `kernel-env`                                     |
| ROCm Python SDK | กลุ่มแพ็กเกจ ROCm 7.13             | ติดตั้งผ่านขั้นตอนการติดตั้งไลบรารีที่จำเป็นของเพลย์บุ๊ก                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | จำเป็นสำหรับ `torch.cuda`, รันไทม์ HIP, การคอมไพล์ JIT และ `CUDAExtension` |
| GPU Driver      | ไดรเวอร์ AMD GPU ที่รองรับ ROCm/HIP | จำเป็นก่อนที่ PyTorch จะสามารถตรวจพบ AMD GPU ได้                               |

> หมายเหตุ: หากคุณกำลังใช้งานบน AMD Ryzen™ AI Halo Developer Platform ซอฟต์แวร์ AMD ROCm™ และ PyTorch จะถูกติดตั้งไว้ล่วงหน้าแล้ว

## ข้อกำหนดเบื้องต้นสำหรับ Linux

จำเป็นต้องมีแพ็กเกจระบบต่อไปนี้:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` จำเป็นสำหรับการสร้าง `kernel-env`
* `build-essential`, `gcc` และ `g++` จำเป็นสำหรับบทเรียนส่วนขยาย C++
* `amd-smi` ใช้สำหรับการตรวจสอบการมองเห็น/การใช้งาน GPU บน Linux

ตัวอย่างส่วนขยาย C++ จะสร้างโมดูล `.so` แบบเนทีฟจากไฟล์ `.cu` โดยใช้เส้นทาง `CUDAExtension` ของ PyTorch

## ข้อกำหนดเบื้องต้นสำหรับ Windows

รันเนอร์ Windows ต้องมี:

* Python ที่สามารถเรียกใช้ผ่าน `python`
* ติดตั้งเวอร์ชันล่าสุด: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) หรือ[เวอร์ชันใหม่กว่า](https://visualstudio.microsoft.com/vs/community/) พร้อมชุดงาน **Desktop development with C++**

สภาพแวดล้อม Visual Studio C++ ต้องมี:
* `vcvars64.bat`
* `cl.exe`
* เส้นทาง include และ library ของ Windows SDK

ตัวอย่างส่วนขยาย C++ จะสร้างโมดูล `.pyd` แบบเนทีฟจากไฟล์ `.cu` โดยใช้เส้นทาง `CUDAExtension` ของ PyTorch