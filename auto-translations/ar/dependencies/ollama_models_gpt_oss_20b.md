<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### تنزيل GPT-OSS 20B من أجل Ollama

اسحب نموذج GPT-OSS 20B إلى Ollama:

```bash
ollama pull gpt-oss:20b
```

يجب أن يكون خادم Ollama قيد التشغيل حتى تنجح عملية السحب؛ يؤدي الأمر `ollama serve` إلى تشغيله إذا لم يكن يعمل بالفعل.

تأكد من وجود النموذج:

```bash
ollama list
```

يجب أن تشاهد `gpt-oss:20b` في المخرجات إلى جانب حجمه وتاريخ آخر تعديل له.

<!-- @os:linux -->
<!-- @test:id=ollama-model-present-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
ollama list | grep -q 'gpt-oss:20b'
```
<!-- @test:end -->
<!-- @os:end -->