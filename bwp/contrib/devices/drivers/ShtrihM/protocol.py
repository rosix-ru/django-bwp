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

# Протокол работы ККТ

VERSION = (1, 1)
VERSION_DATE = (2012, 05, 28)
__version__ = '.'.join([ str(x) for x in VERSION ])

""" Команды ККТ
        Разрядность денежных величин
  Все суммы в данном разделе – целые величины, указанные в «мде». МДЕ –
минимальная денежная единица. С 01.01.1998 в Российской Федерации 1 МДЕ
равна 1 копейке (до 01.01.1998 1 МДЕ была равна 1 рублю).

        Формат передачи значений
  Все числовые величины передаются в двоичном формате, если не указано
другое. Первым передается самый младший байт, последним самый старший
байт.
  При передаче даты (3 байта) сначала передаѐтся число (1 байт – ДД),
затем месяц (2 байта – ММ), и последним – год (1 байт – ГГ).
  При передаче времени (3 байта) первым байтом передаются часы (1 байт
– ЧЧ), затем минуты (2 байта – ММ), и последними передаются секунды (1
байт – СС).

        Ответы и коды ошибок
  Ответное сообщение содержит корректную информацию, если код ошибки (второй
байт в ответном сообщении) 0. Если код ошибки не 0, передается только код команды и код
ошибки – 2 байта.
"""
KKT_COMMANDS = {
    0x01: u'Запрос дампа',
    0x02: u'Запрос данных',
    0x03: u'Прерывание выдачи данных',
    0x0D: u'Фискализация (перерегистрация) с длинным РНМ',
    0x0E: u'Ввод длинного заводского номера',
    0x0F: u'Запрос длинного заводского номера и длинного РНМ',

    0x10: u'Короткий запрос состояния ФР',
    0x11: u'Запрос состояния ФР',
    0x12: u'Печать жирной строки',
    0x13: u'Гудок',
    0x14: u'Установка параметров обмена',
    0x15: u'Чтение параметров обмена',
    0x16: u'Технологическое обнуление',
    0x17: u'Печать строки',
    0x18: u'Печать заголовка документа',
    0x19: u'Тестовый прогон',
    0x1A: u'Запрос денежного регистра',
    0x1B: u'Запрос операционного регистра',
    0x1C: u'Запись лицензии',
    0x1D: u'Чтение лицензии',
    0x1E: u'Запись таблицы',
    0x1F: u'Чтение таблицы',

    0x20: u'Запись положения десятичной точки',
    0x21: u'Программирование времени',
    0x22: u'Программирование даты',
    0x23: u'Подтверждение программирования даты',
    0x24: u'Инициализация таблиц начальными значениями',
    0x25: u'Отрезка чека',
    0x26: u'Прочитать параметры шрифта',
    0x27: u'Общее гашение',
    0x28: u'Открыть денежный ящик',
    0x29: u'Протяжка',
    0x2A: u'Выброс подкладного документа',
    0x2B: u'Прерывание тестового прогона',
    0x2C: u'Снятие показаний операционных регистров',
    0x2D: u'Запрос структуры таблицы',
    0x2E: u'Запрос структуры поля',
    0x2F: u'Печать строки данным шрифтом',

    0x40: u'Суточный отчет без гашения',
    0x41: u'Суточный отчет с гашением',
    0x42: u'Отчёт по секциям',
    0x43: u'Отчёт по налогам',
    
    0x50: u'Внесение',
    0x51: u'Выплата',
    0x52: u'Печать клише',
    0x53: u'Конец документа',
    0x53: u'Печать рекламного текста',

    0x60: u'Ввод заводского номера',
    0x61: u'Инициализация ФП',
    0x62: u'Запрос суммы записей в ФП',
    0x63: u'Запрос даты последней записи в ФП',
    0x64: u'Запрос диапазона дат и смен',
    0x65: u'Фискализация (перерегистрация)',
    0x66: u'Фискальный отчет по диапазону дат',
    0x67: u'Фискальный отчет по диапазону смен',
    0x68: u'Прерывание полного отчета',
    0x69: u'Чтение параметров фискализации (перерегистрации)',

    0x70: u'Открыть фискальный подкладной документ',
    0x71: u'Открыть стандартный фискальный подкладной документ',
    0x72: u'Формирование операции на подкладном документе',
    0x73: u'Формирование стандартной операции на подкладном документе',
    0x74: u'Формирование скидки/надбавки на подкладном документе',
    0x75: u'Формирование стандартной скидки/надбавки на подкладном документе',
    0x76: u'Формирование закрытия чека на подкладном документе',
    0x77: u'Формирование стандартного закрытия чека на подкладном документе',
    0x78: u'Конфигурация подкладного документа',
    0x79: u'Установка стандартной конфигурации подкладного документа',
    0x7A: u'Заполнение буфера подкладного документа нефискальной информацией',
    0x7B: u'Очистка строки буфера подкладного документа от нефискальной информации',
    0x7C: u'Очистка всего буфера подкладного документа от нефискальной информации',
    0x7D: u'Печать подкладного документа',
    0x7E: u'Общая конфигурация подкладного документа',

    0x80: u'Продажа',
    0x81: u'Покупка',
    0x82: u'Возврат продажи',
    0x83: u'Возврат покупки',
    0x84: u'Сторно',
    0x85: u'Закрытие чека',
    0x86: u'Скидка',
    0x87: u'Надбавка',
    0x88: u'Аннулирование чека',
    0x89: u'Подытог чека',
    0x8A: u'Сторно скидки',
    0x8B: u'Сторно надбавки',
    0x8C: u'Повтор документа',
    0x8D: u'Открыть чек',

    0x90: u'Формирование чека отпуска нефтепродуктов в режиме предоплаты заданной дозы',
    0x91: u'Формирование чека отпуска нефтепродуктов в режиме предоплаты на заданную сумму',
    0x92: u'Формирование чека коррекции при неполном отпуске нефтепродуктов',
    0x93: u'Задание дозы РК в миллилитрах',
    0x94: u'Задание дозы РК в денежных единицах',
    0x95: u'Продажа нефтепродуктов',
    0x96: u'Останов РК',
    0x97: u'Пуск РК',
    0x98: u'Сброс РК',
    0x99: u'Сброс всех ТРК',
    0x9A: u'Задание параметров РК',
    0x9B: u'Считать литровый суммарный счетчик',

    0x9E: u'Запрос текущей дозы РК',
    0x9F: u'Запрос состояния РК',

    0xA0: u'Отчет ЭКЛЗ по отделам в заданном диапазоне дат',
    0xA1: u'Отчет ЭКЛЗ по отделам в заданном диапазоне номеров смен',
    0xA2: u'Отчет ЭКЛЗ по закрытиям смен в заданном диапазоне дат',
    0xA3: u'Отчет ЭКЛЗ по закрытиям смен в заданном диапазоне номеров смен',
    0xA4: u'Итоги смены по номеру смены ЭКЛЗ',
    0xA5: u'Платежный документ из ЭКЛЗ по номеру КПК',
    0xA6: u'Контрольная лента из ЭКЛЗ по номеру смены',
    0xA7: u'Прерывание полного отчета ЭКЛЗ или контрольной ленты ЭКЛЗ или печати платежного документа ЭКЛЗ',
    0xA8: u'Итог активизации ЭКЛЗ',
    0xA9: u'Активизация ЭКЛЗ',
    0xAA: u'Закрытие архива ЭКЛЗ',
    0xAB: u'Запрос регистрационного номера ЭКЛЗ',
    0xAC: u'Прекращение ЭКЛЗ',
    0xAD: u'Запрос состояния по коду 1 ЭКЛЗ',
    0xAE: u'Запрос состояния по коду 2 ЭКЛЗ',
    0xAF: u'Тест целостности архива ЭКЛЗ',

    0xB0: u'Продолжение печати',
    0xB1: u'Запрос версии ЭКЛЗ',
    0xB2: u'Инициализация архива ЭКЛЗ',
    0xB3: u'Запрос данных отчёта ЭКЛЗ',
    0xB4: u'Запрос контрольной ленты ЭКЛЗ',
    0xB5: u'Запрос документа ЭКЛЗ',
    0xB6: u'Запрос отчёта ЭКЛЗ по отделам в заданном диапазоне дат',
    0xB7: u'Запрос отчёта ЭКЛЗ по отделам в заданном диапазоне номеров смен',
    0xB8: u'Запрос отчёта ЭКЛЗ по закрытиям смен в заданном диапазоне дат',
    0xB9: u'Запрос отчёта ЭКЛЗ по закрытиям смен в заданном диапазоне номеров смен',
    0xBA: u'Запрос в ЭКЛЗ итогов смены по номеру смены',
    0xBB: u'Запрос итога активизации ЭКЛЗ',
    0xBC: u'Вернуть ошибку ЭКЛЗ',

    0xC0: u'Загрузка графики',
    0xC1: u'Печать графики',
    0xC2: u'Печать штрих-кода',
    0xC3: u'Загрузка расширенной графики',
    0xC4: u'Печать расширенной графики',
    0xC5: u'Печать линии',
    0xC6: u'Суточный отчет с гашением в буфер',
    0xC7: u'Распечатать отчет из буфера',
    0xC8: u'Запрос количества строк в буфере печати',
    0xC9: u'Получить строку буфера печати ',
    0xCA: u'Очистить буфер печати ',

    0xD0: u'Запрос состояния ФР IBM длинный',
    0xD1: u'Коды ошибок',

    0xDD: u'Загрузка данных',
    0xDE: u'Печать многомерного штрих-кода',

    0xE0: u'Открыть смену',
    0xE1: u'Допечатать ПД',
    0xE2: u'Открыть нефискальный документ',
    0xE3: u'Закрыть нефискальный документ',
    0xE4: u'Печать Реквизита',
    0xE5: u'Запрос состояния купюроприемника',
    0xE6: u'Запрос регистров купюроприемника',
    0xE7: u'Отчет по купюроприемнику',
    0xE8: u'Оперативный отчет НИ',

    0xF0: u'Управление заслонкой',
    0xF1: u'Выдать чек',

    0xF3: u'Установить пароль ЦТО',

    0xFC: u'Получить тип устройства',
    0xFD: u'Управление портом дополнительного внешнего устройства',
}

