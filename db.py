import sqlite3
from datetime import datetime, timedelta


class Lorin():
    def __init__(self, db='lorin.db'):
        self.con = sqlite3.connect(db)
        self.cur = self.con.cursor()
        self.init_db()

    def init_db(self):
        probes = '''
            CREATE TABLE IF NOT EXISTS probes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mac TEXT,
                enter_datetime DATETIME,
                last_seen DATETIME,
                exited BOOLEAN DEFAULT False
            )
        '''

        mac_log = '''
        CREATE TABLE IF NOT EXISTS mac_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mac TEXT,
            enter_datetime DATETIME,
            last_seen DATETIME,
            hz INTEGER DEFAULT 0
        )
        '''

        self.cur.execute(probes)
        self.cur.execute(mac_log)
        self.cur.execute('''
            CREATE INDEX IF NOT EXISTS last_seen_index ON probes (last_seen)
            ''')
        self.cur.execute('''
            CREATE INDEX IF NOT EXISTS mac_index ON probes (mac)
            ''')
        self.con.commit()

    def insert_update_log(self, mac):
        """Insert or Update probe data.

        mac: str 01:01:01:01:01:01
        """

        self.cur.execute(
            f'SELECT * FROM probes WHERE mac="{mac}" AND exited="False" ')
        probe = self.cur.fetchone()

        self.cur.execute(f'SELECT * FROM mac_log WHERE mac="{mac}" ')
        mac_log = self.cur.fetchone()

        time_stamp = datetime.now()

        def new_log():

            query = f'''
                INSERT INTO probes (
                    mac,
                    enter_datetime,
                    last_seen
                ) VALUES ('{mac}', '{time_stamp}', '{time_stamp}' )
                '''
            try:
                self.cur.execute(query)
            except Exception as e:
                self.con.rollback()
                print(e)
        if not mac_log:
            try:
                self.cur.execute(f"""
                    INSERT INTO mac_log (mac, enter_datetime, last_seen, hz)
                    VALUES ('{mac}', '{time_stamp}', '{time_stamp}', '1')
                """)

            except Exception as e:
                self.con.rollback()
                print(e)

        if probe:
            print('\033[91m' + f'Updating device {mac} last seen = {time_stamp}' + '\033[0m')
            try:
                query = f'''
                    UPDATE probes set last_seen='{time_stamp}'
                    WHERE mac='{mac}' AND enter_datetime='{probe[2]}'
                '''
                self.cur.execute(query)
            except Exception as e:
                print(e)

            enter_datetime = datetime.strptime(
                probe[2], '%Y-%m-%d %H:%M:%S.%f')
            last_seen = datetime.strptime(probe[3], '%Y-%m-%d %H:%M:%S.%f')
            time_diff_up_8h = divmod(
                (last_seen - enter_datetime).total_seconds(), 3600)

            if time_diff_up_8h[0] > 0.5:
                print('\033[96m' + f'Updating Mac Graphs.... \033[0m')
                try:
                    query = f'''
                        UPDATE probes set exited="True"
                        WHERE mac='{mac}' AND enter_datetime='{probe[2]}'
                    '''
                    self.cur.execute(query)
                except Exception as e:
                    print(e)

                new_log()
            if mac_log:
                try:
                    hz = int(mac_log[4]) + 1
                    self.cur.execute(f"""
                        UPDATE mac_log SET hz='{hz}', last_seen='{time_stamp}' WHERE mac="{mac}"
                    """)

                except Exception as e:
                    self.con.rollback()
                    print(e)
        else:
            print('\033[93m' + f'Logging a new device:  {mac} | last seen: {time_stamp}' + '\033[0m')
            new_log()

        self.con.commit()

    def tearDown(self):
        self.con.commit()
        self.con.close()
