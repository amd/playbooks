<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 为 Lemonade 下载 GPT-OSS 20B

Lemonade 服务器提供 GPT-OSS 20B MXFP4 GGUF 模型(`gpt-oss-20b-mxfp4-GGUF`)服务。要提前下载该模型:

```bash
lemonade pull gpt-oss-20b-mxfp4-GGUF
```

如果模型尚未存在,`lemonade run gpt-oss-20b-mxfp4-GGUF` 在首次使用时也会下载该模型,然后将其加载以进行推理。

拉取完成后,该模型会出现在 Lemonade 服务器的已下载模型列表中;下面的检查用于确认该模型已存在于本机上。

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-gpt-oss-20b-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:gpt-oss-20b-mxfp4-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-gpt-oss-20b-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q gpt-oss-20b-mxfp4-GGUF
```
<!-- @test:end -->
<!-- @os:end -->