""" Коды ошибок
  В первом параметре значений указывается источник возникновения ошибки:
фискальная память (ФП), электронная контрольная лента защищѐнная
(ЭКЛЗ) или сама ККТ.
"""
BUGS = {
    0x00: (u'ФП', u'Ошибок нет'),
    0x01: (u'ФП', u'Неисправен накопитель ФП 1, ФП 2 или часы'),
    0x02: (u'ФП', u'Отсутствует ФП 1'),
    0x03: (u'ФП', u'Отсутствует ФП 2'),
    0x04: (u'ФП', u'Некорректные параметры в команде обращения к ФП'),
    0x05: (u'ФП', u'Нет запрошенных данных'),
    0x06: (u'ФП', u'ФП в режиме вывода данных'),
    0x07: (u'ФП', u'Некорректные параметры в команде для данной реализации ФП'),
    0x08: (u'ФП', u'Команда не поддерживается в данной реализации ФП'),
    0x09: (u'ФП', u'Некорректная длина команды'),
    0x0A: (u'ФП', u'Формат данных не BCD'),
    0x0B: (u'ФП', u'Неисправна ячейка памяти ФП при записи итога'),

    0x11: (u'ФП', u'Не введена лицензия'),
    0x12: (u'ФП', u'Заводской номер уже введен'),
    0x13: (u'ФП', u'Текущая дата меньше даты последней записи в ФП'),
    0x14: (u'ФП', u'Область сменных итогов ФП переполнена'),
    0x15: (u'ФП', u'Смена уже открыта'),
    0x16: (u'ФП', u'Смена не открыта'),
    0x17: (u'ФП', u'Номер первой смены больше номера последней смены'),
    0x18: (u'ФП', u'Дата первой смены больше даты последней смены'),
    0x19: (u'ФП', u'Нет данных в ФП'),
    0x1A: (u'ФП', u'Область перерегистраций в ФП переполнена'),
    0x1B: (u'ФП', u'Заводской номер не введен'),
    0x1C: (u'ФП', u'В заданном диапазоне есть поврежденная запись'),
    0x1D: (u'ФП', u'Повреждена последняя запись сменных итогов'),
    0x1E: (u'ФП', u'Область перерегистраций ФП переполнена'),
    0x1F: (u'ФП', u'Отсутствует память регистров'),

    0x20: (u'ФП', u'Переполнение денежного регистра при добавлении'),
    0x21: (u'ФП', u'Вычитаемая сумма больше содержимого денежного регистра'),
    0x22: (u'ФП', u'Неверная дата'),
    0x23: (u'ФП', u'Нет записи активизации'),
    0x24: (u'ФП', u'Область активизаций переполнена'),
    0x25: (u'ФП', u'Нет активизации с запрашиваемым номером'),
    0x26: (u'ФП', u'В ФП присутствует 3 или более битых записей сменных итогов'),
    0x27: (u'ФП', u'Признак несовпадения КС, з/н, перерегистраций или активизаций'),

    0x2B: (u'ККТ', u'Невозможно отменить предыдущую команду'),
    0x2C: (u'ККТ', u'Обнулѐнная касса (повторное гашение невозможно)'),
    0x2D: (u'ККТ', u'Сумма чека по секции меньше суммы сторно'),
    0x2E: (u'ККТ', u'В ККТ нет денег для выплаты'),

    0x30: (u'ККТ', u'ККТ заблокирован, ждет ввода пароля налогового инспектора'),

    0x32: (u'ККТ', u'Требуется выполнение общего гашения'),
    0x33: (u'ККТ', u'Некорректные параметры в команде'),
    0x34: (u'ККТ', u'Нет данных'),
    0x35: (u'ККТ', u'Некорректный параметр при данных настройках'),
    0x36: (u'ККТ', u'Некорректные параметры в команде для данной реализации ККТ'),
    0x37: (u'ККТ', u'Команда не поддерживается в данной реализации ККТ'),
    0x38: (u'ККТ', u'Ошибка в ПЗУ'),
    0x39: (u'ККТ', u'Внутренняя ошибка ПО ККТ'),
    0x3A: (u'ККТ', u'Переполнение накопления по надбавкам в смене'),
    0x3B: (u'ККТ', u'Переполнение накопления в смене'),
    0x3C: (u'ККТ', u'ЭКЛЗ: неверный регистрационный номер'),
    0x3D: (u'ККТ', u'Смена не открыта – операция невозможна'),
    0x3E: (u'ККТ', u'Переполнение накопления по секциям в смене'),
    0x3F: (u'ККТ', u'Переполнение накопления по скидкам в смене'),

    0x40: (u'ККТ', u'Переполнение диапазона скидок'),
    0x41: (u'ККТ', u'Переполнение диапазона оплаты наличными'),
    0x42: (u'ККТ', u'Переполнение диапазона оплаты типом 2'),
    0x43: (u'ККТ', u'Переполнение диапазона оплаты типом 3'),
    0x44: (u'ККТ', u'Переполнение диапазона оплаты типом 4'),
    0x45: (u'ККТ', u'Cумма всех типов оплаты меньше итога чека'),
    0x46: (u'ККТ', u'Не хватает наличности в кассе'),
    0x47: (u'ККТ', u'Переполнение накопления по налогам в смене'),
    0x48: (u'ККТ', u'Переполнение итога чека'),
    0x49: (u'ККТ', u'Операция невозможна в открытом чеке данного типа'),
    0x4A: (u'ККТ', u'Открыт чек – операция невозможна'),
    0x4B: (u'ККТ', u'Буфер чека переполнен'),
    0x4C: (u'ККТ', u'Переполнение накопления по обороту налогов в смене'),
    0x4D: (u'ККТ', u'Вносимая безналичной оплатой сумма больше суммы чека'),
    0x4E: (u'ККТ', u'Смена превысила 24 часа'),
    0x4F: (u'ККТ', u'Неверный пароль'),

    0x50: (u'ККТ', u'Идет печать предыдущей команды'),
    0x51: (u'ККТ', u'Переполнение накоплений наличными в смене'),
    0x52: (u'ККТ', u'Переполнение накоплений по типу оплаты 2 в смене'),
    0x53: (u'ККТ', u'Переполнение накоплений по типу оплаты 3 в смене'),
    0x54: (u'ККТ', u'Переполнение накоплений по типу оплаты 4 в смене'),
    0x55: (u'ККТ', u'Чек закрыт – операция невозможна'),
    0x56: (u'ККТ', u'Нет документа для повтора'),
    0x57: (u'ККТ', u'ЭКЛЗ: количество закрытых смен не совпадает с ФП'),
    0x58: (u'ККТ', u'Ожидание команды продолжения печати'),
    0x59: (u'ККТ', u'Документ открыт другим оператором'),
    0x5A: (u'ККТ', u'Скидка превышает накопления в чеке'),
    0x5B: (u'ККТ', u'Переполнение диапазона надбавок'),
    0x5C: (u'ККТ', u'Понижено напряжение 24В'),
    0x5D: (u'ККТ', u'Таблица не определена'),
    0x5E: (u'ККТ', u'Некорректная операция'),
    0x5F: (u'ККТ', u'Отрицательный итог чека'),

    0x60: (u'ККТ', u'Переполнение при умножении'),
    0x61: (u'ККТ', u'Переполнение диапазона цены'),
    0x62: (u'ККТ', u'Переполнение диапазона количества'),
    0x63: (u'ККТ', u'Переполнение диапазона отдела'),
    0x64: (u'ККТ', u'ФП отсутствует'),
    0x65: (u'ККТ', u'Не хватает денег в секции'),
    0x66: (u'ККТ', u'Переполнение денег в секции'),
    0x67: (u'ККТ', u'Ошибка связи с ФП'),
    0x68: (u'ККТ', u'Не хватает денег по обороту налогов'),
    0x69: (u'ККТ', u'Переполнение денег по обороту налогов'),
    0x6A: (u'ККТ', u'Ошибка питания в момент ответа по I2C'),
    0x6B: (u'ККТ', u'Нет чековой ленты'),
    0x6C: (u'ККТ', u'Нет контрольной ленты'),
    0x6D: (u'ККТ', u'Не хватает денег по налогу'),
    0x6E: (u'ККТ', u'Переполнение денег по налогу'),
    0x6F: (u'ККТ', u'Переполнение по выплате в смене'),

    0x70: (u'ККТ', u'Переполнение ФП'),
    0x71: (u'ККТ', u'Ошибка отрезчика'),
    0x72: (u'ККТ', u'Команда не поддерживается в данном подрежиме'),
    0x73: (u'ККТ', u'Команда не поддерживается в данном режиме'),
    0x74: (u'ККТ', u'Ошибка ОЗУ'),
    0x75: (u'ККТ', u'Ошибка питания'),
    0x76: (u'ККТ', u'Ошибка принтера: нет импульсов с тахогенератора'),
    0x77: (u'ККТ', u'Ошибка принтера: нет сигнала с датчиков'),
    0x78: (u'ККТ', u'Замена ПО'),
    0x79: (u'ККТ', u'Замена ФП'),
    0x7A: (u'ККТ', u'Поле не редактируется'),
    0x7B: (u'ККТ', u'Ошибка оборудования'),
    0x7C: (u'ККТ', u'Не совпадает дата'),
    0x7D: (u'ККТ', u'Неверный формат даты'),
    0x7E: (u'ККТ', u'Неверное значение в поле длины'),
    0x7F: (u'ККТ', u'Переполнение диапазона итога чека'),

    0x80: (u'ККТ', u'Ошибка связи с ФП'),
    0x81: (u'ККТ', u'Ошибка связи с ФП'),
    0x82: (u'ККТ', u'Ошибка связи с ФП'),
    0x83: (u'ККТ', u'Ошибка связи с ФП'),
    0x84: (u'ККТ', u'Переполнение наличности'),
    0x85: (u'ККТ', u'Переполнение по продажам в смене'),
    0x86: (u'ККТ', u'Переполнение по покупкам в смене'),
    0x87: (u'ККТ', u'Переполнение по возвратам продаж в смене'),
    0x88: (u'ККТ', u'Переполнение по возвратам покупок в смене'),
    0x89: (u'ККТ', u'Переполнение по внесению в смене'),
    0x8A: (u'ККТ', u'Переполнение по надбавкам в чеке'),
    0x8B: (u'ККТ', u'Переполнение по скидкам в чеке'),
    0x8C: (u'ККТ', u'Отрицательный итог надбавки в чеке'),
    0x8D: (u'ККТ', u'Отрицательный итог скидки в чеке'),
    0x8E: (u'ККТ', u'Отрицательный итог скидки в чеке'),
    0x8F: (u'ККТ', u'Касса не фискализирована'),

    0x90: (u'ККТ', u'Поле превышает размер, установленный в настройках'),
    0x91: (u'ККТ', u'Выход за границу поля печати при данных настройках шрифта'),
    0x92: (u'ККТ', u'Наложение полей'),
    0x93: (u'ККТ', u'Восстановление ОЗУ прошло успешно'),
    0x94: (u'ККТ', u'Исчерпан лимит операций в чеке'),
    0x95: (u'ЭКЛЗ', u'Неизвестная ошибка ЭКЛЗ'),

    0xA0: (u'ККТ', u'Ошибка связи с ЭКЛЗ'),
    0xA1: (u'ККТ', u'ЭКЛЗ отсутствует'),
    0xA2: (u'ЭКЛЗ', u'ЭКЛЗ: Некорректный формат или параметр команды'),
    0xA3: (u'ЭКЛЗ', u'Некорректное состояние ЭКЛЗ'),
    0xA4: (u'ЭКЛЗ', u'Авария ЭКЛЗ'),
    0xA5: (u'ЭКЛЗ', u'Авария КС в составе ЭКЛЗ'),
    0xA6: (u'ЭКЛЗ', u'Исчерпан временной ресурс ЭКЛЗ'),
    0xA7: (u'ЭКЛЗ', u'ЭКЛЗ переполнена'),
    0xA8: (u'ЭКЛЗ', u'ЭКЛЗ: Неверные дата и время'),
    0xA9: (u'ЭКЛЗ', u'ЭКЛЗ: Нет запрошенных данных'),
    0xAA: (u'ЭКЛЗ', u'Переполнение ЭКЛЗ (отрицательный итог документа)'),

    0xB0: (u'ККТ', u'ЭКЛЗ: Переполнение в параметре количество'),
    0xB1: (u'ККТ', u'ЭКЛЗ: Переполнение в параметре сумма'),
    0xB2: (u'ККТ', u'ЭКЛЗ: Уже активизирована'),

    0xC0: (u'ККТ', u'Контроль даты и времени (подтвердите дату и время)'),
    0xC1: (u'ККТ', u'ЭКЛЗ: суточный отчѐт с гашением прервать нельзя'),
    0xC2: (u'ККТ', u'Превышение напряжения в блоке питания'),
    0xC3: (u'ККТ', u'Несовпадение итогов чека и ЭКЛЗ'),
    0xC4: (u'ККТ', u'Несовпадение номеров смен'),
    0xC5: (u'ККТ', u'Буфер подкладного документа пуст'),
    0xC6: (u'ККТ', u'Подкладной документ отсутствует'),
    0xC7: (u'ККТ', u'Поле не редактируется в данном режиме'),
    0xC8: (u'ККТ', u'Отсутствуют импульсы от таходатчика'),
    0xC9: (u'ККТ', u'Перегрев печатающей головки'),
    0xCA: (u'ККТ', u'Температура вне условий эксплуатации'),
}

