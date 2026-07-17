<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM مُقدَّم عبر صورة حاوية مُعدَّة مسبقًا مع دعم ROCm. استخدم أمر التشغيل بدلاً من تثبيت vLLM أو PyTorch مباشرةً على المضيف:

```bash
vllm-launch
```

يبدأ المُشغِّل الحاوية، ويستهدف iGPU، ويعرض واجهة برمجة التطبيقات المتوافقة مع OpenAI الخاصة بـ vLLM على `http://localhost:8001`.