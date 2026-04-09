import pyrebase

firebase_config = {
    "apiKey": "AIzaSyDMeEfyh5L3pOuFmuHad7h10YEjTwrcgmk",
    "authDomain": "arquiboxfirebase.firebaseapp.com",
    "projectId": "arquiboxfirebase",
    "storageBucket": "arquiboxfirebase.appspot.com",
    "messagingSenderId": "245454913618",
    "appId": "1:245454913618:web:ce60848f8a4113d6651f8b",
    "measurementId": "G-VBJ40M33DP",
    "databaseURL": ""  
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

'''
email = "usuario@example.com"
senha = "senhaSegura123"

try:
    usuario = auth.sign_in_with_email_and_password(email, senha)
    print("Usuário autenticado com sucesso!")
    print("Token de ID:", usuario['idToken'])
except Exception as e:
    print("Erro ao autenticar:", e)
'''