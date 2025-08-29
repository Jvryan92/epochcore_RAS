"""
PROTECTED FILE - EPOCHCORE RAS STRIPE WEBHOOK HANDLER
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved
"""

import logging
import os

from fastapi import FastAPI, HTTPException, Request

from .stripe_integration import EpochCoreStripeManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('epochcore_webhook')

app = FastAPI()
stripe_manager = EpochCoreStripeManager()


@app.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    try:
        # Get the raw payload and signature header
        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')

        if not sig_header:
            raise HTTPException(status_code=400, detail="No signature header")

        # Process the webhook
        result = await stripe_manager.handle_webhook(payload, sig_header)

        return {"status": "success", "result": result}

    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
