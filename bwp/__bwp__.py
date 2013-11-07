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
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from bwp.sites import site
from bwp.models import ModelBWP, ComposeBWP, LogEntry,\
        GlobalUserSettings, TempUploadFile, ManyToManyBWP
from bwp.contrib.users.models import User, Group, Permission

label_id = _('ID')
label_pk = _('PK')

class LogEntryAdmin(ModelBWP):
    list_display = ('action_time', 'user', '__unicode__', 'id')
    search_fields = ('user__username', 'object_repr', 'change_message')
    allow_clone = False
site.register(LogEntry, LogEntryAdmin)

class GlobalUserSettingsAdmin(ModelBWP):
    list_display = ('__unicode__', 'id')
site.register(GlobalUserSettings, GlobalUserSettingsAdmin)

class TempUploadFileAdmin(ModelBWP):
    list_display = ('__unicode__', 'user', 'created')
site.register(TempUploadFile, TempUploadFileAdmin)
