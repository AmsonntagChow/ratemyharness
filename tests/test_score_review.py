import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "ratemyharness" / "scripts" / "score_review.py"
SPEC = importlib.util.spec_from_file_location("score_review", SCRIPT)
score_review = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(score_review)


def base_payload():
    identity = {
        "harness_build": "harness@sha256:test",
        "model": "model@test",
        "prompt": "prompt@sha256:test",
        "tool_schemas": "tools@sha256:test",
        "retrieval_data": "none",
        "dataset": "dataset@test",
        "rubric": "rubric@test",
    }
    judge = {
        "kind": "llm",
        "id": "quality-judge",
        "version": "1",
        "digest": "sha256:" + "c" * 64,
        "calibration_evidence_ids": ["e-judge"],
    }
    identity_sha256 = score_review.quality_identity_sha256(identity, judge)
    evidence = [
        {"id": "e-install", "kind": "install", "result": "pass", "reproducible": True, "fresh": True, "lane": "structural", "assertion_type": "deterministic"},
        {"id": "e-reference", "kind": "reference", "result": "pass", "reproducible": True, "fresh": True, "lane": "structural", "assertion_type": "deterministic"},
        {"id": "e-runtime", "kind": "runtime", "result": "pass", "reproducible": True, "fresh": True, "lane": "critical-journey-e2e", "assertion_type": "deterministic"},
        {"id": "e-failure_recovery", "kind": "test", "result": "pass", "reproducible": True, "fresh": True, "lane": "deterministic-checks", "assertion_type": "deterministic"},
        {"id": "e-deterministic", "kind": "test", "result": "pass", "reproducible": True, "fresh": True, "lane": "deterministic-checks", "assertion_type": "deterministic"},
        {"id": "e-journey", "kind": "runtime", "result": "pass", "reproducible": True, "fresh": True, "lane": "critical-journey-e2e", "assertion_type": "deterministic"},
        {"id": "e-quality", "kind": "eval", "result": "pass", "reproducible": True, "fresh": True, "lane": "probabilistic-eval", "assertion_type": "mixed", "identity_sha256": identity_sha256},
        {"id": "e-continuous", "kind": "metric", "result": "pass", "reproducible": True, "fresh": True, "lane": "continuous-evidence", "assertion_type": "deterministic", "identity_sha256": identity_sha256},
        {"id": "e-judge", "kind": "eval", "result": "pass", "reproducible": True, "fresh": True, "lane": "probabilistic-eval", "assertion_type": "mixed", "identity_sha256": identity_sha256},
    ]
    return {
        "schema_version": "2",
        "mode": "harness-owner",
        "rubric_id": "test/default-v1",
        "publish_target": "public-release",
        "dimensions": [
            {
                "id": "instructions",
                "weight": 25,
                "score": 90,
                "verification": "verified",
                "evidence_ids": ["e-reference"],
            },
            {
                "id": "failure_recovery",
                "weight": 25,
                "score": 90,
                "verification": "verified",
                "evidence_ids": ["e-failure_recovery"],
            },
            {
                "id": "execution",
                "weight": 25,
                "score": 90,
                "verification": "verified",
                "evidence_ids": ["e-runtime"],
            },
            {
                "id": "safety",
                "weight": 25,
                "score": 90,
                "verification": "verified",
                "evidence_ids": ["e-failure_recovery"],
            },
        ],
        "evidence": evidence,
        "evidence_lanes": {
            "deterministic-checks": {"status": "PASS", "evidence_ids": ["e-deterministic"]},
            "critical-journey-e2e": {"status": "PASS", "evidence_ids": ["e-journey"]},
            "probabilistic-eval": {"status": "PASS", "evidence_ids": ["e-quality", "e-judge"]},
            "continuous-evidence": {"status": "PASS", "evidence_ids": ["e-continuous"]},
        },
        "quality_evaluation": {
            "applicability": "required",
            "identity": identity,
            "identity_sha256": identity_sha256,
            "comparison": {
                "with_harness": {"runs": 10, "successes": 9},
                "baseline": {"runs": 10, "successes": 6},
                "uplift": {"observed": 0.3, "minimum": 0.1},
            },
            "task_success": {"observed": 0.9, "minimum": 0.8},
            "task_success_variance": {
                "observed_standard_deviation": 0.04,
                "maximum_standard_deviation": 0.1,
                "policy": "Repeat equal arms and withhold PASS above the declared maximum.",
            },
            "unsafe_effect_rate": {"observed": 0, "maximum": 0.01},
            "cost_per_success": {"observed": 0.2, "maximum": 0.3, "unit": "USD"},
            "latency_ms": {"observed_p95": 2000, "maximum_p95": 3000},
            "judge": judge,
            "evidence_ids": ["e-quality", "e-judge"],
        },
        "coverage": {
            "runtime": {"level": "full", "evidence_ids": ["e-runtime"]},
            "failure_recovery": {"level": "tested", "evidence_ids": ["e-failure_recovery"]},
            "clean_deploy": {"level": "tested", "evidence_ids": ["e-install"]},
            "required_artifacts": {
                "total": 2,
                "resolved": 2,
                "evidence_ids": ["e-reference"],
            },
        },
        "gates": [],
        "publish_checks": [
            {
                "id": "clean-install",
                "required": True,
                "status": "pass",
                "evidence_ids": ["e-runtime"],
            }
        ],
    }


