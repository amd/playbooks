<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM מסופק באמצעות תמונת קונטיינר בנויה מראש עם תמיכת ROCm. השתמשו בפקודת המפעיל (launcher) במקום להתקין את vLLM או PyTorch ישירות על המארח:

```bash
vllm-launch
```

המפעיל מפעיל את הקונטיינר, מכוון אל ה-GPU המשולב, וחושף את ה-API של vLLM התואם ל-OpenAI בכתובת `http://localhost:8001`.