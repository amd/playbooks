<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Herunterladen von Qwen3-Coder 30B A3B für Lemonade

Der Lemonade-Server stellt das Qwen3-Coder 30B A3B Modell (`Qwen3-Coder-30B-A3B-Instruct-GGUF`) bereit. Um es im Voraus herunterzuladen:

```bash
lemonade pull Qwen3-Coder-30B-A3B-Instruct-GGUF
```

`lemonade run Qwen3-Coder-30B-A3B-Instruct-GGUF` lädt das Modell bei der ersten Verwendung ebenfalls automatisch herunter, falls es noch nicht vorhanden ist, und lädt es anschließend für die Inferenz.

Das Modell erscheint in der Liste der heruntergeladenen Modelle des Lemonade-Servers, sobald der Download abgeschlossen ist; die folgenden Prüfungen bestätigen, dass es auf dem Rechner vorhanden ist.

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