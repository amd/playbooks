<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### uv Kurulumu

[uv](https://docs.astral.sh/uv/), Agent Canvas'ın agent sunucusu ortamını oluşturmak için kullandığı Python paket/ortam yöneticisidir. Resmi betik ile kurun:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`uv`, `~/.local/bin` dizinine kurulur; bu dizinin `PATH` değişkeninizde olduğundan emin olun.

<!-- @os:linux -->
<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->