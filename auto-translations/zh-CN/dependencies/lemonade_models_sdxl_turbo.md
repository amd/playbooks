<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 为 Lemonade 下载 SDXL-Turbo

Lemonade 服务器提供 SDXL-Turbo 模型（`SDXL-Turbo`）。要提前下载它：

```bash
lemonade pull SDXL-Turbo
```

`lemonade run SDXL-Turbo` 在首次使用时也会下载该模型（如果尚未存在），然后将其加载以进行推理。

拉取完成后，该模型会出现在 Lemonade 服务器的已下载模型列表中；以下检查可确认它已存在于本机上。

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-sdxl-turbo-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:SDXL-Turbo
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-sdxl-turbo-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q SDXL-Turbo
```
<!-- @test:end -->
<!-- @os:end -->