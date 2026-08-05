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

Το **AMD Sync** μετατρέπει το laptop σας σε απομακρυσμένο πιλοτήριο για τον AMD Ryzen™ AI Halo. Παρακάμψτε τη χειροκίνητη ρύθμιση SSH, κλειδιών και IDE — εγκαταστήστε το AMD Sync και αποκτήστε πρόσβαση με ένα κλικ σε τερματικό, VS Code, JupyterLab και έναν ζωντανό πίνακα ελέγχου GPU/CPU/μνήμης στο Ryzen AI Halo.

Το τοπικό σας μηχάνημα παραμένει οικείο· κάθε εντολή, notebook και μοντέλο εκτελείται στο Ryzen AI Halo.

> **Συμβουλή**: Αυτή η σελίδα θα περιέχει τυχόν νέες ενημερώσεις για το AMDSync. 

## Τι θα Μάθετε

- Να ενεργοποιείτε το SSH στο Ryzen AI Halo και να συνδέεστε σε αυτό από το AMD Sync
- Να εκκινείτε το VS Code, το Terminal, το JupyterLab και τις Ζωντανές Μετρήσεις (Live Metrics) στο Ryzen AI Halo με ένα κλικ
- Να οργανώνετε την απομακρυσμένη εργασία σας χρησιμοποιώντας τους διαχειριζόμενους φακέλους έργων του AMD Sync

---

## Βασικές Έννοιες

Το AMD Sync έχει δύο πλευρές: έναν **client** (το laptop σας, όπου εκτελείται η εφαρμογή AMD Sync) και έναν **server** (το Ryzen AI Halo, όπου εκτελείται ένας διακομιστής SSH στον οποίο το AMD Sync δημιουργεί τούνελ). Οτιδήποτε εκκινείτε από το AMD Sync — VS Code, τερματικό, notebook — ανοίγει τοπικά αλλά εκτελείται στο Ryzen AI Halo.

> **Υποστηριζόμενοι clients:** Windows 11 και Linux. Το macOS δεν υποστηρίζεται.

---

## Βήμα 1 — Ενεργοποίηση SSH στο Ryzen AI Halo


> **Σημείωση:** Στα Windows, το Ryzen AI Halo παραδίδεται με τον διακομιστή SSH *απενεργοποιημένο από προεπιλογή*. Στο Linux, παραδίδεται με τον διακομιστή SSH *ενεργοποιημένο από προεπιλογή*.

1. Στο Ryzen AI Halo, ανοίξτε το **AMD Ryzen™ AI Developer Center**.
2. Μεταβείτε στην καρτέλα **Remote**.
3. Ενεργοποιήστε τον διακόπτη **SSH Server**.
4. Σημειώστε τη **διεύθυνση IP**, τη **θύρα** και το **όνομα χρήστη** που εμφανίζονται κάτω από το **Server Information** — θα τα επικολλήσετε στο AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Σημείωση:** Αυτό είναι το AMD Developer Center για Windows. Αυτό για Linux ενδέχεται να έχει διαφορετικό περιβάλλον χρήστη, αλλά παρόμοια λειτουργικότητα απομακρυσμένης πρόσβασης.

> **Συμβουλή:** Το AMD Sync ζητά τον **κωδικό πρόσβασης σύνδεσης του λειτουργικού συστήματος** αυτού του χρήστη, όχι κωδικό πρόσβασης από το Developer Center.

---

## Βήμα 2 — Εγκατάσταση του AMD Sync στον Client σας

Το AMD Sync εκτελείται σε Windows 11 και Linux. Κατεβάστε το πρόγραμμα εγκατάστασης για το λειτουργικό σας σύστημα και ακολουθήστε τα παρακάτω βήματα. Μετά την εγκατάσταση, κάντε κλικ στο **Accept & Install** στην οθόνη **Get Started** — το AMD Sync εκκινείται αυτόματα μόλις ολοκληρωθεί.

### Windows

