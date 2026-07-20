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

**Εγκαταστήστε το ROCm στο εικονικό περιβάλλον που δημιουργήσατε.**
> **Σημείωση**: Βεβαιωθείτε ότι το εικονικό περιβάλλον είναι ενεργό πριν προχωρήσετε.

<!-- @device:halo,halo_box -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1150/ "rocm[libraries,devel]"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:krk -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1152/ "rocm[libraries,devel]"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx7900xt -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx110X-all/ "rocm[libraries,devel]"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx9070xt,r9700 -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx120X-all/ "rocm[libraries,devel]"
```
<!-- @test:end -->
<!-- @device:end -->

Για περισσότερη βοήθεια σχετικά με την εγκατάσταση, δείτε αυτόν τον [σύνδεσμο](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).