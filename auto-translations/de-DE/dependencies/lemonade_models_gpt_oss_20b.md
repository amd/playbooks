<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Herunterladen von GPT-OSS 20B für Lemonade

Der Lemonade-Server stellt das GPT-OSS 20B MXFP4 GGUF-Modell (`gpt-oss-20b-mxfp4-GGUF`) bereit. Um es im Voraus herunterzuladen:

```bash
lemonade pull gpt-oss-20b-mxfp4-GGUF
```

`lemonade run gpt-oss-20b-mxfp4-GGUF` lädt das Modell bei der ersten Verwendung ebenfalls automatisch herunter, falls es noch nicht vorhanden ist, und lädt es anschließend für die Inferenz.

Das Modell erscheint in der Liste der heruntergeladenen Modelle des Lemonade-Servers, sobald der Download abgeschlossen ist; die folgenden Prüfungen bestätigen, dass es auf dem Rechner vorhanden ist.

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