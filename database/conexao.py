import oracledb #importa a biblioteca oracledb para realizar a conexão

def conectar(): #cria a função conectar
    return oracledb.connect( #retorna oracledb.connect
        user="arquibox",            # precisa por o usuario que foi criado no banco de dados.
        password="oracle",      # a senha do banco de dados deve ser a mesma, para ter a conexão.
        dsn="192.168.56.101/FREEPDB1"  # o dns tem que ser exatamente igual o como foi criado a conexao no banco de dados.
        
    )

#colocar o banco de dados na mesma pasta que for colocar o arquivo da conexão python.

def testar_conexao():
    try:
        conn = conectar()  # conecta ao banco
        cursor = conn.cursor()  # cria o cursor
        cursor.execute("SELECT 'Conexão bem-sucedida' FROM dual")  # executa o select no dual
        resultado = cursor.fetchone()  # pega o primeiro resultado
        print("Resultado da consulta:", resultado[0])
    except Exception as e:
        print("Erro ao conectar ou executar consulta:", e)
    finally:
        if 'conn' in locals():
            conn.close()  # fecha a conexão

# executa o teste
testar_conexao()
