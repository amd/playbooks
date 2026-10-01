# Translation quality report

Automated MQM/GEMBA adequacy+fluency scores (0-100) per locale. No human review.

| Locale | Files | Mean | Min | Judge |
|--------|-------|------|-----|-------|
| ar | 80 | 93.1 | 82 | Claude-Opus-4.8 |
| cs-CZ | 80 | 92.5 | 72 | Claude-Opus-4.8 |
| da-DK | 80 | 92.4 | 72 | Claude-Opus-4.8 |
| de-DE | 80 | 93.2 | 72 | Claude-Opus-4.8 |
| el-GR | 80 | 92.0 | 70 | Claude-Opus-4.8 |
| es-LA | 80 | 93.0 | 78 | Claude-Opus-4.8 |
| fi-FI | 80 | 91.3 | 72 | Claude-Opus-4.8 |
| fr-CA | 80 | 91.0 | 72 | Claude-Opus-4.8 |
| fr-FR | 80 | 93.1 | 72 | Claude-Opus-4.8 |
| he | 80 | 92.0 | 60 | Claude-Opus-4.8 |
| hu-HU | 80 | 91.7 | 78 | Claude-Opus-4.8 |
| it-IT | 80 | 94.0 | 82 | Claude-Opus-4.8 |
| ja-JP | 80 | 93.0 | 62 | Claude-Opus-4.8 |
| ko-KR | 80 | 93.4 | 72 | Claude-Opus-4.8 |
| nb-NO | 80 | 92.1 | 82 | Claude-Opus-4.8 |
| nl-NL | 80 | 92.5 | 72 | Claude-Opus-4.8 |
| pl-PL | 80 | 93.2 | 78 | Claude-Opus-4.8 |
| pt-BR | 80 | 93.7 | 82 | Claude-Opus-4.8 |
| pt-PT | 80 | 92.8 | 82 | Claude-Opus-4.8 |
| ro-RO | 80 | 92.5 | 78 | Claude-Opus-4.8 |
| ru-RU | 80 | 93.0 | 85 | Claude-Opus-4.8 |
| sk-SK | 80 | 91.0 | 78 | Claude-Opus-4.8 |
| sl-SI | 80 | 90.8 | 70 | Claude-Opus-4.8 |
| sr-Latn | 80 | 91.5 | 82 | Claude-Opus-4.8 |
| sv-SE | 80 | 92.7 | 78 | Claude-Opus-4.8 |
| th-TH | 80 | 92.6 | 40 | Claude-Opus-4.8 |
| tr-TR | 80 | 91.9 | 40 | Claude-Opus-4.8 |
| uk-UA | 80 | 92.3 | 72 | Claude-Opus-4.8 |
| zh-CN | 80 | 93.7 | 78 | Claude-Opus-4.8 |
| zh-TW | 80 | 93.5 | 78 | Claude-Opus-4.8 |

## Files below 85 (87)

