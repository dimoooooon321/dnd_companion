from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.database import engine
from app.main import app

client = TestClient(app)
email = 'character-flow@example.com'
password = 'strongpass123'

register_response = client.post('/auth/register', json={'email': email, 'password': password, 'role': 'player'})
print('register', register_response.status_code, register_response.json())

login_response = client.post('/auth/login', data={'username': email, 'password': password})
print('login', login_response.status_code, login_response.json())

token = login_response.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}
create_response = client.post('/characters/', json={'name': 'Torgrim', 'race': 'Human', 'class_name': 'Barbarian', 'max_hp': 20}, headers=headers)
print('create_character', create_response.status_code, create_response.json())

with engine.connect() as connection:
    users = connection.execute(text('SELECT id, email FROM users WHERE email = :email'), {'email': email}).fetchall()
    characters = connection.execute(text('SELECT id, owner_id, name FROM characters WHERE name = :name'), {'name': 'Torgrim'}).fetchall()
    memberships = connection.execute(text('SELECT id, campaign_id, character_id FROM campaign_memberships')).fetchall()
    print('db_users', users)
    print('db_characters', characters)
    print('db_memberships', memberships)