""" Режимы ККТ
  Режим ККМ – одно из состояний ККМ, в котором она может находиться.
Режимы ККМ описываются одним байтом: младший полубайт – номер режима,
старший полубайт – битовое поле, определяющее статус режима (для режимов
8, 13 и 14). Номера и назначение режимов и статусов:
"""
KKT_MODES = {
    0:  (u'Принтер в рабочем режиме.', {}),
    1:  (u'Выдача данных.', {}),
    2:  (u'Открытая смена, 24 часа не кончились.', {}),
    3:  (u'Открытая смена, 24 часа кончились.', {}),
    4:  (u'Закрытая смена.', {}),
    5:  (u'Блокировка по неправильному паролю налогового инспектора.', {}),
    6:  (u'Ожидание подтверждения ввода даты.', {}),
    7:  (u'Разрешение изменения положения десятичной точки.', {}),
    8:  (u'Открытый документ:', {
            0:  u'Продажа.',
            1:  u'Покупка.',
            2:  u'Возврат продажи.',
            3:  u'Возврат покупки.'
        }),
    9:  (u'Режим разрешения технологического обнуления. В этот режим ККМ '\
        u'переходит по включению питания, если некорректна информация в '\
        u'энергонезависимом ОЗУ ККМ.', {}),
    10: (u'Тестовый прогон.', {}),
    11: (u'Печать полного фис. отчета.', {}),
    12: (u'Печать отчёта ЭКЛЗ.', {}),
    13: (u'Работа с фискальным подкладным документом:', {
            0:  u'Продажа (открыт).',
            1:  u'Покупка (открыт).',
            2:  u'Возврат продажи (открыт).',
            3:  u'Возврат покупки (открыт).'
        }),
    14: (u'Печать подкладного документа.', {
            0:  u'Ожидание загрузки.',
            1:  u'Загрузка и позиционирование.',
            2:  u'Позиционирование.',
            3:  u'Печать.',
            4:  u'Печать закончена.',
            5:  u'Выброс документа.',
            6:  u'Ожидание извлечения.'
        }),
    15: (u'Фискальный подкладной документ сформирован.', {}),
}

