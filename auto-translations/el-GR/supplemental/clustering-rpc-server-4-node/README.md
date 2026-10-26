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

# Ομαδοποίηση Τεσσάρων Ryzen™ AI Halo με RPC

## Επισκόπηση

Το Ryzen™ AI Halo σας είναι ήδη ικανό να εκτελεί μεγάλα γλωσσικά μοντέλα τοπικά. Η ομαδοποίηση (clustering) πηγαίνει αυτό ένα βήμα παραπέρα, συνδυάζοντας τη μνήμη GPU πολλαπλών συστημάτων μέσω τοπικού δικτύου, δίνοντάς σας πρόσβαση σε ακόμη μεγαλύτερα μοντέλα με ισχυρότερη λογική συλλογιστική, καλύτερη παραγωγή κώδικα και βαθύτερη πολυγλωσσική κατανόηση, όλα εξ ολοκλήρου στο δικό σας υλικό.

Αυτός ο οδηγός σας διδάσκει πώς να ομαδοποιήσετε τέσσερα συστήματα Ryzen AI Halo χρησιμοποιώντας τη μηχανή RPC του llama.cpp και να εκτελέσετε το Kimi K2.6, ένα μεγάλο μοντέλο μείγματος ειδικών (mixture-of-experts), σε όλα τα τέσσερα μηχανήματα με επιτάχυνση AMD ROCm™.

## Τι θα Μάθετε

- Πώς να επεκτείνετε την κατανομή VRAM σε συστήματα Ryzen AI Halo
- Εγκατάσταση του llama.cpp με υποστήριξη ROCm και RPC
- Διαμόρφωση εργατών RPC (RPC workers) και εκκίνηση κατανεμημένης συμπερασματικής επεξεργασίας (inference) σε τέσσερους κόμβους
- Εκτέλεση ενός μοντέλου 1T παραμέτρων σε τέσσερα διασυνδεδεμένα συστήματα Ryzen AI Halo

## Ρύθμιση της Διαμόρφωσης Μνήμης

> **Σημείωση**: Ολοκληρώστε αυτό το βήμα και στα τέσσερα μηχανήματα (Μηχάνημα 1 έως Μηχάνημα 4).

