from fastapi import FastAPI, Depends, HTTPException, Path
from typing import Annotated
import models
from starlette import status
from models import Todos
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from request_models import TodosRequest

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

# Setting up the database connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency: Session = Depends(get_db)


@app.get('/todos', status_code=status.HTTP_200_OK)
async def get_all(db = db_dependency):
    todos = db.query(Todos).all()
    return todos


@app.get('/todos/{todo_id}', status_code=status.HTTP_200_OK)
async def get_todo_by_id(todo_id: int= Path(gt=0), db = db_dependency):
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@app.post('/todos', status_code=status.HTTP_201_CREATED)
async def create_todo(todo_request: TodosRequest, db = db_dependency):
    todo_model = Todos(**todo_request.model_dump())
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)
    # Return the newly created todo
    return todo_model
