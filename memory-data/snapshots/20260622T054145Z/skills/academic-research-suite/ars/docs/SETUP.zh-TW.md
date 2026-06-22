# ARS Codex 瀹夎瑷畾

鏈枃瑾槑 `academic-research-skills-codex` 鐨?Codex 鐗堣ō瀹氭柟寮忥紝涓嶆槸
Claude Code plugin 瀹夎鎸囧崡銆侰laude Code 鍘熺敓鐗堟湰璜嬩娇鐢?
`Imbad0202/academic-research-skills`銆?

## 鏈€灏忓彲琛岃ō瀹?

# REDACTED: sensitive-looking memory line
瀛樺彇琛岀偤閮芥瘮杓冪┅瀹氾細

```bash
python "$HOME/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo Imbad0202/academic-research-skills-codex \
  --ref main \
  --path skills/academic-research-suite \
  --method git
```

鏇存柊鏃㈡湁瀹夎锛?

```bash
rm -rf "$HOME/.codex/skills/academic-research-suite"
python "$HOME/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo Imbad0202/academic-research-skills-codex \
  --ref main \
  --path skills/academic-research-suite \
  --method git
```

# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line

浣跨敤鏅傛槑纰哄懠鍙細

```text
Use $academic-research-suite to plan a systematic literature review on AI in higher education QA.
```

Skill 鍚嶇ū鏄柈鏁革細`$academic-research-suite`銆?

鐢?`/skills` 椹楄瓑瀹夎銆傛甯哥媭鎱嬫噳瑭插彧鐪嬪埌涓€鍊?ARS 鍏ュ彛锛?
`academic-research-suite` 鎴?`Academic Research ...`銆傚鏋滅湅鍒版湰 package
椤嶅鏆撮湶 `academic-paper`銆乣academic-pipeline`銆乣deep-research`銆?
`academic-paper-reviewer` 绛夌崹绔?skill锛岃珛鐢ㄤ笂鏂规洿鏂版寚浠ら噸鏂板畨瑁濓紝涓﹂枊鏂扮殑
Codex conversation銆?

涓€鑸?Codex 浣跨敤涓嶉渶瑕?Anthropic API key銆備富瑕佹ā鍨嬬敱鐩墠 Codex runtime
# REDACTED: sensitive-looking memory line

## Claude-style aliases

Claude Code ARS 鏈冨畨瑁?`/ars-*` slash commands銆侰odex 娌掓湁鍚屼竴濂?command
registry锛屾墍浠ユ湰 package 鍦?`$academic-research-suite` router 瑁℃ā鎿悓妯ｆ剰鍦栥€?

濡傛灉 Codex client 鏈冩敂鎴?slash input锛岃珛鐢ㄤ笉鍚?slash 鐨?alias锛?

```text
ars-plan my paper on AI governance in universities
ars-revision-coach reviewer_comments.md
ars-full topic: demographic decline and university quality assurance
```

涔熷彲浠ュ寘鍦ㄦ槑纰虹殑 skill 鍛煎彨鍏э細

```text
Use $academic-research-suite: ars-outline for this manuscript draft.
```

| Claude command | Codex alias | 璺敱 workflow |
|---|---|---|
| `/ars-plan` | `ars-plan` | `academic-paper` `plan` mode |
| `/ars-outline` | `ars-outline` | `academic-paper` `outline-only` mode |
| `/ars-abstract` | `ars-abstract` | `academic-paper` `abstract-only` mode |
| `/ars-lit-review` | `ars-lit-review` | `academic-paper` `lit-review` mode |
| `/ars-citation-check` | `ars-citation-check` | `academic-paper` `citation-check` mode |
| `/ars-disclosure` | `ars-disclosure` | `academic-paper` `disclosure` mode |
| `/ars-format-convert` | `ars-format-convert` | `academic-paper` `format-convert` mode |
| `/ars-revision-coach` | `ars-revision-coach` | `academic-paper` `revision-coach` mode |
| `/ars-revision` | `ars-revision` | `academic-paper` `revision` mode |
| `/ars-full` | `ars-full` | `academic-pipeline` full workflow |

`commands/ars-*.md` frontmatter 瑁＄殑 `model: opus` / `model: sonnet` 鏄?
Claude Code routing metadata銆侰odex 鏈冧娇鐢ㄧ洰鍓?active model锛岄櫎闈炰娇鐢ㄨ€呭湪灏嶈┍涓槑纰烘寚瀹氬叾浠栨ā鍨嬨€?

## 妯＄硦璜栨枃椤岀洰鐨?Socratic 鏀舵杺

鐣朵娇鐢ㄨ€呰鎯冲璜栨枃锛屼絾鍙湁椤岀洰銆佹毇瀹氭椤屾垨澶ф柟鍚戯紝閭勬矑鏈夋槑纰?research
question 鏅傦紝Codex router 鎳夋瘮鐓?upstream ARS锛氬厛閫?`deep-research`
`socratic` mode锛屼笉鐩存帴鐢㈢敓澶х侗銆乨raft 鎴栧畬鏁?pipeline銆?

