#coding: utf-8

import peewee
from peewee import fn
from app.models import *
from datetime import timedelta
from playhouse.shortcuts import model_to_dict
import re
from  pprint import pprint


class Searcher(object):
    def __init__(self, ui):
        self.ui = ui
        self.query = ''
        self.queries = []

    def startSearch(self, query):
        self.query = query
        self._determinant()

        base_query = ((0|0))
        for query in self.queries:
            base_query = (base_query | query)

        self.result = (Ticket.select()
                .join(User, on=(User.id == Ticket.user_id))
                .join(Phone, on=(User.id == Phone.user_id))
                .join(Email, on=(User.id == Email.user_id))
                .join(Product, on=(Product.id == Ticket.product_id))
                .where(base_query)).group_by(Ticket.id)

        return self.result

    def _getInt(self, query):
        try: return int(query)
        except: pass

    def _determinant(self):
        if self.ui.searchTickets.checkState() == 2:
            self.queries.append((Ticket.id == self._getInt(self.query)))
            self.queries.append((Product.name.contains(self.query)))
            self.queries.append((Product.code.contains(self.query)))

            if self.ui.wideSearch.checkState() == 2:
                self.queries.append((Ticket.break_type == self.query)) #TODO пофиксить числовой выбор
                self.queries.append((Ticket.reason.contains(self.query)))
                self.queries.append((Ticket.fix.contains(self.query)))
                self.queries.append((Ticket.comment.contains(self.query)))


        if self.ui.searchUsers.checkState() == 2:
            self.queries.append((User.id == self._getInt(self.query)))
            self.queries.append((User.name.contains(self.query)))
            self.queries.append((Phone.phone.contains(self.query)))
            self.queries.append((Email.email.contains(self.query)))
            if self.ui.wideSearch.checkState() == 2:
                self.queries.append((User.address.contains(self.query)))
                self.queries.append((User.comment.contains(self.query)))


        if self.ui.searchHaveChange.checkState() == 2:
            self.queries.append((Ticket.changed_number.contains(self.query) & (Ticket.changed_number != "")))
            if self.ui.wideSearch.checkState() == 2:
                self.queries.append((Ticket.changed_comment.contains(self.query)))


        if self.ui.searchOpened.checkState() == 2:
            self.queries.append((Ticket.closed == 0))

        if self.ui.searchClosed.checkState() == 2:
            self.queries.append((Ticket.closed == 2))

class DB(object):
    def savePhone(self, user_id, phone):
        """Создаёт или возвращает id номера"""
        with db:
            for i in phone.split(' '):
                if i == '+': continue
                user_id, status = Phone.get_or_create(
                        phone = i.strip(),
                        defaults={'user_id': user_id})

    def dropPhone(self, user_id):
        """Удаляет все телефоны пользователя при изменении профиля"""
        with db:
            ad = Phone.delete().where(Phone.user_id == user_id)
            ad.execute()



    def saveEmail(self, user_id, email):
        """Создаёт или возвращает id мыла"""
        with db:
            for i in email.split(' '):
                u_id, status = Email.get_or_create(
                        email = i.strip(),
                        defaults={'user_id': user_id})


    def dropEmail(self, user_id):
        """Удаляет все email пользователя при изменении профиля"""
        with db:
            ad = Email.delete().where(Email.user_id == user_id)
            ad.execute()

