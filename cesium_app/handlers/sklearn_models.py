from .base import BaseHandler
from ..ext.sklearn_models import model_descriptions


class SklearnModelsHandler(BaseHandler):
    def get(self):
        self.success(model_descriptions)
