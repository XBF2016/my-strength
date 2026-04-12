# Workspace Files

Use these workspace files to keep the process stable across new threads.

## Required Files

- `strength-system/protocol.md`
- `strength-system/cases/`
- `strength-system/hypotheses/`
- `strength-system/reviews.md`
- `strength-system/case-index.json`

## Optional Generated File

- `strength-system/case-library.md`

## Protocol File

`strength-system/protocol.md` should contain:

- the fixed three-point definition of unique advantage
- the hybrid collaboration workflow
- the scoring rules
- a short recommended start prompt

## Case Files

Store each formal case as its own Markdown file under `strength-system/cases/`.

Use filenames like `001.md`, `002.md`, `003.md`.

Each file should contain exactly one formal case using this structure:

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

## Hypothesis Files

Store each low-evidence note as its own Markdown file under `strength-system/hypotheses/`.

Use filenames like `001.md`, `002.md`, `003.md`.

Each file should contain exactly one hypothesis note using this structure:

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

## Review File

Store cross-case review notes in `strength-system/reviews.md`.

## Review Format

When the user asks for a periodic review, append a short note to `strength-system/reviews.md`:

```markdown
## Review YYYY-MM-DD

- Cases reviewed: 00X, 00Y, 00Z
- Repeated patterns:
- Strongest candidate advantage directions:
- Weak or missing evidence:
- Next cases worth collecting:
```

## Case Index File

`strength-system/case-index.json` is the generated helper index.

- Treat `strength-system/cases/`, `strength-system/hypotheses/`, and `strength-system/reviews.md` as the source of truth.
- Rebuild the index after every archive change.
- Use the index for fast listing, counting, and review overviews.
- Keep the index lightweight and summary-only. Prefer storing only compact metadata such as `id`, `title`, `path`, `date`, scores, and judgment or status.
- Do not duplicate display labels, section labels, or other presentation-only fields in the index.
- If the index is missing or stale, regenerate it from the source files.

## Generated Overview File

`strength-system/case-library.md` is an optional generated overview for quick human browsing.

- Do not treat it as the source of truth.
- Regenerate it together with the index after archive changes.
- If the workspace still uses a legacy single-file archive as the source of truth, migrate it first.
