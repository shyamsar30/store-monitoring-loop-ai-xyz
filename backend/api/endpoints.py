import time
from flask import request, send_file
from flask_restx import Namespace, Resource
from celery.result import AsyncResult

from backend.celery.tasks import generate_report
from backend.config import Config

namespace = Namespace("Store Report Generation", "Store Monitoring", path='/')

@namespace.route('/trigger_report')
class TriggerReportView(Resource):
    def get(self):

        result = generate_report.delay(Config.CURRENT_TIMESTAMP_UTC)
        return result.id
    
@namespace.route('/get_report')
class GetReportView(Resource):

    @namespace.param('report_id')
    def get(self):
        result = AsyncResult(request.args.get('report_id'))
        if result.state == "PENDING":
            response = "RUNNING"
        else:
            response = send_file('data.csv', as_attachment='data.csv', download_name='data.csv')
        return response