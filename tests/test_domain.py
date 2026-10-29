import unittest

from domain import Workflow


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.workflow = Workflow()

    def test_urgent_reply_opens_review_alert(self):
        self.workflow.send_mock_check_in("case-a")
        state = self.workflow.submit_reply("case-a", "urgent")
        self.assertEqual(state["case-a"]["alert"], "open")
        self.assertEqual(state["case-a"]["status"], "needs_review")
        self.assertEqual(self.workflow.acknowledge("case-a")["case-a"]["alert"], "acknowledged")

    def test_reply_requires_check_in_and_known_choice(self):
        with self.assertRaises(ValueError):
            self.workflow.submit_reply("case-a", "okay")
        self.workflow.send_mock_check_in("case-a")
        with self.assertRaises(ValueError):
            self.workflow.submit_reply("case-a", "free_text")

    def test_reset_discards_demo_state(self):
        self.workflow.send_mock_check_in("case-b")
        self.workflow.reset()
        self.assertEqual(self.workflow.state()["case-b"]["status"], "check_in_ready")


if __name__ == "__main__":
    unittest.main()
