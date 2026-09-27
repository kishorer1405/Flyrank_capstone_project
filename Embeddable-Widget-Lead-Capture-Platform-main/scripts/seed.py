import sys
sys.path.insert(0, ".")
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models import User, Widget
from app.core.security import hash_password

with SessionLocal() as db:
    email = "demo@flyrank.local"
    user = db.scalar(select(User).where(User.email == email))
    if not user:
        user = User(email=email, password_hash=hash_password("Demo@12345"), company_name="Northstar Demo")
        db.add(user)
        db.flush()
    widget = db.scalar(select(Widget).where(Widget.tenant_id == user.id))
    if not widget:
        widget = Widget(
            tenant_id=user.id,
            title="Request a demo",
            description="Tell us how we can help.",
            widget_type="signup",
            fields=[
                {"name":"name","label":"Full name","type":"text","required":True,"placeholder":"Your name"},
                {"name":"email","label":"Work email","type":"email","required":True,"placeholder":"you@company.com"},
                {"name":"phone","label":"Phone","type":"tel","required":False,"placeholder":"+91 98765 43210"},
            ],
            button_text="Request demo",
            display_options={"theme":"clean"},
            is_active=True,
            version=1,
        )
        db.add(widget)
    db.commit()
    db.refresh(widget)
    print(f"Demo email: {email}")
    print("Demo password: Demo@12345")
    print(f"Widget ID: {widget.id}")
    print(f'Embed snippet: <script src="http://localhost:8000/widget.v1.js?id={widget.id}"></script>')
