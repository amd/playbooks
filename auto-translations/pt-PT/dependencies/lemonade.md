<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Instalar o Lemonade

<!-- @os:windows -->
Transfira o instalador mais recente em [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) e execute o ficheiro `.msi`. 

Após a instalação:
- O CLI `lemonade` é adicionado automaticamente ao PATH do sistema
- Espera-se que o servidor Lemonade seja executado automaticamente em segundo plano

Também pode instalar em modo silencioso a partir da linha de comandos:
```cmd
msiexec /i lemonade-server-minimal.msi /qn
```
<!-- @os:end -->

<!-- @os:linux -->
**Ubuntu:**
```bash
sudo add-apt-repository ppa:lemonade-team/stable
sudo apt install lemonade-server
```

**Arch Linux (AUR):**
```bash
yay -S lemonade-server
```

Para outras distribuições ou para instalar a partir do código-fonte, consulte as [opções completas de instalação](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:end -->


#### Verificar a instalação do Lemonade

Abra um terminal e execute:
```bash
lemonade --version
```

Deverá ver um resultado semelhante a:
```
lemonade version x.y.z
```

Se vir um número de versão, o Lemonade está instalado corretamente e pronto a utilizar.

Para referência rápida, aqui estão alguns comandos comuns do CLI do Lemonade:

| Comando | O que faz |
| --- | --- |
| `lemonade --help` | Mostra todos os comandos e flags disponíveis. |
| `lemonade --version` | Mostra a versão instalada do Lemonade. |
| `lemonade status` | Confirma se o servidor Lemonade está em execução e acessível. O URL base da API compatível com OpenAI predefinido é `http://localhost:13305/api/v1`. |
| `lemonade list` | Lista os modelos disponíveis na sua configuração do Lemonade. |
| `lemonade pull <MODEL_NAME>` | Transfere um modelo sem o iniciar. |
| `lemonade run <MODEL_NAME>` | Transfere o modelo, se necessário, e depois inicia-o para inferência/chat. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | Inicia um modelo llama.cpp com o backend ROCm. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Inicia um modelo llama.cpp com o backend Vulkan. |
| `lemonade config` | Mostra os valores de configuração atuais do Lemonade. |
| `lemonade config set llamacpp.backend=rocm` | Define o backend llama.cpp predefinido como ROCm. |

Para as opções mais recentes do servidor Lemonade ou para resolução de problemas, consulte a [documentação oficial do Lemonade](https://lemonade-server.ai/docs/lemonade-cli/).