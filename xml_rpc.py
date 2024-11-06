

# ''' Conexión a localhost '''
url = "http://localhost:8069"
db = "DEV_17012024"
username = 'LSantosL@iingen.unam.mx'
password = 'Axv2517lal$'

import xmlrpc.client
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
common.version()

uid = common.authenticate(db, username, password, {})
print("UID", uid)
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

''' Busqueda para encontrar nombre de quien se autenticó en la base '''
user_data = models.execute_kw(db, uid, password, 'res.users', 'read', [[uid]], {'fields': ['partner_id']})
if user_data:
    partner_id = user_data[0].get('partner_id', False)
    if partner_id:
        partner_data = models.execute_kw(db, uid, password, 'res.partner', 'read', [[partner_id[0]]], {'fields': ['name']})
        if partner_data:
            partner_name = partner_data[0].get('name', '')
            print("El nombre del usuario que se ha autenticado es:", partner_name)
        else:
            print("No se encontró el partner con el ID especificado.")
    else:
        print("El usuario no tiene un partner asociado.")
else:
    print("No se encontró el usuario con el UID especificado.")


# ''' Agregar registro a res_city '''
# # Verificar si la ciudad ya existe
# city_name = 'Benito Juárez'
# city_search = models.execute_kw(
#     db, uid, password, 'res.city', 'search_read', 
#     [[['name', '=', city_name], ['country_id', '=', 156], ['state_id', '=', 506]]], 
#     {'fields': ['id', 'name']}
# )

# if city_search:
#     print("La ciudad ya existe:", city_search)
# else:
#     # Crear el nuevo registro en res.city
#     city_id = models.execute_kw(
#         db, uid, password, 'res.city', 'create', 
#         [{
#             'name': city_name,
#             'country_id': 156,
#             'state_id': 506
#         }]
#     )
#     print("Se ha creado la ciudad con ID:", city_id)


''' Busqueda en tabla de Proveedores '''
record_id = [['id', '=', 13]]
new_cve_beneficiary = 'N1754127'
# Verificar si el registro existe
ns_id = models.execute_kw(db, uid, password, 'stantards.nationalsuppliers', 'search_read', 
                                [[('id', '=', 13)]], 
                                {'fields': ['id']})
if ns_id:
    print(f"El Beneficiario con ID {ns_id} se le actualizó su clave beneficiario a {new_cve_beneficiary}")
    

