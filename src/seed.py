import asyncio
import logging
from datetime import date, time
from decimal import Decimal
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.core.database import async_sessionmaker, engine
from src.academic.models import School, Student, Guardian, StudentSchoolInfo, StudentHealthProfile
from src.classes.models import ClassGroup, ClassSchedule
from src.financial.models import Donor, Donation, FinancialTransaction
from src.core.setup import create_initial_admin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def clear_database(session: AsyncSession):
    logger.info("Limpando banco de dados...")
    # truncate mantendo a tabela alembic_version intacta
    await session.execute(text("""
        TRUNCATE TABLE 
            user_identities, refresh_tokens, users,
            student_health_profiles, student_school_info, guardians, students, schools,
            attendance_records, lessons, class_schedules, class_groups,
            donations, donors, financial_transactions
        CASCADE;
    """))
    await session.commit()

async def seed_academic(session: AsyncSession):
    logger.info("Semeando Domínio Acadêmico...")
    
    escolas = [
        School(name="E.M. Santos Dumont", address="Rua das Flores, Centro"),
        School(name="E.M. Machado de Assis", address="Av. Brasil, 100"),
        School(name="Colégio São José", address="Rua São Paulo, 88"),
    ]
    session.add_all(escolas)
    await session.flush()
    
    aluno1 = Student(
        name="Lucas Ferreira", cpf="123.456.789-00", rg="12.345.678-9",
        matricula="MAT-2026-001", birth_date=date(2012, 3, 15), gender="masculino",
        email="lucas@email.com", phone="(11) 99999-1111",
        belt_name="white_belt", belt_degree=0, status="ativo",
        address={"cep": "01001-000", "street": "Rua das Flores", "number": "45", "neighborhood": "Centro", "city": "São Paulo", "state": "SP"}
    )
    session.add(aluno1)
    await session.flush()
    
    g1 = Guardian(student_id=aluno1.id, name="Maria Ferreira", cpf="111.222.333-44", relationship_type="mae", phone="(11) 98888-1111", email="maria.f@email.com", profession="Professora", is_primary=True)
    g2 = Guardian(student_id=aluno1.id, name="José Ferreira", cpf="222.333.444-55", relationship_type="pai", phone="(11) 97777-2222", email="jose.f@email.com", profession="Eletricista", is_primary=False)
    s1_info = StudentSchoolInfo(student_id=aluno1.id, school_id=escolas[0].id, school_level="Fundamental I", school_year="5º ano", school_shift="Manhã")
    session.add_all([g1, g2, s1_info])
    
    aluno2 = Student(
        name="Beatriz Lima", cpf="234.567.890-11", matricula="MAT-2026-002",
        birth_date=date(2011, 7, 22), gender="feminino",
        belt_name="white_belt", belt_degree=2, status="ativo"
    )
    session.add(aluno2)
    await session.flush()
    
    g3 = Guardian(student_id=aluno2.id, name="Claudia Lima", cpf="333.444.555-66", relationship_type="mae", phone="(11) 96666-3333", email="claudia.l@email.com", profession="Enfermeira", is_primary=True)
    s2_info = StudentSchoolInfo(student_id=aluno2.id, school_id=escolas[1].id, school_level="Fundamental II", school_year="6º ano", school_shift="Manhã")
    session.add_all([g3, s2_info])
    
    await session.commit()

async def seed_classes(session: AsyncSession):
    logger.info("Semeando Domínio de Turmas...")
    cg1 = ClassGroup(
        name="Kids Iniciante", description="Turma para crianças de 6 a 9 anos, faixa branca",
        instructor_id=uuid.uuid4(), instructor_name="Prof. Ricardo Silva",
        location="Quadra Principal", capacity=25, status="ativa",
        age_range="6-9 anos", belt_range="Branca"
    )
    session.add(cg1)
    await session.flush()
    
    # Terças (1) e Quintas (3) no python o weekday() 0 é segunda, então terça é 1, quinta é 3
    sched1 = ClassSchedule(class_group_id=cg1.id, day_of_week=1, start_time=time(14,0), end_time=time(15,0))
    sched2 = ClassSchedule(class_group_id=cg1.id, day_of_week=3, start_time=time(14,0), end_time=time(15,0))
    session.add_all([sched1, sched2])
    
    await session.commit()

async def seed_finance(session: AsyncSession):
    logger.info("Semeando Domínio Financeiro...")
    donor = Donor(name="Empresa Parceira LTDA", email="contato@parceira.com.br", phone="(11) 3333-4444", type="pessoa_juridica", document="00.000.000/0001-00")
    session.add(donor)
    await session.flush()
    
    t1 = FinancialTransaction(type="receita", category="doacao", description="Doação de Tatames Novos", amount=Decimal("2500.00"), date=date.today(), status="pago", paid_by="Empresa Parceira LTDA")
    session.add(t1)
    await session.flush()
    
    d1 = Donation(donor_id=donor.id, amount=Decimal("2500.00"), date=date.today(), method="transferencia", description="Doação de Tatames Novos", transaction_id=t1.id)
    session.add(d1)
    
    t2 = FinancialTransaction(type="receita", category="mensalidade", description="Mensalidade Lucas (Abril)", amount=Decimal("150.00"), date=date.today(), status="pago", paid_by="Maria Ferreira")
    t3 = FinancialTransaction(type="despesa", category="aluguel", description="Aluguel do Galpão (Abril)", amount=Decimal("2000.00"), date=date.today(), status="pago")
    session.add_all([t2, t3])
    
    await session.commit()

async def main():
    async with async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)() as session:
        try:
            await clear_database(session)
            await seed_academic(session)
            await seed_classes(session)
            await seed_finance(session)
            
            logger.info("Semeando Usuário Admin...")
            await create_initial_admin()
            
            logger.info("Seed completo com sucesso!")
        except Exception as e:
            logger.error(f"Erro durante o seed: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(main())
