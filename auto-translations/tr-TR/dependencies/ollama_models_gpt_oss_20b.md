<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Ollama için GPT-OSS 20B İndirme

GPT-OSS 20B modelini Ollama'ya çekin:

```bash
ollama pull gpt-oss:20b
```

Çekme işleminin başarılı olması için Ollama sunucusunun çalışıyor olması gerekir; eğer zaten çalışmıyorsa `ollama serve` komutu onu başlatır.

Modelin mevcut olduğunu doğrulayın:

```bash
ollama list
```

Çıktıda `gpt-oss:20b` modelini, boyutu ve son değiştirilme tarihiyle birlikte görmelisiniz.

<!-- @os:linux -->
<!-- @test:id=ollama-model-present-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
ollama list | grep -q 'gpt-oss:20b'
```
<!-- @test:end -->
<!-- @os:end -->