from dataclasses import dataclass
from typing import Optional
from database.supabase_client import supabase

@dataclass
class Usuario:
    id: int
    nome: str
    email: str
    senha_hash: str
    tipo_usuario: str
    pais: str
    email_confirmado: bool
    ativo: bool
    criado_em: str

@dataclass
class Pet:
    id: int
    nome: str
    especie: str
    tutor_id: int
    idade: Optional[int] = None
    peso: Optional[float] = None
    criado_em: Optional[str] = None

# Usuários
def buscar_usuario_por_email(email: str) -> Optional[Usuario]:
    resp = supabase.table("usuarios").select("*").eq("email", email).execute()
    if resp.error or not resp.data:
        return None
    row = resp.data[0]
    return Usuario(**{
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "senha_hash": row["senha_hash"],
        "tipo_usuario": row["tipo_usuario"],
        "pais": row["pais"],
        "email_confirmado": row["email_confirmado"],
        "ativo": row["ativo"],
        "criado_em": row["data_cadastro"]
    })

def buscar_usuario_por_id(user_id: int) -> Optional[Usuario]:
    resp = supabase.table("usuarios").select("*").eq("id", user_id).execute()
    if resp.error or not resp.data:
        return None
    row = resp.data[0]
    return Usuario(**{
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "senha_hash": row["senha_hash"],
        "tipo_usuario": row["tipo_usuario"],
        "pais": row["pais"],
        "email_confirmado": row["email_confirmado"],
        "ativo": row["ativo"],
        "criado_em": row["data_cadastro"]
    })

# Pets
def buscar_pet_por_id(pet_id: int) -> Optional[Pet]:
    resp = supabase.table("pets").select("*").eq("id", pet_id).execute()
    if resp.error or not resp.data:
        return None
    row = resp.data[0]
    return Pet(**{
        "id": row["id"],
        "nome": row["nome"],
        "especie": row["especie"],
        "tutor_id": row["id_usuario"],
        "idade": row.get("idade"),
        "peso": row.get("peso"),
        "criado_em": row.get("data_cadastro")
    })
