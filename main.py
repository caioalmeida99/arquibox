from interface.tela_menu import TelaMenu
from interface.tela_login import TelaLogin
from models.models import Base

if __name__ == "__main__":
    #Base.metadata.create_all(bind=True)
    app = TelaLogin()
    app.mainloop()

    