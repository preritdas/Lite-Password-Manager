#import os
import sys, getpass
import sqlite3 as sql
from cryptography.fernet import Fernet

"""This is the main class representing a Password object and all associated methods"""
class Password_Obj:
   
    def __init__(self,account_description = None, user = None, _password = None, email = None, *encrypted_password):
        """Password constructor method"""
        self.account_description = account_description
        self.user = user
        self.email = email
        self.password = _password
        self.encrypted_password = encrypted_password

    def get_password_info(self, cursor, sql_connection):
        """Getting the password data from DB based on account description"""   
        print("\nPlease enter the account description")
        account_description = input("Account description: ")
        try:
            cursor.execute(
                f"""
                SELECT * FROM Passwords WHERE account_description == '{account_description}'
                """)
            password_data = cursor.fetchone()
            sql_connection.close()
        except sql_connection.Error as error:
            print(error)
        return self.format_password_data(password_data)
        
    def show_all_passwords(self, cursor, sql_connection):
        """Function to retrieve all the passwords from the SQL DB"""
        try:
            cursor.execute("""SELECT * FROM Passwords""")
            password_data= cursor.fetchall()
        except sql_connection.Error as error:
            print(f"SQL database error: {error}")
        sql_connection.close()

        return self.format_password_data(password_data)

    def request_password_info(self):
        """Requesting data from users to instantiate the class/object representing a password"""
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
                password_validation = input() #Need to secure this input

        print("\nPlease enter the email associated to the account:")
        email = input()

        return account_description, user,_password, email

    def format_password_data(self,password_data):
        password_dict = {"Account Description":None,
                        "User":None,
                        "Password":None,
                        "Email":None}
        p_keys = password_dict.keys()
        if type(password_data) == list:
            for password in password_data:
                for i in p_keys:
                    print(p_keys + password)
        if type(password_data) == tuple:
            print(password_data)
        return password_dict
    
    def encrypt_password(self, _password, fernet):
        string = _password.encode()
        self.encrypted_password = fernet.encrypt(string)

    def decrypt_password(self, encrypted_password, fernet):
        decrypted_password= fernet.decrypt(encrypted_password)
        return decrypted_password.decode()

    def init_SQL_Db(self, sql):
        """Intializing SQL Lite Data base"""
        try:
            sql_connection = sql.connect("db\sql.db")
            cursor = sql_connection.cursor()
            query = 'select sqlite_version();'
            cursor.execute(query)
            result = cursor.fetchall()
        except sql.Error as error:
            print(f"SQL database error: {error}")
        
        return sql_connection, cursor
    
    def create_check_db_table(self, cursor):
        """Create table if not already, otherwise return existing table"""
        try:
            table = cursor.execute(  
                """
                CREATE TABLE IF NOT EXISTS Passwords (
                account_description CHAR(255) NOT NULL,
                user CHAR(255) NOT NULL,
                encrypted_password TEXT NOT NULL,
                email CHAR(255) NOT NULL);
                """
                )
        except table.Error as error:
            print(f"SQL database table error: {error}")
        return table

    def save_password_db(self, cursor, sql_connection):
        try:
            cursor.execute(f''' 
                INSERT INTO Passwords VALUES ("{self.account_description}", "{self.user}", "{self.password}","{self.email}");
            ''')
            print("Password has been saved successfully")
        except sql_connection.Error as error:
            print(f"SQL database error: {error}")
        sql_connection.commit()
        sql_connection.close()

def main(argv):
    """Instantiating the Password object as empty, we'll fill out the data later on"""
    Password = Password_Obj()

    """Let's init the DB"""
    sql_connection, cursor = Password.init_SQL_Db(sql)

    """Creating table, otherwise returning an existing table"""
    db_table = Password.create_check_db_table(cursor)

    """Parsing arguments"""
    #Check on this later! 
    argv_index = argv.index(argv[0])
    if argv_index == 0:
        if argv[argv_index] == "--newpassword":
            """Requesting information to the user"""
            account_description, user, _password, email = Password.request_password_info()

            """Since we now have data from the user, let's fill up the empty Password Object"""   
            Password.__init__(account_description, user, _password, email)

            """Encrypting Password"""
            #Password.encrypt_password(_password, fernet)

            """Saving Password to SQL Password DB"""
            Password.save_password_db(cursor, sql_connection)
            sys.exit(0)

        elif argv[argv_index] == "--showallpasswords":
            print("showing all passwords")
            all_passwords = Password.show_all_passwords(cursor, sql_connection)
            print(all_passwords)
            sys.exit(0)

        elif argv[argv_index] == "--getpassword":
            """For now lets just print the data stored on the password object"""
            Password.get_password_info(cursor, sql_connection)
            sys.exit(0)

        elif argv[argv_index] == "--help":
            print("Displaying usage options")
            sys.exit(0)

    else:
        print("Use --help to see options")
        sys.exit(0)
        
if __name__ == '__main__':
    """Main will receive the arguments"""
    main(sys.argv[1:])