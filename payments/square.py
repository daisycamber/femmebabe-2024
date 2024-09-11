def get_payment_link(price, product, description, email, token, subscription=False):
    from django.conf import settings
    import uuid, urllib
    headers = {
        'Square-Version': '2024-07-17',
        'Authorization': 'Bearer {}'.format(settings.SQUARE_ACCESS_TOKEN),
        'Content-Type': 'application/json',
    }
    sub = None
    if subscription:
        import requests, json
        pay = {
            'object_ids': [
                'A3FWKJF3OQ2Z2CLKOBPFY2WR',
            ],
        }
        res = requests.post('https://connect.squareup.com/v2/catalog/batch-retrieve', data=json.dumps(pay), headers=headers).json()
        print(json.dumps(res))
        SQUARE_CATEGORY = "EFKKLKRWLTZPNZXPX5XBLROX"
        SQUARE_SUB_ITEM = res['objects'][0]['item_data']['variations'][0]['id']
        payload_sub = {
            "idempotency_key": str(uuid.uuid4()),
            "object": {
                "type": "SUBSCRIPTION_PLAN",
                "id": "#1",
                "subscription_plan_data": {
                    "name": "Member Subscription",
                    "all_items": False,
                    "eligible_category_ids": [
                        "{}".format(SQUARE_CATEGORY),
                    ]
                }
            }
        }
        import requests, json
        print(email)
        j = requests.post('https://connect.squareup.com/v2/catalog/object/', data=json.dumps(payload_sub), headers=headers).json()
        print(json.dumps(j))
        p = j['catalog_object']
        sub = p['id']
        print(sub)
    payload = {
        "idempotency_key": str(uuid.uuid4()),
        "quick_pay": {
          "name": description,
          "price_money": {
            "amount": int(float(price) * 100),
            "currency": "USD"
          },
          "location_id": settings.SQUARE_LOCATION
        },
        "redirect_url": settings.BASE_URL + '/payments/square/?token={}'.format(token),
        "pre_populated_data": {
            "buyer_email": str(urllib.parse.unquote(email)),
        },
        "checkout_options":{'allow_tipping': True} if not subscription else {'subscription_plan_variation_id': sub},
    }
    import requests, json
    print(email)
    j = requests.post('https://connect.squareup.com/v2/online-checkout/payment-links', data=json.dumps(payload), headers=headers).json()
    print(json.dumps(j))
    p = j['payment_link']
    return p['order_id'], p['url']
