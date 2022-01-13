#coding: utf-8

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from Ui import LoginUI, MainUI, ProfileUI, TicketUI
from DataBase.DbMethods import *
import datetime
import os
import json
import logging
import re
import xlrd
from  pprint import pprint

logging.basicConfig(level=logging.INFO, handlers=[logging.FileHandler("program.log"), logging.StreamHandler()])

db = DB()

class Main(object):
    def __init__(self):
        self.directory = f"{os.getcwd()}\\data\\Tickets\\None"
        self.basketPath = f"{os.getcwd()}\\data\\Basket"
        self.configPath = f"{os.getcwd()}\\data\\config.json"

        self.openedTickets = []
        self.openedProfiles = []
        self.today = datetime.datetime.now()
        self.openMainWindow()

#-----------------------------------------[ВЬЮХИ]
    def loginView(self):
        """Отображение логинки"""
        self.Login = QtWidgets.QDialog()
        ui = LoginUI.Ui_Login()
        ui.setupUi(self.Login)
        ui.enterButton.clicked.connect(lambda: self.verification(ui))
        self.Login.show()
        self.getConfig()


    def mainWindowView(self):
        """Отображение главного окна"""
        self.MainWindow = QtWidgets.QMainWindow()
        ui = MainUI.Ui_MainWindow()
        ui.setupUi(self.MainWindow)
        self.setHeadIndexesOfMainTable(ui)
        self.setConnectsToMain(ui)
        self.MainWindow.show()
        return ui


    def profileView(self):
        """Отображение профиля"""
        self.Profile = QtWidgets.QDialog()
        ui = ProfileUI.Ui_Profile()
        ui.setupUi(self.Profile)
        self.setConnectsToProfile(ui)
        self.Profile.show()
        self.openedProfiles.append(self.Profile)
        return ui


    def ticketView(self):
        """Отображение тикета"""
        self.Ticket = QtWidgets.QDialog()
        ui = TicketUI.Ui_Ticket()
        ui.setupUi(self.Ticket)
        self.setConnectsToTicket(ui)
        self._setBrokeTypes(ui)
        self.Ticket.show()
        self.openedTickets.append(self.Ticket)
        return ui

#-----------------------------------------[КОННЕКТЫ]
    def setConnectsToMain(self, ui):
        ui.createTicketButton.clicked.connect(self.createNewTicket)
        ui.refreshTablesButton.clicked.connect(lambda: self.refreshTables(ui))
        ui.mainTable.cellPressed[int, int].connect(self.clickedRowColumnMain)
        ui.deadlineTable.cellPressed[int, int].connect(self.clickedRowColumnDeadline)
        ui.searchButton.clicked.connect(lambda: self.startSearch(ui))
        ui.date.dateChanged.connect(lambda: self.nextDate(ui))
        ui.uploadData.clicked.connect(self.loadTables)


    def setConnectsToTicket(self, ui):
        ui.openUserButton.clicked.connect(lambda: self.openProfile(ui.openUserButton.text()))
        ui.checkByEmail.clicked.connect(lambda: self.checkEmail(ui))
        ui.checkByPhone.clicked.connect(lambda: self.checkPhone(ui))
        ui.showFileButton.clicked.connect(lambda: self.showFiles(ui.ticketID.text()))
        ui.saveButton.clicked.connect(lambda: self.saveTicket(ui))
        ui.checkBox.clicked.connect(lambda: self.closeTicket(ui))
        ui.deadLine.setDate(self.today)
        ui.editCheckBox.clicked.connect(lambda: self.setModeOfTicketForm(ui))


    def setConnectsToProfile(self, ui):
        ui.createTicketButton.clicked.connect(lambda: self.createTicketFromProfile(ui))
        ui.saveButton.clicked.connect(lambda: self.saveProfile(ui))
        ui.tickets.cellPressed[int, int].connect(self.clickedRowColumn)
        ui.editCheckBox.clicked.connect(lambda: self.setModeOfProfileForm(ui))

