def get_paypal_token():
    import requests
    from django.conf import settings
    data = {
        'grant_type': 'client_credentials',
    }
    import json
    response = requests.post('https://api-m.paypal.com/v1/oauth2/token', data=data, auth=(settings.PAYPAL_ID, settings.PAYPAL_SECRET)).json()
    print(json.dumps(response))
    return response['access_token']

def get_paypal_link(invoice, price, token):
    import requests
    import uuid
    from django.conf import settings
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(get_paypal_token()),
        'PayPal-Request-Id': str(uuid.uuid4()),
    }
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "reference_id": invoice,
                "amount": {
                    "currency_code": "USD",
                    "value": "{}.00".format(price)
                }
            }
        ],
         "payment_source": {
              "paypal": {
                   "experience_context": {
                       "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
                       "brand_name": settings.SITE_NAME,
                       "locale": "en-US",
                        "landing_page": "LOGIN",
                        "shipping_preference": "SET_PROVIDED_ADDRESS",
                            "user_action": "PAY_NOW",
                            "return_url": "{}{}".format(settings.BASE_URL, '/payments/paypal/?token={}'.format(token)),
                            "cancel_url": "{}{}".format(settings.BASE_URL, '/payments/cancel/')
                        }
                    }
                }
            }
    import json
    response = requests.post('https://api-m.paypal.com/v2/checkout/orders', headers=headers, data=json.dumps(payload)).json()
    print(json.dumps(response))
    return response['id'], response['links'][1]['href']

def get_order_status(id):
    import requests, jsosn
    headers = {
        'Authorization': 'Bearer access_token{}'.format(get_paypal_token()),
    }
    response = requests.get('https://api-m.paypal.com/v2/checkout/orders/{}'.format(id), headers=headers).json()
    print(json.dumps(response))
    return response['status'] == 'APPROVED'