寤鸿 prompt锛?

```text
Use $academic-research-suite.
鎴戞兂鍋氫竴绡囪珫鏂囷紝椤岀洰鏂瑰悜鏄?AI adoption in higher education quality assurance銆?
鎴戦倓娌掓湁鏄庣⒑ research question銆?
璜嬪厛鐢?SCR / Socratic 鍟忕瓟骞垜鏀舵杺鍟忛锛屼笉瑕佸厛瀵ぇ缍便€?
```

闋愭湡琛岀偤锛?

- route 鍒?`deep-research` `socratic` mode
- 鍏堝晱鏀舵杺鍟忛
- 姊濅欢瓒冲寰屾墠鏁寸悊 2-3 鍊嬪€欓伕 RQ
- RQ 娓呮鍓嶄笉閫插叆 `academic-paper` 澶х侗鎴栧浣?

濡傛灉瑕佽窇瀹屾暣 pipeline锛屼絾 Stage 1 鍏?SCR锛?

```text
Use $academic-research-suite to start academic-pipeline.
Stage 1 璜嬪厛鐢?deep-research socratic mode锛屽洜鐐烘垜鐩墠鍙湁妯＄硦涓婚銆?
Stop after the RQ Brief and pipeline dashboard.
```

## Smoke tests

Codex app / interactive CLI锛?

```text
/skills
```

闋愭湡锛氬彧鐪嬪埌涓€鍊?ARS 鍏ュ彛銆?

Router smoke锛?

```text
Use $academic-research-suite.
鎴戞兂鍋氫竴绡囪珫鏂囷紝椤岀洰鏂瑰悜鏄?AI adoption in higher education quality assurance銆?
鎴戦倓娌掓湁鏄庣⒑ research question銆?
```

闋愭湡锛氶€插叆 `deep-research` `socratic` mode銆?

Codex CLI锛?

```bash
codex exec --ephemeral --sandbox read-only \
  -C /path/to/academic-research-skills-codex \
  'Use $academic-research-suite. Router smoke test only. User request to classify: 鎴戞兂鍋氫竴绡囪珫鏂囷紝椤岀洰鏂瑰悜鏄?AI adoption in higher education quality assurance锛屼絾鎴戦倓娌掓湁鏄庣⒑ research question銆?According to the academic-research-suite router, classify the workflow and mode.'
```

## 涓嶄唬琛ㄥ畨瑁濆け鏁楃殑 Codex 璀﹀憡

鐪嬪埌涓嬪垪瑷婃伅涓嶄唬琛?ARS 瀹夎澶辨晽锛?

- `[features].codex_hooks is deprecated`锛氭湁绌哄啀鏇存柊 Codex config 鍗冲彲銆侫RS
  Codex 姝ｅ父浣跨敤涓嶉渶瑕?hooks銆?
- `hooks need review before they can run`锛氬鏋滀綘鏈変娇鐢ㄩ偅浜?hooks锛屽啀鍙﹀瀵╂牳鍗冲彲銆傛湰
  package vendored 鐨?Claude hooks 鍙綔 traceability锛屼笉鏈冭 Codex 瀹夎鎴栧煼琛屻€?

## 閬哥敤鏈宸ュ叿

Markdown 杓稿嚭涓嶉渶瑕侀澶栧伐鍏枫€傚彧鏈夊湪闇€瑕佺┅瀹氭湰姗熻綁妾旀垨 corpus adapter 鏅傛墠瀹夎涓嬪垪宸ュ叿銆?

### DOCX 杓稿嚭

鐩存帴鐢㈢敓 `.docx` 闇€瑕?Pandoc銆傝嫢娌掓湁 Pandoc锛孉RS Codex 鎳夊洖閫€鐐?
Markdown 鍔犺綁妾旇鏄庛€?

```bash
# macOS
brew install pandoc

# Linux (Debian/Ubuntu)
sudo apt-get install pandoc
```

### LaTeX / PDF 杓稿嚭

PDF 杓稿嚭闇€瑕?`tectonic` 鑸囩浉闂滃瓧鍨嬨€傞€欐槸閬哥敤鍔熻兘銆?

```bash
# macOS
brew install tectonic

# Linux (Debian/Ubuntu)
curl --proto '=https' --tlsv1.2 -fsSL https://drop-sh.fullyjustified.net | sh
```

APA 7 涓枃杓稿嚭寤鸿瀛楀瀷锛?

- Times New Roman
- Source Han Serif TC VF / Noto Serif TC
- Courier New

### Adapter 渚濊炒

Material Passport reference adapters 浣跨敤 vendored `requirements-dev.txt`锛?

```bash
cd skills/academic-research-suite/ars
python -m pip install -r requirements-dev.txt
```

## Material Passport `literature_corpus[]` adapters

# REDACTED: sensitive-looking memory line
`passport.yaml` 浜ょ郸 Codex銆?

寰?vendored ARS root 鍩疯锛?

```bash
cd skills/academic-research-suite/ars

python scripts/adapters/folder_scan.py \
  --input /path/to/pdfs \
  --passport passport.yaml \
  --rejection-log rejection_log.yaml

python scripts/adapters/zotero.py \
  --input my-zotero-export.json \
  --passport passport.yaml \
  --rejection-log rejection_log.yaml

python scripts/adapters/obsidian.py \
  --input ~/Obsidian/Lit\ Notes \
  --passport passport.yaml \
  --rejection-log rejection_log.yaml
```

Consumer protocol 鑸?upstream ARS 鐩稿悓锛歚bibliography_agent` 鑸?
`literature_strategist_agent` 鍦ㄥ伒娓埌闈炵┖涓斿彲瑙ｆ瀽鐨?corpus 鏅傦紝鎺?
corpus-first / search-fills-gap 琛岀偤銆傝┏瑕?
[`academic-pipeline/references/literature_corpus_consumers.md`](../academic-pipeline/references/literature_corpus_consumers.md)銆?

## 閬哥敤鐠板璁婃暩

鎵€鏈?flag 閮芥槸 opt-in銆?

| Flag | Codex 琛岀偤 |
|---|---|
| `ARS_SOCRATIC_READING_PROBE=1` | workflow 閫插叆 `socratic_mentor_agent` prompt 鏅傦紝鍟熺敤 Socratic reading-check probe銆?|
# REDACTED: sensitive-looking memory line
| `ARS_CLAIM_AUDIT=1` | workflow 閫插叆 upstream 灏嶆噳璺緫鏅傦紝鍟熺敤閬哥敤鐨?v3.8 claim-reference alignment audit gate銆?|
# REDACTED: sensitive-looking memory line
| `ARS_CROSS_MODEL_SAMPLE_INTERVAL` | 鏄庣⒑鍟熺敤 cross-model review 鏅傜殑 advisory sampling interval銆?|
# REDACTED: sensitive-looking memory line
| `OPENALEX_POLITE_EMAIL`, `CROSSREF_POLITE_EMAIL` | ARS v3.9.0 OpenAlex / Crossref triangulation clients 鐨勯伕鐢?polite-pool 璀樺垾璩囪▕銆?|

Upstream GPT/Gemini cross-model 绡勪緥鍦?Codex package 瑁′笉鍟熺敤銆備笉瑕佺偤
# REDACTED: sensitive-looking memory line
Codex 鏈韩宸叉彁渚涗富瑕?OpenAI model銆?

## 鐒℃硶鐩存帴瑜囪＝鐨?Claude Code 鍔熻兘

| Claude Code 鍔熻兘 | Codex 鐙€鎱?|
|---|---|
| `/plugin marketplace add` / `/plugin install` | 涓嶆敮鎻淬€傝珛鎶婃湰 repo 瀹夎鐐?Codex skill銆?|
| 鍘熺敓 `/ars-*` slash command 瑷诲唺 | 涓嶆敮鎻淬€傛敼鐢?`$academic-research-suite` 鍏х殑 `ars-*` alias銆?|
| `skills/` symlink 鑷嫊鎺㈢储 | 鏀圭偤鍠竴 Codex router skill銆?|
| plugin-shipped `agents/` | 浣滅偤 role prompt 鍏ц伅浣跨敤锛屼笉鑷嫊 dispatch銆?|
| Claude Code Agent Team / Task tool | Codex subagents 鍙湁鍦ㄤ娇鐢ㄨ€呮槑纰鸿姹傚娲炬垨骞宠 agent work 鏅傛墠浣跨敤銆?|
# REDACTED: sensitive-looking memory line
| `model: opus` / `model: sonnet` command routing | 涓嶄綔 routing 鎺у埗锛汣odex 浣跨敤鐩墠 active model銆?|
| plugin auto-update | 涓嶆敮鎻达紱鏇存柊鏂瑰紡鏄噸鏂板畨瑁濇垨 pull Codex repo銆?|

## 闁嬬櫦椹楄瓑

寰?Codex repo root 鍩疯锛?

```bash
python -m json.tool skills/academic-research-suite/manifest.json
python skills/academic-research-suite/ars/scripts/check_data_access_level.py --path skills/academic-research-suite/ars
python skills/academic-research-suite/ars/scripts/check_task_type.py --path skills/academic-research-suite/ars
```

Upstream pytest 璜嬪緸 vendored ARS root 鍩疯锛屽洜鐐烘脯瑭︽渻 import
`scripts.*`锛?

```bash
cd skills/academic-research-suite/ars
python -m pytest --tb=short -q
```

Codex package 宸插湪鍙铏曡 nested path lookup銆傜涓€娆?vendor銆佷絾鏈?repo Git
history 灏氭湭鍖呭惈 upstream v3.6.7 manifest 鏅傦紝
`scripts/check_v3_6_8_pattern_protection.py` 鏈?fallback 鍒?
`scripts/codex_v3_6_7_block_baseline.json`锛屽洜姝?byte-equivalence check 浠嶆渻鎶撳埌
protected block mutation锛屼笉鏈冨洜鐐虹己 Git baseline 鑰岃嚜鎴戝熀婧栧寲銆?
