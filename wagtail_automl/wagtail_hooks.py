from wagtail.core import hooks
from wagtail.contrib.modeladmin.options import modeladmin_register

from wagtail_automl.admin import MLGroup
from wagtail_automl.views.pipeline import MLPipelineChooserViewSet

@hooks.register("register_admin_viewset")
def register_site_chooser_viewset():
    return MLPipelineChooserViewSet("mlpipeline_chooser",
                                    url_prefix="mlpipeline-chooser")


# registers the MLProject and MLPipeline menu
modeladmin_register(MLGroup)
