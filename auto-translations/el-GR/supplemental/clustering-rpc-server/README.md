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

# Ομαδοποίηση Δύο Ryzen™ AI Halo με RPC

## Επισκόπηση

Το Ryzen™ AI Halo σας είναι ήδη ικανό να εκτελεί τοπικά μεγάλα γλωσσικά μοντέλα. Η ομαδοποίηση (clustering) πηγαίνει αυτό ένα βήμα παραπέρα, συνδυάζοντας τη μνήμη GPU πολλαπλών συστημάτων μέσω τοπικού δικτύου, δίνοντάς σας πρόσβαση σε ακόμη μεγαλύτερα μοντέλα με ισχυρότερη λογική συλλογιστική, καλύτερη παραγωγή κώδικα και βαθύτερη πολυγλωσσική κατανόηση, όλα εξ ολοκλήρου στο δικό σας υλικό.

Αυτό το playbook σας διδάσκει πώς να ομαδοποιήσετε δύο συστήματα Ryzen AI Halo χρησιμοποιώντας τη μηχανή RPC του llama.cpp και να εκτελέσετε το GLM 4.7, ένα μοντέλο 358B παραμέτρων, σε δύο μηχανήματα με επιτάχυνση AMD ROCm™.

## Τι Θα Μάθετε

- Πώς να επεκτείνετε την κατανομή VRAM σε συστήματα Ryzen AI Halo
- Εγκατάσταση του llama.cpp με υποστήριξη ROCm και RPC
- Ρύθμιση ενός RPC worker και εκκίνηση κατανεμημένου inference σε δύο κόμβους
- Εκτέλεση ενός μοντέλου 358B παραμέτρων σε δύο δικτυωμένα συστήματα Ryzen AI Halo

## Ρύθμιση της Διαμόρφωσης Μνήμης

> **Σημείωση**: Ολοκληρώστε αυτό το βήμα και στο Machine 1 και στο Machine 2.

<!-- @os:windows -->
Στα Windows, για να εκτελέσετε μεγαλύτερα μοντέλα που απαιτούν περισσότερη μνήμη, χρειάζεται να χρησιμοποιήσουμε την κατανομή AMD Variable Graphics Memory (iGPU VRAM).

Αυτό μπορεί να γίνει ανοίγοντας το control panel AMD Software: Adrenalin Edition και πηγαίνοντας στο: `Performance > Tuning > AMD Variable Graphics Memory`. Ορίστε την τιμή στα **96 GB**. Παρακαλώ επανεκκινήστε το σύστημα για να εφαρμοστούν οι αλλαγές.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Στο Linux, το ROCm χρησιμοποιεί μια κοινόχρηστη δεξαμενή μνήμης συστήματος, και αυτή η δεξαμενή είναι ρυθμισμένη από προεπιλογή στο μισό της μνήμης του συστήματος.

Αυτό το ποσό μπορεί να αυξηθεί αλλάζοντας τη ρύθμιση σελίδων του Translation Table Manager (TTM) του πυρήνα, με τις παρακάτω οδηγίες. Η AMD συνιστά να ορίσετε την ελάχιστη αποκλειστική VRAM στο BIOS (0.5 GB).

* Εγκαταστήστε το εργαλείο pipx και προσθέστε τη διαδρομή για τα wheels που εγκαθιστά το pipx στη διαδρομή αναζήτησης του συστήματος.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Εγκαταστήστε το wheel amd-debug-tools από το PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Εκτελέστε το εργαλείο amd-ttm για να δείτε τις τρέχουσες ρυθμίσεις κοινόχρηστης μνήμης.
  ```bash
  amd-ttm
  ```

* Επαναδιαμορφώστε τις ρυθμίσεις κοινόχρηστης μνήμης στα **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Επανεκκινήστε το σύστημα για να εφαρμοστούν οι αλλαγές.


<!-- @os:end -->
<!-- @device:halo_box -->
## Έλεγχος για Ενημερώσεις Λογισμικού

