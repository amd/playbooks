# Translation quality report

Automated MQM/GEMBA adequacy+fluency scores (0-100) per locale. No human review.

| Locale | Files | Mean | Min | Judge |
|--------|-------|------|-----|-------|
| ar | 78 | 93.3 | 88 | Claude-Opus-4.8 |
| cs-CZ | 78 | 92.9 | 78 | Claude-Opus-4.8 |
| da-DK | 78 | 93.2 | 88 | Claude-Opus-4.8 |
| de-DE | 78 | 93.6 | 72 | Claude-Opus-4.8 |
| el-GR | 78 | 92.6 | 78 | Claude-Opus-4.8 |
| es-LA | 78 | 93.6 | 84 | Claude-Opus-4.8 |
| fi-FI | 78 | 92.1 | 88 | Claude-Opus-4.8 |
| fr-CA | 78 | 91.3 | 78 | Claude-Opus-4.8 |
| fr-FR | 78 | 93.1 | 78 | Claude-Opus-4.8 |
| he | 78 | 92.9 | 88 | Claude-Opus-4.8 |
| hu-HU | 78 | 92.3 | 88 | Claude-Opus-4.8 |
| it-IT | 78 | 94.2 | 72 | Claude-Opus-4.8 |
| ja-JP | 78 | 94.1 | 78 | Claude-Opus-4.8 |
| ko-KR | 78 | 94.0 | 88 | Claude-Opus-4.8 |
| nb-NO | 78 | 92.0 | 88 | Claude-Opus-4.8 |
| nl-NL | 78 | 92.5 | 78 | Claude-Opus-4.8 |
| pl-PL | 78 | 93.6 | 78 | Claude-Opus-4.8 |
| pt-BR | 78 | 94.0 | 78 | Claude-Opus-4.8 |
| pt-PT | 78 | 91.9 | 78 | Claude-Opus-4.8 |
| ro-RO | 78 | 93.5 | 84 | Claude-Opus-4.8 |
| ru-RU | 78 | 92.9 | 88 | Claude-Opus-4.8 |
| sk-SK | 78 | 92.2 | 82 | Claude-Opus-4.8 |
| sl-SI | 78 | 91.2 | 78 | Claude-Opus-4.8 |
| sr-Latn | 78 | 91.5 | 82 | Claude-Opus-4.8 |
| sv-SE | 78 | 92.6 | 88 | Claude-Opus-4.8 |
| th-TH | 78 | 93.2 | 72 | Claude-Opus-4.8 |
| tr-TR | 78 | 92.7 | 80 | Claude-Opus-4.8 |
| uk-UA | 78 | 93.0 | 88 | Claude-Opus-4.8 |
| zh-CN | 78 | 93.3 | 78 | Claude-Opus-4.8 |
| zh-TW | 78 | 93.5 | 82 | Claude-Opus-4.8 |

## Files below 85 (41)

