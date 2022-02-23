from peewee import *
import datetime
import os
dbPath = f"{os.getcwd()}\data\db.sqlite3"
db = SqliteDatabase(dbPath)

class BaseModel(Model):
    class Meta: database = db
    id = AutoField()


class User(BaseModel):
    class Meta: db_table = 'Users'
    name = TextField()
    address = TextField()
    comment = TextField()
    change_date = TextField()
    remind_date = DateTimeField()
    remind_is_have = IntegerField()


class Phone(BaseModel):
    class Meta: db_table = 'Phones'
    user_id = ForeignKeyField(User)
    phone = IntegerField()


class Email(BaseModel):
    class Meta: db_table = 'Emails'
    user_id = ForeignKeyField(User)
    email = IntegerField()


class Product(BaseModel):
    class Meta: db_table = 'Products'
    name = TextField()
    code = TextField()


class Ticket(BaseModel):
    class Meta: db_table = 'Tickets'
    user_id = ForeignKeyField(User)
    product_id = ForeignKeyField(Product)    
    serial_number = TextField()
    break_type = IntegerField()
    changed_number = TextField()
    changed_comment = TextField()
    reason = TextField()
    fix = TextField()
    comment = TextField()
    open_date = DateTimeField()
    change_date = DateTimeField()
    close_date = DateTimeField()
    deadline = DateTimeField()
    closed = IntegerField()

# if __name__ == '__main__':
#     with db:
#         db.create_tables([User, Phone, Email, Ticket, Product])
    

#     print('DONE')
if not os.path.exists(dbPath):
    with db:
        db.create_tables([User, Phone, Email, Ticket, Product])