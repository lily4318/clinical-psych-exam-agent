"""Guarded child/adolescent exam generation to two DOCX files.

A separate candidate pipeline: no legacy substance-use blueprint, no Stub,
no paid API and no changes to existing approved releases. It does NOT certify
the factual correctness of model-written clinical material.
"""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Callable, Mapping
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from .domain_blueprints import build_child_pair_specs, load_domain_blueprint
from .export_docx import _safe_slug, export_parallel_docx
from .verify_external_delivery import normalize_question_stem, verify_pair
from .ollama_provider import OllamaLocalJsonCallback
from .child_source_fetch import fetch_official_guidance_evidence

LETTERS = "ABCD"
DRAFT_VERSION = "child-unverified-v0.1"
BANNED_PLACEHOLDERS = ("[STUB]", "TODO", "TBD", "待補", "待填", "範例題幹")
SYSTEM_RULES = (
    "你是臺灣臨床心理師國考兒童／青少年臨床心理命題 Agent。"
    "考生是臨床心理師，不是兒童。每一組應產出不同情境的甲、乙平行題，"
    "各有四個選項、單一最佳答案與逐項解析。"
    "只能參考本次提供的臨床指引摘錄，不可捏造診斷準則、藥理、安全處置"
    "或來源；摘錄不足時回報 source_insufficient=true。"
    "不得自稱已經專家審查、使用者核可或正式發布。請只輸出合法 JSON object。"
)


def _substantive(value: Any) -> bool:
    return (
        isinstance(value, str)
        and bool(value.strip())
        and not any(banned.casefold() in value.casefold() for banned in BANNED_PLACEHOLDERS)
    )


def _preflight_evidence(
    specs: list[dict[str, Any]],
    catalog: Mapping[str, Any],
    evidence: Mapping[str, Any],
) -> dict[str, list[dict[str, str]]]:
    """Require explicit source excerpts BEFORE contacting the local model.

    Provenance and presence checks are deterministic. Whether excerpts really
    support future generated clinical claims requires external verification.
    """
    if not isinstance(evidence, Mapping):
        raise ValueError("Source evidence must be a JSON object keyed by source_id.")

    contexts: dict[str, list[dict[str, str]]] = {}
    for spec in specs:
        chosen: list[dict[str, str]] = []
        for source_id in spec["source_ids"]:
            if source_id not in evidence:
                continue
            source = catalog[source_id]
            supplied = evidence[source_id]
            if not isinstance(supplied, dict):
                raise ValueError(f"{source_id}: evidence must be an object.")
            if supplied.get("url") != source["url"]:
                raise ValueError(f"{source_id}: evidence URL does not match the blueprint.")
            passage = supplied.get("passage")
            if not _substantive(passage) or len(passage.strip()) < 30:
                raise ValueError(f"{source_id}: a substantial original passage is required.")
            retrieved_at = supplied.get("retrieved_at")
            if not _substantive(retrieved_at):
                raise ValueError(f"{source_id}: retrieved_at is required for audit.")
            chosen.append({
                "source_id": source_id,
                "title": source["title"],
                "url": source["url"],
                "excerpt": passage.strip(),
                "retrieved_at": retrieved_at.strip(),
                "verification_status": "provided_excerpt_not_semantically_verified",
            })
        if not chosen:
            raise ValueError(
                f"{spec['pair_id']} ({spec['category']}): missing clinical source "
                "passage; refuse generation rather than inferring from a bare URL."
            )
        contexts[spec["pair_id"]] = chosen
    return contexts


