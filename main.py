from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import asyncio
import logging
from telegram_client import TelegramClientManager
from bot_handler import BotHandler
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Telegram Bot API Middleware", version="1.0.0")

# Global variables
telegram_client = None
bot_handler = None

@app.on_event("startup")
async def startup_event():
    """Initialize Telegram client on startup"""
    global telegram_client, bot_handler
    try:
        config = Config()
        telegram_client = TelegramClientManager(config.SESSION_STRING, config.API_ID, config.API_HASH)
        await telegram_client.start()
        bot_handler = BotHandler(telegram_client, config.BOT_USERNAME)
        logger.info("Telegram client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Telegram client: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    global telegram_client
    if telegram_client:
        await telegram_client.stop()
        logger.info("Telegram client stopped")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "active", "message": "Telegram Bot API Middleware is running"}

@app.get("/number_info")
async def number_info(number: str = Query(..., description="Phone number to search")):
    """Get information about a phone number"""
    try:
        if not number or len(number) < 10:
            raise HTTPException(status_code=400, detail="Invalid phone number format")
        
        if not bot_handler:
            raise HTTPException(status_code=503, detail="Bot handler not initialized")
        result = await bot_handler.get_number_info(number)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in number_info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/fam")
async def fam_info(fam_id: str = Query(..., description="FamPay ID to search")):
    """Get FamPay information"""
    try:
        if not fam_id:
            raise HTTPException(status_code=400, detail="FamPay ID is required")
        
        if not bot_handler:
            raise HTTPException(status_code=503, detail="Bot handler not initialized")
        result = await bot_handler.get_fampay_info(fam_id)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in fam_info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/aadhar")
async def aadhar_info(aadhar_id: str = Query(..., description="Aadhar number to search")):
    """Get Aadhar information"""
    try:
        if not aadhar_id or len(aadhar_id) != 12:
            raise HTTPException(status_code=400, detail="Invalid Aadhar number format (12 digits required)")
        
        if not bot_handler:
            raise HTTPException(status_code=503, detail="Bot handler not initialized")
        result = await bot_handler.get_aadhar_info(aadhar_id)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in aadhar_info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vehicle")
async def vehicle_info(vehicle_id: str = Query(..., description="Vehicle registration number")):
    """Get vehicle information"""
    try:
        if not vehicle_id:
            raise HTTPException(status_code=400, detail="Vehicle ID is required")
        
        if not bot_handler:
            raise HTTPException(status_code=503, detail="Bot handler not initialized")
        result = await bot_handler.get_vehicle_info(vehicle_id)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in vehicle_info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ration")
async def ration_info(ration_id: str = Query(..., description="Ration card number")):
    """Get ration card information"""
    try:
        if not ration_id:
            raise HTTPException(status_code=400, detail="Ration card ID is required")
        
        if not bot_handler:
            raise HTTPException(status_code=503, detail="Bot handler not initialized")
        result = await bot_handler.get_ration_info(ration_id)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in ration_info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/breach")
async def breach_info(email: str = Query(..., description="Email to check for breaches")):
    """Get breach information for email"""
    try:
        if not email or "@" not in email:
            raise HTTPException(status_code=400, detail="Valid email address is required")
        
        if not bot_handler:
            raise HTTPException(status_code=503, detail="Bot handler not initialized")
        result = await bot_handler.get_breach_info(email)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in breach_info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/challan")
async def challan_info(vehicle_number: str = Query(..., description="Vehicle number for challan check")):
    """Get challan information"""
    try:
        if not vehicle_number:
            raise HTTPException(status_code=400, detail="Vehicle number is required")
        
        if not bot_handler:
            raise HTTPException(status_code=503, detail="Bot handler not initialized")
        result = await bot_handler.get_challan_info(vehicle_number)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in challan_info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/upi")
async def upi_info(upi_id: str = Query(..., description="UPI ID to search")):
    """Get UPI information"""
    try:
        if not upi_id or "@" not in upi_id:
            raise HTTPException(status_code=400, detail="Valid UPI ID is required")
        
        if not bot_handler:
            raise HTTPException(status_code=503, detail="Bot handler not initialized")
        result = await bot_handler.get_upi_info(upi_id)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in upi_info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
