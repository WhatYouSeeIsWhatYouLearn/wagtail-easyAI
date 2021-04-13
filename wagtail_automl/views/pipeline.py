from wagtail_automl.models.pipeline import MLPipeline
from generic_chooser.views import ModelChooserViewSet, ModelChooserMixin


class MLPipelineChooserViewSet(ModelChooserViewSet):
    model = MLPipeline
    icon = 'image'
    page_title = "Choose a Pipeline"
    per_page = 10
    order_by = "title"
    edit_item_url_name = "wagtail_automl_mlpipeline_modeladmin_edit" 
