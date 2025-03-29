from sqlalchemy.orm import Session
from models import BotSettings, ScanURL, ScanTime

# bot_settings のデータ取得
def get_bot_settings(db: Session):
    return db.query(BotSettings).first()

# scan_url の読み込み
def get_scan_url(db: Session):
    return db.query(ScanURL).first()

# scan_url の更新
def update_scan_url(db: Session, id: int, new_url: str):
    db_url = db.query(ScanURL).filter(ScanURL.id == id).first()  # 更新対象を取得
    if db_url is None:
        return None  # データがなければ `None` を返す（エラーハンドリング）

    db_url.url = new_url  # URL を更新
    db.commit()  # 変更を確定
    db.refresh(db_url)  # 最新のDBデータを取得
    return db_url  # 更新後のオブジェクトを返す

# scan_times の読み込み
def get_scan_time(db: Session):
    return db.query(ScanTime).all()

# scan_times の更新
def update_scan_times(db: Session, scan_times: list[str], url_id: int, bot_id: int):
    # 既存データを削除
    db.query(ScanTime).filter(ScanTime.url_id == url_id, ScanTime.bot_id == bot_id).delete()

    # 新しい scan_times を一括追加
    new_scan_times = [ScanTime(url_id=url_id, scan_time=time, bot_id=bot_id) for time in scan_times]
    db.add_all(new_scan_times)

    db.commit()
    return {"message": "Scan times updated", "added": scan_times}
