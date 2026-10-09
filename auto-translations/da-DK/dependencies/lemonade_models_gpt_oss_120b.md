<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Download af GPT-OSS 120B til Lemonade

Lemonade-serveren serverer GPT-OSS 120B MXFP4 GGUF-modellen (`gpt-oss-120b-mxfp-GGUF`). Sådan downloader du den på forhånd:

```bash
lemonade pull gpt-oss-120b-mxfp-GGUF
```

`lemonade run gpt-oss-120b-mxfp-GGUF` downloader også modellen ved første brug, hvis den ikke allerede findes, og indlæser den derefter til inferens.

Modellen vises på listen over downloadede modeller i Lemonade-serveren, når download er fuldført; tjekkene nedenfor bekræfter, at den findes på maskinen.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-gpt-oss-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:gpt-oss-120b-mxfp-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-gpt-oss-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q gpt-oss-120b-mxfp-GGUF
```
<!-- @test:end -->
<!-- @os:end -->