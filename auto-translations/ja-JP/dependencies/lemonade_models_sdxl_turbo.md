<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade 用に SDXL-Turbo をダウンロードする

Lemonade サーバーは SDXL-Turbo モデル(`SDXL-Turbo`)を提供します。事前にダウンロードするには:

```bash
lemonade pull SDXL-Turbo
```

`lemonade run SDXL-Turbo` は、モデルがまだ存在しない場合、初回使用時にもモデルをダウンロードし、その後推論用にロードします。

ダウンロードが完了すると、モデルは Lemonade サーバーのダウンロード済みモデル一覧に表示されます。以下のチェックは、マシン上にモデルが存在することを確認するものです。

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