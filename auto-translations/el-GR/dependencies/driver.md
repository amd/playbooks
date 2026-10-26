<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### Πρόγραμμα οδήγησης AMD GPU

Ενημερώστε στο πιο πρόσφατο πρόγραμμα οδήγησης AMD GPU χρησιμοποιώντας το [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Ανοίξτε το `AMD Software: Adrenalin Edition` από το μενού Έναρξη ή τη γραμμή συστήματος.
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
### Πρόγραμμα οδήγησης AMD GPU

Εγκαταστήστε το πρόγραμμα οδήγησης AMD GPU (amdgpu) χρησιμοποιώντας τη ροή Radeon Software for Linux (RSL). Για οδηγίες σχετικά με τη διανομή σας, δείτε την εγκατάσταση του ROCm στο: [Install the kernel driver](https://rocm.docs.amd.com/en/latest/install/rocm.html?fam=radeon&w=graphics&os=ubuntu&ubuntu-ver=26.04&i=amdgpu-install).

Για το ίδιο το πρόγραμμα οδήγησης, δείτε [Linux® Drivers for AMD Radeon™](https://www.amd.com/en/support/download/linux-drivers.html)

<!-- @device:end -->
<!-- @os:end -->