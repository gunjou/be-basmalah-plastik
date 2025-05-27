from flask_restx import Namespace, Resource, reqparse
from flask_jwt_extended import jwt_required
from .query.q_reports import get_transaction_report

reports_ns = Namespace("reports", description="Laporan transaksi")

parser = reqparse.RequestParser()
parser.add_argument("tipe", type=str, required=True, choices=("harian", "mingguan", "bulanan", "tahunan"), help="Tipe laporan")
parser.add_argument("tanggal", type=str, required=True, help="Tanggal acuan format YYYY-MM-DD")
parser.add_argument("lokasi_id", type=int, required=False)

@reports_ns.route('/transactions')
class ReportTransaction(Resource):
    @jwt_required()
    @reports_ns.expect(parser)
    def get(self):
        args = parser.parse_args()
        try:
            report = get_transaction_report(args['tipe'], args['tanggal'], args.get('lokasi_id'))
            return {"status": "success", "data": report}, 200
        except ValueError as e:
            return {"status": "error", "message": str(e)}, 400
        except Exception:
            return {"status": "error", "message": "Terjadi kesalahan server"}, 500
