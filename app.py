from ast import arg
import sys, getpass
import sqlite3 as sql
from cryptography.fernet import Fernet

key = Fernet.generate_key()
fernet = Fernet(key)

"""This is the main class representing a Password object and all associated methods"""
class Password_Obj:
   
    def __init__(self,account_description = None, user = None, _password = None, email = None, *encrypted_password):
        """Password constructor method"""
        self.account_description = account_description
        self.user = user
        self.email = email
        self.password = _password
        self.encrypted_password = encrypted_password

    def get_password_info(self):
        """Getting the passowrd data from the user"""   
        print("\nUser's Password data:\n")
        print(f"Account Description: {self.account_description}")
        print(f"User: {self.user}")
        print(f"Email {self.email}")
        print(f"Password: {self.password}")
        print(f"Encrypted Password: {self.encrypted_password}")
        
    def request_password_info(self):
        """Requesting data from users to Instantiate the class/object representing a password"""
        print("\nPlease enter the following information to create a new password in the Lite Password Manager\n")

        print("\nPlease enter a description:")
        account_description = input()

        print("\nPlease enter the user name:")
        user = input()

        print("\nPlease enter the password for this account:")
        _password = getpass.getpass(prompt=" ")

        print("\nPlease enter again the password to confirm is valid:")
        password_validation = getpass.getpass(prompt=" ")

        """Here we are validating the entered password is valid or that at least matches"""
        while True:
            if _password == password_validation:
                print("\nPassword is valid\n")
                break
            else:
                print("\nPassword is not valid, please try again:")
                password_validation = input()

        print("\nPlease enter the email associated to the account:")
        email = input()

        return account_description, user,_password, email
    
    def encrypt_password(self):
        string = self.password.encode()
        self.encrypted_password = fernet.encrypt(string)

    def load_password_database(self):
        return

    def init_SQL_Db(self, sql):
        """Intializing SQL Lite Data base"""
        try:
            sql_connection = sql.connect("db\sql.db")
            cursor = sql_connection.cursor()
            print("SQL database initialized")
            query = 'select sqlite_version();'
            cursor.execute(query)
            result = cursor.fetchall()
            print(f"SQL database version {result}")
        except sql.Error as error:
            print(f"SQL database error: {error}")
        
        return sql_connection, cursor
    
    def create_check_db_table(self, cursor):
        """Create table if not already, otherwise return existing table"""
        table = cursor.execute(  """CREATE TABLE IF NOT EXISTS Passwords (
            account_description CHAR(255) NOT NULL,
            user CHAR(255) NOT NULL,
            encrypted_password CHAR(255) NOT NULL,
            email CHAR(255) NOT NULL
        )""")
        if table is not None:
            print("Passwords table exist")
        else:
            print("Passwords table not exist")
        return table

def main(argv):
    """Instantiating the Password object as empty, we'll fill out the data later on"""
    Password = Password_Obj()

    """Let's first init the DB"""
    sql_connection, cursor = Password.init_SQL_Db(sql)

    """Creating table, otherwise returning existing table"""
    db_table = Password.create_check_db_table(cursor)

    """Arguments system"""
    argv_index = argv.index(argv[0])
    if argv_index == 0:
        if argv[argv_index] == "--newpassword":
            """Requesting information to the user"""
            account_description, user, _password, email = Password.request_password_info()
        elif argv[argv_index] == "--showallpasswords":
            print("showing all passwords")
        elif argv[argv_index] == "--getpassword":
            """For now lets just print the data stored on the password object"""
            Password.get_password_info()
        elif argv[argv_index] == "--help":
            print("Displaying usage options")
            sys.exit(0)
    else:
        print("Use --help to see options")
        sys.exit(0)
        
    """Since we now have data from the user, let's fill up the empty Password Object"""   
    Password.__init__(account_description, user, _password, email)

    """Encrypting Password"""
    Password.encrypt_password()

if __name__ == '__main__':
    """Main will receive the arguments"""
    main(sys.argv[1:])