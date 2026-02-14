import pytest
from unittest.mock import AsyncMock
from workflows.loyalfans_controller import LoyalFansController

@pytest.fixture
def controller():
    return LoyalFansController(AsyncMock(), AsyncMock(), AsyncMock(), AsyncMock())

@pytest.mark.asyncio
async def test_workflow_success(controller):
    # Теперь проверяем с учетом аргумента status
    result = await controller.execute_workflow("user_1", "sync_messages", {"messages": [1]})
    assert result["status"] == "synced"
    controller.notifier.send_alert.assert_called_with("Task sync_messages finished!", status="SUCCESS")

@pytest.mark.asyncio
async def test_workflow_failure(controller):
    controller.auth.get_credentials.side_effect = Exception("Auth Fail")
    result = await controller.execute_workflow("user_1", "sync_messages", {})
    assert result["status"] == "error"
    controller.notifier.send_alert.assert_called_with("Workflow sync_messages failed: Auth Fail", status="ERROR")