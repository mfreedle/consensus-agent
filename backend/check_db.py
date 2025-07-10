import sqlite3

conn = sqlite3.connect('agent_mark.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Tables:', tables)

if ('users',) in tables:
    # First, check the schema of the users table
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    print('\n📋 Users table schema:')
    for col in columns:
        print(f'  {col[1]} ({col[2]})')
    
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f'\nUser count: {user_count}')
    
    if user_count > 0:
        print('\n👥 All Users in Database:')
        print('=' * 50)
        
        # Get all column names
        column_names = [col[1] for col in columns]
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        
        for user in users:
            for i, value in enumerate(user):
                if i < len(column_names):
                    col_name = column_names[i]
                    if 'password' in col_name.lower() and value:
                        print(f'{col_name}: {str(value)[:20]}...')
                    else:
                        print(f'{col_name}: {value}')
            print('-' * 30)

if ('files',) in tables:
    cursor.execute("SELECT COUNT(*) FROM files")
    file_count = cursor.fetchone()[0]
    print(f'File count: {file_count}')

conn.close()