TARGET_CHECK_FIXTURES = (
    ("sandboxed-authority-and-side-effects", "e-authority", "runtime"),
    ("retry-idempotency-and-recovery", "e-idempotency", "test"),
    ("independent-domain-review", "e-domain-review", "document"),
    ("human-control", "e-human-control", "test"),
    ("auditability", "e-auditability", "log"),
    ("incident-response", "e-incident-response", "test"),
)


def add_target_checks(payload, target):
    if target == "privileged-production":
        fixtures = TARGET_CHECK_FIXTURES[:2]
    elif target == "high-stakes":
        fixtures = TARGET_CHECK_FIXTURES
    else:
        fixtures = ()
    for check_id, evidence_id, kind in fixtures:
        lane = (
            "continuous-evidence"
            if kind == "log"
            else "deterministic-checks"
            if kind in {"runtime", "test", "trace"}
            else "structural"
        )
        payload["evidence"].append(
            {
                "id": evidence_id,
                "kind": kind,
                "result": "pass",
                "reproducible": True,
                "fresh": True,
                "lane": lane,
                "assertion_type": "deterministic",
            }
        )
        payload["publish_checks"].append(
            {
                "id": check_id,
                "required": True,
                "status": "pass",
                "evidence_ids": [evidence_id],
            }
        )


