import json
import random
import urllib.request
from urllib.error import HTTPError


HOST = 'localhost'
PORT = 8069
DB = 'DEV_17012024'
USER = 'LSantosL@iingen.unam.mx'
PASS = 'Axv2517lal$'

class RPCError(Exception):
    def __init__(self, message):
        super().__init__(message)

def json_rpc(url, method, params):
    data = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": random.randint(0, 1000000000),
    }
    req = urllib.request.Request(url=url, data=json.dumps(data).encode(), headers={
        "Content-Type":"application/json",
    })
    reply = json.loads(urllib.request.urlopen(req).read().decode('UTF-8'))
    if reply.get("error"):
        raise RPCError(reply["error"])
    return reply["result"]

def call(url, service, method, *args):
    return json_rpc(url, "call", {"service": service, "method": method, "args": args})

# log in the given database
url = "http://%s:%s/jsonrpc" % (HOST, PORT)
uid = call(url, "common", "login", DB, USER, PASS)

print("UID", uid)

''' Busqueda para encontrar nombre de quien se autenticó en la base '''
res_user_id = call(url, "object", "execute", DB, uid, PASS, 'res.users', 'read', [uid], ['partner_id'])
if res_user_id:
    partner_id = res_user_id[0].get('partner_id', False)
    if partner_id:
        partner_data = call(url, "object", "execute", DB, uid, PASS, 'res.partner', 'read', [partner_id[0]], ['name'])
        if partner_data:
            partner_name = partner_data[0].get('name', '')
            print("El nombre del usuario que se ha autenticado es:", partner_name)
        else:
            print("No se encontró el partner con el ID especificado.")
    else:
        print("El usuario no tiene un partner asociado.")
else:
    print("No se encontró el usuario con el UID especificado.")

