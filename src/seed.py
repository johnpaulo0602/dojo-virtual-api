"""Seed script — populates the database with test data.

Usage: cd api && uv run python -m src.seed
"""
import asyncio
from datetime import date, time
from decimal import Decimal

from sqlalchemy import select

from src.core.database import engine, AsyncSessionLocal
from src.core.security import get_password_hash
from src.identity.models import User
from src.academic.models import (
    School, Student, Guardian, StudentSchoolInfo, StudentHealthProfile,
    EmergencyContact, BeltPromotion, StudentContribution,
)
from src.classes.models import ClassGroup, ClassSchedule
from src.financial.models import FinancialTransaction, Donor
from src.config.models import Config


async def seed():
    async with AsyncSessionLocal() as db:
        # Check if data exists
        result = await db.execute(select(User))
        if result.scalars().first():
            print("Database already has data. Skipping seed.")
            return

        print("Seeding database...")

        # --- Users ---
        admin = User(email="admin@admin.com", name="Admin", hashed_password=get_password_hash("admin"), role="admin")
        inst1 = User(email="rafael@projeto.com", name="Rafael Silva", hashed_password=get_password_hash("123"), role="instrutor", belt_name="preta", belt_degree=3, specialties="guarda,raspagem")
        inst2 = User(email="camila@projeto.com", name="Camila Souza", hashed_password=get_password_hash("123"), role="instrutor", belt_name="preta", belt_degree=1, specialties="defesa pessoal,competição")
        monitor = User(email="lucas@projeto.com", name="Lucas Oliveira", hashed_password=get_password_hash("123"), role="monitor", belt_name="roxa", belt_degree=2)
        db.add_all([admin, inst1, inst2, monitor])
        await db.flush()

        # --- Schools ---
        school1 = School(name="EMEF Prof. João da Silva", address="Rua das Flores, 123 - Centro")
        school2 = School(name="Escola Estadual São Paulo", address="Av. Brasil, 456 - Jardim")
        school3 = School(name="EMEF Criança Feliz", address="Rua da Paz, 789 - Vila Nova")
        db.add_all([school1, school2, school3])
        await db.flush()

        # --- Class Groups ---
        turma1 = ClassGroup(name="Kids Iniciante", instructor_id=inst1.id, instructor_name=inst1.name, location="Sala Principal", capacity=25, age_range="6-9", status="ativa")
        turma2 = ClassGroup(name="Kids Avançado", instructor_id=inst2.id, instructor_name=inst2.name, location="Sala Principal", capacity=20, age_range="8-12", status="ativa")
        turma3 = ClassGroup(name="Juvenil", instructor_id=inst1.id, instructor_name=inst1.name, location="Sala 2", capacity=30, age_range="12-17", status="ativa")
        db.add_all([turma1, turma2, turma3])
        await db.flush()

        # Schedules
        db.add_all([
            ClassSchedule(class_group_id=turma1.id, day_of_week=1, start_time=time(14, 0), end_time=time(15, 0)),
            ClassSchedule(class_group_id=turma1.id, day_of_week=3, start_time=time(14, 0), end_time=time(15, 0)),
            ClassSchedule(class_group_id=turma2.id, day_of_week=2, start_time=time(15, 0), end_time=time(16, 0)),
            ClassSchedule(class_group_id=turma2.id, day_of_week=4, start_time=time(15, 0), end_time=time(16, 0)),
            ClassSchedule(class_group_id=turma3.id, day_of_week=1, start_time=time(16, 0), end_time=time(17, 30)),
            ClassSchedule(class_group_id=turma3.id, day_of_week=3, start_time=time(16, 0), end_time=time(17, 30)),
            ClassSchedule(class_group_id=turma3.id, day_of_week=5, start_time=time(16, 0), end_time=time(17, 30)),
        ])
        await db.flush()

        # --- Students (5 minors + 3 adults) ---
        students_data = [
            # Minors
            {"name": "Pedro Santos", "cpf": "11111111111", "birth_date": date(2014, 3, 15), "gender": "M", "phone": "(11) 99999-0001", "belt_name": "branca", "belt_degree": 2, "start_date": date(2025, 2, 1)},
            {"name": "Ana Clara Lima", "cpf": "22222222222", "birth_date": date(2012, 7, 22), "gender": "F", "phone": "(11) 99999-0002", "belt_name": "cinza", "belt_degree": 0, "start_date": date(2024, 8, 15)},
            {"name": "Lucas Ferreira", "cpf": "33333333333", "birth_date": date(2013, 11, 5), "gender": "M", "phone": "(11) 99999-0003", "belt_name": "amarela", "belt_degree": 1, "start_date": date(2024, 3, 1)},
            {"name": "Beatriz Costa", "cpf": "44444444444", "birth_date": date(2015, 1, 30), "gender": "F", "phone": "(11) 99999-0004", "belt_name": "branca", "belt_degree": 0, "start_date": date(2026, 1, 10)},
            {"name": "Gabriel Rocha", "cpf": "55555555555", "birth_date": date(2011, 9, 12), "gender": "M", "phone": "(11) 99999-0005", "belt_name": "laranja", "belt_degree": 0, "start_date": date(2023, 6, 1)},
            # Adults
            {"name": "Marcos Oliveira", "cpf": "66666666666", "birth_date": date(1990, 4, 10), "gender": "M", "phone": "(11) 99999-0006", "belt_name": "azul", "belt_degree": 2, "profession": "Engenheiro", "start_date": date(2022, 1, 15), "contributes": True, "contribution_amount": Decimal("80.00")},
            {"name": "Juliana Mendes", "cpf": "77777777777", "birth_date": date(1995, 12, 3), "gender": "F", "phone": "(11) 99999-0007", "belt_name": "branca", "belt_degree": 4, "profession": "Professora", "start_date": date(2025, 5, 1), "contributes": True, "contribution_amount": Decimal("50.00")},
            {"name": "Roberto Alves", "cpf": "88888888888", "birth_date": date(1985, 6, 20), "gender": "M", "phone": "(11) 99999-0008", "belt_name": "roxa", "belt_degree": 1, "profession": "Autônomo", "start_date": date(2020, 3, 1), "contributes": True, "contribution_amount": Decimal("100.00")},
        ]

        students = []
        for i, data in enumerate(students_data):
            s = Student(matricula=f"MAT{10001 + i}", **data)
            db.add(s)
            students.append(s)
        await db.flush()

        # --- Guardians (for minors) ---
        db.add_all([
            Guardian(student_id=students[0].id, name="Maria Santos", cpf="10000000001", relationship_type="mae", phone="(11) 98888-0001", is_primary=True),
            Guardian(student_id=students[1].id, name="Roberto Lima", cpf="10000000002", relationship_type="pai", phone="(11) 98888-0002", is_primary=True),
            Guardian(student_id=students[1].id, name="Fernanda Lima", cpf="10000000003", relationship_type="mae", phone="(11) 98888-0003"),
            Guardian(student_id=students[2].id, name="Claudia Ferreira", cpf="10000000004", relationship_type="mae", phone="(11) 98888-0004", is_primary=True),
            Guardian(student_id=students[3].id, name="José Costa", cpf="10000000005", relationship_type="pai", phone="(11) 98888-0005", is_primary=True),
            Guardian(student_id=students[4].id, name="Sandra Rocha", cpf="10000000006", relationship_type="mae", phone="(11) 98888-0006", is_primary=True),
        ])

        # --- School Info (for minors) ---
        db.add_all([
            StudentSchoolInfo(student_id=students[0].id, school_id=school1.id, is_student=True, school_level="fundamental", school_year="5", school_shift="manha"),
            StudentSchoolInfo(student_id=students[1].id, school_id=school2.id, is_student=True, school_level="fundamental", school_year="7", school_shift="tarde"),
            StudentSchoolInfo(student_id=students[2].id, school_id=school1.id, is_student=True, school_level="fundamental", school_year="6", school_shift="manha"),
            StudentSchoolInfo(student_id=students[3].id, school_id=school3.id, is_student=True, school_level="fundamental", school_year="4", school_shift="manha"),
            StudentSchoolInfo(student_id=students[4].id, school_id=school2.id, is_student=True, school_level="medio", school_year="1", school_shift="manha"),
        ])

        # --- Health Profiles ---
        db.add_all([
            StudentHealthProfile(student_id=students[0].id, blood_type="O+"),
            StudentHealthProfile(student_id=students[1].id, allergies="Poeira", blood_type="A+"),
            StudentHealthProfile(student_id=students[5].id, conditions="Asma leve", blood_type="B+"),
        ])

        # --- Emergency Contacts ---
        db.add_all([
            EmergencyContact(student_id=students[0].id, name="Maria Santos", phone="(11) 98888-0001", relationship_type="mae"),
            EmergencyContact(student_id=students[1].id, name="Roberto Lima", phone="(11) 98888-0002", relationship_type="pai"),
            EmergencyContact(student_id=students[5].id, name="Carla Oliveira", phone="(11) 97777-0001", relationship_type="conjuge"),
            EmergencyContact(student_id=students[6].id, name="Paulo Mendes", phone="(11) 97777-0002", relationship_type="amigo"),
            EmergencyContact(student_id=students[7].id, name="Sandra Alves", phone="(11) 97777-0003", relationship_type="conjuge"),
        ])

        # --- Belt Promotions ---
        db.add_all([
            BeltPromotion(student_id=students[1].id, previous_belt="branca", previous_degree=4, new_belt="cinza", new_degree=0, promoted_by="Rafael Silva", date=date(2025, 12, 15)),
            BeltPromotion(student_id=students[2].id, previous_belt="cinza", previous_degree=4, new_belt="amarela", new_degree=0, promoted_by="Rafael Silva", date=date(2025, 6, 20)),
            BeltPromotion(student_id=students[2].id, previous_belt="amarela", previous_degree=0, new_belt="amarela", new_degree=1, promoted_by="Camila Souza", date=date(2026, 1, 15)),
            BeltPromotion(student_id=students[7].id, previous_belt="marrom", previous_degree=4, new_belt="roxa", new_degree=0, promoted_by="Rafael Silva", date=date(2024, 11, 1)),
        ])

        # --- Contributions ---
        db.add_all([
            StudentContribution(student_id=students[5].id, reference="Jan/2026", amount=Decimal("80.00"), date=date(2026, 1, 10), method="pix", status="pago"),
            StudentContribution(student_id=students[5].id, reference="Fev/2026", amount=Decimal("80.00"), date=date(2026, 2, 12), method="pix", status="pago"),
            StudentContribution(student_id=students[5].id, reference="Mar/2026", amount=Decimal("80.00"), date=date(2026, 3, 8), method="transferencia", status="pago"),
            StudentContribution(student_id=students[6].id, reference="Mar/2026", amount=Decimal("50.00"), date=date(2026, 3, 15), method="dinheiro", status="pago"),
            StudentContribution(student_id=students[7].id, reference="Mar/2026", amount=Decimal("100.00"), date=date(2026, 3, 5), method="pix", status="pago"),
        ])

        # --- Financial Transactions ---
        db.add_all([
            FinancialTransaction(type="receita", category="doacao", description="Doação empresa ABC", amount=Decimal("2000.00"), date=date(2026, 3, 1), status="pago"),
            FinancialTransaction(type="receita", category="evento", description="Campeonato interno", amount=Decimal("500.00"), date=date(2026, 3, 15), status="pago"),
            FinancialTransaction(type="despesa", category="material", description="Compra de kimonos", amount=Decimal("800.00"), date=date(2026, 3, 10), status="pago"),
            FinancialTransaction(type="despesa", category="transporte", description="Ônibus competição", amount=Decimal("350.00"), date=date(2026, 4, 5), status="pendente"),
            FinancialTransaction(type="despesa", category="alimentacao", description="Lanches para treino", amount=Decimal("120.00"), date=date(2026, 4, 1), status="pago"),
        ])

        # --- Donors ---
        donor1 = Donor(name="Empresa ABC Ltda", email="contato@abc.com", phone="(11) 3000-1111", type="pessoa_juridica", document="12.345.678/0001-90")
        donor2 = Donor(name="Carlos Mendonça", email="carlos@email.com", phone="(11) 99888-1111", type="pessoa_fisica", document="123.456.789-00")
        db.add_all([donor1, donor2])
        await db.flush()

        # --- Categories config ---
        db.add(Config(key="financial_categories", value={"categories": [
            {"id": "c1", "name": "Doações", "type": "receita", "description": "Doações de pessoas físicas e jurídicas"},
            {"id": "c2", "name": "Patrocínio", "type": "receita", "description": "Patrocínios de empresas parceiras"},
            {"id": "c3", "name": "Eventos", "type": "receita", "description": "Receita de eventos e competições"},
            {"id": "c4", "name": "Venda de Materiais", "type": "receita", "description": "Venda de kimonos e equipamentos"},
            {"id": "c5", "name": "Material Esportivo", "type": "despesa", "description": "Compra de kimonos, faixas e equipamentos"},
            {"id": "c6", "name": "Transporte", "type": "despesa", "description": "Transporte para competições e eventos"},
            {"id": "c7", "name": "Alimentação", "type": "despesa", "description": "Lanches e refeições para alunos"},
            {"id": "c8", "name": "Infraestrutura", "type": "despesa", "description": "Manutenção do espaço e equipamentos"},
            {"id": "c9", "name": "Salários", "type": "despesa", "description": "Pagamento de instrutores e monitores"},
        ]}))

        await db.commit()
        print("Seed complete!")
        print("  Users: 4 (admin + 2 instrutores + 1 monitor)")
        print("  Schools: 3")
        print("  Class Groups: 3 (with schedules)")
        print("  Students: 8 (5 minors + 3 adults)")
        print("  Guardians: 6")
        print("  Emergency Contacts: 5")
        print("  Belt Promotions: 4")
        print("  Contributions: 5")
        print("  Financial Transactions: 5")
        print("  Donors: 2")


async def main():
    await seed()
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
