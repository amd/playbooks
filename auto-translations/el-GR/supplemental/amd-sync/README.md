<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Απομακρυσμένη Ανάπτυξη με AMD Sync

## Επισκόπηση

Το **AMD Sync** μετατρέπει το laptop σας σε απομακρυσμένο πίνακα ελέγχου για το AMD Ryzen™ AI Halo. Παρακάμψτε τη χειροκίνητη ρύθμιση SSH, κλειδιών και IDE — εγκαταστήστε το AMD Sync και αποκτήστε πρόσβαση με ένα κλικ σε απομακρυσμένο τερματικό, VS Code, JupyterLab και ένα ζωντανό dashboard GPU/CPU/μνήμης στο Ryzen AI Halo.

Το τοπικό σας μηχάνημα παραμένει οικείο· κάθε εντολή, notebook και μοντέλο εκτελείται στο Ryzen AI Halo.

> **Συμβουλή**: Αυτή η σελίδα θα περιέχει τυχόν νέες ενημερώσεις για το AMDSync.

## Τι Θα Μάθετε

- Ενεργοποίηση SSH στο Ryzen AI Halo και σύνδεση σε αυτό από το AMD Sync
- Εκκίνηση VS Code, Terminal, JupyterLab και Live Metrics για το Ryzen AI Halo με ένα κλικ
- Οργάνωση απομακρυσμένης εργασίας χρησιμοποιώντας τους διαχειριζόμενους φακέλους έργων του AMD Sync

---

## Βασικές Έννοιες

Το AMD Sync έχει δύο πλευρές: έναν **client** (το laptop σας, που εκτελεί την εφαρμογή AMD Sync) και έναν **server** (το Ryzen AI Halo, που εκτελεί έναν SSH server στον οποίο το AMD Sync δημιουργεί tunnel). Ό,τι εκκινείτε από το AMD Sync — VS Code, ένα τερματικό, ένα notebook — ανοίγει τοπικά αλλά εκτελείται στο Ryzen AI Halo.

> **Υποστηριζόμενοι clients:** Windows 11 και Linux. Το macOS δεν υποστηρίζεται.

---

## Βήμα 1 — Ενεργοποίηση SSH στο Ryzen AI Halo


> **Σημείωση:** Στα Windows, το Ryzen AI Halo αποστέλλεται με τον SSH server *απενεργοποιημένο από προεπιλογή*. Στο Linux, αποστέλλεται με τον SSH server *ενεργοποιημένο από προεπιλογή*.

1. Στο Ryzen AI Halo, ανοίξτε το **AMD Ryzen™ AI Developer Center**.
2. Μεταβείτε στην καρτέλα **Remote**.
3. Ενεργοποιήστε τον **SSH Server**.
4. Σημειώστε τη **Διεύθυνση IP**, την **Πόρτα** και το **Όνομα Χρήστη** που εμφανίζονται στο **Server Information** — θα τα επικολλήσετε στο AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Σημείωση:** Αυτό είναι το AMD Developer Center για Windows. Το Linux ενδέχεται να έχει διαφορετικό UI, αλλά παρόμοια απομακρυσμένη λειτουργικότητα.

> **Συμβουλή:** Το AMD Sync ζητά τον **κωδικό πρόσβασης σύνδεσης OS** αυτού του χρήστη, όχι κωδικό από το Developer Center.

---

## Βήμα 2 — Εγκατάσταση AMD Sync στον Client σας

Το AMD Sync εκτελείται σε Windows 11 και Linux. Κατεβάστε το πρόγραμμα εγκατάστασης για το λειτουργικό σας σύστημα και ακολουθήστε τα παρακάτω βήματα. Μετά την εγκατάσταση, κάντε κλικ στο **Accept & Install** στην οθόνη **Get Started** — το AMD Sync εκκινείται αυτόματα όταν ολοκληρωθεί.

### Windows

