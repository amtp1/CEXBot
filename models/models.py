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
        "last_name": orm.String(max_length=128, allow_null=True)
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
        "created": orm.DateTime(default=dt.utcnow()),
        "finished": orm.DateTime(allow_null=True)
    }
