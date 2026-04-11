import pytest
from datetime import date
from src.academic.schemas import StudentOnboarding

def test_student_onboarding_schema_camelcase_alias():
    payload = {
        "name": "John Doe",
        "cpf": "123.456.789-00",
        "matricula": "20230001",
        "birthDate": "2010-05-15",
        "gender": "Masculino",
        "beltName": "Branca",
        "beltDegree": 1,
        "status": "ativo",
        "guardians": [
            {
                "name": "Jane Doe",
                "cpf": "098.765.432-11",
                "relationship": "Mãe",
                "phone": "11999999999",
                "isPrimary": True
            }
        ],
        "schoolInfo": {
            "schoolId": "123e4567-e89b-12d3-a456-426614174000",
            "schoolLevel": "Ensino Fundamental",
            "schoolYear": "6º Ano",
            "schoolShift": "Manhã"
        },
        "health": {
            "bloodType": "O+",
            "emergencyContact": "Jane Doe",
            "emergencyPhone": "11999999999"
        }
    }

    student = StudentOnboarding.model_validate(payload)
    
    assert student.name == "John Doe"
    assert student.birth_date == date(2010, 5, 15)
    assert student.belt_name == "Branca"
    assert student.belt_degree == 1
    assert len(student.guardians) == 1
    assert student.guardians[0].relationship_type == "Mãe"
    assert student.guardians[0].is_primary is True
    assert student.school_info is not None
    assert str(student.school_info.school_id) == "123e4567-e89b-12d3-a456-426614174000"
    assert student.health is not None
    assert student.health.blood_type == "O+"
