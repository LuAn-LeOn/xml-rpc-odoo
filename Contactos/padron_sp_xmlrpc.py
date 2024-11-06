import pandas as pd
import xmlrpc.client
from datetime import date, timedelta, datetime
import pytz

# ''' Conexión a localhost '''
# url = "http://localhost:8069"
# db = "DEV_08092024"
# username = 'LSantosL@iingen.unam.mx'
# password = 'I[-$mvy8YMBJ@=sDez6b8~k$k'

# ''' Conexión con Develop '''
# url = "http://192.168.29.97:18069"
# db = "SIIF_SIDIA_08052024_develop"
# username = 'LSantosL@iingen.unam.mx'
# password = 'I[-$mvy8YMBJ@=sDez6b8~k$k'

# ''' Conexión con QA '''
# url = "https://sidia-qa.patronato.unam.mx/"
# db = "SIIF_SIDIA_06062024_qa"
# username = 'LSantosL@iingen.unam.mx'
# password = 'LSantosL123$$'

# ''' Conexión con 5.45 (Pre-Producción) '''
# url = "http://192.168.5.45:18069"
# db = "SIIF_SIDIA_20092024"
# username = 'LSantosL@iingen.unam.mx'
# password = 'LSantosL123$$'

''' Conexión con Base de UTIC (Pre-Producción) '''
url = "https://siif-pruebas.patronato.unam.mx"
db = "SIIF_SIDIA"
username = 'LSantosL@iingen.unam.mx'
password = 'LSantosL123$$'

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
    df = pd.read_excel(file_path, nrows=2000).fillna('')
    return df

# Función para crear un registro en 'NationalSuppliers' usando XML-RPC
def create_national_supplier(data):
    supplier_id = models.execute_kw(
        db, uid, password,
        'stantards.serviceproviders', 'create',
        [data]
    )
    # Leer el campo contact_id del registro recién creado
    supplier_data = models.execute_kw(
        db, uid, password,
        'stantards.serviceproviders', 'read',
        [supplier_id], {'fields': ['contact_id']}
    )
    
    # Obtener el contact_id
    contact_id = supplier_data[0].get('contact_id') if supplier_data else None
    return supplier_id, contact_id

# Función para buscar el ID de 'tax_regime' basado en su descripción
def get_tax_regime_id(tax_regime_name, models, db, uid, password):
    # Buscar el régimen fiscal por su nombre/descripción en 'sd_base.tax_regime'
    tax_regime = models.execute_kw(db, uid, password, 'sd_base.tax_regime', 'search_read', 
                                [[('name', '=', tax_regime_name)]])
    if tax_regime:
        return tax_regime[0].get('id')
    else:
        print(f"Error: No se encontró el régimen fiscal con la descripción '{tax_regime_name}'")
        return False

# Función para buscar el ID de 'account.account' basado en su código
def get_account_id(account_code, models, db, uid, password):
    # Buscar la cuenta por su código en 'account.account'
    account = models.execute_kw(db, uid, password, 'account.account', 'search_read', 
                                [[('code', '=', account_code)]], {'fields': ['id']})
    if account:
        return account[0].get('id')
    else:
        print(f"Error: No se encontró la cuenta con el código '{account_code}'")
        return False

# Función para buscar el Pais
def get_country_id(country_name, models, db, uid, password):
    # Buscar el país por su nombre en'res.country'
    country = models.execute_kw(db, uid, password, 'res.country', 'search_read', 
                                [[('name', '=', country_name)]], {'fields': ['id']})
    if country:
        return country[0].get('id')
    else:
        print(f"Error: No se encontró el país con el nombre '{country_name}'")
        return False

# Función para buscar el Estado del País
def get_state_id(state_name, country_id, models, db, uid, password):
    # Buscar el estado por su nombre en'res.country.state'
    state = models.execute_kw(db, uid, password, 'res.country.state', 'search_read', 
                                [[('name', '=', state_name), ('country_id', '=', country_id)]], {'fields': ['id']})
    if state:
        return state[0].get('id')
    else:
        print(f"Error: No se encontró el estado con el nombre '{state_name}' en el país {country_id}")
        return False

# Función para buscar el Id de la ciudad
def get_city_hall_id(city_name, state_id, models, db, uid, password):
    # Buscar la ciudad por su nombre en'res.country.state.city'
    city = models.execute_kw(db, uid, password, 'res.city', 'search_read', 
                                [[('name', '=', city_name), ('state_id', '=', state_id)]], {'fields': ['id']})
    if city:
        return city[0].get('id')
    else:
        print(f"Error: No se encontró la ciudad con el nombre '{city_name}' en el estado {state_id}")
        return False

