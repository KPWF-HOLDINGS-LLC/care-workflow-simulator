"""Synthetic, in-memory care workflow rules. No patient data or messaging."""

from dataclasses import dataclass, asdict


SAMPLE_REPLIES = {
    "okay": "I am doing okay today.",
    "help": "I would like a follow-up call.",
    "urgent": "I need urgent assistance."
}


@dataclass
class Case:
    label: str
    status: str = "check_in_ready"
    last_reply: str | None = None
    alert: str | None = None


class Workflow:
    def __init__(self):
        self.reset()

    def reset(self):
        self.cases = {"case-a": Case("Case A"), "case-b": Case("Case B")}

    def state(self):
        return {key: asdict(value) for key, value in self.cases.items()}

    def send_mock_check_in(self, case_id):
        case = self._case(case_id)
        case.status = "awaiting_reply"
        case.last_reply = None
        case.alert = None
        return self.state()

    def submit_reply(self, case_id, reply_key):
        case = self._case(case_id)
        if case.status != "awaiting_reply":
            raise ValueError("A mock check-in must be sent first")
        if reply_key not in SAMPLE_REPLIES:
            raise ValueError("Choose a sample reply")
        case.last_reply = SAMPLE_REPLIES[reply_key]
        if reply_key == "urgent":
            case.status = "needs_review"
            case.alert = "open"
        elif reply_key == "help":
            case.status = "follow_up_requested"
        else:
            case.status = "completed"
        return self.state()

    def acknowledge(self, case_id):
        case = self._case(case_id)
        if case.alert != "open":
            raise ValueError("No open alert for this case")
        case.alert = "acknowledged"
        return self.state()

    def _case(self, case_id):
        try:
            return self.cases[case_id]
        except (KeyError, TypeError):
            raise ValueError("Unknown sample case") from None
