import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tronpy.exceptions import ApiError
from app.main import app
from app.database import Base, get_db
from app.models import AddressQuery

# Используем SQLite базу данных в памяти для тестирования
DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture
def fake_env(monkeypatch):
    """Setup fake environment variables for testing."""
    test_env = {
        "DATABASE_URL": DATABASE_URL,
        "TRON_NETWORK": "shasta",  # Test network
    }

    for key, value in test_env.items():
        monkeypatch.setenv(key, value)

    return test_env


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


@pytest.fixture
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_get_address_info(client):
    """Тест эндпоинта POST /addresses/ для получения информации об адресе."""
    test_address = "TJRabPrwbZy45sbavfcjinPJC18kjpRTv8"

    # Мокаем ответы от Tron API
    with patch("app.endpoints.addresses.tron_client") as mock_tron:
        # Настраиваем моки для ответов
        mock_tron.get_account.return_value = {"balance": 15456907}
        mock_tron.get_account_resource.return_value = {
            "freeNetLimit": 1500,
            "freeNetUsed": 900,
            "EnergyLimit": 1000,
            "EnergyUsed": 1000,
        }

        # Отправляем запрос на эндпоинт
        response = client.post("/addresses/", json={"address": test_address})

        # Проверяем успешный ответ
        assert response.status_code == 200
        data = response.json()
        assert data["address"] == test_address
        assert data["balance_trx"] == 15.456907
        assert data["bandwidth"] == 600
        assert data["energy"] == 0

        # Проверяем, что метод был вызван с правильными параметрами
        mock_tron.get_account.assert_called_once_with(test_address)
        mock_tron.get_account_resource.assert_called_once_with(test_address)


def test_get_address_info_invalid_address(client):
    """Тест эндпоинта POST /addresses/ с некорректным адресом."""
    invalid_address = "invalid_address"

    # Отправляем запрос с некорректным адресом
    response = client.post("/addresses/", json={"address": invalid_address})

    # Проверяем ответ с ошибкой валидации
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_get_address_info_api_error(client):
    """Тест эндпоинта POST /addresses/ при ошибке API Tron."""
    test_address = "TJRabPrwbZy45sbavfcjinPJC18kjpRTv8"

    # Мокаем ответы от Tron API с возбуждением исключения
    with patch("app.endpoints.addresses.tron_client") as mock_tron:
        mock_tron.get_account.side_effect = ApiError()

        # Отправляем запрос на эндпоинт
        response = client.post("/addresses/", json={"address": test_address})

        # Проверяем ответ с ошибкой
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data


def test_get_address_queries(client, test_db):
    """Тест эндпоинта GET /addresses/ для получения истории запросов."""
    # Добавляем тестовые данные в базу
    for i in range(15):
        test_db.add(
            AddressQuery(
                address=f"TJRabPrwbZy45sbavfcjinPJC18kjpRTv8{i}",
                balance_trx=100.0 + i,
                bandwidth=1000 + i,
                energy=2000 + i,
            )
        )
    test_db.commit()

    # Отправляем запрос на получение первой страницы
    response = client.get("/addresses/?page=1&page_size=10")

    # Проверяем успешный ответ
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 15
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert len(data["items"]) == 10

    # Проверяем получение второй страницы
    response = client.get("/addresses/?page=2&page_size=10")
    data = response.json()
    assert data["page"] == 2
    assert len(data["items"]) == 5


def test_get_address_queries_invalid_page(client):
    """Тест эндпоинта GET /addresses/ с некорректными параметрами страницы."""
    # Отправляем запрос с некорректным номером страницы
    response = client.get("/addresses/?page=0")

    # Проверяем ответ с ошибкой валидации
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

    # Отправляем запрос с слишком большим размером страницы
    response = client.get("/addresses/?page_size=101")

    # Проверяем ответ с ошибкой валидации
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
