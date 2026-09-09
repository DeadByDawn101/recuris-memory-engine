import unittest

from recuris_memory.invocation import InvocationPolicy, InvocationRule
from recuris_memory.models import Action, ExecutionEvent, GoalState, Skill, WorkingState


class InvocationTests(unittest.TestCase):
    def test_call_time_invocation_is_tool_keyed_and_requires_draft(self) -> None:
        policy = InvocationPolicy((InvocationRule("writes", ExecutionEvent.STATE_CHANGING_DRAFT, True),))
        skills = (
            Skill("store-safe", "Store safely", tool="store"),
            Skill("delete-safe", "Delete safely", tool="delete"),
        )
        state = WorkingState("t", (GoalState("g", "persist record"),))
        decision = policy.select(
            state,
            ExecutionEvent.STATE_CHANGING_DRAFT,
            Action("store", state_changing=True, draft=True),
            skills,
        )
        self.assertEqual(decision.skill_ids, ("store-safe",))
        self.assertEqual(decision.retrieval_key, "store")

    def test_completed_goal_does_not_match_unresolved_tag(self) -> None:
        from recuris_memory.models import GoalStatus

        policy = InvocationPolicy((InvocationRule("boundary", ExecutionEvent.TURN_BOUNDARY, False, "persist"),))
        state = WorkingState("t", (GoalState("g", "persist record", GoalStatus.DONE, ("receipt",)),))
        decision = policy.select(state, ExecutionEvent.TURN_BOUNDARY, Action("reply"), (Skill("s", "help"),))
        self.assertEqual(decision.skill_ids, ())


if __name__ == "__main__":
    unittest.main()

