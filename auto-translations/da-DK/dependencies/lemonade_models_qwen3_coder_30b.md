<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Download af Qwen3-Coder 30B A3B til Lemonade

Lemonade-serveren serverer Qwen3-Coder 30B A3B-modellen (`Qwen3-Coder-30B-A3B-Instruct-GGUF`). For at downloade den på forhånd:

```bash
lemonade pull Qwen3-Coder-30B-A3B-Instruct-GGUF
```

`lemonade run Qwen3-Coder-30B-A3B-Instruct-GGUF` downloader også modellen ved første brug, hvis den endnu ikke findes, og indlæser den derefter til inferens.

Modellen vises på Lemonade-serverens liste over downloadede modeller, når download er fuldført; tjekene nedenfor bekræfter, at den findes på maskinen.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-coder-30b-a3b-instruct-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-Coder-30B-A3B-Instruct-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-qwen3-coder-30b-a3b-instruct-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Qwen3-Coder-30B-A3B-Instruct-GGUF
```
<!-- @test:end -->
<!-- @os:end -->