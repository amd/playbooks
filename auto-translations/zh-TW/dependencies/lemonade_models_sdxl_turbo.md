<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 為 Lemonade 下載 SDXL-Turbo

Lemonade 伺服器會提供 SDXL-Turbo 模型（`SDXL-Turbo`）。若要事先下載：

```bash
lemonade pull SDXL-Turbo
```

`lemonade run SDXL-Turbo` 也會在首次使用時下載該模型（如果尚未存在的話），然後將其載入以進行推論。

一旦下載完成，該模型就會出現在 Lemonade 伺服器已下載模型清單中；以下檢查可確認其已存在於該機器上。

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