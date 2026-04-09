from sqlalchemy.orm import Session
from models.models import Funcionario
from database.session import SessionLocal

def verificar_permissao(matricula_logada):
    db: Session = SessionLocal()
    funcionario = db.query(Funcionario).filter(Funcionario.matricula == matricula_logada).first()
    db.close()
    
    return funcionario.permissao if funcionario else None