<!-- @device:halo_box -->
<!-- @os:windows -->
> **Εκτέλεση μοντέλων κοντά ή πάνω από 128 GB:** Σε συστήματα AMD Ryzen™ AI Max 400 Series (Gorgon Halo) που εκτελούν Windows, τα μοντέλα που πλησιάζουν ή υπερβαίνουν τα 128 GB μνήμης απαιτούν πρόσθετη διαμόρφωση για να εκτελεστούν χωρίς σφάλματα. Ακολουθήστε τον [Οδηγό AMD Ryzen AI Max PRO 400 Series για Λειτουργικό Σύστημα Windows](https://docs.amd.com/v/u/en-US/73342_1.00_AMD_Ryzen_AI_Max_PRO_400_Series_Windows_OS_Guidelines) πριν φορτώσετε το μοντέλο.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:windows -->
Στα Windows, για να εκτελέσετε μεγαλύτερα μοντέλα που απαιτούν περισσότερη μνήμη, χρειάζεται να χρησιμοποιήσουμε την κατανομή AMD Variable Graphics Memory (iGPU VRAM).

Αυτό μπορεί να γίνει ανοίγοντας το πίνακα ελέγχου AMD Software: Adrenalin Edition και πηγαίνοντας στο: `Performance > Tuning > AMD Variable Graphics Memory`. Ορίστε την τιμή σε **96 GB**. Παρακαλούμε επανεκκινήστε το σύστημα για να εφαρμοστούν οι αλλαγές.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Στο Linux, το ROCm χρησιμοποιεί μια κοινόχρηστη δεξαμενή μνήμης συστήματος, και αυτή η δεξαμενή είναι ρυθμισμένη από προεπιλογή στο μισό της μνήμης του συστήματος.

Αυτή η ποσότητα μπορεί να αυξηθεί αλλάζοντας τη ρύθμιση σελίδων του Translation Table Manager (TTM) του πυρήνα, με τις παρακάτω οδηγίες. Η AMD συνιστά τον ορισμό της ελάχιστης αποκλειστικής VRAM στο BIOS (0.5 GB).

* Εγκαταστήστε το εργαλείο pipx και προσθέστε τη διαδρομή για τα wheels που εγκαθίστανται από το pipx στη διαδρομή αναζήτησης του συστήματος.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Εγκαταστήστε το wheel amd-debug-tools από το PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Εκτελέστε το εργαλείο amd-ttm για να ερωτήσετε τις τρέχουσες ρυθμίσεις για την κοινόχρηστη μνήμη.
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

Αυτός ο οδηγός απαιτεί τέσσερις μονάδες Ryzen AI Halo και έναν διακόπτη δικτύου Ethernet, συνδεδεμένα σε τοπολογία αστέρα με κάθε μονάδα συνδεδεμένη απευθείας στο διακόπτη.

| Στοιχείο | Ποσότητα | Περιγραφή |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Κόμβοι υπολογισμού που αποτελούν το σύμπλεγμα (cluster) |
| Διακόπτης Ethernet 10Gbps | 1 | Κεντρικός διακόπτης που επιτρέπει επικοινωνία πολλαπλών κόμβων Ryzen AI Halo (τουλάχιστον 4 θύρες) |
| Καλώδιο Ethernet | 4 | Συνδέει κάθε μονάδα Halo στο διακόπτη (συνιστάται Cat 7 ή υψηλότερο) |

> **Σημείωση**: Απαιτούνται τέσσερις θύρες διακόπτη Ethernet για τη σύνδεση των τεσσάρων μονάδων Ryzen AI Halo. Απαιτείται πέμπτη θύρα εάν αποκτάτε πρόσβαση στο μοντέλο από ξεχωριστό μηχάνημα-πελάτη αντί από μία από τις μονάδες Halo.

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

## Ρύθμιση Φυσικού Υλικού

> **Σημείωση**: Ολοκληρώστε αυτό το βήμα και στα τέσσερα μηχανήματα (Μηχάνημα 1 έως Μηχάνημα 4).

Συνδέστε κάθε μονάδα Ryzen AI Halo στο διακόπτη Ethernet χρησιμοποιώντας καλώδιο Cat 7 (ή υψηλότερο). Αυτό δημιουργεί τη σύνδεση 10Gbps που χρησιμοποιείται για επικοινωνία υψηλής ταχύτητας μεταξύ των κόμβων.
<!-- @os:linux -->
### 1. Προσδιορισμός Διεπαφών Δικτύου

Σε κάθε μηχάνημα, βρείτε το όνομα της διεπαφής δικτύου του και σημειώστε το (θα αναφέρεται παρακάτω ως `IFNAME`). Εκτελέστε:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Αυτό εκτυπώνει απευθείας το όνομα της διεπαφής, για παράδειγμα:

```bash
enp191s0
```

### 2. Επαλήθευση Ταχυτήτων Σύνδεσης Δικτύου

Επιβεβαιώστε ότι η σύνδεση είναι ενεργή και εκτελείται με πλήρη ταχύτητα ελέγχοντας την ταχύτητα της διεπαφής σας:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Σημείωση**: Αντικαταστήστε το `<IFNAME>` με το όνομα διεπαφής εξόδου από το [1. Προσδιορισμός Διεπαφών Δικτύου](#1-determine-network-interfaces)

Θα πρέπει να δείτε ταχύτητα `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Σημείωση**: Εάν η ταχύτητα είναι χαμηλότερη από `10000Mb/s` ή η σύνδεση δεν ενεργοποιείται, ελέγξτε τη σύνδεση του καλωδίου και επιβεβαιώστε ότι η θύρα του διακόπτη έχει ρυθμιστεί στα 10Gbps. Ορισμένοι διακόπτες απαιτούν την απενεργοποίηση της αυτόματης διαπραγμάτευσης και τον χειροκίνητο ορισμό της ταχύτητας σύνδεσης· ανατρέξτε στην τεκμηρίωση του διακόπτη σας.

<!-- @os:end -->

<!-- @os:windows -->
### Επαλήθευση Ταχύτητας Σύνδεσης Δικτύου

Σε κάθε μηχάνημα, ελέγξτε την ταχύτητα σύνδεσης των διεπαφών δικτύου σας:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Η διεπαφή Ethernet σας θα πρέπει να είναι `Up` και να εκτελείται στα `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Σημείωση**: Εάν η ταχύτητα είναι χαμηλότερη από `10 Gbps` ή η σύνδεση δεν ενεργοποιείται, ελέγξτε τη σύνδεση του καλωδίου και επιβεβαιώστε ότι η θύρα του διακόπτη έχει ρυθμιστεί στα 10Gbps. Ορισμένοι διακόπτες απαιτούν την απενεργοποίηση της αυτόματης διαπραγμάτευσης και τον χειροκίνητο ορισμό της ταχύτητας σύνδεσης· ανατρέξτε στην τεκμηρίωση του διακόπτη σας.

<!-- @os:end -->

## Εγκατάσταση του llama.cpp

> **Σημείωση**: Ολοκληρώστε αυτό το βήμα και στα τέσσερα μηχανήματα (Μηχάνημα 1 έως Μηχάνημα 4).

Υπάρχουν διαθέσιμες δύο επιλογές εγκατάστασης:

- [Επιλογή 1: Lemonade SDK (Συνιστάται)](#option-1-lemonade-sdk-recommended) - προ-χτισμένα δυαδικά αρχεία (binaries), ταχύτερη ρύθμιση
- [Επιλογή 2: Χειροκίνητη Δόμηση από Πηγαίο Κώδικα](#option-2-manual-source-build) - δόμηση από τον πηγαίο κώδικα με πλήρη έλεγχο στις σημαίες δόμησης (build flags)
### Επιλογή 1: Lemonade SDK (Προτείνεται)

Το Lemonade SDK παρέχει νυχτερινές εκδόσεις (nightly builds) του llama.cpp με επιτάχυνση AMD ROCm 7, στοχεύοντας GPU όπως το gfx1151 (Strix Halo / Ryzen AI Max+ 395) και άλλες πρόσφατες αρχιτεκτονικές Radeon.

<!-- @os:windows -->
#### Βήμα 1: Λήψη των Προκατασκευασμένων Δυαδικών Αρχείων

Μεταβείτε στη σελίδα της τελευταίας έκδοσης και κατεβάστε το αρχείο που αντιστοιχεί στην πλατφόρμα και τον στόχο GPU σας:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Κατεβάστε το αρχείο με το όνομα `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (όπου `xxxx` είναι ο αριθμός έκδοσης).

#### Βήμα 2: Αποσυμπίεση των Δυαδικών Αρχείων

Αποσυμπιέστε το ληφθέν αρχείο:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Αυτός ο φάκελος περιέχει πλέον εκδόσεις των `llama-cli.exe`, `llama-server.exe` και `ggml-rpc-server.exe` με ενεργοποιημένο το ROCm, προμεταγλωττισμένες για το σύστημα Ryzen AI Halo σας.

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

Κατεβάστε το αρχείο με το όνομα `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (όπου `xxxx` είναι ο αριθμός έκδοσης).

#### Βήμα 2: Αποσυμπίεση και Προετοιμασία των Δυαδικών Αρχείων

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Αυτός ο φάκελος περιέχει πλέον εκδόσεις των `llama-cli`, `llama-server` και `rpc-server` με ενεργοποιημένο το ROCm, προμεταγλωττισμένες για το σύστημα Ryzen AI Halo σας.

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
Αφού το llama.cpp έχει προετοιμαστεί σε κάθε κόμβο, προχωρήστε στην ενότητα [Λήψη του Μοντέλου](#downloading-the-model).

### Επιλογή 2: Χειροκίνητη Μεταγλώττιση από τον Πηγαίο Κώδικα

<!-- @os:windows -->
#### Βήμα 1: Μεταγλώττιση του llama.cpp

Ανοίξτε το **x64 Native Tools Command Prompt** (εγκαθίσταται μαζί με τα Visual Studio Build Tools) και κλωνοποιήστε το αποθετήριο:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Προσθέστε το HIP στη διαδρομή σας και μεταγλωττίστε με υποστήριξη ROCm και RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Σημαία Μεταγλώττισης | Σκοπός |
|-----------|---------|
| `-DGGML_HIP=ON` | Ενεργοποιεί τη στοίβα λογισμικού ROCm/HIP |
| `-DGGML_RPC=ON` | Ενεργοποιεί το RPC για κατανεμημένη εξαγωγή συμπερασμάτων (inference) |
| `-DGPU_TARGETS=gfx1151` | Στοχεύει το GPU Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Χρησιμοποιεί το σύστημα μεταγλώττισης Ninja |

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

Το παραπάνω βήμα μεταγλώττισης όρισε το `%HIP_PATH%\bin` μόνο για την τρέχουσα συνεδρία. Για να διαθέσετε τις βιβλιοθήκες HIP σε οποιοδήποτε τερματικό (όχι μόνο στο x64 Native Tools Command Prompt), προσθέστε το μόνιμα στο `PATH` χρήστη σας:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Αφού το llama.cpp έχει προετοιμαστεί σε κάθε κόμβο, προχωρήστε στην ενότητα [Λήψη του Μοντέλου](#downloading-the-model).
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
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Σημαία Μεταγλώττισης | Σκοπός |
|-----------|---------|
| `-DGGML_HIP=ON` | Ενεργοποιεί τη στοίβα λογισμικού ROCm |
| `-DGGML_RPC=ON` | Ενεργοποιεί το RPC για κατανεμημένη εξαγωγή συμπερασμάτων (inference) |
| `-DAMDGPU_TARGETS="gfx1151"` | Στοχεύει το GPU Ryzen AI Halo (Radeon 8060s) |

Για περισσότερες επιλογές μεταγλώττισης, ανατρέξτε στην [τεκμηρίωση μεταγλώττισης του llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

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

Αφού το llama.cpp έχει προετοιμαστεί σε κάθε κόμβο, προχωρήστε στην ενότητα [Λήψη του Μοντέλου](#downloading-the-model).
<!-- @os:end -->

## Λήψη του Μοντέλου

Αυτό το playbook χρησιμοποιεί το [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) στην κβαντισμένη μορφή `UD-Q2_K_XL` από το [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL). Αυτή η κβαντισμένη μορφή χωράει εντός της συνολικής μνήμης GPU τεσσάρων κόμβων Ryzen AI Halo.

Κατεβάστε τα αρχεία GGUF χρησιμοποιώντας το Hugging Face CLI:
<!-- @os:linux -->
```bash
pip install huggingface-hub
hf download unsloth/Kimi-K2.6-GGUF --include "UD-Q2_K_XL/*" --local-dir Kimi-K2.6-GGUF
```
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/Kimi-K2.6-GGUF --include "UD-Q2_K_XL/*" --local-dir Kimi-K2.6-GGUF
```
<!-- @os:end -->

> **Σημείωση**: Η λήψη του μοντέλου πρέπει να ολοκληρωθεί στο Μηχάνημα 1 (τον ελεγκτή). Οι κόμβοι εργασίας RPC (Μηχανήματα 2, 3 και 4) δεν χρειάζονται τοπικό αντίγραφο των αρχείων μοντέλου.

## Εκκίνηση του Μοντέλου στο Σύμπλεγμα (Cluster)

Η μηχανή RPC (Remote Procedure Call) του llama.cpp επιτρέπει σε ένα μεμονωμένο στιγμιότυπο llama.cpp να μεταφέρει επίπεδα του μοντέλου σε απομακρυσμένους κόμβους εργασίας μέσω δικτύου. Ένα μηχάνημα λειτουργεί ως **ελεγκτής** (Μηχάνημα 1), διαχειριζόμενο την κωδικοποίηση σε tokens, τον προγραμματισμό και την ενορχήστρωση. Τα άλλα τρία μηχανήματα εκτελούν το καθένα έναν ελαφρύ **διακομιστή RPC** (Μηχανήματα 2, 3 και 4) που εκθέτει τη μνήμη και την υπολογιστική ισχύ του GPU τους στον ελεγκτή.

Κατά τη στιγμή της φόρτωσης, το llama.cpp κατατμεί το μοντέλο σε όλους τους τέσσερις κόμβους. Μόλις φορτωθεί, η εξαγωγή συμπερασμάτων (inference) προχωρά σαν να εκτελείται σε έναν μόνο επιταχυντή. Το RPC χειρίζεται τις μεταφορές τανυστών (tensor) και τον συγχρονισμό στο παρασκήνιο.

### Βήμα 1: Εκκίνηση των Διακομιστών RPC (Μηχανήματα 2, 3 και 4)

Σε καθένα από τα Μηχανήματα 2, 3 και 4, εκκινήστε τον διακομιστή RPC για να εκθέσετε τους πόρους GPU του στον ελεγκτή:
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
| `-p` | Θύρα στην οποία θα μεταδίδεται ο διακομιστής RPC |
| `-c` | Ενεργοποιεί μια τοπική προσωρινή μνήμη (cache) για μεγάλους τανυστές (tensors), αποφεύγοντας επαναλαμβανόμενες μεταφορές δικτύου κατά τη φόρτωση του μοντέλου |
| `--host` | Διεύθυνση IP στην οποία θα συνδεθεί ο διακομιστής RPC (`0.0.0.0` για όλες τις διεπαφές) |

Για περισσότερες επιλογές, ανατρέξτε στην [τεκμηρίωση RPC του llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Βήμα 2: Εκκίνηση του Μοντέλου (Μηχάνημα 1)

Με τους διακομιστές RPC να εκτελούνται στα Μηχανήματα 2, 3 και 4, εκκινήστε την εξαγωγή συμπερασμάτων (inference) από το Μηχάνημα 1 χρησιμοποιώντας είτε το `llama-cli` είτε το `llama-server`.
#### llama-cli

Το `llama-cli` παρέχει μια διεπαφή βασισμένη σε τερματικό για απευθείας αλληλεπίδραση με το μοντέλο. Είναι ιδανικό για benchmarking, αποσφαλμάτωση και πειραματισμό χαμηλού επιπέδου.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/Kimi-K2.6-GGUF/UD-Q2_K_XL/Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  -b 4096 \
  -ub 4096 \
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **Εύρεση `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Σε καθένα από τα Μηχανήματα 2, 3 και 4, εκτελέστε `hostname -I | awk '{print $1}'` για να βρείτε τη δική του τοπική διεύθυνση IP.
<!-- @os:end -->

<!-- @os:windows -->
> **Σημείωση**: Εκτελέστε αυτήν την εντολή σε Terminal (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\Kimi-K2.6-GGUF\UD-Q2_K_XL\Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  -b 4096 `
  -ub 4096 `
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **Εύρεση `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Σε καθένα από τα Μηχανήματα 2, 3 και 4, εκτελέστε `ipconfig | findstr /C:"IPv4"` σε Terminal (Powershell) για να βρείτε τη δική του τοπική διεύθυνση IP.

<!-- @os:end -->

Μόλις ξεκινήσει η εκτέλεση, το `llama-cli` εμφανίζει την πρόοδο φόρτωσης του μοντέλου και εισέρχεται σε μια διαδραστική προτροπή όπου μπορείτε να συνομιλήσετε απευθείας με το μοντέλο:

![llama-cli εκτελώντας το Kimi K2.6 σε τέσσερις κόμβους](assets/llama-cli-example.png)

#### llama-server

Το `llama-server` εκθέτει την ίδια μηχανή συμπερασμού μέσω μιας μόνιμης διεργασίας διακομιστή με ενσωματωμένο web UI και ένα HTTP API συμβατό με OpenAI. Αυτή είναι η προτιμώμενη διεπαφή για αναπτύξεις μεγαλύτερης διάρκειας, πρόσβαση από πολλούς χρήστες και ενσωμάτωση με εξωτερικά εργαλεία.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/Kimi-K2.6-GGUF/UD-Q2_K_XL/Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  -b 4096 \
  -ub 4096 \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **Εύρεση `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Σε καθένα από τα Μηχανήματα 2, 3 και 4, εκτελέστε `hostname -I | awk '{print $1}'` για να βρείτε τη δική του τοπική διεύθυνση IP.
<!-- @os:end -->

<!-- @os:windows -->
> **Σημείωση**: Εκτελέστε αυτήν την εντολή σε Terminal (Powershell).

```powershell
.\llama-server.exe `
  -m C:\path\to\Kimi-K2.6-GGUF\UD-Q2_K_XL\Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  -b 4096 `
  -ub 4096 `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **Εύρεση `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Σε καθένα από τα Μηχανήματα 2, 3 και 4, εκτελέστε `ipconfig | findstr /C:"IPv4"` σε Terminal (Powershell) για να βρείτε τη δική του τοπική διεύθυνση IP.
<!-- @os:end -->

Μόλις ξεκινήσει, ανοίξτε το `http://<HOST_IP>:8081` στο πρόγραμμα περιήγησής σας για να αποκτήσετε πρόσβαση στο ενσωματωμένο web UI. Αυτό παρέχει μια διεπαφή συνομιλίας βασισμένη σε πρόγραμμα περιήγησης για αλληλεπίδραση με το μοντέλο:

![llama-server web UI εκτελώντας το Kimi K2.6 σε τέσσερις κόμβους](assets/llama-server-example.png)

<!-- @os:linux -->
> **Εύρεση `<HOST_IP>`**: Στο Μηχάνημα 1, εκτελέστε `hostname -I | awk '{print $1}'` για να βρείτε τη δική του τοπική διεύθυνση IP.
<!-- @os:end -->

<!-- @os:windows -->
> **Εύρεση `<HOST_IP>`**: Στο Μηχάνημα 1, εκτελέστε `ipconfig | findstr /C:"IPv4"` σε Terminal (Powershell) για να βρείτε τη δική του τοπική διεύθυνση IP.
<!-- @os:end -->

#### Αναφορά Παραμέτρων

| Σημαία | Σκοπός |
|------|---------|
| `-m` | Διαδρομή προς το αρχείο μοντέλου GGUF (χρησιμοποιήστε το πρώτο shard, `00001-of-00008`) |
| `-c` | Μέγεθος context σε tokens. Μεγαλύτερες τιμές χρησιμοποιούν περισσότερη μνήμη |
| `-fa on` | Ενεργοποιεί το rocWMMA Flash Attention για βελτιωμένη απόδοση σε GPU της AMD |
| `-ngl 999` | Μεταφέρει όλα τα layers του μοντέλου στην GPU |
| `-lm none` | Ορίζει τη λειτουργία φόρτωσης μοντέλου σε `none`, απενεργοποιώντας το memory-mapping για μείωση του χρόνου φόρτωσης όταν το μέγεθος του μοντέλου υπερβαίνει τη RAM του συστήματος αλλά χωράει στη VRAM |
| `-b` | Λογικό μέγεθος batch σε tokens. Η ρύθμιση σε 4096 εξισορροπεί την απόδοση και τη χρήση μνήμης μεταξύ των κόμβων |
| `-ub` | Φυσικό (micro) μέγεθος batch για επεξεργασία prompt. Η αντιστοίχιση με το `-b` αποφεύγει περιττό overhead τμηματοποίησης |
| `--host` | Διεύθυνση IP στην οποία θα συνδεθεί το `llama-server` (μόνο για `llama-server`) |
| `--port` | Θύρα για την εξυπηρέτηση του HTTP API (μόνο για `llama-server`) |
| `--rpc` | Λίστα endpoints εργατών RPC (`IP:port`) χωρισμένη με κόμματα |

Για πλήρη χρήση παραμέτρων, ανατρέξτε στην [τεκμηρίωση του llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) και την [τεκμηρίωση του llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Επόμενα Βήματα

- **Σύνδεση εφαρμογών τρίτων**: Το `llama-server` εκθέτει ένα API συμβατό με OpenAI. Κατευθύνετε οποιαδήποτε εφαρμογή συμβατή με OpenAI (όπως το Open WebUI) στο `http://<HOST_IP>:8081` με οποιοδήποτε εικονικό κλειδί API (π.χ., `none`) για να συνδεθείτε στο cluster σας
- **Εξερεύνηση άλλων μοντέλων**: Περιηγηθείτε σε κβαντισμένα GGUF στο [Hugging Face](https://huggingface.co/models?search=gguf) για να βρείτε μοντέλα που χωράνε στη συνολική μνήμη GPU του cluster σας
- **Επέκταση πέρα από τέσσερις κόμβους**: Προσθέστε επιπλέον συστήματα Ryzen AI Halo ως επιπλέον εργάτες RPC για πρόσβαση σε μοντέλα πέρα από την κλίμακα του 1 τρισεκατομμυρίου παραμέτρων. Περάστε επιπλέον endpoints στο `--rpc` ως λίστα χωρισμένη με κόμματα (π.χ., `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)