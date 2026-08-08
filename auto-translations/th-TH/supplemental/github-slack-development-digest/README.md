<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **การแปลด้วยเครื่อง.** หน้านี้ได้รับการแปลโดยอัตโนมัติจากภาษาอังกฤษ และยังไม่ได้รับการตรวจสอบโดยมนุษย์ อาจมีข้อผิดพลาด และคำแนะนำ คำสั่ง การดาวน์โหลด ความพร้อมใช้งานของผลิตภัณฑ์ หรือเนื้อหาอื่นๆ บางส่วนอาจแตกต่างกันไปตามภาษาหรือภูมิภาค ในกรณีที่มีความไม่สอดคล้องหรือความคลาดเคลื่อนใดๆ ให้ถือว่าเวอร์ชันภาษาอังกฤษต้นฉบับของ playbook เป็นฉบับที่มีผลบังคับใช้และมีอำนาจเหนือกว่า
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## ภาพรวม

นักพัฒนาใช้เวลาจำนวนมากไปกับงานวนซ้ำเล็กๆ ที่เกิดขึ้นซ้ำๆ เช่น การรีวิว pull request ที่ติดป้าย
การตอบความคิดเห็นบน GitHub การจัดลำดับความสำคัญของ issue ใหม่ การแปลง Slack
thread ให้เป็นบันทึกการประชุมประจำวันหรือการติดตามผลเหตุการณ์ และการติดตามสัญญาณของการเปิดตัวหรือ
การวิจัย งานวนซ้ำแต่ละงานเป็นสิ่งที่คุ้นเคย แต่ก็ยังต้องอาศัยการตัดสินใจ:
รวบรวมบริบทที่ถูกต้อง ตัดสินใจว่าอะไรสำคัญ และโพสต์การอัปเดตที่ชัดเจนในที่ที่ทีมงาน
ทำงานอยู่แล้ว

