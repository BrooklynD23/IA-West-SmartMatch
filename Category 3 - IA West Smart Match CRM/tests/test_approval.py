"""Tests for ActionProposal state machine (approval.py)."""

import pytest
from src.coordinator.approval import ActionProposal, ProposalStatus


class TestApprovalStateMachine:
    """State machine transition tests for ActionProposal."""

    def test_default_status_is_proposed(self) -> None:
        proposal = ActionProposal()
        assert proposal.status == "proposed"

    def test_default_has_valid_uuid_id(self) -> None:
        import uuid
        proposal = ActionProposal()
        # Should not raise
        parsed = uuid.UUID(proposal.id)
        assert str(parsed) == proposal.id

    def test_approve_transitions_to_approved(self) -> None:
        proposal = ActionProposal()
        proposal.approve()
        assert proposal.status == "approved"

    def test_reject_transitions_to_rejected(self) -> None:
        proposal = ActionProposal()
        proposal.reject()
        assert proposal.status == "rejected"

    def test_approve_raises_if_not_proposed(self) -> None:
        proposal = ActionProposal()
        proposal.approve()
        with pytest.raises(ValueError):
            proposal.approve()

    def test_reject_raises_if_not_proposed(self) -> None:
        proposal = ActionProposal()
        proposal.reject()
        with pytest.raises(ValueError):
            proposal.reject()

    def test_stub_execute_transitions_approved_to_completed(self) -> None:
        proposal = ActionProposal(agent="Discovery Agent")
        proposal.approve()
        proposal.stub_execute()
        assert proposal.status == "completed"

    def test_stub_execute_sets_result_string(self) -> None:
        proposal = ActionProposal(agent="Discovery Agent")
        proposal.approve()
        proposal.stub_execute()
        assert proposal.result == "[Stub] Discovery Agent completed successfully."

    def test_stub_execute_raises_if_not_approved(self) -> None:
        proposal = ActionProposal()
        with pytest.raises(ValueError):
            proposal.stub_execute()

    def test_stub_execute_raises_if_proposed(self) -> None:
        proposal = ActionProposal()
        with pytest.raises(ValueError):
            proposal.stub_execute()

    def test_edited_params_preserved_on_approve(self) -> None:
        proposal = ActionProposal(params={"university": "UCLA"})
        proposal.params["limit"] = 10
        proposal.approve()
        assert proposal.status == "approved"
        assert proposal.params["university"] == "UCLA"
        assert proposal.params["limit"] == 10

    def test_source_defaults_to_parsed(self) -> None:
        proposal = ActionProposal()
        assert proposal.source == "parsed"

    def test_source_can_be_set_to_proactive(self) -> None:
        proposal = ActionProposal(source="proactive")
        assert proposal.source == "proactive"
