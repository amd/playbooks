<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Για το Ryzen AI Halo, η αποκλειστική μνήμη GPU έχει προεπιλεγμένη τιμή 64GB, η οποία επαρκεί για τα περισσότερα φόρτους εργασίας. Για μεγαλύτερα μοντέλα ή μεγαλύτερα πλαίσια περιεχομένου (contexts), η αύξηση αυτής της τιμής ενδέχεται να βοηθήσει. Για να την προσαρμόσετε, ανοίξτε το **AMD Software: Adrenalin Edition™** και μεταβείτε στο **Performance → Tuning → AMD Variable Graphics Memory**. Κάντε επανεκκίνηση για να τεθούν σε ισχύ οι αλλαγές.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Για να αλλάξετε την τιμή της αποκλειστικής μνήμης GPU, ανοίξτε το **AMD Software: Adrenalin Edition™** και μεταβείτε στο **Performance → Tuning → AMD Variable Graphics Memory**. Κάντε επανεκκίνηση για να τεθούν σε ισχύ οι αλλαγές.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

Σε Linux, για να εκτελέσετε μεγαλύτερα μοντέλα, αυξήστε τη δεξαμενή **κοινόχρηστης μνήμης** (shared memory) που είναι διαθέσιμη στην GPU. Αυτό ενδέχεται να απαιτεί τη ρύθμιση της αποκλειστικής μνήμης GPU στο BIOS στην ελάχιστη τιμή, ώστε να μεγιστοποιηθεί η δεξαμενή κοινόχρηστης μνήμης.

<!-- @device:halo_box -->

Για το AMD Ryzen™ AI Halo, για να τροποποιήσετε την προεπιλεγμένη ρύθμιση, ανοίξτε το **AMD Ryzen™ AI Developer Center** και μεταβείτε στην καρτέλα **Settings**. Στην ενότητα **Graphics Performance Settings**, αυξήστε τον ρυθμιστή **Shared Video Memory**, στη συνέχεια κάντε κλικ στο **Apply Changes** και κάντε επανεκκίνηση για να τεθούν σε ισχύ οι αλλαγές.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Αυξήστε τη δεξαμενή κοινόχρηστης μνήμης αλλάζοντας τη ρύθμιση σελίδας του Translation Table Manager (TTM) του πυρήνα. Η AMD συνιστά να ορίσετε την ελάχιστη αποκλειστική μνήμη VRAM στο BIOS (0.5 GB) ώστε η μέγιστη δυνατή ποσότητα να είναι διαθέσιμη ως κοινόχρηστη μνήμη.

1. Εγκαταστήστε το βοηθητικό πρόγραμμα `pipx` και προσθέστε τη διαδρομή για τα wheels που εγκαθίστανται μέσω pipx στη διαδρομή αναζήτησης του συστήματος:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Εγκαταστήστε το wheel `amd-debug-tools` από το PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Ερωτήστε τις τρέχουσες ρυθμίσεις κοινόχρηστης μνήμης:

   ```bash
   amd-ttm
   ```

4. Αυξήστε την κατανομή κοινόχρηστης μνήμης (μονάδες σε GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Κάντε επανεκκίνηση για να τεθούν σε ισχύ οι αλλαγές.

<!-- @device:end -->

<!-- @os:end -->