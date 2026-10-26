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

# การพัฒนาจากระยะไกลด้วย AMD Sync

## ภาพรวม

**AMD Sync** เปลี่ยนแล็ปท็อปของคุณให้กลายเป็นห้องควบคุมระยะไกลสำหรับ AMD Ryzen™ AI Halo ข้ามขั้นตอนการตั้งค่า SSH, คีย์ และ IDE ด้วยมือ — เพียงติดตั้ง AMD Sync แล้วเข้าถึงเทอร์มินัลระยะไกล, VS Code, JupyterLab และแดชบอร์ด GPU/CPU/หน่วยความจำแบบเรียลไทม์บน Ryzen AI Halo ได้ด้วยการคลิกเพียงครั้งเดียว

เครื่องของคุณยังคงคุ้นเคยเหมือนเดิม ส่วนคำสั่ง โน้ตบุ๊ก และโมเดลทุกอย่างจะทำงานบน Ryzen AI Halo

> **เคล็ดลับ**: หน้านี้จะมีข้อมูลอัปเดตใหม่ๆ ของ AMDSync 

## สิ่งที่คุณจะได้เรียนรู้

- เปิดใช้งาน SSH บน Ryzen AI Halo และเชื่อมต่อจาก AMD Sync
- เปิดใช้งาน VS Code, Terminal, JupyterLab และ Live Metrics กับ Ryzen AI Halo ได้ด้วยการคลิกเพียงครั้งเดียว
- จัดระเบียบงานระยะไกลโดยใช้โฟลเดอร์โปรเจกต์ที่ AMD Sync จัดการให้

---

## แนวคิดหลัก

AMD Sync ประกอบด้วยสองฝั่ง: **ฝั่งไคลเอนต์** (แล็ปท็อปของคุณ ซึ่งรันแอป AMD Sync) และ **ฝั่งเซิร์ฟเวอร์** (Ryzen AI Halo ซึ่งรันเซิร์ฟเวอร์ SSH ที่ AMD Sync เจาะอุโมงค์เข้าไป) ทุกสิ่งที่คุณเปิดใช้งานจาก AMD Sync — VS Code, เทอร์มินัล, โน้ตบุ๊ก — จะเปิดในเครื่องแต่ทำงานบน Ryzen AI Halo

> **ไคลเอนต์ที่รองรับ:** Windows 11 และ Linux ไม่รองรับ macOS

---

## ขั้นตอนที่ 1 — เปิดใช้งาน SSH บน Ryzen AI Halo


> **หมายเหตุ:** บน Windows, Ryzen AI Halo มาพร้อมกับเซิร์ฟเวอร์ SSH ที่ *ปิดอยู่โดยค่าเริ่มต้น* ส่วนบน Linux จะมาพร้อมกับเซิร์ฟเวอร์ SSH ที่ *เปิดอยู่โดยค่าเริ่มต้น*

1. บน Ryzen AI Halo เปิด **AMD Ryzen™ AI Developer Center**
2. ไปที่แท็บ **Remote**
3. เปิดสวิตช์ **SSH Server**
4. จดบันทึก **IP Address**, **Port** และ **Username** ที่แสดงอยู่ภายใต้ **Server Information** — คุณจะต้องนำค่าเหล่านี้ไปวางใน AMD Sync

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **หมายเหตุ:** นี่คือ AMD Developer Center สำหรับ Windows ส่วนเวอร์ชัน Linux อาจมี UI ที่แตกต่างกัน แต่มีฟังก์ชันการทำงานระยะไกลที่คล้ายคลึงกัน

> **เคล็ดลับ:** AMD Sync จะขอ **รหัสผ่านการเข้าสู่ระบบ OS** ของผู้ใช้นั้น ไม่ใช่รหัสผ่านจาก Developer Center

---

## ขั้นตอนที่ 2 — ติดตั้ง AMD Sync บนไคลเอนต์ของคุณ

AMD Sync ทำงานบน Windows 11 และ Linux ดาวน์โหลดตัวติดตั้งสำหรับ OS ของคุณ จากนั้นทำตามขั้นตอนด้านล่าง หลังจากติดตั้งแล้ว ให้คลิก **Accept & Install** บนหน้าจอ **Get Started** — AMD Sync จะเปิดใช้งานโดยอัตโนมัติเมื่อเสร็จสิ้น

