<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU Driver

Ενημερώστε στον πιο πρόσφατο οδηγό AMD GPU χρησιμοποιώντας το [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Ανοίξτε το `AMD Software: Adrenalin Edition` από το μενού Έναρξης ή την περιοχή ειδοποιήσεων.
2. Μεταβείτε στο **Driver and Software**, κάντε κλικ στο **Manage Updates**.
3. Εάν υπάρχει διαθέσιμη ενημέρωση, ακολουθήστε τις οδηγίες για λήψη και εγκατάσταση.

<!-- @test:id=amd-gpu-visible-windows timeout=60 hidden=True -->
```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
### AMD GPU Driver

Εγκαταστήστε τον οδηγό AMD GPU (amdgpu) χρησιμοποιώντας τη ροή Radeon Software for Linux (RSL). Για οδηγίες σχετικά με τη διανομή σας, ανατρέξτε στο [Εγκατάσταση του οδηγού πυρήνα](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->