def _request(spec: dict[str, Any], evidence: list[dict[str, str]], number: int) -> dict:
    # Balanced answer letters for any N; do not call the legacy fixed-P01-P20 planner.
    a_answer = LETTERS[(number - 1) % 4]
    b_answer = LETTERS[(number + 1) % 4]
    return {
        "system_instruction": SYSTEM_RULES,
        "task": "依兒少專屬藍圖與附帶來源摘錄建立甲乙兩道平行四選一臨床模擬試題。",
        "pair_spec": {
            "pair_id": spec["pair_id"],
            "category": spec["category"],
            "core_topic": spec["core_topic"],
            "difficulty": spec["difficulty"],
            "cognitive_level": spec["cognitive_level"],
            "equivalence_note": spec["equivalence_note"],
        },
        "forms": [
            {"form": "甲卷", "item_id": spec["form_a_item"], "target_answer_position": a_answer},
            {"form": "乙卷", "item_id": spec["form_b_item"], "target_answer_position": b_answer},
        ],
        "source_context": evidence,
        "constraints": [
            "正確答案須符合每卷指定的 target_answer_position。",
            "甲乙題幹須為不同情境，不可只更換人名或數值。",
            "兩題皆須附逐項 A-D 解析與具體正解依據。",
            "sources 只能列出本次 source_context 的 source_id。",
            "來源摘錄不足時停止；不可以虛構、猜測或引用純網址當作證據。",
            "僅生成題幹、四選項、正確答案、正解及A-D逐項解析、引用來源ID。",
            "題號、卷別、配對ID、領域、難度、認知層次及草稿標示由程式填入，不要重複輸出。",
            "原始摘錄存在不代表臨床主張已通過專家驗證。",
            "所有新題均為草稿，絕不可標成正式核可。",
        ],
        "output_contract": {
            "type": "object",
            "required": ["form_a", "form_b"],
            "item_fields": ["stem", "options", "correct_answer", "rationale", "sources"],
            "rationale_fields": ["correct", "A", "B", "C", "D"],
            "omit_deterministic_metadata": [
                "item_id", "form", "pair_id", "category", "subtopic",
                "difficulty", "cognitive_level", "quality_status",
            ],
        },
    }


