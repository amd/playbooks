<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# การกำหนดค่าแพลตฟอร์ม

เอกสารนี้อธิบายการกำหนดค่าแพลตฟอร์มที่คาดหวังสำหรับการรัน playbook นี้

## แอปพลิเคชัน / เฟรมเวิร์กที่จำเป็น

| Component       | Expected Configuration               | หมายเหตุ                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python with `venv` support         | ใช้สำหรับสร้างและเปิดใช้งาน `kernel-env`                                     |
| ROCm Python SDK | ROCm 7.13 package family             | ติดตั้งผ่านขั้นตอน dependency flow ของ playbook                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | จำเป็นสำหรับ `torch.cuda`, HIP runtime, JIT compilation, และ `CUDAExtension` |
| GPU Driver      | AMD GPU driver with ROCm/HIP support | จำเป็นก่อนที่ PyTorch จะสามารถตรวจพบ AMD GPU ได้                               |

> หมายเหตุ: หากคุณใช้งานบน AMD Ryzen™ AI Halo Developer Platform, AMD ROCm™ software และ PyTorch จะถูกติดตั้งไว้ล่วงหน้าแล้ว

## ข้อกำหนดเบื้องต้นสำหรับ Linux

แพ็กเกจระบบต่อไปนี้เป็นสิ่งจำเป็น:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` จำเป็นสำหรับการสร้าง `kernel-env`
* `build-essential`, `gcc`, และ `g++` จำเป็นสำหรับการทำตาม walkthrough ส่วนขยาย C++
* `amd-smi` ใช้สำหรับการตรวจสอบการมองเห็น/การใช้งาน GPU บน Linux

ตัวอย่างส่วนขยาย C++ จะสร้างโมดูล `.so` แบบ native จากไฟล์ `.cu` โดยใช้เส้นทาง `CUDAExtension` ของ PyTorch

## ข้อกำหนดเบื้องต้นสำหรับ Windows

ผู้ใช้งาน Windows ต้องการ:

* Python ที่สามารถเรียกใช้ได้ผ่าน `python`
* ติดตั้งเวอร์ชันล่าสุด: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) หรือ [เวอร์ชันใหม่กว่า](https://visualstudio.microsoft.com/vs/community/) พร้อม workload **Desktop development with C++**

สภาพแวดล้อม C++ ของ Visual Studio ต้องมี:
* `vcvars64.bat`
* `cl.exe`
* เส้นทาง include และ library ของ Windows SDK

ตัวอย่างส่วนขยาย C++ จะสร้างโมดูล `.pyd` แบบ native จากไฟล์ `.cu` โดยใช้เส้นทาง `CUDAExtension` ของ PyTorch