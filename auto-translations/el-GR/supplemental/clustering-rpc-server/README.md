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

# Ομαδοποίηση δύο Ryzen™ AI Halo με RPC

## Επισκόπηση

Το Ryzen™ AI Halo σας είναι ήδη ικανό να εκτελεί μεγάλα γλωσσικά μοντέλα τοπικά. Η ομαδοποίηση (clustering) πηγαίνει αυτό ένα βήμα παραπέρα, συνδυάζοντας τη μνήμη GPU πολλαπλών συστημάτων μέσω τοπικού δικτύου, δίνοντάς σας πρόσβαση σε ακόμα μεγαλύτερα μοντέλα με ισχυρότερη λογική, καλύτερη παραγωγή κώδικα και βαθύτερη πολυγλωσσική κατανόηση, όλα εξ ολοκλήρου στο δικό σας υλικό.

Αυτό το εγχειρίδιο σάς διδάσκει πώς να ομαδοποιήσετε δύο συστήματα Ryzen AI Halo χρησιμοποιώντας τη μηχανή RPC του llama.cpp και να εκτελέσετε το GLM 4.7, ένα μοντέλο 358 δισεκατομμυρίων παραμέτρων, σε αμφότερα τα μηχανήματα με επιτάχυνση AMD ROCm™.

## Τι Θα Μάθετε

- Πώς να επεκτείνετε την κατανομή VRAM σε συστήματα Ryzen AI Halo
- Εγκατάσταση του llama.cpp με υποστήριξη ROCm και RPC
- Διαμόρφωση ενός RPC worker και εκκίνηση κατανεμημένης συμπερασματολογίας (inference) σε δύο κόμβους
- Εκτέλεση ενός μοντέλου 358 δισεκατομμυρίων παραμέτρων σε δύο δικτυωμένα συστήματα Ryzen AI Halo

## Ρύθμιση Διαμόρφωσης Μνήμης

> **Σημείωση**: Ολοκληρώστε αυτό το βήμα τόσο στο Μηχάνημα 1 όσο και στο Μηχάνημα 2.

<!-- @os:windows -->
Στα Windows, για την εκτέλεση μεγαλύτερων μοντέλων που απαιτούν περισσότερη μνήμη, χρειάζεται να χρησιμοποιήσουμε την κατανομή AMD Variable Graphics Memory (iGPU VRAM).

Αυτό μπορεί να γίνει ανοίγοντας το πίνακα ελέγχου AMD Software: Adrenalin Edition και μεταβαίνοντας στο: `Performance > Tuning > AMD Variable Graphics Memory`. Ορίστε την τιμή στα **96 GB**. Παρακαλούμε επανεκκινήστε το σύστημα για να τεθούν σε ισχύ οι αλλαγές.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Στο Linux, το ROCm χρησιμοποιεί μια κοινή δεξαμενή μνήμης συστήματος, και αυτή η δεξαμενή είναι διαμορφωμένη από προεπιλογή στο μισό της μνήμης του συστήματος.

Αυτή η ποσότητα μπορεί να αυξηθεί αλλάζοντας τη ρύθμιση σελίδας του Translation Table Manager (TTM) του πυρήνα, με τις ακόλουθες οδηγίες. Η AMD συνιστά να ορίσετε την ελάχιστη αφιερωμένη VRAM στο BIOS (0.5 GB).

* Εγκαταστήστε το βοηθητικό πρόγραμμα pipx και προσθέστε τη διαδρομή για τα wheels που εγκαθίστανται από το pipx στη διαδρομή αναζήτησης του συστήματος.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Εγκαταστήστε το wheel amd-debug-tools από το PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Εκτελέστε το εργαλείο amd-ttm για να ερωτήσετε τις τρέχουσες ρυθμίσεις για την κοινή μνήμη.
  ```bash
  amd-ttm
  ```

* Επαναδιαμορφώστε τις ρυθμίσεις κοινής μνήμης στα **120 GB**:
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

Αυτό το εγχειρίδιο απαιτεί δύο μονάδες Ryzen AI Halo και έναν διακόπτη Ethernet, συνδεδεμένα σε τοπολογία αστέρα με κάθε μονάδα συνδεδεμένη απευθείας στο διακόπτη.

| Στοιχείο | Ποσότητα | Περιγραφή |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Κόμβοι υπολογισμού που σχηματίζουν το cluster |
| Διακόπτης Ethernet 10Gbps | 1 | Κεντρικός διακόπτης για την επικοινωνία πολλαπλών κόμβων Ryzen AI Halo (τουλάχιστον 2 θύρες) |
| Καλώδιο Ethernet | 2 | Συνδέει κάθε μονάδα Halo με το διακόπτη (συνιστάται Cat 7 ή υψηλότερο) |