#-----------------------------------------[РЕЖИМ РЕДАКТИРОВАНИЯ ДАННЫХ]
    def setModeOfTicketForm(self, ui):
        if ui.editCheckBox.checkState() == 2:
            self.enableEditModeForTicket(ui)

        elif ui.editCheckBox.checkState() == 0:
            self.disableEditModeForTicket(ui)

    def enableEditModeForTicket(self, ui):
        ui.editCheckBox.setCheckState(2)

        ui.name.setReadOnly(False)
        ui.email.setReadOnly(False)
        ui.phone.setReadOnly(False)
        ui.address.setReadOnly(False)
        ui.comment.setReadOnly(False)
        ui.productName.setReadOnly(False)
        ui.productCode.setReadOnly(False)
        ui.serialNumber.setReadOnly(False)
        ui.changeCode.setReadOnly(False)
        ui.changeComment.setReadOnly(False)
        ui.reason.setReadOnly(False)
        ui.fix.setReadOnly(False)
        ui.comment.setReadOnly(False)

        ui.brokeType.setEnabled(True)
        ui.checkBox.setEnabled(True)
        ui.deadLine.setEnabled(True)
        ui.checkByPhone.setEnabled(True)
        ui.checkByEmail.setEnabled(True)


    def disableEditModeForTicket(self, ui):
        ui.editCheckBox.setCheckState(0)
        
        ui.name.setReadOnly(True)
        ui.email.setReadOnly(True)
        ui.phone.setReadOnly(True)
        ui.address.setReadOnly(True)
        ui.comment.setReadOnly(True)
        ui.productName.setReadOnly(True)
        ui.productCode.setReadOnly(True)
        ui.serialNumber.setReadOnly(True)
        ui.changeCode.setReadOnly(True)
        ui.changeComment.setReadOnly(True)
        ui.reason.setReadOnly(True)
        ui.fix.setReadOnly(True)
        ui.comment.setReadOnly(True)

        ui.brokeType.setEnabled(False)
        ui.checkBox.setEnabled(False)
        ui.deadLine.setEnabled(False)
        ui.checkByPhone.setEnabled(False)
        ui.checkByEmail.setEnabled(False)

    def setModeOfProfileForm(self, ui):
        if ui.editCheckBox.checkState() == 2:
            self.enableEditModeForProfile(ui)

        elif ui.editCheckBox.checkState() == 0:
            self.disableEditModeForProfile(ui)

    def enableEditModeForProfile(self, ui):
        ui.editCheckBox.setCheckState(2)
        ui.name.setReadOnly(False)
        ui.email.setReadOnly(False)
        ui.phone.setReadOnly(False)
        ui.address.setReadOnly(False)
        ui.comment.setReadOnly(False)
        
        ui.reminderTime.setEnabled(True)
        ui.remindCheckBox.setEnabled(True)


    def disableEditModeForProfile(self, ui):
        ui.editCheckBox.setCheckState(0)
        ui.name.setReadOnly(True)
        ui.email.setReadOnly(True)
        ui.phone.setReadOnly(True)
        ui.address.setReadOnly(True)
        ui.comment.setReadOnly(True)

        ui.reminderTime.setEnabled(False)
        ui.remindCheckBox.setEnabled(False)

