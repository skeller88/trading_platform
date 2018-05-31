from core.src.properties.env_properties import EnvProperties
from core.src.storage.setup_db import setup_remote_sql_alchemy, setup_local_sql_alchemy
from trading_platform.storage.sql_alchemy_dtos import table_classes


def main(event, context):
    table_classes.all_tables()
    if EnvProperties.env == 'prod':
        engine = setup_remote_sql_alchemy()
    else:
        engine = setup_local_sql_alchemy()

    print('closing connections')
    engine.dispose()


if __name__ == '__main__':
    main(None, None)