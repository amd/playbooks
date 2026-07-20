# Translation quality report

Automated MQM/GEMBA adequacy+fluency scores (0-100) per locale. No human review.

| Locale | Files | Mean | Min | Judge |
|--------|-------|------|-----|-------|
| ar | 68 | 93.5 | 88 | Claude-Opus-4.8 |
| cs-CZ | 68 | 92.6 | 78 | Claude-Opus-4.8 |
| da-DK | 68 | 93.6 | 88 | Claude-Opus-4.8 |
| de-DE | 68 | 93.8 | 82 | Claude-Opus-4.8 |
| el-GR | 68 | 92.6 | 78 | Claude-Opus-4.8 |
| es-LA | 68 | 94.0 | 78 | Claude-Opus-4.8 |
| fi-FI | 68 | 92.0 | 82 | Claude-Opus-4.8 |
| fr-FR | 68 | 93.0 | 78 | Claude-Opus-4.8 |
| he | 68 | 93.1 | 88 | Claude-Opus-4.8 |
| hu-HU | 68 | 92.2 | 78 | Claude-Opus-4.8 |
| it-IT | 68 | 93.8 | 72 | Claude-Opus-4.8 |
| ja-JP | 68 | 94.1 | 78 | Claude-Opus-4.8 |
| ko-KR | 68 | 94.2 | 82 | Claude-Opus-4.8 |
| nb-NO | 68 | 92.4 | 88 | Claude-Opus-4.8 |
| nl-NL | 68 | 92.6 | 82 | Claude-Opus-4.8 |
| pl-PL | 68 | 93.7 | 78 | Claude-Opus-4.8 |
| pt-BR | 68 | 94.2 | 78 | Claude-Opus-4.8 |
| ro-RO | 68 | 93.6 | 78 | Claude-Opus-4.8 |
| ru-RU | 68 | 93.3 | 88 | Claude-Opus-4.8 |
| sk-SK | 68 | 92.2 | 82 | Claude-Opus-4.8 |
| sl-SI | 68 | 91.1 | 78 | Claude-Opus-4.8 |
| sr-Latn | 68 | 91.7 | 82 | Claude-Opus-4.8 |
| sv-SE | 68 | 93.0 | 78 | Claude-Opus-4.8 |
| th-TH | 68 | 93.6 | 78 | Claude-Opus-4.8 |
| tr-TR | 68 | 92.9 | 82 | Claude-Opus-4.8 |
| uk-UA | 68 | 93.6 | 88 | Claude-Opus-4.8 |
| zh-CN | 68 | 93.0 | 72 | Claude-Opus-4.8 |
| zh-TW | 68 | 93.9 | 82 | Claude-Opus-4.8 |

## Files below 85 (40)