#-----------------------------------------[МЕТОДЫ ОБЩЕГО СОХРАНЕНИЯ]
    def saveTicket(self, **kwargs):
        """Сохраняет данные тикета
        {
            'ticket_id': ticket.ticketID.text(),
            'user_id': user_id,
            'product_id': product_id,
            'serial_number': ticket.serialNumber.text(),
            'break_type': ticket.brokeType.currentIndex(),
            'changed_number': ticket.changeCode.text(),
            'changed_comment': ticket.changeComment.toPlainText(),
            'reason': ticket.reason.toPlainText(),
            'fix': ticket.fix.toPlainText(),
            'comment': ticket.comment.toPlainText(),
            'open_date': self.getStrped(ticket.createDate.text()),
            'change_date': self.getStrped(ticket.lastChange.text()),
            'close_date': self.getStrped(ticket.closeDate.text()),
            'deadline': self.getStrped(ticket.deadLine.text()),
            'closed': ticket.checkBox.checkState()
        }
        """
        if kwargs['ticket_id'] == 'None':
            ticket_id = Ticket.create(
                user_id = kwargs['user_id'],
                product_id = kwargs['product_id'],
                serial_number = kwargs['serial_number'],
                break_type = kwargs['break_type'],
                changed_number = kwargs['changed_number'],
                changed_comment = kwargs['changed_comment'],
                reason = kwargs['reason'],
                fix = kwargs['fix'],
                comment = kwargs['comment'],
                open_date = kwargs['open_date'],
                change_date = kwargs['change_date'],
                close_date = kwargs['close_date'],
                deadline = kwargs['deadline'],
                closed = kwargs['closed']
            )
            return ticket_id

        else:
            ticket = Ticket.get(Ticket.id == kwargs['ticket_id'])
            ticket.user_id = kwargs['user_id']
            ticket.product_id = kwargs['product_id']
            ticket.serial_number = kwargs['serial_number']
            ticket.break_type = kwargs['break_type']
            ticket.changed_number = kwargs['changed_number']
            ticket.changed_comment = kwargs['changed_comment']
            ticket.reason = kwargs['reason']
            ticket.fix = kwargs['fix']
            ticket.comment = kwargs['comment']
            ticket.open_date = kwargs['open_date']
            ticket.change_date = kwargs['change_date']
            ticket.close_date = kwargs['close_date']
            ticket.deadline = kwargs['deadline']
            ticket.closed = kwargs['closed']
            ticket.save()            
            return ticket


    def saveUser(self, **kwargs):
        """Сохраняет данные пользователя, передаёт контакты другим функциям
        """
        if kwargs['user_id'] == 'None':
            with db:
                user_id = User.create(
                    name = kwargs['name'],
                    address = kwargs['address'],
                    comment = kwargs['comment'],
                    change_date = kwargs['change_date'],
                    remind_date = kwargs['remind_date'],
                    remind_is_have = kwargs['remind_is_have'])

                kwargs['user_id'] = user_id
                
        else:
            user = User.get(User.id == kwargs['user_id'])
            user.name = kwargs['name']
            user.address = kwargs['address']
            user.comment = kwargs['comment']
            if not kwargs['from_ticket']:
                user.remind_date = kwargs['remind_date']
                user.remind_is_have = kwargs['remind_is_have']
            user.save()
            
        self.saveEmail(kwargs['user_id'], kwargs['email'].strip())
        self.savePhone(kwargs['user_id'], kwargs['phone'].strip())
        return kwargs['user_id']


    def saveProduct(self, **kwargs):
        """Сохраняет продукты, возвращает продукт_айди"""
        with db:
            product_id, status = Product.get_or_create(
                    name = kwargs['name'],
                    code = kwargs['code'])
        return product_id


#-----------------------------------------[КОМПЛЕКСНОЕ ПОЛУЧЕНИЕ ДАННЫХ]
    def getTicketData(self, ticket_id):
        """Возвращает полную информацию тикета по его id """ 
        ticket = Ticket.get(Ticket.id == ticket_id)
        product = Product.get(Product.id == ticket.product_id)
        data = {
            'ticket_id': str(ticket.id),
            'user_id': ticket.user_id,
            'product_name': product.name,
            'product_code': product.code,
            'serial_number': ticket.serial_number,
            'break_type': ticket.break_type,
            'changed_number': ticket.changed_number,
            'changed_comment': ticket.changed_comment,
            'reason': ticket.reason,
            'fix': ticket.fix,
            'comment': ticket.comment,
            'open_date': ticket.open_date,
            'change_date': ticket.change_date,
            'close_date': ticket.close_date,
            'deadline': ticket.deadline,
            'closed': ticket.closed #Состояние чек бокса
        }
        return data

    def getUserData(self, user_id):
        """Возвращает все данные пользователя"""
        user = User.get(User.id == user_id)
        email = Email.select().where(Email.user_id == user_id)
        phone = Phone.select().where(Phone.user_id == user_id)
        data = {
            'user_id': str(user.id),
            'name': user.name,
            'address': user.address,
            'email': " ".join([(i.email) for i in list(email)]),
            'phone': " ".join([f'+{i.phone}' for i in list(phone)]),  
            'comment': user.comment,
            'remind_date': user.remind_date,
            'remind_is_have': int(user.remind_is_have),
        }
        return data


    def getObjectDict(self, obj):
        return model_to_dict(obj)

    def getTicketsByDate(self, date):
        next_day = date.date() + timedelta(days=1)
        return Ticket.select().where(Ticket.open_date >= date.date()).where(Ticket.open_date <= next_day)
        
    def getTickets(self, user_id):
        """Возвращает объект тикета из базы"""
        tickets = Ticket.select().where(Ticket.user_id == user_id)
        return tickets


    def getTicketsByDeadline(self):
        tickets = Ticket.select().where(Ticket.closed == 0).order_by(Ticket.deadline)
        return tickets


    def getDataForDeadline(self):
        ticket = Ticket.select(Ticket.id, Ticket.deadline).where(Ticket.closed == 0).order_by(Ticket.deadline)
        profile = User.select(User.id, User.remind_date).where(User.remind_is_have == 2).order_by(User.remind_date)
        data = [( i.deadline, i.id, 'ticket') for i in ticket]+[( i.remind_date, i.id, 'user') for i in profile]
        return sorted(data, key=lambda d: d[0])

                        

    def checkEmail(self, email): 
        """Проверяет email. возвращает или none или ticket_id """
        email_obj = Email.get_or_none(Email.email == email.strip())
        if email_obj == None: return None
        else: return email_obj.user_id


    def checkPhone(self, phone): 
        """Проверяет телефон. возвращает или none или phone_id""" 
        phone_obj = Phone.get_or_none(Phone.phone == phone.strip())
        if phone_obj == None: return None
        else: return phone_obj.user_id
