<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# การกำหนดค่าแพลตฟอร์ม

เอกสารนี้อธิบายการกำหนดค่าแพลตฟอร์มที่คาดหวังสำหรับการรันเพลย์บุ๊กนี้

## แอปพลิเคชัน/เฟรมเวิร์กที่จำเป็น

### Windows/Linux

GAIA ควรติดตั้งไว้ล่วงหน้าโดยใช้คำแนะนำที่ให้ไว้ใน[คู่มือการติดตั้ง GAIA](../../dependencies/gaia.md)

Lemonade Server ควรติดตั้งไว้ล่วงหน้าโดยใช้คำแนะนำที่ให้ไว้ใน[คู่มือการติดตั้ง Lemonade](../../dependencies/lemonade.md)

## โมเดลที่จำเป็น

### Windows/Linux

Hardware Advisor Agent ใช้ **Qwen3-Coder-30B** สำหรับการประมวลผลของเอเจนต์ โมเดลนี้จะถูกดาวน์โหลดโดยอัตโนมัติระหว่าง `gaia init` ไม่จำเป็นต้องดาวน์โหลดโมเดลด้วยตนเอง