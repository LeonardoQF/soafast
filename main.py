from fastapi import FastAPI, HTTPException
import httpx
import re

app = FastAPI()

cep_cache = {}

def validar_cep(cep: str) -> bool:
    return re.fullmatch(r"\d{5}-?\d{3}", cep) is not None

async def consultar_cep_externo(cep: str) -> dict:
    url = f"https://viacep.com.br/ws/{cep}/json/"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=404, detail="CEP não encontrado")

@app.get("/cep/{cep}")
async def buscar_cep(cep: str):
    cep = cep.replace("-", "")
    
    if not validar_cep(cep):
        raise HTTPException(status_code=400, detail="Formato de CEP inválido")
    
    if cep in cep_cache:
        return {"data": cep_cache[cep], "cache": True}
    
    dados_cep = await consultar_cep_externo(cep)
    cep_cache[cep] = dados_cep

    if not _is_there_a_cache_duplicate(cep):
        _save_cache(cep, dados_cep)
    
    return {"data": dados_cep, "cache": False}

@app.get("/cache/{cep}")
async def consultar_cache(cep: str):
    cep = cep.replace("-", "")

    if cep in cep_cache:
        return {"data": cep_cache[cep]}
    else:
        raise HTTPException(status_code=404, detail="CEP não encontrado no cache")

@app.get("/cache")
async def consultar_todo_cache():
    return {"data": cep_cache}


#parte de escrita em arquivo
    
def _load_cache() -> {} :
    try:
        with open("cache_db.txt", "r") as file:
            return {Item.parse_raw(line) for line in file}
    except FileNotFoundError:
        return {}


def _save_cache(cep, cache : {}):
    with open("cache_db.txt", "a") as file:
        #for entry in cache:
        file.write(f"{cep} : {cache}\n")

def _is_there_a_cache_duplicate(cep) :
    with open("cache_db.txt", "r") as file:
        for entry in file :
            tempcep = slice(8)
            if tempcep == cep :
                return True
    return False
