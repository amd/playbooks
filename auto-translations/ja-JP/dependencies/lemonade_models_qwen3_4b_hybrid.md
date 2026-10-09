<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

Lemonade用のQwen3 4B Hybridのダウンロード

Lemonadeサーバーは、Ryzen AIプロセッサーのNPUおよびGPU上で動作するQwen3 4B Hybridモデル(`Qwen3-4B-Hybrid`)を提供します。事前にダウンロードするには、以下の手順に従ってください。

```powershell
lemonade pull Qwen3-4B-Hybrid
```

プルが完了すると、Lemonadeサーバーのダウンロード済みモデル一覧にモデルが表示されます。以下のチェックにより、マシン上に存在することを確認できます。

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-4b-hybrid-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-4B-Hybrid
```
<!-- @test:end -->
<!-- @os:end -->