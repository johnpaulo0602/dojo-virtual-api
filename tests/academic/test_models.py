import uuid
from datetime import date
from src.academic.models import School, Student, Guardian, StudentSchoolInfo, StudentHealthProfile

def test_school_model():
    school = School(name="Test School", address="123 Test St")
    assert school.name == "Test School"
    assert school.address == "123 Test St"

def test_student_model():
    student = Student(
        name="John Doe",
        cpf="12345678900",
        matricula="2023001",
        birth_date=date(2000, 1, 1),
        gender="M",
        belt_name="White",
        belt_degree=0,
        status="ativo"
    )
    assert student.name == "John Doe"
    assert student.cpf == "12345678900"
