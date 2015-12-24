import csv
import os
import sqlite3

def clean_existing_db(path):
    try:
        os.remove(path)
    except OSError:
        pass

def import_csv(path):
    tokens = path.split('/')
    file_name = tokens[-1]
    sql_file_name = file_name.replace('csv', 'db')

    clean_existing_db(sql_file_name)

    conn = sqlite3.connect(sql_file_name)
    c = conn.cursor()

    with open(path, 'rb') as f:
        rdr = csv.reader(f)
        header = rdr.next()
        c.execute('''CREATE TABLE data (sn text, result real)''')

        for row in rdr:
            c.execute("""insert into data values (?,?)""", row)
            
    conn.commit()
    conn.close()