import sqlite3

print('Job resetdb located at: extra/resetdb.py version: 1.0 is about to start on runner: local')

DATABASE_NAME = 'users.db'

#Settings override

OVERRIDE_SETTINGS_AND_DELETE_ALL = 'true'
print('OVERRIDE_SETTINGS_AND_DELETE_ALL: ' + OVERRIDE_SETTINGS_AND_DELETE_ALL)

#Settings
if OVERRIDE_SETTINGS_AND_DELETE_ALL != 'true':
    DELETE_USERS = 'true'
    print('DELETE_USERS: ' + DELETE_USERS)
    DELETE_API_KEYS = 'true'
    print('DELETE_API_KEYS: ' + DELETE_API_KEYS)
    DELETE_VERIFY_CODES = 'true'
    print('DELETE_VERIFY_CODES: ' + DELETE_VERIFY_CODES)
    DELETE_USER_SESSIONS = 'true'
    print('DELETE_USER_SESSIONS: ' + DELETE_USER_SESSIONS)
    DELETE_SIGNED_IN_WITH_SCRATCHAUTH_USERS = 'true'
    print('DELETE_SIGNED_IN_WITH_SCRATCHAUTH_USERS: ' + DELETE_USER_SESSIONS)


#Code
conn = sqlite3.connect(DATABASE_NAME)
c = conn.cursor()

if OVERRIDE_SETTINGS_AND_DELETE_ALL != 'true':
  if DELETE_USERS == 'true':
      print('Deleting users')
      c.execute('DELETE FROM users;')
      c.execute('DELETE FROM verify;') 
  if DELETE_API_KEYS == 'true':
      print('Deleting api keys')
      c.execute('DELETE FROM keys;')
  if DELETE_VERIFY_CODES == 'true':
      c.execute('DELETE FROM verifycode;')
      print('Deleting verification codes')
  if DELETE_USER_SESSIONS == 'true':
      c.execute('DELETE FROM strings;')
      print('Deleting user sessions')
  if DELETE_SIGNED_IN_WITH_SCRATCHAUTH_USERS == 'true':
      c.execute('DELETE FROM specialAccounts;')
      print('Deleting Signed in with scratch auth users')
  

else:
  print('DELETING EVERYTHING VIA OVERRIDE_SETTINGS_AND_DELETE_ALL')
  c.execute('DELETE FROM users;')
  c.execute('DELETE FROM verifycode;')
  c.execute('DELETE FROM keys;')
  c.execute('DELETE FROM verify;') 
  c.execute('DELETE FROM strings;')
  c.execute('DELETE FROM specialAccounts;')


print('Commiting changes')
conn.commit()

print('Closing database connection')
conn.close()

print('Job resetdb has been completed.')