| Locale | File | Score | Issues |
|--------|------|-------|--------|
| it-IT | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 72 | Redundant 'Ottimizzazione fine-tuning'; trademark ™ misplaced from Unsloth to LLM; 'fine-tuned' rendered as generic 'ottimizzati'. |
| zh-CN | playbooks/supplemental/clustering-rccl/playbook.json | 72 | Title awkward 'AMD' added not in source; '聚簇...的RCCL' mistranslates 'Clustering with RCCL'. |
| cs-CZ | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 78 | Trademark symbol misplaced (should be on Unsloth/product name); slight redundancy 'jemné doladění' vs 'doladění'. |
| el-GR | playbooks/supplemental/llama-factory-finetuning/playbook.json | 78 | "Λεπτομερής Συντονισμός" awkward for fine-tuning; "LLaMA-Factory" hyphenation inconsistent with brand; LoRA intact. |
| el-GR | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 78 | Trademark symbol misplaced (should follow Unsloth, not LLM); 'Fine-Tuning' terminology inconsistent between title and body. |
| es-LA | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 78 | Trademark symbol misplaced (should follow Unsloth, not LLM); slightly redundant parenthetical; otherwise accurate and fluent. |
| fr-FR | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 78 | Trademark symbol misplaced (should follow LLMs, not the phrase); terminology inconsistency (Ajustement fin vs affinés). |
| hu-HU | playbooks/supplemental/amd-sync/playbook.json | 78 | Title mistranslates 'AMD Sync' as 'AMD-szinkronizálással' instead of keeping brand name; otherwise accurate and fluent. |
| ja-JP | playbooks/supplemental/speech2speech-translation/playbook.json | 78 | "音声対音声" is awkward; "音声から音声への" or "スピーチ・トゥ・スピーチ" more natural. Otherwise accurate. |
| ja-JP | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 78 | Trademark symbol misplaced; source has 'fine-tuned LLMs™' but translation attaches ™ to Unsloth. |
| pl-PL | playbooks/supplemental/amd-sync/playbook.json | 78 | Title translates 'AMD Sync' as generic 'synchronizacją' instead of keeping brand name; inconsistent with body. |
| pt-BR | playbooks/supplemental/amd-sync/playbook.json | 78 | Title translated 'AMD Sync' as 'sincronização AMD' but kept brand elsewhere; inconsistent brand handling. |
| ro-RO | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 78 | Trademark symbol misplaced (should follow Unsloth, not LLM); awkward phrasing 'ajustate fin cu eficiență a memoriei'. |
| sl-SI | playbooks/supplemental/llama-factory-finetuning/playbook.json | 78 | Awkward 'fino prilagajanje'; parenthetical '(fine-tune)' clutters; 'LLaMA-Factory' hyphen inconsistent with brand. |
| sl-SI | playbooks/supplemental/pytorch-finetuning/playbook.json | 78 | Redundant English glosses in parentheses; 'fino prilagajanje' awkward for fine-tuning, though terms and brands intact. |
| sv-SE | playbooks/supplemental/speech2speech-translation/playbook.json | 78 | Title mistranslates 'speech-to-speech' as 'speech recognition and speech translation'; body is accurate. |
| th-TH | playbooks/core/comfyui-image-gen/playbook.json | 78 | Title mistranslated as progressive 'กำลังสร้าง' (generating in progress) instead of gerund heading; slightly awkward phrasing. |
| cs-CZ | playbooks/supplemental/clustering-rccl/playbook.json | 82 | "Clustrování" awkward neologism; "vícenodový" non-standard (better: víceuzlový). Terminology intact, otherwise fluent and accurate. |
| de-DE | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Inconsistent terminology (Feinabstimmung vs Fine-Tuning); trademark symbol misplaced from original 'fine-tuned LLMs™'. |
| fi-FI | playbooks/supplemental/openclaw-lemonade-server/playbook.json | 82 | Inconsistent brand term: 'Lemonade-palvelimella' vs 'Lemonade Server'; 'OpenClaw-autonominen' compound slightly awkward. |
| fi-FI | playbooks/supplemental/vllm-inference/playbook.json | 82 | 'palvelua' awkward for serving; 'konteinoitua' non-standard term; otherwise accurate and fluent. |
| it-IT | playbooks/supplemental/llama-factory-finetuning/playbook.json | 82 | Title redundant: 'Ottimizzazione fine-tuning' pleonastic; otherwise accurate, fluent, terms intact. |
| it-IT | playbooks/supplemental/speech2speech-translation/playbook.json | 82 | Title omits 'speech-to-speech' nuance; 'voce a voce' slightly awkward but acceptable; overall accurate and fluent. |
| ko-KR | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Inconsistent terminology (파인튜닝 vs 미세 조정); slightly awkward phrasing in second line. |
| nl-NL | playbooks/supplemental/pytorch-finetuning/playbook.json | 82 | Inconsistent terminology: 'Fijnafstemmen' vs 'Verfijn' for fine-tuning; 'Fijnafstemmen' is awkward but acceptable. |
| sk-SK | playbooks/supplemental/amd-sync/playbook.json | 82 | Title mistranslates 'AMD Sync' as 'synchronizáciou AMD' instead of keeping brand name; body correct. |
| sk-SK | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Trademark symbol misplaced (should follow Unsloth, not LLM); otherwise accurate and fluent. |
| sl-SI | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Redundant parenthetical (fine-tuning) repeated; trademark ™ misplaced from 'LLMs' brand context; otherwise accurate, fluent. |
| sr-Latn | playbooks/supplemental/pytorch-kernels/playbook.json | 82 | Inconsistent terminology: 'kernela' vs 'jezgra' for same term; otherwise accurate, fluent, brands intact. |
| th-TH | playbooks/supplemental/cvml/playbook.json | 82 | Title left 'Local Computer Vision' untranslated; otherwise accurate, fluent, terms and brands intact. |
| th-TH | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Trademark symbol misplaced; 'fine-tuned LLMs™' rendered awkwardly; minor fluency loss but meaning preserved. |
| tr-TR | playbooks/supplemental/pytorch-finetuning/playbook.json | 82 | Second sentence grammar awkward: 'modellerini ince ayar yapın' should be 'modellerinde ince ayar yapın' or 'ince ayarlayın'. |
| tr-TR | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Trademark symbol ™ misplaced; should follow Unsloth brand, not sentence end. Otherwise accurate and fluent. |
| tr-TR | playbooks/supplemental/vllm-inference/playbook.json | 82 | Added 'AMD' not in source; 'çıkarım/sunum' acceptable but adds slight interpretation. |
| zh-CN | playbooks/supplemental/clustering-rpc-server/playbook.json | 82 | Added 'AMD' not in source; 'RPC server' left untranslated but acceptable; otherwise accurate and fluent. |
| zh-CN | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Second line awkward; trademark symbol misplaced (belongs to LLM brand, not translation); slightly literal phrasing. |
| zh-TW | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | ™ symbol misplaced (belongs to Unsloth, not LLM); otherwise accurate and fluent. |
| es-LA | playbooks/supplemental/pytorch-finetuning/playbook.json | 84 | Redundant '(fine-tune)' gloss awkward; 'LLMs' plural anglicized; otherwise accurate and fluent. |
| ro-RO | playbooks/supplemental/speech2speech-translation/playbook.json | 84 | Awkward 'construiește o traducere'; 'vorbire-în-vorbire' unusual hyphenation but understandable; otherwise accurate. |
| sr-Latn | playbooks/supplemental/openclaw-lemonade-server/playbook.json | 84 | Minor: 'agent' should be accusative 'agenta'; brand hyphenation slightly awkward but acceptable. |
