<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Αυτό το playbook χρησιμοποιεί ειδικές ετικέτες που το GitHub δεν μπορεί να αποδώσει. Επισκεφθείτε το [amd.com/playbooks](https://amd.com/playbooks) για να προβάλετε σωστά αυτό το περιεχόμενο.
<!-- @github-only:end -->

# Σύνδεση δύο Ryzen™ AI Halo με RPC σε Cluster

## Επισκόπηση

Το Ryzen™ AI Halo σας είναι ήδη ικανό να εκτελεί μεγάλα γλωσσικά μοντέλα τοπικά. Η δημιουργία cluster προχωρά ένα βήμα παραπέρα, συνδυάζοντας τη μνήμη GPU πολλαπλών συστημάτων μέσω τοπικού δικτύου, δίνοντάς σας πρόσβαση σε ακόμα μεγαλύτερα μοντέλα με ισχυρότερη συλλογιστική, καλύτερη δημιουργία κώδικα και βαθύτερη πολύγλωσση κατανόηση, όλα εξ ολοκλήρου στο δικό σας υλικό.

Αυτό το playbook σας διδάσκει πώς να συνδέσετε δύο συστήματα Ryzen AI Halo σε cluster χρησιμοποιώντας τη μηχανή RPC του llama.cpp και να εκτελέσετε το GLM 4.7, ένα μοντέλο 358B παραμέτρων, και στις δύο μηχανές με επιτάχυνση AMD ROCm™.

## Τι θα Μάθετε

- Πώς να επεκτείνετε την κατανομή VRAM σε συστήματα Ryzen AI Halo
- Εγκατάσταση του llama.cpp με υποστήριξη ROCm και RPC
- Ρύθμιση παραμέτρων ενός RPC worker και εκκίνηση κατανεμημένης εξαγωγής συμπερασμάτων σε δύο κόμβους
- Εκτέλεση ενός μοντέλου 358B παραμέτρων σε δύο δικτυωμένα συστήματα Ryzen AI Halo

## Ρύθμιση της Διαμόρφωσης Μνήμης

> **Σημείωση**: Ολοκληρώστε αυτό το βήμα και στη Μηχανή 1 και στη Μηχανή 2.

<!-- @os:windows -->
Στα Windows, για να εκτελέσετε μεγαλύτερα μοντέλα που απαιτούν υψηλότερη μνήμη, πρέπει να χρησιμοποιήσουμε την κατανομή AMD Variable Graphics Memory (iGPU VRAM).

Αυτό μπορεί να γίνει ανοίγοντας τον πίνακα ελέγχου AMD Software: Adrenalin Edition και μεταβαίνοντας στο: `Performance > Tuning > AMD Variable Graphics Memory`. Ορίστε την τιμή σε **96 GB**. Παρακαλώ επανεκκινήστε το σύστημα για να τεθούν σε ισχύ οι αλλαγές.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Στο Linux, το ROCm χρησιμοποιεί ένα κοινόχρηστο pool μνήμης συστήματος, και αυτό το pool ρυθμίζεται από προεπιλογή στο μισό της μνήμης του συστήματος.

Αυτή η ποσότητα μπορεί να αυξηθεί αλλάζοντας τη ρύθμιση σελίδας Translation Table Manager (TTM) του πυρήνα, με τις παρακάτω οδηγίες. Η AMD συνιστά να ορίσετε την ελάχιστη αποκλειστική VRAM στο BIOS (0,5 GB).

* Εγκαταστήστε το βοηθητικό πρόγραμμα pipx και προσθέστε τη διαδρομή για τα wheels που εγκαθίστανται από το pipx στη διαδρομή αναζήτησης του συστήματος.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Εγκαταστήστε το wheel amd-debug-tools από το PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Εκτελέστε το εργαλείο amd-ttm για να υποβάλετε ερώτημα σχετικά με τις τρέχουσες ρυθμίσεις κοινόχρηστης μνήμης.
  ```bash
  amd-ttm
  ```

* Επαναρυθμίστε τις ρυθμίσεις κοινόχρηστης μνήμης σε **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Επανεκκινήστε το σύστημα για να τεθούν σε ισχύ οι αλλαγές.


<!-- @os:end -->
<!-- @device:halo_box -->
## Έλεγχος για Ενημερώσεις Λογισμικού

<!-- @require:software-update -->
<!-- @device:end -->
## Προαπαιτούμενα

### Υλικό

Αυτό το playbook απαιτεί δύο μονάδες Ryzen AI Halo και έναν διακόπτη Ethernet, συνδεδεμένους σε τοπολογία αστέρα με κάθε μονάδα ενσύρματα συνδεδεμένη απευθείας στον διακόπτη.

| Εξάρτημα | Ποσότητα | Περιγραφή |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Κόμβοι υπολογισμού που αποτελούν το cluster |
| Διακόπτης Ethernet 10Gbps | 1 | Κεντρικός διακόπτης για επικοινωνία πολλαπλών κόμβων Ryzen AI Halo (τουλάχιστον 2 θύρες) |
| Καλώδιο Ethernet | 2 | Συνδέει κάθε μονάδα Halo στον διακόπτη (συνιστάται Cat 7 ή υψηλότερο) |

> **Σημείωση**: Απαιτούνται δύο θύρες διακόπτη Ethernet για τη σύνδεση των δύο μονάδων Ryzen AI Halo. Απαιτείται τρίτη θύρα εάν αποκτάτε πρόσβαση στο μοντέλο από ξεχωριστή μηχανή-πελάτη αντί από μία από τις μονάδες Halo.

### Λογισμικό
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Παρακαλώ εγκαταστήστε:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) με τον φόρτο εργασίας **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Φυσική Εγκατάσταση Υλικού

