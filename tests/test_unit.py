import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, AddressQuery

# Используем SQLite базу данных в памяти для тестирования
DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture
def test_db():
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_create_address_query(test_db):
    """Тест создания записи AddressQuery в базе данных."""
    # Создаем тестовый запрос адреса
    test_address = "TJRabPrwbZy45sbavfcjinPJC18kjpRTv8"
    db_record = AddressQuery(
        address=test_address, balance_trx=100.5, bandwidth=1000, energy=2000
    )

    # Добавляем в базу данных и сохраняем
    test_db.add(db_record)
    test_db.commit()
    test_db.refresh(db_record)

    # Запрашиваем базу данных, чтобы проверить, была ли запись сохранена
    saved_record = (
        test_db.query(AddressQuery).filter(AddressQuery.address == test_address).first()
    )

    # Проверяем, что запись была сохранена правильно
    assert saved_record is not None
    assert saved_record.address == test_address
    assert saved_record.balance_trx == 100.5
    assert saved_record.bandwidth == 1000
    assert saved_record.energy == 2000
