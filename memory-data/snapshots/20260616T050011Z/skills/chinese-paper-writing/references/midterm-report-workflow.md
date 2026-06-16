# Midterm Report Workflow

## Purpose

Use this reference when drafting, restructuring, or reviewing a Chinese master's thesis midterm report or related defense material.

## Inputs To Request Or Infer

- School or department template, if available
- Thesis title and research direction
- Supervisor requirements
- Completed work
- Datasets, systems, experiments, figures, tables, and metrics
- Current problems and next-stage plan
- Required word count or page limit

If inputs are missing, proceed with placeholders such as `[寰呰ˉ鍏咃細鏁版嵁闆嗗悕绉癩` and keep the surrounding prose usable.

## Recommended Structure

### 1. 璇鹃鑳屾櫙涓庣爺绌舵剰涔?
Write from broad context to specific problem. Avoid grand claims. A strong paragraph usually contains:

1. Field context
2. Concrete technical problem
3. Why existing methods or systems are insufficient
4. Why the thesis topic is worth studying

### 2. 鍥藉唴澶栫爺绌剁幇鐘?
Organize by technical line, not by paper list. For each line:

- define the line
- name representative methods or systems
- summarize strengths
- identify limitations relevant to the thesis
- transition to why the proposed work is needed

Avoid "A proposed..., B proposed..., C proposed..." chains unless the user asks for a chronological survey.

### 3. 鐮旂┒鐩爣涓庝富瑕佸唴瀹?
Separate goals from tasks:

- Goal: the higher-level capability or problem the thesis aims to address
- Content: concrete modules, experiments, algorithms, systems, or analyses

Use numbered items when the template expects them. Each item should start with a research action: 鏋勫缓, 璁捐, 鎻愬嚭, 瀹炵幇, 璇勪及, 鍒嗘瀽, 楠岃瘉.

### 4. 鎶€鏈矾绾夸笌鐮旂┒鏂规硶

Write as a pipeline:

1. Input data or problem setting
2. Preprocessing or representation
3. Core method or model
4. Training, inference, or system implementation
5. Evaluation protocol
6. Expected output

For figures, describe what each block does and how information flows between blocks.

### 5. 宸插畬鎴愬伐浣滀笌闃舵鎬ф垚鏋?
Be concrete and restrained. Good evidence includes:

- implemented modules
- completed experiments
- preliminary metrics
- figures/tables
- datasets prepared
- code repository state
- manuscript or report sections completed

Use "鍒濇缁撴灉琛ㄦ槑" when the evidence is early. Avoid final-paper language if experiments are incomplete.

### 6. 瀛樺湪闂涓庤В鍐虫€濊矾

Name problems as research risks, not excuses:

- 鏁版嵁瑙勬ā鎴栬川閲忎笉瓒?- 瀵规瘮瀹為獙涓嶅厖鍒?- 娑堣瀺瀹為獙灏氭湭瀹屾垚
- 妯″瀷娉涘寲鑳藉姏鏈夊緟楠岃瘉
- 绯荤粺鏁堢巼鎴栫ǔ瀹氭€т粛闇€浼樺寲
- 璁烘枃缁撴瀯鍜屽浘琛ㄨ〃杈鹃渶杩涗竴姝ュ畬鍠?
Each problem should have a matching solution or next action.

### 7. 鍚庣画璁″垝涓庤繘搴﹀畨鎺?
Use time-bounded milestones:

- 鏂囩尞琛ュ厖涓庨棶棰樺嚌缁?- 鏂规硶鏀硅繘涓庢ā鍧楀疄鐜?- 瀹為獙琛ュ厖涓庢秷铻嶅垎鏋?- 璁烘枃鎾板啓涓庡浘琛ㄦ暣鐞?- 棰勭瓟杈╀慨鏀逛笌瀹氱

Prefer month ranges or week ranges if the user provides a deadline.

## Defense Slide Conversion

For PPT, compress the report into:

1. 鐮旂┒鑳屾櫙
2. 闂瀹氫箟
3. 鐮旂┒鍐呭
4. 鎶€鏈矾绾?5. 闃舵鎴愭灉
6. 鍚庣画璁″垝
7. 璇疯€佸笀鎵硅瘎鎸囨

Each slide should carry one claim, one figure/table/list, and one spoken takeaway.
