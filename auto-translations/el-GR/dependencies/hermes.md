<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Εγκατάσταση του Hermes

Εγκαταστήστε το Hermes agent CLI με τον επίσημο installer. Η σημαία `--skip-setup` διατηρεί την εγκατάσταση χωρίς επίβλεψη:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Το Hermes εγκαθίσταται στο `~/.local/bin`· βεβαιωθείτε ότι αυτός ο φάκελος βρίσκεται στο `PATH` σας.

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->