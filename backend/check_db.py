import sqlite3

conn = sqlite3.connect('agent_mark.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Tables:', tables)

if ('users',) in tables:
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f'User count: {user_count}')
    
    if user_count > 0:
        cursor.execute("SELECT id, username FROM users LIMIT 5")
        users = cursor.fetchall()
        print('Sample users:', users)

if ('files',) in tables:
    cursor.execute("SELECT COUNT(*) FROM files")
    file_count = cursor.fetchone()[0]
    print(f'File count: {file_count}')

conn.close()
