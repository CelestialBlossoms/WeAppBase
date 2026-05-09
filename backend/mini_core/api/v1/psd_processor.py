from flask.views import MethodView

from backend.mini_core.schema.psd_processor import (
    PSDProcessRequestSchema,
    PSDProcessResponseSchema,
)
from backend.mini_core.service.psd_processor import process_psd_file
from kit.util.blueprint import APIBlueprint


blp = APIBlueprint('psd_processor', 'psd_processor', url_prefix='/psd')


@blp.route('/process')
class PSDProcessAPI(MethodView):
    """PSD 处理 API"""

    @blp.arguments(PSDProcessRequestSchema)
    @blp.response(PSDProcessResponseSchema)
    def post(self, args: dict):
        psd_path = args.get('psd_path', 'jinjiang2.psd')
        new_text = args.get('new_text', '茅台')
        return process_psd_file(psd_path=psd_path, new_text=new_text)
