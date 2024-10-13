from sqlalchemy import create_engine, text

engine = create_engine('mysql+pymysql://pma:NtxFL6ms7pn3zRK2G9feDy@localhost/orchidsense_user_db')

try:
    conn = engine.connect()
    results = conn.execute(text("SELECT 1"))
    print(results.fetchone())
    conn.close()
except Exception as e:
    print("Erro ao conectar ao banco de dados:", e)


