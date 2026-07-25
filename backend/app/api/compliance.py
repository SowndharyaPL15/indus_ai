from fastapi import APIRouter

router = APIRouter()

@router.get('/')
def read_compliance():
    return {'message': 'compliance endpoint'}

