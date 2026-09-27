from sqlalchemy import select
from app.db.session import get_db
from tests.conftest import TestingSession
from app.models import User,Widget,Submission,BackgroundJob
from app.core.security import hash_password,create_access_token

def seed_user(email="a@example.com"):
    db=TestingSession();u=User(email=email,password_hash=hash_password("Password123"),company_name="Tenant A");db.add(u);db.flush();w=Widget(tenant_id=u.id,title="Lead",description="Demo",widget_type="signup",fields=[{"name":"name","label":"Name","type":"text","required":True},{"name":"email","label":"Email","type":"email","required":True}],button_text="Send",display_options={},is_active=True,version=1);db.add(w);db.commit();db.refresh(u);db.refresh(w);db.close();return u,w

def auth(u):return {"Authorization":"Bearer "+create_access_token(str(u.id))}

def test_auth_and_widget_crud(client):
    r=client.post('/api/v1/auth/register',json={"email":"new@example.com","password":"Password123","company_name":"New Co"});assert r.status_code==201
    r=client.post('/api/v1/auth/login',data={"username":"new@example.com","password":"Password123"});assert r.status_code==200;token=r.json()['access_token']
    h={"Authorization":"Bearer "+token};r=client.post('/api/v1/widgets',headers=h,json={"title":"Signup","description":"Hi","widget_type":"signup","fields":[{"name":"email","label":"Email","type":"email","required":True}],"button_text":"Join","display_options":{},"is_active":True});assert r.status_code==201;wid=r.json()['id'];assert '<script' in r.json()['embed_snippet']
    assert client.get('/api/v1/widgets/'+wid,headers=h).status_code==200
    assert client.patch('/api/v1/widgets/'+wid,headers=h,json={"title":"Updated"}).status_code==200
    assert client.delete('/api/v1/widgets/'+wid,headers=h).status_code==204

def test_tenant_isolation(client):
    a,wa=seed_user('a@example.com');b,wb=seed_user('b@example.com');r=client.get(f'/api/v1/widgets/{wa.id}',headers=auth(b));assert r.status_code==404

def test_public_submission_honeypot_idempotency_and_storage(client):
    u,w=seed_user();p={"widget_id":str(w.id),"data":{"name":"Krish","email":"krish@example.com"},"honeypot":""};h={"Origin":"http://localhost:5500","Idempotency-Key":"same-key"}
    r=client.post('/api/v1/public/submissions',headers=h,json=p);assert r.status_code==201
    r2=client.post('/api/v1/public/submissions',headers=h,json=p);assert r2.status_code==201 and r2.json()['duplicate'] is True
    db=TestingSession();assert db.scalar(select(Submission).where(Submission.widget_id==w.id)) is not None;assert db.scalar(select(BackgroundJob)) is not None;db.close()
    spam=client.post('/api/v1/public/submissions',json={**p,"honeypot":"bot"});assert spam.status_code==400

def test_invalid_and_unknown_fields(client):
    _,w=seed_user();p={"widget_id":str(w.id),"data":{"name":"","email":"bad"},"honeypot":""};r=client.post('/api/v1/public/submissions',json=p);assert r.status_code==422
    p['data']={"name":"Good","email":"good@example.com","unknown":"x"};assert client.post('/api/v1/public/submissions',json=p).status_code==422

def test_rate_limit_returns_429(client):
    _,w=seed_user();p={"widget_id":str(w.id),"data":{"name":"Good","email":"good@example.com"},"honeypot":""}
    statuses=[client.post('/api/v1/public/submissions',json={**p,"data":{**p['data'],"name":str(i)}}).status_code for i in range(6)];assert 429 in statuses

def test_cors_preflight(client):
    r=client.options('/api/v1/public/submissions',headers={"Origin":"http://localhost:5500","Access-Control-Request-Method":"POST","Access-Control-Request-Headers":"content-type,idempotency-key"});assert r.status_code==204;assert r.headers.get('access-control-allow-origin')=='http://localhost:5500'

def test_dashboard_is_tenant_scoped(client):
    a,wa=seed_user();b,wb=seed_user('b@example.com');p={"widget_id":str(wa.id),"data":{"name":"A","email":"a@example.com"}};client.post('/api/v1/public/submissions',json=p);r=client.get('/api/v1/dashboard/submissions',headers=auth(b));assert r.status_code==200 and r.json()['total']==0
