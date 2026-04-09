from sqlalchemy.orm import Session
from models.models import Localizacao, Caixa

def localizacoes_vazia(db: Session):
    try:
        localizacoes_sem_caixas = db.query(Localizacao)\
            .outerjoin(Caixa, Localizacao.id == Caixa.localizacao_id)\
            .filter(Caixa.id.is_(None))\
            .order_by(Localizacao.sala, Localizacao.prateleira, Localizacao.coluna)\
            .all()
        
        return localizacoes_sem_caixas
    except Exception as e:
        print(f"Erro ao obter localizações sem caixas: {e}")
        return []

def localizacoes_usadas(db: Session):
    try:
        
        localizacoes_com_caixas = db.query(Localizacao)\
            .join(Caixa, Localizacao.id == Caixa.localizacao_id)\
            .distinct()\
            .all()
        
        return localizacoes_com_caixas
    except Exception as e:
        print(f"Erro ao obter localizações com caixas: {e}")
        return []
