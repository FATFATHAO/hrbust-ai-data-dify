"""
Unit tests for personal_qa_flow router.
"""
import asyncio
from http import HTTPStatus
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from enterprise_chat_api.schemas.department_qa_flow import QAFlowUpdate


class TestRequireFlowOwner:
    """Test suite for require_flow_owner helper."""

    def test_success(self, mock_db, mock_current_user):
        """require_flow_owner passes for flow owner."""
        flow = MagicMock()
        flow.id = str(uuid4())
        flow.account_id = mock_current_user.id
        flow.tenant_id = mock_current_user.tenant_id

        from enterprise_chat_api.routers.personal_qa_flow import require_flow_owner

        result = require_flow_owner(mock_db, flow, mock_current_user)
        assert result == flow

    def test_forbidden(self, mock_db, mock_current_user):
        """require_flow_owner raises 403 for non-owner."""
        flow = MagicMock()
        flow.id = str(uuid4())
        flow.account_id = str(uuid4())  # Different user
        flow.tenant_id = mock_current_user.tenant_id

        from enterprise_chat_api.routers.personal_qa_flow import require_flow_owner

        with pytest.raises(HTTPException) as exc_info:
            require_flow_owner(mock_db, flow, mock_current_user)
        assert exc_info.value.status_code == HTTPStatus.FORBIDDEN
        assert "Only flow owner" in exc_info.value.detail


