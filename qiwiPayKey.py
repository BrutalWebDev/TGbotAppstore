import requests
import time
import json

def pay_simple_prv(api_access_token, prv_id, to_account, sum_pay):
    s = requests.Session()
    s.headers['Accept'] = 'application/json'
    s.headers['Content-Type'] = 'application/json'
    s.headers['authorization'] = 'Bearer ' + api_access_token
    postjson = {"id":"","sum": {"amount":"","currency":"643"},"paymentMethod": {"type":"Account","accountId":"643"},"fields": {"account":""}}
    postjson['id'] = str(int(time.time() * 1000))
    postjson['sum']['amount'] = sum_pay
    postjson['fields']['account'] = to_account
    res = s.post('https://edge.qiwi.com/sinap/api/v2/terms/'+prv_id+'/payments', json = postjson)
    return res.json()



