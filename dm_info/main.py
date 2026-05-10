from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import List, Optional
from datetime import datetime
import os
import re
from pydantic import validator

# Configuration de la base de données
DATABASE_URL = "sqlite:///./dm_info.db"
engine = create_engine(DATABASE_URL, echo=True)

# Modèles SQLModel
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    status: str = Field(default="online")


class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sender_name: str = Field(index=True)
    recipient_name: str = Field(index=True)
    text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class UserCreate(SQLModel):
    name: str
    email: str

    @validator('email')
    def validate_email(cls, v):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Email invalide')
        return v


class MessageCreate(SQLModel):
    sender_name: str
    recipient_name: str
    text: str


# Créer les tables
SQLModel.metadata.create_all(engine)
app = FastAPI()

# Ajouter CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Endpoints
@app.post("/api/users", response_model=User)
def create_user(user: UserCreate):
    """Créer un nouvel utilisateur"""
    with Session(engine) as session:
        # Vérifier si l'utilisateur existe déjà
        existing_user = session.exec(
            select(User).where((User.email == user.email) | (User.name == user.name))
        ).first()

        if existing_user:
            return existing_user

        db_user = User(name=user.name, email=user.email, status="online")
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user


@app.get("/api/users", response_model=List[User])
def get_users():
    """Récupérer tous les utilisateurs"""
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        return users


@app.get("/api/messages/{sender_name}/{recipient_name}", response_model=List[Message])
def get_messages(sender_name: str, recipient_name: str):
    """Récupérer les messages entre deux utilisateurs"""
    with Session(engine) as session:
        messages = session.exec(
            select(Message).where(
                ((Message.sender_name == sender_name) & (Message.recipient_name == recipient_name)) |
                ((Message.sender_name == recipient_name) & (Message.recipient_name == sender_name))
            ).order_by(Message.timestamp)
        ).all()

        return messages


@app.post("/api/messages", response_model=Message)
def send_message(message: MessageCreate):
    """Envoyer un message"""
    with Session(engine) as session:
        db_message = Message(
            sender_name=message.sender_name,
            recipient_name=message.recipient_name,
            text=message.text
        )
        session.add(db_message)
        session.commit()
        session.refresh(db_message)
        return db_message


@app.get("/api/init")
def init_db():
    """Initialiser la base de données sans ajouter d'utilisateurs fictifs"""
    # Les tables sont créées au démarrage avec SQLModel.metadata.create_all(engine)
    return {"message": "Base de données initialisée"}


@app.get("/")
def read_root():
    return {"message": "API dm_info avec FastAPI, SQLModel et SQLite est en fonctionnement"}


# WebSocket pour les connexions en temps réel
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except:
                pass


manager = ConnectionManager()


@app.websocket("/ws/chat/{user_name}")
async def websocket_endpoint(websocket: WebSocket, user_name: str):
    """WebSocket pour les messages en temps réel"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            
            # Sauvegarder le message en base de données
            with Session(engine) as session:
                db_message = Message(
                    sender_name=user_name,
                    recipient_name=data.get("recipient_name"),
                    text=data.get("text")
                )
                session.add(db_message)
                session.commit()
            
            # Diffuser à tous les clients connectés
            await manager.broadcast({
                "sender": user_name,
                "recipient": data.get("recipient_name"),
                "text": data.get("text"),
                "timestamp": datetime.utcnow().isoformat()
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast({"message": f"{user_name} a quitté le chat"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
