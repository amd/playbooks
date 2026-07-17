<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Για το Ryzen AI Halo, η αποκλειστική μνήμη GPU έχει προεπιλογή 64GB, η οποία είναι επαρκής για τα περισσότερα φορτία εργασίας. Για μεγαλύτερα μοντέλα ή μεγαλύτερα πλαίσια, η αύξησή της στα 96GB μπορεί να βοηθήσει. Για να το ρυθμίσετε, ανοίξτε το **AMD Software: Adrenalin Edition™** και μεταβείτε στο **Performance → Tuning → AMD Variable Graphics Memory**. Επανεκκινήστε για να τεθούν σε ισχύ οι αλλαγές.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Για να αλλάξετε την τιμή της αποκλειστικής μνήμης GPU, ανοίξτε το **AMD Software: Adrenalin Edition™** και μεταβείτε στο **Performance → Tuning → AMD Variable Graphics Memory**. Επανεκκινήστε για να τεθούν σε ισχύ οι αλλαγές.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

Στο Linux, για να εκτελέσετε μεγαλύτερα μοντέλα, αυξήστε τη δεξαμενή **κοινόχρηστης μνήμης** που είναι διαθέσιμη στο GPU. Αυτό μπορεί να απαιτεί τη ρύθμιση της αποκλειστικής μνήμης GPU στο BIOS στο ελάχιστο, ώστε η δεξαμενή κοινόχρηστης μνήμης να μεγιστοποιηθεί.

<!-- @device:halo_box -->

Για το AMD Ryzen™ AI Halo, η προεπιλογή είναι 96GB κοινόχρηστη. Για να το τροποποιήσετε, ανοίξτε το **AMD Ryzen™ AI Developer Center** και μεταβείτε στην καρτέλα **Settings**. Στην ενότητα **Graphics Performance Settings**, αυξήστε το ρυθμιστικό **Shared Video Memory**, στη συνέχεια κάντε κλικ στο **Apply Changes** και επανεκκινήστε για να τεθούν σε ισχύ οι αλλαγές.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Αυξήστε τη δεξαμενή κοινόχρηστης μνήμης αλλάζοντας τη ρύθμιση σελίδας Translation Table Manager (TTM) του πυρήνα. Η AMD συνιστά να ορίσετε την ελάχιστη αποκλειστική VRAM στο BIOS (0,5 GB) ώστε η μέγιστη ποσότητα να είναι διαθέσιμη ως κοινόχρηστη μνήμη.

1. Εγκαταστήστε το βοηθητικό πρόγραμμα `pipx` και προσθέστε τη διαδρομή για τα wheels που εγκαθίστανται μέσω pipx στη διαδρομή αναζήτησης του συστήματος:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Εγκαταστήστε το wheel `amd-debug-tools` από το PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Ελέγξτε τις τρέχουσες ρυθμίσεις κοινόχρηστης μνήμης:

   ```bash
   amd-ttm
   ```

4. Αυξήστε την κατανομή κοινόχρηστης μνήμης (μονάδες σε GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Επανεκκινήστε για να τεθούν σε ισχύ οι αλλαγές.

<!-- @device:end -->

<!-- @os:end -->