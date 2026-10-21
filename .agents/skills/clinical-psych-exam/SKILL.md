---
name: clinical-psych-exam
description: Apply the public clinical-psych-exam-agent GitHub rules to draft, review, check, and deliver Taiwan clinical psychologist national exam parallel papers (甲卷/乙卷), including child/adolescent clinical psychology, variable item counts, and first-response DOCX attachments. Use when a user shares this repository or asks to use this Agent.
compatibility: Requires repository file access. DOCX creation requires tools for local file generation and downloadable attachments; clinical source checking needs appropriate source access.
---

# 臨床心理師模擬考題 Agent — portable skill

This skill routes to the **canonical repository rules**; it does not replace them or carry model weights.

## Activate and read the source of truth

When the user provides `https://github.com/lily4318/clinical-psych-exam-agent` and a short task, retrieve from **repository root**, in order:

1. `START_HERE.md`
2. `config/simulation_policy.yaml`
3. `release/current_release.yaml`
4. `agent/system_prompt.md`
5. The task's domain blueprint, exam-history index, trusted clinical source material and release/review manifest as needed.
6. `docs/CROSS_PLATFORM_ACCEPTANCE.md`

Do not request that the user paste all files if the host can read them. If GitHub retrieval fails, disclose the source-reading limitation rather than inventing content.

## Interpret a short user task

- `兒童版` is **child/adolescent clinical psychologist exam subject matter** at professional examinee level.
- If no item count is specified, plan **20 questions in each form**; if the user says N, create **N in 甲卷 and N in 乙卷**, by proportionally reallocating the domain blueprint rather than cutting down the original 20 questions.
- Use the **latest five available official exam years** from the repository index; do not permanently lock the year window.
- Preserve `formal-v1.0` and all approved artifacts. New papers are draft/unverified unless and until the owner approves them.

## Generate and deliver real documents

1. Establish domain-appropriate evidence and generate two substantive, paired sets of questions with four A–D options, one defensible best answer, and correct/distractor rationales. Never use the repository's Stub/fixture as a real paper.
2. Clearly label unreviewed output `未經獨立專家驗證`. Do not imply automatically generated medical guidance or exam items have undergone independent expert validation.
3. Create **two real, distinct DOCX** files; each contains questions followed by that form's answer key and explanations.
4. Re-open the files and check file existence, integrity, question count, options, key and rationales. If the execution environment supports this repository's Python modules, you may additionally run `python -m src.verify_external_delivery form_a.docx form_b.docx --items N`.
5. In the **first final answer**, attach both actually verified files as clickable download links, clearly labelled `下載甲卷 Word` and `下載乙卷 Word`. Never invent file paths or claim links are accessible without evidence.
6. If the current host cannot create, inspect or attach files, state `Word 尚未交付` **in that same first answer** and specify what was/was not completed. Do not defer a promised attachment to a follow-up message.

## Evaluate honestly

The portable DOCX checker establishes document structure (G3), **not** host download access (G4), professional correctness (G5), or psychometric equivalence. Refer to `docs/CROSS_PLATFORM_ACCEPTANCE.md` for six separate gates; log unknowns as unknowns. Public users have read-only access to the author's repository and should not push results into it. Do not invoke paid model APIs or services merely to execute this skill.