#-----------------------------------------[Методы Таблиц]
    def setMainTableData(self, tickets, ui):
        """Заполняет таблицу данными"""
        ui.mainTable.setRowCount(len(tickets))
        self.ticketsInRowMain = []
        for col, ticket in enumerate(reversed(tickets)):
            self.ticketsInRowMain.append(str(ticket.id))
            profile = db.getUserData(ticket.user_id)
            ticket = db.getTicketData(ticket.id)
            row_data = {}
            row_data.update(ticket)
            row_data.update(profile)
            for row, item_dict in enumerate(self.getConfig()['Indexes']):
                item = QtWidgets.QTableWidgetItem()
                if item_dict['field_name'] == 'files':
                    item.setText(self.getFileCounts(row_data['ticket_id']))

                elif item_dict['field_name'] == 'break_type':
                    broke_types = self.getConfig()['broke types']
                    item.setText(broke_types[int(row_data['break_type'])])

                elif item_dict['field_name'] in ['open_date', 'deadline']:
                    item.setText(self.getStrfed(row_data[item_dict['field_name']]))

                else: 
                    item.setText(row_data[item_dict['field_name']])

                ui.mainTable.setItem(col, row, item)  

                if item_dict['field_name'] in ['user_id', 'ticket_id', 'files']:
                    ui.mainTable.item(col, row).setTextAlignment(QtCore.Qt.AlignCenter)

        ui.count.setText(str(len(self.ticketsInRowMain)))


    def setHeadIndexesOfMainTable(self, ui):
        """Устанавливает индексы мейн таблицы"""
        indexes = self.getConfig()['Indexes']
        ui.mainTable.setColumnCount(len(indexes))
        for index, item_dict in enumerate(indexes):
            item = QtWidgets.QTableWidgetItem(item_dict['name'])
            ui.mainTable.setHorizontalHeaderItem(index, item)


    def setUserTableData(self, user_id, profile):
        """Заполняет пользовательскую таблицу"""
        tickets = db.getTickets(user_id)
        profile.tickets.setRowCount(len(tickets))
        self.ticketsInRowProfile = []
        for index, item in enumerate(reversed(tickets)):
            self.ticketsInRowProfile.append(str(item.id))
            profile.tickets.setItem(index, 0, QtWidgets.QTableWidgetItem(str(item.id)))
            profile.tickets.item(index, 0).setTextAlignment(QtCore.Qt.AlignCenter)
            config = self.getConfig()['broke types']
            profile.tickets.setItem(index, 1, QtWidgets.QTableWidgetItem(config[int(item.break_type)]))
            profile.tickets.setItem(index, 2, QtWidgets.QTableWidgetItem(str(item.open_date)[0:10]))


    def setDeadlines(self, ui):
        data = db.getDataForDeadline()
        pprint(data)
        # data = [(self.getStrped(self.getStrfed(i[0])), i[1], i[2]) for i in data]

        # tickets = db.getTicketsByDeadline()
        # profile = db.getUserData()
        ui.deadlineTable.setRowCount(len(data))
        self.ticketsInRowDeadline = []
        for index, item  in enumerate(reversed(data)):
            id = f'{item[2].capitalize()} {item[1]}'
            time = item[0]
            self.ticketsInRowDeadline.append(id)
            ui.deadlineTable.setItem(index, 0, QtWidgets.QTableWidgetItem(id))
            ui.deadlineTable.item(index, 0).setTextAlignment(QtCore.Qt.AlignCenter)
            days_delta = time - datetime.datetime.now()
            days = str(days_delta).split(',')[0].split('.')[0]
            ui.deadlineTable.setItem(index, 1, QtWidgets.QTableWidgetItem(days))


    def clickedRowColumn(self, a, b):
        """Отлавливает нажатия на ячейки таблицы"""
        ticket_id = self.ticketsInRowProfile[a]
        if b == 0:  self.openTicket(ticket_id)

    def clickedRowColumnMain(self, a, b):
        """Отлавливает нажатия на ячейки мейн таблицы"""
        ticket_id = self.ticketsInRowMain[a]
        if b == 1: 
            ticket = db.getTicketData(ticket_id)
            self.openProfile(ticket['user_id'])

        if b == 2: self.showFiles(ticket_id)
        elif b == 0:  self.openTicket(ticket_id)

    def clickedRowColumnDeadline(self, a, b):
        """Отлавливает нажатия на ячейки таблицы"""
        type_ = self.ticketsInRowDeadline[a].split(' ')[0]
        id_ = int(self.ticketsInRowDeadline[a].split(' ')[1])

        if b == 0 and type_ == 'Ticket':  self.openTicket(id_)
        elif b == 0 and type_ == 'User':  self.openProfile(id_)

    def refreshTables(self, ui):
        """Обновляет данные в таблицах главного окна"""
        tickets = db.getTicketsByDate(self.today)
        self.setMainTableData(tickets, ui)
        self.setDeadlines(ui)
        ui.date.setDate(self.today)

