import sqlite3
import shelve
import cfg


class SQLighter:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def select_for_params(self, **kwargs):
        """Create query by user params

        returned list of names"""
        query = f"SELECT name FROM pet_names WHERE"
        query_args = ()
        query_conditions = []
        for key in kwargs.keys():
            if key == "name":
                query_conditions.append(f" name LIKE \'{kwargs['name']}%\'")
            else:
                query_conditions.append(f" {str(key)} = ?")
                query_args += (kwargs[key],)
        query += " AND".join(query_conditions)
        # Sending a query to database
        with self.connection:
            res = self.cursor.execute(query, query_args).fetchall()
            return [i for sub in res for i in sub if i]

    def get_buttons(self, field):
        """Returned list of buttons"""
        with self.connection:
            query = f"SELECT DISTINCT {field} FROM pet_names"
            res = self.cursor.execute(query).fetchall()
            return [i for sub in res for i in sub if i]

    def get_random(self):
        with self.connection:
            query = f"SELECT name FROM pet_names"
            res = self.cursor.execute(query).fetchall()
            return [i for sub in res for i in sub if i]


def new_user(user_id, user_name):
    with shelve.open(cfg.storage) as storage:
        storage[str(user_id)] = {
            "name": user_name,
            "response_list": [],
            "params": {},
            "filters": {}}


def update_data(user_id, params=None, response_list=None, filters=None):
    with shelve.open(cfg.storage) as storage:
        if params:
            # storage[str(user_id)]["params"].update(params) - Does not work ;(
            temporary = storage[str(user_id)]
            temporary["params"].update(params)
            storage[str(user_id)] = temporary
        if response_list:
            temporary = storage[str(user_id)]
            temporary["response_list"] = response_list
            storage[str(user_id)] = temporary
        if filters:
            temporary = storage[str(user_id)]
            temporary["filters"].update(filters)
            storage[str(user_id)] = temporary


def get_data(user_id, data_type="all_data"):
    with shelve.open(cfg.storage, flag="r") as storage:
        if str(user_id) not in storage:
            print("Not Exists")
        elif data_type == "all_data":
            print(storage[str(user_id)])
            return storage[str(user_id)]
        else:
            return storage[str(user_id)][data_type]


def clear_storage():
    with shelve.open(cfg.storage) as storage:
        storage.clear()


def get_users_count():
    with shelve.open(cfg.storage) as storage:
        return len(storage)