| Locale | File | Score | Issues |
|--------|------|-------|--------|
| de-DE | playbooks/supplemental/deepseek-v4-flash-ds4/playbook.json | 72 | Untranslated 'Deploy' left in English; imperative structure inconsistent (Deploy...verwalten Sie). |
| it-IT | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 72 | Redundant 'Ottimizzazione fine-tuning'; trademark ™ misplaced from Unsloth to LLM; 'fine-tuned' rendered as generic 'ottimizzati'. |
| th-TH | playbooks/supplemental/deepseek-v4-flash-ds4/playbook.json | 72 | Title left untranslated ('Running...'); 'inference engine' not localized. Otherwise accurate, brand terms intact. |
| cs-CZ | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 78 | Trademark symbol misplaced (should be on Unsloth/product name); slight redundancy 'jemné doladění' vs 'doladění'. |
| el-GR | playbooks/supplemental/llama-factory-finetuning/playbook.json | 78 | "Λεπτομερής Συντονισμός" awkward for fine-tuning; "LLaMA-Factory" hyphenation inconsistent with brand; LoRA intact. |
| el-GR | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 78 | Trademark symbol misplaced (should follow Unsloth, not LLM); 'Fine-Tuning' terminology inconsistent between title and body. |
| fr-CA | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 78 | Trademark misplaced: ™ belongs after 'fine-tuned LLMs' concept; awkward placement on 'LLM™'. Otherwise accurate, fluent. |
| fr-FR | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 78 | Trademark symbol misplaced (should follow LLMs, not the phrase); terminology inconsistency (Ajustement fin vs affinés). |
| ja-JP | playbooks/supplemental/speech2speech-translation/playbook.json | 78 | "音声対音声" is awkward; "音声から音声への" or "スピーチ・トゥ・スピーチ" more natural. Otherwise accurate. |
| ja-JP | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 78 | Trademark symbol misplaced; source has 'fine-tuned LLMs™' but translation attaches ™ to Unsloth. |
| nl-NL | playbooks/supplemental/deepseek-v4-flash-ds4/playbook.json | 78 | Untranslated 'Running' in title heading; otherwise accurate and fluent. |
| pl-PL | playbooks/supplemental/amd-sync/playbook.json | 78 | Title translates 'AMD Sync' as generic 'synchronizacją' instead of keeping brand name; inconsistent with body. |
| pt-BR | playbooks/supplemental/amd-sync/playbook.json | 78 | Title translated 'AMD Sync' as 'sincronização AMD' but kept brand elsewhere; inconsistent brand handling. |
| pt-PT | playbooks/supplemental/hermes-lemonade-server/playbook.json | 78 | Awkward 'A Executar' title; 'backend' untranslated (acceptable); inconsistent Agent/Agente handling. |
| sl-SI | playbooks/supplemental/pytorch-finetuning/playbook.json | 78 | Redundant English glosses in parentheses; 'fino prilagajanje' awkward for fine-tuning, though terms and brands intact. |
| th-TH | playbooks/core/comfyui-image-gen/playbook.json | 78 | Title mistranslated as progressive 'กำลังสร้าง' (generating in progress) instead of gerund heading; slightly awkward phrasing. |
| zh-CN | playbooks/supplemental/deepseek-v4-flash-ds4/playbook.json | 78 | Title mistranslated: 'Running...with ds4' rendered as passive 'is running', losing imperative/gerund meaning. |
| tr-TR | playbooks/supplemental/speech2speech-translation/platform.md | 80 | Headings left untranslated (Platform Configuration, Prerequisites, Required Models, Network Requirements); table headers untranslated. Body translation accurate and fluent. |
| cs-CZ | playbooks/supplemental/clustering-rccl/playbook.json | 82 | "Clustrování" awkward neologism; "vícenodový" non-standard (better: víceuzlový). Terminology intact, otherwise fluent and accurate. |
| de-DE | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Inconsistent terminology (Feinabstimmung vs Fine-Tuning); trademark symbol misplaced from original 'fine-tuned LLMs™'. |
| fr-CA | playbooks/supplemental/speech2speech-translation/playbook.json | 82 | Inconsistent term: 'voix-voix' vs 'voix-à-voix'; 'voix-à-voix' is anglicized calque, 'parole à parole' preferable. |
| it-IT | playbooks/supplemental/speech2speech-translation/playbook.json | 82 | Title omits 'speech-to-speech' nuance; 'voce a voce' slightly awkward but acceptable; overall accurate and fluent. |
| pl-PL | playbooks/supplemental/github-slack-development-digest/playbook.json | 82 | Title adds 'codzienny' (daily) not in source; 'from development' loosely rendered. Otherwise accurate, fluent, terms intact. |
| pt-PT | playbooks/core/pytorch-rocm-llms/playbook.json | 82 | Brazilian-style gerund 'Executando' unnatural for pt-PT; prefer 'Executar/A executar'. Otherwise accurate and fluent. |
| pt-PT | playbooks/supplemental/clustering-rccl/playbook.json | 82 | 'Clustering' left untranslated; 'usando' less formal than 'utilizando' for pt-PT; otherwise accurate. |
| pt-PT | playbooks/supplemental/clustering-rpc-server/playbook.json | 82 | 'Clustering' left untranslated (agrupamento); otherwise accurate, fluent, terminology and brands intact. |
| pt-PT | playbooks/supplemental/lemonade-getting-started/playbook.json | 82 | "IA Gen" awkward; should be "IA generativa" or "Gen AI" kept intact. |
| pt-PT | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Trademark symbol misplaced (should follow Unsloth); 'eficiência de memória' slightly literal but acceptable. |
| sk-SK | playbooks/supplemental/amd-sync/playbook.json | 82 | Title mistranslates 'AMD Sync' as 'synchronizáciou AMD' instead of keeping brand name; body correct. |
| sk-SK | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Trademark symbol misplaced (should follow Unsloth, not LLM); otherwise accurate and fluent. |
| sl-SI | playbooks/supplemental/llama-factory-finetuning/playbook.json | 82 | Inconsistent brand form 'LLaMA-Factory' vs 'LLaMA Factory'; 'fino prilagajanje' awkward; second sentence omits fine-tuning nuance. |
| sl-SI | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Redundant parenthetical (fine-tuning) repeated; trademark ™ misplaced from 'LLMs' brand context; otherwise accurate, fluent. |
| sr-Latn | playbooks/supplemental/pytorch-kernels/playbook.json | 82 | Inconsistent terminology: 'kernela' vs 'jezgra' for same term; otherwise accurate, fluent, brands intact. |
| th-TH | playbooks/supplemental/cvml/playbook.json | 82 | Title left 'Local Computer Vision' untranslated; otherwise accurate, fluent, terms and brands intact. |
| tr-TR | playbooks/supplemental/pytorch-finetuning/playbook.json | 82 | Second sentence grammar awkward: 'modellerini ince ayar yapın' should be 'modellerinde ince ayar yapın' or 'ince ayarlayın'. |
| zh-CN | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Second line awkward; trademark symbol misplaced (belongs to LLM brand, not translation); slightly literal phrasing. |
| zh-TW | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | ™ symbol misplaced (belongs to Unsloth, not LLM); otherwise accurate and fluent. |
| es-LA | playbooks/supplemental/pytorch-finetuning/playbook.json | 84 | Redundant '(fine-tune)' gloss awkward; 'LLMs' plural anglicized; otherwise accurate and fluent. |
| pt-PT | playbooks/supplemental/github-slack-development-digest/playbook.json | 84 | Inconsistent handling of 'digest' (kept English in title, glossed later); 'GitHub-to-Slack' untranslated may be intentional. |
| ro-RO | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 84 | Trademark symbol misplaced (belongs to LLMs, not memory phrase); slightly awkward phrasing but accurate. |
| sr-Latn | playbooks/supplemental/github-slack-development-digest/playbook.json | 84 | 'digest' left untranslated inconsistently (earlier 'dnevni pregled'); otherwise accurate, fluent, terms intact. |
