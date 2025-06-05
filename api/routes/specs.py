from fastapi import APIRouter, Path, HTTPException
from typing import List
from bson import ObjectId
from db.mongo import get_database
from api.schemas.specs import VehicleSpec

router = APIRouter()

@router.get('/{automaker}', response_model=List[str])
async def listar_modelos_por_montadora(automaker: str = Path(..., description='Nome da montadora')):
    db = get_database()
    cursor = db.vehicle_specs.find({'automaker': automaker.lower()})

    modelos = set()
    for doc in cursor:
        modelos.add(doc['model'])

    if not modelos:
        raise HTTPException(status_code=404, detail="Montadora não encontrada")

    return list(modelos)

@router.get('/{automaker}/{model}', response_model=List[dict])
async def listar_versions_e_anos(
        automaker: str = Path(..., description='Nome da montadora'),
        model: str = Path(..., description='Nome do modelo')
):
    db = get_database()
    cursor = db.vehicle_specs.find({
        'automaker': automaker.lower(),
        'model': model.lower()
    })

    combinacoes = []

    for doc in cursor:
        combinacoes.append({
            'version': doc.get('version'),
            'year': doc.get('year')
        })

    if not combinacoes:
        raise HTTPException(status_code=404, detail='Modelo não encontrado para essa montadora')

    return combinacoes


@router.get("/{automaker}/{model}/{version}/{year}", response_model=VehicleSpec)
async def obter_ficha_tecnica_completa(
        automaker: str = Path(..., description="Montadora"),
        model: str = Path(..., description="Modelo"),
        version: str = Path(..., description="Versão"),
        year: str = Path(..., description="Ano")
):
    db = get_database()

    doc = db.vehicle_specs.find_one({
        "automaker": automaker.lower(),
        "model": model.lower(),
        "version": version,
        "year": year
    })

    if not doc:
        raise HTTPException(status_code=404, detail="Ficha técnica não encontrada")

    doc["id"] = str(doc["_id"])
    return doc