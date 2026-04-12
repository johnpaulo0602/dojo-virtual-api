import pytest
from datetime import date
from src.academic.schemas import StudentOnboarding

def test_student_onboarding_schema_camelcase_alias():
    payload = {
        "name": "John Doe",
        "cpf": "123.456.789-00",
        "birthDate": "2010-05-15",
        "gender": "Masculino",
        "beltName": "Branca",
        "beltDegree": 1,
        "startDate": "2026-01-01",
    }

    student = StudentOnboarding.model_validate(payload)

    assert student.name == "John Doe"
    assert student.birth_date == date(2010, 5, 15)
    assert student.belt_name == "Branca"
    assert student.belt_degree == 1
    assert student.start_date == date(2026, 1, 1)
    assert student.gender == "Masculino"