#-----------------------------------------[ОТКРЫВАШКИ]
    def openMainWindow(self):
        """Открывает основное окно из логинки"""
        ui = self.mainWindowView()
        tickets = db.getTicketsByDate(self.today)
        self.setMainTableData(tickets, ui)
        self.setDeadlines(ui)
        ui.date.setDate(self.today)


    def openProfile(self, user_id):
        """Открывает профиль из тикета"""
        ui = self.profileView()
        user_data = db.getUserData(user_id)
        ui.userID.setText(user_data['user_id'])
        ui.name.setText(user_data['name'])
        ui.email.setText(user_data['email'])
        ui.phone.setText(user_data['phone'])
        ui.address.setText(user_data['address'])
        ui.comment.setText(user_data['comment'])
        ui.reminderTime.setDateTime(self.getStrped(user_data['remind_date'])) 
        ui.remindCheckBox.setCheckState(user_data['remind_is_have']) 

        self.setUserTableData(user_id, ui)
        self.disableEditModeForProfile(ui)


    def openTicket(self, ticket_id):
        """Открывает уже существующий тикет"""
        ui = self.ticketView()
        ticket_data = db.getTicketData(ticket_id)
        self._fillUserData(ticket_data['user_id'], ui)
        ui.ticketID.setText(ticket_data['ticket_id'])
        ui.productName.setText(ticket_data['product_name'])
        ui.productCode.setText(ticket_data['product_code'])
        ui.serialNumber.setText(ticket_data['serial_number'])
        ui.brokeType.setCurrentIndex(int(ticket_data['break_type']))
        ui.changeCode.setText(ticket_data['changed_number'])
        ui.changeComment.setText(ticket_data['changed_comment'])
        ui.reason.setText(ticket_data['reason'])
        ui.fix.setText(ticket_data['fix'])
        ui.comment.setText(ticket_data['comment'])
        ui.createDate.setText(self.getStrfed(ticket_data['open_date']))
        ui.lastChange.setText(self.getStrfed(ticket_data['change_date']))
        ui.closeDate.setText(self.getStrfed(ticket_data['close_date']))
        ui.checkBox.setCheckState(int(ticket_data['closed']))
        ui.deadLine.setDate(self.getStrped(ticket_data['deadline']))
        ui.showFileButton.setText('Файлы: ' + self.getFileCounts(ticket_data['ticket_id']))
        if ticket_data['changed_number'] != '':
            ui.tabWidget.setTabText(ui.tabWidget.indexOf(ui.tab_2), "Замена +")
        self.disableEditModeForTicket(ui)


    def createNewTicket(self):
        """Создаёт тикет из главного окна"""
        ticket = self.ticketView()
        ticket.createDate.setText(self.getStrfed())

    def createTicketFromProfile(self, ui):
        """Создаёт тикет из профиля с заполнением форм"""
        ticket = self.ticketView()
        ticket.createDate.setText(self.getStrfed())
        self._fillUserData(ui.userID.text(), ticket)

#-----------------------------------------[СОХРАНЕНИЕ]
    def saveProfile(self, ui):
        """Сохраняет профиль юзера"""
        db.dropPhone(ui.userID.text())
        db.dropEmail(ui.userID.text())
        kwargs = {
            'user_id': ui.userID.text(),
            'name': ui.name.text(),
            'email': ui.email.text(),
            'phone': ui.phone.text(),
            'address': ui.address.toPlainText(),
            'comment': ui.comment.toPlainText(),
            'change_date': self.getStrfed(),
            'remind_date': self.getStrped(ui.reminderTime.text()),
            'remind_is_have': ui.remindCheckBox.checkState(),
            'from_ticket': False
            }
        db.saveUser(**kwargs)
        ui.changeDate.setText(self.getStrfed())
        self.disableEditModeForProfile(ui)

    def saveTicket(self, ticket):
        """Сохраняет данные тикета на его айди"""
        self.phoneFilter(ticket)
        ticket.lastChange.setText(self.getStrfed())
        kwargs = {
            'user_id': ticket.openUserButton.text(),
            'name': ticket.name.text(),
            'email': ticket.email.text(),
            'phone': ticket.phone.text(),
            'address': ticket.address.toPlainText(),
            'comment': '',
            'change_date':self.getStrfed(),
            'remind_date': self.getStrped(),
            'remind_is_have': 0,
            'from_ticket': True}

        user_id = db.saveUser(**kwargs)
        ticket.openUserButton.setText(str(user_id))

        kwargs = {
            'name': ticket.productName.text(),
            'code': ticket.productCode.text()}
        product_id = db.saveProduct(**kwargs)
        
        kwargs = {
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
            'closed': ticket.checkBox.checkState()}
        ticket_id = db.saveTicket(**kwargs)
        ticket.ticketID.setText(str(ticket_id))

        self.disableEditModeForTicket(ticket)
        if os.path.isdir(self.directory):
            os.renames(self.directory, self.directory.replace('None', ticket.ticketID.text()))