""" Подрежимы ККТ
  Подрежим ККТ – одно из состояний ККТ , в котором он может находиться.
Номера и назначение подрежимов:
"""
KKT_SUBMODES = {
    0:  u'Бумага есть – ККТ не в фазе печати операции – может принимать '\
        u'от хоста команды, связанные с печатью на том документе, датчик'\
        u' которого сообщает о наличии бумаги.',
    1:  u'Пассивное отсутствие бумаги – ККТ не в фазе печати операции – '\
        u'не принимает от хоста команды, связанные с печатью на том '\
        u'документе, датчик которого сообщает об отсутствии бумаги.',
    2:  u'Активное отсутствие бумаги – ККТ в фазе печати операции – '\
        u'принимает только команды, не связанные с печатью. Переход из '\
        u'этого подрежима только в подрежим 3.',
    3:  u'После активного отсутствия бумаги – ККТ ждет команду '\
        u'продолжения печати. Кроме этого принимает команды, не '\
        u'связанные с печатью.',
    4:  u'Фаза печати операции полных фискальных отчетов – ККТ не '\
        u'принимает от хоста команды, связанные с печатью, кроме команды'\
        u' прерывания печати.',
    5:  u'Фаза печати операции – ККТ не принимает от хоста команды, '\
        u'связанные с печатью.',
}

