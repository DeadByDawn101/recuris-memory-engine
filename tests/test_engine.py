import unittest

from recuris_memory.engine import RecurisEngine
from recuris_memory.invocation import InvocationPolicy, InvocationRule
from recuris_memory.kernel import EvidenceKernel, receipt_checker
from recuris_memory.models import (
    Action, ExecutionEvent, GoalProposal, GoalState, GoalStatus, MemoryControl,
    Observation, Skill, WorkingState,
)


class EngineTests(unittest.TestCase):
    def test_trace_joins_state_invocation_action_observation_and_checker(self) -> None:
        skill = Skill("safe-write", "verify writes", tool="store")
        rule = InvocationRule("call", ExecutionEvent.STATE_CHANGING_DRAFT, True)
        memory = MemoryControl((skill,), ("status",), (rule,), ("g",))
        engine = RecurisEngine(memory, InvocationPolicy((rule,)), EvidenceKernel({"g": receipt_checker("id")}))
        state = WorkingState("t", (GoalState("g", "write"),))
        action = Action("store", state_changing=True, draft=True)
        result = engine.step(
            state,
            ExecutionEvent.STATE_CHANGING_DRAFT,
            action,
            Observation(False, {}, "not executed"),
            (GoalProposal("g", GoalStatus.DONE, ("claim",)),),
        )
        self.assertEqual(result.goal("g").status, GoalStatus.PENDING)
        self.assertEqual(len(engine.trace), 1)
        entry = engine.trace[0]
        self.assertEqual(entry.invocation.skill_ids, ("safe-write",))
        self.assertEqual(entry.action, action)
        self.assertFalse(entry.checker_decisions[0].accepted)


if __name__ == "__main__":
    unittest.main()

