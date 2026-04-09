from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "oracle+oracledb://arquibox:oracle@192.168.56.101/?service_name=FREEPDB1"

engine = create_engine(
    DATABASE_URL,
    echo=True,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

#Capturar a matricula de quem está logado
matricula_logada = None