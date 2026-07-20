<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Instalando o Lemonade

<!-- @os:windows -->
Baixe o instalador mais recente em [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) e execute o arquivo `.msi`. 

Após a instalação:
- O CLI `lemonade` é adicionado automaticamente ao PATH do sistema
- O servidor Lemonade é executado automaticamente em segundo plano

Você também pode instalar silenciosamente pela linha de comando:
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


#### Verificando a instalação do Lemonade

Abra um terminal e execute:
```bash
lemonade --version
```

Você deverá ver uma saída semelhante a:
```
lemonade version x.y.z
```

Se você vir um número de versão, o Lemonade está instalado corretamente e pronto para uso.

Para referência rápida, aqui estão alguns comandos comuns do CLI do Lemonade:

| Comando | O que faz |
| --- | --- |
| `lemonade --help` | Mostra todos os comandos e flags disponíveis. |
| `lemonade --version` | Exibe a versão instalada do Lemonade. |
| `lemonade status` | Confirma se o servidor Lemonade está em execução e acessível. A URL base padrão da API compatível com OpenAI é `http://localhost:13305/api/v1`. |
| `lemonade list` | Lista os modelos disponíveis na sua configuração do Lemonade. |
| `lemonade pull <MODEL_NAME>` | Baixa um modelo sem iniciá-lo. |
| `lemonade run <MODEL_NAME>` | Baixa o modelo, se necessário, e o inicia para inferência/chat. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | Inicia um modelo llama.cpp com o backend ROCm. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Inicia um modelo llama.cpp com o backend Vulkan. |
| `lemonade config` | Exibe os valores de configuração atuais do Lemonade. |
| `lemonade config set llamacpp.backend=rocm` | Define o backend padrão do llama.cpp como ROCm. |

Para obter as opções mais recentes do servidor Lemonade ou solução de problemas, consulte a [documentação oficial do Lemonade](https://lemonade-server.ai/docs/lemonade-cli/).