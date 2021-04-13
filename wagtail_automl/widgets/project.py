from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.utils import quote

from generic_chooser.widgets import AdminChooser

from wagtail_automl.models.project import MLProject


class MLProjectChooser(AdminChooser):
    model = MLProject

    choose_one_text = _('Choose a project')
    choose_another_text = _('Choose another project')
    link_to_chosen_text = _('Edit this project')
    choose_modal_url_name = 'mlproject_chooser:choose'
    edit_item_url_name = 'wagtail_automl_mlproject_modeladmin_edit'
