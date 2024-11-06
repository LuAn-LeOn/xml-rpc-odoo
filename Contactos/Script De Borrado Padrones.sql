-- Proveedor Nacional
DELETE FROM stantards_nationalsuppliers;
-- Proveedor Extranjero
DELETE FROM standards_foreignsupplier;
-- Prestador de Servicios Profesionales
DELETE FROM stantards_serviceproviders;
-- Becarios
DELETE FROM stantards_scholarships;
-- Consecutivos Layouts
DELETE FROM layouts_consecutive_padron;
-- Beneficiario Registro Layout
DELETE FROM beneficiary_registration_layouts;
-- Sanciones
DELETE FROM stantards_sanctions;
-- Banco-Cuenta-layout
DELETE FROM bank_account_layout;
-- Contacto-Padrón
DELETE FROM contactpadron_relationship;
-- Solicitudes de Pago Canceladas
DELETE FROM general_payment_request_cancel;
-- Cuentas Relacionadas a un Beneficiario
DELETE FROM ns_bankaccounts;

UPDATE res_partner
SET flag_national_supplier = NULL
WHERE flag_national_supplier = TRUE;

UPDATE res_partner
SET flag_foreign_supplier = NULL
WHERE flag_foreign_supplier = TRUE;

UPDATE res_partner
SET flag_service_provider = NULL
WHERE flag_service_provider = TRUE;

UPDATE res_partner
SET flag_scholarship = NULL
WHERE flag_scholarship = TRUE;






