<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Εγκατάσταση του Agent Canvas

Το [Agent Canvas](https://github.com/OpenHands/agent-canvas) είναι το UI/CLI περιήγησης για το OpenHands, το οποίο διανέμεται ως το πακέτο npm `@openhands/agent-canvas`. Απαιτεί **Node.js 24 ή νεότερη έκδοση**. Εγκαταστήστε το καθολικά:

```bash
npm install -g @openhands/agent-canvas
```

Το εκτελέσιμο `agent-canvas` τοποθετείται στον καθολικό φάκελο bin του npm (π.χ. `~/.npm-global/bin`)· βεβαιωθείτε ότι αυτός ο κατάλογος βρίσκεται στο `PATH` σας.

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->