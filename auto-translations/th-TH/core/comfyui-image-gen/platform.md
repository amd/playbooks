<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **การแปลด้วยเครื่อง.** หน้านี้ได้รับการแปลโดยอัตโนมัติจากภาษาอังกฤษ และยังไม่ได้รับการตรวจสอบโดยมนุษย์ อาจมีข้อผิดพลาด และคำแนะนำ คำสั่ง การดาวน์โหลด ความพร้อมใช้งานของผลิตภัณฑ์ หรือเนื้อหาอื่นๆ บางส่วนอาจแตกต่างกันไปตามภาษาหรือภูมิภาค ในกรณีที่มีความไม่สอดคล้องหรือความคลาดเคลื่อนใดๆ ให้ถือว่าเวอร์ชันภาษาอังกฤษต้นฉบับของ playbook เป็นฉบับที่มีผลบังคับใช้และมีอำนาจเหนือกว่า
<!-- auto-translated-disclaimer:end -->

# การกำหนดค่าแพลตฟอร์ม

เอกสารนี้อธิบายการกำหนดค่าแพลตฟอร์มที่คาดหวังสำหรับการรัน playbook นี้

## แอป/เฟรมเวิร์กที่จำเป็น
### Windows/Linux

ควรติดตั้ง ComfyUI ล่วงหน้าโดยใช้คำแนะนำที่ระบุไว้ใน [คู่มือการติดตั้ง ComfyUI](../../dependencies/comfyui.md)

## โมเดลที่จำเป็น

### Windows/Linux

โมเดลต่อไปนี้ต้องมีอยู่ในไดเรกทอรีที่ติดตั้ง ComfyUI ภายในโฟลเดอร์ `models`

| ประเภทโมเดล | ชื่อไฟล์ | ขนาด | ตำแหน่ง | ดาวน์โหลด |
|------------|----------|------|----------|----------|
| Text Encoder | `qwen_3_4b.safetensors` | 7.49 GB | `models/text_encoders/` | [ลิงก์](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162.25 MB | `models/loras/` | [ลิงก์](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Diffusion Model | `z_image_turbo_bf16.safetensors` | 11.46 GB | `models/diffusion_models/` | [ลิงก์](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319.77 MB | `models/vae/` | [ลิงก์](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


หากต้องการทดสอบว่าโมเดลถูกวางไว้อย่างถูกต้องหรือไม่ ให้ [แสดงตัวอย่าง playbook ของ ComfyUI โดยใช้เว็บไซต์ onboarding](../../README.md#previewing-the-playbooks) แล้วทำตามคำแนะนำ โมเดลจะถูกวางไว้อย่างถูกต้องหากไม่มีหน้า "Models not found" ปรากฏขึ้นเมื่อเปิดใช้งานเทมเพลต Z-Image Turbo