class TestPersonalQAFlowRouter:
    """Test suite for personal QA flow async endpoint tests."""

    def test_list_user_datasets(self, mock_db, mock_current_user):
        """Test listing user datasets returns empty list."""
        with patch(
            "enterprise_chat_api.routers.personal_qa_flow.KnowledgeBaseService"
        ) as MockKBService:
            mock_kb_instance = MagicMock()
            mock_kb_instance.get_accessible_datasets_for_user.return_value = []
            MockKBService.return_value = mock_kb_instance

            from enterprise_chat_api.routers.personal_qa_flow import list_user_datasets

            result = asyncio.run(list_user_datasets(
                db=mock_db,
                current_user=mock_current_user,
            ))

            assert result.total == 0
            mock_kb_instance.get_accessible_datasets_for_user.assert_called_once_with(
                mock_current_user.id, mock_current_user.tenant_id
            )

    def test_create_personal_qa_flow(self, mock_db, mock_current_user, mock_qa_flow_create):
        """Test creating a personal QA flow via API."""
        mock_flow = MagicMock()
        mock_flow.id = str(uuid4())
        mock_flow.name = mock_qa_flow_create.name
        mock_flow.description = mock_qa_flow_create.description
        mock_flow.tenant_id = mock_current_user.tenant_id
        mock_flow.account_id = mock_current_user.id
        mock_flow.dsl_file_path = "/path/to/dsl.yml"
        mock_flow.app_id = str(uuid4())
        mock_flow.workflow_id = None
        mock_flow.dataset_ids = mock_qa_flow_create.dataset_ids
        mock_flow.status = "active"

        with patch(
            "enterprise_chat_api.routers.personal_qa_flow.KnowledgeBaseService"
        ) as MockKBService:
            mock_kb_instance = MagicMock()
            mock_kb_instance.validate_dataset_ids.return_value = mock_qa_flow_create.dataset_ids
            MockKBService.return_value = mock_kb_instance

            with patch(
                "enterprise_chat_api.routers.personal_qa_flow.QAFlowService"
            ) as MockService:
                mock_service_instance = MagicMock()
                mock_service_instance.create_personal_qa_flow.return_value = mock_flow
                MockService.return_value = mock_service_instance

                from enterprise_chat_api.routers.personal_qa_flow import create_personal_qa_flow

                result = asyncio.run(create_personal_qa_flow(
                    flow_data=mock_qa_flow_create,
                    db=mock_db,
                    current_user=mock_current_user,
                ))

                assert result.name == mock_qa_flow_create.name
                mock_service_instance.create_personal_qa_flow.assert_called_once()
                call_kwargs = mock_service_instance.create_personal_qa_flow.call_args.kwargs
                assert call_kwargs["flow_data"] == mock_qa_flow_create

    def test_list_personal_qa_flows(self, mock_db, mock_current_user):
        """Test listing personal QA flows returns 2 flows."""
        mock_flows = []
        for i in range(2):
            flow = MagicMock()
            flow.id = str(uuid4())
            flow.name = f"我的问答流{i}"
            flow.description = f"描述{i}"
            flow.tenant_id = mock_current_user.tenant_id
            flow.account_id = mock_current_user.id
            flow.dsl_file_path = "/path/to/dsl.yml"
            flow.app_id = str(uuid4())
            flow.workflow_id = None
            flow.dataset_ids = []
            flow.status = "active"
            mock_flows.append(flow)

        mock_db.query.return_value.filter.return_value.all.return_value = mock_flows

        from enterprise_chat_api.routers.personal_qa_flow import list_personal_qa_flows

        result = asyncio.run(list_personal_qa_flows(
            db=mock_db,
            current_user=mock_current_user,
        ))

        assert result.total == 2
        assert len(result.data) == 2

    def test_get_personal_qa_flow_not_found(self, mock_db, mock_current_user):
        """Test getting a non-existent personal QA flow raises 404."""
        flow_id = str(uuid4())
        mock_db.query.return_value.filter.return_value.first.return_value = None

        from enterprise_chat_api.routers.personal_qa_flow import get_personal_qa_flow

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(get_personal_qa_flow(
                flow_id=flow_id,
                db=mock_db,
                current_user=mock_current_user,
            ))
        assert exc_info.value.status_code == HTTPStatus.NOT_FOUND

    def test_update_personal_qa_flow_not_found(self, mock_db, mock_current_user):
        """Test updating a non-existent personal QA flow raises 404."""
        flow_id = str(uuid4())
        mock_db.query.return_value.filter.return_value.first.return_value = None

        update_data = MagicMock()
        update_data.name = "新名称"
        update_data.description = "新描述"
        update_data.dataset_ids = None
        update_data.status = None

        from enterprise_chat_api.routers.personal_qa_flow import update_personal_qa_flow

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(update_personal_qa_flow(
                flow_id=flow_id,
                flow_data=update_data,
                db=mock_db,
                current_user=mock_current_user,
            ))
        assert exc_info.value.status_code == HTTPStatus.NOT_FOUND

    def test_delete_personal_qa_flow_not_found(self, mock_db, mock_current_user):
        """Test deleting a non-existent personal QA flow raises 404."""
        flow_id = str(uuid4())
        mock_db.query.return_value.filter.return_value.first.return_value = None

        from enterprise_chat_api.routers.personal_qa_flow import delete_personal_qa_flow

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(delete_personal_qa_flow(
                flow_id=flow_id,
                db=mock_db,
                current_user=mock_current_user,
            ))
        assert exc_info.value.status_code == HTTPStatus.NOT_FOUND

    def test_update_personal_qa_flow_success(self, mock_db, mock_current_user):
        """Test successfully updating a personal QA flow."""
        flow_id = str(uuid4())
        flow = MagicMock()
        flow.id = flow_id
        flow.name = "旧名称"
        flow.description = "旧描述"
        flow.tenant_id = mock_current_user.tenant_id
        flow.account_id = mock_current_user.id
        flow.dsl_file_path = "/path/to/dsl.yml"
        flow.app_id = str(uuid4())
        flow.workflow_id = None
        flow.dataset_ids = []
        flow.status = "active"

        update_data = QAFlowUpdate(
            name="新名称",
            description="新描述",
        )

        mock_db.query.return_value.filter.return_value.first.return_value = flow

        with patch(
            "enterprise_chat_api.routers.personal_qa_flow.require_flow_owner",
            return_value=flow,
        ):
            with patch(
                "enterprise_chat_api.routers.personal_qa_flow.KnowledgeBaseService"
            ) as MockKBService:
                mock_kb_instance = MagicMock()
                MockKBService.return_value = mock_kb_instance

                with patch(
                    "enterprise_chat_api.routers.personal_qa_flow.QAFlowService"
                ) as MockService:
                    mock_service_instance = MagicMock()
                    # The service updates flow in-place and returns it
                    mock_service_instance.update_personal_qa_flow.return_value = flow
                    MockService.return_value = mock_service_instance

                    from enterprise_chat_api.routers.personal_qa_flow import update_personal_qa_flow

                    result = asyncio.run(update_personal_qa_flow(
                        flow_id=flow_id,
                        flow_data=update_data,
                        db=mock_db,
                        current_user=mock_current_user,
                    ))

                    # Verify flow object was passed to service for update
                    mock_service_instance.update_personal_qa_flow.assert_called_once()
                    call_args = mock_service_instance.update_personal_qa_flow.call_args
                    # Args are passed positionally: (flow, flow_data)
                    assert call_args[0][0] == flow
                    assert call_args[0][1] == update_data

    def test_delete_personal_qa_flow_success(self, mock_db, mock_current_user):
        """Test successfully deleting a personal QA flow."""
        flow_id = str(uuid4())
        flow = MagicMock()
        flow.id = flow_id
        flow.tenant_id = mock_current_user.tenant_id
        flow.account_id = mock_current_user.id

        mock_db.query.return_value.filter.return_value.first.return_value = flow

        with patch(
            "enterprise_chat_api.routers.personal_qa_flow.require_flow_owner",
            return_value=flow,
        ):
            with patch(
                "enterprise_chat_api.routers.personal_qa_flow.QAFlowService"
            ) as MockService:
                mock_service_instance = MagicMock()
                MockService.return_value = mock_service_instance

                from enterprise_chat_api.routers.personal_qa_flow import delete_personal_qa_flow

                asyncio.run(delete_personal_qa_flow(
                    flow_id=flow_id,
                    db=mock_db,
                    current_user=mock_current_user,
                ))

                mock_service_instance.delete_personal_qa_flow.assert_called_once_with(flow)
