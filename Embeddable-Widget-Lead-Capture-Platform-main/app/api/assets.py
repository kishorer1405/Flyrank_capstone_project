from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import Response
from app.core.config import get_settings
router=APIRouter(tags=["widget-delivery"])
settings=get_settings()
SCRIPT=(Path(__file__).resolve().parents[2]/"widget"/"widget.v1.js").read_text(encoding="utf-8")
@router.get("/widget.v1.js")
def widget_script(): return Response(SCRIPT,media_type="application/javascript",headers={"Cache-Control":f"public, max-age={settings.widget_cache_seconds}, immutable","X-Widget-Version":"1"})
