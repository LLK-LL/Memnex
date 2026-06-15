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

If inputs are missing, proceed with placeholders such as `[待补充：数据集名称]` and keep the surrounding prose usable.

## Recommended Structure

### 1. 课题背景与研究意义

Write from broad context to specific problem. Avoid grand claims. A strong paragraph usually contains:

1. Field context
2. Concrete technical problem
3. Why existing methods or systems are insufficient
4. Why the thesis topic is worth studying

### 2. 国内外研究现状

Organize by technical line, not by paper list. For each line:

- define the line
- name representative methods or systems
- summarize strengths
- identify limitations relevant to the thesis
- transition to why the proposed work is needed

Avoid "A proposed..., B proposed..., C proposed..." chains unless the user asks for a chronological survey.

### 3. 研究目标与主要内容

Separate goals from tasks:

- Goal: the higher-level capability or problem the thesis aims to address
- Content: concrete modules, experiments, algorithms, systems, or analyses

Use numbered items when the template expects them. Each item should start with a research action: 构建, 设计, 提出, 实现, 评估, 分析, 验证.

### 4. 技术路线与研究方法

Write as a pipeline:

1. Input data or problem setting
2. Preprocessing or representation
3. Core method or model
4. Training, inference, or system implementation
5. Evaluation protocol
6. Expected output

For figures, describe what each block does and how information flows between blocks.

### 5. 已完成工作与阶段性成果

Be concrete and restrained. Good evidence includes:

- implemented modules
- completed experiments
- preliminary metrics
- figures/tables
- datasets prepared
- code repository state
- manuscript or report sections completed

Use "初步结果表明" when the evidence is early. Avoid final-paper language if experiments are incomplete.

### 6. 存在问题与解决思路

Name problems as research risks, not excuses:

- 数据规模或质量不足
- 对比实验不充分
- 消融实验尚未完成
- 模型泛化能力有待验证
- 系统效率或稳定性仍需优化
- 论文结构和图表表达需进一步完善

Each problem should have a matching solution or next action.

### 7. 后续计划与进度安排

Use time-bounded milestones:

- 文献补充与问题凝练
- 方法改进与模块实现
- 实验补充与消融分析
- 论文撰写与图表整理
- 预答辩修改与定稿

Prefer month ranges or week ranges if the user provides a deadline.

## Defense Slide Conversion

For PPT, compress the report into:

1. 研究背景
2. 问题定义
3. 研究内容
4. 技术路线
5. 阶段成果
6. 后续计划
7. 请老师批评指正

Each slide should carry one claim, one figure/table/list, and one spoken takeaway.