<!-- @require:software-update -->
<!-- @device:end -->
## Προαπαιτούμενα

### Υλικό

Αυτό το playbook απαιτεί δύο μονάδες Ryzen AI Halo και έναν διακόπτη Ethernet, συνδεδεμένα σε τοπολογία αστέρα με κάθε μονάδα καλωδιωμένη απευθείας στον διακόπτη.

| Στοιχείο | Ποσότητα | Περιγραφή |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Κόμβοι υπολογισμού που σχηματίζουν το cluster |
| Διακόπτης Ethernet 10Gbps | 1 | Κεντρικός διακόπτης για επικοινωνία πολλαπλών κόμβων Ryzen AI Halo (τουλάχιστον 2 θύρες) |
| Καλώδιο Ethernet | 2 | Συνδέει κάθε μονάδα Halo με τον διακόπτη (συνιστάται Cat 7 ή υψηλότερο) |

> **Σημείωση**: Απαιτούνται δύο θύρες διακόπτη Ethernet για τη σύνδεση των δύο μονάδων Ryzen AI Halo. Απαιτείται μια τρίτη θύρα εάν αποκτάτε πρόσβαση στο μοντέλο από ξεχωριστό μηχάνημα-πελάτη αντί από μία από τις μονάδες Halo.

### Λογισμικό
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Παρακαλώ εγκαταστήστε:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) με το workload **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Φυσική Ρύθμιση Υλικού

> **Σημείωση**: Ολοκληρώστε αυτό το βήμα και στο Machine 1 και στο Machine 2.

Συνδέστε κάθε μονάδα Ryzen AI Halo στον διακόπτη Ethernet χρησιμοποιώντας καλώδιο Cat 7 (ή υψηλότερο). Αυτό δημιουργεί τη σύνδεση 10Gbps που χρησιμοποιείται για επικοινωνία υψηλής ταχύτητας μεταξύ των κόμβων.
<!-- @os:linux -->
### 1. Προσδιορισμός Διεπαφών Δικτύου

Σε κάθε μηχάνημα, βρείτε το όνομα της διεπαφής δικτύου του και σημειώστε το (θα αναφέρεται παρακάτω ως `IFNAME`). Εκτελέστε:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Αυτό εμφανίζει απευθείας το όνομα της διεπαφής, για παράδειγμα:

```bash
enp191s0
```

### 2. Επαλήθευση Ταχυτήτων Σύνδεσης Δικτύου

