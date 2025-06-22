from fastapi import APIRouter, Depends, HTTPException
from stem.security import get_current_user
from stem.models import UserModel
from parietal import hardware

# Central router for all parietal-related endpoints
router = APIRouter(
    prefix="/parietal",
    tags=["parietal"],
    dependencies=[Depends(get_current_user)]
)

# --- System Information ---

@router.get("/system-info")
async def system_info_api(user: UserModel = Depends(get_current_user)):
    """
    Returns comprehensive system and hardware information for the debug console.
    Requires authentication.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return hardware.get_comprehensive_system_info()

# --- Performance Benchmarking ---

@router.post("/benchmark")
async def benchmark_api(user: UserModel = Depends(get_current_user)):
    """
    Runs comprehensive benchmark tests for LLM and tool performance.
    Requires authentication.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return hardware.run_comprehensive_benchmark()

@router.post("/benchmark/llm")
async def llm_benchmark_api(user: UserModel = Depends(get_current_user)):
    """
    Runs LLM-specific benchmark tests.
    Requires authentication.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return hardware.run_llm_benchmark()

@router.post("/benchmark/tools")
async def tools_benchmark_api(user: UserModel = Depends(get_current_user)):
    """
    Runs tool-specific benchmark tests.
    Requires authentication.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return hardware.run_tool_benchmark() 