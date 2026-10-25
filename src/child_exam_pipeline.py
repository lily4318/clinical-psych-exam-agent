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
from .export_docx import export_parallel_docx
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
            "原始摘錄存在不代表臨床主張已通過專家驗證。",
            "所有新題均為草稿，絕不可標成正式核可。",
        ],
        "output_contract": {
            "type": "object",
            "required": ["pair_id", "form_a", "form_b"],
            "item_fields": [
                "item_id", "form", "pair_id", "stem", "options", "correct_answer",
                "category", "subtopic", "difficulty", "cognitive_level",
                "rationale", "sources", "quality_status",
            ],
        },
    }


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
    elif (not all(_substantive(options[k]) for k in LETTERS)
          or len({options[k].strip().casefold() for k in LETTERS}) != 4):
        errors.append("Options must be substantial and pairwise distinct.")

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

    blueprint = load_domain_blueprint()
    specs = build_child_pair_specs(items_per_form, blueprint=blueprint)
    contexts = _preflight_evidence(specs, blueprint["sources"], evidence)

    a_items: list[dict] = []
    b_items: list[dict] = []
    seen_stems: dict[str, tuple[str, str]] = {}
    for number, spec in enumerate(specs, start=1):
        request = _request(spec, contexts[spec["pair_id"]], number)
        result = callback(request)
        if not isinstance(result, dict) or result.get("source_insufficient"):
            raise ValueError(f"{spec['pair_id']}: model could not supply a valid pair.")

        if result.get("pair_id") != spec["pair_id"]:
            raise ValueError(f"{spec['pair_id']}: model pair_id mismatch.")

        allowed = {source["source_id"] for source in request["source_context"]}
        first, second = result.get("form_a"), result.get("form_b")
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
        "--check-local-model", action="store_true",
        help="Only check that local Ollama and the named model are ready; no generation or source fetch",
    )
    parser.add_argument(
        "--probe-local-inference", action="store_true",
        help="Run one minimal real local JSON inference; no clinical content or source fetch",
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
    result = generate_child_parallel_docx(
        model, evidence, args.out, items_per_form=args.items, version=args.version
    )
    for form, path in result.items():
        print(f"{form}: {path}")


if __name__ == "__main__":
    main()