# Función para obtener el ID asociado en branch.offices
def get_branch_office_id(supplier_id, models, db, uid, password):
    # Buscar el registro en branch.offices por supplier_id
    branch_office = models.execute_kw(db, uid, password, 'branch.offices', 'search_read',
                                    [[('service_providers_id', '=', supplier_id)]], {'fields': ['id']})
    if branch_office:
        return branch_office[0].get('id')
    else:
        print(f"Error: No se encontró el registro asociado en branch.offices para el supplier_id {supplier_id}")
        return False
    
# Función para buscar el ID de la cuenta bancaria en res.partner.bank basado en su número de cuenta
def get_partner_bank_id(account_number, bank_id, clabe, partner_id, models, db, uid, password):
    # Buscar la cuenta bancaria por su número en 'res.partner.bank'
    partner_bank = models.execute_kw(db, uid, password, 'res.partner.bank', 'search_read', 
                                    [['|', ('acc_number', '=', account_number), ('l10n_mx_edi_clabe', '=', clabe)]], {'fields': ['id']})
    
    if partner_bank:
        return partner_bank[0].get('id')
    else:
        print(f"Error: No se encontró la cuenta bancaria con el número '{account_number}'")

def create_bank_account_partner(acc_number, clabe, bank_id, partner_id):

    bank_account_data = {
        'acc_number': acc_number,
        'bank_id': bank_id,
        'l10n_mx_edi_clabe': clabe,
        'partner_id': partner_id,
    }
    bank_account_id = create_bank_partner(bank_account_data)
    return bank_account_id

# Función para crear cuentas nuevas relacionadas al partner_id
def create_bank_partner(data):
    bank_account_id = models.execute_kw(
        db, uid, password,
        'res.partner.bank', 'create',
        [data]
    )
    return bank_account_id

# Función para crear un registro en 'ns.bankaccounts'
def create_ns_bank_account(data):
    bank_account_id = models.execute_kw(
        db, uid, password,
        'ns.bankaccounts', 'create',
        [data]
    )
    return bank_account_id

# Función para buscar el ID del banco en res.bank basado en el nombre del banco que trae el excel
def get_bank_id(nombre_banco, models, db, uid, password):
    # Buscar el banco por su nombre en'res.bank'
    bank = models.execute_kw(db, uid, password,'res.bank', 'search_read', 
                                [[('name', '=', nombre_banco)]], {'fields': ['id']})
    if bank:
        return bank[0].get('id')
    else:
        print(f"Error: No se encontró el banco con el nombre '{nombre_banco}'")
        return False

def get_partner_id(titular, models, db, uid, password):
    # Buscar el titular por su nombre en'res.partner'
    partner = models.execute_kw(db, uid, password,'res.partner', 'search_read', 
                                [[('name', '=', titular)]], {'fields': ['id']})
    if partner:
        return partner[0].get('id')
    else:
        print(f"Error: No se encontró el titular con el nombre '{titular}'")
        return False

def get_partner_rfc_id(rfc, models, db, uid, password):
    # Buscar el titular por su nombre en'res.partner'
    partner = models.execute_kw(db, uid, password,'res.partner', 'search_read', 
                                [[('vat', '=', rfc)]], {'fields': ['id']})
    if partner:
        return partner[0].get('id')
    else:
        print(f"Error: No se encontró el Partner con el rfc: '{rfc}'")
        return False
    
def update_partner_name(partner_id, full_name, models, db, uid, password):
    # Buscar el titular por su nombre en'res.partner'
    partner = models.execute_kw(db, uid, password,'res.partner', 'search_read', 
                                [[('id', '=', partner_id)]], {'fields': ['id', 'name']})
    if partner:
        models.execute_kw(
            db, uid, password,
            'res.partner', 'write',
            [[partner_id], {'name': full_name}]
        )
        print(f"Nombre completo actualizado para el ID {partner_id} en res.partner.")


def get_layout_id(models, db, uid, password):
    # Buscar ID del Layout activo y que en su Descripción tenga Alta Beneficiarios
    layout_id = models.execute_kw(db, uid, password, 'bank.layouts.catalog', 'search_read', 
                                [[('census', '=', 'professional_services_provider'), ('description', '=', 'Alta Beneficiarios'), ('states', '=', 'active')]], 
                                {'fields': ['id', 'bank_id']})
    if layout_id:
        return layout_id
    else:
        print("Error: No se encontró el Layout activo para Proveedor Nacional con descripción 'Alta Beneficiarios'")
        return False

