<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Ollama用GPT-OSS 20Bのダウンロード

GPT-OSS 20BモデルをOllamaにプルします:

```bash
ollama pull gpt-oss:20b
```

プルを成功させるにはOllamaサーバーが起動している必要があります。まだ起動していない場合は`ollama serve`で起動できます。

モデルが存在することを確認します:

```bash
ollama list
```

出力に`gpt-oss:20b`がそのサイズと最終更新日とともに表示されるはずです。

<!-- @os:linux -->
<!-- @test:id=ollama-model-present-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
ollama list | grep -q 'gpt-oss:20b'
```
<!-- @test:end -->
<!-- @os:end -->