<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU ドライバー

[`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html) を使用して、最新の AMD GPU ドライバーに更新します。

1. スタートメニューまたはシステムトレイから `AMD Software: Adrenalin Edition` を開きます。
2. **Driver and Software** に移動し、**Manage Updates** をクリックします。
3. アップデートが利用可能な場合は、画面の指示に従ってダウンロードおよびインストールします。

<!-- @test:id=amd-gpu-visible-windows timeout=60 hidden=True -->
```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
### AMD GPU ドライバー

Radeon Software for Linux (RSL) フローを使用して AMD GPU ドライバー (amdgpu) をインストールします。お使いのディストリビューション向けの手順については、[Install the kernel driver](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html) を参照してください。

<!-- @device:end -->
<!-- @os:end -->