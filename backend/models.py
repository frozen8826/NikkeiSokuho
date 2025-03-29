from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

# bot_settings テーブル
class BotSettings(Base):
    __tablename__ = "bot_settings"

    id = Column(Integer, primary_key=True, index=True)
    bot_token = Column(Text, nullable=False)  # Token は1つのみのため、unique 制約なし

    scan_times = relationship("ScanTime", back_populates="bot")

# scan_url テーブル
class ScanURL(Base):
    __tablename__ = "scan_url"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(Text, nullable=False)

    scan_times = relationship("ScanTime", back_populates="url")

# scan_times テーブル
class ScanTime(Base):
    __tablename__ = "scan_times"

    id = Column(Integer, primary_key=True, index=True)
    url_id = Column(Integer, ForeignKey("scan_url.id"), nullable=False)
    scan_time = Column(Text, nullable=True)  # スキャン時間は可変
    bot_id = Column(Integer, ForeignKey("bot_settings.id"), nullable=False)

    url = relationship("ScanURL", back_populates="scan_times")
    bot = relationship("BotSettings", back_populates="scan_times")