def _single_form_request(
    pair_request: dict[str, Any], form_key: str, previous_stem: str | None = None,
    *, repair_duplicate_options: bool = False,
    repair_identical_stem: bool = False,
    repair_repeated_stem: bool = False,
) -> dict[str, Any]:
    """Ask a small local model for ONE bounded JSON item, preserving pair planning.

    Only source IDs and excerpts are sent to the model; full provenance was
    already preflighted and remains in the deterministic export catalog.
    """
    slot = pair_request["forms"][0 if form_key == "form_a" else 1]
    request = {
        "system_instruction": (
            "你是臺灣臨床心理師國考兒童／青少年領域命題 Agent。"
            "考生是臨床心理師。只產生一題四選一、單一最佳答案的草稿。"
            "只根據所附官方來源原文；不足時回傳 source_insufficient=true，"
            "不得編造診斷、藥理、答案或引用，不得自稱專家核可。"
            "僅回傳合法 JSON object，不要輸出說明文字。"
        ),
        "task": (
            "依照配對考點只產生本卷一題，請回傳 {item: {...}}。"
            "item 必須含 stem、options(A,B,C,D)、correct_answer、"
            "rationale(correct,A,B,C,D)、sources(來源ID陣列)。"
            "四個選項必須各自具體、彼此不同，不得複製同一內容或只改標籤。"
            "每個選項解析須各自具體說明正誤，文字精簡但不能省略。"
            "答案位置必須符合 form.target_answer_position；"
            "僅當所有提供的摘錄都無法支持本考點的安全命題時，才回報 source_insufficient=true；"
            "若其中至少一份摘錄能直接支持題幹、正解與 A-D 逐項解析，"
            "請完成 item，並省略 source_insufficient 或填 false。"
            "不得為避免拒答而捏造來源未提及的臨床事實。"
            "sources 陣列只能填 allowed_source_ids 中的完整 ID，"
            "不得引用其他指引、縮寫、標題或自行產生的來源名稱；"
            "不能確定引用是否受到摘錄支持時回報來源不足。"
            "不要輸出題號、卷別、難度、核可狀態等程式可填入的欄位。"
        ),
        "pair_spec": pair_request["pair_spec"],
        "form": slot,
        # An explicit, pair-specific whitelist is easier for a small model to
        # follow than extracting permitted citations from long source excerpts.
        # This is a prompt hint only; _check_item remains the fail-closed gate.
        "allowed_source_ids": sorted({
            source["source_id"] for source in pair_request["source_context"]
        }),
        "source_context": [
            {"source_id": source["source_id"], "excerpt": source["excerpt"]}
            for source in pair_request["source_context"]
        ],
        "output_contract": {
            "required": ["item"],
            "item_fields": ["stem", "options", "correct_answer", "rationale", "sources"],
            "rationale_fields": ["correct", "A", "B", "C", "D"],
        },
    }
    # Do not show the A stem to the B model: small deterministic models
    # sometimes copy the negative example verbatim. The validator still
    # compares both stems in Python and rejects any identical pair.
    if previous_stem is None:
        request["task"] += (
            "甲卷採個案初次呈現困擾的視角，題幹先描述主要問題，"
            "再考查來源支持的最佳評估或處遇判斷。"
        )
    else:
        request["task"] += (
            "乙卷應改用來源摘錄直接支持的另一臨床情境與決策角度，"
            "可採追蹤功能影響與多方資訊的視角，但不可強制加入來源未提及的"
            "追蹤程序、量表或臨床主張；也可選擇來源明示的辨識、評估或轉介情境。"
            "不得沿用甲卷題幹，亦不得只更換姓名、年齡或數字。"
            "若來源不足以支持另一個具單一最佳答案的安全情境，"
            "請回報 source_insufficient=true，絕不可捏造。"
        )
    if repair_identical_stem:
        # Regenerate the entire B item once; do not edit clinical claims.
        request["retry_reason"] = "identical_parallel_stem"
        request["task"] += (
            "前次乙卷題幹與甲卷相同，請重新產生完整 item。"
            "使用不同的臨床情境、行為表現與功能影響考查同一核心概念。"
            "不得沿用甲卷題幹或只更換姓名與數字。"
            "四選項、正解、逐項解析及來源仍須完整且一致。"
        )
    if repair_repeated_stem:
        # Regenerate the whole item once, never rewrite clinical content locally.
        request["retry_reason"] = "repeated_stem_across_pairs"
        request["task"] += (
            "前次題幹與其他已生成題目重複，請重新產生完整 item。"
            "使用來源摘錄直接支持的另一個臨床情境及決策角度；"
            "不得只更換姓名、年齡、數字或重複舊題。"
            "四選項、正解、逐項解析及來源仍須完整且一致；"
            "來源不足時必須回報 source_insufficient=true。"
        )
    if repair_duplicate_options:
        # A single bounded regeneration, never an automatic clinical edit.
        request["retry_reason"] = "duplicate_answer_options"
        request["task"] += (
            "前次輸出的四個選項出現重複，已被程式拒絕。請重新產生完整 item。"
            "A、B、C、D 必須是四個具體且不同的臨床判斷或處置，"
            "不得只更換標籤、空白或同義詞；各選項解析也須對應新選項。"
            "正解、題幹及解析仍須嚴格受到提供的來源支持。"
        )
    return request


def _with_planned_metadata(
    item: Any, spec: dict[str, Any], expected: dict[str, str],
) -> Any:
    """Fill only omitted deterministic fields; never overwrite a conflicting claim.

    The normal downstream validator still rejects mismatched metadata, unsafe
    approval claims, incomplete explanations and unsupported source IDs.
    """
    if not isinstance(item, dict):
        return item
    planned = {
        "item_id": expected["item_id"],
        "form": expected["form"],
        "pair_id": spec["pair_id"],
        "category": spec["category"],
        "subtopic": spec["core_topic"],
        "difficulty": spec["difficulty"],
        "cognitive_level": spec["cognitive_level"],
        "quality_status": "草稿",
    }
    return {**planned, **item}


