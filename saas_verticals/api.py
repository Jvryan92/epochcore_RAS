"""
FastAPI-based API interface for EpochCore RAS SaaS verticals
"""

import json
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.security import HTTPBearer

from .audit_trail.service import AuditTrail
from .vertical_manager import VerticalManager

app = FastAPI(
    title="EpochCore RAS SaaS",
    description="Enterprise-grade security services",
    version="1.0.0"
)

security = HTTPBearer()
vertical_manager = VerticalManager()

# Dependency for auth


async def get_org_id(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    # In production, validate JWT and extract org_id
    return "org_" + authorization.split()[1][:6]

# AuditTrail Routes


@app.post("/api/v1/atass/events")
async def create_audit_event(
    event_type: str,
    data: Dict,
    org_id: str = Depends(get_org_id)
):
    """Create a new audit trail event"""
    audit = AuditTrail(org_id)
    event = audit.log_event(event_type, data)
    return {"status": "success", "event": event}


@app.get("/api/v1/atass/events")
async def get_audit_events(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    org_id: str = Depends(get_org_id)
):
    """Get audit trail events in time range"""
    audit = AuditTrail(org_id)
    events = audit.export_logs(start_time, end_time)
    return {"status": "success", "events": events}


@app.post("/api/v1/atass/verify")
async def verify_audit_chain(
    org_id: str = Depends(get_org_id)
):
    """Verify audit trail integrity"""
    audit = AuditTrail(org_id)
    is_valid = audit.verify_chain()
    return {"status": "success", "valid": is_valid}

# Vertical Management Routes


@app.post("/api/v1/verticals/{vertical_name}")
async def launch_vertical(
    vertical_name: str,
    tier: str,
    org_id: str = Depends(get_org_id)
):
    """Launch a new vertical instance"""
    try:
        instance_id = vertical_manager.launch_vertical(vertical_name, tier)
        return {
            "status": "success",
            "instance_id": instance_id,
            "message": f"Launched {vertical_name} vertical with tier {tier}"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/verticals/{instance_id}")
async def get_vertical_status(
    instance_id: str,
    org_id: str = Depends(get_org_id)
):
    """Get status of a vertical instance"""
    try:
        status = vertical_manager.get_vertical_status(instance_id)
        return {"status": "success", "vertical_status": status}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/v1/verticals/{vertical_name}/pricing")
async def get_vertical_pricing(vertical_name: str):
    """Get pricing information for a vertical"""
    try:
        pricing = vertical_manager.get_pricing(vertical_name)
        return {"status": "success", "pricing": pricing}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
