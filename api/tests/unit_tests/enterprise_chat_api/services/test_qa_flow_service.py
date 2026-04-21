"""
Unit tests for QAFlowService.
"""
import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from enterprise_chat_api.services.qa_flow_service import QAFlowService
from enterprise_chat_api.schemas.department_qa_flow import QAFlowCreate, QAFlowUpdate
from enterprise_chat_api.models.department_qa_flow import DepartmentQAFlow
from enterprise_chat_api.models.personal_qa_flow import PersonalQAFlow
from services.app_dsl_service import ImportStatus


class TestQAFlowService:
    """Test suite for QAFlowService."""

    def test_create_department_qa_flow_success(
        self, mock_db, mock_department, mock_account, mock_qa_flow_create
    ):
        """Test successful creation of a department QA flow."""
        app_id = str(uuid4())

        # Mock AppDslService result
        mock_import_result = MagicMock()
        mock_import_result.status = ImportStatus.COMPLETED
        mock_import_result.app_id = app_id
        mock_import_result.error = None

        with patch(
            "enterprise_chat_api.services.qa_flow_service.AppDslService"
        ) as MockAppDslService:
            MockAppDslService.return_value.import_app.return_value = mock_import_result

            service = QAFlowService(mock_db)
            flow = service.create_department_qa_flow(
                department=mock_department,
                flow_data=mock_qa_flow_create,
                created_by=mock_account.id,
            )

            # Verify AppDslService was called
            MockAppDslService.return_value.import_app.assert_called_once()
            call_kwargs = MockAppDslService.return_value.import_app.call_args.kwargs
            assert call_kwargs["name"] == mock_qa_flow_create.name
            assert call_kwargs["description"] == mock_qa_flow_create.description
            assert call_kwargs["import_mode"] == "yaml-content"

            # Verify flow was added to session
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()

            # Verify the added object has correct properties
            added_obj = mock_db.add.call_args[0][0]
            assert isinstance(added_obj, DepartmentQAFlow)
            assert added_obj.tenant_id == mock_department.tenant_id
            assert added_obj.department_id == mock_department.id
            assert added_obj.created_by == mock_account.id
            assert added_obj.name == mock_qa_flow_create.name
            assert added_obj.workflow_id is None  # chat mode has no workflow
            assert added_obj.status == "active"

    def test_create_department_qa_flow_import_failed(self, mock_db, mock_department, mock_account, mock_qa_flow_create):
        """Test department QA flow creation when import fails."""
        mock_import_result = MagicMock()
        mock_import_result.status = ImportStatus.FAILED
        mock_import_result.error = "Import failed"

        with patch(
            "enterprise_chat_api.services.qa_flow_service.AppDslService"
        ) as MockAppDslService:
            MockAppDslService.return_value.import_app.return_value = mock_import_result

            service = QAFlowService(mock_db)

            with pytest.raises(ValueError, match="Failed to import app"):
                service.create_department_qa_flow(
                    department=mock_department,
                    flow_data=mock_qa_flow_create,
                    created_by=mock_account.id,
                )

    def test_create_personal_qa_flow_success(self, mock_db, mock_account, mock_qa_flow_create):
        """Test successful creation of a personal QA flow."""
        app_id = str(uuid4())

        mock_import_result = MagicMock()
        mock_import_result.status = ImportStatus.COMPLETED
        mock_import_result.app_id = app_id

        with patch(
            "enterprise_chat_api.services.qa_flow_service.AppDslService"
        ) as MockAppDslService:
            MockAppDslService.return_value.import_app.return_value = mock_import_result

            service = QAFlowService(mock_db)
            flow = service.create_personal_qa_flow(
                flow_data=mock_qa_flow_create,
                account_id=mock_account.id,
                tenant_id=mock_account.tenant_id,
            )

            MockAppDslService.return_value.import_app.assert_called_once()
            call_kwargs = MockAppDslService.return_value.import_app.call_args.kwargs
            assert call_kwargs["name"] == mock_qa_flow_create.name
            assert call_kwargs["import_mode"] == "yaml-content"

            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()

            # Verify the added object has correct properties
            added_obj = mock_db.add.call_args[0][0]
            assert isinstance(added_obj, PersonalQAFlow)
            assert added_obj.tenant_id == mock_account.tenant_id
            assert added_obj.account_id == mock_account.id
            assert added_obj.workflow_id is None  # chat mode has no workflow
            assert added_obj.status == "active"

    def test_create_personal_qa_flow_account_not_found(self, mock_db, mock_qa_flow_create):
        """Test personal QA flow creation when account is not found."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        service = QAFlowService(mock_db)

        with pytest.raises(ValueError, match="Account not found"):
            service.create_personal_qa_flow(
                flow_data=mock_qa_flow_create,
                account_id="nonexistent-id",
                tenant_id="test-tenant",
            )

    def test_update_department_qa_flow(self, mock_db):
        """Test updating a department QA flow."""
        flow = MagicMock(spec=DepartmentQAFlow)
        flow.name = "旧名称"
        flow.description = "旧描述"
        flow.dataset_ids = []
        flow.status = "active"

        update_data = QAFlowUpdate(
            name="新名称",
            description="新描述",
            dataset_ids=["ds-1"],
            status="inactive",
        )

        service = QAFlowService(mock_db)
        result = service.update_department_qa_flow(flow, update_data)

        assert flow.name == "新名称"
        assert flow.description == "新描述"
        assert flow.dataset_ids == ["ds-1"]
        assert flow.status == "inactive"
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_update_personal_qa_flow(self, mock_db):
        """Test updating a personal QA flow."""
        flow = MagicMock(spec=PersonalQAFlow)
        flow.name = "旧名称"
        flow.description = "旧描述"
        flow.dataset_ids = []
        flow.status = "active"

        update_data = QAFlowUpdate(
            name="新名称",
            description="新描述",
        )

        service = QAFlowService(mock_db)
        result = service.update_personal_qa_flow(flow, update_data)

        assert flow.name == "新名称"
        assert flow.description == "新描述"
        mock_db.commit.assert_called_once()

    def test_delete_department_qa_flow(self, mock_db):
        """Test deleting a department QA flow."""
        flow = MagicMock(spec=DepartmentQAFlow)

        service = QAFlowService(mock_db)
        service.delete_department_qa_flow(flow)

        mock_db.delete.assert_called_once_with(flow)
        mock_db.commit.assert_called_once()

    def test_delete_personal_qa_flow(self, mock_db):
        """Test deleting a personal QA flow."""
        flow = MagicMock(spec=PersonalQAFlow)

        service = QAFlowService(mock_db)
        service.delete_personal_qa_flow(flow)

        mock_db.delete.assert_called_once_with(flow)
        mock_db.commit.assert_called_once()


class TestQAFlowServiceReadDslFile:
    """Test DSL file reading functionality."""

    def test_read_dsl_file_success(self, mock_db, tmp_path):
        """Test successful reading of DSL file."""
        dsl_content = """
