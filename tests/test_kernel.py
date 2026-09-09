import unittest

from recuris_memory.kernel import EvidenceKernel, receipt_checker
from recuris_memory.models import Action, GoalProposal, GoalState, GoalStatus, Observation, WorkingState


class KernelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state = WorkingState("task", (GoalState("write", "Write record"),))
        self.kernel = EvidenceKernel({"write": receipt_checker("id")})
        self.proposal = (GoalProposal("write", GoalStatus.DONE, ("id=7",)),)

    def test_model_claim_without_receipt_does_not_complete_goal(self) -> None:
        state, decisions = self.kernel.commit(
            self.state, self.proposal, Action("store", state_changing=True), Observation(True, {})
        )
        self.assertEqual(state.goal("write").status, GoalStatus.PENDING)
        self.assertFalse(decisions[0].accepted)

    def test_draft_action_never_completes_goal(self) -> None:
        state, decisions = self.kernel.commit(
            self.state,
            self.proposal,
            Action("store", state_changing=True, draft=True),
            Observation(True, {"id": "7"}),
        )
        self.assertEqual(state.goal("write").status, GoalStatus.PENDING)
        self.assertEqual(decisions[0].reason, "draft action was not executed")

    def test_verified_receipt_completes_goal(self) -> None:
        state, decisions = self.kernel.commit(
            self.state,
            self.proposal,
            Action("store", state_changing=True),
            Observation(True, {"id": "7"}),
        )
        self.assertEqual(state.goal("write").status, GoalStatus.DONE)
        self.assertTrue(decisions[0].accepted)


if __name__ == "__main__":
    unittest.main()

