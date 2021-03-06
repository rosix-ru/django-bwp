# -*- coding: utf-8 -*-
#
#  bwp/contrib/devices/drivers/ShtrihM/__init__.py
#
#  Copyright 2013 Grigoriy Kramarenko <root@rosix.ru>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
from __future__ import unicode_literals
import datetime
import logging
import time

from django.utils.translation import ugettext as _
from django.utils.encoding import force_bytes

from shtrihmfr.kkt import KKT, KktError, int2
from shtrihmfr.protocol import KKT_MODES

from bwp.contrib.devices.remote import RemoteCommand

logger = logging.getLogger('bwp.contrib.devices.drivers.ShtrihM')


SPOOLER_TIMEOUT = 1
SPOOLER_MAX_ATTEMPT = 30


class ShtrihFRK(object):
    "Для онлайн-касс второй версии протокола."

    SpoolerDevice = None
    local_device = None
    kkt = None
    is_remote = False
    is_open = False
    is_ready = False
    payments = {}
    _status = None
    _status_display = None

    def __init__(self, remote=False, *args, **kwargs):
        if remote:
            self.is_remote = True
            self.remote = RemoteCommand(*args, **kwargs)
        else:
            self.kkt = KKT(*args, **kwargs)
            if 'payments' in kwargs:
                self.payments = kwargs.pop('payments')
            # Тестируем правильность установки типов оплат
            assert isinstance(self.payments, dict), \
                'Типы оплат должны быть словарём.'
            self.route_payments(0, 0, 0, 0)

    def route_payments(self, cash, credit, packaging, card):
        "Возвращает направление типов оплат для закрытия чека."
        payments = [0 for x in range(16)]
        payments[self.payments.get('cash', 0)] = cash
        # Клубная карта клиента (дебетовая)
        payments[self.payments.get('card', 1)] = card
        # Банковская карта
        payments[self.payments.get('credit', 2)] = credit
        # Любая другая форма оплаты
        payments[self.payments.get('packaging', 15)] = packaging
        assert len(payments) == 16, \
            'Количество типов оплат должно быть равно 16.'
        return payments

    def get_method_name(self, method):
        if method.im_self == self:
            return method.im_func.func_name
        else:
            return 'kkt.' + method.im_func.func_name

    def make_spooler(self, method, **kwargs):
        if not self.SpoolerDevice:
            return method(**kwargs)

        method = self.get_method_name(method)
        spooler = self.SpoolerDevice(
            local_device=self.local_device,
            method=method,
            kwargs=kwargs,
        )
        spooler.save()
        return spooler.group_hash

    def append_spooler(self, group_hash, method, **kwargs):
        if not self.SpoolerDevice:
            return method(**kwargs)

        method = self.get_method_name(method)

        spooler = self.SpoolerDevice(
            local_device=self.local_device,
            method=method,
            kwargs=kwargs,
            group_hash=group_hash,
        )
        spooler.save()
        return spooler.group_hash

    def result_spooler(self, group_hash, method, strict=True, **kwargs):
        if not self.SpoolerDevice:
            return method(**kwargs)

        method = self.get_method_name(method)

        spooler = self.SpoolerDevice(
            local_device=self.local_device,
            method=method,
            kwargs=kwargs,
            group_hash=group_hash,
        )
        spooler.save()

        STATE_WAITING = self.SpoolerDevice.STATE_WAITING
        STATE_ERROR = self.SpoolerDevice.STATE_ERROR

        all_sps = self.SpoolerDevice.objects.filter(
            local_device=self.local_device, state=STATE_WAITING
        ).order_by('pk')
        self_sps = all_sps.filter(group_hash=spooler.group_hash)
        min_pk = self_sps[0].pk

        other_sps = all_sps.exclude(group_hash=spooler.group_hash)
        c = other_sps.count()
        o = other_sps[0].pk < min_pk if c else False
        n = 0
        while c and o and n < SPOOLER_MAX_ATTEMPT:
            time.sleep(SPOOLER_TIMEOUT)
            n += 1
            other_sps = all_sps.exclude(group_hash=spooler.group_hash)
            c = other_sps.count()
            o = other_sps[0].pk < min_pk if c else False

        if c and o:
            if strict:
                self_sps.all().delete()
                raise KktError(_('The device is busy large queue'))
            else:
                self_sps.update(state=STATE_ERROR)
                return 'Queued'
        else:
            result = None
            for s in self_sps.order_by('pk'):
                method = eval('self.' + s.method)
                kwargs = s.kwargs
                try:
                    result = method(**kwargs)
                except Exception as e:
                    if strict:
                        self_sps.all().delete()
                        raise e
                    else:
                        self_sps.update(state=STATE_ERROR)
                        return 'Queued'
            # time.sleep(SPOOLER_TIMEOUT)
            self_sps.all().delete()
            return result

    def open(self):
        "Начало работы с ККТ."
        if self.is_remote:
            return self.remote("open")

        if not self.is_open:
            kkt_mode = self.status()['kkt_mode']
            if kkt_mode == 4:
                self.kkt.xE0()
                time.sleep(5)
            elif kkt_mode != 2:
                self.kkt.x41()
                time.sleep(5)
                self.kkt.xE0()
                time.sleep(5)
            # снова проверяем статус
            self.status()
        return self.is_open

    def status(self, short=True):
        "Cостояние ККТ, по-умолчанию короткое."
        if self.is_remote:
            self._status = self.remote("status", short=short)
            return self._status

        logger.debug('status %s' % ('short' if short else 'long'))
        method = self.kkt.x10 if short else self.kkt.x11
        self._status = {}

        def set_status():
            self._status = method()
            kkt_mode = self._status['kkt_mode']
            self.is_open = False if kkt_mode != 2 else True
            self.is_ready = True if kkt_mode == 2 else False

        for i in range(10):
            try:
                set_status()
            except Exception as e:
                logger.error(e)
                time.sleep(1)
            else:
                return self._status
        set_status()
        return self._status

    def status_display(self):
        "Cостояние ККТ в читаемом виде."
        if self.is_remote:
            self._status_display = self.remote("status_display")
            return self._status_display

        status = self.status(short=False)

        mode, submodes = KKT_MODES[status['kkt_mode']]
        if submodes:
            mode += ' %s' % submodes[status['kkt_submode']]
        text = 'ИНН: %s\n' % status['inn']
        text += 'Заводской номер: %s\n' % status['serial_number']
        text += 'Номер ФН: %s\n' % self.kkt.xFF02()
        text += 'Срок действия ФН: %(day)s.%(month)s.%(year)sг.\n' % self.kkt.xFF03()
        fn_version = self.kkt.xFF04()
        if fn_version['is_serial']:
            text += 'Серийная версия ФН: %(version)s\n' % fn_version
        else:
            text += 'Отладочная версия ФН: %(version)s\n' % fn_version
        text += 'Режим: %s\n' % mode
        text += 'Дата: %s\n' % status['date']
        text += 'Время: %s\n' % status['time']
        text += 'Последняя закрытая смена: %s\n' % status['last_closed_session']
        text += 'Порт ККТ: %s\n' % status['kkt_port']
        text += 'Порт устройства: %s\n' % self.kkt.port
        text += 'Скорость устройства: %s\n' % self.kkt.bod

        info = self.kkt.xFF39()

        text += 'Состояние чтения сообщения: %s\n' % info['is_read']
        text += 'Количество сообщений для ОФД: %s\n' % info['messages']
        text += 'Документ для ОФД в очереди: %(number)d от %(date)s\n' % (
            info['first']
        )
        info_status = (
            '\tТранспортное соединение установлено: %(connection)s\n'
            '\tЕсть сообщение для передачи в ОФД: %(message)s\n'
            '\tОжидание ответного сообщения от ОФД: %(wait_message)s\n'
            '\tЕсть команда от ОФД: %(command)s\n'
            '\tИзменились настройки соединения с ОФД: %(changed)s\n'
            '\tОжидание ответа на команду от ОФД: %(wait_command)s\n'
        ) % info['status']
        text += 'Статус информационного обмена:\n%s' % info_status
        logger.debug('\n' + text)
        return text

    def reset(self):
        "Сброс предыдущей ошибки или остановки печати."
        logger.debug('reset')
        try:
            self.print_continue()  # предварительный вывод неоконченных
        except:
            try:
                self.cancel()  # отмена ошибочных чеков
            except:
                pass
        return True

    def print_document(self, text='', header='', quick=False):
        "Печать предварительного чека или чего-либо другого."
        if self.is_remote:
            return self.remote("print_document", text=text, header=header)

        if quick:
            group_hash = None
            self.reset()
        else:
            group_hash = self.make_spooler(self.reset)

        if header:
            for line in header.split('\n'):
                self.append_spooler(group_hash, self.kkt.x12_loop, text=line)
        if not text:
            text = 'Текст документа не передан\n' * 10
            text += ' \n' * 10
        for line in text.split('\n'):
            self.append_spooler(group_hash, self.kkt.x17_loop, text=line)
        return self.result_spooler(group_hash, self.cut_tape, strict=False)

    def print_copy(self):
        "Печать копии последнего документа."
        if self.is_remote:
            return self.remote("print_copy")

        group_hash = self.make_spooler(self.reset)
        return self.result_spooler(group_hash, self.kkt.x8C)

    def print_continue(self):
        "Продолжение печати, прерванной из-за сбоя."
        if self.is_remote:
            return self.remote("print_continue")
        return self.kkt.xB0()

    def print_report(self):
        "Печать X-отчета."
        if self.is_remote:
            return self.remote("print_report")
        group_hash = self.make_spooler(self.reset)
        return self.result_spooler(group_hash, self.kkt.x40)

    def close_session(self):
        "Закрытие смены с печатью Z-отчета."
        if self.is_remote:
            return self.remote("close_session")

        result = self.status(False)
        if result['kkt_mode'] != 4:
            group_hash = self.make_spooler(self.reset)
            result = self.result_spooler(group_hash, self.kkt.x41)

        # Автоматическая коррекция времени после закрытия смены
        status = self.status(False)
        now = datetime.datetime.now()
        cur = '%s %s' % (status['date'], status['time'])
        try:
            cur = datetime.datetime.strptime(cur, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            pass
        else:
            diff = now - cur
            ts = diff.total_seconds()
            # Если разбежка более двух часов, то скорее всего слетело время
            # на компьютере или в фискальнике
            if 7200 > abs(ts) > 60:
                self.setup_time(now)
                self.setup_date(now)
        return result

    def cancel_receipt(self):
        "Отмена чека."
        if self.is_remote:
            return self.remote("cancel_receipt")
        return self.kkt.x88()

    def cancel(self):
        "Отмена операции."
        if self.is_remote:
            return self.remote("cancel")
        return self.cancel_receipt()

    def setup_date(self, now=None):
        "Установка даты как в компьютере."
        if self.is_remote:
            return self.remote("setup_date")
        if not now:
            now = datetime.datetime.now()
        error = self.kkt.x22(now.year, now.month, now.day)
        if error:
            return error
        return self.kkt.x23(now.year, now.month, now.day)

    def setup_time(self, now=None):
        "Установка времени как в компьютере."
        if self.is_remote:
            return self.remote("setup_time")
        if not now:
            now = datetime.datetime.now()
        return self.kkt.x21(now.hour, now.minute, now.second)

    def add_money(self, summa):
        "Внесение денег в кассу."
        if self.is_remote:
            return self.remote("add_money", summa=summa)
        return self.kkt.x50(summa)

    def get_money(self, summa):
        "Инкассация."
        if self.is_remote:
            return self.remote("get_money", summa=summa)
        return self.kkt.x51(summa)

    def cut_tape(self, fullcut=True):
        "Отрез чековой ленты."
        if self.is_remote:
            return self.remote("cut_tape", fullcut=fullcut)
        return self.kkt.x25(fullcut=fullcut)

    def print_receipt(self, specs, cash=0, credit=0, packaging=0, card=0,
                      discount_summa=0, discount_percent=0, document_type=0,
                      nds=0, header='', comment='', buyer='',
                      mail_or_phone='',
                      seller_name='',
                      **kwargs):
        """ Печать чека.
            Новый метод продаж и возвратов для онлайн-касс.

            specs - Это список словарей проданных позиций:
            [
                {
                    'title': 'Хлеб',
                    'price': '10.00',
                    'count': '3',
                    'summa': '30.00',
                    'discount_summa': 1.0,
                },
            ]
            Типы оплат:
                cash      - наличными
                credit    - кредитом
                packaging - тарой
                card      - платёжной картой
            Тип документа:
                0 – продажа -->> (1 – Приход);
                1 – покупка -->> (3 – Расход);
                2 – возврат продажи --> (2 – Возврат прихода);
                3 – возврат покупки --> (4 – Возврат расхода);

        """
        if self.is_remote:
            return self.remote(
                "print_receipt",
                specs=specs, cash=cash, credit=credit,
                packaging=packaging, card=card,
                discount_summa=discount_summa,
                discount_percent=discount_percent,
                document_type=document_type, nds=nds,
                header=header, comment=comment, buyer=buyer,
                mail_or_phone=mail_or_phone,
                **kwargs
            )

        self.reset()

        status = self.status()
        self.open()
        assert self.is_open, 'Невозможно начать смену на регистраторе.'
        assert self.is_ready, 'Регистратор не готов к приёму чека (занят).'

        kkt = self.kkt  # short link

        group_hash = self.make_spooler(self.reset)

        taxes = [0, 0, 0, 0]
        if nds > 0:
            taxes[0] = 2
            # Включаем начисление налогов на ВСЮ операцию чека
            # self.append_spooler(
            #     group_hash,
            #     kkt.x1E, table=1, row=1, field=17, value=chr(0x1),
            # )
            # Включаем печатать налоговые ставки и сумму налога
            # self.append_spooler(
            #     group_hash,
            #     kkt.x1E, table=1, row=1, field=19, value=chr(0x2),
            # )
            # self.append_spooler(
            #     group_hash,
            #     kkt.x1E, table=6, row=2, field=1,
            #     value=int2.pack(nds * 100),
            # )

        # Открыть чек
        # self.append_spooler(
        #     group_hash, kkt.x8D, document_type=document_type
        # )

        if header:
            for line in header.split('\n'):
                self.append_spooler(group_hash, kkt.x17_loop, text=line)

        if document_type == 0:
            text_buyer = 'Приход от %s'
            operation = 1
        elif document_type == 2:
            text_buyer = 'Возврат прихода %s'
            operation = 2
        elif document_type == 1:
            text_buyer = 'Расход к %s'
            operation = 3
        elif document_type == 3:
            text_buyer = 'Возврат расхода %s'
            operation = 4
        else:
            raise KktError(_('Type of document must be 0..3'))

        text_seller = ('Кассир: %s' % seller_name if seller_name else '').strip()
        text_buyer = (text_buyer % buyer if buyer else '').strip()

        total_summa = 0
        total_discount = 0

        for spec in specs:
            text = spec['title']
            barcode = spec.get('barcode') or 0
            if barcode and not isinstance(barcode, int):
                try:
                    barcode = int(barcode)
                except ValueError:
                    barcode = 0
            count = round(float(spec['count']), 2)
            price = round(float(spec['price']), 2)
            summa = round(float(spec['summa']), 2)
            discount = round(float(spec.get('discount_summa', 0)), 2)
            if discount:
                # При скидке 5% переменная равна 0.5.
                _percent = round(1.0 * discount / summa, 2)
                # Цена за единицу со скидкой
                price = round(price - (price * _percent), 2)
                # Реальная скидка
                discount = summa - round(price * count, 2)

            summa = round(count * price, 2)
            total_summa += summa
            total_discount += discount

            self.append_spooler(
                group_hash,
                kkt.xFF0D,
                operation=operation,
                count=count,
                price=price,
                discount=0,
                increment=0,
                department=0,
                tax=0,
                barcode=barcode,
                text=text,
            )
            if discount:
                line = '{0:>36}'.format('включая скидку: %.2f' % discount)
                self.append_spooler(group_hash, kkt.x17_loop, text=line)

        tlv_dict = {}

        if seller_name:
            tlv_dict[1021] = seller_name
        if mail_or_phone:
            text_buyer += ' (%s)' % mail_or_phone
            tlv_dict[1008] = mail_or_phone

        if tlv_dict:
            logger.debug('TLV: %s' % tlv_dict)
            # Передача TLV для ОФД
            self.append_spooler(
                group_hash,
                kkt.xFF0C,
                tlv_dict=tlv_dict,
            )

        if text_seller:
            for line in text_seller.split('\n'):
                self.append_spooler(group_hash, kkt.x17_loop, text=line)
        if text_buyer:
            for line in text_buyer.split('\n'):
                self.append_spooler(group_hash, kkt.x17_loop, text=line)
        if comment:
            for line in comment.split('\n'):
                self.append_spooler(group_hash, kkt.x17_loop, text=line)

        if total_discount:
            self.append_spooler(group_hash, kkt.x17_loop, text='-' * 36)
            line = '{0:>36}'.format('общая скидка: %.2f' % total_discount)
            self.append_spooler(group_hash, kkt.x17_loop, text=line)
        self.append_spooler(group_hash, kkt.x17_loop, text=('=' * 36))

        test_total_summa = round(total_summa, 5)
        test_payment_sums = round(cash + credit + packaging + card, 5)
        # Сумма оплат равна сумме чека
        if test_payment_sums - test_total_summa == 0:
            pass
        # Сумма оплат больше суммы чека
        elif test_payment_sums - test_total_summa > 0:
            # Фикс оплаты клубной картой
            if card and round(card - credit - cash - packaging, 5) > test_total_summa:
                card = test_total_summa - credit - cash - packaging
            # Фикс оплаты банковской картой
            elif credit and round(credit - cash - card - packaging, 5) > test_total_summa:
                credit = test_total_summa - cash - card - packaging
        # Сумма чека в пределах рубля больше суммы оплат из-за пересчёта скидки
        elif 0 < test_total_summa - test_payment_sums < 1:
            # Погрешность приведения скидок ставим в наличные
            cash += test_total_summa - test_payment_sums
        # Сумма чека сильно больше суммы оплат
        else:
            assert test_total_summa <= test_payment_sums, force_bytes(
                'Сумма спецификаций больше, чем сумма типов оплат: '
                '%.5f != %.5f' % (test_total_summa, test_payment_sums)
            )

        payments = self.route_payments(cash, credit, packaging, card)

        data = None
        try:
            data = self.result_spooler(
                group_hash,
                kkt.x8E,
                payments=payments,
                taxes=taxes,
                discount_percent=0,  # Очень важно теперь ничего не передавать!
            )
        except Exception as e:
            logger.error(e)
            raise e
        finally:
            return data


ShtrihFRK2 = ShtrihFRK


def run_tests(port='/dev/ttyACM0', bod=115200):
    dev = ShtrihFRK(port=port, bod=bod)
    dev.status_display()

    # logger.debug('print_document:')
    # header = 'Заголовок документа'
    # text = (
    #     'Текст документа с переводом первой строки и большой второй строкой:\n'
    #     'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do '
    #     'eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim '
    #     'ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut '
    #     'aliquip ex ea commodo consequat. Duis aute irure dolor in '
    #     'reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla '
    #     'pariatur. Excepteur sint occaecat cupidatat non proident, sunt in '
    #     'culpa qui officia deserunt mollit anim id est laborum.'
    #     ' \n \n \n \n \n \n \n \n \n \n'
    # )
    # logger.debug(dev.print_document(text=text, header=header))

    # order = {
    #     'comment': '',
    #     'mail_or_phone': '',
    #     'discount_summa': 1178.15,
    #     'credit': 0,
    #     'cash': 0.0,
    #     'packaging': 0,
    #     'card': 11.9,
    #     'header': 'POS: Смотровая',
    #     'discount_percent': 0,
    #     'buyer': 'Иванов И.И. ЗК-195',
    #     'nds': 0,
    #     'document_type': 0,
    #     'specs': [
    #         {
    #             'count': 1.0,
    #             'discount_summa': 99.0,
    #             'price': 100.0,
    #             'summa': 100.0,
    #             'title': 'Доставка пиццы',
    #         },
    #         {
    #             'count': 2.0,
    #             'discount_summa': 0.02,
    #             'price': 0.01,
    #             'summa': 0.02,
    #             'title': 'АКЦИЯ Кока-Кола 1 литр.',
    #         },
    #         {
    #             'count': 3.0,
    #             'discount_summa': 0.03,
    #             'price': 0.01,
    #             'summa': 0.03,
    #             'title': 'АКЦИЯ Сок Яблоко',
    #         },
    #         {
    #             'count': 1.0,
    #             'discount_summa': 237.6,
    #             'price': 240.0,
    #             'summa': 240.0,
    #             'title': 'Мини-пицца Пышная "Вегетарианская"',
    #         },
    #         {
    #             'count': 1.0,
    #             'discount_summa': 227.7,
    #             'price': 230.0,
    #             'summa': 230.0,
    #             'title': 'Мини-пицца ПЫШНАЯ "Гавайская"',
    #         },
    #         {
    #             'count': 2.0,
    #             'discount_summa': 613.8,
    #             'price': 310.0,
    #             'summa': 620.0,
    #             'title': 'Мини-пицца ПЫШНАЯ "Грибная"',
    #         },
    #     ]
    # }
    # logger.debug('print_receipt:')
    # logger.debug(dev.print_receipt(**order))

    # specs = [
    #     {
    #         'title': 'Хлеб чёрный Бородинский',
    #         'price': '30.00',
    #         'count': '0.5',
    #         'summa': '15.00',
    #         'discount_summa': '0.33',
    #     },
    #     {
    #         'title': 'Молоко',
    #         'price': '54.00',
    #         'count': '3',
    #         'summa': '162.00',
    #         'discount_summa': 4.50,
    #     },
    #     {
    #         'title': 'Водка Беленькая',
    #         'price': '390.00',
    #         'count': '2',
    #         'summa': '780.00',
    #         'discount_summa': 30.0,
    #         'barcode': 999999999999,
    #     },
    # ]
    # summa = 15 - 0.33 + 162 - 4.50 + 780 - 30
    # cash = summa
    # card = summa / 3
    # credit = summa / 3
    # packaging = 0
    # header = 'Продажа товаров'
    # comment = 'Комментарий к продаже товаров'
    # buyer = 'Иван Иванов'
    # mail_or_phone = '89997776655'

    # logger.debug('print_receipt:')
    # logger.debug(dev.print_receipt(
    #     specs, cash=cash, credit=credit, packaging=packaging, card=card,
    #     discount_summa=0, discount_percent=0, document_type=0, nds=0,
    #     header=header, comment=comment, buyer=buyer,
    #     mail_or_phone=mail_or_phone
    # ))

    # logger.debug('print_document:')
    # header = 'Заголовок документа'
    # text = (
    #     'Текст документа с переводом первой строки и большой второй строкой:\n'
    #     'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do '
    #     'eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim '
    #     'ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut '
    #     'aliquip ex ea commodo consequat. Duis aute irure dolor in '
    #     'reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla '
    #     'pariatur. Excepteur sint occaecat cupidatat non proident, sunt in '
    #     'culpa qui officia deserunt mollit anim id est laborum.'
    #     ' \n \n \n \n \n \n \n \n \n \n'
    # )
    # logger.debug(dev.print_document(text=text, header=header))

    # time.sleep(10)
    # print(dev.print_copy())
    # time.sleep(10)
    # print(dev.print_report())
    # time.sleep(10)
    # print(dev.close_session())
    return


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    run_tests()
