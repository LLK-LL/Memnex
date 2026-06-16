# REDACTED: sensitive-looking memory line

# REDACTED: sensitive-looking memory line
`涓枃鏍稿`, `涓嫳瀵圭収`, `瀹＄鎰忚鍥炲`, `閫愮偣鍥炲`, `淇洖淇, `澶т慨鍥炲`, or `灏忎慨鍥炲`.

## Default behavior

# REDACTED: sensitive-looking memory line
- Draft the final point-by-point response letter in English unless the user explicitly asks for Chinese only.
# REDACTED: sensitive-looking memory line
- Translate intent, not literal wording.
- Convert vague Chinese notes into concrete response evidence requirements.

## Common Chinese note conversions

| Chinese note | Problem | Better handling |
|---|---|---|
| `鎴戜滑宸茬粡鏀逛簡` | Too vague | Ask what changed, where it appears, and whether revised text is available |
# REDACTED: sensitive-looking memory line
| `鎴戜滑琛ヤ簡瀹為獙` | Missing evidence | Request experiment name, conditions, replicate/sample details, result summary, and figure/table location |
| `鎴戜滑琛ヤ簡鍒嗘瀽` | Missing analysis detail | Request analysis method, data source, key result, statistical output, and manuscript location |
| `杩欎釜闂涓嶉噸瑕乣 | Defensive and unsupported | Reframe as scope, evidence, or claim-boundary reasoning if scientifically justified |
| `鐢变簬鏃堕棿鍘熷洜娌″仛` | High-risk excuse | Replace with study-design or scope boundary only if true; otherwise flag risk |
| `瀹＄浜鸿瑙ｄ簡` | Accusatory | Reframe as manuscript clarity issue and add clarification |
| `璇﹁姝ｆ枃` | Not traceable | Require section, page, line, figure, table, or supplement |
| `鎴戜滑璁や负瓒冲浜哷 | Unsupported sufficiency claim | Explain what evidence addresses the concern or mark remaining limitation |

## Chinese confirmation section

Use concise Chinese action notes:

```text
涓枃鏍稿
- R1.1: 璇疯ˉ鍏呴獙璇佸垎鏋愮殑涓昏缁撴灉銆佹牱鏈噺鎴栨暟鎹泦瑙勬ā锛屼互鍙?Fig. 5 瀵瑰簲鐨勬鏂囦綅缃€?
- R1.2: 璇风‘璁ょ粺璁℃楠屽悕绉般€侀噸澶嶅崟浣嶃€佹牱鏈噺鍜屽閲嶆楠屾牎姝ｆ柟娉曘€?
- R2.1: 鐩墠涓嶈兘澹扮О宸插畬鎴愬姩鐗╅獙璇侊紱寤鸿鏀逛负鑼冨洿璇存槑 + Discussion limitation銆?
```

## Bilingual drafting pattern

When the user supplies Chinese notes:

1. Preserve reviewer comments in their supplied language unless asked to translate.
2. Build the tracker using English action labels.
3. Draft the response letter in polished English.
4. Add `涓枃鏍稿` only for decisions, missing facts, and high-risk issues.

## Tone correction examples

# REDACTED: sensitive-looking memory line

```text
瀹＄浜烘病鏈夌悊瑙ｆ垜浠殑鏂规硶銆?
```

Response stance:

```text
We agree that the original Methods description did not make this distinction sufficiently clear.
We have revised the Methods to clarify [specific distinction and location].
```

# REDACTED: sensitive-looking memory line

```text
杩欎釜瀹為獙瓒呭嚭浜嗘垜浠殑鑳藉姏銆?
```

Response stance:

```text
We agree that this experiment would provide an additional test of [claim]. However, it would require
[new cohort/system/longitudinal design], which is outside the scope of the present study. We have
therefore softened the claim and added a limitation in [location].
```
