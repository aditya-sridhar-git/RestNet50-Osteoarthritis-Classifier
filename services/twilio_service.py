import os
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")


def send_otp_sms(phone_number: str, otp: str) -> dict:
    """
    Send OTP via Twilio SMS.
    
    Args:
        phone_number: Phone number with country code (e.g., +917849001200)
        otp: 6-digit OTP code
    
    Returns:
        dict with 'success' (bool), 'message' (str), and optionally 'otp' for dev mode
    """
    # If Twilio credentials not configured, return OTP for development mode
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_PHONE_NUMBER:
        print("⚠️ Twilio credentials not configured. Running in development mode.")
        return {
            "success": True,
            "message": "Development mode: OTP not sent via SMS",
            "otp": otp  # Return OTP for development
        }
    
    # Ensure phone number has country code
    if not phone_number.startswith("+"):
        # Assume Indian number if no country code
        if phone_number.startswith("91"):
            phone_number = "+" + phone_number
        else:
            phone_number = "+91" + phone_number
    
    # Prepare SMS message
    message_body = f"Your OsteoAI OTP is {otp}. Valid for 5 minutes. Do not share with anyone."
    
    try:
        # Initialize Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        print(f"📤 Sending OTP to {phone_number} via Twilio...")
        
        # Send SMS
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        
        print(f"✅ OTP sent successfully to {phone_number}")
        print(f"📥 Twilio Message SID: {message.sid}")
        
        return {
            "success": True,
            "message": "OTP sent successfully to your phone"
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Twilio error: {error_msg}")
        
        # Check for common errors
        if "not a valid phone number" in error_msg.lower():
            print("❌ Invalid phone number format")
        elif "unverified" in error_msg.lower():
            print("❌ Phone number not verified in Twilio trial account")
            print("💡 Verify this number at: https://console.twilio.com/us1/develop/phone-numbers/manage/verified")
        
        # Fallback to development mode on error
        return {
            "success": True,
            "message": "SMS service temporarily unavailable",
            "otp": otp  # Return OTP as fallback
        }
