import firebase_admin
from firebase_admin import credentials, auth

cred = credentials.Certificate('C:/handson/database/arquiboxfirebase.json')

firebase_admin.initialize_app(cred)


'''user = auth.create_user(
    email='usuario@example.com',
    password='senhaSegura123'
)
print('Usuário criado com UID:', user.uid)'''