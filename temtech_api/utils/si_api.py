import frappe
import json
from frappe.utils import getdate, nowdate, nowtime
from datetime import datetime


@frappe.whitelist(allow_guest=True)
def submit_sales_invoice():
    try:
        sales_invoice_data = json.loads(frappe.request.data)

        customer_name = sales_invoice_data["customer_name"]
        customer_phone_number = sales_invoice_data["customer_phone_number"]
        customer_email = sales_invoice_data["customer_email"]

        si_customer_name = validate_customer(
            customer_name, customer_phone_number, customer_email
        )

        posting_date = getdate(sales_invoice_data["posting_date"]) if sales_invoice_data.get(
            "posting_date") else getdate()
        posting_time = sales_invoice_data["posting_time"] if sales_invoice_data.get(
            "posting_time") else nowtime()
        currency = "USD"

        is_pos = 1
        pos_profile = "Social Media"

        transaction_id = sales_invoice_data["transaction_id"]

        tax_category = "VAT 10%"
        taxes_and_charges = "VAT 10% - TTT"

        taxes_and_charges_row_charge_type = "On Net Total"
        taxes_and_charges_row_account_head = "21201 - ضريبة القيمة المضافة واجبة السداد VAT - TTT"
        taxes_and_charges_row_rate = 10
        taxes_and_charges_row_included_in_print_rate = 1

        payments_row_mode_of_payment = "CrediMAX Gateway"
        payments_row_amount = sales_invoice_data["amount"]

        items_row_item_code = f"""SM{sales_invoice_data["amount"]}""" if sales_invoice_data.get(
            "amount") else 0
        items_row_item_name = f"""SM{sales_invoice_data["amount"]}""" if sales_invoice_data.get(
            "amount") else 0
        items_row_qty = 1
        items_row_uom = "Nos"
        items_row_rate = sales_invoice_data["amount"]
        items_row_income_account = "4121 - المبيعات (سوشيال ميديا) - TTT"
        items_row_cost_center = "Main - TTT"

        si_doc = frappe.new_doc('Sales Invoice')
        si_doc.customer = si_customer_name
        si_doc.posting_date = posting_date
        si_doc.posting_time = posting_time
        si_doc.currency = currency

        si_doc.is_pos = is_pos
        si_doc.pos_profile = pos_profile
        si_doc.custom_transaction_id = transaction_id

        si_doc.tax_category = tax_category
        si_doc.taxes_and_charges = taxes_and_charges
        si_doc.taxes = []
        si_doc.append('taxes', {
            "charge_type": taxes_and_charges_row_charge_type,
            "description": " ضريبة القيمة المضافة واجبة السداد VAT ",
            "account_head": taxes_and_charges_row_account_head,
            "included_in_print_rate": taxes_and_charges_row_included_in_print_rate,
            "rate": taxes_and_charges_row_rate
        })

        si_doc.payments = []
        si_doc.append('payments', {
            "mode_of_payment": payments_row_mode_of_payment,
            "amount": payments_row_amount
        })

        si_doc.items = []
        si_doc.append('items', {
            "item_code": items_row_item_code,
            "item_name": items_row_item_name,
            "qty": items_row_qty,
            "uom": items_row_uom,
            "rate": items_row_rate,
            "income_account": items_row_income_account,
            "cost_center": items_row_cost_center
        })

        si_doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return si_doc.name
    except Exception as ex:
        frappe.log_error(frappe.get_traceback(), "submit_sales_invoice:api")
        frappe.throw(frappe.get_traceback())


def validate_customer(customer_name, customer_phone_number, customer_email):
    if not frappe.db.exists("Customer", customer_name):
        customer_doc = frappe.new_doc('Customer')
        customer_doc.customer_name = customer_name
        customer_doc.custom_phone_number = customer_phone_number
        customer_doc.custom_email = customer_email
        customer_doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return customer_doc.customer_name
    return customer_name
