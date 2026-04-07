from sqlmodel import SQLModel, Field, Session, create_engine, select
from fastapi import FastAPI, Depends
from typing import List
from sqlmodel import Relationship


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str 
    email: str
    message_envoyes: List["Message"] = Relationship(back_populates="sender")
    message_reçus: List["Message"] = Relationship(back_populates="recipient")

class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    subject: str
    content: str

    sender: User = Relationship(back_populates="message_envoyes")
    sender_id: int = Field(foreign_key="user.id")
    
    recipient: User = Relationship(back_populates="message_reçus")
    recipient_id: int = Field(foreign_key="user.id")
    
    date_sent: str
    status : str= "unread"

database_url = "sqlite:///./users.db"
engine = create_engine(database_url, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)
init_db()
def get_session():
    with Session(engine) as session:
        yield session

app = FastAPI()

@app.post("/users/", response_model=User)
def create_user(name: str, email: str, session: Session = Depends(get_session)):
    user = User(name=name, email=email)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@app.get("/users/", response_model=List[User])
def read_user(id : int, session: Session = Depends(get_session)):
    user = session.query(User).where(User.id == id)
    return user

@app.post("/users/", response_model=Message)
def create_message(subject: str, content: str, sender_id: int, recipient_id: int, date_sent: str, session: Session = Depends(get_session)):
    message = Message(subject=subject, content=content, sender_id=sender_id, recipient_id=recipient_id, date_sent=date_sent)
    session.add(message)
    session.commit()
    session.refresh(message)
    return message

@app.get("/users/", response_model=List[Message])
def read_message(id : int, session: Session = Depends(get_session)):
    message = session.query(Message).where(Message.id == id)
    return message