""" Флаги ККТ """
KKT_FLAGS = {
    0:  u'Рулон операционного журнала',
    1:  u'Рулон чековой ленты',
    2:  u'Верхний датчик подкладного документа',
    3:  u'Нижний датчик подкладного документа',
    4:  u'Положение десятичной точки',
    5:  u'ЭКЛЗ',
    6:  u'Оптический датчик операционного журнала',
    7:  u'Оптический датчик чековой ленты',
    8:  u'Рычаг термоголовки операционного журнала',
    9:  u'Рычаг термоголовки чековой ленты',
    10: u'Крышка корпуса ФР',
    11: u'Денежный ящик',
    12: u'Отказ правого датчика принтера | Бумага на входе в презентер | Модель принтера',
    13: u'Отказ левого датчика принтера | Бумага на выходе из презентера',
    14: u'ЭКЛЗ почти заполнена',
    15: u'Увеличенная точность количества | Буфер принтера непуст',
}

""" Флаги ФП """
FP_FLAGS = {
    0: u'ФП 1 (0 – нет, 1 – есть)',
    1: u'ФП 2 (0 – нет, 1 – есть)',
    2: u'Лицензия (0 – не введена, 1 – введена)',
    3: u'Переполнение ФП (0 – нет, 1 – есть)',
    4: u'Батарея ФП (0 – >80%, 1 – <80%)',
    5: u'Последняя запись ФП (0 – испорчена, 1 – корректна)',
    6: u'Смена в ФП (0 – закрыта, 1 – открыта)',
    7: u'24 часа в ФП (0 – не кончились, 1 – кончились)',
}