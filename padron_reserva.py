import pandas as pd
import xmlrpc.client
from datetime import date, timedelta, datetime
import pytz

# ''' Conexión a localhost '''
# url = "http://localhost:8069"
# db = "DEV_08092024"
# username = 'LSantosL@iingen.unam.mx'
# password = 'I[-$mvy8YMBJ@=sDez6b8~k$k'

''' Conexión a develop '''
url = "http://192.168.29.97:18069"
db = "SIIF_SIDIA_08052024_develop"
username = 'LSantosL@iingen.unam.mx'
password = 'I[-$mvy8YMBJ@=sDez6b8~k$k'

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

def read_excel_file(file_path):
    # Lee el archivo Excel en un DataFrame
    df = pd.read_excel(file_path)
    return df


# Función para procesar cada fila del DataFrame
def process_suppliers(df):
    

        # Llamada al método para crear el proveedor en Odoo
        try:

        except Exception as e:
            print(f"Error al crear el proveedor: {e}")
        

# Ruta del archivo Excel en tu computadora
file_path = '/home/luanleon/Documentos/Padrones/Carga Inicial/IINGEN-UTICT-Padron-Proveedores_V2 - gfc 3.xlsx'

# Leer el archivo Excel
df_suppliers = read_excel_file(file_path)

# Procesar y validar cada registro
process_suppliers(df_suppliers)