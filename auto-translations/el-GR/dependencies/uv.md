<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Εγκατάσταση του uv

Το [uv](https://docs.astral.sh/uv/) είναι ο διαχειριστής πακέτων/περιβαλλόντων Python που χρησιμοποιεί το Agent Canvas για να δημιουργήσει το περιβάλλον του agent-server του. Εγκαταστήστε το με το επίσημο script:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Το `uv` εγκαθίσταται στο `~/.local/bin`· βεβαιωθείτε ότι αυτός ο κατάλογος βρίσκεται στο `PATH` σας.

<!-- @os:linux -->
<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->