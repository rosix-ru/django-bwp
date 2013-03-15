# -*- coding: utf-8 -*-
"""
###############################################################################
# Copyright 2013 Grigoriy Kramarenko.
###############################################################################
# This file is part of BWP.
#
#    BWP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    BWP is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with BWP.  If not, see <http://www.gnu.org/licenses/>.
#
# Этот файл — часть BWP.
#
#   BWP - свободная программа: вы можете перераспространять ее и/или
#   изменять ее на условиях Стандартной общественной лицензии GNU в том виде,
#   в каком она была опубликована Фондом свободного программного обеспечения;
#   либо версии 3 лицензии, либо (по вашему выбору) любой более поздней
#   версии.
#
#   BWP распространяется в надежде, что она будет полезной,
#   но БЕЗО ВСЯКИХ ГАРАНТИЙ; даже без неявной гарантии ТОВАРНОГО ВИДА
#   или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ. Подробнее см. в Стандартной
#   общественной лицензии GNU.
#
#   Вы должны были получить копию Стандартной общественной лицензии GNU
#   вместе с этой программой. Если это не так, см.
#   <http://www.gnu.org/licenses/>.
###############################################################################
"""
from django.utils.translation import ugettext as _
from django.db.models.base import ModelBase
from django.core.exceptions import ImproperlyConfigured
from django.utils.text import capfirst

from bwp.models import ModelBWP
from bwp.forms import BWPAuthenticationForm
from bwp.conf import settings


class AlreadyRegistered(Exception):
    pass

class NotRegistered(Exception):
    pass

class BWPSite(object):
    """ Класс объекта для регистрации моделей в BWP из одного экземпляра """

    def __init__(self, name='bwp', app_name='bwp'):
        self._registry = {} # model_class class -> bwp_class instance
        self.name = name
        self.app_name = app_name

    def register(self, model_or_iterable, bwp_class=None, **options):
        """
        Registers the given model(s) with the given bwp class.

        The model(s) should be Model classes, not instances.

        If an bwp class isn't given, it will use ModelBWP (the default
        bwp options). If keyword arguments are given -- e.g., list_display --
        they'll be applied as options to the bwp class.

        If a model is already registered, this will raise AlreadyRegistered.

        If a model is abstract, this will raise ImproperlyConfigured.
        """
        if not bwp_class:
            bwp_class = ModelBWP

        # Don't import the humongous validation code unless required
        if bwp_class and settings.DEBUG:
            from bwp.validation import validate
        else:
            validate = lambda model, bwpclass: None
        validate = lambda model, bwpclass: None

        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
            if model._meta.abstract:
                raise ImproperlyConfigured('The model %s is abstract, so it '
                      'cannot be registered with bwp.' % model.__name__)

            if model in self._registry:
                raise AlreadyRegistered('The model %s is already registered' % model.__name__)

            # If we got **options then dynamically construct a subclass of
            # bwp_class with those **options.
            if options:
                # For reasons I don't quite understand, without a __module__
                # the created class appears to "live" in the wrong place,
                # which causes issues later on.
                options['__module__'] = __name__
                bwp_class = type("%sBWP" % model.__name__, (bwp_class,), options)

            # Validate (which might be a no-op)
            validate(bwp_class, model)

            # Instantiate the bwp class to save in the registry
            self._registry[model] = bwp_class(model, self)

    def unregister(self, model_or_iterable):
        """
        Unregisters the given model(s).

        If a model isn't already registered, this will raise NotRegistered.
        """
        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
            if model not in self._registry:
                raise NotRegistered('The model %s is not registered' % model.__name__)
            del self._registry[model]

    def has_permission(self, request):
        """
        Returns True if the given HttpRequest has permission to view
        *at least one* page in the bwp site.
        """
        return request.user.is_active and request.user.is_staff

    def check_dependencies(self):
        """
        Check that all things needed to run the bwp have been correctly installed.

        The default implementation checks that LogEntry, ContentType and the
        auth context processor are installed.
        """
        from django.contrib.contenttypes.models import ContentType

        if 'quickapi' not in settings.INSTALLED_APPS:
            raise ImproperlyConfigured("Put 'quickapi' in your "
                "INSTALLED_APPS setting in order to use the bwp application.")

        #~ if 'django.contrib.admin' in settings.INSTALLED_APPS:
            #~ raise ImproperlyConfigured("Remove 'django.contrib.admin' in your "
                #~ "INSTALLED_APPS setting in order to use the bwp application.")
        if not ContentType._meta.installed:
            raise ImproperlyConfigured("Put 'django.contrib.contenttypes' in "
                "your INSTALLED_APPS setting in order to use the bwp application.")
        if not ('django.contrib.auth.context_processors.auth' in settings.TEMPLATE_CONTEXT_PROCESSORS or
            'django.core.context_processors.auth' in settings.TEMPLATE_CONTEXT_PROCESSORS):
            raise ImproperlyConfigured("Put 'django.contrib.auth.context_processors.auth' "
                "in your TEMPLATE_CONTEXT_PROCESSORS setting in order to use the bwp application.")

    @property
    def bwp_dict(self):
        return dict([ (str(model._meta), model_bwp) \
            for model, model_bwp in self._registry.items()
        ])

    def app_dict(self, request):
        app_dict = {}
        for model, model_bwp in self._registry.items():
            app_label = model._meta.app_label
            has_module_perms = request.user.has_module_perms(app_label)

            if has_module_perms:
                perms = model_bwp.get_model_perms(request)

                if True in perms.values():
                    info = (app_label, model._meta.module_name)
                    model_dict = {
                        'id': str(model._meta),
                        'html_id': str(model._meta).replace('.','-'),
                        'meta': model._meta,
                        'name': capfirst(model._meta.verbose_name_plural),
                        'perms': perms,
                        'bwp': model_bwp,
                    }

                    if app_label in app_dict:
                        app_dict[app_label]['models'].append(model_dict)
                    else:
                        app_dict[app_label] = {
                            'name': app_label.title(),
                            'has_module_perms': has_module_perms,
                            'models': [model_dict],
                        }
        return app_dict

    def app_list(self, request):
        # Sort the apps alphabetically.
        app_list = self.app_dict(request).values()
        app_list.sort(key=lambda x: x['name'])

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])

        return app_list


# This global object represents the default bwp site, for the common case.
# You can instantiate BWPSite in your own code to create a custom bwp site.
site = BWPSite()