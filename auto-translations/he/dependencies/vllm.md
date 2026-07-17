<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM מסופק דרך תמונת קונטיינר מוכנה מראש עם תמיכה ב-ROCm. השתמש בפקודת ה-launcher במקום להתקין את vLLM או PyTorch ישירות על המארח:

```bash
vllm-launch
```

ה-launcher מפעיל את הקונטיינר, מכוון ל-GPU המשולב, וחושף את ה-API של vLLM התואם ל-OpenAI בכתובת `http://localhost:8001`.