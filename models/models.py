from typing import List
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, PrimaryKeyConstraint, VARCHAR, Numeric
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Departamento(Base):
    __tablename__ = 'departamento'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='departamento_pk'),
        {'schema': 'ARQUIBOX'}
    )

    id: Mapped[int] = mapped_column(NUMBER(10, 0, False), autoincrement=True)
    nome: Mapped[str] = mapped_column(VARCHAR(200), nullable=False)

    '''funcionarios: Mapped[List['Funcionario']] = relationship('Funcionario', back_populates='departamento')'''

'''class Pessoa(Base):
    __tablename__ = 'pessoa'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pessoa_pk'),
        {'schema': 'ARQUIBOX'}
    )

    id: Mapped[int] = mapped_column(NUMBER(10, 0, False), autoincrement=True)
    nome: Mapped[str] = mapped_column(VARCHAR(200), nullable=False)

    funcionarios: Mapped[List['Funcionario']] = relationship('Funcionario', back_populates='pessoa')'''

class Funcionario(Base):
    __tablename__ = 'funcionario'
    __table_args__ = (
        PrimaryKeyConstraint('matricula', name='funcionario_pk'),
        {'schema': 'ARQUIBOX'}
    )

    matricula: Mapped[int] = mapped_column(NUMBER(10, 0), autoincrement=True)
    nome: Mapped[str] = mapped_column(VARCHAR(150), nullable=False)
    email: Mapped[str] = mapped_column(VARCHAR(250), nullable=False, unique=True)
    cargo: Mapped[str] = mapped_column(VARCHAR(200), nullable=False)
    departamento_id: Mapped[int] = mapped_column(ForeignKey('ARQUIBOX.departamento.id'), nullable=False)
    permissao: Mapped[int] = mapped_column(NUMBER(3, 0))

    #pessoa_id: Mapped[int] = mapped_column(ForeignKey('ARQUIBOX.pessoa.id'), nullable=False)
    '''pessoa: Mapped['Pessoa'] = relationship('Pessoa', back_populates='funcionarios')
    departamento: Mapped['Departamento'] = relationship('Departamento', back_populates='funcionarios')
    acessos: Mapped[List['AcessoCaixa']] = relationship('AcessoCaixa', back_populates='funcionario')'''

class Documento(Base):
    __tablename__ = 'documento'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='documento_pk'),
        {'schema': 'ARQUIBOX'}
    )

    id: Mapped[int] = mapped_column(Numeric(precision=200, scale=0), autoincrement=True)
    tp_doc: Mapped[str] = mapped_column(VARCHAR(200), nullable=False)
    temp_arq: Mapped[int] = mapped_column(NUMBER(10, 0, False), nullable=False)

    '''caixas: Mapped[List['Caixa']] = relationship('Caixa', back_populates='documento')'''

class Localizacao(Base):
    __tablename__ = 'localizacao'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='localizacao_pk'),
        {'schema': 'ARQUIBOX'}
    )

    id: Mapped[int] = mapped_column(Numeric(precision=200, scale=0), autoincrement=True)
    sala: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)
    prateleira: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)
    coluna: Mapped[str] = mapped_column(VARCHAR(10), nullable=False)

    '''caixas: Mapped[List['Caixa']] = relationship('Caixa', back_populates='localizacao')'''

class Status(Base):
    __tablename__ = 'status'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='status_pk'),
        {'schema': 'ARQUIBOX'}
    )

    id: Mapped[int] = mapped_column(NUMBER(10, 0, False), autoincrement=True)
    tipo: Mapped[str] = mapped_column(VARCHAR(200), nullable=False)

    '''caixas: Mapped[List['Caixa']] = relationship('Caixa', back_populates='status')'''

class Caixa(Base):
    __tablename__ = 'caixa'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='caixa_pk'),
        {'schema': 'ARQUIBOX'}
    )

    id: Mapped[int] = mapped_column(NUMBER(10, 0, False), autoincrement=True)
    dt_previsao: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    dt_arquivamento: Mapped[datetime] = mapped_column(DateTime, name="DT_ARQUIVAMENTO", nullable=False)
    documento_id: Mapped[int] = mapped_column(ForeignKey('ARQUIBOX.documento.id'), nullable=False)
    status_id: Mapped[int] = mapped_column(ForeignKey('ARQUIBOX.status.id'), nullable=False)
    localizacao_id: Mapped[int] = mapped_column(ForeignKey('ARQUIBOX.localizacao.id'), nullable=False)
    periodo_inc: Mapped[datetime] = mapped_column(DateTime, name="PERIODO_INC", nullable=True)
    periodo_fim: Mapped[datetime] = mapped_column(DateTime, name="PERIODO_FIM", nullable=True)
    dt_exclusao: Mapped[datetime] = mapped_column(DateTime, name="DT_EXCLUSAO", nullable=True)


    '''documento: Mapped['Documento'] = relationship('Documento', back_populates='caixas')
    status: Mapped['Status'] = relationship('Status', back_populates='caixas')
    localizacao: Mapped['Localizacao'] = relationship('Localizacao', back_populates='caixas')
    acessos: Mapped[List['AcessoCaixa']] = relationship('AcessoCaixa', back_populates='caixa')'''

class AcessoCaixa(Base):
    __tablename__ = 'acesso_caixa'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='acesso_caixa_pk'),
        {'schema': 'ARQUIBOX'}
    )

    id: Mapped[int] = mapped_column(NUMBER(10, 0, False), autoincrement=True)
    dt_acesso: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    funcionario_matricula: Mapped[int] = mapped_column(ForeignKey('ARQUIBOX.funcionario.matricula'), nullable=False)
    caixa_id: Mapped[int] = mapped_column(ForeignKey('ARQUIBOX.caixa.id'), nullable=False)
    status: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)

    '''funcionario: Mapped['Funcionario'] = relationship('Funcionario', back_populates='acessos')
    caixa: Mapped['Caixa'] = relationship('Caixa', back_populates='acessos')'''
