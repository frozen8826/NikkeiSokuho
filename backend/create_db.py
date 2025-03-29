from database import engine
from models import Base

# テーブルを作成
Base.metadata.create_all(bind=engine)

print("Database tables created successfully.")
