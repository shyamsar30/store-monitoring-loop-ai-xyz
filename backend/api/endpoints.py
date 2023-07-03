from flask_restx import Namespace, Resource

from backend.celery.tasks import add

namespace = Namespace("Store Report Generation", "Store Monitoring", path='/')

@namespace.route('/add')
class Add(Resource):
    def get(self):

        result = add.delay(1,2)

        return result.id