### Windows

[ดาวน์โหลด AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. ดับเบิลคลิก `AMDSyncInstaller.exe`
2. คลิก **Accept & Install**

> หากไฟร์วอลล์ของ Windows แจ้งเตือน ให้อนุญาตให้ AMD Sync เข้าถึงเครือข่ายเพื่อให้สามารถเชื่อมต่อกับ Ryzen AI Halo ผ่าน SSH ได้

### Linux

คลิกลิงก์เพื่อดาวน์โหลดรูปแบบไฟล์ที่คุณต้องการ:

| รูปแบบ | ดาวน์โหลด | คำสั่งติดตั้ง |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **หมายเหตุ:** Ubuntu App Center อาจแจ้งเตือนไฟล์ `.deb` ที่เปิดในเครื่องว่า *"อาจไม่ปลอดภัย"* ซึ่งเป็นคำเตือนมาตรฐานสำหรับตัวติดตั้งในเครื่องจากบุคคลที่สามทั่วไป หากการดับเบิลคลิกไฟล์ `.deb` ไม่สำเร็จ ให้ใช้คำสั่งเทอร์มินัลด้านบน

---

## ขั้นตอนที่ 3 — เชื่อมต่อกับ Ryzen AI Halo ของคุณ

เมื่อเปิดใช้งานครั้งแรก AMD Sync จะแสดงฟอร์ม **Add a Remote Device** กรอกข้อมูลโดยใช้ค่าจากแท็บ **Remote** ของ Developer Center

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| ฟิลด์ | หมายเหตุ |
|-------|-------|
| **Device Name** *(ไม่บังคับ)* | ป้ายชื่อที่เป็นมิตร เช่น `Ryzen AI Halo` ค่าเริ่มต้นคือ `Device 1`, `Device 2`, … |
| **Hostname or IP** | จากแท็บ Remote |
| **SSH Port** | จากแท็บ Remote (ตัวเลขเท่านั้น) |
| **Username** | ชื่อบัญชี OS ของคุณบน Ryzen AI Halo |
| **Password** | รหัสผ่านเข้าสู่ระบบ OS ของคุณ — จะถูกปิดบังขณะพิมพ์ |

คลิก **Add Device** หลังจากหน้าจอโหลดสั้นๆ คุณจะเห็น **"Connection Successful"** และเข้าสู่หน้าโฮม ซึ่งอยู่ในถาดระบบของคุณ คลิกออกจากหน้าต่างเพื่อปิด AMD Sync จะยังคงทำงานอยู่และพร้อมใช้งานได้ด้วยการคลิกเพียงครั้งเดียว

> **หากการเชื่อมต่อล้มเหลว** AMD Sync จะกลับไปที่ฟอร์มพร้อมกับค่าที่คุณกรอกไว้เดิม สาเหตุที่พบบ่อยคือ SSH ถูกปิดใช้งานบน Ryzen AI Halo, รหัสผ่านไม่ถูกต้อง หรืออุปกรณ์ทั้งสองอยู่คนละเครือข่ายกัน

---

## ขั้นตอนที่ 4 — เปิดใช้งานเครื่องมือระยะไกลเครื่องแรกของคุณ

หน้าโฮมมีคอมโพเนนต์ที่ใช้งานได้ด้วยการคลิกเพียงครั้งเดียวห้ารายการ — ทั้งหมดใช้งานได้ไม่ว่าไคลเอนต์และ Ryzen AI Halo จะรัน OS ใดก็ตาม

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| คอมโพเนนต์ | สิ่งที่ทำ |
|-----------|--------------|
| **Directory** | เลือกโฟลเดอร์บน Ryzen AI Halo ที่ VS Code, Terminal และ JupyterLab จะเปิดใช้งาน ค่าเริ่มต้นคือพื้นที่ทำงาน `Documents/AMD_Sync` ที่จัดการให้ |
| **VS Code** | เปิด VS Code ในเครื่องพร้อมอุโมงค์ SSH เข้าไปยังโฟลเดอร์ที่เลือก |
| **Terminal** | เปิดเทอร์มินัลในเครื่องที่เชื่อมต่อ SSH กับ Ryzen AI Halo ในโฟลเดอร์ที่เลือก |
| **JupyterLab** | เปิดโปรเจกต์โน้ตบุ๊กที่เชื่อมต่อ SSH กับ Ryzen AI Halo โดยจำกัดขอบเขตไว้ในโฟลเดอร์ที่เลือก |
| **Live Metrics** | มุมมองแบบเรียลไทม์ของการใช้งาน GPU, หน่วยความจำ และ CPU บน Ryzen AI Halo |

### ลองใช้ VS Code

สำหรับการเปิดใช้งานครั้งแรก ลองใช้ **VS Code** คำแนะนำต่อไปนี้เป็นของ Linux แต่ประสบการณ์บน Windows ก็คล้ายคลึงกัน

1. ปล่อย **Directory** ไว้ที่ค่าเริ่มต้น `~/Documents/AMD_Sync`
2. คลิก **VS Code**
3. AMD Sync จะสร้าง `Documents/AMD_Sync/Project_1` บน Ryzen AI Halo และเปิด VS Code ในเครื่องโดยเจาะอุโมงค์เข้าไป

ตอนนี้คุณกำลังแก้ไขไฟล์ที่อยู่บน Ryzen AI Halo ด้วยการตั้งค่า VS Code ในเครื่องของคุณ สร้าง `helloworld.py` เพิ่ม `print("hello world")` เปิดเทอร์มินัลในตัว (`` Ctrl + ` ``) และรันมัน:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

แถบสถานะจะแสดง **SSH: Linux** — เป็นหลักฐานว่าโค้ดของคุณกำลังทำงานบน Ryzen AI Halo ไม่ใช่บนแล็ปท็อปของคุณ
### ลองใช้ Terminal

คลิก **Terminal** เพื่อเชื่อมต่อผ่าน SSH เข้าสู่โฟลเดอร์เดียวกันได้ทันทีโดยไม่ต้องละมือจากคีย์บอร์ด

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

บน Windows เทอร์มินัลเริ่มต้นคือ **PowerShell** — สามารถเปลี่ยนเป็น **Windows Command Prompt** ได้จากเมนู Settings หากต้องการ บน Linux AMD Sync จะใช้เทอร์มินัลเริ่มต้นของระบบ

---

## วิธีการทำงานของ Directory

ดรอปดาวน์ **Directory** คือตัวควบคุมที่สำคัญที่สุดเพียงหนึ่งเดียวใน AMD Sync — เป็นตัวกำหนดว่าเครื่องมือทุกตัวที่คุณเปิดใช้งานจะไปอยู่ที่ใดบน Ryzen AI Halo

- **`~/Documents/AMD_Sync` (ค่าเริ่มต้น)** — การเปิด VS Code หรือ JupyterLab จากที่นี่จะสร้างโฟลเดอร์โปรเจกต์ใหม่ให้โดยอัตโนมัติ (`Project_1`, `Project_2`, … สำหรับ VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … สำหรับ JupyterLab)
- **โฟลเดอร์โปรเจกต์ที่มีอยู่แล้ว** — โฟลเดอร์ลูกโดยตรงใดๆ ของ `AMD_Sync` (รวมถึงโฟลเดอร์ที่คุณสร้างเองบน Ryzen AI Halo) จะปรากฏในดรอปดาวน์ โฟลเดอร์ล่าสุดที่คุณใช้งานจะกลายเป็นค่าเริ่มต้นในครั้งถัดไป
- **เส้นทางที่กำหนดเอง** — พิมพ์เส้นทางแบบ absolute เพื่อเปิดโฟลเดอร์ที่อื่นบน Ryzen AI Halo AMD Sync จะทำการ *เปิด* เท่านั้น — จะไม่สร้างโฟลเดอร์นอก `AMD_Sync` และเส้นทางที่กำหนดเองจะไม่ถูกบันทึกไว้ข้ามเซสชัน

หากเส้นทางที่กำหนดเองใช้งานไม่ได้ AMD Sync จะแจ้งเหตุผลให้ทราบ เช่น ไวยากรณ์ไม่ถูกต้อง โฟลเดอร์ไม่มีอยู่จริง หรือเส้นทางนั้นชี้ไปยังไฟล์แทนที่จะเป็นโฟลเดอร์

---

## Live Metrics และ JupyterLab

- **Live Metrics** — แดชบอร์ดแบบเรียลไทม์แสดงการใช้งาน GPU หน่วยความจำ และ CPU เป็นวิธีที่เร็วที่สุดในการยืนยันว่าการฝึกโมเดลระยะไกลกำลังทำงานบนฮาร์ดแวร์จริง
- **JupyterLab** — โปรเจกต์โน้ตบุ๊กแบบเต็มรูปแบบที่เชื่อมต่อ SSH กับ Ryzen AI Halo พร้อมเทอร์มินัลในตัวสำหรับผสมผสานเซลล์โน้ตบุ๊กและคำสั่งเชลล์ได้โดยไม่ต้องออกจาก UI

---

## Settings และอุปกรณ์หลายเครื่อง

เมนู **Settings** มีสามแท็บ ได้แก่

| แท็บ | สิ่งที่ครอบคลุม |
|-----|----------------|
| **Devices** | แสดงรายการ Ryzen AI Halo ทุกเครื่องที่คุณเคยเชื่อมต่อสำเร็จ สามารถเชื่อมต่อใหม่ แก้ไขข้อมูลรับรอง หรือเพิ่มอุปกรณ์ใหม่ได้ |
| **Information** | ลิงก์ไปยังเอกสารและฟอรัมสนับสนุน |
| **Customize** | ย้ายตำแหน่งแอปบนเดสก์ท็อปของคุณ สลับประเภทเทอร์มินัล (เฉพาะ Windows) และตรวจสอบการอัปเดตของ AMD Sync |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **ประเภทเทอร์มินัล (Windows)** — เลือกระหว่าง **PowerShell** (ค่าเริ่มต้น) และ **Windows Command Prompt**
- **ประเภทเทอร์มินัล (Linux)** — มีให้ใช้เฉพาะเทอร์มินัลเริ่มต้นของระบบเท่านั้น
- **การอัปเดตแอป** — แท็บนี้เป็นจุดที่เหมาะสมในการตรวจสอบและติดตั้ง AMD Sync เวอร์ชันใหม่จากภายใน UI โดยตรง โดยไม่ต้องใช้ตัวอัปเดตแยกต่างหาก

> อุปกรณ์จะปรากฏใต้ **Devices** ก็ต่อเมื่อเชื่อมต่อสำเร็จในครั้งแรกเท่านั้น ดังนั้นความพยายามที่ล้มเหลวจะไม่ไปรกรายการ

---

## การแก้ไขปัญหา

- **การเชื่อมต่อล้มเหลวทันที** — ตรวจสอบว่าเปิดใช้งาน SSH server บนแท็บ **Remote** ของ Ryzen AI Halo ใน Developer Center แล้ว
- **ข้อผิดพลาดรหัสผ่านไม่ถูกต้อง** — ใช้ **รหัสผ่านสำหรับเข้าสู่ระบบ OS** บน Ryzen AI Halo ไม่ใช่รหัสผ่านที่นำมาจาก Developer Center
- **ปุ่ม VS Code ไม่มีการตอบสนอง** — ติดตั้ง VS Code บนเครื่องไคลเอนต์ของคุณจาก [code.visualstudio.com](https://code.visualstudio.com)
- **ไอคอน AMD Sync บนทรายหายไป (Linux/GNOME)** — ติดตั้งและเปิดใช้งานส่วนขยาย AppIndicator
- **ไฟล์ `.deb` เปิดไม่ได้จากตัวจัดการไฟล์** — ใช้คำสั่ง `sudo apt install ./AMDSyncInstaller.deb` จากเทอร์มินัล
- **หน้าตั้งค่าปรากฏซ้ำทุกครั้งที่เปิดใช้งาน (Linux)**: ปลดล็อก login keyring ของคุณ หรือเปิดใช้งานด้วย `--password-store=gnome-libsecret` จากนั้นทำการตั้งค่าใหม่อีกครั้งหนึ่งครั้ง

---