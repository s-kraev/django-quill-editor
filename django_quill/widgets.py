from collections.abc import Mapping

from django import forms
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.renderers import get_default_renderer
from django.forms.utils import flatatt
from django.utils.encoding import force_str
from django.utils.functional import Promise
from django.utils.safestring import mark_safe

from .config import DEFAULT_CONFIG, MEDIA_JS, MEDIA_CSS

__all__ = (
    "LazyEncoder",
    "QuillWidget",
)


class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_str(obj)
        return super(LazyEncoder, self).default(obj)


json_encode = LazyEncoder().encode


class QuillWidget(forms.Textarea):
    template_name = 'django_quill/widget.html'

    class Media:
        js = MEDIA_JS
        css = {"all": MEDIA_CSS}

    def __init__(self, config_name="default", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = DEFAULT_CONFIG.copy()
        configs = getattr(settings, "QUILL_CONFIGS", None)
        if configs:
            if isinstance(configs, Mapping):
                if config_name in configs:
                    config = configs[config_name]
                    if not isinstance(config, Mapping):
                        raise ImproperlyConfigured(
                            'QUILL_CONFIGS["%s"] setting must be a Mapping object'
                            % config_name
                        )
                    self.config.update(config)
                else:
                    raise ImproperlyConfigured(
                        'No configuration named "%s" found in your QUILL_CONFIGS'
                        % config_name
                    )
            else:
                raise ImproperlyConfigured(
                    "QUILL_CONFIGS settings must be a Mapping object"
                )

    def get_context(self, name, value, attrs):
        context = super(QuillWidget, self).get_context(name, value, attrs)
        context['widget']['config'] = json_encode(self.config)
        return context

    def format_value(self, value):
        return json_encode(value)