[Λήψη AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Κάντε διπλό κλικ στο `AMDSyncInstaller.exe`.
2. Κάντε κλικ στο **Accept & Install**.

> Εάν το Windows Firewall σας ζητήσει επιβεβαίωση, επιτρέψτε στο AMD Sync πρόσβαση στο δίκτυο ώστε να μπορεί να επικοινωνεί με το Ryzen AI Halo μέσω SSH.

### Linux

Κάντε κλικ στον σύνδεσμο για να κατεβάσετε την προτιμώμενη μορφή:

| Μορφή | Λήψη | Εντολή εγκατάστασης |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Σημείωση:** Το Ubuntu App Center ενδέχεται να επισημάνει ένα τοπικά ανοιγμένο `.deb` ως *"Potentially unsafe."* Αυτή είναι η τυπική προειδοποίηση για οποιοδήποτε τοπικό πρόγραμμα εγκατάστασης τρίτου κατασκευαστή. Εάν το διπλό κλικ στο `.deb` αποτύχει, χρησιμοποιήστε την παραπάνω εντολή τερματικού.

---

## Βήμα 3 — Σύνδεση στο Ryzen AI Halo σας

Κατά την πρώτη εκκίνηση, το AMD Sync εμφανίζει τη φόρμα **Add a Remote Device**. Συμπληρώστε την χρησιμοποιώντας τις τιμές από την καρτέλα **Remote** του Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Πεδίο | Σημειώσεις |
|-------|-------|
| **Device Name** *(προαιρετικό)* | Μια φιλική ετικέτα όπως `Ryzen AI Halo`. Προεπιλογή: `Device 1`, `Device 2`, … |
| **Hostname or IP** | Από την καρτέλα Remote |
| **SSH Port** | Από την καρτέλα Remote (μόνο αριθμοί) |
| **Username** | Το όνομα λογαριασμού OS σας στο Ryzen AI Halo |
| **Password** | Ο κωδικός πρόσβασης σύνδεσης OS σας — αποκρύπτεται κατά την πληκτρολόγηση |

Κάντε κλικ στο **Add Device**. Μετά από μια σύντομη οθόνη φόρτωσης, θα δείτε **"Connection Successful"** και θα μεταφερθείτε στην αρχική προβολή, η οποία βρίσκεται στο system tray σας. Κάντε κλικ εκτός του παραθύρου για να το κλείσετε· το AMD Sync παραμένει σε λειτουργία και είναι ένα κλικ μακριά.

> **Εάν η σύνδεση αποτύχει,** το AMD Sync επιστρέφει στη φόρμα με τις τιμές σας διατηρημένες. Οι συνήθεις αιτίες είναι η απενεργοποίηση SSH στο Ryzen AI Halo, ο λανθασμένος κωδικός πρόσβασης ή το ότι οι δύο συσκευές βρίσκονται σε διαφορετικά δίκτυα.

---

## Βήμα 4 — Εκκίνηση του Πρώτου Απομακρυσμένου Εργαλείου σας

Η αρχική προβολή σας παρέχει πέντε στοιχεία με ένα κλικ — όλα διαθέσιμα ανεξάρτητα από το λειτουργικό σύστημα που εκτελούν ο client και το Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Στοιχείο | Τι κάνει |
|-----------|--------------|
| **Directory** | Επιλέγει τον φάκελο στο Ryzen AI Halo στον οποίο θα ανοίξουν το VS Code, το Terminal και το JupyterLab. Προεπιλογή: διαχειριζόμενος χώρος εργασίας `Documents/AMD_Sync`. |
| **VS Code** | Ανοίγει το VS Code τοπικά με SSH tunnel στον επιλεγμένο φάκελο. |
| **Terminal** | Ανοίγει ένα τοπικό τερματικό συνδεδεμένο μέσω SSH στο Ryzen AI Halo, στον επιλεγμένο φάκελο. |
| **JupyterLab** | Εκκινεί ένα έργο notebook συνδεδεμένο μέσω SSH στο Ryzen AI Halo, εντός του επιλεγμένου φακέλου. |
| **Live Metrics** | Προβολή σε πραγματικό χρόνο της χρήσης GPU, μνήμης και CPU στο Ryzen AI Halo. |

### Δοκιμάστε το VS Code

Για την πρώτη σας εκκίνηση, δοκιμάστε το **VS Code**.

1. Αφήστε το **Directory** στο προεπιλεγμένο `~/Documents/AMD_Sync`.
2. Κάντε κλικ στο **VS Code**.
3. Το AMD Sync δημιουργεί το `Documents/AMD_Sync/Project_1` στο Ryzen AI Halo και ανοίγει το VS Code τοπικά, με tunnel σε αυτό.

Τώρα επεξεργάζεστε αρχεία που βρίσκονται στο Ryzen AI Halo με την τοπική σας ρύθμιση VS Code. Δημιουργήστε το `helloworld.py`, προσθέστε `print("hello world")`, ανοίξτε το ενσωματωμένο τερματικό (`` Ctrl + ` ``), και εκτελέστε το:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Η γραμμή κατάστασης εμφανίζει **SSH: Linux** — απόδειξη ότι ο κώδικάς σας εκτελείται στο Ryzen AI Halo, όχι στο laptop σας.

### Δοκιμάστε το Terminal

Κάντε κλικ στο **Terminal** για να μεταβείτε στον ίδιο φάκελο μέσω SSH χωρίς να αφήσετε το πληκτρολόγιο.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Στα Windows, το προεπιλεγμένο τερματικό είναι **PowerShell** — μεταβείτε στο **Windows Command Prompt** από το μενού Ρυθμίσεων εάν το προτιμάτε. Στο Linux, το AMD Sync χρησιμοποιεί το προεπιλεγμένο τερματικό του συστήματός σας.

---

## Πώς Λειτουργεί ο Directory

Το αναπτυσσόμενο μενού **Directory** είναι ο πιο σημαντικός έλεγχος στο AMD Sync — καθορίζει πού θα βρεθεί κάθε εργαλείο που εκκινείτε στο Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (προεπιλογή)** — Η εκκίνηση VS Code ή JupyterLab από εδώ δημιουργεί αυτόματα έναν νέο φάκελο έργου (`Project_1`, `Project_2`, … για VS Code· `Notebook_Project_1`, `Notebook_Project_2`, … για JupyterLab).
- **Υπάρχοντες φάκελοι έργων** — Οποιοδήποτε άμεσο παιδί του `AMD_Sync` (συμπεριλαμβανομένων φακέλων που δημιουργείτε χειροκίνητα στο Ryzen AI Halo) εμφανίζεται στο αναπτυσσόμενο μενού. Ο τελευταίος φάκελος που χρησιμοποιήσατε γίνεται η προεπιλογή την επόμενη φορά.
- **Προσαρμοσμένες διαδρομές** — Πληκτρολογήστε οποιαδήποτε απόλυτη διαδρομή για να ανοίξετε έναν φάκελο αλλού στο Ryzen AI Halo. Το AMD Sync μόνο τον *ανοίγει* — δεν δημιουργεί φακέλους εκτός του `AMD_Sync`, και οι προσαρμοσμένες διαδρομές δεν αποθηκεύονται μεταξύ συνεδριών.

Εάν μια προσαρμοσμένη διαδρομή δεν λειτουργεί, το AMD Sync σας ενημερώνει για τον λόγο: μη έγκυρη σύνταξη, ο φάκελος δεν υπάρχει ή η διαδρομή δείχνει σε αρχείο.

---

## Live Metrics και JupyterLab

- **Live Metrics** — Ένα ζωντανό dashboard χρήσης GPU, μνήμης και CPU. Ο γρηγορότερος τρόπος για να επιβεβαιώσετε ότι μια απομακρυσμένη εκπαίδευση πράγματι χρησιμοποιεί το υλικό.
- **JupyterLab** — Ένα πλήρες έργο notebook συνδεδεμένο μέσω SSH στο Ryzen AI Halo, με το δικό του ενσωματωμένο τερματικό για ανάμειξη κελιών notebook και εντολών shell χωρίς να εγκαταλείψετε το UI.

---

## Ρυθμίσεις και Πολλαπλές Συσκευές

Το μενού **Settings** έχει τρεις καρτέλες:

| Καρτέλα | Τι καλύπτει |
|-----|----------------|
| **Devices** | Παραθέτει κάθε Ryzen AI Halo στο οποίο έχετε συνδεθεί επιτυχώς. Επανασύνδεση, επεξεργασία διαπιστευτηρίων ή προσθήκη νέας συσκευής. |
| **Information** | Σύνδεσμοι προς τεκμηρίωση και υποστήριξη φόρουμ. |
| **Customize** | Αλλαγή θέσης της εφαρμογής στην επιφάνεια εργασίας σας, εναλλαγή τύπου τερματικού (μόνο Windows) και έλεγχος για ενημερώσεις AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Τύπος τερματικού (Windows)** — Επιλέξτε μεταξύ **PowerShell** (προεπιλογή) και **Windows Command Prompt**.
- **Τύπος τερματικού (Linux)** — Διατίθεται μόνο το προεπιλεγμένο τερματικό συστήματος.
- **Ενημερώσεις εφαρμογής** — Αυτή η καρτέλα είναι το κατάλληλο μέρος για έλεγχο και εγκατάσταση νέων εκδόσεων AMD Sync από το UI· δεν απαιτείται ξεχωριστό πρόγραμμα ενημέρωσης.

> Μια συσκευή εμφανίζεται στις **Devices** μόνο μετά από επιτυχή πρώτη σύνδεση, οπότε οι αποτυχημένες προσπάθειες δεν θα γεμίσουν τη λίστα.

---

## Αντιμετώπιση Προβλημάτων

- **Η σύνδεση αποτυγχάνει αμέσως** — Επιβεβαιώστε ότι ο SSH server είναι ενεργοποιημένος στην καρτέλα **Remote** του Ryzen AI Halo στο Developer Center.
- **Σφάλμα λανθασμένου κωδικού πρόσβασης** — Χρησιμοποιήστε τον **κωδικό πρόσβασης σύνδεσης OS** στο Ryzen AI Halo, όχι κωδικούς από το Developer Center.
- **Το κουμπί VS Code δεν κάνει τίποτα** — Εγκαταστήστε το VS Code στο μηχάνημα client σας από το [code.visualstudio.com](https://code.visualstudio.com).
- **Το εικονίδιο AMD Sync στο tray λείπει (Linux/GNOME)** — Εγκαταστήστε και ενεργοποιήστε την επέκταση AppIndicator.
- **Το `.deb` δεν ανοίγει από τον διαχειριστή αρχείων** — Χρησιμοποιήστε `sudo apt install ./AMDSyncInstaller.deb` από ένα τερματικό.

---