"""
Unit tests for department_qa_flow router.
"""
import asyncio
from http import HTTPStatus
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException


class TestRequireDepartmentCreator:
    """Test suite for require_department_creator helper."""

    def test_success(self, mock_db, mock_current_user):
        """require_department_creator passes for department creator."""
        department_id = str(uuid4())
        department = MagicMock()
        department.id = department_id
        department.tenant_id = mock_current_user.tenant_id
        department.created_by = mock_current_user.id

        mock_db.query.return_value.filter.return_value.first.return_value = department

        from enterprise_chat_api.routers.department_qa_flow import require_department_creator

        result = require_department_creator(mock_db, department_id, mock_current_user)
        assert result == department

    def test_not_found(self, mock_db, mock_current_user):
        """require_department_creator raises 404 when department not found."""
        department_id = str(uuid4())
        mock_db.query.return_value.filter.return_value.first.return_value = None

        from enterprise_chat_api.routers.department_qa_flow import require_department_creator

        with pytest.raises(HTTPException) as exc_info:
            require_department_creator(mock_db, department_id, mock_current_user)
        assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
        assert "Department not found" in exc_info.value.detail

    def test_forbidden(self, mock_db, mock_current_user):
        """require_department_creator raises 403 for non-creator."""
        department_id = str(uuid4())
        department = MagicMock()
        department.id = department_id
        department.tenant_id = mock_current_user.tenant_id
        department.created_by = str(uuid4())  # Different user

        mock_db.query.return_value.filter.return_value.first.return_value = department

        from enterprise_chat_api.routers.department_qa_flow import require_department_creator

        with pytest.raises(HTTPException) as exc_info:
            require_department_creator(mock_db, department_id, mock_current_user)
        assert exc_info.value.status_code == HTTPStatus.FORBIDDEN
        assert "Only department creator" in exc_info.value.detail


