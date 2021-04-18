from django.contrib import admin
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import re_path

from wagtail.contrib.modeladmin.options import ModelAdmin, ModelAdminGroup, modeladmin_register
from wagtail.contrib.modeladmin.helpers import ButtonHelper, AdminURLHelper
from wagtail.contrib.modeladmin.views import InstanceSpecificView

from wagtail_easyai.models.project import MLProject


class MLProjectButtonHelper(ButtonHelper):
    view_button_classnames = ['button-small', 'icon', 'icon-site']

    def train_button(self, pk, classnames_add=None, classnames_exclude=None):
        if classnames_add is None:
            classnames_add = []
        if classnames_exclude is None:
            classnames_exclude = []
        classnames = self.add_button_classnames + classnames_add
        cn = self.finalise_classname(classnames, classnames_exclude)

        text = f'Train {self.verbose_name}'
        return {
            'url': self.url_helper.get_action_url("train", pk.pk,
                query_params=self.request.GET),
            'label': text,
            'classname': cn,
            'title': text,
        }

    def predict_button(self, pk, classnames_add=None, classnames_exclude=None):
        if classnames_add is None:
            classnames_add = []
        if classnames_exclude is None:
            classnames_exclude = []
        classnames = self.add_button_classnames + classnames_add
        cn = self.finalise_classname(classnames, classnames_exclude)

        text = f'Predict {self.verbose_name}'
        return {
            'url': self.url_helper.get_action_url("predict", pk.pk,
                query_params=self.request.GET),
            'label': text,
            'classname': cn,
            'title': text,
        }

    def get_buttons_for_obj(self, obj, exclude=None, classnames_add=None, classnames_exclude=None):
        btns = super().get_buttons_for_obj(obj, exclude, classnames_add, classnames_exclude)
        btns += [
                self.train_button(obj),
                self.predict_button(obj),
                ]
        return btns


class MLProjectAdminURLHelper(AdminURLHelper):
    def get_action_url(self, action, *args, **kwargs):
        query_params = kwargs.pop('query_params', None)
        url_name = self.get_action_url_name(action)
        if action in ('create', 'choose_parent', 'index'):
            url = reverse(url_name)
        else:
            url = reverse(url_name, args=args, kwargs=kwargs)

        if query_params:
            url += '?{params}'.format(params=query_params.urlencode())

        return url


class TrainView(InstanceSpecificView):
    template_name = "wagtail-easyai/train.html"
    
    def train_model(self):
        instance = self.get_context_data()["instance"]
        train_results, instance = instance.train_model()
        return train_results

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        dispatch_results = super().dispatch(request, *args, **kwargs)
        train_results = self.train_model()
        return dispatch_results 


class PredictView(InstanceSpecificView):
    template_name = "wagtail-easyai/predict.html"

    def predict(self):
        print(dir(self))
        instance = self.get_context_data()["instance"]
        predictions = instance.predict()
        print(predictions)
        return predictions 

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        dispatch_results = super().dispatch(request, *args, **kwargs)
        predict_results = self.predict()
        return dispatch_results 


class MLProjectAdmin(ModelAdmin):
    menu_label = "Projects"
    menu_icon = 'pilcrow'

    model = MLProject
    inspect_view_enabled=True
    inspect_template_name = "wagtail-easyai/inspect.html"

    train_view_class = TrainView
    predict_view_class = PredictView
    url_helper_class = MLProjectAdminURLHelper
    button_helper_class = MLProjectButtonHelper

    list_display = ('title',)
    list_filter = ('title',)
    search_fields = ('title', 'data')

    def get_admin_urls_for_registration(self):
        urls = super().get_admin_urls_for_registration()
        urls += (
            re_path(
                self.url_helper.get_action_url_pattern('predict'),
                self.predict_view,
                name=self.url_helper.get_action_url_name('predict')
            ),
            re_path(
                self.url_helper.get_action_url_pattern('train'),
                self.train_view,
                name=self.url_helper.get_action_url_name('train')
            ),
        )

        return urls

    def predict_view(self, request, instance_pk):
        kwargs = {'model_admin': self, "instance_pk": instance_pk}
        view_class = self.predict_view_class
        return view_class.as_view(**kwargs)(request)

    def train_view(self, request, instance_pk):
        kwargs = {"model_admin": self, "instance_pk": instance_pk}
        view_class = self.train_view_class
        return view_class.as_view(**kwargs)(request)


class MLGroup(ModelAdminGroup):
    menu_label = 'Machine learning'
    menu_icon = 'folder-open-inverse'
    menu_order = 200

    items = (MLProjectAdmin,)
