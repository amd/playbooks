<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Μηχανική μετάφραση.** Αυτή η σελίδα μεταφράστηκε αυτόματα από τα Αγγλικά και δεν έχει ελεγχθεί από άνθρωπο. Ενδέχεται να περιέχει σφάλματα, και ορισμένες οδηγίες, εντολές, στοιχεία λήψης, διαθεσιμότητα προϊόντων ή άλλο περιεχόμενο ενδέχεται να διαφέρουν ανάλογα με τη γλώσσα ή την περιοχή. Σε περίπτωση οποιασδήποτε ασυμφωνίας ή απόκλισης, υπερισχύει η πρωτότυπη αγγλική έκδοση του playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Απομακρυσμένη Ανάπτυξη με το AMD Sync

## Επισκόπηση

Το **AMD Sync** μετατρέπει το laptop σας σε ένα απομακρυσμένο κέντρο ελέγχου για το AMD Ryzen™ AI Halo. Παρακάμψτε τη χειροκίνητη ρύθμιση SSH, κλειδιών και IDE — εγκαταστήστε το AMD Sync και αποκτήστε πρόσβαση με ένα κλικ σε απομακρυσμένο τερματικό, VS Code, JupyterLab, και έναν πίνακα ελέγχου GPU/CPU/μνήμης σε πραγματικό χρόνο στο Ryzen AI Halo.

Το τοπικό σας μηχάνημα παραμένει οικείο· κάθε εντολή, notebook, και μοντέλο εκτελείται στο Ryzen AI Halo.

> **Συμβουλή**: Αυτή η σελίδα θα περιέχει τυχόν νέες ενημερώσεις για το AMDSync.

## Τι Θα Μάθετε

- Να ενεργοποιείτε το SSH στο Ryzen AI Halo και να συνδέεστε σε αυτό από το AMD Sync
- Να εκκινείτε το VS Code, το Terminal, το JupyterLab, και το Live Metrics έναντι του Ryzen AI Halo με ένα κλικ
- Να οργανώνετε την απομακρυσμένη εργασία χρησιμοποιώντας τους διαχειριζόμενους φακέλους έργων του AMD Sync

---

## Βασικές Έννοιες

Το AMD Sync έχει δύο πλευρές: έναν **client** (το laptop σας, που εκτελεί την εφαρμογή AMD Sync) και έναν **server** (το Ryzen AI Halo, που εκτελεί έναν διακομιστή SSH στον οποίο συνδέεται το AMD Sync μέσω tunnel). Οτιδήποτε εκκινείτε από το AMD Sync — VS Code, ένα τερματικό, ένα notebook — ανοίγει τοπικά αλλά εκτελείται στο Ryzen AI Halo.

> **Υποστηριζόμενοι clients:** Windows 11 και Linux. Το macOS δεν υποστηρίζεται.

---

## Βήμα 1 — Ενεργοποίηση SSH στο Ryzen AI Halo


> **Σημείωση:** Στα Windows, το Ryzen AI Halo παραδίδεται με τον διακομιστή SSH *απενεργοποιημένο από προεπιλογή*. Στο Linux, έρχεται με τον διακομιστή SSH *ενεργοποιημένο από προεπιλογή*.

1. Στο Ryzen AI Halo, ανοίξτε το **AMD Ryzen™ AI Developer Center**.
2. Μεταβείτε στην καρτέλα **Remote**.
3. Ενεργοποιήστε το **SSH Server**.
4. Σημειώστε το **IP Address**, τη **Port**, και το **Username** που εμφανίζονται κάτω από **Server Information** — θα τα επικολλήσετε στο AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Σημείωση:** Αυτό είναι το AMD Developer Center για Windows. Το αντίστοιχο για Linux μπορεί να έχει διαφορετικό UI, αλλά παρόμοια λειτουργικότητα απομακρυσμένης πρόσβασης.

> **Συμβουλή:** Το AMD Sync ζητά τον **κωδικό πρόσβασης σύνδεσης λειτουργικού συστήματος** αυτού του χρήστη, όχι έναν κωδικό πρόσβασης από το Developer Center.