| Locale | File | Score | Issues |
|--------|------|-------|--------|
| th-TH | playbooks/core/vscode-qwen3-coder/playbook.json | 40 | Added 'AMD' not in source; Chinese text '使用' left untranslated at start of second sentence. |
| tr-TR | playbooks/supplemental/github-slack-development-digest/playbook.json | 40 | Hallucinated 'AMD Geliştirici Dokümanları' and meta-commentary note not in source; core translation accurate but major additions. |
| he | playbooks/supplemental/clustering-rpc-server/playbook.json | 60 | Title left mostly untranslated in English ('Clustering Two Ryzen AI Halos'); body translation is good and accurate. |
| he | playbooks/supplemental/deepseek-v4-flash-ds4/playbook.json | 60 | Title left untranslated ('Running'); rest is accurate and fluent. |
| ja-JP | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 62 | First line mistranslated: 'LLMによる' wrong; should be 'UnslothでLLMをファインチューニング'. Trademark symbol misplaced in source handling. |
| el-GR | playbooks/supplemental/vllm-inference/playbook.json | 70 | Untranslated technical terms (inference, serving, containerized) left in English where Greek equivalents exist; otherwise accurate and fluent. |
| sl-SI | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 70 | Inconsistent terminology (prilagajanje vs nastavljanje); trademark ™ misplaced; redundant 'jezikovnih modelov LLM'; acceptable but awkward. |
| cs-CZ | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 72 | Trademark ™ misplaced (belongs to Unsloth, not LLM); otherwise accurate but awkward double parentheticals. |
| da-DK | playbooks/supplemental/speech2speech-translation/playbook.json | 72 | Inconsistent terminology: title uses 'Tale-til-tale' but body keeps English 'speech-to-speech'; should be consistent in Danish. |
| de-DE | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 72 | Trademark symbol misplaced; source attaches ™ to 'LLMs™', translation moves it after 'erstellen', altering meaning/branding. |
| el-GR | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 72 | Trademark symbol misplaced (should be on Unsloth); 'βελτιστοποίηση' ambiguous for fine-tuning; otherwise adequate and fluent. |
| fi-FI | playbooks/supplemental/lemonade-getting-started/playbook.json | 72 | Brand name inflected incorrectly ('Lemonadenin', 'Lemonaden'); should be 'Lemonaden' / 'Lemonade-palvelimen'. Otherwise fluent and accurate. |
| fi-FI | playbooks/supplemental/llama-factory-finetuning/playbook.json | 72 | Title mistranslates 'with LLMs' as 'kanssa'; awkward. Body slightly misparses LLaMA Factory as technique. |
| fr-CA | playbooks/supplemental/amd-sync/playbook.json | 72 | Title translates 'AMD Sync' as 'synchronisation AMD' but body keeps 'AMD Sync'—inconsistent brand handling. |
| fr-CA | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 72 | Trademark symbol misplaced (moved from Unsloth to end); 'affinés/économe en mémoire' awkward but acceptable; inconsistent terminology. |
| fr-FR | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 72 | Trademark symbol misplaced (should follow 'fine-tuned LLMs'); 'affiner' less standard than 'affinage/ajustement fin'; minor fluency issues. |
| he | playbooks/supplemental/clustering-rpc-server-4-node/playbook.json | 72 | 1T+ mistranslated as T1+; 'ריכוב' awkward term for clustering. |
| ja-JP | playbooks/supplemental/vllm-inference/playbook.json | 72 | Added 'AMD' not in source; source says 'integrated GPU' not 'AMD iGPU'. Otherwise accurate and fluent. |
| ko-KR | playbooks/supplemental/vllm-inference/playbook.json | 72 | Mistranslation: 'integrated GPU' rendered as 'ROCm Instinct GPU', altering source meaning. |
| nl-NL | playbooks/supplemental/deepseek-v4-flash-ds4/playbook.json | 72 | Title left untranslated ('Running' not translated); otherwise accurate and fluent. |
| tr-TR | playbooks/supplemental/vllm-inference/playbook.json | 72 | Added 'AMD Radeon' not in source; 'çıkarım' and 'sunum' acceptable but awkward phrasing. |
| uk-UA | playbooks/core/n8n-automation-gpt-oss/playbook.json | 72 | 'саммарайзер' is awkward anglicism; better 'засіб для підсумовування новин'. Otherwise accurate. |
| el-GR | playbooks/core/n8n-automation-gpt-oss/playbook.json | 78 | Untranslated 'AI-powered'; should be 'τροφοδοτούμενο από AI' for fluency; otherwise accurate, brands intact. |
| es-LA | playbooks/supplemental/ollama-getting-started/playbook.json | 78 | 'Primero pasos' grammatical error; should be 'Primeros pasos'. |
| fr-FR | playbooks/supplemental/amd-sync/playbook.json | 78 | Title inconsistency: 'AMD Sync' translated in title but kept in body; should keep brand name consistent. |
| hu-HU | playbooks/supplemental/amd-sync/playbook.json | 78 | Inconsistent brand term: 'AMD Sync' translated as 'AMD szinkronizálással' in title, untranslated in body. |
| hu-HU | playbooks/supplemental/pytorch-kernels/playbook.json | 78 | First line 'PyTorch-pal' awkward, inconsistent kernel hyphenation between lines; otherwise accurate, terms intact. |
| ja-JP | playbooks/supplemental/hermes-lemonade-server/playbook.json | 78 | Title uses lowercase 'hermes' instead of brand 'Hermes Agent'; otherwise accurate. |
| nl-NL | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 78 | Inconsistent terminology: 'Fijnafstemming' vs 'fine-tuned'; trademark placement differs from source (LLMs™ vs LLM's™). |
| pl-PL | playbooks/supplemental/amd-sync/playbook.json | 78 | 'AMD Sync' brand mistranslated as 'synchronizacją AMD' in title; otherwise accurate and fluent. |
| ro-RO | playbooks/supplemental/vllm-inference/playbook.json | 78 | 'Primii' misspelled (Primii→Primii); 'serverea' is awkward/incorrect neologism for 'serving' |
| sk-SK | playbooks/core/lmstudio-rocm-llms/playbook.json | 78 | 'servovanie' is awkward/incorrect; 'poskytovanie' (used later) is better and should be consistent. |
| sk-SK | playbooks/supplemental/amd-sync/playbook.json | 78 | Title translated 'AMD Sync' as 'synchronizáciou AMD' instead of keeping brand name; inconsistent with body text. |
| sk-SK | playbooks/supplemental/clustering-rpc-server/playbook.json | 78 | Title omits 'with RPC'; otherwise accurate, fluent, terminology and brand terms intact. |
| sk-SK | playbooks/supplemental/speech2speech-translation/playbook.json | 78 | Title omits 'speech-to-speech' nuance; 'na vlastnom lokálnom' slightly redundant but acceptable. |
| sl-SI | playbooks/supplemental/llama-factory-finetuning/playbook.json | 78 | 'Fino prilagajanje' is awkward; 'natančno nastavljanje/prilagajanje' preferred for fine-tuning. Otherwise accurate, terms intact. |
| sv-SE | playbooks/supplemental/lemonade-getting-started/playbook.json | 78 | Awkward phrasing 'öppen källkods-lokal AI-server'; should be 'lokal AI-server med öppen källkod'. |
| zh-CN | playbooks/supplemental/amd-sync/playbook.json | 78 | Inconsistent brand rendering: 'AMD 同步' vs 'AMD Sync' in title; should keep 'AMD Sync' untranslated. |
| zh-TW | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 78 | Trademark symbol misplaced (should be on Unsloth, not LLM); otherwise accurate and fluent. |
| zh-TW | playbooks/supplemental/vllm-inference/playbook.json | 78 | 'integrated GPU' rendered as '內顯' (slang); more formal '內建 GPU/整合式 GPU' preferred. |
| sk-SK | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 80 | Trademark symbol misplaced (should be on Unsloth, not LLM); otherwise accurate and fluent. |
| sl-SI | playbooks/supplemental/pytorch-kernels/playbook.json | 80 | Inconsistent GPU rendering (GPU vs GPE); 'kernel' untranslated but acceptable; otherwise accurate and fluent. |
| tr-TR | playbooks/supplemental/speech2speech-translation/platform.md | 80 | Headings left untranslated (Platform Configuration, Prerequisites, Required Models, Network Requirements); table headers untranslated. Body translation accurate and fluent. |
| ar | playbooks/supplemental/llama-factory-finetuning/playbook.json | 82 | Title omits 'Fine' (ضبط vs ضبط بدقة); minor inconsistency LLaMA Factory vs LLaMA-Factory. |
| cs-CZ | playbooks/supplemental/amd-sync/playbook.json | 82 | Title translates 'AMD Sync' as 'synchronizací AMD' instead of brand name; 'Živým metrikám' over-translates product feature name. |
| cs-CZ | playbooks/supplemental/clustering-rpc-server-4-node/playbook.json | 82 | English 'Clustering' untranslated in title; 'odvozování' awkward for inference; otherwise accurate, terms intact. |
| da-DK | playbooks/core/lmstudio-rocm-llms/playbook.json | 82 | "servering"/"levere" awkward for serving LLMs; "betjene" more idiomatic. Otherwise accurate and fluent. |
| da-DK | playbooks/supplemental/hermes-lemonade-server/playbook.json | 82 | Title 'Kører' awkward; 'dens' should be 'sin'; 'Hermes Agent autonom AI-agent' lacks comma/structure for fluency |
| de-DE | playbooks/supplemental/amd-sync/playbook.json | 82 | Grammar error: 'per einem Klick' should be 'per einem Klick'→'mit einem Klick' or 'per Klick'. |
| de-DE | playbooks/supplemental/llama-factory-finetuning/playbook.json | 82 | Inconsistent brand formatting (LLaMA Factory vs LLaMA-Factory); 'Feinabstimmung' acceptable but 'Fine-Tuning' more standard in technical German. |
| el-GR | playbooks/supplemental/llama-factory-finetuning/playbook.json | 82 | Inconsistent fine-tuning rendering (Βελτιστοποίηση vs Μικρορύθμιση); otherwise accurate, fluent, terms intact. |
| el-GR | playbooks/supplemental/pytorch-finetuning/playbook.json | 82 | Fine-tuning rendered as 'βελτιστοποίηση' (optimization), slightly imprecise; otherwise accurate, brands intact. |
| fi-FI | playbooks/supplemental/ollama-getting-started/playbook.json | 82 | Redundant 'suorita...ajaminen'; otherwise accurate and fluent. |
| fi-FI | playbooks/supplemental/pytorch-finetuning/playbook.json | 82 | Second sentence adds 'parametreja' and 'tekniikoita' not in source; slight inaccuracy but fluent. |
| fi-FI | playbooks/supplemental/hermes-lemonade-server/playbook.json | 82 | Second sentence slightly awkward grammar ('Hermes Agent -autonomisen'), case/structure issues; otherwise accurate, terminology preserved. |
| fr-CA | playbooks/core/lmstudio-rocm-llms/playbook.json | 82 | Inconsistent 'diffusion'/'servir' for serve; 'de grands modèles' preferred over 'des grands modèles'. |
| fr-CA | playbooks/supplemental/speech2speech-translation/playbook.json | 82 | Title drops 'speech-to-speech' nuance; 'voix à voix' acceptable but slightly awkward; overall accurate and fluent. |
| he | playbooks/supplemental/clustering-rccl/playbook.json | 82 | Title 'צרור' (bundle) mistranslates 'Clustering'; should be 'אשכול/קיבוץ'. Otherwise accurate and fluent. |
| hu-HU | playbooks/supplemental/speech2speech-translation/playbook.json | 82 | Second sentence slightly awkward word order; 'beszédfordítás...beszédről beszédre' redundant but acceptable, meaning preserved. |
| hu-HU | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Title slightly awkward phrasing; trademark symbol placement; otherwise accurate and fluent. |
| hu-HU | playbooks/supplemental/deepseek-v4-flash-ds4/playbook.json | 82 | Title phrasing awkward/unnatural word order; otherwise accurate, terms intact. |
| it-IT | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Trademark symbol misplaced (should be on Unsloth); 'fine-tuned' rendered as 'ottimizzati' is slightly imprecise. |
| ja-JP | playbooks/supplemental/ollama-getting-started/playbook.json | 82 | LLM lowercased as 'llm'; inconsistent spacing around Ollama |
| ja-JP | playbooks/supplemental/speech2speech-translation/playbook.json | 82 | "音声対音声" is literal; "音声間翻訳" or "スピーチ・トゥ・スピーチ" more natural. Otherwise accurate. |
| nb-NO | playbooks/supplemental/cvml/playbook.json | 82 | Gender error: 'Lokal datasyn' should be 'Lokalt datasyn'; otherwise accurate and fluent. |
| nl-NL | playbooks/supplemental/llama-factory-finetuning/playbook.json | 82 | Title 'Fijn afstemmen' inconsistent with 'Finetune' in body; prefer consistent 'Finetunen'. |
| nl-NL | playbooks/supplemental/pytorch-finetuning/playbook.json | 82 | Inconsistent terminology: 'Fijnafstemmen' vs 'Finetune'; 'Fijnafstemmen' is uncommon for fine-tuning. |
| pl-PL | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Trademark misplaced (should be on 'fine-tuned LLMs'); 'efektywnie pamięciowo' slightly awkward phrasing. |
| pl-PL | playbooks/supplemental/github-slack-development-digest/playbook.json | 82 | 'Digest' as 'cyfrowy przegląd' is redundant/awkward; 'local-LLM digest' slightly ambiguous but acceptable. |
| pt-BR | playbooks/supplemental/clustering-rccl/playbook.json | 82 | 'Clustering' and 'multi-node' left untranslated; could use 'Agrupamento' and 'multi-nó' for better fluency |
| pt-PT | playbooks/supplemental/deepseek-v4-flash-ds4/playbook.json | 82 | Title uses Brazilian gerund 'Executando'; pt-PT prefers 'Executar/A executar'. Otherwise accurate and fluent. |
| ro-RO | playbooks/supplemental/clustering-rccl/playbook.json | 82 | "Clustering" left untranslated, awkward in title; otherwise accurate, fluent, terms intact. |
| ro-RO | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Inconsistent 'reglare fină'/'ajustate fin'; trademark symbol misplaced; 'fine-tuned LLMs™' as brand slightly altered. |
| ro-RO | playbooks/supplemental/deepseek-v4-flash-ds4/playbook.json | 82 | Title 'Rulez' (1st person) should be 'Rularea'; inconsistent register with formal body. |
| sk-SK | playbooks/supplemental/vllm-inference/playbook.json | 82 | 'Servovanie' is unnatural; 'obsluhu'/'poskytovanie' better fits serving context. Otherwise accurate and fluent. |
| sl-SI | playbooks/supplemental/pytorch-finetuning/playbook.json | 82 | Verbose 'fino prilagajanje' is awkward; otherwise accurate, brands/terms intact. |
| sr-Latn | playbooks/supplemental/github-slack-development-digest/playbook.json | 82 | Awkward 'GitHub-u-Slack'; 'digest' left untranslated inconsistently (izveštaj vs digest). |
| sv-SE | playbooks/supplemental/cvml/playbook.json | 82 | Grammatical gender error: 'Lokal datorseende' should be 'Lokalt datorseende' (neuter noun). |
| th-TH | playbooks/core/comfyui-image-gen/playbook.json | 82 | Title uses progressive 'กำลังสร้าง' instead of gerund heading; 'stunning' slightly softened. |
| th-TH | playbooks/supplemental/openclaw-lemonade-server/playbook.json | 82 | Added 'โมเดล' (model) not in source; 'autonomous' better as 'ทำงานอัตโนมัติ' but acceptable; otherwise accurate. |
| tr-TR | playbooks/supplemental/llama-factory-finetuning/playbook.json | 82 | Second sentence grammar slightly off: 'ince ayar yapın' doesn't agree with accusative object; should be 'ince ayarlayın'. |
| uk-UA | playbooks/supplemental/speech2speech-translation/playbook.json | 82 | Title omits speech-to-speech specificity; '(мова-мова)' awkward; otherwise fluent and accurate. |
| uk-UA | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Inconsistent term for fine-tuning (донастроювання vs тонке налаштування); trademark symbol misplaced from LLMs™. |
| ko-KR | playbooks/supplemental/clustering-rccl/playbook.json | 84 | Title omits 'with RCCL' clarity slightly; otherwise accurate, fluent, terms intact. |
| nb-NO | playbooks/supplemental/clustering-rccl/playbook.json | 84 | "Klynging" and "Halo-er" awkward; repeated "med" slightly clunky but accurate and intact. |
| sl-SI | playbooks/supplemental/deepseek-v4-flash-ds4/playbook.json | 84 | "izpeljevalnega pogona" awkward for inference engine; "Namestite" vs "Deploy" acceptable; brands intact. |
| uk-UA | playbooks/supplemental/github-slack-development-digest/playbook.json | 84 | 'GitHub-у-Slack' awkward phrasing; 'Development Digest' not fully conveyed; otherwise accurate, fluent, terms intact |
