from peewee import Model, CharField, PostgresqlDatabase


class ItemModel(Model):
    item_id = CharField(primary_key=True)
    description = CharField()

    class Meta:
        table_name = "items"
        database = PostgresqlDatabase("postgres_db",
                                      user="postgres_user",
                                      password="postgres_password",
                                      host="localhost",
                                      port="5430")
