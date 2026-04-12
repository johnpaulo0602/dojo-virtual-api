"""Seed script — populates the database with rich test data.

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
    EmergencyContact, BeltPromotion, InstructorFeedback, StudentContribution,
)
from src.classes.models import ClassGroup, ClassSchedule
from src.classes.services import generate_lessons
from src.classes.schemas import LessonGenerateRequest
from src.financial.models import FinancialTransaction, Donor, Donation
from src.config.models import Config


async def seed():
    async with AsyncSessionLocal() as db:
        # Check if data exists
        result = await db.execute(select(User))
        if result.scalars().first():
            print("Database already has data. Skipping seed.")
            return

        print("Seeding database...")

        # ------------------------------------------------------------------ #
        # USERS                                                                #
        # ------------------------------------------------------------------ #
        admin = User(
            email="admin@admin.com", name="Admin",
            hashed_password=get_password_hash("admin"), role="admin",
        )
        inst1 = User(
            email="rafael@projeto.com", name="Rafael Silva",
            hashed_password=get_password_hash("123"), role="instrutor",
            belt_name="preta", belt_degree=4,
            specialties="guarda,raspagem,competição",
        )
        inst2 = User(
            email="camila@projeto.com", name="Camila Souza",
            hashed_password=get_password_hash("123"), role="instrutor",
            belt_name="preta", belt_degree=2,
            specialties="defesa pessoal,guarda fechada",
        )
        inst3 = User(
            email="joao@projeto.com", name="João Pereira",
            hashed_password=get_password_hash("123"), role="instrutor",
            belt_name="preta", belt_degree=1,
            specialties="half guard,leg locks",
        )
        mon1 = User(
            email="lucas@projeto.com", name="Lucas Oliveira",
            hashed_password=get_password_hash("123"), role="monitor",
            belt_name="roxa", belt_degree=2,
        )
        mon2 = User(
            email="patricia@projeto.com", name="Patrícia Gomes",
            hashed_password=get_password_hash("123"), role="monitor",
            belt_name="marrom", belt_degree=0,
        )
        resp1 = User(
            email="roberto.lima@email.com", name="Roberto Lima",
            hashed_password=get_password_hash("123"), role="responsavel",
        )
        resp2 = User(
            email="claudia.ferreira@email.com", name="Cláudia Ferreira",
            hashed_password=get_password_hash("123"), role="responsavel",
        )

        db.add_all([admin, inst1, inst2, inst3, mon1, mon2, resp1, resp2])
        await db.flush()

        # ------------------------------------------------------------------ #
        # SCHOOLS                                                              #
        # ------------------------------------------------------------------ #
        school1 = School(name="EMEF Prof. João da Silva", address="Rua das Flores, 123 - Centro")
        school2 = School(name="Escola Estadual São Paulo", address="Av. Brasil, 456 - Jardim América")
        school3 = School(name="EMEF Criança Feliz", address="Rua da Paz, 789 - Vila Nova")
        school4 = School(name="Colégio Particular São Bento", address="Rua Vergueiro, 2000 - Liberdade")
        school5 = School(name="Escola Estadual Presidente Vargas", address="Av. Paulista, 900 - Bela Vista")

        db.add_all([school1, school2, school3, school4, school5])
        await db.flush()

        # ------------------------------------------------------------------ #
        # CLASS GROUPS + SCHEDULES                                             #
        # ------------------------------------------------------------------ #
        turma1 = ClassGroup(
            name="Kids Iniciante", instructor_id=inst1.id, instructor_name=inst1.name,
            location="Sala Principal", capacity=25, age_range="6-9",
            description="Turma de iniciantes de 6 a 9 anos", status="ativa",
        )
        turma2 = ClassGroup(
            name="Kids Avançado", instructor_id=inst2.id, instructor_name=inst2.name,
            location="Sala Principal", capacity=20, age_range="8-12",
            description="Turma avançada de 8 a 12 anos", status="ativa",
        )
        turma3 = ClassGroup(
            name="Juvenil", instructor_id=inst1.id, instructor_name=inst1.name,
            location="Sala 2", capacity=30, age_range="12-17",
            description="Turma juvenil de 12 a 17 anos", status="ativa",
        )
        turma4 = ClassGroup(
            name="Adulto Iniciante", instructor_id=inst3.id, instructor_name=inst3.name,
            location="Sala Principal", capacity=30, age_range="18+",
            description="Turma adulto iniciante a partir de 18 anos", status="ativa",
        )
        turma5 = ClassGroup(
            name="Competição", instructor_id=inst1.id, instructor_name=inst1.name,
            location="Sala de Competição", capacity=15, age_range="todas",
            description="Turma de competição para atletas de alto desempenho", status="ativa",
        )

        db.add_all([turma1, turma2, turma3, turma4, turma5])
        await db.flush()

        # Schedules (0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun)
        db.add_all([
            # Kids Iniciante: Mon/Wed 14:00-15:00
            ClassSchedule(class_group_id=turma1.id, day_of_week=0, start_time=time(14, 0), end_time=time(15, 0)),
            ClassSchedule(class_group_id=turma1.id, day_of_week=2, start_time=time(14, 0), end_time=time(15, 0)),
            # Kids Avançado: Tue/Thu 15:00-16:00
            ClassSchedule(class_group_id=turma2.id, day_of_week=1, start_time=time(15, 0), end_time=time(16, 0)),
            ClassSchedule(class_group_id=turma2.id, day_of_week=3, start_time=time(15, 0), end_time=time(16, 0)),
            # Juvenil: Mon/Wed/Fri 16:00-17:30
            ClassSchedule(class_group_id=turma3.id, day_of_week=0, start_time=time(16, 0), end_time=time(17, 30)),
            ClassSchedule(class_group_id=turma3.id, day_of_week=2, start_time=time(16, 0), end_time=time(17, 30)),
            ClassSchedule(class_group_id=turma3.id, day_of_week=4, start_time=time(16, 0), end_time=time(17, 30)),
            # Adulto Iniciante: Tue/Thu/Sat 19:00-20:30
            ClassSchedule(class_group_id=turma4.id, day_of_week=1, start_time=time(19, 0), end_time=time(20, 30)),
            ClassSchedule(class_group_id=turma4.id, day_of_week=3, start_time=time(19, 0), end_time=time(20, 30)),
            ClassSchedule(class_group_id=turma4.id, day_of_week=5, start_time=time(19, 0), end_time=time(20, 30)),
            # Competição: Sat 10:00-12:00
            ClassSchedule(class_group_id=turma5.id, day_of_week=5, start_time=time(10, 0), end_time=time(12, 0)),
        ])
        await db.flush()

        # ------------------------------------------------------------------ #
        # STUDENTS (8 kids + 5 juvenis + 7 adults = 20)                       #
        # ------------------------------------------------------------------ #
        students_data = [
            # ---- Kids (6-10 anos, born 2016-2020) ----
            {
                "name": "Pedro Santos", "cpf": "11111111111",
                "birth_date": date(2018, 3, 15), "gender": "M",
                "phone": "(11) 99999-0001", "belt_name": "branca", "belt_degree": 2,
                "start_date": date(2025, 2, 1),
                "address": {"logradouro": "Rua das Acácias, 45", "bairro": "Jardim das Flores", "cidade": "São Paulo", "estado": "SP", "cep": "01234-567"},
            },
            {
                "name": "Ana Clara Lima", "cpf": "22222222222",
                "birth_date": date(2017, 7, 22), "gender": "F",
                "phone": "(11) 99999-0002", "belt_name": "cinza", "belt_degree": 0,
                "start_date": date(2024, 8, 15),
                "address": {"logradouro": "Rua do Sol, 120", "bairro": "Vila Nova", "cidade": "São Paulo", "estado": "SP", "cep": "02345-678"},
            },
            {
                "name": "Lucas Ferreira", "cpf": "33333333333",
                "birth_date": date(2016, 11, 5), "gender": "M",
                "phone": "(11) 99999-0003", "belt_name": "amarela", "belt_degree": 1,
                "start_date": date(2024, 3, 1),
                "address": {"logradouro": "Av. Central, 88", "bairro": "Centro", "cidade": "São Paulo", "estado": "SP", "cep": "03456-789"},
            },
            {
                "name": "Beatriz Costa", "cpf": "44444444444",
                "birth_date": date(2019, 1, 30), "gender": "F",
                "phone": "(11) 99999-0004", "belt_name": "branca", "belt_degree": 0,
                "start_date": date(2026, 1, 10),
                "address": {"logradouro": "Rua Pinheiros, 67", "bairro": "Pinheiros", "cidade": "São Paulo", "estado": "SP", "cep": "04567-890"},
            },
            {
                "name": "Davi Rodrigues", "cpf": "55555555555",
                "birth_date": date(2020, 6, 18), "gender": "M",
                "phone": "(11) 99999-0005", "belt_name": "branca", "belt_degree": 1,
                "start_date": date(2025, 8, 5),
                "address": {"logradouro": "Rua das Palmeiras, 33", "bairro": "Mooca", "cidade": "São Paulo", "estado": "SP", "cep": "05678-901"},
            },
            {
                "name": "Sofia Almeida", "cpf": "66666666666",
                "birth_date": date(2018, 9, 12), "gender": "F",
                "phone": "(11) 99999-0006", "belt_name": "cinza", "belt_degree": 1,
                "start_date": date(2024, 5, 20),
                "address": {"logradouro": "Rua dos Ipês, 15", "bairro": "Tatuapé", "cidade": "São Paulo", "estado": "SP", "cep": "06789-012"},
            },
            {
                "name": "Miguel Carvalho", "cpf": "77777777777",
                "birth_date": date(2017, 4, 3), "gender": "M",
                "phone": "(11) 99999-0007", "belt_name": "amarela", "belt_degree": 0,
                "start_date": date(2025, 1, 15),
                "address": {"logradouro": "Av. dos Pássaros, 200", "bairro": "Santana", "cidade": "São Paulo", "estado": "SP", "cep": "07890-123"},
            },
            {
                "name": "Isabella Nunes", "cpf": "88888888888",
                "birth_date": date(2019, 12, 25), "gender": "F",
                "phone": "(11) 99999-0008", "belt_name": "branca", "belt_degree": 0,
                "start_date": date(2026, 2, 1),
                "address": {"logradouro": "Rua Consolação, 500", "bairro": "Consolação", "cidade": "São Paulo", "estado": "SP", "cep": "08901-234"},
            },
            # ---- Juvenis (11-16 anos, born 2010-2015) ----
            {
                "name": "Gabriel Rocha", "cpf": "99999999901",
                "birth_date": date(2011, 9, 12), "gender": "M",
                "phone": "(11) 99999-0009", "belt_name": "laranja", "belt_degree": 0,
                "start_date": date(2023, 6, 1),
                "address": {"logradouro": "Rua dos Bambuzais, 77", "bairro": "Lapa", "cidade": "São Paulo", "estado": "SP", "cep": "09012-345"},
            },
            {
                "name": "Fernanda Martins", "cpf": "99999999902",
                "birth_date": date(2012, 3, 8), "gender": "F",
                "phone": "(11) 99999-0010", "belt_name": "verde", "belt_degree": 0,
                "start_date": date(2022, 4, 10),
                "address": {"logradouro": "Av. Jabaquara, 340", "bairro": "Jabaquara", "cidade": "São Paulo", "estado": "SP", "cep": "10123-456"},
            },
            {
                "name": "Thiago Barbosa", "cpf": "99999999903",
                "birth_date": date(2013, 7, 20), "gender": "M",
                "phone": "(11) 99999-0011", "belt_name": "laranja", "belt_degree": 2,
                "start_date": date(2023, 9, 1),
                "address": {"logradouro": "Rua Vergueiro, 800", "bairro": "Vila Mariana", "cidade": "São Paulo", "estado": "SP", "cep": "11234-567"},
            },
            {
                "name": "Larissa Teixeira", "cpf": "99999999904",
                "birth_date": date(2010, 11, 14), "gender": "F",
                "phone": "(11) 99999-0012", "belt_name": "verde", "belt_degree": 1,
                "start_date": date(2021, 3, 15),
                "address": {"logradouro": "Rua Augusta, 1200", "bairro": "Cerqueira César", "cidade": "São Paulo", "estado": "SP", "cep": "12345-678"},
            },
            {
                "name": "Matheus Dias", "cpf": "99999999905",
                "birth_date": date(2014, 5, 5), "gender": "M",
                "phone": "(11) 99999-0013", "belt_name": "amarela", "belt_degree": 2,
                "start_date": date(2024, 1, 8),
                "address": {"logradouro": "Rua da Consolação, 900", "bairro": "Consolação", "cidade": "São Paulo", "estado": "SP", "cep": "13456-789"},
            },
            # ---- Adults (18-40 anos, born 1986-2008) ----
            {
                "name": "Marcos Oliveira", "cpf": "99999999906",
                "birth_date": date(1990, 4, 10), "gender": "M",
                "phone": "(11) 99999-0014", "belt_name": "azul", "belt_degree": 2,
                "profession": "Engenheiro Civil",
                "start_date": date(2022, 1, 15),
                "contributes": True, "contribution_amount": Decimal("80.00"),
                "address": {"logradouro": "Rua Bela Cintra, 300", "bairro": "Consolação", "cidade": "São Paulo", "estado": "SP", "cep": "14567-890"},
            },
            {
                "name": "Juliana Mendes", "cpf": "99999999907",
                "birth_date": date(1995, 12, 3), "gender": "F",
                "phone": "(11) 99999-0015", "belt_name": "branca", "belt_degree": 4,
                "profession": "Professora de Matemática",
                "start_date": date(2025, 5, 1),
                "contributes": True, "contribution_amount": Decimal("50.00"),
                "address": {"logradouro": "Rua da Liberdade, 450", "bairro": "Liberdade", "cidade": "São Paulo", "estado": "SP", "cep": "15678-901"},
            },
            {
                "name": "Roberto Alves", "cpf": "99999999908",
                "birth_date": date(1985, 6, 20), "gender": "M",
                "phone": "(11) 99999-0016", "belt_name": "roxa", "belt_degree": 1,
                "profession": "Autônomo",
                "start_date": date(2020, 3, 1),
                "contributes": True, "contribution_amount": Decimal("100.00"),
                "address": {"logradouro": "Av. Rebouças, 1500", "bairro": "Pinheiros", "cidade": "São Paulo", "estado": "SP", "cep": "16789-012"},
            },
            {
                "name": "Camila Ramos", "cpf": "99999999909",
                "birth_date": date(2000, 8, 17), "gender": "F",
                "phone": "(11) 99999-0017", "belt_name": "azul", "belt_degree": 0,
                "profession": "Estudante Universitária",
                "start_date": date(2023, 3, 10),
                "contributes": False,
                "address": {"logradouro": "Rua Pamplona, 200", "bairro": "Jardins", "cidade": "São Paulo", "estado": "SP", "cep": "17890-123"},
            },
            {
                "name": "Felipe Nascimento", "cpf": "99999999910",
                "birth_date": date(1988, 2, 28), "gender": "M",
                "phone": "(11) 99999-0018", "belt_name": "roxa", "belt_degree": 0,
                "profession": "Médico",
                "start_date": date(2021, 7, 5),
                "contributes": True, "contribution_amount": Decimal("120.00"),
                "address": {"logradouro": "Al. Santos, 800", "bairro": "Jardim Paulista", "cidade": "São Paulo", "estado": "SP", "cep": "18901-234"},
            },
            {
                "name": "Amanda Correia", "cpf": "99999999911",
                "birth_date": date(2003, 10, 30), "gender": "F",
                "phone": "(11) 99999-0019", "belt_name": "branca", "belt_degree": 3,
                "profession": "Atleta",
                "start_date": date(2024, 9, 1),
                "contributes": False,
                "address": {"logradouro": "Rua Oscar Freire, 100", "bairro": "Jardins", "cidade": "São Paulo", "estado": "SP", "cep": "19012-345"},
            },
            {
                "name": "Rodrigo Souza", "cpf": "99999999912",
                "birth_date": date(1992, 5, 14), "gender": "M",
                "phone": "(11) 99999-0020", "belt_name": "azul", "belt_degree": 3,
                "profession": "Advogado",
                "start_date": date(2022, 11, 20),
                "contributes": True, "contribution_amount": Decimal("80.00"),
                "address": {"logradouro": "Rua Haddock Lobo, 400", "bairro": "Cerqueira César", "cidade": "São Paulo", "estado": "SP", "cep": "20123-456"},
            },
        ]

        students = []
        for i, data in enumerate(students_data):
            s = Student(matricula=f"MAT{10001 + i}", **data)
            db.add(s)
            students.append(s)
        await db.flush()

        # Conveniences: index 0-7 kids, 8-12 juvenis, 13-19 adults
        kids = students[0:8]
        juvenis = students[8:13]
        adults = students[13:20]

        # ------------------------------------------------------------------ #
        # GUARDIANS (for all minors = kids + juvenis)                         #
        # ------------------------------------------------------------------ #
        db.add_all([
            # Kids
            Guardian(student_id=kids[0].id, name="Maria Santos",      cpf="10000000001", relationship_type="mae", phone="(11) 98888-0001", email="maria.santos@email.com",  profession="Comerciante",  is_primary=True),
            Guardian(student_id=kids[0].id, name="José Santos",       cpf="10000000002", relationship_type="pai", phone="(11) 98888-0002", email="jose.santos@email.com",   profession="Motorista"),

            Guardian(student_id=kids[1].id, name="Roberto Lima",      cpf="10000000003", relationship_type="pai", phone="(11) 98888-0003", email="roberto.lima@email.com",  profession="Engenheiro",   is_primary=True),
            Guardian(student_id=kids[1].id, name="Fernanda Lima",     cpf="10000000004", relationship_type="mae", phone="(11) 98888-0004", email="fernanda.lima@email.com", profession="Enfermeira"),

            Guardian(student_id=kids[2].id, name="Cláudia Ferreira",  cpf="10000000005", relationship_type="mae", phone="(11) 98888-0005", email="claudia.f@email.com",     profession="Professora",   is_primary=True),

            Guardian(student_id=kids[3].id, name="José Costa",        cpf="10000000006", relationship_type="pai", phone="(11) 98888-0006", email="jose.costa@email.com",    profession="Contador",     is_primary=True),
            Guardian(student_id=kids[3].id, name="Ana Costa",         cpf="10000000007", relationship_type="mae", phone="(11) 98888-0007"),

            Guardian(student_id=kids[4].id, name="Paulo Rodrigues",   cpf="10000000008", relationship_type="pai", phone="(11) 98888-0008", is_primary=True),

            Guardian(student_id=kids[5].id, name="Sandra Almeida",    cpf="10000000009", relationship_type="mae", phone="(11) 98888-0009", is_primary=True),
            Guardian(student_id=kids[5].id, name="Renato Almeida",    cpf="10000000010", relationship_type="pai", phone="(11) 98888-0010"),

            Guardian(student_id=kids[6].id, name="Vera Carvalho",     cpf="10000000011", relationship_type="mae", phone="(11) 98888-0011", is_primary=True),

            Guardian(student_id=kids[7].id, name="Carlos Nunes",      cpf="10000000012", relationship_type="pai", phone="(11) 98888-0012", is_primary=True),
            Guardian(student_id=kids[7].id, name="Tereza Nunes",      cpf="10000000013", relationship_type="mae", phone="(11) 98888-0013"),

            # Juvenis
            Guardian(student_id=juvenis[0].id, name="Sandra Rocha",   cpf="10000000014", relationship_type="mae", phone="(11) 98888-0014", is_primary=True),
            Guardian(student_id=juvenis[0].id, name="Marcos Rocha",   cpf="10000000015", relationship_type="pai", phone="(11) 98888-0015"),

            Guardian(student_id=juvenis[1].id, name="Luiz Martins",   cpf="10000000016", relationship_type="pai", phone="(11) 98888-0016", is_primary=True),

            Guardian(student_id=juvenis[2].id, name="Sônia Barbosa",  cpf="10000000017", relationship_type="mae", phone="(11) 98888-0017", is_primary=True),
            Guardian(student_id=juvenis[2].id, name="André Barbosa",  cpf="10000000018", relationship_type="pai", phone="(11) 98888-0018"),

            Guardian(student_id=juvenis[3].id, name="Helena Teixeira", cpf="10000000019", relationship_type="mae", phone="(11) 98888-0019", is_primary=True),

            Guardian(student_id=juvenis[4].id, name="Paulo Dias",     cpf="10000000020", relationship_type="pai", phone="(11) 98888-0020", is_primary=True),
            Guardian(student_id=juvenis[4].id, name="Laura Dias",     cpf="10000000021", relationship_type="mae", phone="(11) 98888-0021"),
        ])
        await db.flush()

        # ------------------------------------------------------------------ #
        # EMERGENCY CONTACTS                                                   #
        # ------------------------------------------------------------------ #
        db.add_all([
            EmergencyContact(student_id=kids[0].id,    name="Maria Santos",     phone="(11) 98888-0001", relationship_type="mae"),
            EmergencyContact(student_id=kids[0].id,    name="José Santos",      phone="(11) 98888-0002", relationship_type="pai"),
            EmergencyContact(student_id=kids[1].id,    name="Roberto Lima",     phone="(11) 98888-0003", relationship_type="pai"),
            EmergencyContact(student_id=kids[2].id,    name="Cláudia Ferreira", phone="(11) 98888-0005", relationship_type="mae"),
            EmergencyContact(student_id=kids[3].id,    name="José Costa",       phone="(11) 98888-0006", relationship_type="pai"),
            EmergencyContact(student_id=kids[4].id,    name="Paulo Rodrigues",  phone="(11) 98888-0008", relationship_type="pai"),
            EmergencyContact(student_id=kids[5].id,    name="Sandra Almeida",   phone="(11) 98888-0009", relationship_type="mae"),
            EmergencyContact(student_id=kids[6].id,    name="Vera Carvalho",    phone="(11) 98888-0011", relationship_type="mae"),
            EmergencyContact(student_id=kids[7].id,    name="Carlos Nunes",     phone="(11) 98888-0012", relationship_type="pai"),
            EmergencyContact(student_id=juvenis[0].id, name="Sandra Rocha",     phone="(11) 98888-0014", relationship_type="mae"),
            EmergencyContact(student_id=juvenis[1].id, name="Luiz Martins",     phone="(11) 98888-0016", relationship_type="pai"),
            EmergencyContact(student_id=juvenis[2].id, name="Sônia Barbosa",    phone="(11) 98888-0017", relationship_type="mae"),
            EmergencyContact(student_id=juvenis[3].id, name="Helena Teixeira",  phone="(11) 98888-0019", relationship_type="mae"),
            EmergencyContact(student_id=juvenis[4].id, name="Paulo Dias",       phone="(11) 98888-0020", relationship_type="pai"),
            # Adults
            EmergencyContact(student_id=adults[0].id,  name="Carla Oliveira",   phone="(11) 97777-0001", relationship_type="conjuge"),
            EmergencyContact(student_id=adults[1].id,  name="Paulo Mendes",     phone="(11) 97777-0002", relationship_type="amigo"),
            EmergencyContact(student_id=adults[2].id,  name="Sandra Alves",     phone="(11) 97777-0003", relationship_type="conjuge"),
            EmergencyContact(student_id=adults[3].id,  name="Bruna Ramos",      phone="(11) 97777-0004", relationship_type="mae"),
            EmergencyContact(student_id=adults[4].id,  name="Rafaela Nascimento", phone="(11) 97777-0005", relationship_type="conjuge"),
            EmergencyContact(student_id=adults[4].id,  name="Teresinha Nascimento", phone="(11) 97777-0006", relationship_type="mae"),
            EmergencyContact(student_id=adults[5].id,  name="Joana Correia",    phone="(11) 97777-0007", relationship_type="mae"),
            EmergencyContact(student_id=adults[6].id,  name="Bianca Souza",     phone="(11) 97777-0008", relationship_type="conjuge"),
        ])
        await db.flush()

        # ------------------------------------------------------------------ #
        # SCHOOL INFO (for minors)                                             #
        # ------------------------------------------------------------------ #
        db.add_all([
            StudentSchoolInfo(student_id=kids[0].id,    school_id=school1.id, is_student=True, school_level="fundamental", school_year="2",  school_shift="manha"),
            StudentSchoolInfo(student_id=kids[1].id,    school_id=school2.id, is_student=True, school_level="fundamental", school_year="3",  school_shift="tarde"),
            StudentSchoolInfo(student_id=kids[2].id,    school_id=school1.id, is_student=True, school_level="fundamental", school_year="4",  school_shift="manha"),
            StudentSchoolInfo(student_id=kids[3].id,    school_id=school3.id, is_student=True, school_level="fundamental", school_year="1",  school_shift="integral"),
            StudentSchoolInfo(student_id=kids[4].id,    school_id=school4.id, is_student=True, school_level="fundamental", school_year="1",  school_shift="manha"),
            StudentSchoolInfo(student_id=kids[5].id,    school_id=school2.id, is_student=True, school_level="fundamental", school_year="3",  school_shift="tarde"),
            StudentSchoolInfo(student_id=kids[6].id,    school_id=school3.id, is_student=True, school_level="fundamental", school_year="2",  school_shift="manha"),
            StudentSchoolInfo(student_id=kids[7].id,    school_id=school5.id, is_student=True, school_level="fundamental", school_year="1",  school_shift="tarde"),
            StudentSchoolInfo(student_id=juvenis[0].id, school_id=school5.id, is_student=True, school_level="fundamental", school_year="7",  school_shift="manha"),
            StudentSchoolInfo(student_id=juvenis[1].id, school_id=school2.id, is_student=True, school_level="fundamental", school_year="8",  school_shift="tarde"),
            StudentSchoolInfo(student_id=juvenis[2].id, school_id=school4.id, is_student=True, school_level="fundamental", school_year="6",  school_shift="integral"),
            StudentSchoolInfo(student_id=juvenis[3].id, school_id=school1.id, is_student=True, school_level="medio",       school_year="1",  school_shift="manha"),
            StudentSchoolInfo(student_id=juvenis[4].id, school_id=school3.id, is_student=True, school_level="fundamental", school_year="5",  school_shift="tarde"),
        ])
        await db.flush()

        # ------------------------------------------------------------------ #
        # HEALTH PROFILES (~10 students)                                       #
        # ------------------------------------------------------------------ #
        db.add_all([
            StudentHealthProfile(student_id=kids[0].id,    blood_type="O+"),
            StudentHealthProfile(student_id=kids[1].id,    allergies="Poeira, látex", blood_type="A+"),
            StudentHealthProfile(student_id=kids[2].id,    blood_type="B+"),
            StudentHealthProfile(student_id=kids[4].id,    conditions="Rinite alérgica", blood_type="AB+", observations="Usa spray nasal antes de treinos"),
            StudentHealthProfile(student_id=kids[6].id,    allergies="Amendoim", blood_type="O-"),
            StudentHealthProfile(student_id=juvenis[0].id, conditions="Asma leve", blood_type="A-", medications="Salbutamol (quando necessário)"),
            StudentHealthProfile(student_id=juvenis[2].id, blood_type="O+"),
            StudentHealthProfile(student_id=adults[0].id,  conditions="Asma leve", blood_type="B+", medications="Loratadina"),
            StudentHealthProfile(student_id=adults[2].id,  blood_type="A+", observations="Cirurgia no joelho esquerdo em 2019 — evitar pressão excessiva"),
            StudentHealthProfile(student_id=adults[4].id,  blood_type="O+", observations="Hipertensão controlada"),
        ])
        await db.flush()

        # ------------------------------------------------------------------ #
        # BELT PROMOTIONS (15+ records)                                        #
        # ------------------------------------------------------------------ #
        db.add_all([
            # Kids belt progression
            BeltPromotion(student_id=kids[1].id,    previous_belt="branca",  previous_degree=4, new_belt="cinza",   new_degree=0, promoted_by="Rafael Silva", date=date(2024, 12, 15), notes="Excelente progresso, boa técnica de queda"),
            BeltPromotion(student_id=kids[2].id,    previous_belt="branca",  previous_degree=4, new_belt="cinza",   new_degree=0, promoted_by="Rafael Silva", date=date(2024, 6, 20)),
            BeltPromotion(student_id=kids[2].id,    previous_belt="cinza",   previous_degree=4, new_belt="amarela", new_degree=0, promoted_by="Camila Souza", date=date(2024, 12, 10)),
            BeltPromotion(student_id=kids[2].id,    previous_belt="amarela", previous_degree=0, new_belt="amarela", new_degree=1, promoted_by="Camila Souza", date=date(2025, 6, 15)),
            BeltPromotion(student_id=kids[2].id,    previous_belt="amarela", previous_degree=1, new_belt="amarela", new_degree=1, promoted_by="Rafael Silva", date=date(2026, 1, 15), notes="Promovida após campeonato estadual"),
            BeltPromotion(student_id=kids[5].id,    previous_belt="branca",  previous_degree=4, new_belt="cinza",   new_degree=0, promoted_by="Rafael Silva", date=date(2025, 3, 10)),
            BeltPromotion(student_id=kids[5].id,    previous_belt="cinza",   previous_degree=0, new_belt="cinza",   new_degree=1, promoted_by="Camila Souza", date=date(2025, 9, 5)),
            # Juvenis
            BeltPromotion(student_id=juvenis[0].id, previous_belt="amarela", previous_degree=4, new_belt="laranja", new_degree=0, promoted_by="Rafael Silva", date=date(2024, 12, 15)),
            BeltPromotion(student_id=juvenis[1].id, previous_belt="laranja", previous_degree=4, new_belt="verde",   new_degree=0, promoted_by="Rafael Silva", date=date(2024, 8, 20)),
            BeltPromotion(student_id=juvenis[2].id, previous_belt="amarela", previous_degree=2, new_belt="laranja", new_degree=0, promoted_by="Camila Souza", date=date(2025, 3, 18)),
            BeltPromotion(student_id=juvenis[2].id, previous_belt="laranja", previous_degree=0, new_belt="laranja", new_degree=2, promoted_by="Rafael Silva", date=date(2025, 12, 10)),
            BeltPromotion(student_id=juvenis[3].id, previous_belt="cinza",   previous_degree=4, new_belt="verde",   new_degree=0, promoted_by="Rafael Silva", date=date(2023, 12, 15)),
            BeltPromotion(student_id=juvenis[3].id, previous_belt="verde",   previous_degree=0, new_belt="verde",   new_degree=1, promoted_by="Camila Souza", date=date(2025, 6, 8)),
            # Adults
            BeltPromotion(student_id=adults[2].id, previous_belt="marrom",  previous_degree=4, new_belt="roxa",    new_degree=0, promoted_by="Rafael Silva", date=date(2024, 11, 1), notes="Excelente competidor, merecida promoção"),
            BeltPromotion(student_id=adults[2].id, previous_belt="roxa",    previous_degree=0, new_belt="roxa",    new_degree=1, promoted_by="Rafael Silva", date=date(2026, 2, 14)),
            BeltPromotion(student_id=adults[4].id, previous_belt="azul",    previous_degree=4, new_belt="roxa",    new_degree=0, promoted_by="Rafael Silva", date=date(2025, 7, 20)),
            BeltPromotion(student_id=adults[6].id, previous_belt="azul",    previous_degree=2, new_belt="azul",    new_degree=3, promoted_by="João Pereira",  date=date(2025, 12, 20)),
        ])
        await db.flush()

        # ------------------------------------------------------------------ #
        # INSTRUCTOR FEEDBACKS (10+ records)                                   #
        # ------------------------------------------------------------------ #
        db.add_all([
            InstructorFeedback(student_id=kids[2].id,    author_id=inst1.id, date=date(2025, 10, 8),  text="Lucas demonstra ótima evolução na guarda fechada. Precisa trabalhar mais as quedas defensivas, mas a dedicação é notável."),
            InstructorFeedback(student_id=kids[2].id,    author_id=inst2.id, date=date(2026, 1, 20),  text="Excelente comprometimento no treino. A raspagem de guarda melhorou bastante desde o último trimestre."),
            InstructorFeedback(student_id=kids[5].id,    author_id=inst1.id, date=date(2025, 11, 3),  text="Sofia é muito dedicada. Sua posição de base está melhorando. Recomendo foco nas quedas."),
            InstructorFeedback(student_id=juvenis[0].id, author_id=inst1.id, date=date(2025, 9, 15),  text="Gabriel tem potencial competitivo. Sua guarda aranha está muito bem desenvolvida para a idade."),
            InstructorFeedback(student_id=juvenis[0].id, author_id=inst3.id, date=date(2026, 2, 10),  text="Recomendo Gabriel para o próximo campeonato. Half guard defensivo está excelente."),
            InstructorFeedback(student_id=juvenis[1].id, author_id=inst1.id, date=date(2025, 12, 5),  text="Fernanda é uma das alunas mais técnicas da turma juvenil. Promoção para faixa verde muito merecida."),
            InstructorFeedback(student_id=juvenis[3].id, author_id=inst2.id, date=date(2026, 1, 8),   text="Larissa demonstra liderança dentro do tatame. Boa referência para as turmas menores."),
            InstructorFeedback(student_id=adults[0].id,  author_id=inst3.id, date=date(2025, 10, 20), text="Marcos está evoluindo bem nas finalizações de perna. Treino constante, nunca falta."),
            InstructorFeedback(student_id=adults[0].id,  author_id=inst1.id, date=date(2026, 3, 5),   text="Recomendo Marcos para a turma de competição. Nível técnico está maduro para faixa roxa."),
            InstructorFeedback(student_id=adults[2].id,  author_id=inst1.id, date=date(2026, 3, 18),  text="Roberto é referência para todos os adultos. Ensina com paciência e lidera pelo exemplo."),
            InstructorFeedback(student_id=adults[4].id,  author_id=inst3.id, date=date(2026, 2, 25),  text="Felipe demonstra excelente controle de posição. Leg locks bem desenvolvidos para faixa roxa."),
            InstructorFeedback(student_id=adults[6].id,  author_id=inst3.id, date=date(2026, 4, 2),   text="Rodrigo tem evoluído muito nas últimas semanas. Candidato forte para a próxima graduação."),
        ])
        await db.flush()

        # ------------------------------------------------------------------ #
        # STUDENT CONTRIBUTIONS (20+ payments)                                 #
        # ------------------------------------------------------------------ #
        db.add_all([
            # Marcos Oliveira (adults[0]) — R$80/mês
            StudentContribution(student_id=adults[0].id, reference="Jan/2026", amount=Decimal("80.00"), date=date(2026, 1, 10), method="pix",          status="pago"),
            StudentContribution(student_id=adults[0].id, reference="Fev/2026", amount=Decimal("80.00"), date=date(2026, 2, 12), method="pix",          status="pago"),
            StudentContribution(student_id=adults[0].id, reference="Mar/2026", amount=Decimal("80.00"), date=date(2026, 3, 8),  method="transferencia", status="pago"),
            StudentContribution(student_id=adults[0].id, reference="Abr/2026", amount=Decimal("80.00"), date=date(2026, 4, 9),  method="pix",          status="pendente"),

            # Juliana Mendes (adults[1]) — R$50/mês
            StudentContribution(student_id=adults[1].id, reference="Fev/2026", amount=Decimal("50.00"), date=date(2026, 2, 5),  method="dinheiro",     status="pago"),
            StudentContribution(student_id=adults[1].id, reference="Mar/2026", amount=Decimal("50.00"), date=date(2026, 3, 15), method="dinheiro",     status="pago"),
            StudentContribution(student_id=adults[1].id, reference="Abr/2026", amount=Decimal("50.00"), date=date(2026, 4, 7),  method="dinheiro",     status="pendente"),

            # Roberto Alves (adults[2]) — R$100/mês
            StudentContribution(student_id=adults[2].id, reference="Jan/2026", amount=Decimal("100.00"), date=date(2026, 1, 5),  method="pix",         status="pago"),
            StudentContribution(student_id=adults[2].id, reference="Fev/2026", amount=Decimal("100.00"), date=date(2026, 2, 3),  method="pix",         status="pago"),
            StudentContribution(student_id=adults[2].id, reference="Mar/2026", amount=Decimal("100.00"), date=date(2026, 3, 5),  method="pix",         status="pago"),
            StudentContribution(student_id=adults[2].id, reference="Abr/2026", amount=Decimal("100.00"), date=date(2026, 4, 5),  method="pix",         status="pago"),

            # Felipe Nascimento (adults[4]) — R$120/mês
            StudentContribution(student_id=adults[4].id, reference="Jan/2026", amount=Decimal("120.00"), date=date(2026, 1, 20), method="transferencia", status="pago"),
            StudentContribution(student_id=adults[4].id, reference="Fev/2026", amount=Decimal("120.00"), date=date(2026, 2, 20), method="transferencia", status="pago"),
            StudentContribution(student_id=adults[4].id, reference="Mar/2026", amount=Decimal("120.00"), date=date(2026, 3, 20), method="transferencia", status="pago"),
            StudentContribution(student_id=adults[4].id, reference="Abr/2026", amount=Decimal("120.00"), date=date(2026, 4, 10), method="transferencia", status="pendente"),

            # Rodrigo Souza (adults[6]) — R$80/mês
            StudentContribution(student_id=adults[6].id, reference="Jan/2026", amount=Decimal("80.00"), date=date(2026, 1, 15), method="pix",          status="pago"),
            StudentContribution(student_id=adults[6].id, reference="Fev/2026", amount=Decimal("80.00"), date=date(2026, 2, 15), method="pix",          status="pago"),
            StudentContribution(student_id=adults[6].id, reference="Mar/2026", amount=Decimal("80.00"), date=date(2026, 3, 18), method="pix",          status="pago"),
            StudentContribution(student_id=adults[6].id, reference="Abr/2026", amount=Decimal("80.00"), date=date(2026, 4, 8),  method="pix",          status="pendente"),
        ])
        await db.flush()

        # ------------------------------------------------------------------ #
        # FINANCIAL TRANSACTIONS (15+)                                         #
        # ------------------------------------------------------------------ #
        tx_doacao1 = FinancialTransaction(type="receita", category="doacao",       description="Doação empresa ABC Ltda - Março",   amount=Decimal("2000.00"),  date=date(2026, 3, 1),  status="pago", paid_by="ABC Ltda")
        tx_doacao2 = FinancialTransaction(type="receita", category="doacao",       description="Doação Carlos Mendonça - Março",    amount=Decimal("500.00"),   date=date(2026, 3, 10), status="pago", paid_by="Carlos Mendonça")
        tx_patr1   = FinancialTransaction(type="receita", category="patrocinio",   description="Patrocínio Kimono Brasil - Q1",     amount=Decimal("3000.00"),  date=date(2026, 1, 5),  status="pago")
        tx_patr2   = FinancialTransaction(type="receita", category="patrocinio",   description="Patrocínio Sport Center - Março",   amount=Decimal("1500.00"),  date=date(2026, 3, 20), status="pago")
        tx_evento1 = FinancialTransaction(type="receita", category="evento",       description="Campeonato interno - inscrições",   amount=Decimal("800.00"),   date=date(2026, 3, 15), status="pago")
        tx_evento2 = FinancialTransaction(type="receita", category="evento",       description="Copa Solidária - inscrições",       amount=Decimal("1200.00"),  date=date(2026, 4, 5),  status="pendente")
        tx_mens1   = FinancialTransaction(type="receita", category="mensalidade",  description="Mensalidades Janeiro 2026",         amount=Decimal("430.00"),   date=date(2026, 1, 31), status="pago")
        tx_mens2   = FinancialTransaction(type="receita", category="mensalidade",  description="Mensalidades Fevereiro 2026",       amount=Decimal("350.00"),   date=date(2026, 2, 28), status="pago")
        tx_mens3   = FinancialTransaction(type="receita", category="mensalidade",  description="Mensalidades Março 2026",           amount=Decimal("430.00"),   date=date(2026, 3, 31), status="pago")

        tx_mat1  = FinancialTransaction(type="despesa", category="material",       description="Compra de kimonos - lote 20un",    amount=Decimal("1600.00"),  date=date(2026, 1, 15), status="pago")
        tx_mat2  = FinancialTransaction(type="despesa", category="material",       description="Faixas e tatames reposição",        amount=Decimal("450.00"),   date=date(2026, 3, 10), status="pago")
        tx_transp= FinancialTransaction(type="despesa", category="transporte",     description="Ônibus campeonato estadual",        amount=Decimal("700.00"),   date=date(2026, 4, 5),  status="pendente")
        tx_alim  = FinancialTransaction(type="despesa", category="alimentacao",    description="Lanches treino especial março",     amount=Decimal("280.00"),   date=date(2026, 3, 22), status="pago")
        tx_infra = FinancialTransaction(type="despesa", category="infraestrutura", description="Manutenção tatame principal",       amount=Decimal("900.00"),   date=date(2026, 2, 10), status="pago")
        tx_sal1  = FinancialTransaction(type="despesa", category="salarios",       description="Pro labore instrutores - Jan",     amount=Decimal("2400.00"),  date=date(2026, 1, 31), status="pago")
        tx_sal2  = FinancialTransaction(type="despesa", category="salarios",       description="Pro labore instrutores - Fev",     amount=Decimal("2400.00"),  date=date(2026, 2, 28), status="pago")
        tx_sal3  = FinancialTransaction(type="despesa", category="salarios",       description="Pro labore instrutores - Mar",     amount=Decimal("2400.00"),  date=date(2026, 3, 31), status="pago")

        db.add_all([
            tx_doacao1, tx_doacao2, tx_patr1, tx_patr2,
            tx_evento1, tx_evento2, tx_mens1, tx_mens2, tx_mens3,
            tx_mat1, tx_mat2, tx_transp, tx_alim, tx_infra,
            tx_sal1, tx_sal2, tx_sal3,
        ])
        await db.flush()

        # ------------------------------------------------------------------ #
        # DONORS + DONATIONS                                                   #
        # ------------------------------------------------------------------ #
        donor1 = Donor(
            name="ABC Ltda", email="contato@abc.com.br",
            phone="(11) 3000-1111", whatsapp="(11) 93000-1111",
            type="pessoa_juridica", document="12.345.678/0001-90",
            address="Av. Paulista, 1000 - Bela Vista, São Paulo - SP",
            notes="Parceiro desde 2025. Contato: Diretor Carlos.",
        )
        donor2 = Donor(
            name="Carlos Mendonça", email="carlos.mendonca@email.com",
            phone="(11) 99888-1111",
            type="pessoa_fisica", document="123.456.789-00",
            notes="Ex-aluno, apoia o projeto voluntariamente.",
        )
        donor3 = Donor(
            name="Sport Center LTDA", email="contato@sportcenter.com.br",
            phone="(11) 3111-2222", whatsapp="(11) 93111-2222",
            type="pessoa_juridica", document="98.765.432/0001-10",
            address="Rua do Esporte, 500 - Moema, São Paulo - SP",
            notes="Parceria de patrocínio e fornecimento de material.",
        )
        donor4 = Donor(
            name="Marina Bastos", email="marina.bastos@email.com",
            phone="(11) 98765-4321",
            type="pessoa_fisica", document="987.654.321-00",
            notes="Voluntária e doadora recorrente.",
        )

        db.add_all([donor1, donor2, donor3, donor4])
        await db.flush()

        db.add_all([
            Donation(donor_id=donor1.id, amount=Decimal("2000.00"), date=date(2026, 3, 1),  method="transferencia", description="Doação mensal março", transaction_id=tx_doacao1.id),
            Donation(donor_id=donor2.id, amount=Decimal("500.00"),  date=date(2026, 3, 10), method="pix",           description="Doação espontânea",   transaction_id=tx_doacao2.id),
        ])
        await db.flush()

        # ------------------------------------------------------------------ #
        # CATEGORIES CONFIG                                                    #
        # ------------------------------------------------------------------ #
        db.add(Config(key="financial_categories", value={"categories": [
            {"id": "c1", "name": "Doações",            "type": "receita", "description": "Doações de pessoas físicas e jurídicas"},
            {"id": "c2", "name": "Patrocínio",         "type": "receita", "description": "Patrocínios de empresas parceiras"},
            {"id": "c3", "name": "Eventos",            "type": "receita", "description": "Receita de eventos e competições"},
            {"id": "c4", "name": "Mensalidades",       "type": "receita", "description": "Contribuições mensais dos alunos"},
            {"id": "c5", "name": "Material Esportivo", "type": "despesa", "description": "Compra de kimonos, faixas e equipamentos"},
            {"id": "c6", "name": "Transporte",         "type": "despesa", "description": "Transporte para competições e eventos"},
            {"id": "c7", "name": "Alimentação",        "type": "despesa", "description": "Lanches e refeições para alunos"},
            {"id": "c8", "name": "Infraestrutura",     "type": "despesa", "description": "Manutenção do espaço e equipamentos"},
            {"id": "c9", "name": "Salários",           "type": "despesa", "description": "Pagamento de instrutores e monitores"},
        ]}))
        await db.flush()

        # ------------------------------------------------------------------ #
        # LESSONS — generate for April 2026                                    #
        # ------------------------------------------------------------------ #
        lesson_req = LessonGenerateRequest(start_date=date(2026, 4, 1), end_date=date(2026, 4, 30))
        total_lessons = 0
        for turma in [turma1, turma2, turma3, turma4, turma5]:
            lessons = await generate_lessons(db, turma.id, lesson_req)
            total_lessons += len(lessons)

        await db.commit()

        # ------------------------------------------------------------------ #
        # SUMMARY                                                              #
        # ------------------------------------------------------------------ #
        print("\nSeed complete!")
        print(f"  Users:                8  (1 admin + 3 instrutores + 2 monitores + 2 responsaveis)")
        print(f"  Schools:              5")
        print(f"  Class Groups:         5  (with 11 schedules)")
        print(f"  Students:            20  (8 kids + 5 juvenis + 7 adults)")
        print(f"  Guardians:           21")
        print(f"  Emergency Contacts:  22")
        print(f"  School Info:         13  (all minors)")
        print(f"  Health Profiles:     10")
        print(f"  Belt Promotions:     17")
        print(f"  Instructor Feedbacks:12")
        print(f"  Contributions:       19  payments")
        print(f"  Financial Txns:      17  (9 receitas + 8 despesas)")
        print(f"  Donors:               4  (2 PF + 2 PJ)")
        print(f"  Donations:            2")
        print(f"  Lessons generated:   {total_lessons}  (April 2026)")


async def main():
    await seed()
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