Επιβεβαιώστε ότι η σύνδεση είναι ενεργή και λειτουργεί σε πλήρη ταχύτητα ελέγχοντας την ταχύτητα της διεπαφής σας:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Σημείωση**: Αντικαταστήστε το `<IFNAME>` με το όνομα διεπαφής εξόδου από το [1. Προσδιορισμός Διεπαφών Δικτύου](#1-determine-network-interfaces)

Θα πρέπει να δείτε ταχύτητα `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Σημείωση**: Εάν η ταχύτητα είναι χαμηλότερη από `10000Mb/s` ή η σύνδεση δεν ενεργοποιείται, ελέγξτε τη σύνδεση του καλωδίου και επιβεβαιώστε ότι η θύρα του διακόπτη είναι ρυθμισμένη στα 10Gbps. Ορισμένοι διακόπτες απαιτούν την απενεργοποίηση της αυτόματης διαπραγμάτευσης και τη μη αυτόματη ρύθμιση της ταχύτητας σύνδεσης· ανατρέξτε στην τεκμηρίωση του διακόπτη σας.

<!-- @os:end -->

<!-- @os:windows -->
### Επαλήθευση Ταχύτητας Σύνδεσης Δικτύου

Σε κάθε μηχάνημα, ελέγξτε την ταχύτητα σύνδεσης των διεπαφών δικτύου σας:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Η διεπαφή Ethernet σας θα πρέπει να είναι `Up` και να λειτουργεί στα `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Σημείωση**: Εάν η ταχύτητα είναι χαμηλότερη από `10 Gbps` ή η σύνδεση δεν ενεργοποιείται, ελέγξτε τη σύνδεση του καλωδίου και επιβεβαιώστε ότι η θύρα του διακόπτη είναι ρυθμισμένη στα 10Gbps. Ορισμένοι διακόπτες απαιτούν την απενεργοποίηση της αυτόματης διαπραγμάτευσης και τη μη αυτόματη ρύθμιση της ταχύτητας σύνδεσης· ανατρέξτε στην τεκμηρίωση του διακόπτη σας.

<!-- @os:end -->

## Εγκατάσταση του llama.cpp

> **Σημείωση**: Ολοκληρώστε αυτό το βήμα και στο Machine 1 και στο Machine 2.

Διατίθενται δύο επιλογές εγκατάστασης:

- [Επιλογή 1: Lemonade SDK (Συνιστάται)](#option-1-lemonade-sdk-recommended) - προκατασκευασμένα binaries, ταχύτερη ρύθμιση
- [Επιλογή 2: Χειροκίνητη Δημιουργία από Πηγαίο Κώδικα](#option-2-manual-source-build) - δημιουργία από πηγαίο κώδικα με πλήρη έλεγχο των flags δημιουργίας

### Επιλογή 1: Lemonade SDK (Συνιστάται)

Το Lemonade SDK παρέχει νυχτερινές εκδόσεις (nightly builds) του llama.cpp με επιτάχυνση AMD ROCm 7, στοχεύοντας GPU όπως το gfx1151 (Strix Halo / Ryzen AI Max+ 395) και άλλες πρόσφατες αρχιτεκτονικές Radeon.

<!-- @os:windows -->
#### Βήμα 1: Λήψη των Προκατασκευασμένων Binaries

Μεταβείτε στη σελίδα της τελευταίας έκδοσης και κατεβάστε το αρχείο που αντιστοιχεί στην πλατφόρμα και τον στόχο GPU σας:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Κατεβάστε το αρχείο με όνομα `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (όπου `xxxx` είναι ο αριθμός έκδοσης).

#### Βήμα 2: Αποσυμπίεση των Binaries

Αποσυμπιέστε το αρχείο που κατεβάσατε:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Αυτός ο κατάλογος περιέχει πλέον εκδόσεις με ενεργοποιημένο ROCm των `llama-cli.exe`, `llama-server.exe` και `rpc-server.exe`, προμεταγλωττισμένες για το σύστημα Ryzen AI Halo σας.

#### Βήμα 3: Επαλήθευση Εντοπισμού GPU

```bash
.\llama-cli.exe --list-devices
```

Αναμενόμενο αποτέλεσμα:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### Βήμα 1: Λήψη των Προκατασκευασμένων Binaries

Μεταβείτε στη σελίδα της τελευταίας έκδοσης και κατεβάστε το αρχείο που αντιστοιχεί στην πλατφόρμα και τον στόχο GPU σας:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Κατεβάστε το αρχείο με όνομα `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (όπου `xxxx` είναι ο αριθμός έκδοσης).

#### Βήμα 2: Αποσυμπίεση και Προετοιμασία των Binaries

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Αυτός ο κατάλογος περιέχει πλέον εκδόσεις με ενεργοποιημένο ROCm των `llama-cli`, `llama-server` και `rpc-server`, προμεταγλωττισμένες για το σύστημα Ryzen AI Halo σας.

#### Βήμα 3: Επαλήθευση Εντοπισμού GPU

```bash
./llama-cli --list-devices
```

Αναμενόμενο αποτέλεσμα:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
Αφού προετοιμάσετε το llama.cpp σε κάθε κόμβο, συνεχίστε στην ενότητα [Λήψη του Μοντέλου](#downloading-the-model).

### Επιλογή 2: Χειροκίνητη Μεταγλώττιση από τον Πηγαίο Κώδικα

<!-- @os:windows -->
#### Βήμα 1: Μεταγλώττιση του llama.cpp

Ανοίξτε το **x64 Native Tools Command Prompt** (εγκατεστημένο μαζί με τα Visual Studio Build Tools) και κλωνοποιήστε το αποθετήριο:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Προσθέστε το HIP στο path σας και μεταγλωττίστε με υποστήριξη ROCm και RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Σημαία Μεταγλώττισης | Σκοπός |
|-----------|---------|
| `-DGGML_HIP=ON` | Ενεργοποιεί το λογισμικό ROCm/HIP |
| `-DGGML_RPC=ON` | Ενεργοποιεί το RPC για κατανεμημένη επίλυση συμπερασμάτων |
| `-DGPU_TARGETS=gfx1151` | Στοχεύει το GPU Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Χρησιμοποιεί το σύστημα μεταγλώττισης Ninja |

#### Βήμα 2: Επαλήθευση Εντοπισμού GPU

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

Αναμενόμενο αποτέλεσμα:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### Βήμα 3: Προσθήκη του HIP στο Path Χρήστη σας

Το παραπάνω βήμα μεταγλώττισης όρισε το `%HIP_PATH%\bin` μόνο για την τρέχουσα συνεδρία. Για να καταστήσετε τις βιβλιοθήκες HIP διαθέσιμες σε οποιοδήποτε τερματικό (όχι μόνο στο x64 Native Tools Command Prompt), προσθέστε το μόνιμα στο `PATH` χρήστη σας:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Αφού προετοιμάσετε το llama.cpp σε κάθε κόμβο, συνεχίστε στην ενότητα [Λήψη του Μοντέλου](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Βήμα 1: Μεταγλώττιση του llama.cpp

Κλωνοποιήστε το αποθετήριο:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Μεταγλωττίστε με υποστήριξη ROCm και RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Σημαία Μεταγλώττισης | Σκοπός |
|-----------|---------|
| `-DGGML_HIP=ON` | Ενεργοποιεί το λογισμικό ROCm |
| `-DGGML_RPC=ON` | Ενεργοποιεί το RPC για κατανεμημένη επίλυση συμπερασμάτων |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Ενεργοποιεί το rocWMMA για βελτιωμένη Flash Attention σε GPU AMD |
| `-DAMDGPU_TARGETS="gfx1151"` | Στοχεύει το GPU Ryzen AI Halo (Radeon 8060s) |

Για περισσότερες επιλογές μεταγλώττισης, ανατρέξτε στην [τεκμηρίωση μεταγλώττισης του llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Βήμα 2: Επαλήθευση Εντοπισμού GPU

```bash
cd rocm/bin
./llama-cli --list-devices
```

Αναμενόμενο αποτέλεσμα:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

Αφού προετοιμάσετε το llama.cpp σε κάθε κόμβο, συνεχίστε στην ενότητα [Λήψη του Μοντέλου](#downloading-the-model).
<!-- @os:end -->

## Λήψη του Μοντέλου

Αυτός ο οδηγός χρησιμοποιεί το [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), ένα μοντέλο 358B παραμέτρων στην κβαντοποίηση `Q4_K_XL` από την [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Σε αυτή την κβαντοποίηση το μοντέλο απαιτεί περίπου 205GB αποθηκευτικού χώρου και χωράει εντός της συνδυασμένης μνήμης GPU δύο κόμβων Ryzen AI Halo.

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

> **Σημείωση**: Η λήψη του μοντέλου πρέπει να ολοκληρωθεί στο Machine 1 (τον controller). Οι κόμβοι εργασίας RPC δεν χρειάζονται τοπικό αντίγραφο των αρχείων του μοντέλου.

## Εκκίνηση του Μοντέλου στο Cluster

Η μηχανή RPC (Remote Procedure Call) του llama.cpp επιτρέπει σε ένα μεμονωμένο instance του llama.cpp να μεταφέρει επίπεδα του μοντέλου σε απομακρυσμένους workers μέσω δικτύου. Ένα μηχάνημα λειτουργεί ως ο **controller** (Machine 1), διαχειριζόμενο την tokenization, τον προγραμματισμό και τον συντονισμό. Το άλλο μηχάνημα εκτελεί έναν ελαφρύ **RPC server** (Machine 2) που εκθέτει τη μνήμη GPU και την υπολογιστική του ισχύ στον controller.

Κατά τη διάρκεια της φόρτωσης, το llama.cpp κατανέμει το μοντέλο και στους δύο κόμβους. Μόλις φορτωθεί, η επίλυση συμπερασμάτων προχωρά σαν να εκτελείται σε έναν μοναδικό επιταχυντή. Το RPC διαχειρίζεται τις μεταφορές tensor και τον συγχρονισμό στο παρασκήνιο.

### Βήμα 1: Εκκίνηση του RPC Server (Machine 2)

Στο Machine 2, εκκινήστε τον RPC server για να εκθέσετε τους πόρους GPU του στον controller:
<!-- @os:linux -->
```bash
./ggml-rpc-server -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
.\ggml-rpc-server.exe -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

| Σημαία | Σκοπός |
|------|---------|
| `-p` | Θύρα στην οποία θα μεταδίδεται ο RPC server |
| `-c` | Ενεργοποιεί μια τοπική cache για μεγάλα tensors, αποφεύγοντας επαναλαμβανόμενες μεταφορές δικτύου κατά τη φόρτωση του μοντέλου |
| `--host` | Διεύθυνση IP στην οποία θα συνδεθεί ο RPC server (`0.0.0.0` για όλες τις διεπαφές) |

Για περισσότερες επιλογές, ανατρέξτε στην [τεκμηρίωση RPC του llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Βήμα 2: Εκκίνηση του Μοντέλου (Machine 1)

Με τον RPC server σε λειτουργία στο Machine 2, εκκινήστε την επίλυση συμπερασμάτων από το Machine 1 χρησιμοποιώντας είτε το `llama-cli` είτε το `llama-server`.

#### llama-cli

Το `llama-cli` παρέχει μια διεπαφή βασισμένη σε τερματικό για απευθείας αλληλεπίδραση με το μοντέλο. Είναι ιδανικό για συγκριτική αξιολόγηση απόδοσης (benchmarking), αποσφαλμάτωση και πειραματισμό χαμηλού επιπέδου.

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

> **Εύρεση του `<RPC_WORKER_IP>`**: Στο Machine 2, εκτελέστε `hostname -I | awk '{print $1}'` για να βρείτε την τοπική του διεύθυνση IP.
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

> **Εύρεση του `<RPC_WORKER_IP>`**: Στο Machine 2, εκτελέστε `ipconfig | findstr /C:"IPv4"` στο Terminal (Powershell) για να βρείτε την τοπική του διεύθυνση IP.

<!-- @os:end -->

Μόλις εκκινηθεί, το `llama-cli` εμφανίζει την πρόοδο φόρτωσης του μοντέλου και εισέρχεται σε μια διαδραστική προτροπή όπου μπορείτε να συνομιλήσετε απευθείας με το μοντέλο:

![Το llama-cli εκτελεί το GLM 4.7 σε δύο κόμβους](assets/llama-cli-example.png)
#### llama-server

Το `llama-server` εκθέτει την ίδια μηχανή συμπερασμού μέσω μιας μόνιμης διεργασίας διακομιστή με ενσωματωμένο web UI και HTTP API συμβατό με OpenAI. Αυτή είναι η προτιμώμενη διεπαφή για αναπτύξεις μεγαλύτερης διάρκειας, πρόσβαση πολλών χρηστών και ενσωμάτωση με εξωτερικά εργαλεία.

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

> **Εύρεση `<RPC_WORKER_IP>`**: Στο Μηχάνημα 2, εκτελέστε `hostname -I | awk '{print $1}'` για να βρείτε τη τοπική του διεύθυνση IP.
<!-- @os:end -->

<!-- @os:windows -->
> **Σημείωση**: Εκτελέστε αυτήν την εντολή στο Terminal (Powershell).

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

> **Εύρεση `<RPC_WORKER_IP>`**: Στο Μηχάνημα 2, εκτελέστε `ipconfig | findstr /C:"IPv4"` στο Terminal (Powershell) για να βρείτε τη τοπική του διεύθυνση IP.
<!-- @os:end -->

Μόλις ξεκινήσει, ανοίξτε το `http://<HOST_IP>:8081` στο πρόγραμμα περιήγησής σας για να αποκτήσετε πρόσβαση στο ενσωματωμένο web UI. Αυτό παρέχει μια διεπαφή συνομιλίας μέσω προγράμματος περιήγησης για την αλληλεπίδραση με το μοντέλο:

![llama-server web UI εκτελώντας το GLM 4.7 σε δύο κόμβους](assets/llama-server-example.png)

<!-- @os:linux -->
> **Εύρεση `<HOST_IP>`**: Στο Μηχάνημα 1, εκτελέστε `hostname -I | awk '{print $1}'` για να βρείτε τη τοπική του διεύθυνση IP.
<!-- @os:end -->

<!-- @os:windows -->
> **Εύρεση `<HOST_IP>`**: Στο Μηχάνημα 1, εκτελέστε `ipconfig | findstr /C:"IPv4"` στο Terminal (Powershell) για να βρείτε τη τοπική του διεύθυνση IP.
<!-- @os:end -->

#### Αναφορά Παραμέτρων

| Σημαία | Σκοπός |
|------|---------|
| `-m` | Διαδρομή προς το αρχείο μοντέλου GGUF (χρησιμοποιήστε το πρώτο τμήμα, `00001-of-00005`) |
| `-c` | Μέγεθος πλαισίου σε tokens. Μεγαλύτερες τιμές χρησιμοποιούν περισσότερη μνήμη |
| `-fa on` | Ενεργοποιεί το rocWMMA Flash Attention για βελτιωμένη απόδοση σε AMD GPUs |
| `-ngl 999` | Μεταφέρει όλα τα επίπεδα του μοντέλου στη GPU |
| `--no-mmap` | Απενεργοποιεί την αντιστοίχιση μνήμης (memory-mapping), μειώνοντας τους χρόνους φόρτωσης όταν το μέγεθος του μοντέλου υπερβαίνει τη μνήμη RAM του συστήματος αλλά χωράει στη VRAM |
| `--host` | Διεύθυνση IP στην οποία θα συνδεθεί το `llama-server` (μόνο για `llama-server`) |
| `--port` | Θύρα στην οποία θα εξυπηρετείται το HTTP API (μόνο για `llama-server`) |
| `--rpc` | Λίστα διαχωρισμένη με κόμμα από endpoints εργαζομένων RPC (`IP:port`) |

Για την πλήρη χρήση των παραμέτρων, ανατρέξτε στην [τεκμηρίωση llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) και στην [τεκμηρίωση llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Επόμενα Βήματα

- **Σύνδεση εφαρμογών τρίτων**: Το `llama-server` εκθέτει ένα API συμβατό με OpenAI. Κατευθύνετε οποιαδήποτε εφαρμογή συμβατή με OpenAI (όπως το Open WebUI) στη διεύθυνση `http://<HOST_IP>:8081` με οποιοδήποτε δοκιμαστικό κλειδί API (π.χ., `none`) για να συνδεθείτε στο cluster σας
- **Εξερεύνηση άλλων μοντέλων**: Περιηγηθείτε σε κβαντισμένα GGUF στο [Hugging Face](https://huggingface.co/models?search=gguf) για να βρείτε μοντέλα που χωρούν εντός της συνολικής μνήμης GPU του cluster σας
- **Κλιμάκωση σε τέσσερις κόμβους**: Προσθέστε δύο ακόμα συστήματα Ryzen AI Halo ως επιπλέον εργαζομένους RPC για πρόσβαση σε μοντέλα κλίμακας 1 τρισεκατομμυρίου παραμέτρων. Περάστε επιπλέον endpoints στο `--rpc` ως λίστα διαχωρισμένη με κόμμα (π.χ., `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)