def create_control_cuentas(layout_id, bank_account_id, supplier_id, bank_id, branch_office_id):
    for rec in layout_id:
        data_account_layout = {
            'bank_id': rec['bank_id'][0],
            'account_id': bank_account_id,
            'status': 'Activo',
            'description': 'Activo por Servicio Web',
        }
        account_layout_id = create_bank_account_layout(data_account_layout)
        print(f"Creada la Activación de la Cuenta, ID: {account_layout_id}")
        data_beneficiary_layout = {
            'branch_office_id': branch_office_id,
            'service_provider_id': supplier_id,
            'account_id_reg_bank': bank_account_id,
            'bank_id_reg_bank': bank_id,
            'bank_registration': rec['bank_id'][0],
            'description_bank': 'Activo por Servicio Web',
            'status_bancario': True,
        }
        bank_records = create_beneficiary_registration_layout(data_beneficiary_layout)
        print(f"Creados los Registros Bancarios según los layouts Activos y como Alta de Beneficiarios, ID: {bank_records}")


def create_control_cuentas_2(layout_id, bank_account_id, supplier_id, bank_id, branch_office_id):
    for rec in layout_id:
        data_beneficiary_layout = {
            'branch_office_id': branch_office_id,
            'service_provider_id': supplier_id,
            'account_id_reg_bank': bank_account_id,
            'bank_id_reg_bank': bank_id,
            'bank_registration': rec['bank_id'][0],
            'description_bank': 'Activo por Servicio Web',
            'status_bancario': True,
        }
        bank_records = create_beneficiary_registration_layout(data_beneficiary_layout)
        print(f"Creados los Registros Bancarios según los layouts Activos y como Alta de Beneficiarios, ID: {bank_records}")

# Función para crear un registro en 'ns.bankaccounts'
def create_bank_account_layout(data):
    account_layout_id = models.execute_kw(
        db, uid, password,
        'bank.account.layout', 'create',
        [data]
    )
    return account_layout_id

# Función para crear los Registro Bancarios
def create_beneficiary_registration_layout(data):
    records_bank = models.execute_kw(
        db, uid, password,
        'beneficiary.registration.layouts', 'create',
        [data]
    )
    return records_bank

# Función para crear el Contacto Padron
def create_contact_padron(data):
    record = models.execute_kw(
        db, uid, password,
        'contactpadron.relationship', 'create',
        [data]
    )
    return record

def get_bank_account_layout(bank_id, account_id, models, db, uid, password):
    registro_bank_account_layout = models.execute_kw(db, uid, password, 'bank.account.layout', 'search_read', 
                                [[('bank_id', '=', bank_id), ('account_id', '=', account_id), ('status', '=', 'Activo')]], 
                                {'fields': ['id']})
    if registro_bank_account_layout:
        return registro_bank_account_layout[0].get('id')


def change_ns_flag(partner_id):
    layout_id = models.execute_kw(db, uid, password, 'res.partner', 'search_read', 
                                [[('id', '=', partner_id)]], 
                                {'fields': ['id']})
    if layout_id:
        models.execute_kw(db, uid, password, 'res.partner', 'write', [[partner_id], {'flag_service_provider': True}])
        print(f"El Contacto Padron con ID {partner_id} se ha marcado con NS_FLAG")


def change_ns_states(supplier_id):
    layout_id = models.execute_kw(db, uid, password, 'stantards.serviceproviders', 'search_read', 
                                [[('id', '=', supplier_id)]], 
                                {'fields': ['id']})
    if layout_id:
        models.execute_kw(db, uid, password, 'stantards.serviceproviders', 'write', [[supplier_id], {'states': 'active'}])
        print(f"El Beneficiario con ID {supplier_id} se Activó")

def prepare_record_ns(supplier_id, branch_office_id, bank_account_id, bank_id, numero_cuenta, clabe):
    data_ns_bankaccounts = {
        'account_id': bank_account_id,
        'service_providers_id': supplier_id,
        'branch_office_id': branch_office_id,
        'bank_id': bank_id,
        'acc_num': numero_cuenta,
        'clabe': clabe,
    }
    ns_bankaccounts_id = create_ns_bank_account(data_ns_bankaccounts)
    print(f"Registro de cuenta bancaria creado con ID: {ns_bankaccounts_id}")


