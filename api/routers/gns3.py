from fastapi import APIRouter, HTTPException

from core.gns3_manager import GNS3Manager

router = APIRouter(prefix="/api/gns3", tags=["GNS3"])


@router.get("")
def gns3_status():
    return GNS3Manager().test_connection()


@router.get("/projects")
def projects():
    try:
        return GNS3Manager().get_projects()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.get("/projects/{project_id}/nodes")
def nodes(project_id: str):
    try:
        return GNS3Manager().get_project_nodes(project_id)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )
