from django.shortcuts import render
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from urllib import parse
import psycopg2
from django.shortcuts import  get_object_or_404
from shop.models import Platezhi
from django.db import transaction
from django.shortcuts import redirect


#Payment success
@login_required
@csrf_exempt
@require_POST
@transaction.atomic
def success(request):
    if request.method == 'POST':
        j = request.body
        j = parse.parse_qs(str(j))
        masked_card = str(j["masked_card"][0])
        rrn = str(j["b'rrn"][0])
        summ = int(j['actual_amount'][0])/100
        merchant_id = str(j['merchant_id'][0])
        order_id = str(j['order_id'][0])
        payment_id = str(j['payment_id'][0])
        head, sep, tail = order_id.partition('/')
        user_id = int(tail)
        ord_id = int(head)

        conn = psycopg2.connect(dbname='*****', user='*****',
                            password='********', host='127.0.0.1', port=6432)
        cur = conn.cursor()

        cur.execute(
                           "SELECT summ from shop_platezhi WHERE id=%s", (ord_id,)
                           )
        summ_t = cur.fetchone()
        summ_t = summ_t[0]

        cur.execute(
                           "SELECT us_name from shop_platezhi WHERE id=%s", (ord_id,)
                           )
        us_name = cur.fetchone()
        us_name = us_name[0]

        if int(summ_t) == int(summ) and int(user_id)== int(us_name) and int(merchant_id)== 1454662:
            cur.execute(
                               "SELECT cash from setings_profile WHERE user_id=%s", (user_id,)
                               )
            cash = cur.fetchone()
            cash = cash[0]
            cash = cash + summ
            cur.execute(
                        "UPDATE setings_profile SET cash = %s WHERE user_id=%s", (cash, user_id,)
                                   )
            conn.commit()
            cur.close()
            conn.close()

            link = get_object_or_404(Platezhi, id=ord_id)
            r = Platezhi(masked_card = masked_card, payment_id = payment_id, rrn = rrn, is_paid = True, id = ord_id)
            r.save(update_fields=['payment_id', 'paid', 'is_paid', 'masked_card', 'rrn'])

            return redirect('setings:LinksList')



#Payment error
@login_required
@csrf_exempt
@require_POST
@transaction.atomic
def error(request):
    if request.method == 'POST':

            return render(request, 'error.html', {
                            })
