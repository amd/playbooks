<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Εγκατάσταση του Lemonade

<!-- @os:windows -->
Κατεβάστε το πιο πρόσφατο πρόγραμμα εγκατάστασης από το [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) και εκτελέστε το αρχείο `.msi`.

Μετά την εγκατάσταση:
- Το CLI `lemonade` προστίθεται αυτόματα στο PATH του συστήματός σας
- Ο διακομιστής Lemonade αναμένεται να εκτελείται αυτόματα στο παρασκήνιο

Μπορείτε επίσης να πραγματοποιήσετε αθόρυβη εγκατάσταση από τη γραμμή εντολών:
```cmd
msiexec /i lemonade-server-minimal.msi /qn
```
<!-- @os:end -->

<!-- @os:linux -->
**Ubuntu:**
```bash
sudo add-apt-repository ppa:lemonade-team/stable
sudo apt install lemonade-server
```

**Arch Linux (AUR):**
```bash
yay -S lemonade-server
```

Για άλλες διανομές ή για εγκατάσταση από τον πηγαίο κώδικα, δείτε τις [πλήρεις επιλογές εγκατάστασης](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:end -->


#### Επαλήθευση της Εγκατάστασης του Lemonade

Ανοίξτε ένα τερματικό και εκτελέστε:
```bash
lemonade --version
```

Θα πρέπει να δείτε έξοδο όπως:
```
lemonade version x.y.z
```

Εάν εμφανιστεί αριθμός έκδοσης, το Lemonade είναι εγκατεστημένο σωστά και έτοιμο για χρήση.

Για γρήγορη αναφορά, ακολουθούν οι συνηθισμένες εντολές CLI του Lemonade:

| Εντολή | Τι κάνει |
| --- | --- |
| `lemonade --help` | Εμφανίζει όλες τις διαθέσιμες εντολές και σημαίες. |
| `lemonade --version` | Εκτυπώνει την εγκατεστημένη έκδοση του Lemonade. |
| `lemonade status` | Επιβεβαιώνει εάν ο διακομιστής Lemonade εκτελείται και είναι προσβάσιμος. Η προεπιλεγμένη βασική διεύθυνση URL συμβατή με OpenAI είναι `http://localhost:13305/api/v1`. |
| `lemonade list` | Παραθέτει τα μοντέλα που είναι διαθέσιμα στη ρύθμιση Lemonade σας. |
| `lemonade pull <MODEL_NAME>` | Κατεβάζει ένα μοντέλο χωρίς να το εκκινήσει. |
| `lemonade run <MODEL_NAME>` | Κατεβάζει το μοντέλο εάν χρειάζεται και στη συνέχεια το εκκινεί για συμπερασμό/συνομιλία. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | Εκκινεί ένα μοντέλο llama.cpp με το backend ROCm. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Εκκινεί ένα μοντέλο llama.cpp με το backend Vulkan. |
| `lemonade config` | Εμφανίζει τις τρέχουσες τιμές διαμόρφωσης του Lemonade. |
| `lemonade config set llamacpp.backend=rocm` | Ορίζει το προεπιλεγμένο backend llama.cpp σε ROCm. |

Για τις πιο πρόσφατες επιλογές διακομιστή Lemonade ή αντιμετώπιση προβλημάτων, ανατρέξτε στην [επίσημη τεκμηρίωση Lemonade](https://lemonade-server.ai/docs/lemonade-cli/).