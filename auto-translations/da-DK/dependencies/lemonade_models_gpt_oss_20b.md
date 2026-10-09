<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Download af GPT-OSS 20B til Lemonade

Lemonade-serveren leverer GPT-OSS 20B MXFP4 GGUF-modellen (`gpt-oss-20b-mxfp4-GGUF`). Sådan downloader du den på forhånd:

```bash
lemonade pull gpt-oss-20b-mxfp4-GGUF
```

`lemonade run gpt-oss-20b-mxfp4-GGUF` downloader også modellen ved første brug, hvis den ikke allerede er til stede, og indlæser den derefter til inferens.

Modellen vises på Lemonade-serverens liste over downloadede modeller, så snart hentningen er fuldført; nedenstående kontroller bekræfter, at den er til stede på maskinen.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-gpt-oss-20b-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:gpt-oss-20b-mxfp4-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-gpt-oss-20b-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q gpt-oss-20b-mxfp4-GGUF
```
<!-- @test:end -->
<!-- @os:end -->