from django.conf import settings
ANET_NAME = settings.ANET_NAME
ANET_KEY = settings.ANET_KEY

def pay_fee(model, amount, card, full_name=None, address=None, customer_type=None, name=None, description=None):
    import random
    import imp
    import os
    import sys
    from authorizenet import apicontractsv1
    from authorizenet.apicontrollers import createTransactionController
    # Create a merchantAuthenticationType object with authentication details
    # retrieved from the constants file
    merchantAuth = apicontractsv1.merchantAuthenticationType()
    merchantAuth.name = ANET_NAME
    merchantAuth.transactionKey = ANET_KEY
    # Create the payment data for a credit card
    creditCard = apicontractsv1.creditCardType()
    creditCard.cardNumber = str(card.number)
    creditCard.expirationDate = "{}-{}".format(card.expiry_year, card.expiry_month)
    creditCard.cardCode = str(card.cvv_code)
    # Add the payment data to a paymentType object
    payment = apicontractsv1.paymentType()
    payment.creditCard = creditCard
    # Create order information
    order = apicontractsv1.orderType()
    order.invoiceNumber = str(random.randint(10000,99999))
    order.description = "Adult webcam modeling" if not description else description
    info = card.user.verifications.filter(verified=True).last()
    address = card.address if not address else address
    # Set the customer's Bill To address
    customerAddress = apicontractsv1.customerAddressType()
    if full_name:
        customerAddress.firstName = full_name.split(' ')[0]
        customerAddress.lastName = (full_name.split(' ')[2] if len(full_name.split(' ')) > 2 else full_name.split(' ')[1])
    else:
        customerAddress.firstName = info.full_name.split(' ')[0]
        customerAddress.lastName = (info.full_name.split(' ')[2] if len(info.full_name.split(' ')) > 2 else info.full_name.split(' ')[1])
    customerAddress.company = ""
    customerAddress.address = address.raw.split(',')[0]
    customerAddress.city = address.locality.name
    customerAddress.state = address.locality.state.code
    customerAddress.zip = str(address.locality.postal_code)
    customerAddress.country = address.locality.state.country.code
    # Set the customer's identifying information
    customerData = apicontractsv1.customerDataType()
    customerData.type = "individual" if not customer_type else customer_type
    customerData.id = str(card.user.id)
    customerData.email = card.user.email if not customer_email else customer_email
    # Add values for transaction settings
    duplicateWindowSetting = apicontractsv1.settingType()
    duplicateWindowSetting.settingName = "duplicateWindow"
    duplicateWindowSetting.settingValue = "600"
    settings = apicontractsv1.ArrayOfSetting()
    settings.setting.append(duplicateWindowSetting)
    # setup individual line items
    line_item_1 = apicontractsv1.lineItemType()
    line_item_1.itemId = str(model.id)
    line_item_1.name = model.profile.name if not name else name
    line_item_1.description = (model.profile.bio[:20] + '...') if not description else description
    line_item_1.quantity = "1"
    line_item_1.unitPrice = str(amount)
    # build the array of line items
    line_items = apicontractsv1.ArrayOfLineItem()
    line_items.lineItem.append(line_item_1)
    # Create a transactionRequestType object and add the previous objects to it.
    transactionrequest = apicontractsv1.transactionRequestType()
    transactionrequest.transactionType = "authCaptureTransaction"
    transactionrequest.amount = amount
    transactionrequest.payment = payment
    transactionrequest.order = order
    transactionrequest.billTo = customerAddress
    transactionrequest.customer = customerData
    transactionrequest.transactionSettings = settings
    transactionrequest.lineItems = line_items
    # Assemble the complete transaction request
    createtransactionrequest = apicontractsv1.createTransactionRequest()
    createtransactionrequest.merchantAuthentication = merchantAuth
    createtransactionrequest.refId = "MerchantID-0001"
    createtransactionrequest.transactionRequest = transactionrequest
    # Create the controller
    createtransactioncontroller = createTransactionController(
        createtransactionrequest)
    createtransactioncontroller.execute()
    response = createtransactioncontroller.getresponse()
    if response is not None:
        # Check to see if the API request was successfully received and acted upon
        if response.messages.resultCode == "Ok":
            # Since the API request was successful, look for a transaction response
            # and parse it to display the results of authorizing the card
            if hasattr(response.transactionResponse, 'messages') is True:
                print(
                    'Successfully created transaction with Transaction ID: %s'
                    % response.transactionResponse.transId)
                print('Transaction Response Code: %s' %
                      response.transactionResponse.responseCode)
                print('Message Code: %s' %
                      response.transactionResponse.messages.message[0].code)
                print('Description: %s' % response.transactionResponse.
                      messages.message[0].description)
                return True
            else:
                print('Failed Transaction.')
                if hasattr(response.transactionResponse, 'errors') is True:
                    print('Error Code:  %s' % str(response.transactionResponse.
                                                  errors.error[0].errorCode))
                    print(
                        'Error message: %s' %
                        response.transactionResponse.errors.error[0].errorText)
                return False
        # Or, print errors if the API request wasn't successful
        else:
            print('Failed Transaction.')
            if hasattr(response, 'transactionResponse') is True and hasattr(
                    response.transactionResponse, 'errors') is True:
                print('Error Code: %s' % str(
                    response.transactionResponse.errors.error[0].errorCode))
                print('Error message: %s' %
                      response.transactionResponse.errors.error[0].errorText)
            else:
                print('Error Code: %s' %
                      response.messages.message[0]['code'].text)
                print('Error message: %s' %
                      response.messages.message[0]['text'].text)
            return False
    else:
        print('Null Response.')
        return False
    return False