[Λήψη AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Κάντε διπλό κλικ στο `AMDSyncInstaller.exe`.
2. Κάντε κλικ στο **Accept & Install**.

> Αν το Windows Firewall σας εμφανίσει προτροπή, επιτρέψτε στο AMD Sync πρόσβαση στο δίκτυο ώστε να μπορεί να προσεγγίσει το Ryzen AI Halo μέσω SSH.

### Linux

Κάντε κλικ στον σύνδεσμο για να κατεβάσετε τη μορφή που προτιμάτε:

| Μορφή | Λήψη | Εντολή εγκατάστασης |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Σημείωση:** Το Ubuntu App Center ενδέχεται να επισημάνει ένα τοπικά ανοιγμένο `.deb` ως *"Potentially unsafe."* Αυτή είναι η τυπική προειδοποίηση για κάθε τοπικό πρόγραμμα εγκατάστασης τρίτου κατασκευαστή. Αν το διπλό κλικ στο `.deb` αποτύχει, χρησιμοποιήστε την παραπάνω εντολή τερματικού.

---

## Βήμα 3 — Σύνδεση στο Ryzen AI Halo σας

Κατά την πρώτη εκκίνηση, το AMD Sync εμφανίζει τη φόρμα **Add a Remote Device**. Συμπληρώστε τη χρησιμοποιώντας τις τιμές από την καρτέλα **Remote** του Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Πεδίο | Σημειώσεις |
|-------|-------|
| **Device Name** *(προαιρετικό)* | Μια φιλική ετικέτα όπως `Ryzen AI Halo`. Η προεπιλογή είναι `Device 1`, `Device 2`, … |
| **Hostname or IP** | Από την καρτέλα Remote |
| **SSH Port** | Από την καρτέλα Remote (μόνο αριθμοί) |
| **Username** | Το όνομα λογαριασμού λειτουργικού συστήματος στο Ryzen AI Halo |
| **Password** | Ο κωδικός πρόσβασης σύνδεσης του λειτουργικού συστήματος — αποκρύπτεται καθώς πληκτρολογείτε |

Κάντε κλικ στο **Add Device**. Μετά από μια σύντομη οθόνη φόρτωσης, θα δείτε **"Connection Successful"** και θα βρεθείτε στην αρχική προβολή, η οποία βρίσκεται στη γραμμή συστήματός σας (system tray). Κάντε κλικ έξω από το παράθυρο για να το κλείσετε· το AMD Sync συνεχίζει να εκτελείται και είναι διαθέσιμο με ένα κλικ.

> **Αν η σύνδεση αποτύχει,** το AMD Sync επιστρέφει στη φόρμα διατηρώντας τις τιμές σας. Οι συνήθεις αιτίες είναι το SSH να είναι απενεργοποιημένο στο Ryzen AI Halo, λανθασμένος κωδικός πρόσβασης ή οι δύο συσκευές να βρίσκονται σε διαφορετικά δίκτυα.

---

## Βήμα 4 — Εκκίνηση του Πρώτου σας Απομακρυσμένου Εργαλείου

Η αρχική προβολή σάς παρέχει πέντε εργαλεία με ένα κλικ — όλα διαθέσιμα ανεξάρτητα από το λειτουργικό σύστημα που εκτελείται στον client και στο Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Στοιχείο | Τι κάνει |
|-----------|--------------|
| **Directory** | Επιλέγει τον φάκελο στο Ryzen AI Halo στον οποίο θα ανοίγουν τα VS Code, Terminal και JupyterLab. Η προεπιλογή είναι ένας διαχειριζόμενος χώρος εργασίας `Documents/AMD_Sync`. |
| **VS Code** | Ανοίγει το VS Code τοπικά με ένα τούνελ SSH προς τον επιλεγμένο φάκελο. |
| **Terminal** | Ανοίγει ένα τοπικό τερματικό συνδεδεμένο μέσω SSH στο Ryzen AI Halo, στον επιλεγμένο φάκελο. |
| **JupyterLab** | Εκκινεί ένα έργο notebook συνδεδεμένο μέσω SSH στο Ryzen AI Halo, εντός του επιλεγμένου φακέλου. |
| **Live Metrics** | Προβολή σε πραγματικό χρόνο της χρήσης GPU, μνήμης και CPU στο Ryzen AI Halo. |

### Δοκιμάστε το VS Code

Για την πρώτη σας εκκίνηση, δοκιμάστε το **VS Code**.

1. Αφήστε το **Directory** στην προεπιλογή `~/Documents/AMD_Sync`.
2. Κάντε κλικ στο **VS Code**.
3. Το AMD Sync δημιουργεί το `Documents/AMD_Sync/Project_1` στο Ryzen AI Halo και ανοίγει το VS Code τοπικά, με τούνελ προς αυτό.

Τώρα επεξεργάζεστε αρχεία που βρίσκονται στο Ryzen AI Halo με το τοπικό σας περιβάλλον VS Code. Δημιουργήστε το `helloworld.py`, προσθέστε `print("hello world")`, ανοίξτε το ενσωματωμένο τερματικό (`` Ctrl + ` ``) και εκτελέστε το:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Η γραμμή κατάστασης δείχνει **SSH: Linux** — απόδειξη ότι ο κώδικάς σας εκτελείται στο Ryzen AI Halo, όχι στο laptop σας.
### Δοκιμάστε το Terminal

Κάντε κλικ στο **Terminal** για να μεταφερθείτε στον ίδιο φάκελο μέσω SSH χωρίς να απομακρυνθείτε από το πληκτρολόγιο.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Στα Windows, το προεπιλεγμένο terminal είναι το **PowerShell** — μεταβείτε στο **Windows Command Prompt** από το μενού Settings αν το προτιμάτε. Στο Linux, το AMD Sync χρησιμοποιεί το προεπιλεγμένο terminal του συστήματός σας.

---

## Πώς λειτουργεί ο Directory

Το αναπτυσσόμενο μενού **Directory** είναι το πιο σημαντικό στοιχείο ελέγχου στο AMD Sync — καθορίζει πού καταλήγει κάθε εργαλείο που εκκινείτε στο Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (προεπιλογή)** — Η εκκίνηση του VS Code ή του JupyterLab από εδώ δημιουργεί αυτόματα έναν νέο φάκελο έργου (`Project_1`, `Project_2`, … για το VS Code· `Notebook_Project_1`, `Notebook_Project_2`, … για το JupyterLab).
- **Υπάρχοντες φάκελοι έργων** — Κάθε άμεσος υποφάκελος του `AMD_Sync` (συμπεριλαμβανομένων φακέλων που δημιουργείτε χειροκίνητα στο Ryzen AI Halo) εμφανίζεται στο αναπτυσσόμενο μενού. Ο τελευταίος φάκελος που χρησιμοποιήσατε γίνεται η προεπιλογή την επόμενη φορά.
- **Προσαρμοσμένες διαδρομές** — Πληκτρολογήστε οποιαδήποτε απόλυτη διαδρομή για να ανοίξετε έναν φάκελο αλλού στο Ryzen AI Halo. Το AMD Sync απλώς τον *ανοίγει* — δεν θα δημιουργήσει φακέλους εκτός του `AMD_Sync`, και οι προσαρμοσμένες διαδρομές δεν αποθηκεύονται μεταξύ των συνεδριών.

Αν μια προσαρμοσμένη διαδρομή δεν λειτουργεί, το AMD Sync σας εξηγεί γιατί: μη έγκυρη σύνταξη, ο φάκελος δεν υπάρχει, ή η διαδρομή δείχνει σε αρχείο.

---

## Live Metrics και JupyterLab

- **Live Metrics** — Ένας ζωντανός πίνακας ελέγχου της χρήσης GPU, μνήμης και CPU. Ο ταχύτερος τρόπος για να επιβεβαιώσετε ότι μια απομακρυσμένη διαδικασία εκπαίδευσης χρησιμοποιεί όντως το υλικό.
- **JupyterLab** — Ένα πλήρες έργο notebook συνδεδεμένο μέσω SSH με το Ryzen AI Halo, με το δικό του ενσωματωμένο terminal για συνδυασμό κελιών notebook και εντολών shell χωρίς να χρειάζεται να φύγετε από το UI.

---

## Settings και Πολλαπλές Συσκευές

Το μενού **Settings** έχει τρεις καρτέλες:

| Καρτέλα | Τι καλύπτει |
|-----|----------------|
| **Devices** | Παραθέτει κάθε Ryzen AI Halo με το οποίο έχετε συνδεθεί επιτυχώς. Επανασυνδεθείτε, επεξεργαστείτε διαπιστευτήρια ή προσθέστε νέα συσκευή. |
| **Information** | Σύνδεσμοι προς την τεκμηρίωση και την υποστήριξη στο forum. |
| **Customize** | Επανατοποθετήστε την εφαρμογή στην επιφάνεια εργασίας σας, αλλάξτε τον τύπο terminal (μόνο Windows) και ελέγξτε για ενημερώσεις του AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Τύπος terminal (Windows)** — Επιλέξτε ανάμεσα σε **PowerShell** (προεπιλογή) και **Windows Command Prompt**.
- **Τύπος terminal (Linux)** — Διατίθεται μόνο το προεπιλεγμένο terminal του συστήματος.
- **Ενημερώσεις εφαρμογής** — Αυτή η καρτέλα είναι το κατάλληλο μέρος για να ελέγξετε και να εγκαταστήσετε νέες εκδόσεις του AMD Sync μέσα από το UI· δεν χρειάζεται ξεχωριστό εργαλείο ενημέρωσης.

> Μια συσκευή εμφανίζεται στο **Devices** μόνο μετά από μια επιτυχημένη πρώτη σύνδεση, ώστε οι αποτυχημένες προσπάθειες να μη γεμίζουν τη λίστα.

---

## Αντιμετώπιση Προβλημάτων

- **Η σύνδεση αποτυγχάνει αμέσως** — Επιβεβαιώστε ότι ο διακομιστής SSH είναι ενεργοποιημένος στην καρτέλα **Remote** του Developer Center στο Ryzen AI Halo.
- **Σφάλμα λανθασμένου κωδικού πρόσβασης** — Χρησιμοποιήστε τον **κωδικό πρόσβασης σύνδεσης του λειτουργικού συστήματος** στο Ryzen AI Halo, όχι κωδικούς πρόσβασης από το Developer Center.
- **Το κουμπί VS Code δεν κάνει τίποτα** — Εγκαταστήστε το VS Code στον υπολογιστή-πελάτη σας από το [code.visualstudio.com](https://code.visualstudio.com).
- **Λείπει το εικονίδιο του AMD Sync στη γραμμή συστήματος (Linux/GNOME)** — Εγκαταστήστε και ενεργοποιήστε την επέκταση AppIndicator.
- **Το `.deb` δεν ανοίγει από τον διαχειριστή αρχείων** — Χρησιμοποιήστε την εντολή `sudo apt install ./AMDSyncInstaller.deb` από ένα terminal.

---