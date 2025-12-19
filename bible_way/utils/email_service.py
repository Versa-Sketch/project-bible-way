import requests
import os
import logging

logger = logging.getLogger(__name__)


class ZeptoMailService:
    """
    Service for sending emails via ZeptoMail API
    """
    
    def __init__(self):
        self.api_url = "https://api.zeptomail.in/v1.1/email"
        self.api_token = os.getenv('ZEPTOMAIL_API_TOKEN', '')
        self.from_email = os.getenv('ZEPTOMAIL_FROM_EMAIL', 'noreply@linchpinsoftsolution.com')
    
    def send_verification_email(self, user_email: str, user_name: str, otp: str) -> tuple[bool, str]:
        """
        Send verification email with OTP code
        
        Args:
            user_email: Recipient email address
            user_name: User's name/username
            otp: 4-digit OTP code
            
        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.api_token:
            logger.error("ZEPTOMAIL_API_TOKEN not configured")
            return False, "Email service not configured"
        
        try:
            payload = {
                "from": {
                    "address": self.from_email
                },
                "to": [{
                    "email_address": {
                        "address": user_email,
                        "name": user_name
                    }
                }],
                "subject": "Verify Your Email - Bible Way",
                "htmlbody": f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #333;">Email Verification</h2>
                    <p>Hello {user_name},</p>
                    <p>Thank you for signing up with Bible Way! Please verify your email address by entering the following OTP code:</p>
                    <div style="background-color: #f4f4f4; padding: 20px; text-align: center; margin: 20px 0;">
                        <h1 style="color: #007bff; font-size: 32px; margin: 0; letter-spacing: 5px;">{otp}</h1>
                    </div>
                    <p>This code will expire in 15 minutes.</p>
                    <p>If you didn't create an account with Bible Way, please ignore this email.</p>
                    <p>Best regards,<br>The Bible Way Team</p>
                </div>
                """
            }
            
            headers = {
                'accept': 'application/json',
                'content-type': 'application/json',
                'authorization': f'Zoho-enczapikey {self.api_token}'
            }
            
            response = requests.post(self.api_url, json=payload, headers=headers)
            
            # ZeptoMail API returns 201 (Created) for successful email requests
            # Also check response body for success indicators
            if response.status_code in [200, 201]:
                try:
                    response_data = response.json()
                    # Check if response indicates success
                    if response_data.get('message') == 'OK' or response_data.get('object') == 'email':
                        logger.info(f"Verification email sent successfully to {user_email}")
                        return True, "Email sent successfully"
                except:
                    # If JSON parsing fails but status is 200/201, consider it success
                    logger.info(f"Verification email sent successfully to {user_email}")
                    return True, "Email sent successfully"
            
            # Log error for debugging
            logger.error(f"Failed to send email: {response.status_code} - {response.text}")
            return False, f"Failed to send email: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Error sending verification email: {str(e)}")
            return False, f"Error sending email: {str(e)}"

