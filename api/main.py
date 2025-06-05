from fastapi import FastAPI
from api.routes import specs

app = FastAPI(
    title='API Ficha Técnica',
    description='API para consultar fichas técnicas de veículos',
    version='1.0.0'
)

app.include_router(specs.router, prefix='/api/specs', tags=['Fichas Técnicas'])