[OpenHands automations](https://docs.openhands.dev/openhands/usage/automations/overview)
เปลี่ยนงานวนซ้ำเหล่านั้นให้เป็นบทสนทนาของเอเจนต์ที่กำหนดเวลาหรือเรียกใช้ตามเหตุการณ์: การรัน
ที่ AI software agent สามารถอ่านบริบท เรียกใช้เครื่องมือ และสร้างการอัปเดต
เทมเพลตการทำงานอัตโนมัติที่ใช้ร่วมกันใน OpenHands extensions catalog เป็นไปตาม
รูปแบบนี้สำหรับการรีวิว GitHub pull request การตรวจสอบ repository การจัดลำดับความสำคัญของ
Linear issue การทบทวนเหตุการณ์ (incident retrospective) สรุปการประชุมประจำวันบน Slack และสรุปงานวิจัย:
การทำงานอัตโนมัติจะตื่นขึ้น ใช้การผสานการทำงาน (integration) ที่กำหนดค่าไว้ เช่น GitHub หรือ
Slack เพื่อดึงบริบท ประมวลผลบริบทนั้นด้วยโมเดลภาษาขนาดใหญ่
(LLM) และเขียนผลลัพธ์กลับไป

[Agent Canvas](https://github.com/OpenHands/agent-canvas) คือ control
plane ในเครื่องสำหรับสร้างและทดสอบการทำงานอัตโนมัติเหล่านั้น ในเพลย์บุ๊กนี้จะรัน
OpenHands Agent Server ซึ่งเป็นกระบวนการ backend ที่ดำเนินการบทสนทนาของเอเจนต์
และเชื่อมต่อเอเจนต์กับบริการภายนอก เช่น GitHub และ Slack

เพื่อให้เวิร์กโฟลว์อยู่บนระบบ AMD ของคุณ เอเจนต์จะสื่อสารกับโมเดลในเครื่อง
ที่ให้บริการโดย Lemonade Server Lemonade เปิดใช้งานโมเดลนั้นผ่าน
API ที่เข้ากันได้กับ OpenAI ดังนั้น Agent Canvas จึงสามารถกำหนดค่าโมเดลนี้เหมือนกับ
endpoint แบบ OpenAI ระยะไกล ในขณะที่โมเดล พรอมต์ และบริบทของเวิร์กโฟลว์ยังคงอยู่ในเครื่อง

ในเพลย์บุ๊กนี้ คุณจะสร้างการทำงานอัตโนมัติที่เป็นรูปธรรมหนึ่งอย่าง: สรุปการพัฒนาจาก
GitHub ไปยัง Slack ตามกำหนดเวลา โดยใช้ GitHub ในการตรวจสอบกิจกรรมล่าสุดของ repository
Slack ในการโพสต์สรุป การเรียก Agent Canvas API เพื่อกำหนดค่าและ
ทดสอบการทำงานอัตโนมัติ และ Lemonade เพื่อรัน LLM ในเครื่อง

![แผนภาพสถาปัตยกรรมแสดง GitHub MCP, OpenHands automation, Lemonade Server และ Slack MCP](assets/00-architecture-overview.png)

## สิ่งที่คุณจะได้เรียนรู้

- วิธีเริ่มต้น Lemonade Server และตรวจสอบว่าโมเดลในเครื่องตอบคำขอแชทได้
- วิธีเปิด Agent Canvas และชี้ Agent Server ไปยัง LLM ในเครื่อง
- วิธีติดตั้ง GitHub และ Slack Model Context Protocol (MCP) server ผ่าน
  Agent Server API
- วิธีสร้างและเรียกใช้การทำงานอัตโนมัติของ OpenHands ตามกำหนดเวลาที่โพสต์
  สรุปการพัฒนาไปยัง Slack
- วิธีแก้ไขปัญหาความล้มเหลวที่พบบ่อยที่สุดของโมเดลในเครื่องและการทำงานอัตโนมัติ

## แนวคิดหลัก

| แนวคิด | คืออะไร | เกี่ยวข้องกับเพลย์บุ๊กนี้อย่างไร |
| --- | --- | --- |
| Lemonade Server | แพลตฟอร์มให้บริการ LLM ในเครื่องที่สร้างขึ้นสำหรับฮาร์ดแวร์ AMD ซึ่งเปิดใช้งาน API ที่เข้ากันได้กับ OpenAI ข้อมูลของคุณจะไม่ออกจากเครื่องของคุณ | รันโมเดลที่ขับเคลื่อนเอเจนต์ |
| OpenHands Agent Server | กระบวนการ backend ที่ดำเนินการบทสนทนาของเอเจนต์ OpenHands | โฮสต์เอเจนต์ โปรไฟล์ LLM และ MCP server ของมัน |
| Agent Canvas | control plane ในเครื่องสำหรับ OpenHands ที่รัน Agent Server และ UI สำหรับตรวจสอบการรันของเอเจนต์ | เปิดใช้งาน backend และให้ API ที่คุณเรียกใช้ |
| MCP server | Model Context Protocol server ที่ให้เครื่องมือแก่เอเจนต์สำหรับบริการภายนอก เช่น GitHub หรือ Slack | ให้เอเจนต์อ่าน GitHub และเขียนไปยัง Slack |
| OpenHands automation | บทสนทนาของเอเจนต์ที่กำหนดเวลาหรือเรียกใช้ตามเหตุการณ์ ซึ่งดึงบริบท ประมวลผล และเขียนผลลัพธ์ไปยังที่ใดที่หนึ่ง | สรุปจาก GitHub ไปยัง Slack ที่คุณสร้างในที่นี้ |

<!-- @device:stx,krk -->
> [!NOTE]
> เวิร์กโฟลว์ของ coding-agent ได้ประโยชน์จากโมเดลและหน้าต่างบริบทที่ใหญ่ขึ้น ใช้หน่วยความจำระบบ
> อย่างน้อย 32 GB และควรมี 64 GB ขึ้นไปสำหรับโมเดล GGUF ขนาดใหญ่กว่า
<!-- @device:end -->

## สิ่งที่ต้องมีก่อน

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

คุณต้องมี:

- Lemonade Server ที่ติดตั้งตาม
  [คู่มือการติดตั้ง Lemonade](https://lemonade-server.ai/docs/guide/install/) มาตรฐาน
- Node.js 22.12 หรือใหม่กว่า และ `npm` ที่ใช้ติดตั้ง Agent Canvas
  CLI ที่เผยแพร่และรัน MCP server ด้วย `npx`
- แพ็กเกจ `@openhands/agent-canvas` เวอร์ชันล่าสุดที่เผยแพร่ พร้อม
  การตั้งค่าเอเจนต์ที่ขับเคลื่อนด้วยสคีมา `LLMSummarizingCondenserSettings.max_tokens`
  และการรองรับ LLM `custom_tokenizer`
- แพ็กเกจ Python `transformers` ที่มีอยู่ในสภาพแวดล้อม Agent Server
  จำเป็นสำหรับการนับ token ตาม chat-template เมื่อตั้งค่า `custom_tokenizer`
- GitHub token ที่มีสิทธิ์อ่าน repository ที่คุณต้องการสรุป
- Slack bot token (`xoxb-...`) ที่มีสิทธิ์ `chat:write` และการอ่านช่อง
- Slack team ID (`T...`)
- Slack channel ID (`C...`) ที่จะโพสต์สรุป

เชิญแอป Slack เข้าร่วมช่องเป้าหมายก่อนทดสอบการทำงานอัตโนมัติ

## ตัวแปรที่ใช้ในเพลย์บุ๊กนี้

<!-- @device:halo,halo_box,stx,krk -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

```bash
export LEMONADE_BASE_URL="http://127.0.0.1:13305/api/v1"
export LEMONADE_MODEL="Qwen3.6-35B-A3B-GGUF"
export OPENHANDS_LLM_MODEL="openai/${LEMONADE_MODEL}"
export QWEN_CUSTOM_TOKENIZER="Qwen/Qwen3.6-35B-A3B"
export CONDENSER_MAX_TOKENS="56000"
```

ค่าต่อไปนี้จะถูกป้อนเข้าไปในหน้า UI ของ Agent Canvas ในขั้นตอนถัดไป ตั้งค่า
ไว้ที่นี่เพื่อให้คุณคัดลอกได้:

```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```

ใช้ค่า `owner/repo` ที่ชัดเจนสำหรับ `GITHUB_REPO_FILTER` การใช้สัญลักษณ์แทน (wildcard)
ขององค์กรที่กว้างเกินไปอาจส่งคืนบริบท MCP มากเกินไปสำหรับโมเดลในเครื่อง

## 1. เริ่มต้น Lemonade Server

เริ่มต้นโมเดลจาก Lemonade CLI:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```

Lemonade เปิดใช้งาน API ที่เข้ากันได้กับ OpenAI ที่:

```text
http://127.0.0.1:13305/api/v1
```

ทางเลือกเสริม: หาก Agent Canvas หรือตัวรันการทำงานอัตโนมัติไม่ได้อยู่บนเครื่องเดียวกัน
ให้เผยแพร่ endpoint ของ Lemonade ผ่านทันเนลที่ปลอดภัย และใช้ URL แบบ HTTPS เป็น
LLM base URL:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. ตรวจสอบโมเดลในเครื่อง

ยืนยันว่า Lemonade สามารถให้บริการโมเดลที่เลือกได้:

```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

จากนั้นส่งคำขอแชทเล็กๆ:

```bash
curl -sS "${LEMONADE_BASE_URL}/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"${LEMONADE_MODEL}"'",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```

หากได้รับอาร์เรย์ `choices` กลับมา แสดงว่า Lemonade พร้อมสำหรับ Agent Canvas แล้ว
## 3. เริ่มต้น Agent Canvas

ติดตั้งแพ็กเกจ Agent Canvas ที่เผยแพร่แล้วและเริ่มการทำงานของสแต็กทั้งหมด:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

หากการติดตั้ง npm แบบ global ล้มเหลวเนื่องจากข้อผิดพลาดด้านสิทธิ์การเข้าถึง
โปรดดูรายการแก้ไขปัญหาเกี่ยวกับสิทธิ์การเข้าถึงของ npm ด้านล่าง

โดยค่าเริ่มต้น Agent Canvas จะเริ่มทำงานที่ `http://localhost:8000`
เปิด URL นั้นในเบราว์เซอร์ของคุณ backend ท้องถิ่นเริ่มต้นควรแสดงสถานะสมบูรณ์ที่หน้าจอหลัก

คำสั่ง `agent-canvas` จะเริ่มต้น agent server, automation backend และ
web frontend พร้อมกัน คุณต้องใช้คำสั่งเดียวนี้เท่านั้นในการรัน OpenHands
บนเครื่องของคุณ ส่วนที่เหลือของคู่มือนี้จะกำหนดค่าทุกอย่างผ่าน UI ของ
Agent Canvas ในเบราว์เซอร์ของคุณ

## 4. กำหนดค่า LLM ท้องถิ่นใน UI

เมื่อเปิดใช้งานครั้งแรก Agent Canvas จะแสดงขั้นตอนการเริ่มต้นใช้งาน ในขั้นตอนนั้น:

1. คงค่า **OpenHands** ที่เลือกไว้เป็น agent และคลิก **Next**
2. ที่ **Set up your LLM** ให้เลือก **Advanced**
3. คงค่า **Authentication** ไว้ที่ **API key**
4. ตั้งค่า **Custom Model** เป็นค่าของ `OPENHANDS_LLM_MODEL`
   ซึ่งคือ `openai/Qwen3.6-35B-A3B-GGUF`
5. ตั้งค่า **Base URL** เป็น `http://127.0.0.1:13305/api/v1`
6. สำหรับ **API Key** ให้ใส่ค่าตัวยึดตำแหน่งที่ไม่ว่างเปล่าใดๆ เช่น `lemonade-local`
   Lemonade ไม่จำเป็นต้องใช้คีย์จริง แต่ไคลเอนต์ OpenHands ต้องการค่าเพื่อส่งออกไป

ช่องข้อมูลการเชื่อมต่อควรมีลักษณะดังนี้ ช่อง API key จะถูกซ่อนด้วย UI

![การตั้งค่า LLM Advanced สำหรับการใช้งาน Agent Canvas ครั้งแรกพร้อมโมเดล Lemonade และ base URL ท้องถิ่น](assets/01-llm-advanced-settings.png)

จากนั้นเลือก **All** และตั้งค่าฟิลด์เพิ่มเติมสำหรับโมเดลท้องถิ่น:

1. เลื่อนไปที่ **Custom Tokenizer** และตั้งค่าเป็น `Qwen/Qwen3.6-35B-A3B`
2. เลื่อนไปที่ **LiteLLM Extra Body** และตั้งค่าเป็น
   `{"enable_thinking": true}`
3. คลิก **Next**

![แท็บ LLM All สำหรับการใช้งาน Agent Canvas ครั้งแรกพร้อม Qwen custom tokenizer](assets/02-llm-all-tokenizer-settings.png)

![แท็บ LLM All สำหรับการใช้งาน Agent Canvas ครั้งแรกพร้อมการกำหนดค่า LiteLLM extra body](assets/03-llm-all-extra-body-settings.png)

การตั้งค่า LLM ควรแสดงดังนี้:

| ฟิลด์ | ค่า |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

คำนำหน้า `openai/` บอกให้ LiteLLM ใช้รูปแบบการร้องขอที่เข้ากันได้กับ OpenAI
ในการเชื่อมต่อกับ endpoint ของ Lemonade custom tokenizer คือ tokenizer ดั้งเดิมของ Hugging
Face สำหรับโมเดล GGUF ซึ่งช่วยให้ OpenHands นับจำนวนโทเคนของ
chat-template แบบเดียวกับที่ local model server เห็น ฟอร์ม LLM สำหรับการใช้งานครั้งแรกในปัจจุบันไม่แสดงการตั้งค่า condenser
หากบิลด์ Agent Canvas ของคุณแสดงการตั้งค่า condenser ในภายหลังภายใต้ **Settings > LLM**
ให้ใช้ `llm_summarizing` และ
ตั้งค่าจำนวนโทเคนสูงสุดให้ต่ำกว่าขนาด context window ของ Lemonade เช่น `56000`

## 5. ติดตั้ง GitHub และ Slack MCP Server

ใน UI ของ Agent Canvas ให้เปิด **Customize** (หรือ **Settings > MCP**) เพื่อเพิ่ม
MCP server ที่ให้เครื่องมือแก่ agent สำหรับ GitHub และ Slack ค่าโทเคนจะถูกส่ง
ไปยัง Agent Server ท้องถิ่นของคุณเท่านั้น และจะถูกบันทึกเป็นการตั้งค่าที่เข้ารหัสไว้

### GitHub MCP server

เพิ่ม MCP server ใหม่ด้วยการตั้งค่าต่อไปนี้:

| ฟิลด์ | ค่า |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = โทเคน GitHub ของคุณ |

ใช้โทเคน GitHub ที่มีสิทธิ์อ่านสำหรับ repository ที่คุณต้องการสรุป

### Slack MCP server

เพิ่ม MCP server ตัวที่สองด้วยการตั้งค่าต่อไปนี้:

| ฟิลด์ | ค่า |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = ID ของช่องสรุปข่าวของคุณ |

ตั้งค่า `SLACK_CHANNEL_IDS` เป็น ID ของช่องสรุปข่าว (ค่าเดียวกันกับ
`SLACK_DIGEST_CHANNEL`) เพื่อให้ agent ไม่ต้องเปิดดูทีละช่อง Slack
ทั้งหมด

หลังจากเพิ่ม server ทั้งสองแล้ว ให้ใช้ปุ่ม **Test** ในแต่ละตัวเพื่อยืนยันว่า
เชื่อมต่อและแสดงเครื่องมือได้ GitHub server ควรแสดงรายการเครื่องมือของ GitHub
และ Slack server ควรแสดงรายการเครื่องมือของ Slack

![หน้า MCP ของ Agent Canvas พร้อม GitHub และ Slack server ที่ติดตั้งแล้ว](assets/04-mcp-servers-installed.png)

## 6. สร้าง Digest Automation

ใน UI ของ Agent Canvas ให้เปิดหน้า **Automations** และสร้าง automation ใหม่:

1. เลือก **Create automation** และเลือกประเภท **Prompt preset**
2. ตั้งค่า **Name** เป็น `GitHub Development Digest to Slack`
3. ตั้งค่า **Prompt** เป็นข้อความต่อไปนี้ โดยแทนที่ตัวยึดตำแหน่งของ repository และ
   channel ด้วยค่าของคุณ:

   ```text
   Use the GitHub MCP server for exactly one repository: your-org/your-repo.
   Inspect recent development activity since the previous weekday, including
   merged pull requests, newly opened or reopened pull requests, notable
   commits pushed to main or release branches, new issues, important issue
   updates, releases, risks, blockers, and review requests. Keep GitHub
   lookups small: inspect the latest 3 to 5 commits, pull requests, issues,
   and releases. Use the Slack MCP server to post directly to channel ID
   C0123456789. Keep the Slack message concise: title with date range, 3 to 7
   bullets, links back to GitHub, and a Needs attention section only if
   needed. End with: This digest was generated by an AI agent (OpenHands) on
   behalf of the user. Do not include secrets, raw tokens, private
   environment variables, or unrelated Slack messages.
   ```

4. ตั้งค่า **Trigger** เป็น **Cron** ด้วยตารางเวลา `0 9 * * 1-5` (9 โมงเช้า
   ในวันธรรมดา) และตั้งค่า **Timezone** เป็นเขตเวลาของคุณ เช่น
   `America/New_York`
5. ตั้งค่า **Timeout** เป็น `900` วินาที
6. บันทึก automation

หน้ารายละเอียด automation จะแสดง automation ใหม่พร้อมกับ cron trigger และ
entrypoint แบบ prompt-preset ที่สร้างขึ้น

![หน้ารายละเอียด automation ของ Agent Canvas หลังการสร้าง](assets/05-automation-created.png)
## 7. ทดสอบการทำงานอัตโนมัติ

จากหน้ารายละเอียดการทำงานอัตโนมัติใน Agent Canvas UI:

1. คลิก **Run now** (หรือ **Dispatch**) เพื่อรันการทำงานอัตโนมัติทันทีหนึ่งครั้ง
2. สังเกตรายการรันในหน้าเดียวกัน การรันล่าสุดควรเปลี่ยนสถานะเป็น
   `COMPLETED`
3. เปิด Slack channel เป้าหมายของคุณ ควรมีข้อความสรุปที่สร้างขึ้นปรากฏอยู่

คุณไม่จำเป็นต้องรอให้ cron schedule ทำงาน—**Run now** จะสั่งให้เกิดการรัน
ทันทีตามต้องการ เพื่อให้คุณสามารถยืนยันว่า prompt การเชื่อมต่อ MCP และการโพสต์ไปยัง Slack
ทำงานได้ทั้งหมดก่อนที่จะพึ่งพากำหนดการ

![Agent Canvas automation run completed successfully](assets/06-automation-run-completed.png)

![Slack channel showing the generated OpenHands digest](assets/07-slackbot-message.png)

## การแก้ไขปัญหา

- **Lemonade หยุดทำงาน:** รีสตาร์ตด้วยคำสั่ง
  `lemonade run "${LEMONADE_MODEL}"` ในขั้นตอนที่ 1 จากนั้นตรวจสอบสถานะสุขภาพอีกครั้ง
- **`npm install -g` ล้มเหลวเนื่องจากข้อผิดพลาดด้านสิทธิ์:** บน Linux หรือ WSL
  ให้ตั้งค่าไดเรกทอรี npm แบบ global ที่ผู้ใช้เป็นเจ้าของ เพิ่มไดเรกทอรีดังกล่าวไปยังไฟล์เริ่มต้น shell
  ของคุณ จากนั้นติดตั้ง Agent Canvas อีกครั้ง:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

  หากคุณใช้ `zsh` ให้เพิ่มบรรทัด `export PATH=...` เดียวกันนี้ไปยัง `~/.zshrc` แทน
  `~/.bashrc`
- **Agent Canvas ปฏิเสธการตั้งค่า LLM หลังจากตั้งค่า `custom_tokenizer`:**
  ติดตั้ง `transformers` ในสภาพแวดล้อม Python ของ Agent Server รีสตาร์ต Agent
  Canvas หากจำเป็น แล้วลองบันทึกการตั้งค่า LLM อีกครั้ง OpenHands ต้องใช้
  Transformers เพื่อโหลด tokenizer chat template เมื่อมีการตั้งค่า `custom_tokenizer`
- **Agent Canvas ไม่สามารถเชื่อมต่อกับ Lemonade ได้:** ตรวจสอบด้วย
  `curl -fsS "${LEMONADE_BASE_URL}/health"` และยืนยันว่า base URL ที่กรอกไว้ใน
  แบบฟอร์ม LLM ครั้งแรกหรือใน **Settings > LLM** ตรงกับ endpoint ในเครื่องที่กำลัง
  ทำงานอยู่ หรือ HTTPS tunnel
- **การตั้งค่า LLM ไม่ถูกบันทึก:** ตรวจสอบให้แน่ใจว่าคุณคลิก **Next** หลังจาก
  กรอกค่าต่างๆ แล้ว เปิด **Settings > LLM** อีกครั้งเพื่อยืนยันว่าค่าดังกล่าวถูกบันทึกไว้
- **GitHub MCP ไม่สามารถมองเห็น private repositories:** ตรวจสอบว่า GitHub token มี
  สิทธิ์อ่านสำหรับ repository เป้าหมาย และปุ่ม **Test** ของ MCP ใน
  **Customize** แสดงเครื่องมือของ GitHub
- **Slack สามารถอ่าน channel ได้แต่ไม่สามารถโพสต์ได้:** เชิญแอป Slack เข้าสู่
  channel เป้าหมาย และยืนยันว่า bot มีสิทธิ์ `chat:write`
- **การทำงานอัตโนมัติแสดงรายการ Slack channel มากเกินไป:** ใช้ Slack channel ID และ
  ตั้งค่า `SLACK_CHANNEL_IDS` บน Slack MCP server ใน **Customize**
- **การรันการทำงานอัตโนมัติล้มเหลวหรือเกิน context:** ยืนยันว่า Lemonade ถูกเริ่มต้น
  ด้วย `ctx_size=65536` ยืนยันว่า OpenHands LLM มีการตั้งค่า `custom_tokenizer`
  และใช้ repository ที่ระบุอย่างชัดเจนโดยจำกัดชุดผลลัพธ์จาก GitHub ไว้ที่ 3 ถึง 5
  รายการ หากรุ่น Agent Canvas ของคุณมีการตั้งค่า condenser ให้ตั้งค่า condenser
  max tokens ให้ต่ำกว่าขนาดหน้าต่าง context ของ Lemonade

## ขั้นตอนถัดไป

- เพิ่มข้อความสรุปรายสัปดาห์เฉพาะสำหรับ release
- เพิ่มการทำงานอัตโนมัติที่ทริกเกอร์ด้วยเหตุการณ์ GitHub เพื่อการแจ้งเตือน PR หรือ push ที่รวดเร็วขึ้น
- ส่งข้อความสรุปเดียวกันไปยัง Notion, Linear หรือเครื่องมืออื่นที่รองรับ MCP

## แหล่งข้อมูล

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [เอกสาร Lemonade Server](https://lemonade-server.ai/docs)
- [ที่เก็บส่วนขยาย OpenHands](https://github.com/OpenHands/extensions)
- [Model Context Protocol servers](https://github.com/modelcontextprotocol/servers)
- [แพ็กเกจ Slack MCP](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)