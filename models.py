from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///banco_local.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class BookGerado(Base):
    __tablename__ = "logs_databook"
    id = Column(Integer, primary_key=True, index=True)
    nome_usuario = Column(String(50), nullable=False)
    registro = Column(String(200), nullable=True)
    pf = Column(String(200), nullable=True)
    codigo = Column(String(100), nullable=True)
    caminho_pdf = Column(Text, nullable=False)
    status = Column(String(20), nullable=False)
    log_detalhado = Column(Text, nullable=True)
    data_geracao = Column(DateTime, default=datetime.now)

class RascunhoModel(Base):
    __tablename__ = "rascunhos_databook"
    id = Column(Integer, primary_key=True, index=True)
    nome_usuario = Column(String(50), unique=True, nullable=False)
    registro = Column(String(200), nullable=True)
    pf = Column(String(200), nullable=True)
    codigo = Column(String(100), nullable=True)
    arquivos_json = Column(Text, nullable=True)
    ultima_atualizacao = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# Cria as tabelas automaticamente
Base.metadata.create_all(bind=engine)