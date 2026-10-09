<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ดาวน์โหลด GPT-OSS 20B สำหรับ Ollama

ดึงโมเดล GPT-OSS 20B มาที่ Ollama:

```bash
ollama pull gpt-oss:20b
```

เซิร์ฟเวอร์ Ollama ต้องทำงานอยู่เพื่อให้การดึงโมเดลสำเร็จ; `ollama serve` จะเริ่มเซิร์ฟเวอร์หากยังไม่ได้ทำงานอยู่

ตรวจสอบว่ามีโมเดลอยู่แล้ว:

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