> **Σημείωση**: Απαιτούνται δύο θύρες διακόπτη Ethernet για τη σύνδεση των δύο μονάδων Ryzen AI Halo. Απαιτείται τρίτη θύρα εάν έχετε πρόσβαση στο μοντέλο από ξεχωριστό μηχάνημα-πελάτη αντί από μία από τις μονάδες Halo.

### Λογισμικό
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Παρακαλούμε εγκαταστήστε:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) με το φόρτο εργασίας **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Φυσική Εγκατάσταση Υλικού

> **Σημείωση**: Ολοκληρώστε αυτό το βήμα τόσο στο Μηχάνημα 1 όσο και στο Μηχάνημα 2.

Συνδέστε κάθε μονάδα Ryzen AI Halo στο διακόπτη Ethernet χρησιμοποιώντας καλώδιο Cat 7 (ή υψηλότερο). Αυτό δημιουργεί τη σύνδεση 10Gbps που χρησιμοποιείται για επικοινωνία υψηλής ταχύτητας μεταξύ των κόμβων.
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

Επιβεβαιώστε ότι η σύνδεση είναι ενεργή και λειτουργεί με πλήρη ταχύτητα ελέγχοντας την ταχύτητα της διεπαφής σας:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Σημείωση**: Αντικαταστήστε το `<IFNAME>` με το όνομα διεπαφής εξόδου από το [1. Προσδιορισμός Διεπαφών Δικτύου](#1-determine-network-interfaces)

Θα πρέπει να δείτε ταχύτητα `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Σημείωση**: Εάν η ταχύτητα είναι χαμηλότερη από `10000Mb/s` ή η σύνδεση δεν ενεργοποιείται, ελέγξτε τη σύνδεση καλωδίου και επιβεβαιώστε ότι η θύρα του διακόπτη είναι ρυθμισμένη στα 10Gbps. Ορισμένοι διακόπτες απαιτούν να απενεργοποιηθεί η αυτόματη διαπραγμάτευση και η ταχύτητα σύνδεσης να οριστεί χειροκίνητα· ανατρέξτε στην τεκμηρίωση του διακόπτη σας.

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

> **Σημείωση**: Εάν η ταχύτητα είναι χαμηλότερη από `10 Gbps` ή η σύνδεση δεν ενεργοποιείται, ελέγξτε τη σύνδεση καλωδίου και επιβεβαιώστε ότι η θύρα του διακόπτη είναι ρυθμισμένη στα 10Gbps. Ορισμένοι διακόπτες απαιτούν να απενεργοποιηθεί η αυτόματη διαπραγμάτευση και η ταχύτητα σύνδεσης να οριστεί χειροκίνητα· ανατρέξτε στην τεκμηρίωση του διακόπτη σας.

<!-- @os:end -->

## Εγκατάσταση του llama.cpp

> **Σημείωση**: Ολοκληρώστε αυτό το βήμα τόσο στο Μηχάνημα 1 όσο και στο Μηχάνημα 2.

Διατίθενται δύο επιλογές εγκατάστασης:

- [Επιλογή 1: Lemonade SDK (Συνιστάται)](#option-1-lemonade-sdk-recommended) - προ-χτισμένα δυαδικά αρχεία, ταχύτερη ρύθμιση
- [Επιλογή 2: Χειροκίνητη Κατασκευή από Πηγαίο Κώδικα](#option-2-manual-source-build) - κατασκευή από πηγαίο κώδικα με πλήρη έλεγχο των σημαιών κατασκευής

### Επιλογή 1: Lemonade SDK (Συνιστάται)

Το Lemonade SDK παρέχει νυχτερινές εκδόσεις (nightly builds) του llama.cpp με επιτάχυνση AMD ROCm 7, στοχεύοντας GPU όπως το gfx1151 (Strix Halo / Ryzen AI Max+ 395) και άλλες πρόσφατες αρχιτεκτονικές Radeon.

<!-- @os:windows -->
#### Βήμα 1: Λήψη των Προκατασκευασμένων Δυαδικών Αρχείων

Μεταβείτε στη σελίδα της τελευταίας έκδοσης και κατεβάστε το αρχείο που αντιστοιχεί στην πλατφόρμα και τον στόχο GPU σας:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Κατεβάστε το αρχείο με όνομα `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (όπου το `xxxx` είναι ο αριθμός έκδοσης).

#### Βήμα 2: Αποσυμπίεση των Δυαδικών Αρχείων

Αποσυμπιέστε το αρχείο που κατεβάσατε:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Αυτός ο κατάλογος περιέχει πλέον εκδόσεις με υποστήριξη ROCm των `llama-cli.exe`, `llama-server.exe`, και `rpc-server.exe`, προμεταγλωττισμένες για το σύστημα Ryzen AI Halo σας.

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
#### Βήμα 1: Λήψη των Προκατασκευασμένων Δυαδικών Αρχείων

Μεταβείτε στη σελίδα της τελευταίας έκδοσης και κατεβάστε το αρχείο που αντιστοιχεί στην πλατφόρμα και τον στόχο GPU σας:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Κατεβάστε το αρχείο με όνομα `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (όπου το `xxxx` είναι ο αριθμός έκδοσης).

#### Βήμα 2: Αποσυμπίεση και Προετοιμασία των Δυαδικών Αρχείων

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Αυτός ο κατάλογος περιέχει πλέον εκδόσεις με υποστήριξη ROCm των `llama-cli`, `llama-server`, και `rpc-server`, προμεταγλωττισμένες για το σύστημα Ryzen AI Halo σας.

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
Με το llama.cpp έτοιμο σε κάθε κόμβο, προχωρήστε στο [Λήψη του Μοντέλου](#downloading-the-model).

### Επιλογή 2: Χειροκίνητη Δημιουργία από τον Πηγαίο Κώδικα

<!-- @os:windows -->
#### Βήμα 1: Δημιουργία του llama.cpp

Ανοίξτε το **x64 Native Tools Command Prompt** (εγκατεστημένο μαζί με τα Visual Studio Build Tools) και κλωνοποιήστε το αποθετήριο:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Προσθέστε το HIP στη διαδρομή σας και δημιουργήστε με υποστήριξη ROCm και RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Σημαία Δημιουργίας | Σκοπός |
|-----------|---------|
| `-DGGML_HIP=ON` | Ενεργοποιεί τη στοίβα λογισμικού ROCm/HIP |
| `-DGGML_RPC=ON` | Ενεργοποιεί το RPC για κατανεμημένη εξαγωγή συμπερασμάτων |
| `-DGPU_TARGETS=gfx1151` | Στοχεύει στο GPU Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Χρησιμοποιεί το σύστημα δημιουργίας Ninja |

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

#### Βήμα 3: Προσθήκη του HIP στη Διαδρομή Χρήστη σας

Το παραπάνω βήμα δημιουργίας όρισε το `%HIP_PATH%\bin` μόνο για την τρέχουσα συνεδρία. Για να καταστήσετε τις βιβλιοθήκες HIP διαθέσιμες σε οποιοδήποτε τερματικό (όχι μόνο στο x64 Native Tools Command Prompt), προσθέστε το μόνιμα στο `PATH` του χρήστη σας:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Με το llama.cpp έτοιμο σε κάθε κόμβο, προχωρήστε στο [Λήψη του Μοντέλου](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Βήμα 1: Δημιουργία του llama.cpp

Κλωνοποιήστε το αποθετήριο:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Δημιουργήστε με υποστήριξη ROCm και RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Σημαία Δημιουργίας | Σκοπός |
|-----------|---------|
| `-DGGML_HIP=ON` | Ενεργοποιεί τη στοίβα λογισμικού ROCm |
| `-DGGML_RPC=ON` | Ενεργοποιεί το RPC για κατανεμημένη εξαγωγή συμπερασμάτων |
| `-DAMDGPU_TARGETS="gfx1151"` | Στοχεύει στο GPU Ryzen AI Halo (Radeon 8060s) |

Για περισσότερες επιλογές δημιουργίας, ανατρέξτε στην [τεκμηρίωση δημιουργίας του llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

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

Με το llama.cpp έτοιμο σε κάθε κόμβο, προχωρήστε στο [Λήψη του Μοντέλου](#downloading-the-model).
<!-- @os:end -->

## Λήψη του Μοντέλου

Αυτός ο οδηγός χρησιμοποιεί το [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), ένα μοντέλο 358 δισεκατομμυρίων παραμέτρων στην κβαντοποίηση `Q4_K_XL` από την [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Σε αυτή την κβαντοποίηση, το μοντέλο απαιτεί περίπου 205GB αποθηκευτικού χώρου και χωράει εντός της συνδυασμένης μνήμης GPU δύο κόμβων Ryzen AI Halo.

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

> **Σημείωση**: Η λήψη του μοντέλου πρέπει να ολοκληρωθεί στο Μηχάνημα 1 (τον ελεγκτή). Οι κόμβοι εργασίας RPC δεν χρειάζονται τοπικό αντίγραφο των αρχείων του μοντέλου.

## Εκκίνηση του Μοντέλου στο Cluster

Η μηχανή RPC (Remote Procedure Call) του llama.cpp επιτρέπει σε ένα μεμονωμένο στιγμιότυπο llama.cpp να μεταβιβάζει επίπεδα του μοντέλου σε απομακρυσμένους εργάτες μέσω δικτύου. Ένα μηχάνημα λειτουργεί ως **ελεγκτής** (Μηχάνημα 1), χειριζόμενο τη διακριτοποίηση, τον προγραμματισμό και τον συντονισμό. Το άλλο μηχάνημα εκτελεί έναν ελαφρύ **διακομιστή RPC** (Μηχάνημα 2) που εκθέτει τη μνήμη GPU και την υπολογιστική του ισχύ στον ελεγκτή.

Κατά τη φόρτωση, το llama.cpp κατατεμαχίζει το μοντέλο και στους δύο κόμβους. Μόλις φορτωθεί, η εξαγωγή συμπερασμάτων προχωρά σαν να εκτελείται σε έναν μοναδικό επιταχυντή. Το RPC χειρίζεται τις μεταφορές τανυστών και τον συγχρονισμό στο παρασκήνιο.

### Βήμα 1: Εκκίνηση του Διακομιστή RPC (Μηχάνημα 2)

Στο Μηχάνημα 2, εκκινήστε τον διακομιστή RPC για να εκθέσετε τους πόρους GPU του στον ελεγκτή:
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
| `-p` | Θύρα στην οποία θα εκπέμπεται ο διακομιστής RPC |
| `-c` | Ενεργοποιεί μια τοπική προσωρινή μνήμη (cache) για μεγάλους τανυστές, αποφεύγοντας επαναλαμβανόμενες μεταφορές δικτύου κατά τη φόρτωση του μοντέλου |
| `--host` | Διεύθυνση IP στην οποία θα συνδεθεί ο διακομιστής RPC (`0.0.0.0` για όλες τις διεπαφές) |

Για περισσότερες επιλογές, ανατρέξτε στην [τεκμηρίωση RPC του llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Βήμα 2: Εκκίνηση του Μοντέλου (Μηχάνημα 1)

Με τον διακομιστή RPC να εκτελείται στο Μηχάνημα 2, εκκινήστε την εξαγωγή συμπερασμάτων από το Μηχάνημα 1 χρησιμοποιώντας είτε το `llama-cli` είτε το `llama-server`.

#### llama-cli

Το `llama-cli` παρέχει μια διεπαφή βασισμένη σε τερματικό για απευθείας αλληλεπίδραση με το μοντέλο. Είναι ιδανικό για συγκριτική αξιολόγηση απόδοσης, αποσφαλμάτωση και πειραματισμό χαμηλού επιπέδου.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  --rpc <RPC_WORKER_IP>:50053
```

> **Εύρεση του `<RPC_WORKER_IP>`**: Στο Μηχάνημα 2, εκτελέστε `hostname -I | awk '{print $1}'` για να βρείτε την τοπική διεύθυνση IP του.
<!-- @os:end -->

<!-- @os:windows -->
> **Σημείωση**: Εκτελέστε αυτή την εντολή στο Terminal (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --rpc <RPC_WORKER_IP>:50053
```

> **Εύρεση του `<RPC_WORKER_IP>`**: Στο Μηχάνημα 2, εκτελέστε `ipconfig | findstr /C:"IPv4"` στο Terminal (Powershell) για να βρείτε την τοπική διεύθυνση IP του.

<!-- @os:end -->

Μόλις εκτελεστεί, το `llama-cli` εμφανίζει την πρόοδο φόρτωσης του μοντέλου και εισέρχεται σε μια διαδραστική προτροπή όπου μπορείτε να συνομιλήσετε απευθείας με το μοντέλο:

![το llama-cli εκτελεί το GLM 4.7 σε δύο κόμβους](assets/llama-cli-example.png)
#### llama-server

Το `llama-server` εκθέτει την ίδια μηχανή συμπερασμού μέσω μιας μόνιμης διαδικασίας διακομιστή με ενσωματωμένο web UI και ένα HTTP API συμβατό με το OpenAI. Αυτή είναι η προτιμώμενη διεπαφή για αναπτύξεις μεγαλύτερης διάρκειας, πρόσβαση πολλών χρηστών και ενσωμάτωση με εξωτερικά εργαλεία.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_IP>:50053
```

> **Εύρεση του `<RPC_WORKER_IP>`**: Στο Μηχάνημα 2, εκτελέστε `hostname -I | awk '{print $1}'` για να βρείτε την τοπική του διεύθυνση IP.
<!-- @os:end -->

<!-- @os:windows -->
> **Σημείωση**: Εκτελέστε αυτήν την εντολή στο Terminal (Powershell).

```powershell
.\llama-server.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_IP>:50053
```

> **Εύρεση του `<RPC_WORKER_IP>`**: Στο Μηχάνημα 2, εκτελέστε `ipconfig | findstr /C:"IPv4"` στο Terminal (Powershell) για να βρείτε την τοπική του διεύθυνση IP.
<!-- @os:end -->

Μόλις ξεκινήσει, ανοίξτε το `http://<HOST_IP>:8081` στο πρόγραμμα περιήγησής σας για πρόσβαση στο ενσωματωμένο web UI. Αυτό παρέχει μια διεπαφή συνομιλίας μέσω προγράμματος περιήγησης για αλληλεπίδραση με το μοντέλο:

![llama-server web UI running GLM 4.7 across two nodes](assets/llama-server-example.png)

<!-- @os:linux -->
> **Εύρεση του `<HOST_IP>`**: Στο Μηχάνημα 1, εκτελέστε `hostname -I | awk '{print $1}'` για να βρείτε την τοπική του διεύθυνση IP.
<!-- @os:end -->

<!-- @os:windows -->
> **Εύρεση του `<HOST_IP>`**: Στο Μηχάνημα 1, εκτελέστε `ipconfig | findstr /C:"IPv4"` στο Terminal (Powershell) για να βρείτε την τοπική του διεύθυνση IP.
<!-- @os:end -->

#### Αναφορά Παραμέτρων

| Σημαία | Σκοπός |
|------|---------|
| `-m` | Διαδρομή προς το αρχείο μοντέλου GGUF (χρησιμοποιήστε το πρώτο shard, `00001-of-00005`) |
| `-c` | Μέγεθος πλαισίου (context) σε tokens. Μεγαλύτερες τιμές χρησιμοποιούν περισσότερη μνήμη |
| `-fa on` | Ενεργοποιεί το rocWMMA Flash Attention για βελτιωμένη απόδοση σε GPU της AMD |
| `-ngl 999` | Μεταφέρει όλα τα layers του μοντέλου στη GPU |
| `-lm none` | Ορίζει τη λειτουργία φόρτωσης μοντέλου σε `none`, απενεργοποιώντας το memory-mapping για μείωση των χρόνων φόρτωσης όταν το μέγεθος του μοντέλου υπερβαίνει τη μνήμη RAM του συστήματος αλλά χωράει στη VRAM |
| `--host` | Η διεύθυνση IP στην οποία θα συνδεθεί το `llama-server` (μόνο για το `llama-server`) |
| `--port` | Η θύρα στην οποία θα εξυπηρετείται το HTTP API (μόνο για το `llama-server`) |
| `--rpc` | Λίστα διαχωρισμένων με κόμμα endpoints εργαζομένων RPC (`IP:port`) |

Για την πλήρη χρήση των παραμέτρων, ανατρέξτε στην [τεκμηρίωση llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) και στην [τεκμηρίωση llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Επόμενα Βήματα

- **Σύνδεση εφαρμογών τρίτων**: Το `llama-server` εκθέτει ένα API συμβατό με το OpenAI. Κατευθύνετε οποιαδήποτε εφαρμογή συμβατή με OpenAI (όπως το Open WebUI) στη διεύθυνση `http://<HOST_IP>:8081` με οποιοδήποτε προσωρινό (placeholder) API key (π.χ., `none`) για να συνδεθείτε στο cluster σας
- **Εξερεύνηση άλλων μοντέλων**: Περιηγηθείτε στα κβαντισμένα (quantized) GGUFs στο [Hugging Face](https://huggingface.co/models?search=gguf) για να βρείτε μοντέλα που χωράνε στη συνδυασμένη μνήμη GPU του cluster σας
- **Κλιμάκωση σε τέσσερις κόμβους**: Προσθέστε δύο ακόμη συστήματα Ryzen AI Halo ως επιπλέον εργαζόμενους RPC για πρόσβαση σε μοντέλα κλίμακας 1 τρισεκατομμυρίου παραμέτρων. Περάστε επιπλέον endpoints στο `--rpc` ως λίστα διαχωρισμένη με κόμμα (π.χ., `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)