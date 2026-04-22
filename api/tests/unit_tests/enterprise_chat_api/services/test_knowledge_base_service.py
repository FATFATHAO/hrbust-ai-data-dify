"""
Unit tests for KnowledgeBaseService.
"""
from unittest.mock import MagicMock

from enterprise_chat_api.services.knowledge_base_service import KnowledgeBaseService


class TestKnowledgeBaseServiceGetAccessibleDatasets:
    """Test get_accessible_datasets_for_user method."""

    def test_returns_empty_when_no_permissions(self, mock_db):
        """Returns empty list when user has no dataset permissions."""
        # Mock query chain: no personal perms, no department perms
        mock_query = MagicMock()
        mock_query.filter.return_value.all.return_value = []  # personal perms
        mock_db.query.return_value = mock_query

        service = KnowledgeBaseService(mock_db)
        result = service.get_accessible_datasets_for_user("user-1", "tenant-1")

        assert result == []

    def test_returns_personal_datasets(self, mock_db):
        """Returns datasets from personal permissions."""
        # Create mock permission
        mock_perm = MagicMock()
        mock_perm.dataset_id = "ds-1"

        # Create mock dataset
        mock_dataset = MagicMock()
        mock_dataset.id = "ds-1"
        mock_dataset.name = "个人知识库"

        mock_query = MagicMock()
        # First call: personal perms query
        mock_query.filter.return_value.all.side_effect = [
            [mock_perm],  # personal perms
            [],  # user departments
            [mock_dataset],  # datasets
        ]
        mock_db.query.return_value = mock_query

        service = KnowledgeBaseService(mock_db)
        result = service.get_accessible_datasets_for_user("user-1", "tenant-1")

        assert len(result) == 1
        assert result[0].id == "ds-1"

    def test_returns_department_datasets(self, mock_db):
        """Returns datasets from department bindings."""
        # Mock department
        mock_dept = MagicMock()
        mock_dept.department_id = "dept-1"

        # Mock department binding
        mock_binding = MagicMock()
        mock_binding.dataset_id = "ds-2"

        # Mock dataset
        mock_dataset = MagicMock()
        mock_dataset.id = "ds-2"
        mock_dataset.name = "部门知识库"

        mock_query = MagicMock()
        mock_query.filter.return_value.all.side_effect = [
            [],  # no personal perms
            [mock_dept],  # user departments
            [mock_binding],  # department bindings
            [mock_dataset],  # datasets
        ]
        mock_db.query.return_value = mock_query

        service = KnowledgeBaseService(mock_db)
        result = service.get_accessible_datasets_for_user("user-1", "tenant-1")

        assert len(result) == 1
        assert result[0].id == "ds-2"

    def test_combines_personal_and_department_datasets(self, mock_db):
        """Returns combined datasets from personal and department sources."""
        mock_perm = MagicMock()
        mock_perm.dataset_id = "ds-1"

        mock_dept = MagicMock()
        mock_dept.department_id = "dept-1"

        mock_binding = MagicMock()
        mock_binding.dataset_id = "ds-2"

        mock_ds1 = MagicMock()
        mock_ds1.id = "ds-1"
        mock_ds2 = MagicMock()
        mock_ds2.id = "ds-2"

        mock_query = MagicMock()
        mock_query.filter.return_value.all.side_effect = [
            [mock_perm],
            [mock_dept],
            [mock_binding],
            [mock_ds1, mock_ds2],
        ]
        mock_db.query.return_value = mock_query

        service = KnowledgeBaseService(mock_db)
        result = service.get_accessible_datasets_for_user("user-1", "tenant-1")

        assert len(result) == 2


class TestKnowledgeBaseServiceGetDepartmentDatasets:
    """Test get_department_datasets method."""

    def test_returns_empty_when_no_bindings(self, mock_db):
        """Returns empty list when department has no dataset bindings."""
        mock_query = MagicMock()
        mock_query.filter.return_value.all.return_value = []
        mock_db.query.return_value = mock_query

        service = KnowledgeBaseService(mock_db)
        result = service.get_department_datasets("dept-1", "tenant-1")

        assert result == []

    def test_returns_bound_datasets(self, mock_db):
        """Returns datasets bound to department."""
        mock_binding = MagicMock()
        mock_binding.dataset_id = "ds-1"

        mock_dataset = MagicMock()
        mock_dataset.id = "ds-1"
        mock_dataset.name = "部门知识库"

        mock_query = MagicMock()
        mock_query.filter.return_value.all.side_effect = [
            [mock_binding],  # bindings query
            [mock_dataset],  # datasets query
        ]
        mock_db.query.return_value = mock_query

        service = KnowledgeBaseService(mock_db)
        result = service.get_department_datasets("dept-1", "tenant-1")

        assert len(result) == 1
        assert result[0].id == "ds-1"


class TestKnowledgeBaseServiceValidateDatasetIds:
    """Test validate_dataset_ids method."""

    def test_filters_inaccessible_datasets(self, mock_db):
        """Only returns dataset IDs that user can access."""
        # Mock permission with dataset_id
        mock_perm = MagicMock()
        mock_perm.dataset_id = "ds-1"

        # Mock accessible dataset
        mock_dataset = MagicMock()
        mock_dataset.id = "ds-1"
        mock_dataset.name = "测试知识库"

        # Need personal perms to populate dataset_ids, then datasets query returns the accessible one
        mock_query = MagicMock()
        mock_query.filter.return_value.all.side_effect = [
            [mock_perm],  # personal perms - populates dataset_ids with ds-1
            [],  # user departments
            [mock_dataset],  # datasets - returns the actual accessible dataset
        ]
        mock_db.query.return_value = mock_query

        service = KnowledgeBaseService(mock_db)
        result = service.validate_dataset_ids(
            dataset_ids=["ds-1", "ds-2", "ds-3"],
            user_id="user-1",
            tenant_id="tenant-1",
        )

        # Only ds-1 should be returned since it's the only accessible one
        assert result == ["ds-1"]

    def test_returns_empty_list_when_no_access(self, mock_db):
        """Returns empty list when user has no access to any requested datasets."""
        mock_query = MagicMock()
        mock_query.filter.return_value.all.side_effect = [
            [],  # personal perms
            [],  # user departments
            [],  # datasets
        ]
        mock_db.query.return_value = mock_query

        service = KnowledgeBaseService(mock_db)
        result = service.validate_dataset_ids(
            dataset_ids=["ds-1", "ds-2"],
            user_id="user-1",
            tenant_id="tenant-1",
        )

        assert result == []

    def test_returns_all_when_all_accessible(self, mock_db):
        """Returns all dataset IDs when user has access to all."""
        mock_perm1 = MagicMock()
        mock_perm1.dataset_id = "ds-1"
        mock_perm2 = MagicMock()
        mock_perm2.dataset_id = "ds-2"

        mock_ds1 = MagicMock()
        mock_ds1.id = "ds-1"
        mock_ds1.name = "知识库1"
        mock_ds2 = MagicMock()
        mock_ds2.id = "ds-2"
        mock_ds2.name = "知识库2"

        mock_query = MagicMock()
        mock_query.filter.return_value.all.side_effect = [
            [mock_perm1, mock_perm2],  # personal perms - populates dataset_ids
            [],  # user departments
            [mock_ds1, mock_ds2],  # datasets
        ]
        mock_db.query.return_value = mock_query

        service = KnowledgeBaseService(mock_db)
        result = service.validate_dataset_ids(
            dataset_ids=["ds-1", "ds-2"],
            user_id="user-1",
            tenant_id="tenant-1",
        )

        assert set(result) == {"ds-1", "ds-2"}
