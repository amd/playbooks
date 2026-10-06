<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ดาวน์โหลด GPT-OSS 20B สำหรับ Ollama

ดึงโมเดล GPT-OSS 20B ลงใน Ollama:

```bash
ollama pull gpt-oss:20b
```

เซิร์ฟเวอร์ Ollama ต้องทำงานอยู่เพื่อให้การดึงข้อมูลสำเร็จ `ollama serve` จะเริ่มต้นเซิร์ฟเวอร์หากยังไม่ได้ทำงานอยู่

ยืนยันว่ามีโมเดลอยู่:

```bash
ollama list
```

คุณควรเห็น `gpt-oss:20b` ในผลลัพธ์พร้อมกับขนาดและวันที่แก้ไขล่าสุด

<!-- @os:linux -->
<!-- @test:id=ollama-model-present-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
ollama list | grep -q 'gpt-oss:20b'
```
<!-- @test:end -->
<!-- @os:end -->