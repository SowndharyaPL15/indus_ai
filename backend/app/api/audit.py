from fastapi import APIRouter

router = APIRouter()

@router.get('/')
def read_audit():
    return {'message': 'audit endpoint'}