class TestDepartmentQAFlowRouter:
    """Test suite for department QA flow async endpoint tests."""

    def test_list_department_datasets(self, mock_db, mock_current_user):
        """Test listing department datasets returns empty list."""
        department_id = str(uuid4())
        department = MagicMock()
        department.id = department_id
        department.tenant_id = mock_current_user.tenant_id
        department.created_by = mock_current_user.id

        mock_db.query.return_value.filter.return_value.first.side_effect = [department, None]

        with patch(
            "enterprise_chat_api.routers.department_qa_flow.KnowledgeBaseService"
        ) as MockKBService:
            mock_kb_instance = MagicMock()
            mock_kb_instance.get_department_datasets.return_value = []
            MockKBService.return_value = mock_kb_instance

            from enterprise_chat_api.routers.department_qa_flow import list_department_datasets

            result = asyncio.run(list_department_datasets(
                department_id=department_id,
                db=mock_db,
                current_user=mock_current_user,
            ))

            assert result.total == 0
            assert len(result.data) == 0
            mock_kb_instance.get_department_datasets.assert_called_once_with(
                department_id, mock_current_user.tenant_id
            )

    def test_create_department_qa_flow(self, mock_db, mock_current_user, mock_qa_flow_create):
        """Test creating a department QA flow via API."""
        department_id = str(uuid4())
        department = MagicMock()
        department.id = department_id
        department.tenant_id = mock_current_user.tenant_id
        department.created_by = mock_current_user.id

        mock_flow = MagicMock()
        mock_flow.id = str(uuid4())
        mock_flow.name = mock_qa_flow_create.name
        mock_flow.description = mock_qa_flow_create.description
        mock_flow.tenant_id = mock_current_user.tenant_id
        mock_flow.department_id = department_id
        mock_flow.created_by = mock_current_user.id
        mock_flow.dsl_file_path = "/path/to/dsl.yml"
        mock_flow.app_id = str(uuid4())
        mock_flow.workflow_id = None
        mock_flow.dataset_ids = mock_qa_flow_create.dataset_ids
        mock_flow.status = "active"

        with patch(
            "enterprise_chat_api.routers.department_qa_flow.require_department_creator",
            return_value=department,
        ):
            with patch(
                "enterprise_chat_api.routers.department_qa_flow.KnowledgeBaseService"
            ) as MockKBService:
                mock_kb_instance = MagicMock()
                mock_kb_instance.validate_dataset_ids.return_value = mock_qa_flow_create.dataset_ids
                MockKBService.return_value = mock_kb_instance

                with patch(
                    "enterprise_chat_api.routers.department_qa_flow.QAFlowService"
                ) as MockService:
                    mock_service_instance = MagicMock()
                    mock_service_instance.create_department_qa_flow.return_value = mock_flow
                    MockService.return_value = mock_service_instance

                    from enterprise_chat_api.routers.department_qa_flow import create_department_qa_flow

                    result = asyncio.run(create_department_qa_flow(
                        department_id=department_id,
                        flow_data=mock_qa_flow_create,
                        db=mock_db,
                        current_user=mock_current_user,
                    ))

                    assert result.name == mock_qa_flow_create.name
                    mock_service_instance.create_department_qa_flow.assert_called_once()
                    call_kwargs = mock_service_instance.create_department_qa_flow.call_args.kwargs
                    assert call_kwargs["department"] == department
                    assert call_kwargs["flow_data"] == mock_qa_flow_create

    def test_list_department_qa_flows(self, mock_db, mock_current_user):
        """Test listing department QA flows returns 3 flows."""
        department_id = str(uuid4())
        department = MagicMock()
        department.id = department_id
        department.tenant_id = mock_current_user.tenant_id
        department.created_by = mock_current_user.id

        mock_flows = []
        for i in range(3):
            flow = MagicMock()
            flow.id = str(uuid4())
            flow.name = f"测试问答流{i}"
            flow.description = f"描述{i}"
            flow.tenant_id = mock_current_user.tenant_id
            flow.department_id = department_id
            flow.dsl_file_path = "/path/to/dsl.yml"
            flow.app_id = str(uuid4())
            flow.workflow_id = None
            flow.dataset_ids = []
            flow.status = "active"
            flow.created_by = mock_current_user.id
            mock_flows.append(flow)

        mock_db.query.return_value.filter.return_value.all.return_value = mock_flows

        with patch(
            "enterprise_chat_api.routers.department_qa_flow.require_department_creator",
            return_value=department,
        ):
            from enterprise_chat_api.routers.department_qa_flow import list_department_qa_flows

            result = asyncio.run(list_department_qa_flows(
                department_id=department_id,
                db=mock_db,
                current_user=mock_current_user,
            ))

            assert result.total == 3
            assert len(result.data) == 3

    def test_get_department_qa_flow_not_found(self, mock_db, mock_current_user):
        """Test getting a non-existent department QA flow raises 404."""
        department_id = str(uuid4())
        flow_id = str(uuid4())

        department = MagicMock()
        department.id = department_id
        department.tenant_id = mock_current_user.tenant_id
        department.created_by = mock_current_user.id

        mock_db.query.return_value.filter.return_value.first.return_value = None

        with patch(
            "enterprise_chat_api.routers.department_qa_flow.require_department_creator",
            return_value=department,
        ):
            from enterprise_chat_api.routers.department_qa_flow import get_department_qa_flow

            with pytest.raises(HTTPException) as exc_info:
                asyncio.run(get_department_qa_flow(
                    department_id=department_id,
                    flow_id=flow_id,
                    db=mock_db,
                    current_user=mock_current_user,
                ))
            assert exc_info.value.status_code == HTTPStatus.NOT_FOUND

    def test_update_department_qa_flow_not_found(self, mock_db, mock_current_user):
        """Test updating a non-existent department QA flow raises 404."""
        department_id = str(uuid4())
        flow_id = str(uuid4())

        department = MagicMock()
        department.id = department_id
        department.tenant_id = mock_current_user.tenant_id
        department.created_by = mock_current_user.id

        # Query for flow returns None
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with patch(
            "enterprise_chat_api.routers.department_qa_flow.require_department_creator",
            return_value=department,
        ):
            from enterprise_chat_api.routers.department_qa_flow import update_department_qa_flow

            update_data = MagicMock()
            update_data.name = "新名称"
            update_data.description = "新描述"
            update_data.dataset_ids = None
            update_data.status = None

            with pytest.raises(HTTPException) as exc_info:
                asyncio.run(update_department_qa_flow(
                    department_id=department_id,
                    flow_id=flow_id,
                    flow_data=update_data,
                    db=mock_db,
                    current_user=mock_current_user,
                ))
            assert exc_info.value.status_code == HTTPStatus.NOT_FOUND

    def test_delete_department_qa_flow_not_found(self, mock_db, mock_current_user):
        """Test deleting a non-existent department QA flow raises 404."""
        department_id = str(uuid4())
        flow_id = str(uuid4())

        department = MagicMock()
        department.id = department_id
        department.tenant_id = mock_current_user.tenant_id
        department.created_by = mock_current_user.id

        mock_db.query.return_value.filter.return_value.first.return_value = None

        with patch(
            "enterprise_chat_api.routers.department_qa_flow.require_department_creator",
            return_value=department,
        ):
            from enterprise_chat_api.routers.department_qa_flow import delete_department_qa_flow

            with pytest.raises(HTTPException) as exc_info:
                asyncio.run(delete_department_qa_flow(
                    department_id=department_id,
                    flow_id=flow_id,
                    db=mock_db,
                    current_user=mock_current_user,
                ))
            assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
