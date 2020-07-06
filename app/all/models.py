from . import *

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
DATABASE = PROJECT_DIR + '/matcha.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


class Model:
    table = None

    def init(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return self

    def exists(self):
        return True if len(self.__dict__) > 0 else False

    def all(self, only=None):
        db = get_db()
        cur = db.cursor()
        cur.execute("select * from {} order by id;".format(self.table))
        column_names = [d[0] for d in cur.description]
        result = list()
        for row in cur.fetchall():
            result.append(copy(self.init(**dict(zip(column_names, row)))))
        if only:
            new_result = [getattr(d, only) for d in result]
            return new_result
        return result

    def get(self, **kwargs):
        db = get_db()
        cur = db.cursor()
        wheres = list()
        if len(kwargs) == 0:
            return None
        for i, j in kwargs.items():
            wheres.append("{} = '{}'".format(i, j))
            wherestr = " and ".join(wheres)
        cur.execute("select * from {} where {};".format(self.table, wherestr))
        column_names = [d[0] for d in cur.description]
        for row in cur.fetchall()[0:1]:
            self.init(**dict(zip(column_names, row)))
            return self
        return self

    def filter(self, **kwargs):
        db = get_db()
        cur = db.cursor()
        wheres = list()
        result = list()
        if len(kwargs) == 0:
            return None
        for i, j in kwargs.items():
            wheres.append("{} = '{}'".format(i, j))
            wherestr = " and ".join(wheres)
        cur.execute("select * from {} where {} order by id;".format(self.table, wherestr))
        column_names = [d[0] for d in cur.description]
        for row in cur.fetchall():
            result.append(copy(self.init(**dict(zip(column_names, row)))))
        return result

    def create(self, **kwargs):
        db = get_db()
        cur = db.cursor()
        fields = list()
        values = list()
        if len(kwargs) == 0:
            return None
        for i, j in kwargs.items():
            if type(i) is str:
                fields.append("{}".format(escape(i)))
            else:
                fields.append("{}".format(i))
            if type(j) is str:
                values.append("'{}'".format(escape(j)))
            else:
                values.append("{}".format(j))
        fieldstr = ", ".join(fields)
        valuestr = ", ".join(values)
        query = "insert into {}({}) values({})".format(self.table, fieldstr, valuestr)
        cur.execute(query)
        db.commit()

    def update(self, field, field_value, **kwargs):
        db = get_db()
        cur = db.cursor()
        if len(kwargs) > 0:
            sets = list()
            for i, j in kwargs.items():
                sets.append("{} = '{}'".format(i, j))
            setstr = ", ".join(sets)
            try:
                cur.execute("update {} set {} where {} = '{}';".format(self.table, setstr, field, field_value))
                db.commit()
            except:
                db.rollback()

    def delete(self, field, field_value):
        db = get_db()
        cur = db.cursor()
        try:
            cur.execute("delete from {} where {} = '{}';".format(self.table, field, field_value))
            db.commit()
        except:
            db.rollback()


class User(Model):
    table = "users"


class Chats(Model):
    table = "chats"


class Tags(Model):
    table = "tags"


class Likes(Model):
    table = "likes"


class Visits(Model):
    table = "visits"


class Notifs(Model):
    table = "notifs"


class Reports(Model):
    table = "reports"


class Blocks(Model):
    table = "blocks"
