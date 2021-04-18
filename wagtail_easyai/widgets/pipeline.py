from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.utils import quote

from generic_chooser.widgets import AdminChooser

from wagtail_easyai.models.pipeline import MLPipeline


class MLPipelineChooser(AdminChooser):
    model = MLPipeline

    choose_one_text = _('Choose a pipeline')
    choose_another_text = _('Choose another pipeline')
    link_to_chosen_text = _('Edit this pipeline')
    choose_modal_url_name = 'mlpipeline_chooser:choose'
    edit_item_url_name = "wagtail_easyai_mlpipeline_modeladmin_edit" 
