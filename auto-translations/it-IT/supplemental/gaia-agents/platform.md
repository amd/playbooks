<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configurazione della Piattaforma

Questo documento descrive le configurazioni di piattaforma previste per l'esecuzione di questo playbook.

## App/Framework Richiesti

### Windows/Linux

GAIA deve essere pre-installato seguendo le istruzioni fornite nella [Guida all'Installazione di GAIA](../../dependencies/gaia.md).

Lemonade Server deve essere pre-installato seguendo le istruzioni fornite nella [Guida all'Installazione di Lemonade](../../dependencies/lemonade.md).

## Modelli Richiesti

### Windows/Linux

L'Hardware Advisor Agent utilizza **Qwen3-Coder-30B** per il ragionamento dell'agente. Questo modello viene scaricato automaticamente durante `gaia init`. Non sono richiesti download manuali di modelli.