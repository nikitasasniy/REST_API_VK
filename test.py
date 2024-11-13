import pytest
from fastapi.testclient import TestClient
from main import app
from main import Neo4jQueries  # Импортируем Neo4jQueries

# Создаем клиент для тестов
client = TestClient(app)

# Токен для тестов
VALID_TOKEN = "MY_TOKEN"
INVALID_TOKEN = "INVALID_TOKEN"

# Фикстура для инициализации базы данных
@pytest.fixture(scope="module")
def setup_db():
    # Создаем подключение к БД в контексте тестов
    app.state.db = Neo4jQueries("bolt://localhost:7687", "neo4j", "neo4jpassword")
    yield
    # После завершения тестов закрываем подключение
    app.state.db.close()

# Тест на получение всех узлов
def test_get_all_nodes(setup_db):
    response = client.get("/nodes", headers={"Authorization": f"Bearer {VALID_TOKEN}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Тест на получение узла по ID
def test_get_node(setup_db):
    # Сначала добавим тестовый узел
    node_data = {
        "label": "TestLabel",
        "properties": {"id": 1, "name": "Test Node"},
        "relationships": []
    }
    response = client.post("/nodes", json=node_data, headers={"Authorization": f"Bearer {VALID_TOKEN}"})
    assert response.status_code == 200

    # Теперь получим этот узел
    node_id = 1  # Мы можем использовать конкретный ID, если знаем его
    response = client.get(f"/nodes/{node_id}", headers={"Authorization": f"Bearer {VALID_TOKEN}"})
    assert response.status_code == 200
    assert "node" in response.json()[0]

# Тест на добавление узла
def test_add_node(setup_db):
    node_data = {
        "label": "Person",
        "properties": {"id": 2, "name": "John Doe"},
        "relationships": [{"target_id": 1, "attributes": {"type": "friend"}}]
    }
    response = client.post("/nodes", json=node_data, headers={"Authorization": f"Bearer {VALID_TOKEN}"})
    assert response.status_code == 200
    assert response.json() == {"message": "Node and relationships added successfully"}

    # Проверим, что узел добавлен
    response = client.get("/nodes", headers={"Authorization": f"Bearer {VALID_TOKEN}"})
    assert any(node["id"] == 2 for node in response.json())

# Тест на удаление узла
def test_delete_node(setup_db):
    # Добавим узел для удаления
    node_data = {
        "label": "TestLabel",
        "properties": {"id": 3, "name": "Node to be deleted"},
        "relationships": []
    }
    response = client.post("/nodes", json=node_data, headers={"Authorization": f"Bearer {VALID_TOKEN}"})
    assert response.status_code == 200

    # Удалим узел
    node_id = 3
    response = client.delete(f"/nodes/{node_id}", headers={"Authorization": f"Bearer {VALID_TOKEN}"})
    assert response.status_code == 200
    assert response.json() == {"message": "Node and relationships deleted successfully"}

    # Проверим, что узел удален
    response = client.get(f"/nodes/{node_id}", headers={"Authorization": f"Bearer {VALID_TOKEN}"})
    assert response.status_code == 404

# Тест на авторизацию с неправильным токеном
def test_invalid_token(setup_db):
    response = client.get("/nodes", headers={"Authorization": f"Bearer {INVALID_TOKEN}"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token INVALID_TOKEN"}

# Тест на авторизацию с правильным токеном
def test_valid_token(setup_db):
    response = client.get("/nodes", headers={"Authorization": f"Bearer {VALID_TOKEN}"})
    assert response.status_code == 200