# Función para procesar cada fila del DataFrame
def process_suppliers(df):
    curp = ''
    name = ''
    last_name = ''
    mother_last_name = ''
    name_company = ''
    num_int = ''
    cuenta_id = ''
    type_person = ''
    # Definir la zona horaria de México (o la que corresponda)
    timezone = pytz.timezone('America/Mexico_City')
    # Obtener la fecha actual en formato YYYY-MM-DD
    current_date = datetime.now(timezone).strftime('%Y-%m-%d')

    for index, row in df.iterrows():
        tipo_persona_str = str(row['Tipo de Persona']).strip()

        # Transformar el valor directamente con if-elif-else
        if tipo_persona_str == 'Física':
            type_person = 'physics'
        elif tipo_persona_str == 'Moral':
            type_person = 'moral'
        else:
            type_person = ''
        
        # Obtener el ID de la cuenta por cobrar usando el código de la cuenta del Excel
        account_receivable_id = get_account_id(row['Cuenta a Cobrar'], models, db, uid, password)
        if not account_receivable_id:
            print(f"Error: No se encontró la cuenta por cobrar en la fila {index + 1}: {row['Cuenta Cobrar']}")
            continue  # Saltar esta fila si no se encuentra la cuenta

        # Obtener el ID de la cuenta por pagar usando el código de la cuenta del Excel
        account_payable_id = get_account_id(row['Cuenta a Pagar'], models, db, uid, password)
        if not account_payable_id:
            print(f"Error: No se encontró la cuenta por pagar en la fila {index + 1}: {row['Cuenta Pagar']}")
            continue  # Saltar esta fila si no se encuentra la cuenta

        # Obten el Id del País usando nombre del País en el excel
        country_id = get_country_id(row['País'], models, db, uid, password)
        if not country_id:
            print(f"Error: No se encontró el País en la fila {index + 1}: {row['Pais']}")
            continue  # Saltar esta fila si no se encuentra el País

        # Obten el Id del Estado usando nombre del Estado en el excel
        state_id = get_state_id(row['Estado'], country_id, models, db, uid, password)

        # Obtener el ID de la ciudad usando el nombre de la ciudad en el Excel
        city_hall_id = get_city_hall_id(row['Ciudad'], state_id, models, db, uid, password)
        if not city_hall_id:
            print(f"Error: No se encontró la ciudad en la fila {index + 1}: {row['Ciudad']}")
            continue  # Saltar esta fila si no se encuentra la ciudad

        # Obtener el Id del Banco usuando el nombre del banco del excel
        bank_id = get_bank_id(row['Banco'], models, db, uid, password)
        print(f"ID BANCO: {bank_id}")
        
        phone = str(row['Teléfono Fiscal']).split('.')[0]

        curp_vacio = str(row['CURP'])
        if curp_vacio == 'nan':
            curp = False
        else:
            curp = row['CURP']

        name_vacio = row['Nombre']
        if name_vacio == 'nan':
            name = False
        else:
            name = row['Nombre']
        
        last_name_vacio = row['Apellido Paterno']
        if last_name_vacio == 'nan':
            last_name = False
        else:
            last_name = row['Apellido Paterno']

        mother_last_name_vacio = row['Apellido Materno']
        if mother_last_name_vacio == 'nan':
            mother_last_name = False
        else:
            mother_last_name = row['Apellido Materno']

        name_company_vacio = row['Nombre Compañía']
        if name_company_vacio == 'nan':
            name_company = False
        else:
            name_company = row['Nombre Compañía']
        
        num_int_vacio = row['Num. Int.']
        if num_int_vacio == 'nan':
            num_int = False
        else:
            num_int = row['Num. Int.']
        if type_person == 'physics':
            partner_id = get_partner_rfc_id(row['RFC'], models, db, uid, password)
            full_name = row['Apellido Paterno'] + ' ' + row['Apellido Materno'] + ' ' + row['Nombre']
            print(f"RES FULL NAME: {full_name}")
            if partner_id and name != full_name:
                update_partner_name(partner_id, full_name, models, db, uid, password)
                print(f"RES PARTNER: {partner_id}")
            if not partner_id:
                print(f"Error: No se encontró el RFC en la fila {index + 1}: {row['RFC']}")
        
        tax_regime_id = get_tax_regime_id(row['Regimen Fiscal'], models, db, uid, password)


        # Convertir la fila del DataFrame en un diccionario
        supplier_data = {
            'name_psp': row['Nombre'],
            'last_name_psp': last_name,
            'mother_last_name_psp': mother_last_name,
            # 'name_company_psp': name_company,
            'rfc': row['RFC'],
            'curp': curp,
            'beneficiary_key': row['Clave de Beneficiario'],
            'type_person': type_person,
            'tax_regime_id': tax_regime_id,
            'tax_email': row['Correo Electrónico Fiscal'],
            'tax_phone': phone,
            'account_receivable_id': account_receivable_id,
            'account_payable_id': account_payable_id,
            'country_psp': country_id,
            'state_psp': state_id,
            'city_hall_psp': city_hall_id,
            'colony_psp': row['Colonia'],
            'street_psp': row['Calle'],
            'num_ext_psp': row['Num. Ext.'],
            'num_int_psp': num_int,
            'zip_code_psp': row['Código Postal'],
            'states': 'in_review',
            'start_date': current_date,
            # Añadir aquí más campos según sea necesario
        }
        # Realizar validaciones o invocar métodos en Odoo
        print(f"Procesando proveedor: {supplier_data['name_psp']}")

        # Llamada al método para crear el proveedor en Odoo
        try:
            supplier_id, contact_id = create_national_supplier(supplier_data)
            print(f"Proveedor creado con ID: {supplier_id}")

            print(f"TITULAR EN RES PARTNER: {contact_id[1]}")

            # Obtener el ID de la cuenta bancaria usando el número de cuenta del Excel
            numero_cuenta = str(row['Cuenta Bancaria'])
            print(f"NUMERO DE CUENTA: {numero_cuenta}")
            clabe = str(row['Cuenta Clabe'])
            print(f"CUENTA CLABE: {clabe}")
            bank_account_id = get_partner_bank_id(numero_cuenta, bank_id, clabe, contact_id[0], models, db, uid, password)
            if bank_account_id:
                print(f"CUENTA ID: {bank_account_id}")
                cuenta_id = bank_account_id
            if not bank_account_id:
                # Crear registro en res.partner.bank
                print(f"CUANTA NO ENCONTRADA: {numero_cuenta}, se creará.")
                cuenta_id = create_bank_account_partner(numero_cuenta, clabe, bank_id, contact_id[0])
                print(f"CUENTA CREADA CORRECTAMENTE CON ID: {cuenta_id} Y ACC NUMBER {numero_cuenta}")

            # Obtener el ID del registro asociado en branch.offices
            branch_office_id = get_branch_office_id(supplier_id, models, db, uid, password)
            if branch_office_id:
                print(f"Registro asociado en branch.offices con ID: {branch_office_id}")
                prepare_record_ns(supplier_id, branch_office_id, cuenta_id, bank_id, numero_cuenta, clabe)
            else:
                print("No se encontró un registro asociado en branch.offices.")
            # Obtener Ids de los layouts activos y que en su Descripción tengan Alta de Beneficiario
            layout_id = get_layout_id(models, db, uid, password)
            bank_account_layout = get_bank_account_layout(bank_id, cuenta_id, models, db, uid, password)
            print(f"ID DE BANK ACCOUNT LAYOUT: {bank_account_layout}")
            if not bank_account_layout:
                # Crear registro en bank.account.layout
                create_control_cuentas(layout_id, cuenta_id, supplier_id, bank_id, branch_office_id)
            else:
                create_control_cuentas_2(layout_id, cuenta_id, supplier_id, bank_id, branch_office_id)
            # Definir la zona horaria de México (o la que corresponda)
            timezone = pytz.timezone('America/Mexico_City')
            # Obtener la fecha actual en formato YYYY-MM-DD
            current_date = datetime.now(timezone).strftime('%Y-%m-%d')
            data_contact_padron = {
                'contact_id': contact_id[0],
                'rfc': row['RFC'],
                'curp': row['CURP'],
                'cve_beneficiary': row['Clave de Beneficiario'],
                'type_beneficiary': 'service_provider',
                'service_providers_id': supplier_id,
                'start_date': current_date,
                'state': 'active'
            }
            contact_padron = create_contact_padron(data_contact_padron)
            print(f"Creado el Registro en Padrones, ID: {contact_padron}")
            change_ns_flag(contact_id[0])
            change_ns_states(supplier_id)

        except Exception as e:
            print(f"Error al crear el proveedor: {e}")
        

# Ruta del archivo Excel en tu computadora
file_path = '/home/luanleon/Documentos/Padrones/Carga Inicial/IINGEN-UTICT-Padron-Prestadores de Servicios_24-10-24 - carga 1.xlsx'

# Leer el archivo Excel
df_suppliers = read_excel_file(file_path)

# Procesar y validar cada registro
process_suppliers(df_suppliers)