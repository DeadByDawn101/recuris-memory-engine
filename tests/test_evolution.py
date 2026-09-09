import unittest

from recuris_memory.evolution import AdmissionGate, ComponentPatch, apply_scoped_patches
from recuris_memory.models import Component, MemoryControl, Skill


class EvolutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.baseline = MemoryControl(
            (Skill("base", "baseline"),),
            ("status", "evidence"),
            ("call-time",),
            ("goal-check",),
        )

    def test_patch_cannot_escape_diagnosed_components(self) -> None:
        with self.assertRaisesRegex(ValueError, "escapes diagnosis"):
            apply_scoped_patches(
                self.baseline,
                frozenset({Component.EXPERIENTIAL}),
                (ComponentPatch(Component.CHECKERS, ("changed",), "wrong target"),),
            )

    def test_unimplicated_components_remain_equal(self) -> None:
        candidate = apply_scoped_patches(
            self.baseline,
            frozenset({Component.EXPERIENTIAL}),
            (ComponentPatch(Component.EXPERIENTIAL, (Skill("fixed", "repair"),), "missing skill"),),
        )
        self.assertNotEqual(candidate.skills, self.baseline.skills)
        self.assertEqual(candidate.working_fields, self.baseline.working_fields)
        self.assertEqual(candidate.invocation_rules, self.baseline.invocation_rules)
        self.assertEqual(candidate.checker_ids, self.baseline.checker_ids)

    def test_gate_rejects_anchor_regression_and_preserves_baseline(self) -> None:
        candidate = apply_scoped_patches(
            self.baseline,
            frozenset({Component.EXPERIENTIAL}),
            (ComponentPatch(Component.EXPERIENTIAL, (Skill("fixed", "repair"),), "missing skill"),),
        )
        result = AdmissionGate().evaluate(
            self.baseline,
            candidate,
            source_evaluator=lambda memory: memory is candidate,
            held_out_anchor_evaluator=lambda memory: 1.0 if memory is self.baseline else 0.5,
        )
        self.assertFalse(result.admitted)
        self.assertIs(result.memory, self.baseline)

    def test_gate_admits_repair_without_regression(self) -> None:
        candidate = apply_scoped_patches(
            self.baseline,
            frozenset({Component.EXPERIENTIAL}),
            (ComponentPatch(Component.EXPERIENTIAL, (Skill("fixed", "repair"),), "missing skill"),),
        )
        result = AdmissionGate().evaluate(
            self.baseline,
            candidate,
            source_evaluator=lambda memory: memory is candidate,
            held_out_anchor_evaluator=lambda memory: 1.0,
        )
        self.assertTrue(result.admitted)
        self.assertIs(result.memory, candidate)


if __name__ == "__main__":
    unittest.main()