#-----------------------------------------[РАБОТА С ДАТАТАЙМ]
    def getStrfed(self, dt=None):
        """Трансформирует датетайм в строку"""
        try:
            if dt == None: dt = datetime.datetime.now()
            return dt.strftime('%d.%m.%Y %H:%M')
        except: 
            print('Returned dt')
            return dt

    def getStrped(self, string=None) -> str:
        """Трансформирует строку в датетайм"""
        try:
            if string == None: return datetime.datetime.now()
            else: return datetime.datetime.strptime(string, '%d.%m.%Y %H:%M')
        except:  
            print('returned datetime')
            return string

    def getStrpedDate(self, string=None):
        """Трансформирует строку в датетайм"""
        try:
            if string == None: return datetime.datetime.now()
            else: return datetime.datetime.strptime(string, '%d.%m.%Y')
        except:  return string

    def nextDate(self, ui):
        tickets = db.getTicketsByDate(self.getStrpedDate(ui.date.text()))
        self.setMainTableData(tickets, ui)

#-----------------------------------------[ПОИСКОВИК]
    def startSearch(self, ui): 
        query = ui.searchField.text()
        searcher = Searcher(ui)
        tickets = searcher.startSearch(query)
        self.setMainTableData(tickets, ui)


    # def activateAllFlags(self, ui):
    #     ui.allCheckBoxes.setCheckState(2)

    #     ui.searchTicketId.setCheckState(2)
    #     ui.searchUserId.setCheckState(2)
    #     ui.searchOpened.setCheckState(2)
    #     ui.searchClosed.setCheckState(2)
    #     ui.searchName.setCheckState(2)
    #     ui.searchPhone.setCheckState(2)
    #     ui.searchEmail.setCheckState(2)
    #     ui.searchAddress.setCheckState(2)
    #     ui.searchProductName.setCheckState(2)
    #     ui.searchProductCode.setCheckState(2)
    #     ui.searchComment.setCheckState(2)
    #     ui.searchFix.setCheckState(2)
    #     ui.searchReason.setCheckState(2)
    #     ui.searchBrokeComment.setCheckState(2)
    #     ui.searchHaveChange.setCheckState(2)
    #     ui.searchBrokeType.setCheckState(2)
    #     ui.searchSerialNumber.setCheckState(2)

    # def deactivateAllFlags(self, ui):
    #     ui.allCheckBoxes.setCheckState(0)

    #     ui.searchTicketId.setCheckState(0)
    #     ui.searchUserId.setCheckState(0)
    #     ui.searchOpened.setCheckState(0)
    #     ui.searchClosed.setCheckState(0)
    #     ui.searchName.setCheckState(0)
    #     ui.searchPhone.setCheckState(0)
    #     ui.searchEmail.setCheckState(0)
    #     ui.searchAddress.setCheckState(0)
    #     ui.searchProductName.setCheckState(0)
    #     ui.searchProductCode.setCheckState(0)
    #     ui.searchComment.setCheckState(0)
    #     ui.searchFix.setCheckState(0)
    #     ui.searchReason.setCheckState(0)
    #     ui.searchBrokeComment.setCheckState(0)
    #     ui.searchHaveChange.setCheckState(0)
    #     ui.searchBrokeType.setCheckState(0)
    #     ui.searchSerialNumber.setCheckState(0)
        
    # def setFlags(self, ui):
    #     if ui.allCheckBoxes.checkState() == 2:
    #         self.activateAllFlags(ui)

    #     elif ui.allCheckBoxes.checkState() == 0:
    #         self.deactivateAllFlags(ui)

