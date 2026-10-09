<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Εγκατάσταση του OpenClaw

Εγκαταστήστε το OpenClaw με τον επίσημο εγκαταστάτη:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Οι σημαίες `--no-prompt --no-onboard` παρακάμπτουν τον διαδραστικό οδηγό ρύθμισης, κάτι που είναι απαραίτητο για μη επιτηρούμενες εγκαταστάσεις· το backend μοντέλου ρυθμίζεται ξεχωριστά.

> **Συμβουλή:** Αν δείτε `command not found` μετά την εγκατάσταση, προσθέστε τον καθολικό φάκελο bin του npm στο PATH:
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