"""
Unit tests for enterprise_chat_api schemas (Pydantic validation).
"""
import pytest
from pydantic import ValidationError

from enterprise_chat_api.schemas.department_qa_flow import (
    QAFlowCreate,
    QAFlowUpdate,
    QAFlowResponse,
    QAFlowListResponse,
    DatasetInfo,
    DatasetListResponse,
)


class TestQAFlowCreate:
    """Test QAFlowCreate schema validation."""

    def test_requires_name(self):
        """Name field is required."""
        with pytest.raises(ValidationError) as exc_info:
            QAFlowCreate.model_validate({})
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("name",) for e in errors)

    def test_name_min_length(self):
        """Name cannot be empty string."""
        with pytest.raises(ValidationError) as exc_info:
            QAFlowCreate.model_validate({"name": ""})
        assert exc_info.value.errors()[0]["loc"] == ("name",)

    def test_name_max_length(self):
        """Name must not exceed 255 characters."""
        with pytest.raises(ValidationError) as exc_info:
            QAFlowCreate.model_validate({"name": "a" * 256})
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("name",) and "string_too_long" in e["type"] for e in errors)

    def test_name_valid_length(self):
        """Name at max length (255) is valid."""
        flow = QAFlowCreate(name="a" * 255)
        assert len(flow.name) == 255

    def test_description_optional(self):
        """Description is optional."""
        flow = QAFlowCreate.model_validate({"name": "测试"})
        assert flow.description is None

    def test_description_max_length(self):
        """Description must not exceed 1000 characters."""
        with pytest.raises(ValidationError) as exc_info:
            QAFlowCreate.model_validate({"name": "测试", "description": "a" * 1001})
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("description",) and "string_too_long" in e["type"] for e in errors)

    def test_dataset_ids_optional_defaults_to_empty_list(self):
        """dataset_ids defaults to empty list if not provided."""
        flow = QAFlowCreate.model_validate({"name": "测试"})
        assert flow.dataset_ids == []

    def test_dataset_ids_with_values(self):
        """dataset_ids accepts a list of strings."""
        flow = QAFlowCreate.model_validate({
            "name": "测试",
            "dataset_ids": ["ds-1", "ds-2"],
        })
        assert flow.dataset_ids == ["ds-1", "ds-2"]

    def test_valid_full_payload(self):
        """Full valid payload is accepted."""
        flow = QAFlowCreate(
            name="测试问答流",
            description="这是描述",
            dataset_ids=["ds-1"],
        )
        assert flow.name == "测试问答流"
        assert flow.description == "这是描述"
        assert flow.dataset_ids == ["ds-1"]


class TestQAFlowUpdate:
    """Test QAFlowUpdate schema validation."""

    def test_all_fields_optional(self):
        """All fields are optional for update."""
        update = QAFlowUpdate.model_validate({})
        assert update.name is None
        assert update.description is None
        assert update.dataset_ids is None
        assert update.status is None

    def test_name_optional_but_valid_if_provided(self):
        """Name can be updated to a valid value."""
        update = QAFlowUpdate.model_validate({"name": "新名称"})
        assert update.name == "新名称"

    def test_name_min_length(self):
        """Name cannot be set to empty string on update."""
        with pytest.raises(ValidationError) as exc_info:
            QAFlowUpdate.model_validate({"name": ""})
        assert exc_info.value.errors()[0]["loc"] == ("name",)

    def test_name_max_length(self):
        """Name must not exceed 255 characters on update."""
        with pytest.raises(ValidationError) as exc_info:
            QAFlowUpdate.model_validate({"name": "a" * 256})
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("name",) and "string_too_long" in e["type"] for e in errors)

    def test_status_valid_values(self):
        """Status accepts valid string values."""
        update_active = QAFlowUpdate.model_validate({"status": "active"})
        update_inactive = QAFlowUpdate.model_validate({"status": "inactive"})
        assert update_active.status == "active"
        assert update_inactive.status == "inactive"

    def test_dataset_ids_can_be_empty_list(self):
        """dataset_ids can be set to empty list on update."""
        update = QAFlowUpdate.model_validate({"dataset_ids": []})
        assert update.dataset_ids == []


class TestQAFlowResponse:
    """Test QAFlowResponse schema."""

    def test_from_attributes(self):
        """Response can be created from ORM model attributes."""
        # Simulate ORM model with from_attributes=True
        class MockFlow:
            id = "flow-1"
            tenant_id = "tenant-1"
            department_id = "dept-1"
            created_by = "user-1"
            name = "测试流"
            description = "描述"
            dsl_file_path = "/path/to/dsl.yml"
            app_id = "app-1"
            workflow_id = None
            dataset_ids = ["ds-1"]
            status = "active"
            created_at = None
            updated_at = None

        response = QAFlowResponse.model_validate(MockFlow())
        assert response.id == "flow-1"
        assert response.name == "测试流"
        assert response.workflow_id is None
        assert response.dataset_ids == ["ds-1"]


class TestDatasetInfo:
    """Test DatasetInfo schema."""

    def test_valid_dataset_info(self):
        """Valid dataset info is accepted."""
        info = DatasetInfo(id="ds-1", name="知识库1", description="描述1")
        assert info.id == "ds-1"
        assert info.name == "知识库1"

    def test_description_optional(self):
        """Description is optional."""
        info = DatasetInfo(id="ds-1", name="知识库1")
        assert info.description is None


class TestDatasetListResponse:
    """Test DatasetListResponse schema."""

    def test_empty_list(self):
        """Empty dataset list response."""
        response = DatasetListResponse(data=[], total=0)
        assert response.data == []
        assert response.total == 0

    def test_with_datasets(self):
        """Dataset list response with items."""
        info1 = DatasetInfo(id="ds-1", name="知识库1")
        info2 = DatasetInfo(id="ds-2", name="知识库2")
        response = DatasetListResponse(data=[info1, info2], total=2)
        assert len(response.data) == 2
        assert response.total == 2