app:
  name: test
  mode: chat
version: "0.6.0"
"""
        dsl_file = tmp_path / "test.yml"
        dsl_file.write_text(dsl_content, encoding="utf-8")

        service = QAFlowService(mock_db)
        content = service._read_dsl_file(str(dsl_file))

        assert content == dsl_content

    def test_read_dsl_file_not_found(self, mock_db):
        """Test reading non-existent DSL file raises error."""
        service = QAFlowService(mock_db)

        with pytest.raises(FileNotFoundError):
            service._read_dsl_file("/nonexistent/path.yml")


class TestQAFlowServiceWithPendingImport:
    """Test QAFlowService with PENDING status import result."""

    def test_create_department_qa_flow_pending_status(self, mock_db, mock_department, mock_account, mock_qa_flow_create):
        """Test department QA flow creation when import returns PENDING status."""
        mock_import_result = MagicMock()
        mock_import_result.status = ImportStatus.PENDING
        mock_import_result.app_id = None
        mock_import_result.error = None

        with patch(
            "enterprise_chat_api.services.qa_flow_service.AppDslService"
        ) as MockAppDslService:
            MockAppDslService.return_value.import_app.return_value = mock_import_result

            service = QAFlowService(mock_db)

            with pytest.raises(ValueError, match="Failed to import app"):
                service.create_department_qa_flow(
                    department=mock_department,
                    flow_data=mock_qa_flow_create,
                    created_by=mock_account.id,
                )


class TestQAFlowServiceWorkflowIdBehavior:
    """Test workflow_id=None behavior for chat-mode DSL apps."""

    def test_chat_mode_app_has_no_workflow_id(self, mock_db, mock_department, mock_account, mock_qa_flow_create):
        """
        Chat-mode apps (智能问答助手.yml) do not create a Workflow record.
        Therefore the DepartmentQAFlow.workflow_id should be None.
        """
        app_id = str(uuid4())

        mock_import_result = MagicMock()
        mock_import_result.status = ImportStatus.COMPLETED
        mock_import_result.app_id = app_id

        with patch(
            "enterprise_chat_api.services.qa_flow_service.AppDslService"
        ) as MockAppDslService:
            MockAppDslService.return_value.import_app.return_value = mock_import_result

            service = QAFlowService(mock_db)
            service.create_department_qa_flow(
                department=mock_department,
                flow_data=mock_qa_flow_create,
                created_by=mock_account.id,
            )

            # Verify the stored DepartmentQAFlow has workflow_id=None
            added_obj = mock_db.add.call_args[0][0]
            assert added_obj.workflow_id is None
            assert added_obj.app_id == app_id

    def test_department_qa_flow_dataset_ids_stored(self, mock_db, mock_department, mock_account, mock_qa_flow_create):
        """Dataset IDs provided in QAFlowCreate are stored in the flow record."""
        app_id = str(uuid4())
        mock_qa_flow_create.dataset_ids = ["ds-1", "ds-2"]

        mock_import_result = MagicMock()
        mock_import_result.status = ImportStatus.COMPLETED
        mock_import_result.app_id = app_id

        with patch(
            "enterprise_chat_api.services.qa_flow_service.AppDslService"
        ) as MockAppDslService:
            MockAppDslService.return_value.import_app.return_value = mock_import_result

            service = QAFlowService(mock_db)
            service.create_department_qa_flow(
                department=mock_department,
                flow_data=mock_qa_flow_create,
                created_by=mock_account.id,
            )

            added_obj = mock_db.add.call_args[0][0]
            assert added_obj.dataset_ids == ["ds-1", "ds-2"]

    def test_department_qa_flow_default_status_is_active(self, mock_db, mock_department, mock_account, mock_qa_flow_create):
        """Newly created department QA flows have status='active' by default."""
        app_id = str(uuid4())

        mock_import_result = MagicMock()
        mock_import_result.status = ImportStatus.COMPLETED
        mock_import_result.app_id = app_id

        with patch(
            "enterprise_chat_api.services.qa_flow_service.AppDslService"
        ) as MockAppDslService:
            MockAppDslService.return_value.import_app.return_value = mock_import_result

            service = QAFlowService(mock_db)
            service.create_department_qa_flow(
                department=mock_department,
                flow_data=mock_qa_flow_create,
                created_by=mock_account.id,
            )

            added_obj = mock_db.add.call_args[0][0]
            assert added_obj.status == "active"

