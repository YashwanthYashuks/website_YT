# YT_Boquets_ReturnGifts

Python Flask e-commerce starter for bouquets and return gifts.

## Run on Windows

1. Install Python 3.11+.
2. Open Command Prompt in this folder.
3. Create a virtual environment:
   `python -m venv website_env`
4. Activate:
   `website_env\Scripts\activate`
5. Install:
   `pip install -r requirements.txt`
6. Run:
   `python app.py`
7. Open:
   `http://127.0.0.1:5000`

## Admin

Open `/admin`

Default local credentials:
- Username: `admin`
- Password: `admin123`

Before public deployment, change the admin credentials and SECRET_KEY using environment variables.

## Payment

This starter uses Cash/UPI after order confirmation. Razorpay can be added later once the Razorpay account/API keys are available.

## WhatsApp

Business WhatsApp:
+91 8951104898

The number is stored in `app.py` as `WHATSAPP = "918951104898"`.
