<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Herunterladen von Qwen3 4B Hybrid für Lemonade

Der Lemonade-Server stellt das Modell Qwen3 4B Hybrid (`Qwen3-4B-Hybrid`) bereit, das auf der NPU und GPU von Ryzen AI-Prozessoren läuft. Um es im Voraus herunterzuladen:

```powershell
lemonade pull Qwen3-4B-Hybrid
```

Das Modell erscheint in der Liste der heruntergeladenen Modelle des Lemonade-Servers, sobald der Pull-Vorgang abgeschlossen ist; die folgende Überprüfung bestätigt, dass es auf dem Rechner vorhanden ist.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-4b-hybrid-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-4B-Hybrid
```
<!-- @test:end -->
<!-- @os:end -->