#-----------------------------------------[Data Loader]
    def loadTables(self):
        """Загрузка таблиц"""
        global data 
        data = {}
        datalist = os.listdir(self.basketPath) #получаем спискок файлов в дирректории
        for file in datalist: #перебираем файлы дирректории
            if file.split('.')[1] == 'xlsx' or file.split('.')[1] == 'xls': # пропускаем файлы не формата xlsx
                wb = xlrd.open_workbook(f'{self.basketPath}/{file}') #чтение хлсх файла
                sheet = wb.sheet_by_index(0)
                for i in range(1,sheet.nrows): #Перебираем строки 
                    row = sheet.row_values(i) #Находим очередную строку
                    date = self.getStrfed(xlrd.xldate.xldate_as_datetime(row[0], wb.datemode))
                    ser_num = row[1]
                    model_code = row[2].split('(')[-1][0:-1]
                    model = ''.join(row[2].split('(')[0:-1])
                    problem = row[3]
                    fix = row[4]
                    fio = row[5]
                    email = row[6]
                    phone = row[7]
                    address = row[8]
                    ui = self.ticketView()
                    ui.email.setText(email)
                    self.checkEmail(ui)
                    if ui.phone.text() == "":
                        ui.phone.setText(str(int(phone)))
                        self.checkPhone(ui)
                        if ui.name.text() == "":
                            ui.address.setText(address)
                            ui.name.setText(fio)
                    
                    ui.createDate.setText(date)
                    ui.productName.setText(model)
                    ui.productCode.setText(model_code)
                    ui.serialNumber.setText(ser_num)
                    ui.brokeType.setCurrentIndex(0)
                    ui.changeCode.setText('')
                    ui.changeComment.setText('')
                    ui.reason.setText(problem)
                    ui.fix.setText(fix)
                    ui.comment.setText('')
                    ui.lastChange.setText(self.getStrfed())
                    ui.closeDate.setText(self.getStrfed())
                    ui.checkBox.setCheckState(2)
                    ui.deadLine.setDate(self.getStrped())
                    self.saveTicket(ui)
                    self.openedTickets = []

    def dropData(self): 
        pass


#-----------------------------------------[]
    def phoneFilter(self, ui):
        """Фильтрует номера телефона в поле ввода и устанавливает их заново"""
        new_string = ''
        for number in ui.phone.text().split(' '):
            filtered_number = re.sub('\D', '', number)
            new_string += f'+{filtered_number} '

        ui.phone.setText(new_string.strip())


    def getConfig(self):
        """Возвращает конфиг файл"""
        with open(self.configPath, mode="r",encoding='utf8') as json_file:
            config = json.load(json_file)
        return config


    def _setBrokeTypes(self, ui):
        """Устанавливает значения комбокса поломок в тикете"""
        config = self.getConfig()
        for index, item in enumerate(config['broke types']):
            ui.brokeType.addItem("")
            ui.brokeType.setItemText(index, item)


    def _fillUserData(self, user_id, ui):
        """Заполнение пользователя в тикете """
        if user_id != None:
            user_data = db.getUserData(user_id)
            if ui.email.text() not in user_data['email'].split(' '):
                ui.email.setText(f"{ui.email.text()} {user_data['email']}")

            else: ui.email.setText(user_data['email'])
            ui.openUserButton.setText(user_data['user_id'])
            ui.name.setText(user_data['name'])
            ui.phone.setText(user_data['phone'])
            ui.address.setText(user_data['address'])
            ui.comment.setText(user_data['comment'])
            ui.openUserButton.setEnabled(True)

        else:
            ui.openUserButton.setText('None')
            ui.openUserButton.setEnabled(False)

    def checkEmail(self, ui):
        """Проверяет мыло. если есть заполняет данные пользователя"""
        email = ui.email.text()
        user_id = db.checkEmail(email)
        self._fillUserData(user_id, ui)


    def checkPhone(self, ui):
        """Проверяет телефон. если есть заполняет данные пользователя"""
        self.phoneFilter(ui)
        phone = ui.phone.text()
        user_id = db.checkPhone(phone)
        self._fillUserData(user_id, ui)
    

    def closeTicket(self, ui):
        """Выставляет дату закрытия тикета или убирает её"""
        if ui.checkBox.checkState() == 2:
            ui.closeDate.setText(self.getStrfed())

        elif ui.checkBox.checkState() == 0:
            ui.closeDate.setText('None')


    def showFiles(self, ticket_id):
        """Открытие директории тикета"""
        directory = self.directory.replace('None', ticket_id)
        if not os.path.isdir(directory):
            os.mkdir(directory)

        os.startfile(directory)


    def getFileCounts(self, ticket_id):
        """Возвращает количество файлов в папке тикета"""
        directory = self.directory.replace('None', ticket_id)
        if not os.path.isdir(directory):
            return '0'
        return str(len(os.listdir(directory)))


    def verification(self, ui):
        """Обработка логинки"""
        try:
            if self.getConfig()['login'][ui.login.text()] == ui.password.text():
                self.openMainWindow()
                del self.Login   
            else:
                ui.label.setText('Вы кто такие? Я вас не звал!')

        except KeyError:
            ui.label.setText('Вы кто такие? Я вас не звал!')


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    logging.info('start application')
    mainobj = Main()
    logging.info('exit from application')
    sys.exit(app.exec_())

    
