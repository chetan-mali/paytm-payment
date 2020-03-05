from django.http import HttpResponse
from django.shortcuts import render
from . import Checksum
from django.utils.translation import get_language
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


def home(request):
    return render(request, "home.html")

@csrf_exempt
def payment(request):

    name = request.POST.get('Name')
    email = request.POST.get('Email')
    amount = request.POST.get('Amount')

    MERCHANT_KEY = settings.PAYTM_MERCHANT_KEY
    MERCHANT_ID = settings.PAYTM_MERCHANT_ID
    # get_lang = "/" + get_language() if get_language() else ''
    CALLBACK_URL = settings.HOST_URL  + settings.PAYTM_CALLBACK_URL
    # Generating unique temporary ids
    order_id = Checksum.__id_generator__()

    if amount:
        data_dict = {
                    'MID':MERCHANT_ID,
                    'ORDER_ID':str(order_id),
                    'TXN_AMOUNT': str(amount),
                    'CUST_ID':email,
                    'INDUSTRY_TYPE_ID':'Retail',
                    'WEBSITE': settings.PAYTM_WEBSITE,
                    'CHANNEL_ID':'WEB',
                    'CALLBACK_URL':CALLBACK_URL,
                }
        param_dict = data_dict
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(data_dict, MERCHANT_KEY)
        return render(request,"payment.html",{'paytmdict':param_dict})
    return render(request,'home.html')


@csrf_exempt
def response(request):
    if request.method == "POST":
        MERCHANT_KEY = settings.PAYTM_MERCHANT_KEY
        data_dict = {}
        for key in request.POST:
            data_dict[key] = request.POST[key]
        verify = Checksum.verify_checksum(data_dict, MERCHANT_KEY, data_dict['CHECKSUMHASH'])
        if verify:
            # PaytmHistory.objects.create(user=request.user, **data_dict)
            return render(request,"response.html",{"paytm":data_dict})
        else:
            return HttpResponse("checksum verify failed")
    return HttpResponse(status=200)