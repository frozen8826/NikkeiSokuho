from fastapi import FastAPI

app = FastAPI()#インスタンス化

@app.get("/")#ルーティング　@はdecorator
async def index():
    return {"message":"Hello my nigga"}
