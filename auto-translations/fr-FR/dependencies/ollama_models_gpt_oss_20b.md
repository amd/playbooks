<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Téléchargement de GPT-OSS 20B pour Ollama

Récupérez le modèle GPT-OSS 20B dans Ollama :

```bash
ollama pull gpt-oss:20b
```

Le serveur Ollama doit être en cours d'exécution pour que la récupération réussisse ; `ollama serve` le démarre s'il n'est pas déjà lancé.

Confirmez que le modèle est présent :

```bash
ollama list
```

Vous devriez voir `gpt-oss:20b` dans la sortie, accompagné de sa taille et de sa date de dernière modification.

<!-- @os:linux -->
<!-- @test:id=ollama-model-present-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
ollama list | grep -q 'gpt-oss:20b'
```
<!-- @test:end -->
<!-- @os:end -->