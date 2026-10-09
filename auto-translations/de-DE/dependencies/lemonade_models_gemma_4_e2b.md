<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Herunterladen von Gemma-4 E2B für Lemonade

Der Lemonade-Server stellt das Gemma-4-E2B-Modell (`Gemma-4-E2B-it-GGUF`) bereit. Um es im Voraus herunterzuladen:

```bash
lemonade pull Gemma-4-E2B-it-GGUF
```

`lemonade run Gemma-4-E2B-it-GGUF` lädt das Modell bei der ersten Verwendung ebenfalls automatisch herunter, falls es noch nicht vorhanden ist, und lädt es anschließend für die Inferenz.

Das Modell erscheint in der Liste der heruntergeladenen Modelle des Lemonade-Servers, sobald der Pull abgeschlossen ist; die folgenden Prüfungen bestätigen, dass es auf dem Rechner vorhanden ist.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-gemma-4-e2b-it-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Gemma-4-E2B-it-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-gemma-4-e2b-it-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Gemma-4-E2B-it-GGUF
```
<!-- @test:end -->
<!-- @os:end -->