def _check_item(
    item: Any,
    spec: dict[str, Any],
    expected: dict[str, str],
    allowed_sources: set[str],
) -> list[str]:
    if not isinstance(item, dict):
        return ["Model did not return a question object."]

    checks = {
        "item_id": expected["item_id"],
        "form": expected["form"],
        "pair_id": spec["pair_id"],
        "category": spec["category"],
        "subtopic": spec["core_topic"],
        "difficulty": spec["difficulty"],
        "cognitive_level": spec["cognitive_level"],
        "correct_answer": expected["target_answer_position"],
        "quality_status": "草稿",
    }
    errors = [
        f"{field}: expected {value!r}."
        for field, value in checks.items() if item.get(field) != value
    ]
    if item.get("approved_by_user") is True:
        errors.append("Model must not grant formal approval.")
    if not _substantive(item.get("stem")):
        errors.append("Missing/placeholder question stem.")

    options = item.get("options")
    if not isinstance(options, dict) or set(options) != set(LETTERS):
        errors.append("Options must contain exactly A-D.")
    else:
        invalid = [key for key in LETTERS if not _substantive(options[key])]
        normalized = [
            options[key].strip().casefold()
            for key in LETTERS if isinstance(options[key], str)
        ]
        distinct = len(set(normalized))
        if invalid or distinct != 4:
            # Diagnose structural failure without exposing clinical answer text.
            lengths = ",".join(
                f"{key}:{len(options[key]) if isinstance(options[key], str) else 'nonstring'}"
                for key in LETTERS
            )
            errors.append(
                "Options must be substantial and pairwise distinct "
                f"(invalid={','.join(invalid) or 'none'}; "
                f"distinct={distinct}/4; lengths={lengths})."
            )

    rationale = item.get("rationale")
    if not isinstance(rationale, dict) or any(
        not _substantive(rationale.get(k)) for k in ("correct", *LETTERS)
    ):
        errors.append("Rationale must contain substantive correct and A-D explanations.")

    sources = item.get("sources")
    if (not isinstance(sources, list) or not sources
            or any(not isinstance(source, str) or source not in allowed_sources
                   for source in sources)
            or len(sources) != len(set(str(source) for source in sources))):
        errors.append("Sources must cite unique IDs with supplied evidence for this pair.")
    return errors


def _export_verified_child_pair(
    form_a: dict[str, Any],
    form_b: dict[str, Any],
    out_dir: str | Path,
    *,
    items_per_form: int,
) -> dict[str, Path]:
    """Stage and check BOTH Word files before publishing either one.

    Structural G3 checking is deterministic; it does not prove any clinical
    claim or that an external chat host can offer working download links (G4).
    Existing files are not overwritten and a partial publication is rolled back.
    """
    target = Path(out_dir)
    target.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".child-docx-stage-", dir=target) as tmp:
        staged = export_parallel_docx(form_a, form_b, tmp)
        verification = verify_pair(
            staged["form_a"], staged["form_b"], items_per_form
        )
        forms = verification.get("files") or {}
        strict = verification.get("ok") is True and all(
            isinstance(forms.get(key), dict)
            and forms[key].get("ok") is True
            and forms[key].get("reader_layout") == "modern_strict"
            and forms[key].get("questions") == items_per_form
            and forms[key].get("answers") == items_per_form
            and forms[key].get("complete_option_rationales") == items_per_form
            for key in ("form_a", "form_b")
        )
        if not strict:
            failures = [
                str(error)
                for form in forms.values()
                if isinstance(form, dict)
                for error in form.get("errors", [])
            ]
            raise ValueError(
                "Generated DOCX failed strict structural verification: "
                + ("; ".join(failures) or "incomplete strict acceptance metrics")
            )

        destinations = {
            key: target / staged[key].name for key in ("form_a", "form_b")
        }
        for dest in destinations.values():
            if dest.exists():
                raise FileExistsError(
                    f"Refusing to overwrite an existing exam Word: {dest}"
                )

        committed: list[Path] = []
        try:
            for key in ("form_a", "form_b"):
                dest = destinations[key]
                # Exclusive hard-link creation prevents a race after exists().
                # Staging is inside target, so both paths share a filesystem.
                # Unsupported hard links fail closed; never silently overwrite.
                os.link(staged[key], dest)
                committed.append(dest)
        except Exception:
            # A one-sided output must not be presented as a completed pair.
            for dest in committed:
                dest.unlink(missing_ok=True)
            raise
        return destinations


