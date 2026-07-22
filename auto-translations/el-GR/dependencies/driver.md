<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### Πρόγραμμα οδήγησης GPU AMD

Ενημερώστε στο πιο πρόσφατο πρόγραμμα οδήγησης GPU AMD χρησιμοποιώντας το [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Ανοίξτε το `AMD Software: Adrenalin Edition` από το μενού Έναρξη ή τη γραμμή συστήματος.
2. Μεταβείτε στο **Driver and Software** και κάντε κλικ στο **Manage Updates**.
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
### Πρόγραμμα οδήγησης GPU AMD

Εγκαταστήστε το πρόγραμμα οδήγησης GPU AMD (amdgpu) χρησιμοποιώντας τη ροή Radeon Software for Linux (RSL). Για οδηγίες σχετικά με τη διανομή σας, δείτε [Εγκατάσταση του προγράμματος οδήγησης πυρήνα](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->