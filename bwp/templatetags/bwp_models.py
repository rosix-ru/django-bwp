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
from django.template import Library, Node, TemplateSyntaxError
from bwp.conf import settings
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.utils.text import capfirst

register = Library()


@register.filter
def ordering(objects, ordering):
    if isinstance(ordering, (str, unicode)):
        ordering = [ x.strip(' ') for x in ordering.split(',')]
    return objects.order_by(*ordering)

@register.filter
def filtering(objects, args):
    def get_boolean(bit):
        if bit == u'False':
            return False
        if bit == u'True':
            return True
        return bit
    if isinstance(args, (str, unicode)):
        args = [ x.strip(' ') for x in args.split(',')]
        args = [ x.split('=') for x in args ]
        args = [ {x[0]: get_boolean(x[1])} for x in args ]
        print args

    orm_lookup = [ Q(**x) for x in args ]
    return objects.filter(*orm_lookup)

@register.filter
def sums(objects, attrs):
    if isinstance(attrs, (str, unicode)):
        attrs = [ x.strip(' ') for x in attrs.split(',')]

    def get_value(attr):
        if callable(attr):
            return attr()
        return attr

    SUM = []
    for a in attrs:
        SUM.append(sum([ get_value(getattr(x, a)) for x in objects ]))

    return SUM

class ChildModelNode(Node):
    def __init__(self, target, model, lookout, var_name):
        self.target  = target
        self.model    = model
        self.lookout  = lookout+'__in'
        self.var_name = var_name

    def render(self, context):
        objects = self.target.resolve(context, True)
        objects = self.model.objects.filter(Q(**{self.lookout: [x.pk for x in objects ]}))
        context[self.var_name] = objects
        return ''


@register.tag
def get_child_model_objects(parser, token):
    """ Получение объектов дочерней модели из списка объектов родительской
        
        Для такой схемы моделей:
            Workshift
                Invoice.workshift = Workshift
                    Order.invoice = Invoice
                        Spec.order = Order

        workshift_objects = Workshift.objects.filter(**kwargs)

        этом тэгом можно получить все спецификации за несколько смен в
        отдельную переменную, когда необходимо это сделатьпрямо в шаблоне

        {% get_child_model_objects workshift_objects \
        project.contrib.sales.models.Spec order__invoice__workshift \
        as new_var_name %}
        
        new_var_name == Spec.objects.filter(
            order__invoice__workshift__in=[ x.pk for x in workshift_objects])

    """
    bits = token.contents.split(None, 6)
    if len(bits) != 6:
        raise TemplateSyntaxError("'get_child_model_objects' tag takes five arguments")
    objects = parser.compile_filter(bits[1])
    model_path = bits[2]
    model_path = model_path.split('.')
    try:
        module = __import__('.'.join(model_path[:-1]), fromlist=[''])
        model = getattr(module, model_path[-1])
    except Exception as e:
        print e
        raise TemplateSyntaxError("second argument to 'get_child_model_objects' tag must be 'path.to.model'")

    lookout = bits[3]

    if bits[4] != 'as':
        raise TemplateSyntaxError("next-to-last argument to 'regroup' tag must"
                                  " be 'as'")
    var_name = bits[5]

    return ChildModelNode(objects, model, lookout, var_name)




