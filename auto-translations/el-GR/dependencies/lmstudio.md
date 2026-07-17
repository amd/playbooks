<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
Το LM Studio μπορεί να εγκατασταθεί από το **AMD Ryzen™ AI Developer Center**. Μεταβείτε στην καρτέλα **Updates** και εγκαταστήστε το LM Studio εάν δεν υπάρχει ήδη.

Για να επιτρέψετε στο LM Studio να εντοπίσει τα προεγκατεστημένα μοντέλα, μεταβείτε στις Ρυθμίσεις > General > Models Directory. Στη συνέχεια αλλάξτε τη διαδρομή σε `C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. Κατεβάστε το πρόγραμμα εγκατάστασης από εδώ: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. Εγκαταστήστε.
<!-- @device:end -->

> Συμβουλή: Μετά την εγκατάσταση, εκκινήστε το LM Studio μία φορά για να αρχικοποιήσετε το CLI (`lms`).

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> Σημείωση: Μπορείτε να επιλέξετε να εγκαταστήσετε είτε το .deb είτε το AppImage.
1. Κατεβάστε το appimage από εδώ: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. εκτελέστε `sudo apt install libfuse2`
3. εκτελέστε `cd ~/Downloads`
4. εκτελέστε `chmod +x LM-Studio-*.AppImage`
5. εκτελέστε `./LM-Studio-*.AppImage`
> Συμβουλή: Μετά την εγκατάσταση, εκκινήστε το LM Studio μία φορά για να αρχικοποιήσετε το CLI (`lms`).

<!-- @device:halo_box -->
Για να επιτρέψετε στο LM Studio να εντοπίσει τα προεγκατεστημένα μοντέλα, μεταβείτε στις Ρυθμίσεις > General > Models Directory. Στη συνέχεια αλλάξτε τη διαδρομή σε `/var/cache/models`.

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_linux_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @test:id=lmstudio-cli-linux timeout=60 hidden=True -->
```bash
lms --help
```
<!-- @test:end -->
<!-- @os:end -->