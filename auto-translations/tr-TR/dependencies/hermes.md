<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Hermes'in Kurulumu

Hermes ajan CLI'sini resmi yükleyiciyle kurun. `--skip-setup` bayrağı, kurulumun gözetimsiz kalmasını sağlar:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Hermes, `~/.local/bin` dizinine kurulur; bu dizinin `PATH` değişkeninizde olduğundan emin olun.

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->