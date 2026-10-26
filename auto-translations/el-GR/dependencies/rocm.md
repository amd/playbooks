<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

#### ROCm

**Προσθέστε τον τρέχοντα χρήστη στις ομάδες render και video.** 
```bash
sudo usermod -a -G render,video $LOGNAME
```

**Επανεκκινήστε το σύστημά σας για να εφαρμοστούν οι ρυθμίσεις.**
```bash
sudo reboot
```

**Εγκαταστήστε το ROCm στο εικονικό περιβάλλον που δημιουργήθηκε.**
> **Σημείωση**: Βεβαιωθείτε ότι το εικονικό περιβάλλον είναι ενεργό πριν προχωρήσετε.

<!-- @device:halo_box,halo -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://stable.repo.amd.com/rocm/whl-next/ "rocm[libraries,devel,device-gfx1151]==10.0.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://stable.repo.amd.com/rocm/whl-next/ "rocm[libraries,devel,device-gfx1150]==10.0.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:krk -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://stable.repo.amd.com/rocm/whl-next/ "rocm[libraries,devel,device-gfx1152]==10.0.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx7900xt -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://stable.repo.amd.com/rocm/whl-next/ "rocm[libraries,devel,device-gfx1100]==10.0.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx9070xt,r9700 -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://stable.repo.amd.com/rocm/whl-next/ "rocm[libraries,devel,device-gfx1201]==10.0.0"
```
<!-- @test:end -->
<!-- @device:end -->

Για περαιτέρω βοήθεια εγκατάστασης, ανατρέξτε στην [Τεκμηρίωση ROCm 10.0.0](https://rocm.docs.amd.com/en/latest/install/rocm.html).