"""
Fixtures for enterprise_chat_api unit tests.
"""
import os
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest


# Ensure OpenDAL fs writes to tmp to avoid polluting workspace
os.environ.setdefault("OPENDAL_SCHEME", "fs")
os.environ.setdefault("OPENDAL_FS_ROOT", "/tmp/dify-storage")
os.environ.setdefault("STORAGE_TYPE", "opendal")


@pytest.fixture
def mock_account():
    """Create a mock Account object."""
    account = MagicMock()
    account.id = str(uuid4())
    account.name = "test_user"
    account.email = "test@example.com"
    account.tenant_id = "test-tenant-id"
    account.current_tenant_id = "test-tenant-id"
    return account


@pytest.fixture
def mock_department(mock_account):
    """Create a mock Department object."""
    department = MagicMock()
    department.id = str(uuid4())
    department.tenant_id = mock_account.tenant_id
    department.name = "测试部门"
    department.created_by = mock_account.id
    return department


@pytest.fixture
def mock_current_user():
    """Create a mock current user."""
    user = MagicMock()
    user.id = str(uuid4())
    user.tenant_id = "test-tenant-id"
    user.name = "测试用户"
    return user


@pytest.fixture
def mock_db():
    """
    Create a mock database session.

    Returns a simple MagicMock that tests can configure as needed.
    Tests should set mock_db.query.return_value.filter.return_value.first.return_value
    or mock_db.query.return_value.filter.return_value.all.return_value appropriately.
    """
    db = MagicMock()
    return db


@pytest.fixture
def mock_app_dsl_result():
    """Create a mock AppDslService import result."""
    from services.app_dsl_service import ImportStatus

    result = MagicMock()
    result.status = ImportStatus.COMPLETED
    result.app_id = str(uuid4())
    result.error = None
    return result


@pytest.fixture
def mock_qa_flow_create():
    """Create a QAFlowCreate schema for testing."""
    from enterprise_chat_api.schemas.department_qa_flow import QAFlowCreate

    return QAFlowCreate(
        name="测试问答流",
        description="这是一个测试问答流",
        dataset_ids=["dataset-1", "dataset-2"],
    )


def setup_mock_db_query(mock_db, query_results):
    """
    Helper to set up mock DB query with different return values per model type.

    Args:
        mock_db: The mocked db object
        query_results: Dict mapping model class names to their mock return values.
                      Example: {"Department": department, "Account": account}
    """
    def query_side_effect(model):
        mock_query = MagicMock()

        def filter_side_effect(*args, **kwargs):
            mock_filter = MagicMock()

            def first_side_effect():
                model_name = model.__name__ if hasattr(model, "__name__") else str(model)
                return query_results.get(model_name)

            mock_filter.first.side_effect = first_side_effect

            def all_side_effect():
                model_name = model.__name__ if hasattr(model, "__name__") else str(model)
                result = query_results.get(model_name)
                return [result] if result else []

            mock_filter.all.side_effect = all_side_effect
            return mock_filter

        mock_query.filter.return_value = filter_side_effect()
        mock_query.filter_by.return_value = filter_side_effect()
        return mock_query

    mock_db.query.side_effect = query_side_effect
