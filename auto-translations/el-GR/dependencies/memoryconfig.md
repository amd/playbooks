<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Για το Ryzen AI Halo, η αποκλειστική μνήμη GPU έχει ως προεπιλογή τα 64GB, κάτι που είναι επαρκές για τα περισσότερα φόρτους εργασίας. Για μεγαλύτερα μοντέλα ή μεγαλύτερα contexts, η αύξηση αυτής της τιμής μπορεί να βοηθήσει. Για να την προσαρμόσετε, ανοίξτε το **AMD Software: Adrenalin Edition™** και μεταβείτε στο **Performance → Tuning → AMD Variable Graphics Memory**. Επανεκκινήστε για να εφαρμοστούν οι αλλαγές.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Για να αλλάξετε την τιμή της αποκλειστικής μνήμης GPU, ανοίξτε το **AMD Software: Adrenalin Edition™** και μεταβείτε στο **Performance → Tuning → AMD Variable Graphics Memory**. Επανεκκινήστε για να εφαρμοστούν οι αλλαγές.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

Σε Linux, για να τρέξετε μεγαλύτερα μοντέλα, αυξήστε τη δεξαμενή **shared memory** που είναι διαθέσιμη στη GPU. Αυτό ενδέχεται να απαιτεί τη ρύθμιση της αποκλειστικής μνήμης GPU στο BIOS στο ελάχιστο, ώστε η δεξαμενή shared memory να μπορεί να μεγιστοποιηθεί.

<!-- @device:halo_box -->

Για το AMD Ryzen™ AI Halo, για να τροποποιήσετε την προεπιλεγμένη ρύθμιση, ανοίξτε το **AMD Ryzen™ AI Developer Center** και μεταβείτε στην καρτέλα **Settings**. Κάτω από το **Graphics Performance Settings**, αυξήστε τον ρυθμιστή **Shared Video Memory**, στη συνέχεια κάντε κλικ στο **Apply Changes** και επανεκκινήστε για να εφαρμοστούν οι αλλαγές.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Αυξήστε τη δεξαμενή shared memory αλλάζοντας τη ρύθμιση σελίδας του Translation Table Manager (TTM) του πυρήνα. Η AMD συνιστά τη ρύθμιση της ελάχιστης αποκλειστικής VRAM στο BIOS (0.5 GB) ώστε η μέγιστη δυνατή ποσότητα να είναι διαθέσιμη ως shared memory.

1. Εγκαταστήστε το βοηθητικό πρόγραμμα `pipx` και προσθέστε τη διαδρομή για τα wheels που εγκαθίστανται μέσω pipx στο path αναζήτησης του συστήματος:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Εγκαταστήστε το wheel `amd-debug-tools` από το PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Ερωτήστε τις τρέχουσες ρυθμίσεις shared memory:

   ```bash
   amd-ttm
   ```

4. Αυξήστε την κατανομή shared memory (μονάδες σε GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Επανεκκινήστε για να εφαρμοστούν οι αλλαγές.

<!-- @device:end -->

<!-- @os:end -->