# AGENTS.md — 臨床心理師國考命題 Agent

This is a portable instruction entry point for AI **coding agents** that open or work with this repository. A chat AI given only the GitHub URL may read this file, but URL sharing **does not install a model, mount the repository, enable code execution, or grant file-download capability**.

## Canonical sources — do not fork the rules here

Before answering a request to generate, review, or export a clinical psychologist exam, read these repository-root files in order:

1. `START_HERE.md` — short-task routing, first-response delivery, public read-only usage.
2. `config/simulation_policy.yaml` — latest 5 available exam years, default 20 items per form, dynamic N.
3. `release/current_release.yaml` — actual release state and protected formal release.
4. `agent/system_prompt.md` — exam-writing, clinical evidence, parallel-form, and approval rules.
5. Task-specific domain blueprint, source catalog, manifest, and review files.
6. `docs/CROSS_PLATFORM_ACCEPTANCE.md` — independent G1–G6 acceptance, including download verification.

`START_HERE.md` and the linked policies take precedence over this short navigation file. If your host loads Agent Skills, see `.agents/skills/clinical-psych-exam/SKILL.md`; Claude Code-compatible agents may use `.claude/skills/clinical-psych-exam/SKILL.md`.

## Expected exam behavior

- "兒童版" means child/adolescent **clinical psychologist licensing-exam subject matter**, not questions for children to answer.
- Unspecified question count: **甲卷20題、乙卷20題**. Explicit N: **N per form** (for example, 3 or 10 each). Reallocate the domain blueprint; never truncate the first N of a 20-item plan.
- Determine the current historical window from the exam index when possible; do not freeze 111–115 as a permanent rule.
- Newly written questions require substantive trustworthy sources, one defensible best answer, four options A–D and option-by-option rationale. Distinguish provisional source lists from passages actually read and corroborated.
- New drafts must be clearly labelled **未經獨立專家驗證**; do not claim expert review, psychometric equivalence or 90% validity from model self-evaluation or pytest.
- When Word is requested, deliver **two genuinely created and verified DOCX attachments in the first final reply**, with answers and rationales appended to each form. Both links must work in the recipient's platform. If the host cannot generate/attach files, explicitly say **Word 尚未交付** in that first reply. Never fabricate a sandbox path.
- Generic conversational AI may compose genuine items with its own permitted inference and file tools; it need not have the author's Ollama installed. Never present a `StubQuestionProvider`, fake sources, mocked clinical questions, or a CI fixture as a real generated paper.

## Artifact checks and honest limits

- In a Python-enabled environment, run the repository's native exporter only when the required inputs are available and valid.
- For DOCX output created by any AI, run:
  `python -m src.verify_external_delivery form_a.docx form_b.docx --items N`
- This verifies **document structure (G3)** only. The model/host must separately establish **that both download links worked in the first reply (G4)**, and experts must separately evaluate clinical correctness (G5).
- Do not claim an external platform was tested unless there is an actual independent trial and audit trail.

## Repository modification rules for coding agents

- Public consumers default to **read-only**. Do not push changes to the author's GitHub repository without explicit authorization.
- Existing `formal-v1.0`, approved items, answers and approved blueprints are immutable without the owner's new explicit approval.
- For authorized development, use an isolated branch/PR, run `python -m pytest`, inspect the actual GitHub Actions result and preserve rollback information; do not merge an unverified change.
- Never enable paid APIs, fine-tuning, paid runners or external hosting without the user's explicit consent. Preserve training/development vs truly held-out expert review separation.
