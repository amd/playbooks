<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM มีให้ใช้งานผ่านอิมเมจคอนเทนเนอร์ที่สร้างไว้ล่วงหน้าพร้อมรองรับ ROCm ใช้คำสั่ง launcher แทนการติดตั้ง vLLM หรือ PyTorch โดยตรงบนโฮสต์:

```bash
vllm-launch
```

launcher จะเริ่มต้นคอนเทนเนอร์ กำหนดเป้าหมายไปที่ iGPU และเปิดเผย vLLM API ที่เข้ากันได้กับ OpenAI บน `http://localhost:8001`