import sqlite3
conn = sqlite3.connect(r'C:\Users\franklin.song\Desktop\DSAI\Engineering-and-Design\eks\output\eks_registry.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Tables:', tables)
for t in tables:
    tname = t[0]
    cursor.execute(f'PRAGMA table_info({tname})')
    cols = cursor.fetchall()
    print(f'\n--- {tname} columns ---')
    for c in cols:
        print(c)
    cursor.execute(f'SELECT COUNT(*) FROM {tname}')
    count = cursor.fetchone()[0]
    print(f'Row count: {count}')
conn.close()