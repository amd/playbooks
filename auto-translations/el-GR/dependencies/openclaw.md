<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Εγκατάσταση του OpenClaw

Εγκαταστήστε το OpenClaw χρησιμοποιώντας τον επίσημο installer:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Οι σημαίες `--no-prompt --no-onboard` παρακάμπτουν τον διαδραστικό οδηγό ρύθμισης, κάτι που απαιτείται για ανεπίβλεπτες εγκαταστάσεις· το backend του μοντέλου ρυθμίζεται ξεχωριστά.

> **Συμβουλή:** Αν εμφανιστεί το μήνυμα `command not found` μετά την εγκατάσταση, προσθέστε τον global bin κατάλογο του npm στο PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Για να το κάνετε αυτό μόνιμο, προσθέστε την παραπάνω γραμμή στο αρχείο `~/.bashrc` ή `~/.zshrc`.

<!-- @os:linux -->
<!-- @test:id=openclaw-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
openclaw --version
```
<!-- @test:end -->
<!-- @os:end -->