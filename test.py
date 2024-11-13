from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_nodes():
    response = client.get("/nodes")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    # Дополнительная проверка на наличие хотя бы одного узла
    assert len(response.json()) > 0

def test_post_node():
    # Проверка добавления нового узла
    response = client.post("/nodes", json={
        "node_id": "5000",
        "home_town": "Moscow",
        "name": "Test User",
        "screen_name": "test_user",
        "sex": "Male",
        "followers_count": 100,
        "subscriptions_count": 50,
        "neo4j_id": "node5000"
    })
    assert response.status_code == 201
    assert response.json() == {"message": "Node added"}

    # Проверка, что узел действительно был добавлен
    get_response = client.get("/node/5000")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["node_id"] == "5000"
    assert data["name"] == "Test User"
    assert data["home_town"] == "Moscow"

def test_get_node():
    response = client.get("/node/5000")
    assert response.status_code == 200
    # Проверка на наличие поля node_id в ответе
    data = response.json()
    assert "node_id" in data
    assert data["node_id"] == "1"  # Проверка, что node_id соответствует ожидаемому



def test_delete_node():
    # Добавление узла для теста удаления
    response = client.post("/nodes", json={
        "node_id": "50000",
        "home_town": "St. Petersburg",
        "name": "Test Delete User",
        "screen_name": "test_delete_user",
        "sex": "Female",
        "followers_count": 200,
        "subscriptions_count": 30,
        "neo4j_id": "node2000"
    })
    assert response.status_code == 201

    # Удаление узла
    delete_response = client.delete("/nodes/50000")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"message": "Node deleted"}

    # Проверка, что узел был удален
    get_response = client.get("/node/50000")
    assert get_response.status_code == 404
    assert get_response.json() == {"detail": "Node not found"}