---

## Βήμα 2 — Εγκατάσταση του AMD Sync στον Client σας

Το AMD Sync εκτελείται σε Windows 11 και Linux. Κατεβάστε το πρόγραμμα εγκατάστασης για το λειτουργικό σας σύστημα και ακολουθήστε τα παρακάτω βήματα. Μετά την εγκατάσταση, κάντε κλικ στο **Accept & Install** στην οθόνη **Get Started** — το AMD Sync εκκινείται αυτόματα όταν ολοκληρωθεί.

### Windows

[Λήψη AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Κάντε διπλό κλικ στο `AMDSyncInstaller.exe`.
2. Κάντε κλικ στο **Accept & Install**.

> Αν τα Windows Firewall σας ζητήσουν επιβεβαίωση, επιτρέψτε στο AMD Sync πρόσβαση στο δίκτυο ώστε να μπορεί να επικοινωνήσει με το Ryzen AI Halo μέσω SSH.

### Linux

Κάντε κλικ στον σύνδεσμο για να κατεβάσετε τη μορφή που προτιμάτε:

| Μορφή | Λήψη | Εντολή εγκατάστασης |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Σημείωση:** Το Ubuntu App Center ενδέχεται να επισημάνει ένα τοπικά ανοιγμένο `.deb` ως *«Πιθανώς μη ασφαλές»*. Αυτή είναι η τυπική προειδοποίηση για οποιοδήποτε τοπικό πρόγραμμα εγκατάστασης τρίτου μέρους. Αν το διπλό κλικ στο `.deb` αποτύχει, χρησιμοποιήστε την παραπάνω εντολή τερματικού.

---

## Βήμα 3 — Σύνδεση με το Ryzen AI Halo σας

Κατά την πρώτη εκκίνηση, το AMD Sync εμφανίζει τη φόρμα **Add a Remote Device**. Συμπληρώστε την χρησιμοποιώντας τις τιμές από την καρτέλα **Remote** του Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Πεδίο | Σημειώσεις |
|-------|-------|
| **Device Name** *(προαιρετικό)* | Μια φιλική ετικέτα όπως `Ryzen AI Halo`. Προεπιλογή είναι `Device 1`, `Device 2`, … |
| **Hostname or IP** | Από την καρτέλα Remote |
| **SSH Port** | Από την καρτέλα Remote (μόνο αριθμοί) |
| **Username** | Το όνομα λογαριασμού λειτουργικού συστήματος στο Ryzen AI Halo |
| **Password** | Ο κωδικός πρόσβασης σύνδεσης λειτουργικού συστήματος — κρυμμένος καθώς πληκτρολογείτε |

Κάντε κλικ στο **Add Device**. Μετά από μια σύντομη οθόνη φόρτωσης, θα δείτε **"Connection Successful"** και θα μεταφερθείτε στην κεντρική προβολή, η οποία βρίσκεται στην περιοχή ειδοποιήσεων του συστήματός σας. Κάντε κλικ έξω από το παράθυρο για να το κλείσετε· το AMD Sync συνεχίζει να εκτελείται και είναι διαθέσιμο με ένα κλικ.

> **Αν η σύνδεση αποτύχει,** το AMD Sync επιστρέφει στη φόρμα με τις τιμές σας διατηρημένες. Οι συνήθεις αιτίες είναι το SSH να είναι απενεργοποιημένο στο Ryzen AI Halo, λανθασμένος κωδικός πρόσβασης, ή οι δύο συσκευές να βρίσκονται σε διαφορετικά δίκτυα.

---

## Βήμα 4 — Εκκίνηση του Πρώτου Απομακρυσμένου Εργαλείου σας

Η κεντρική προβολή σας παρέχει πέντε στοιχεία με ένα κλικ — όλα διαθέσιμα ανεξάρτητα από το λειτουργικό σύστημα που εκτελούν ο client και το Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Στοιχείο | Τι κάνει |
|-----------|--------------|
| **Directory** | Επιλέγει τον φάκελο στο Ryzen AI Halo στον οποίο θα ανοίξουν το VS Code, το Terminal, και το JupyterLab. Προεπιλογή είναι ένας διαχειριζόμενος χώρος εργασίας `Documents/AMD_Sync`. |
| **VS Code** | Ανοίγει το VS Code τοπικά με ένα SSH tunnel στον επιλεγμένο φάκελο. |
| **Terminal** | Ανοίγει ένα τοπικό τερματικό συνδεδεμένο μέσω SSH με το Ryzen AI Halo, στον επιλεγμένο φάκελο. |
| **JupyterLab** | Εκκινεί ένα έργο notebook συνδεδεμένο μέσω SSH με το Ryzen AI Halo, περιορισμένο στον επιλεγμένο φάκελο. |
| **Live Metrics** | Προβολή σε πραγματικό χρόνο της χρήσης GPU, μνήμης, και CPU στο Ryzen AI Halo. |

### Δοκιμάστε το VS Code

Για την πρώτη σας εκκίνηση, δοκιμάστε το **VS Code**.

1. Αφήστε το **Directory** στην προεπιλογή `~/Documents/AMD_Sync`.
2. Κάντε κλικ στο **VS Code**.
3. Το AMD Sync δημιουργεί το `Documents/AMD_Sync/Project_1` στο Ryzen AI Halo και ανοίγει το VS Code τοπικά, συνδεδεμένο μέσω tunnel σε αυτό.

Τώρα επεξεργάζεστε αρχεία που βρίσκονται στο Ryzen AI Halo με τη δική σας τοπική ρύθμιση VS Code. Δημιουργήστε το `helloworld.py`, προσθέστε `print("hello world")`, ανοίξτε το ενσωματωμένο τερματικό (`` Ctrl + ` ``), και εκτελέστε το:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Η γραμμή κατάστασης εμφανίζει **SSH: Linux** — απόδειξη ότι ο κώδικάς σας εκτελείται στο Ryzen AI Halo, όχι στο laptop σας.
### Δοκιμάστε το Terminal

Κάντε κλικ στο **Terminal** για να μεταβείτε στον ίδιο φάκελο μέσω SSH χωρίς να αφήσετε το πληκτρολόγιο.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Στα Windows, το προεπιλεγμένο τερματικό είναι το **PowerShell** — μεταβείτε στο **Windows Command Prompt** από το μενού Ρυθμίσεων αν προτιμάτε. Στο Linux, το AMD Sync χρησιμοποιεί το προεπιλεγμένο τερματικό του συστήματός σας.

---

## Πώς Λειτουργεί ο Κατάλογος

Το αναπτυσσόμενο μενού **Directory** είναι το πιο σημαντικό στοιχείο ελέγχου στο AMD Sync — καθορίζει πού καταλήγει κάθε εργαλείο που εκκινείτε στο Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (προεπιλογή)** — Η εκκίνηση του VS Code ή του JupyterLab από εδώ δημιουργεί αυτόματα έναν νέο φάκελο έργου (`Project_1`, `Project_2`, … για το VS Code· `Notebook_Project_1`, `Notebook_Project_2`, … για το JupyterLab).
- **Υπάρχοντες φάκελοι έργων** — Κάθε άμεσος υποφάκελος του `AMD_Sync` (συμπεριλαμβανομένων φακέλων που δημιουργείτε χειροκίνητα στο Ryzen AI Halo) εμφανίζεται στο αναπτυσσόμενο μενού. Ο τελευταίος φάκελος που χρησιμοποιήσατε γίνεται η προεπιλογή την επόμενη φορά.
- **Προσαρμοσμένες διαδρομές** — Πληκτρολογήστε οποιαδήποτε απόλυτη διαδρομή για να ανοίξετε έναν φάκελο αλλού στο Ryzen AI Halo. Το AMD Sync απλώς *ανοίγει* αυτόν τον φάκελο — δεν θα δημιουργήσει φακέλους εκτός του `AMD_Sync`, και οι προσαρμοσμένες διαδρομές δεν αποθηκεύονται μεταξύ των συνεδριών.

Εάν μια προσαρμοσμένη διαδρομή δεν λειτουργεί, το AMD Sync σάς εξηγεί γιατί: μη έγκυρη σύνταξη, ο φάκελος δεν υπάρχει, ή η διαδρομή οδηγεί σε αρχείο.

---

## Live Metrics και JupyterLab

- **Live Metrics** — Ένας ζωντανός πίνακας ελέγχου για τη χρήση GPU, μνήμης και CPU. Ο ταχύτερος τρόπος για να επιβεβαιώσετε ότι μια απομακρυσμένη εκτέλεση εκπαίδευσης χρησιμοποιεί πράγματι το υλικό.
- **JupyterLab** — Ένα πλήρες έργο notebook συνδεδεμένο μέσω SSH στο Ryzen AI Halo, με το δικό του ενσωματωμένο τερματικό για συνδυασμό κελιών notebook και εντολών shell χωρίς να αφήσετε το περιβάλλον χρήσης.

---

## Ρυθμίσεις και Πολλαπλές Συσκευές

Το μενού **Settings** διαθέτει τρεις καρτέλες:

| Καρτέλα | Τι καλύπτει |
|-----|----------------|
| **Devices** | Παραθέτει κάθε Ryzen AI Halo με το οποίο έχετε συνδεθεί επιτυχώς. Επανασύνδεση, επεξεργασία διαπιστευτηρίων, ή προσθήκη νέας συσκευής. |
| **Information** | Σύνδεσμοι προς την τεκμηρίωση και την υποστήριξη φόρουμ. |
| **Customize** | Επανατοποθέτηση της εφαρμογής στην επιφάνεια εργασίας σας, αλλαγή τύπου τερματικού (μόνο για Windows), και έλεγχος για ενημερώσεις του AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Τύπος τερματικού (Windows)** — Επιλέξτε μεταξύ **PowerShell** (προεπιλογή) και **Windows Command Prompt**.
- **Τύπος τερματικού (Linux)** — Διατίθεται μόνο το προεπιλεγμένο τερματικό συστήματος.
- **Ενημερώσεις εφαρμογής** — Αυτή η καρτέλα είναι το κατάλληλο σημείο για να ελέγξετε και να εγκαταστήσετε νέες εκδόσεις του AMD Sync μέσα από το περιβάλλον χρήσης· δεν χρειάζεται ξεχωριστό πρόγραμμα ενημέρωσης.

> Μια συσκευή εμφανίζεται στην καρτέλα **Devices** μόνο μετά από μια επιτυχημένη πρώτη σύνδεση, ώστε οι αποτυχημένες προσπάθειες να μη γεμίζουν τη λίστα.

---

## Αντιμετώπιση Προβλημάτων

- **Η σύνδεση αποτυγχάνει αμέσως** — Επιβεβαιώστε ότι ο διακομιστής SSH είναι ενεργοποιημένος στην καρτέλα **Remote** του Ryzen AI Halo στο Developer Center.
- **Σφάλμα λανθασμένου κωδικού πρόσβασης** — Χρησιμοποιήστε τον **κωδικό πρόσβασης σύνδεσης του λειτουργικού συστήματος** στο Ryzen AI Halo, όχι κωδικούς πρόσβασης από το Developer Center.
- **Το κουμπί VS Code δεν κάνει τίποτα** — Εγκαταστήστε το VS Code στην πελατειακή σας συσκευή από το [code.visualstudio.com](https://code.visualstudio.com).
- **Λείπει το εικονίδιο του AMD Sync στη γραμμή εργασιών (Linux/GNOME)** — Εγκαταστήστε και ενεργοποιήστε την επέκταση AppIndicator.
- **Το `.deb` δεν ανοίγει από τον διαχειριστή αρχείων** — Χρησιμοποιήστε `sudo apt install ./AMDSyncInstaller.deb` από ένα τερματικό.
- **Η ρύθμιση εμφανίζεται ξανά σε κάθε εκκίνηση (Linux)**: ξεκλειδώστε την κλειδοθήκη σύνδεσής σας, ή εκκινήστε με `--password-store=gnome-libsecret`, και επαναλάβετε τη ρύθμιση μία φορά.

---