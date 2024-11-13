from fastapi import FastAPI, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from neomodel import StructuredNode, StringProperty, IntegerProperty, config
from fastapi.security import OAuth2PasswordBearer

# Конфигурация подключения к Neo4j
config.DATABASE_URL = 'bolt://neo4j:neo4jpassword@localhost:7687'

app = FastAPI()


# Авторизация с помощью токена
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def authenticate(token: str = Depends(oauth2_scheme)):
    if token != "token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return token

# Модель для узлов
class MyNode(StructuredNode):
    node_id = StringProperty(unique_index=True, required=True)  # Используем node_id вместо id
    home_town = StringProperty()
    name = StringProperty()
    screen_name = StringProperty()
    sex = StringProperty()
    followers_count = IntegerProperty()  # Поле для followers_count теперь int
    subscriptions_count = IntegerProperty()  # Поле для subscriptions_count теперь int
    neo4j_id = StringProperty()  # Для хранения id из базы данных (если потребуется)

    __label__ = "User"

# Модели данных для запросов/ответов
class NodeResponse(BaseModel):
    node_id: str
    home_town: Optional[str] = "Unknown"
    name: Optional[str] = "Unknown"
    screen_name: Optional[str] = "Unknown"
    sex: Optional[str] = "Unknown"
    followers_count: Optional[int] = 0  # Параметр типа int
    subscriptions_count: Optional[int] = 0  # Параметр типа int
    neo4j_id: Optional[str] = "Unknown"

# Эндпоинт для получения всех узлов
@app.get("/nodes", response_model=List[NodeResponse])
async def get_nodes():
    try:
        nodes = MyNode.nodes.all()  # Получаем все узлы с меткой "User"
        return [
            {
                "node_id": node.node_id if node.node_id is not None else "Unknown",
                "home_town": node.home_town or "Unknown",
                "name": node.name or "Unknown",
                "screen_name": node.screen_name or "Unknown",
                "sex": node.sex or "Unknown",
                "followers_count": node.followers_count or 0,  # Если followers_count None, ставим 0
                "subscriptions_count": node.subscriptions_count or 0,  # Если subscriptions_count None, ставим 0
                "neo4j_id": node.neo4j_id or "Unknown"  # Если neo4j_id None, ставим "Unknown"
            }
            for node in nodes
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving nodes: {e}")

# Эндпоинт для получения конкретного узла
@app.get("/node/{node_id}", response_model=NodeResponse)
async def get_node(node_id: str):
    try:
        node = MyNode.nodes.get(node_id=node_id)  # Получаем узел по node_id
        return {
            "node_id": node.node_id,
            "home_town": node.home_town,
            "name": node.name,
            "screen_name": node.screen_name,
            "sex": node.sex,
            "followers_count": node.followers_count,
            "subscriptions_count": node.subscriptions_count,
            "neo4j_id": node.neo4j_id  # Добавляем neo4j id
        }
    except MyNode.DoesNotExist:
        raise HTTPException(status_code=404, detail="Node not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving node: {e}")

# Эндпоинт для добавления узлов (с токеном авторизации)
@app.post("/nodes", status_code=201)
async def add_node(node: NodeResponse, token: str = Depends(authenticate)):
    try:
        new_node = MyNode(
            node_id=node.node_id,
            home_town=node.home_town,
            name=node.name,
            screen_name=node.screen_name,
            sex=node.sex,
            followers_count=node.followers_count,
            subscriptions_count=node.subscriptions_count,
            neo4j_id=node.neo4j_id  # Сохраняем neo4j_id, если оно было передано
        )
        new_node.save()  # Сохраняем узел в базу данных
        return {"message": "Node added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding node: {e}")

# Эндпоинт для удаления узла (с токеном авторизации)
@app.delete("/nodes/{node_id}")
async def delete_node(node_id: str, token: str = Depends(authenticate)):
    try:
        node = MyNode.nodes.get(node_id=node_id)  # Получаем узел по node_id
        node.delete()  # Удаляем узел
        return {"message": "Node deleted"}
    except MyNode.DoesNotExist:
        raise HTTPException(status_code=404, detail="Node not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting node: {e}")