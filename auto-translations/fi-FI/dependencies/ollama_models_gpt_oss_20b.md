<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### GPT-OSS 20B -mallin lataaminen Ollamaa varten

Lataa GPT-OSS 20B -malli Ollamaan:

```bash
ollama pull gpt-oss:20b
```

Ollama-palvelimen on oltava käynnissä, jotta lataus onnistuu; komento `ollama serve` käynnistää sen, jos se ei ole jo käynnissä.

Vahvista, että malli on saatavilla:

```bash
ollama list
```

Tulosteessa pitäisi näkyä `gpt-oss:20b` sekä sen koko ja viimeisin muokkauspäivämäärä.

<!-- @os:linux -->
<!-- @test:id=ollama-model-present-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
ollama list | grep -q 'gpt-oss:20b'
```
<!-- @test:end -->
<!-- @os:end -->