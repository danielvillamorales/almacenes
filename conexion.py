import cx_Oracle

cx_Oracle.init_oracle_client(lib_dir=r"C:\instantclient")


class conexion:
    def con():
        conexion = None
        try:
            conexion = cx_Oracle.connect(
                user="ka",
                password="K#0stazul",
                dsn="10.10.5.112:1521/oceanic",
                encoding="UTF-8",
            )
            # print(f'verison bd: {conexion.version}')
            return conexion
        except Exception as e:
            print(f"error verison bd: {e}")
        # finally:
        #    conexion.close()