def generate_child_parallel_docx(
    callback: Callable[[dict[str, Any]], dict[str, Any]],
    evidence: Mapping[str, Any],
    out_dir: str | Path,
    *,
    items_per_form: int = 20,
    version: str = DRAFT_VERSION,
    split_pair_inference: bool = False,
) -> dict[str, Path]:
    """One explicit generation pass; fail closed before writing either Word file.

    This checks schema, sources referenced, paired metadata and answer positions.
    It also stages and structurally verifies BOTH final Word files before publishing.
    It does NOT prove source-claim semantic support, host download access or
    psychometric equivalence, and never marks output as expert-validated
    or formally approved.
    """
    if not callable(callback):
        raise TypeError("An actual model callback is required; no Stub fallback.")
    if not _substantive(version):
        raise ValueError("Draft version must be non-empty.")
    if any(x in version.casefold() for x in ("formal", "approved", "核可")):
        raise ValueError("Drafts cannot be labelled as formal or approved.")

    # Fail before N expensive local model calls when this draft version
    # already has an output file. Match export_docx's filename slugging.
    # The final os.link publication still protects against a later race.
    output_root = Path(out_dir)
    if os.path.lexists(output_root) and not output_root.is_dir():
        raise NotADirectoryError(
            f"Exam Word output directory is not a directory: {output_root}"
        )
    slug = _safe_slug(version)
    for form in ("form_a", "form_b"):
        destination = output_root / f"{form}_{slug}.docx"
        if os.path.lexists(destination):
            raise FileExistsError(
                f"Refusing to overwrite an existing exam Word: {destination}"
            )

    blueprint = load_domain_blueprint()
    specs = build_child_pair_specs(items_per_form, blueprint=blueprint)
    contexts = _preflight_evidence(specs, blueprint["sources"], evidence)

    a_items: list[dict] = []
    b_items: list[dict] = []
    seen_stems: dict[str, tuple[str, str]] = {}
    for number, spec in enumerate(specs, start=1):
        request = _request(spec, contexts[spec["pair_id"]], number)
        if split_pair_inference:
            # Two smaller local inferences instead of one truncated two-item
            # response. Validate A before spending another inference on B.
            result = {}
            allowed = {source["source_id"] for source in request["source_context"]}
            for key, index in (("form_a", 0), ("form_b", 1)):
                previous = result["form_a"]["stem"] if key == "form_b" else None
                # Retry once ONLY for otherwise valid items whose substantive
                # A-D options duplicate each other. No fallback or repair is
                # allowed for missing evidence, sources, rationales or metadata.
                retry_reason = None
                for attempt in range(2):
                    single = callback(_single_form_request(
                        request, key, previous,
                        repair_duplicate_options=(attempt == 1 and retry_reason == "duplicate_answer_options"),
                        repair_identical_stem=(attempt == 1 and retry_reason == "identical_parallel_stem"),
                        repair_repeated_stem=(attempt == 1 and retry_reason == "repeated_stem_across_pairs"),
                    ))
                    if not isinstance(single, dict) or single.get("source_insufficient"):
                        raise ValueError(
                            f"{spec['pair_id']} {key}: model could not supply a valid item."
                        )
                    if single.get("pair_id", spec["pair_id"]) != spec["pair_id"]:
                        raise ValueError(f"{spec['pair_id']} {key}: model pair_id mismatch.")
                    item = _with_planned_metadata(
                        single.get("item"), spec, request["forms"][index]
                    )
                    failures = _check_item(
                        item, spec, request["forms"][index], allowed
                    )
                    if not failures:
                        if (key == "form_b" and normalize_question_stem(item["stem"])
                                == normalize_question_stem(result["form_a"]["stem"])):
                            if attempt == 0:
                                retry_reason = "identical_parallel_stem"
                                continue
                            raise ValueError(
                                f"{spec['pair_id']}: parallel question stems are identical."
                            )
                        normalized = normalize_question_stem(item["stem"])
                        if normalized in seen_stems:
                            if attempt == 0:
                                retry_reason = "repeated_stem_across_pairs"
                                continue
                            previous_form, previous_pair = seen_stems[normalized]
                            raise ValueError(
                                f"{spec['pair_id']}: duplicate question stem in "
                                f"{request['forms'][index]['form']}; "
                                f"already used by {previous_form} {previous_pair}."
                            )
                        break
                    retry_duplicate = (
                        attempt == 0 and len(failures) == 1
                        and failures[0].startswith(
                            "Options must be substantial and pairwise distinct "
                        )
                        and "invalid=none;" in failures[0]
                    )
                    if retry_duplicate:
                        retry_reason = "duplicate_answer_options"
                        continue
                    if not retry_duplicate:
                        raise ValueError(
                            f"{spec['pair_id']} {key}: " + "; ".join(failures)
                        )
                result[key] = item
        else:
            result = callback(request)
            if not isinstance(result, dict) or result.get("source_insufficient"):
                raise ValueError(f"{spec['pair_id']}: model could not supply a valid pair.")

            if result.get("pair_id", spec["pair_id"]) != spec["pair_id"]:
                raise ValueError(f"{spec['pair_id']}: model pair_id mismatch.")

        allowed = {source["source_id"] for source in request["source_context"]}
        first = _with_planned_metadata(result.get("form_a"), spec, request["forms"][0])
        second = _with_planned_metadata(result.get("form_b"), spec, request["forms"][1])
        errors = []
        for label, item, expected in (
            ("甲卷", first, request["forms"][0]),
            ("乙卷", second, request["forms"][1]),
        ):
            errors.extend(f"{label}: {message}" for message in _check_item(
                item, spec, expected, allowed
            ))
        if errors:
            raise ValueError(f"{spec['pair_id']}: " + "; ".join(errors))

        normalized_a = normalize_question_stem(first["stem"])
        normalized_b = normalize_question_stem(second["stem"])
        if normalized_a == normalized_b:
            raise ValueError(f"{spec['pair_id']}: parallel question stems are identical.")
        for label, item, normalized in (
            ("甲卷", first, normalized_a),
            ("乙卷", second, normalized_b),
        ):
            if normalized in seen_stems:
                previous_form, previous_pair = seen_stems[normalized]
                raise ValueError(
                    f"{spec['pair_id']}: duplicate question stem in {label}; "
                    f"already used by {previous_form} {previous_pair}."
                )
            seen_stems[normalized] = (label, spec["pair_id"])
        a_items.append(first)
        b_items.append(second)

    common = {
        "version": version,
        "quality_status": "未經獨立專家驗證之模擬草稿",
        "approved_by_user": False,
        "domain_id": "child_adolescent",
        "domain_name": blueprint["scope"]["content_domain"],
        "category_labels": {
            key: category["name"] for key, category in blueprint["categories"].items()
        },
        "source_catalog": {
            key: {"title": source["title"], "url": source["url"]}
            for key, source in blueprint["sources"].items()
        },
    }
    return _export_verified_child_pair(
        {"form": "甲卷", "items": a_items, **common},
        {"form": "乙卷", "items": b_items, **common},
        out_dir,
        items_per_form=items_per_form,
    )


