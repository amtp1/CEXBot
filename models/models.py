from datetime import datetime as dt

import orm
import databases

database = databases.Database("sqlite+aiosqlite:///CEXBot.sqlite")
models = orm.ModelRegistry(database=database)


class User(orm.Model):
    tablename = "users"
    registry = models
    fields = {
        "id": orm.Integer(primary_key=True),
        "user_id": orm.Integer(),
        "username": orm.String(max_length=128, allow_null=True),
        "first_name": orm.String(max_length=128, allow_null=True),
        "last_name": orm.String(max_length=128, allow_null=True),
        "is_chat": orm.Boolean(default=False),
    }


class Deal(orm.Model):
    tablename = "deals"
    registry = models
    fields = {
        "id": orm.Integer(primary_key=True),
        "user": orm.ForeignKey(User, on_delete=orm.CASCADE),
        "send": orm.String(max_length=64),
        "receive": orm.String(max_length=64),
        "method": orm.String(max_length=128),
        "amount": orm.Float(),
        "is_cancel": orm.Boolean(default=False),
        "created": orm.DateTime(default=dt.utcnow()),
        "finished": orm.DateTime(allow_null=True)
    }


class TechnicalTask(orm.Model):
    tablename = "technical_tasks"
    registry = models
    fields = {
        "id": orm.Integer(primary_key=True),
        "deal": orm.ForeignKey(Deal, on_delete=orm.CASCADE),
        "content": orm.Text()
    }


class File(orm.Model):
    tablename = "files"
    registry = models
    fields = {
        "id": orm.Integer(primary_key=True),
        "deal": orm.ForeignKey(Deal, on_delete=orm.CASCADE),
        "title": orm.String(max_length=255),
        "path": orm.String(max_length=255),
        "type": orm.String(max_length=128),
        "is_member": orm.Boolean(),
        "created": orm.DateTime(default=dt.utcnow())
    }
