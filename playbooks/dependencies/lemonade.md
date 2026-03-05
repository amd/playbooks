### Lemonade

#### Installing Lemonade

Download and install Lemonade Server from [lemonade-server.ai](https://lemonade-server.ai).

#### Starting Lemonade

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-gpt-oss-120b timeout=1200 hidden=True -->
```powershell
lemonade-server --version
winget upgrade -e --id AMD.LemonadeServer
lemonade-server --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->

1. Open PowerShell or Command Prompt
2. Start Lemonade with gpt-oss-120b:
```cmd
lemonade-server run gpt-oss-120b-mxfp4-GGUF
```

The server starts on `http://localhost:8000` with an OpenAI-compatible API at `/api/v1`.

<!-- @os:end -->

<!-- @os:linux -->

Start Lemonade with gpt-oss-120b and ROCm backend:
```bash
lemonade-server run gpt-oss-120b-mxfp4-GGUF --llamacpp rocm
```

The server starts on `http://localhost:8000` with an OpenAI-compatible API at `/api/v1`.

> **Tip**: Use `lemonade-server list` to see available models, or `lemonade-server pull <MODEL_NAME>` to download new ones.

<!-- @os:end -->
