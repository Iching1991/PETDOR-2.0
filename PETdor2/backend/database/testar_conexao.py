from .supabase_client import supabase

def testar_conexao():
    try:
        # Faz uma simples consulta no Supabase
        response = supabase.table("teste").select("*").limit(1).execute()
        print("Conexão com Supabase OK!")
        return True
    except Exception as e:
        print("Erro ao conectar ao Supabase:", e)
        return False
