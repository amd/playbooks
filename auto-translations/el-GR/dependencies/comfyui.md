<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. Κατεβάστε το πιο πρόσφατο πρόγραμμα εγκατάστασης ComfyUI για Windows από το [download.comfy.org](https://download.comfy.org/windows/nsis/x64).
2. Επιλέξτε τη ρύθμιση υλικού σας: Επιλέξτε `AMD ROCm`.
3. Επιλέξτε πού θα εγκαταστήσετε το ComfyUI: Χρησιμοποιήστε την προεπιλεγμένη διαδρομή ή τον φάκελο της προτίμησής σας.
4. Ρυθμίσεις εφαρμογής επιφάνειας εργασίας: Συνιστούμε να αποεπιλέξετε τις "Αυτόματες Ενημερώσεις" για να διασφαλίσετε ότι χρησιμοποιείτε την προτεινόμενη έκδοση αυτής της εφαρμογής.
5. Πατήστε "Next" για να ξεκινήσει η εγκατάσταση.

<!-- @os:end -->

<!-- @os:linux -->
#### Κλωνοποίηση του ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (Προαιρετικό) Μεταβείτε σε μια συγκεκριμένη έκδοση
```bash
git checkout v0.19.2
```

#### Εγκατάσταση απαιτήσεων ComfyUI

Με το εικονικό περιβάλλον Python ενεργοποιημένο, εκτελέστε:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **Σημείωση**: Ανατρέξτε στο [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI) για περισσότερες πληροφορίες.

<!-- @os:end -->