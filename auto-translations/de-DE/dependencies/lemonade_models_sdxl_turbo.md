<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Herunterladen von SDXL-Turbo für Lemonade

Der Lemonade-Server stellt das Modell SDXL-Turbo (`SDXL-Turbo`) bereit. So laden Sie es im Voraus herunter:

```bash
lemonade pull SDXL-Turbo
```

`lemonade run SDXL-Turbo` lädt das Modell bei der ersten Verwendung ebenfalls automatisch herunter, falls es noch nicht vorhanden ist, und lädt es anschließend für die Inferenz.

Das Modell erscheint in der Liste der heruntergeladenen Modelle des Lemonade-Servers, sobald der Download abgeschlossen ist; die folgenden Prüfungen bestätigen, dass es auf dem Rechner vorhanden ist.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-sdxl-turbo-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:SDXL-Turbo
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-sdxl-turbo-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q SDXL-Turbo
```
<!-- @test:end -->
<!-- @os:end -->