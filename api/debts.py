from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
import logging
from .query.q_debts import get_debt_summary, get_debtors_list, get_debts, pay_debt

debts_ns = Namespace("debts", description="API hutang pelanggan")

debt_payment_model = debts_ns.model("DebtPayment", {
    "debt_id": fields.Integer(required=True),
    "amount": fields.Float(required=True)
})

@debts_ns.route('')
class DebtList(Resource):
    @jwt_required()
    def get(self):
        lokasi_id = request.args.get("lokasi_id", type=int)
        try:
            debts = get_debts(lokasi_id)
            return {"status": "success", "data": debts}, 200
        except Exception as e:
            logging.error(str(e))
            return {"status": "Terjadi kesalahan server"}, 500

    @jwt_required()
    @debts_ns.expect(debt_payment_model)
    def post(self):
        data = request.get_json()
        debt_id = data.get("debt_id")
        amount = data.get("amount")
        if not debt_id or amount is None:
            return {"status": "Field debt_id dan amount wajib diisi"}, 400

        try:
            updated = pay_debt(debt_id, amount)
            if not updated:
                return {"status": "Data hutang tidak ditemukan"}, 404
            return {"status": "Pembayaran hutang berhasil", "data": updated}, 200
        except ValueError as ve:
            return {"status": "Gagal", "message": str(ve)}, 400
        except Exception as e:
            logging.error(str(e))
            return {"status": "Terjadi kesalahan server"}, 500

@debts_ns.route('/payments')
class DebtPayments(Resource):
    @jwt_required()
    def get(self):
        debt_id = request.args.get("debt_id", type=int)
        if not debt_id:
            return {"status": "Parameter debt_id wajib diisi"}, 400
        try:
            from .query.q_debts import get_debt_payments
            payments = get_debt_payments(debt_id)
            return {"status": "success", "data": payments}, 200
        except Exception as e:
            logging.error(str(e))
            return {"status": "Terjadi kesalahan server"}, 500

@debts_ns.route('/summary')
class DebtSummary(Resource):
    @jwt_required()
    def get(self):
        lokasi_id = request.args.get("lokasi_id", type=int)
        try:
            summary = get_debt_summary(lokasi_id)
            return {"status": "success", "data": summary}, 200
        except Exception as e:
            logging.error(str(e))
            return {"status": "Terjadi kesalahan server"}, 500

@debts_ns.route('/debtors')
class DebtorsList(Resource):
    @jwt_required()
    def get(self):
        lokasi_id = request.args.get("lokasi_id", type=int)
        try:
            debtors = get_debtors_list(lokasi_id)
            return {"status": "success", "data": debtors}, 200
        except Exception as e:
            logging.error(str(e))
            return {"status": "Terjadi kesalahan server"}, 500