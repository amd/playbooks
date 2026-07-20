<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configurazione della piattaforma

Questo documento descrive le configurazioni della piattaforma previste per l'esecuzione di questo playbook.

## App/Framework richiesti

### Windows/Linux

GAIA dovrebbe essere pre-installato seguendo le istruzioni fornite nella [Guida all'installazione di GAIA](../../dependencies/gaia.md).

Lemonade Server dovrebbe essere pre-installato seguendo le istruzioni fornite nella [Guida all'installazione di Lemonade](../../dependencies/lemonade.md).

## Modelli richiesti

### Windows/Linux

L'Hardware Advisor Agent utilizza **Qwen3-Coder-30B** per il ragionamento dell'agente. Questo modello viene scaricato automaticamente durante `gaia init`. Non è richiesto alcun download manuale dei modelli.