<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Inštalácia Hermes

Nainštalujte agenta Hermes CLI pomocou oficiálneho inštalátora. Príznak `--skip-setup` zabezpečí, že inštalácia prebehne bez zásahu používateľa:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Hermes sa nainštaluje do `~/.local/bin`; uistite sa, že tento adresár je zahrnutý vo vašej premennej `PATH`.

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->