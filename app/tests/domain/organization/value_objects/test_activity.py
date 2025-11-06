import pytest

from domain.organization.exceptions import EmptyActivityNameException
from domain.organization.value_objects import ActivityNameValueObject


@pytest.mark.parametrize(
    "name,should_raise",
    [
        ("Еда", False),
        ("Мясная продукция", False),
        ("Молочная продукция", False),
        ("Автомобили", False),
        ("Грузовые", False),
        ("Легковые", False),
        ("Запчасти", False),
        ("Аксессуары", False),
        ("", True),
    ],
)
def test_activity_name_value_object(name, should_raise):
    if should_raise:
        with pytest.raises(EmptyActivityNameException):
            ActivityNameValueObject(value=name)
    else:
        obj = ActivityNameValueObject(value=name)
        assert obj.as_generic_type() == name
