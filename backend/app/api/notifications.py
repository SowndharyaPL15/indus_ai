from fastapi import APIRouter

router = APIRouter()

@router.get('/')
def read_notifications():
    return {'message': 'notifications endpoint'}