> **Σημείωση**: Ολοκληρώστε αυτό το βήμα και στη Μηχανή 1 και στη Μηχανή 2.

Συνδέστε κάθε μονάδα Ryzen AI Halo στον διακόπτη Ethernet χρησιμοποιώντας καλώδιο Cat 7 (ή υψηλότερο). Αυτό δημιουργεί τη σύνδεση 10Gbps που χρησιμοποιείται για υψηλής ταχύτητας επικοινωνία μεταξύ των κόμβων.
<!-- @os:linux -->
### 1. Προσδιορισμός Διεπαφών Δικτύου

Σε κάθε μηχανή, βρείτε το όνομα της διεπαφής δικτύου της και σημειώστε το (θα αναφέρεται παρακάτω ως `IFNAME`). Εκτελέστε:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Αυτό εκτυπώνει απευθείας το όνομα της διεπαφής, για παράδειγμα:

```bash
enp191s0
```

### 2. Επαλήθευση Ταχυτήτων Σύνδεσης Δικτύου

Επιβεβαιώστε ότι η σύνδεση είναι ενεργή και λειτουργεί στην πλήρη ταχύτητά της ελέγχοντας την ταχύτητα της διεπαφής σας:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Σημείωση**: Αντικαταστήστε το `<IFNAME>` με το όνομα διεπαφής εξόδου από το [1. Προσδιορισμός Διεπαφών Δικτύου](#1-determine-network-interfaces)

Θα πρέπει να δείτε ταχύτητα `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Σημείωση**: Εάν η ταχύτητα είναι χαμηλότερη από `10000Mb/s` ή η σύνδεση δεν ενεργοποιηθεί, ελέγξτε τη σύνδεση του καλωδίου και επιβεβαιώστε ότι η θύρα του διακόπτη έχει ρυθμιστεί σε 10Gbps. Ορισμένοι διακόπτες απαιτούν απενεργοποίηση της αυτόματης διαπραγμάτευσης και χειροκίνητη ρύθμιση της ταχύτητας σύνδεσης· ανατρέξτε στην τεκμηρίωση του διακόπτη σας.

<!-- @os:end -->

<!-- @os:windows -->
### Επαλήθευση Ταχύτητας Σύνδεσης Δικτύου

Σε κάθε μηχανή, ελέγξτε την ταχύτητα σύνδεσης των διεπαφών δικτύου σας:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Η διεπαφή Ethernet σας θα πρέπει να είναι `Up` και να λειτουργεί στα `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Σημείωση**: Εάν η ταχύτητα είναι χαμηλότερη από `10 Gbps` ή η σύνδεση δεν ενεργοποιηθεί, ελέγξτε τη σύνδεση του καλωδίου και επιβεβαιώστε ότι η θύρα του διακόπτη έχει ρυθμιστεί σε 10Gbps. Ορισμένοι διακόπτες απαιτούν απενεργοποίηση της αυτόματης διαπραγμάτευσης και χειροκίνητη ρύθμιση της ταχύτητας σύνδεσης· ανατρέξτε στην τεκμηρίωση του διακόπτη σας.

<!-- @os:end -->

## Εγκατάσταση του llama.cpp

> **Σημείωση**: Ολοκληρώστε αυτό το βήμα και στη Μηχανή 1 και στη Μηχανή 2.

Διατίθενται δύο επιλογές εγκατάστασης:

- [Επιλογή 1: Lemonade SDK (Συνιστάται)](#option-1-lemonade-sdk-recommended) - προκατασκευασμένα δυαδικά αρχεία, ταχύτερη εγκατάσταση
- [Επιλογή 2: Χειροκίνητη Κατασκευή από Πηγαίο Κώδικα](#option-2-manual-source-build) - κατασκευή από πηγαίο κώδικα με πλήρη έλεγχο των σημαιών κατασκευής

### Επιλογή 1: Lemonade SDK (Συνιστάται)

Το Lemonade SDK παρέχει nightly builds του llama.cpp με επιτάχυνση AMD ROCm 7, στοχεύοντας GPU όπως το gfx1151 (Strix Halo / Ryzen AI Max+ 395) και άλλες πρόσφατες αρχιτεκτονικές Radeon.

<!-- @os:windows -->
#### Βήμα 1: Λήψη των Προ-Κατασκευασμένων Δυαδικών Αρχείων

Μεταβείτε στη σελίδα της τελευταίας έκδοσης και κατεβάστε το αρχείο που αντιστοιχεί στην πλατφόρμα και τον στόχο GPU σας:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Κατεβάστε το αρχείο με το όνομα `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (όπου `xxxx` είναι ο αριθμός κατασκευής).

#### Βήμα 2: Εξαγωγή των Δυαδικών Αρχείων

Αποσυμπιέστε το ληφθέν αρχείο:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Αυτός ο κατάλογος περιέχει πλέον εκδόσεις με ενεργοποιημένο ROCm των `llama-cli.exe`, `llama-server.exe` και `rpc-server.exe`, προμεταγλωττισμένες για το σύστημά σας Ryzen AI Halo.

#### Βήμα 3: Επαλήθευση Ανίχνευσης GPU

```bash
.\llama-cli.exe --list-devices
```

Αναμενόμενη έξοδος:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### Βήμα 1: Λήψη των Προ-Κατασκευασμένων Δυαδικών Αρχείων

Μεταβείτε στη σελίδα της τελευταίας έκδοσης και κατεβάστε το αρχείο που αντιστοιχεί στην πλατφόρμα και τον στόχο GPU σας:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Κατεβάστε το αρχείο με το όνομα `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (όπου `xxxx` είναι ο αριθμός κατασκευής).

#### Βήμα 2: Εξαγωγή και Προετοιμασία των Δυαδικών Αρχείων

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Αυτός ο κατάλογος περιέχει πλέον εκδόσεις με ενεργοποιημένο ROCm των `llama-cli`, `llama-server` και `rpc-server`, προμεταγλωττισμένες για το σύστημά σας Ryzen AI Halo.

#### Βήμα 3: Επαλήθευση Ανίχνευσης GPU

```bash
./llama-cli --list-devices
```

Αναμενόμενη έξοδος:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
Με το llama.cpp έτοιμο σε κάθε κόμβο, προχωρήστε στην ενότητα [Λήψη του Μοντέλου](#downloading-the-model).

### Επιλογή 2: Χειροκίνητη Κατασκευή από Πηγαίο Κώδικα

<!-- @os:windows -->
#### Βήμα 1: Κατασκευή του llama.cpp

Ανοίξτε το **x64 Native Tools Command Prompt** (εγκατεστημένο με τα Visual Studio Build Tools) και κλωνοποιήστε το αποθετήριο:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Προσθέστε το HIP στη διαδρομή σας και κατασκευάστε με υποστήριξη ROCm και RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Σημαία Κατασκευής | Σκοπός |
|-----------|---------|
| `-DGGML_HIP=ON` | Ενεργοποιεί τη στοίβα λογισμικού ROCm/HIP |
| `-DGGML_RPC=ON` | Ενεργοποιεί το RPC για κατανεμημένη εξαγωγή συμπερασμάτων |
| `-DGPU_TARGETS=gfx1151` | Στοχεύει στο GPU Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Χρησιμοποιεί το σύστημα κατασκευής Ninja |

#### Βήμα 2: Επαλήθευση Ανίχνευσης GPU

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

Αναμενόμενη έξοδος:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### Βήμα 3: Προσθήκη HIP στη Μόνιμη Διαδρομή Χρήστη

Το παραπάνω βήμα κατασκευής ορίζει το `%HIP_PATH%\bin` μόνο για την τρέχουσα συνεδρία. Για να καταστούν οι βιβλιοθήκες HIP διαθέσιμες σε οποιοδήποτε τερματικό (όχι μόνο στο x64 Native Tools Command Prompt), προσθέστε το μόνιμα στη διαδρομή `PATH` του χρήστη σας:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Με το llama.cpp έτοιμο σε κάθε κόμβο, προχωρήστε στην ενότητα [Λήψη του Μοντέλου](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Βήμα 1: Κατασκευή του llama.cpp

Κλωνοποιήστε το αποθετήριο:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Κατασκευάστε με υποστήριξη ROCm και RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Σημαία Κατασκευής | Σκοπός |
|-----------|---------|
| `-DGGML_HIP=ON` | Ενεργοποιεί τη στοίβα λογισμικού ROCm |
| `-DGGML_RPC=ON` | Ενεργοποιεί το RPC για κατανεμημένη εξαγωγή συμπερασμάτων |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Ενεργοποιεί το rocWMMA για βελτιωμένο Flash Attention σε AMD GPUs |
| `-DAMDGPU_TARGETS="gfx1151"` | Στοχεύει στο GPU Ryzen AI Halo (Radeon 8060s) |

Για περισσότερες επιλογές κατασκευής, ανατρέξτε στην [τεκμηρίωση κατασκευής του llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Βήμα 2: Επαλήθευση Ανίχνευσης GPU

```bash
cd rocm/bin
./llama-cli --list-devices
```

Αναμενόμενη έξοδος:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

Με το llama.cpp έτοιμο σε κάθε κόμβο, προχωρήστε στην ενότητα [Λήψη του Μοντέλου](#downloading-the-model).
<!-- @os:end -->

## Λήψη του Μοντέλου

Αυτό το εγχειρίδιο χρησιμοποιεί το [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), ένα μοντέλο 358B παραμέτρων στην κβαντοποίηση `Q4_K_XL` από το [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Σε αυτή την κβαντοποίηση, το μοντέλο απαιτεί περίπου 205GB αποθηκευτικού χώρου και χωράει εντός της συνδυασμένης μνήμης GPU δύο κόμβων Ryzen AI Halo.

Κατεβάστε τα αρχεία GGUF χρησιμοποιώντας το Hugging Face CLI:
<!-- @os:linux -->
```bash
pip install huggingface-hub
hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

> **Σημείωση**: Η λήψη του μοντέλου πρέπει να ολοκληρωθεί στο Μηχάνημα 1 (τον ελεγκτή). Οι κόμβοι εργαζόμενων RPC δεν χρειάζονται τοπικό αντίγραφο των αρχείων μοντέλου.

## Εκκίνηση του Μοντέλου στο Σύμπλεγμα

Η μηχανή RPC (Remote Procedure Call) του llama.cpp επιτρέπει σε μια μεμονωμένη παρουσία llama.cpp να μεταφορτώνει επίπεδα μοντέλου σε απομακρυσμένους εργαζόμενους μέσω δικτύου. Ένα μηχάνημα λειτουργεί ως **ελεγκτής** (Μηχάνημα 1), χειριζόμενο την τοκενοποίηση, τον προγραμματισμό και την ενορχήστρωση. Το άλλο μηχάνημα εκτελεί έναν ελαφρύ **διακομιστή RPC** (Μηχάνημα 2) που εκθέτει τη μνήμη GPU και τους υπολογιστικούς πόρους του στον ελεγκτή.

Κατά τη φόρτωση, το llama.cpp κατανέμει το μοντέλο και στους δύο κόμβους. Μόλις φορτωθεί, η εξαγωγή συμπερασμάτων προχωρά σαν να εκτελείται σε έναν μόνο επιταχυντή. Το RPC διαχειρίζεται τις μεταφορές τανυστών και τον συγχρονισμό στο παρασκήνιο.

### Βήμα 1: Εκκίνηση του Διακομιστή RPC (Μηχάνημα 2)

Στο Μηχάνημα 2, εκκινήστε τον διακομιστή RPC για να εκθέσετε τους πόρους GPU του στον ελεγκτή:
<!-- @os:linux -->
```bash
./rpc-server -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
.\rpc-server.exe -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

| Σημαία | Σκοπός |
|------|---------|
| `-p` | Θύρα για μετάδοση του διακομιστή RPC |
| `-c` | Ενεργοποιεί τοπική κρυφή μνήμη για μεγάλους τανυστές, αποφεύγοντας επαναλαμβανόμενες μεταφορές δικτύου κατά τη φόρτωση του μοντέλου |
| `--host` | Διεύθυνση IP για σύνδεση του διακομιστή RPC (`0.0.0.0` για όλες τις διεπαφές) |

Για περισσότερες επιλογές, ανατρέξτε στην [τεκμηρίωση RPC του llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Βήμα 2: Εκκίνηση του Μοντέλου (Μηχάνημα 1)

Με τον διακομιστή RPC να εκτελείται στο Μηχάνημα 2, εκκινήστε την εξαγωγή συμπερασμάτων από το Μηχάνημα 1 χρησιμοποιώντας είτε το `llama-cli` είτε το `llama-server`.

#### llama-cli

Το `llama-cli` παρέχει μια διεπαφή βασισμένη σε τερματικό για άμεση αλληλεπίδραση με το μοντέλο. Είναι ιδανικό για αξιολόγηση απόδοσης, αποσφαλμάτωση και πειραματισμό χαμηλού επιπέδου.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --rpc <RPC_WORKER_IP>:50053
```

> **Εύρεση `<RPC_WORKER_IP>`**: Στο Μηχάνημα 2, εκτελέστε `hostname -I | awk '{print $1}'` για να βρείτε την τοπική του διεύθυνση IP.
<!-- @os:end -->

<!-- @os:windows -->
> **Σημείωση**: Εκτελέστε αυτή την εντολή στο Terminal (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **Εύρεση `<RPC_WORKER_IP>`**: Στο Μηχάνημα 2, εκτελέστε `ipconfig | findstr /C:"IPv4"` στο Terminal (Powershell) για να βρείτε την τοπική του διεύθυνση IP.

<!-- @os:end -->

Μόλις εκτελεστεί, το `llama-cli` εμφανίζει την πρόοδο φόρτωσης του μοντέλου και εισέρχεται σε μια διαδραστική προτροπή όπου μπορείτε να συνομιλείτε απευθείας με το μοντέλο:

![llama-cli που εκτελεί το GLM 4.7 σε δύο κόμβους](assets/llama-cli-example.png)
#### llama-server

Το `llama-server` εκθέτει την ίδια μηχανή συμπερασμού μέσω μιας επίμονης διεργασίας διακομιστή με ενσωματωμένο web UI και ένα HTTP API συμβατό με OpenAI. Αυτή είναι η προτιμώμενη διεπαφή για μακροχρόνιες αναπτύξεις, πρόσβαση πολλών χρηστών και ενσωμάτωση με εξωτερικά εργαλεία.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_IP>:50053
```

> **Εύρεση `<RPC_WORKER_IP>`**: Στο Μηχάνημα 2, εκτελέστε `hostname -I | awk '{print $1}'` για να βρείτε την τοπική του διεύθυνση IP.
<!-- @os:end -->

<!-- @os:windows -->
> **Σημείωση**: Εκτελέστε αυτή την εντολή στο Terminal (Powershell).

```powershell
.\llama-server.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_IP>:50053
```

> **Εύρεση `<RPC_WORKER_IP>`**: Στο Μηχάνημα 2, εκτελέστε `ipconfig | findstr /C:"IPv4"` στο Terminal (Powershell) για να βρείτε την τοπική του διεύθυνση IP.
<!-- @os:end -->

Μόλις εκκινήσει, ανοίξτε το `http://<HOST_IP>:8081` στο πρόγραμμα περιήγησής σας για να αποκτήσετε πρόσβαση στο ενσωματωμένο web UI. Αυτό παρέχει μια διεπαφή συνομιλίας μέσω προγράμματος περιήγησης για αλληλεπίδραση με το μοντέλο:

![Το web UI του llama-server εκτελεί GLM 4.7 σε δύο κόμβους](assets/llama-server-example.png)

<!-- @os:linux -->
> **Εύρεση `<HOST_IP>`**: Στο Μηχάνημα 1, εκτελέστε `hostname -I | awk '{print $1}'` για να βρείτε την τοπική του διεύθυνση IP.
<!-- @os:end -->

<!-- @os:windows -->
> **Εύρεση `<HOST_IP>`**: Στο Μηχάνημα 1, εκτελέστε `ipconfig | findstr /C:"IPv4"` στο Terminal (Powershell) για να βρείτε την τοπική του διεύθυνση IP.
<!-- @os:end -->

#### Αναφορά Παραμέτρων

| Σημαία | Σκοπός |
|------|---------|
| `-m` | Διαδρομή προς το αρχείο μοντέλου GGUF (χρησιμοποιήστε το πρώτο τμήμα, `00001-of-00005`) |
| `-c` | Μέγεθος πλαισίου σε tokens. Μεγαλύτερες τιμές χρησιμοποιούν περισσότερη μνήμη |
| `-fa on` | Ενεργοποιεί το rocWMMA Flash Attention για βελτιωμένη απόδοση σε AMD GPU |
| `-ngl 999` | Μεταφορτώνει όλα τα επίπεδα του μοντέλου στο GPU |
| `--no-mmap` | Απενεργοποιεί την αντιστοίχιση μνήμης, μειώνοντας τους χρόνους φόρτωσης όταν το μέγεθος του μοντέλου υπερβαίνει τη RAM του συστήματος αλλά χωράει στη VRAM |
| `--host` | IP στο οποίο δεσμεύεται το `llama-server` (μόνο για `llama-server`) |
| `--port` | Θύρα στην οποία εξυπηρετείται το HTTP API (μόνο για `llama-server`) |
| `--rpc` | Λίστα τελικών σημείων εργατών RPC διαχωρισμένη με κόμματα (`IP:port`) |

Για πλήρη χρήση παραμέτρων, ανατρέξτε στην [τεκμηρίωση llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) και στην [τεκμηρίωση llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Επόμενα Βήματα

- **Σύνδεση εφαρμογών τρίτων**: Το `llama-server` εκθέτει ένα API συμβατό με OpenAI. Κατευθύνετε οποιαδήποτε εφαρμογή συμβατή με OpenAI (όπως το Open WebUI) στο `http://<HOST_IP>:8081` με οποιοδήποτε πλαστό κλειδί API (π.χ., `none`) για να συνδεθείτε στο cluster σας
- **Εξερεύνηση άλλων μοντέλων**: Περιηγηθείτε σε κβαντισμένα GGUF στο [Hugging Face](https://huggingface.co/models?search=gguf) για να βρείτε μοντέλα που χωράνε στη συνδυασμένη μνήμη GPU του cluster σας
- **Κλιμάκωση σε τέσσερις κόμβους**: Προσθέστε δύο ακόμη συστήματα Ryzen AI Halo ως επιπλέον εργάτες RPC για πρόσβαση σε μοντέλα στην κλίμακα του 1 τρισεκατομμυρίου παραμέτρων. Περάστε επιπλέον τελικά σημεία στο `--rpc` ως λίστα διαχωρισμένη με κόμματα (π.χ., `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)