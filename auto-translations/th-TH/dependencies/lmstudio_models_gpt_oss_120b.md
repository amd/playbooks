<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### การดาวน์โหลด GPT-OSS 120B บน LM Studio

หากต้องการดาวน์โหลดโมเดล GPT-OSS 120B:

1. กด "Ctrl" + "Shift" + "M" บนแป้นพิมพ์ของคุณ หรือคลิกที่แท็บ "Discover" (ไอคอนแว่นขยาย) บนแถบด้านข้างซ้าย
2. ค้นหา `ggml-org/gpt-oss-120b-GGUF`
3. เลือก `mxfp4` แล้วคลิก Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio จะดาวน์โหลดและวางโมเดลไว้ในไดเรกทอรีที่ถูกต้องโดยอัตโนมัติ

หากคุณต้องการดาวน์โหลดโมเดลเพิ่มเติม คุณสามารถค้นหาได้ในแท็บ Discover และ LM Studio จะจัดการส่วนที่เหลือให้

<!-- @os:windows -->
<!-- @test:id=lmstudio-model-present-windows timeout=60 hidden=True -->
```powershell
lms ls --llm | Select-String -Pattern "gpt-oss-120b"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-model-present-linux timeout=60 hidden=True -->
```bash
lms ls --llm | grep -i "gpt-oss-120b"
```
<!-- @test:end -->
<!-- @os:end -->