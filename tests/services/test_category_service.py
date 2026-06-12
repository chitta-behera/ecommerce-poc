from unittest.mock import Mock
import pytest
from app.services import CategoryService
from app.schemas import CategoryCreate
from app.models.domain import Category
from app.exceptions import NotFoundException


def test_get_category_by_id_found():
    # Arrange
    mock_repo = Mock()
    expected_category = Category(id=1, name="Test", description="A test category")
    mock_repo.get_by_id.return_value = expected_category
    service = CategoryService(mock_repo)

    # Act
    result = service.get_category_by_id(1)

    # Assert
    assert result == expected_category
    mock_repo.get_by_id.assert_called_once_with(1)


def test_get_category_by_id_not_found():
    # Arrange
    mock_repo = Mock()
    mock_repo.get_by_id.return_value = None
    service = CategoryService(mock_repo)

    # Act & Assert
    with pytest.raises(NotFoundException):
        service.get_category_by_id(99)
