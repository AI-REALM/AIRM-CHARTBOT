from sqlalchemy.orm import Session, sessionmaker
from .models import User, Base, Noitfy
from .database import SessionLocal, engine

Base.metadata.create_all(bind=engine)
db = SessionLocal()

def create_user(chat_id:int):
    db_user = User(id=chat_id, indicators=None, interval="1h", style="candle", timezone="America/New_York", chain="ethereum", status="dx")
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except:
        return False
    return db_user

# Define the indicator updating function
def update_indicators(id:int, indicators:str):
    user = db.query(User).filter(User.id == id).update({"indicators" : indicators})
    try:
        db.commit()
    except:
        return False
    return user

# Define the interval updating function
def update_interval(id:int, interval:str):
    user = db.query(User).filter(User.id == id).update({"interval" : interval})
    try:
        db.commit()
    except:
        return False
    return user

# Define the style updating function
def update_style(id:int, style:str):
    user = db.query(User).filter(User.id == id).update({"style" : style})
    try:
        db.commit()
    except:
        return False
    return user

# Define the timezone updating function
def update_timezone(id:int, timezone:str):
    user = db.query(User).filter(User.id == id).update({"timezone" : timezone})
    try:
        db.commit()
    except:
        return False
    return user

# Define the default chain updating function
def update_chain(id:int, chain:str):
    user = db.query(User).filter(User.id == id).update({"chain" : chain})
    try:
        db.commit()
    except:
        return False
    return user

# Define the usert status updating function
def update_status(id:int, status:str):
    user = db.query(User).filter(User.id == id).update({"status" : status})
    try:
        db.commit()
    except:
        return False
    return user

def get_user_by_id(id:int):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        return False
    return user

def delete_user(id:int):
    try:
        db.query(User).filter(User.id == id).delete()
        db.commit()
        return True
    except:
        return False

def count_user():
    user = db.query(User).count()
    if not user:
        return False
    return user

def create_notification(chat_id:int, crypto_type:str, name:str, symbol:str, chain:str, platform:str, condition:str, value:float, notify_method: str):
    db_noitfy = Noitfy(chat_id=chat_id, email=None, phone=None, crypto_type=crypto_type, name=name, symbol=symbol, chain=chain, platform=platform, condition=condition, value=value, notify_method=notify_method)
    try:
        db.add(db_noitfy)
        db.commit()
        db.refresh(db_noitfy)
    except:
        return False
    return db_noitfy

def change_condition(notify_id:int, condition:str):
    notify = db.query(Noitfy).filter(Noitfy.notify_id == notify_id).update({"condition" : condition})
    try:
        db.commit()
    except:
        return False
    return notify

def change_value(notify_id:int, value:int):
    notify = db.query(Noitfy).filter(Noitfy.notify_id == notify_id).update({"value" : value})
    try:
        db.commit()
    except:
        return False
    return notify

def change_notify_method(notify_id:int, notify_method:str):
    notify = db.query(Noitfy).filter(Noitfy.notify_id == notify_id).update({"notify_method" : notify_method})
    try:
        db.commit()
    except:
        return False
    return notify

def get_notify_by_chat_id(chat_id:int):
    notify = db.query(Noitfy).filter(Noitfy.chat_id == chat_id).all()
    if not notify:
        return False
    return notify

def get_notify_by_id(notify_id:int):
    notify = db.query(Noitfy).filter(Noitfy.notify_id == notify_id).first()
    if not notify:
        return False
    return notify

def get_notify_all():
    notify = db.query(Noitfy).filter().all()
    if not notify:
        return False
    return notify

def delete_notification(notify_id:int):
    try:
        db.query(Noitfy).filter(Noitfy.notify_id == notify_id).delete()
        db.commit()
        return True
    except:
        return False