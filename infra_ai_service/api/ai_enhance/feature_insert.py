#!/usr/bin/python3

from fastapi import APIRouter, File, UploadFile


router = APIRouter()


@router.post("/spec-repair/")
async def feature_insert(err_spec_file: UploadFile = File(...),
                              err_log_file: UploadFile = File(...)):
    try:
        pass
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }
