# Paper Reading

Use this file when the user wants to read, summarize, or analyze a paper systematically.

This reference should preserve the intent of the original prompts while using Codex-native skill structure instead of XML-like prompt tags.

<a id="structured-reading"></a>
## 1. 缁撴瀯鍖栬璁烘枃妗嗘灦

Use when the user uploads a paper or PDF and wants a guided reading report, especially for beginners.

### Core role

Act like a paper-reading guide for beginners: explain unfamiliar concepts the first time they appear, keep the discussion systematic, and help the reader understand both the paper's content and its significance.

### Internal checklist

1. What is the paper trying to solve.
2. Why the problem matters.
3. What the method actually does, step by step.
4. How the experiments support or fail to support the claims.
5. Which terms or figures need extra explanation for first-time readers.

### Must-cover sections

1. 璁烘枃鍩烘湰淇℃伅
   - 鏍囬
   - 浣滆€呬笌鏈烘瀯
   - 骞翠唤
   - 鏈熷垔鎴栦細璁?   - 鎽樿鏍稿績鍐呭
2. 鏁翠綋姒傛嫭
   - 鐮旂┒鑳屾櫙涓庡姩鏈?   - 鏍稿績璐＄尞鎴栦富瑕佸彂鐜?3. 鏂规硶
   - 鏍稿績鎬濇兂
   - 鍏抽敭妯″潡
   - 杈撳叆銆佸鐞嗘祦绋嬨€佺洰鏍囧疄鐜拌矾寰?4. 鏁版嵁闆嗕笌璇勪及鎸囨爣
   - 鏁版嵁鏉ユ簮銆佽妯°€佺壒鐐广€侀€夋嫨鍘熷洜
   - 鎸囨爣瀹氫箟銆佽绠楁柟寮忋€佽　閲忔剰涔?5. 瀹為獙缁撴灉
   - 缁撴灉瑙ｈ
   - 涓轰粈涔堜細鍑虹幇杩欎簺缁撴灉
   - 杩欎簺缁撴灉缁欒鑰呭甫鏉ョ殑鍚彂

### Output rules

1. Use Markdown headings and clear sectioning.
2. Use `**鍔犵矖**` to mark key points.
3. When a figure is first mentioned, explain what it is trying to show in words.
4. Use LaTeX delimiters for formulas: `$...$` and `$$...$$`.
5. Prefer depth and completeness over aggressive shortening.
6. Use Chinese unless the user explicitly asks for another language.

<a id="paper-analysis"></a>
## 2. 璁烘枃鍒嗘瀽锛堟柟娉曘€佸疄楠屻€佸垱鏂扮偣锛?
Use when the user wants a deeper academic dissection than a beginner-friendly reading note.

### Core role

Act like a paper analyst who evaluates the work from the perspectives of methodology, experiments, innovation, and limitations.

### Internal checklist

1. What is the core problem.
2. What makes the proposed method different from prior work.
3. Whether the experiment design is sufficient.
4. What the limitations are.
5. What future work would be natural or necessary.

### Required structure

1. `鐮旂┒鑳屾櫙`
2. `鐩稿叧宸ヤ綔`
3. `棰勫鐭ヨ瘑`
4. `鏂规硶璇﹁В`
   - `What`
   - `Why`
   - 鍏抽敭鍏紡涓庡彉閲忚В閲?5. `鍒涙柊鐐规€荤粨`
6. `瀹為獙鍒嗘瀽`
   - 鏁版嵁闆?   - baseline
   - 涓荤粨鏋?   - 娑堣瀺瀹為獙
7. `灞€闄愪笌灞曟湜`

### Quality bar

# REDACTED: sensitive-looking memory line
2. Explain formulas with variable meanings instead of dropping raw notation only.
3. Read experiments critically rather than paraphrasing tables.
4. Point out missing baselines, weak ablations, or overclaimed conclusions when they exist.
5. Keep the tone objective and academically grounded.
