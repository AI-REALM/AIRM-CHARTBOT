from sqlalchemy.orm import Session, sessionmaker
from .models import User, Base, Notify
from .database import SessionLocal, engine
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

Base.metadata.create_all(bind=engine)
db = SessionLocal()

def create_user(chat_id:int):
    db_user = User(id=chat_id, premium=False, premium_date=None, indicators=None, interval="1h", style="candle", timezone="America/New_York", chain="ethereum", status="dx")
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except:
        return False
    return db_user

# Define the premium updating function
def update_premium(id:int, end:str):
    user = db.query(User).filter(User.id == id).update({"indicators" : end})
    try:
        db.commit()
    except:
        return False
    return user

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

def update_invoice(id:int, invoice:int):
    user = db.query(User).filter(User.id == id).update({"invoice" : invoice})
    try:
        db.commit()
    except:
        return False
    return user

def update_premium(id:int, price: str):
    months = {
        '1': 1,
        '2.5': 3,
        '4.5': 6
    }
    now_date = datetime.now().date()
    new_date = now_date + relativedelta(months=+months[price])
    user = db.query(User).filter(User.id == id).update({"premium" : True, 'invoice':None, "premium_date":new_date})
    if not user:
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

def count_individual_user():
    user_count = db.query(User).filter(User.id > 0).count()
    return user_count if user_count >= 0 else False

# Define count function for groups
def count_groups():
    user_group = db.query(User).filter(User.id < 0).count()
    return user_group if user_group >= 0 else False

def get_users_invoice_enable():
    user = db.query(User).filter(User.invoice != None).all()
    if not user:
        return False
    return user

def create_notification(chat_id:int, crypto_type:str, name:str, symbol:str, chain:str, platform:str, condition:str, con_type:str, value:float, notify_method: str):
    db_noitfy = Notify(chat_id=chat_id, email=None, phone=None, crypto_type=crypto_type, name=name, symbol=symbol, chain=chain, platform=platform, condition=condition, con_type=con_type, value=value, notify_method=notify_method)
    try:
        db.add(db_noitfy)
        db.commit()
        db.refresh(db_noitfy)
    except:
        return False
    return db_noitfy

def change_condition(notify_id:int, condition:str, con_type:str):
    notify = db.query(Notify).filter(Notify.notify_id == notify_id).update({"condition" : condition, "con_type":con_type})
    try:
        db.commit()
    except:
        return False
    return notify

def change_value(notify_id:int, value:float):
    notify = db.query(Notify).filter(Notify.notify_id == notify_id).update({"value" : value})
    try:
        db.commit()
    except:
        return False
    return notify

def change_notify_method(notify_id:int, notify_method:str):
    notify = db.query(Notify).filter(Notify.notify_id == notify_id).update({"notify_method" : notify_method})
    try:
        db.commit()
    except:
        return False
    return notify

def get_notify_by_chat_id(chat_id:int):
    notify = db.query(Notify).filter(Notify.chat_id == chat_id).all()
    if not notify:
        return False
    return notify

def get_notify_by_id(notify_id:int):
    notify = db.query(Notify).filter(Notify.notify_id == notify_id).first()
    if not notify:
        return False
    return notify

def get_notify_all():
    notify = db.query(Notify).filter().all()
    if not notify:
        return False
    return notify

def delete_notification(notify_id:int):
    try:
        db.query(Notify).filter(Notify.notify_id == notify_id).delete()
        db.commit()
        return True
    except:
        return False