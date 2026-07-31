<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

يُوفَّر vLLM من خلال صورة حاوية جاهزة مسبقًا (prebuilt container image) مع دعم ROCm. استخدم أمر المُشغِّل (launcher) بدلاً من تثبيت vLLM أو PyTorch مباشرةً على المضيف:

```bash
vllm-launch
```

يقوم المُشغِّل بتشغيل الحاوية، واستهداف الـ GPU المدمج (integrated GPU)، وإتاحة واجهة برمجة تطبيقات vLLM المتوافقة مع OpenAI على `http://localhost:8001`.