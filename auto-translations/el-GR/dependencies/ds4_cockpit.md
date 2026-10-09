<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

Εγκατάσταση του ds4-cockpit

Το [ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) είναι ένα ελαφρύ τερματικό UI που αναλαμβάνει τη δημιουργία containers toolbox, τη λήψη βαρών μοντέλων και την εκκίνηση διακομιστών. Εγκαταστήστε το με `pipx`:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

Το `pipx` εγκαθιστά το entry point στο `~/.local/bin`· βεβαιωθείτε ότι ο συγκεκριμένος κατάλογος βρίσκεται στο `PATH` σας.

<!-- @os:linux -->
<!-- @test:id=ds4-cockpit-installed-linux timeout=60 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
command -v ds4-cockpit
```
<!-- @test:end -->
<!-- @os:end -->