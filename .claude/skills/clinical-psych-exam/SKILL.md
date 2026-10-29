---
name: clinical-psych-exam
description: Run the clinical-psych-exam-agent GitHub workflow for Taiwan clinical psychologist national examination mock tests, child/adolescent or other clinical domains, paired A/B DOCX delivery, and independent file acceptance. Use for requests containing this repository URL or asking for a clinical psychologist exam.
---

# 臨床心理師命題 Agent — Claude Code discovery entry

This is a **discovery adapter**, not a separate set of clinical exam rules. Read the full portable skill at `.agents/skills/clinical-psych-exam/SKILL.md` in the repository root, followed by the canonical `START_HERE.md`, `config/simulation_policy.yaml`, `release/current_release.yaml` and `agent/system_prompt.md` according to that skill.

The expected output is **two real Word files in the first final reply**, one for 甲卷 and one for 乙卷, each with its own answer key and explanations. If attachments are not possible, immediately state `Word 尚未交付`; never invent sandbox/download paths. Default is 20 items per form unless the user specifies N, which means N **per** form. No mocked clinical questions or paid-model fallback; preserve the approved `formal-v1.0` release.

This file is for clients that discover repository-local Claude Skills; simply pasting the GitHub URL into claude.ai does **not** guarantee automatic skill installation or document-generation tools.
