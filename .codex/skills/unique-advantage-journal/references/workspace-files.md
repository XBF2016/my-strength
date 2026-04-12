# Workspace Files

Use these workspace files to keep the process stable across new threads.

## Required Files

- `strength-system/protocol.md`
- `strength-system/case-library.md`
- `strength-system/case-index.json`

## Protocol File

`strength-system/protocol.md` should contain:

- the fixed three-point definition of unique advantage
- the hybrid collaboration workflow
- the scoring rules
- a short recommended start prompt

## Case Library File

`strength-system/case-library.md` should contain:

- a short header that repeats the three-point definition
- the record template
- an `Entries` section where new cases are appended
- a `Hypothesis Notes` section for low-evidence but useful leads
- an optional `Review Notes` section for cross-case summaries

## Case Index File

`strength-system/case-index.json` is the generated helper index.

- Treat `strength-system/case-library.md` as the source of truth.
- Rebuild the index after every archive change.
- Use the index for fast listing, counting, and review overviews.
- If the index is missing or stale, regenerate it from the library.

## Standard Record Format

Use this exact section structure for each new case:

```markdown
## 正式案例 00X - <short title>

- 日期: YYYY-MM-DD
- 来源: 用户口述案例
- 长期可持续性评分: 0-2
- 学习速度评分: 0-2
- 外部验证评分: 0-2
- 初步判断: strong signal | possible signal | insufficient evidence

### 事实
<what happened, what the user did, and the outcome>

### 长期可持续性信号
<evidence for whether the user can keep doing this kind of work over time>

### 学习速度信号
<evidence for whether the user learned or organized faster than most people>

### 结果与外部验证
<evidence that the result was better and reality confirmed it>

### 备注
<short caveats, missing evidence, or follow-up items>
```

## Hypothesis Note Format

Use this structure when the input is mainly speculative or preference-based:

```markdown
## 假设线索 00X - <short title>

- 日期: YYYY-MM-DD
- 来源: 用户口述线索
- 状态: 假设线索

### 这条线索说明什么
<possible direction, preference, or management style signal>

### 为什么还不能算正式证据
<what is still missing: real event, result, or external validation>

### 需要什么证据来升级
<specific future facts worth collecting>
```

## Review Format

When the user asks for a periodic review, append a short note under `Review Notes`:

```markdown
## Review YYYY-MM-DD

- Cases reviewed: 00X, 00Y, 00Z
- Repeated patterns:
- Strongest candidate advantage directions:
- Weak or missing evidence:
- Next cases worth collecting:
```