class ScoreReviewTests(unittest.TestCase):
    def compute(self, payload):
        return score_review.compute(score_review.validate(payload))

    def run_cli(self, payload_text=None, extra_args=None):
        extra_args = extra_args or []
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "scorecard.json"
            if payload_text is not None:
                path.write_text(payload_text, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(SCRIPT), *extra_args, str(path)],
                check=False,
                capture_output=True,
                text=True,
            )

    def add_active_gate(self, payload, gate_id, affected_targets=None):
        payload["evidence"].append(
            {"id": "e-veto", "kind": "static-analysis", "result": "fail", "reproducible": True, "fresh": True, "lane": "structural", "assertion_type": "deterministic"}
        )
        gate = {
            "id": gate_id,
            "state": "active",
            "evidence_ids": ["e-veto"],
            "retest_evidence_ids": [],
        }
        if affected_targets is not None:
            gate["affected_targets"] = affected_targets
        payload["gates"] = [gate]

    def rebind_quality_identity(self, payload):
        quality = payload["quality_evaluation"]
        digest = score_review.quality_identity_sha256(quality["identity"], quality["judge"])
        quality["identity_sha256"] = digest
        for evidence in payload["evidence"]:
            if evidence["id"] in {"e-quality", "e-judge", "e-continuous"}:
                evidence["identity_sha256"] = digest

    def test_fully_evidenced_harness_is_ready_for_release(self):
        result = self.compute(base_payload())
        self.assertEqual(result["decision"], "READY")
        self.assertEqual(result["scores"], {"raw_quality": 90, "publish_readiness": 90})
        self.assertEqual(result["coverage"]["confidence"], "A")
        self.assertEqual(result["distribution_evidence_gaps"], [])
        self.assertEqual(result["publish_checks"]["target_required"], [])
        self.assertEqual(
            {lane: value["status"] for lane, value in result["evidence_lanes"]["lanes"].items()},
            {
                "deterministic-checks": "PASS",
                "critical-journey-e2e": "PASS",
                "probabilistic-eval": "PASS",
                "continuous-evidence": "PASS",
            },
        )

    def test_deterministic_failure_cannot_be_hidden_by_quality_pass(self):
        payload = base_payload()
        next(item for item in payload["evidence"] if item["id"] == "e-deterministic")["result"] = "fail"
        payload["evidence_lanes"]["deterministic-checks"]["status"] = "FAIL"
        result = self.compute(payload)
        self.assertEqual(result["decision"], "NOT_READY")
        self.assertEqual(result["evidence_lanes"]["failed"], ["deterministic-checks"])
        self.assertEqual(result["evidence_lanes"]["lanes"]["probabilistic-eval"]["status"], "PASS")

    def test_quality_failure_cannot_be_hidden_by_stable_runtime(self):
        payload = base_payload()
        next(item for item in payload["evidence"] if item["id"] == "e-quality")["result"] = "fail"
        payload["evidence_lanes"]["probabilistic-eval"]["status"] = "FAIL"
        result = self.compute(payload)
        self.assertEqual(result["decision"], "NOT_READY")
        self.assertEqual(result["evidence_lanes"]["failed"], ["probabilistic-eval"])
        self.assertEqual(result["evidence_lanes"]["lanes"]["deterministic-checks"]["status"], "PASS")

    def test_lane_evidence_cannot_be_reused(self):
        payload = base_payload()
        payload["evidence_lanes"]["critical-journey-e2e"]["evidence_ids"] = ["e-deterministic"]
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertIn("classified as", caught.exception.message)

    def test_structural_test_cannot_satisfy_critical_journey(self):
        payload = base_payload()
        journey = next(item for item in payload["evidence"] if item["id"] == "e-journey")
        journey["kind"] = "test"
        journey["lane"] = "structural"
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertEqual(
            caught.exception.path,
            "$.evidence_lanes.critical-journey-e2e.evidence_ids",
        )
        self.assertIn("structural", caught.exception.message)

    def test_structural_test_cannot_satisfy_probabilistic_eval(self):
        payload = base_payload()
        next(item for item in payload["evidence"] if item["id"] == "e-quality")["kind"] = "test"
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertIn("allowed kinds", caught.exception.message)

    def test_public_release_requires_continuous_evidence(self):
        payload = base_payload()
        payload["evidence_lanes"]["continuous-evidence"] = {
            "status": "UNVERIFIED",
            "evidence_ids": [],
            "reason": "No deployed canary yet",
        }
        result = self.compute(payload)
        self.assertEqual(result["decision"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(result["evidence_lanes"]["unverified_required"], ["continuous-evidence"])

    def test_local_component_review_can_mark_online_and_quality_lanes_not_applicable(self):
        payload = base_payload()
        payload["publish_target"] = "local-prototype"
        payload["evidence_lanes"]["probabilistic-eval"] = {
            "status": "N/A",
            "evidence_ids": [],
            "reason": "Component-only loop review makes no task-quality claim",
        }
        payload["evidence_lanes"]["continuous-evidence"] = {
            "status": "N/A",
            "evidence_ids": [],
            "reason": "Local prototype has no deployment",
        }
        payload["quality_evaluation"] = {
            "applicability": "not-applicable",
            "reason": "Component-only loop review makes no task-quality claim",
        }
        self.assertEqual(self.compute(payload)["decision"], "READY")

    def test_uncalibrated_llm_judge_cannot_support_quality_pass(self):
        payload = base_payload()
        payload["quality_evaluation"]["judge"]["calibration_evidence_ids"] = []
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertIn("LLM judge requires", caught.exception.message)

    def test_deterministic_judge_needs_identity_but_not_llm_calibration(self):
        payload = base_payload()
        payload["quality_evaluation"]["judge"].update(
            {"kind": "deterministic", "calibration_evidence_ids": []}
        )
        self.rebind_quality_identity(payload)
        self.assertEqual(self.compute(payload)["decision"], "READY")

    def test_judge_digest_must_be_sha256(self):
        payload = base_payload()
        payload["quality_evaluation"]["judge"]["digest"] = "judge-v1"
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertEqual(caught.exception.path, "$.quality_evaluation.judge.digest")

    def test_quality_pass_must_meet_declared_thresholds(self):
        payload = base_payload()
        payload["quality_evaluation"]["comparison"]["with_harness"]["successes"] = 7
        payload["quality_evaluation"]["comparison"]["uplift"]["observed"] = 0.1
        payload["quality_evaluation"]["task_success"]["observed"] = 0.7
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertIn("task_success", caught.exception.message)

    def test_no_uplift_cannot_be_hidden_by_absolute_task_success(self):
        payload = base_payload()
        payload["quality_evaluation"]["comparison"]["baseline"]["successes"] = 9
        payload["quality_evaluation"]["comparison"]["uplift"]["observed"] = 0
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertIn("uplift", caught.exception.message)

    def test_quality_comparison_requires_equal_arm_counts(self):
        payload = base_payload()
        payload["quality_evaluation"]["comparison"]["baseline"]["runs"] = 9
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertIn("equal run counts", caught.exception.message)

    def test_excessive_variance_cannot_pass_on_a_high_mean(self):
        payload = base_payload()
        payload["quality_evaluation"]["task_success_variance"][
            "observed_standard_deviation"
        ] = 0.9
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertIn("task_success_variance", caught.exception.message)

    def test_continuous_evidence_must_match_evaluation_identity(self):
        payload = base_payload()
        next(item for item in payload["evidence"] if item["id"] == "e-continuous")[
            "identity_sha256"
        ] = "sha256:" + "d" * 64
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertEqual(
            caught.exception.path,
            "$.evidence_lanes.continuous-evidence.evidence_ids",
        )

    def test_identity_tuple_change_invalidates_recorded_digest(self):
        payload = base_payload()
        payload["quality_evaluation"]["identity"]["model"] = "different-model@2"
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertEqual(caught.exception.path, "$.quality_evaluation.identity_sha256")

    def test_all_requested_modes_are_supported(self):
        for mode in (
            "harness-owner",
            "staff-runtime-engineer",
            "runtime-engineer",
            "red-team",
            "adversarial",
            "sre-operator",
            "oral-defense",
        ):
            with self.subTest(mode=mode):
                payload = base_payload()
                payload["mode"] = mode
                self.assertEqual(self.compute(payload)["mode"], mode)

    def test_distribution_target_thresholds_match_the_published_ladder(self):
        expected = {
            "local-prototype": 50,
            "team-shared": 65,
            "public-release": 75,
            "privileged-production": 85,
            "high-stakes": 90,
        }
        for target, threshold in expected.items():
            with self.subTest(target=target):
                payload = base_payload()
                payload["publish_target"] = target
                add_target_checks(payload, target)
                result = self.compute(payload)
                self.assertEqual(result["publish_threshold"], threshold)
                self.assertEqual(result["decision"], "READY")

    def test_privileged_production_requires_sandboxed_authority_check(self):
        payload = base_payload()
        payload["publish_target"] = "privileged-production"
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertEqual(caught.exception.path, "$.publish_checks")
        self.assertIn("sandboxed-authority-and-side-effects", caught.exception.message)

    def test_privileged_production_requires_retry_idempotency_check(self):
        payload = base_payload()
        payload["publish_target"] = "privileged-production"
        add_target_checks(payload, "privileged-production")
        payload["publish_checks"] = [
            item
            for item in payload["publish_checks"]
            if item["id"] != "retry-idempotency-and-recovery"
        ]
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertIn("retry-idempotency-and-recovery", caught.exception.message)

    def test_privileged_authority_check_must_be_marked_required(self):
        payload = base_payload()
        payload["publish_target"] = "privileged-production"
        add_target_checks(payload, "privileged-production")
        next(
            item
            for item in payload["publish_checks"]
            if item["id"] == "sandboxed-authority-and-side-effects"
        )["required"] = False
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertIn("must set required to true", caught.exception.message)

    def test_unverified_privileged_authority_check_is_insufficient_evidence(self):
        payload = base_payload()
        payload["publish_target"] = "privileged-production"
        add_target_checks(payload, "privileged-production")
        check = next(
            item
            for item in payload["publish_checks"]
            if item["id"] == "sandboxed-authority-and-side-effects"
        )
        check["status"] = "unverified"
        check["evidence_ids"] = []
        result = self.compute(payload)
        self.assertEqual(result["decision"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(
            result["publish_checks"]["unverified_required"],
            ["sandboxed-authority-and-side-effects"],
        )

    def test_privileged_authority_check_rejects_stale_passing_evidence(self):
        payload = base_payload()
        payload["publish_target"] = "privileged-production"
        add_target_checks(payload, "privileged-production")
        next(item for item in payload["evidence"] if item["id"] == "e-authority")["fresh"] = False
        with self.assertRaises(score_review.ValidationError):
            score_review.validate(payload)

    def test_privileged_authority_check_rejects_document_only_evidence(self):
        payload = base_payload()
        payload["publish_target"] = "privileged-production"
        add_target_checks(payload, "privileged-production")
        next(item for item in payload["evidence"] if item["id"] == "e-authority")["kind"] = "document"
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertIn("allowed kind", caught.exception.message)

    def test_high_stakes_requires_every_target_specific_check(self):
        payload = base_payload()
        payload["publish_target"] = "high-stakes"
        add_target_checks(payload, "high-stakes")
        for check_id, _, _ in TARGET_CHECK_FIXTURES:
            with self.subTest(check_id=check_id):
                candidate = copy.deepcopy(payload)
                candidate["publish_checks"] = [
                    item for item in candidate["publish_checks"] if item["id"] != check_id
                ]
                with self.assertRaises(score_review.ValidationError) as caught:
                    score_review.validate(candidate)
                self.assertIn(check_id, caught.exception.message)

    def test_unverified_domain_review_blocks_high_stakes_approval(self):
        payload = base_payload()
        payload["publish_target"] = "high-stakes"
        add_target_checks(payload, "high-stakes")
        check = next(
            item
            for item in payload["publish_checks"]
            if item["id"] == "independent-domain-review"
        )
        check["status"] = "unverified"
        check["evidence_ids"] = []
        result = self.compute(payload)
        self.assertEqual(result["decision"], "INSUFFICIENT_EVIDENCE")
        self.assertIn("independent-domain-review", result["publish_checks"]["unverified_required"])

    def test_high_stakes_ready_reports_all_target_specific_checks(self):
        payload = base_payload()
        payload["publish_target"] = "high-stakes"
        add_target_checks(payload, "high-stakes")
        result = self.compute(payload)
        self.assertEqual(result["decision"], "READY")
        self.assertEqual(
            result["publish_checks"]["target_required"],
            sorted(item[0] for item in TARGET_CHECK_FIXTURES),
        )

    def test_raw_quality_is_separate_from_evidence_adjusted_readiness(self):
        payload = base_payload()
        for dimension in payload["dimensions"]:
            dimension["verification"] = "unverified"
            dimension["evidence_ids"] = []
        result = self.compute(payload)
        self.assertEqual(result["scores"]["raw_quality"], 90)
        self.assertEqual(result["scores"]["publish_readiness"], 49)
        self.assertEqual(result["coverage"]["confidence"], "D")
        self.assertEqual(result["decision"], "NOT_READY")

    def test_missing_runtime_evidence_caps_public_release_approval(self):
        payload = base_payload()
        payload["coverage"]["runtime"] = {"level": "static", "evidence_ids": []}
        result = self.compute(payload)
        self.assertEqual(result["scores"]["raw_quality"], 90)
        self.assertEqual(result["scores"]["publish_readiness"], 69)
        self.assertEqual(result["distribution_evidence_gaps"], ["runtime"])
        self.assertEqual(result["decision"], "INSUFFICIENT_EVIDENCE")

    def test_missing_failure_recovery_evidence_caps_public_release_approval(self):
        payload = base_payload()
        payload["coverage"]["failure_recovery"] = {"level": "claimed", "evidence_ids": []}
        result = self.compute(payload)
        self.assertEqual(result["scores"]["publish_readiness"], 69)
        self.assertEqual(result["distribution_evidence_gaps"], ["failure-recovery"])
        self.assertEqual(result["decision"], "INSUFFICIENT_EVIDENCE")

    def test_missing_clean_deploy_evidence_caps_public_release_approval(self):
        payload = base_payload()
        payload["coverage"]["clean_deploy"] = {"level": "claimed", "evidence_ids": []}
        result = self.compute(payload)
        self.assertEqual(result["scores"]["publish_readiness"], 69)
        self.assertEqual(result["distribution_evidence_gaps"], ["clean-deploy"])
        self.assertEqual(result["decision"], "INSUFFICIENT_EVIDENCE")

    def test_unresolved_required_artifact_caps_public_release_approval(self):
        payload = base_payload()
        payload["coverage"]["required_artifacts"]["resolved"] = 1
        result = self.compute(payload)
        self.assertEqual(result["scores"]["publish_readiness"], 69)
        self.assertEqual(result["distribution_evidence_gaps"], ["required-artifacts"])
        self.assertEqual(result["decision"], "INSUFFICIENT_EVIDENCE")

    def test_static_and_claimed_evidence_can_be_enough_for_local_prototype(self):
        payload = base_payload()
        payload["publish_target"] = "local-prototype"
        payload["coverage"]["runtime"] = {"level": "static", "evidence_ids": []}
        payload["coverage"]["failure_recovery"] = {"level": "claimed", "evidence_ids": []}
        result = self.compute(payload)
        self.assertEqual(result["scores"]["publish_readiness"], 69)
        self.assertEqual(result["distribution_evidence_gaps"], [])
        self.assertEqual(result["decision"], "READY")

    def test_team_shared_requires_fresh_execution_and_failure_recovery_evidence(self):
        payload = base_payload()
        payload["publish_target"] = "team-shared"
        payload["coverage"]["runtime"] = {"level": "static", "evidence_ids": []}
        payload["coverage"]["failure_recovery"] = {"level": "claimed", "evidence_ids": []}
        result = self.compute(payload)
        self.assertEqual(result["scores"]["publish_readiness"], 64)
        self.assertEqual(result["distribution_evidence_gaps"], ["runtime", "failure-recovery"])
        self.assertEqual(result["decision"], "INSUFFICIENT_EVIDENCE")

    def test_secret_or_cross_boundary_data_leak_is_a_veto(self):
        payload = base_payload()
        self.add_active_gate(payload, "secret-or-cross-boundary-data-leak")
        result = self.compute(payload)
        self.assertEqual(result["scores"], {"raw_quality": 90, "publish_readiness": 39})
        self.assertEqual(result["decision"], "BLOCKED")

    def test_unbounded_or_uncancellable_loop_is_a_veto(self):
        payload = base_payload()
        self.add_active_gate(payload, "unbounded-or-uncancellable-loop")
        self.assertEqual(self.compute(payload)["decision"], "BLOCKED")

    def test_untrusted_content_controls_runtime_is_a_veto(self):
        payload = base_payload()
        self.add_active_gate(payload, "untrusted-content-controls-runtime")
        self.assertEqual(self.compute(payload)["decision"], "BLOCKED")

    def test_unauthorized_tool_or_side_effect_is_a_veto(self):
        payload = base_payload()
        self.add_active_gate(payload, "unauthorized-tool-or-side-effect")
        self.assertEqual(self.compute(payload)["decision"], "BLOCKED")

    def test_unsafe_code_execution_is_a_veto(self):
        payload = base_payload()
        self.add_active_gate(payload, "unsafe-code-execution")
        self.assertEqual(self.compute(payload)["decision"], "BLOCKED")

    def test_sandbox_or_approval_bypass_is_a_veto(self):
        payload = base_payload()
        self.add_active_gate(payload, "sandbox-or-approval-bypass")
        self.assertEqual(self.compute(payload)["decision"], "BLOCKED")

    def test_duplicate_non_idempotent_effect_is_a_veto(self):
        payload = base_payload()
        self.add_active_gate(payload, "duplicate-non-idempotent-effect")
        self.assertEqual(self.compute(payload)["decision"], "BLOCKED")

    def test_hidden_network_or_telemetry_is_a_veto(self):
        payload = base_payload()
        self.add_active_gate(payload, "hidden-network-or-telemetry")
        self.assertEqual(self.compute(payload)["decision"], "BLOCKED")

    def test_fabricated_tool_or_completion_state_is_a_veto(self):
        payload = base_payload()
        self.add_active_gate(payload, "fabricated-tool-or-completion-state")
        self.assertEqual(self.compute(payload)["decision"], "BLOCKED")

    def test_broken_core_runtime_is_a_veto(self):
        payload = base_payload()
        self.add_active_gate(payload, "broken-core-runtime")
        self.assertEqual(self.compute(payload)["decision"], "BLOCKED")

    def test_license_or_provenance_breach_is_a_veto(self):
        payload = base_payload()
        self.add_active_gate(payload, "license-or-provenance-breach")
        self.assertEqual(self.compute(payload)["decision"], "BLOCKED")

    def test_legacy_gate_without_affected_targets_still_blocks_every_target(self):
        payload = base_payload()
        self.add_active_gate(payload, "broken-core-runtime")
        result = self.compute(payload)
        self.assertEqual(result["decision"], "BLOCKED")
        self.assertTrue(result["vetoed"])
        self.assertEqual(result["active_gates"], result["blocking_gates"])
        self.assertEqual(
            result["active_gates"][0]["affected_targets"],
            sorted(score_review.PUBLISH_THRESHOLDS),
        )

    def test_target_scoped_gate_blocks_a_matching_target(self):
        payload = base_payload()
        self.add_active_gate(
            payload,
            "hidden-network-or-telemetry",
            ["public-release", "privileged-production"],
        )
        result = self.compute(payload)
        self.assertEqual(result["decision"], "BLOCKED")
        self.assertEqual(result["scores"]["publish_readiness"], 39)
        self.assertEqual(result["blocking_gates"], result["active_gates"])
        self.assertEqual(
            result["blocking_gates"][0]["affected_targets"],
            ["privileged-production", "public-release"],
        )

    def test_target_scoped_gate_does_not_block_an_unaffected_target(self):
        payload = base_payload()
        self.add_active_gate(
            payload,
            "hidden-network-or-telemetry",
            ["privileged-production", "high-stakes"],
        )
        result = self.compute(payload)
        self.assertEqual(result["decision"], "READY")
        self.assertEqual(result["scores"]["publish_readiness"], 90)
        self.assertEqual(len(result["active_gates"]), 1)
        self.assertEqual(result["blocking_gates"], [])
        self.assertFalse(result["vetoed"])
        self.assertFalse(
            any(item["source"] == "safety-gate" for item in result["applied_caps"])
        )

    def test_affected_targets_reject_empty_duplicate_and_unknown_values(self):
        invalid_values = (
            ([], "at least one target"),
            (["public-release", "public-release"], "duplicate targets"),
            (["future-target"], "must be one of"),
        )
        for affected_targets, expected_message in invalid_values:
            with self.subTest(affected_targets=affected_targets):
                payload = base_payload()
                self.add_active_gate(
                    payload,
                    "hidden-network-or-telemetry",
                    affected_targets,
                )
                with self.assertRaises(score_review.ValidationError) as caught:
                    score_review.validate(payload)
                self.assertTrue(
                    caught.exception.path.startswith("$.gates[0].affected_targets")
                )
                self.assertIn(expected_message, caught.exception.message)

    def test_fixed_veto_requires_reproducible_passing_retest(self):
        payload = base_payload()
        payload["gates"] = [
            {
                "id": "untrusted-content-controls-runtime",
                "state": "fixed",
                "evidence_ids": [],
                "retest_evidence_ids": [],
            }
        ]
        with self.assertRaises(score_review.ValidationError):
            score_review.validate(payload)

    def test_fixed_veto_accepts_reproducible_passing_retest(self):
        payload = base_payload()
        payload["gates"] = [
            {
                "id": "untrusted-content-controls-runtime",
                "state": "fixed",
                "evidence_ids": [],
                "retest_evidence_ids": ["e-failure_recovery"],
            }
        ]
        result = self.compute(payload)
        self.assertEqual(result["decision"], "READY")
        self.assertFalse(result["vetoed"])

    def test_unknown_veto_is_rejected(self):
        payload = base_payload()
        payload["gates"] = [
            {
                "id": "caller-invented-veto",
                "state": "active",
                "evidence_ids": ["e-runtime"],
                "retest_evidence_ids": [],
            }
        ]
        with self.assertRaises(score_review.ValidationError):
            score_review.validate(payload)

    def test_required_failed_publish_check_is_not_ready(self):
        payload = base_payload()
        payload["evidence"].append(
            {"id": "e-failure", "kind": "runtime", "result": "fail", "reproducible": True, "fresh": True, "lane": "critical-journey-e2e", "assertion_type": "deterministic"}
        )
        payload["publish_checks"] = [
            {
                "id": "clean-install",
                "required": True,
                "status": "fail",
                "evidence_ids": ["e-failure"],
            }
        ]
        self.assertEqual(self.compute(payload)["decision"], "NOT_READY")

    def test_required_unverified_publish_check_is_insufficient_evidence(self):
        payload = base_payload()
        payload["publish_checks"] = [
            {
                "id": "failure_recovery-regression",
                "required": True,
                "status": "unverified",
                "evidence_ids": [],
            }
        ]
        self.assertEqual(self.compute(payload)["decision"], "INSUFFICIENT_EVIDENCE")

    def test_optional_publish_gap_yields_ready_with_conditions(self):
        payload = base_payload()
        payload["publish_checks"].append(
            {
                "id": "extra-platform",
                "required": False,
                "status": "unverified",
                "evidence_ids": [],
            }
        )
        self.assertEqual(self.compute(payload)["decision"], "READY_WITH_CONDITIONS")

    def test_weights_must_total_100(self):
        payload = base_payload()
        payload["dimensions"][0]["weight"] = 24
        with self.assertRaises(score_review.ValidationError):
            score_review.validate(payload)

    def test_boolean_is_not_an_integer_score(self):
        payload = base_payload()
        payload["dimensions"][0]["score"] = True
        with self.assertRaises(score_review.ValidationError):
            score_review.validate(payload)

    def test_verified_dimension_rejects_claim_only_evidence(self):
        payload = base_payload()
        payload["evidence"].append(
            {"id": "e-claim", "kind": "claim", "result": "pass", "reproducible": True, "fresh": True, "lane": "structural", "assertion_type": "not-applicable"}
        )
        payload["dimensions"][0]["evidence_ids"] = ["e-claim"]
        with self.assertRaises(score_review.ValidationError):
            score_review.validate(payload)

    def test_full_runtime_coverage_requires_runtime_evidence(self):
        payload = base_payload()
        payload["coverage"]["runtime"]["evidence_ids"] = []
        with self.assertRaises(score_review.ValidationError):
            score_review.validate(payload)

    def test_runtime_coverage_rejects_stale_execution_evidence(self):
        payload = base_payload()
        next(item for item in payload["evidence"] if item["id"] == "e-runtime")["fresh"] = False
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertEqual(caught.exception.path, "$.coverage.runtime.evidence_ids")

    def test_tested_failure_recovery_coverage_requires_failure_recovery_evidence(self):
        payload = base_payload()
        payload["coverage"]["failure_recovery"]["evidence_ids"] = []
        with self.assertRaises(score_review.ValidationError):
            score_review.validate(payload)

    def test_failure_recovery_coverage_rejects_stale_discovery_evidence(self):
        payload = base_payload()
        next(item for item in payload["evidence"] if item["id"] == "e-failure_recovery")["fresh"] = False
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertEqual(caught.exception.path, "$.coverage.failure_recovery.evidence_ids")

    def test_tested_clean_deploy_coverage_requires_install_evidence(self):
        payload = base_payload()
        payload["coverage"]["clean_deploy"]["evidence_ids"] = []
        with self.assertRaises(score_review.ValidationError):
            score_review.validate(payload)

    def test_clean_deploy_coverage_rejects_stale_install_evidence(self):
        payload = base_payload()
        next(item for item in payload["evidence"] if item["id"] == "e-install")["fresh"] = False
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertEqual(caught.exception.path, "$.coverage.clean_deploy.evidence_ids")

    def test_resolved_artifacts_require_reference_evidence(self):
        payload = base_payload()
        payload["coverage"]["required_artifacts"]["evidence_ids"] = []
        with self.assertRaises(score_review.ValidationError):
            score_review.validate(payload)

    def test_unknown_root_field_is_rejected(self):
        payload = base_payload()
        payload["surprise"] = True
        with self.assertRaises(score_review.ValidationError):
            score_review.validate(payload)

    def test_duplicate_evidence_id_is_rejected(self):
        payload = base_payload()
        payload["evidence"].append(copy.deepcopy(payload["evidence"][0]))
        with self.assertRaises(score_review.ValidationError):
            score_review.validate(payload)

    def test_input_order_does_not_change_output(self):
        payload = base_payload()
        first = score_review.render(self.compute(payload), pretty=False)
        reordered = copy.deepcopy(payload)
        reordered["dimensions"].reverse()
        reordered["evidence"].reverse()
        reordered["coverage"]["required_artifacts"]["evidence_ids"].reverse()
        second = score_review.render(self.compute(reordered), pretty=False)
        self.assertEqual(first, second)

    def test_cli_success_uses_stdout_only(self):
        result = self.run_cli(json.dumps(base_payload()))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertTrue(json.loads(result.stdout)["ok"])

    def test_cli_invalid_json_exits_one_and_uses_stderr(self):
        result = self.run_cli("{not-json")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertEqual(json.loads(result.stderr)["error"]["code"], "validation_error")

    def test_cli_argument_error_exits_two(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--unknown"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertEqual(json.loads(result.stderr)["error"]["code"], "argument_error")


if __name__ == "__main__":
    unittest.main()