def _probe_local_inference(model: OllamaLocalJsonCallback) -> None:
    """Exercise one real local JSON inference, without clinical text or sources.

    Passing this small transport probe does NOT demonstrate clinical accuracy,
    20-pair capacity, source grounding or Word delivery.
    """
    response = model({
        "system_instruction": (
            "This is a local-only JSON transport probe, not a clinical exam. "
            'Return only a JSON object with the exact field "probe": "ok".'
        ),
        "task": 'Return the JSON object {"probe": "ok"}.',
    })
    if not isinstance(response, dict) or response.get("probe") != "ok":
        raise RuntimeError(
            "Local Ollama responded but failed the minimal JSON inference probe. "
            "No clinical questions or Word files were generated."
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate candidate child/adolescent parallel exams from local Ollama."
    )
    evidence_group = parser.add_mutually_exclusive_group(required=False)
    evidence_group.add_argument(
        "--evidence", type=Path,
        help="Existing reviewed JSON: source_id -> {url, passage, retrieved_at}",
    )
    evidence_group.add_argument(
        "--auto-evidence", action="store_true",
        help="Fetch only the allowlisted official NICE guidance excerpts (internet required)",
    )
    parser.add_argument("--model", default=None, help="Already-installed local model (or OLLAMA_MODEL)")
    parser.add_argument(
        "--timeout-seconds", type=float, default=None,
        help="Local Ollama inference timeout in seconds (1-600); default 180",
    )
    parser.add_argument(
        "--max-output-tokens", type=int, default=None,
        help="Optional local model output limit (1-4096 tokens); truncated JSON fails closed",
    )
    parser.add_argument(
        "--check-local-model", action="store_true",
        help="Only check that local Ollama and the named model are ready; no generation or source fetch",
    )
    parser.add_argument(
        "--probe-local-inference", action="store_true",
        help="Run one minimal real local JSON inference; no clinical content or source fetch",
    )
    parser.add_argument(
        "--split-pair-inference", action="store_true",
        help="Use two bounded local inferences per A/B pair; no partial Word publication",
    )
    parser.add_argument("--items", type=int, default=20, help="Number of items in EACH form")
    parser.add_argument("--version", default=DRAFT_VERSION)
    parser.add_argument("--out", type=Path, default=Path("output/child-docx"))
    args = parser.parse_args()
    if args.check_local_model and args.probe_local_inference:
        parser.error("Choose only one local model diagnostic mode")
    if (args.check_local_model or args.probe_local_inference) and (
        args.auto_evidence or args.evidence is not None
    ):
        parser.error("Local model diagnostics cannot be combined with evidence arguments")
    if not (args.check_local_model or args.probe_local_inference) and (
        not args.auto_evidence and args.evidence is None
    ):
        parser.error("generation requires --evidence or --auto-evidence")
    # Fail before network source retrieval or 20 expensive local model calls.
    # Keep the existing constructor contract unchanged when no override is set.
    # Slow CPU-only local inference can exceed the default 180 seconds per pair.
    model_options = {"model": args.model}
    if args.timeout_seconds is not None:
        model_options["timeout_seconds"] = args.timeout_seconds
    if args.max_output_tokens is not None:
        model_options["max_output_tokens"] = args.max_output_tokens
    model = OllamaLocalJsonCallback(**model_options)
    model.check_ready()
    if args.check_local_model:
        print(f"Local Ollama model ready: {model.model} (no inference or download)")
        return
    if args.probe_local_inference:
        _probe_local_inference(model)
        print(
            f"Local Ollama JSON inference probe passed: {model.model} "
            "(one real local inference; no exam or Word generated)"
        )
        return
    if args.auto_evidence:
        blueprint = load_domain_blueprint()
        specs = build_child_pair_specs(args.items, blueprint=blueprint)
        required_ids = {source_id for spec in specs for source_id in spec["source_ids"]}
        evidence = fetch_official_guidance_evidence(blueprint["sources"], required_ids)
    else:
        evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
    generation_options = {"items_per_form": args.items, "version": args.version}
    # Preserve the existing CLI-to-generator call contract by default.
    if args.split_pair_inference:
        generation_options["split_pair_inference"] = True
    result = generate_child_parallel_docx(
        model, evidence, args.out, **generation_options
    )
    for form, path in result.items():
        print(f"{form}: {path}")


if __name__ == "__main__":
    main()
