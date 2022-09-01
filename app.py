import os, os.path
import sys, getpass
import sqlite3 as sql
from cryptography.fernet import Fernet

KEY_PATH = "key//fernet_key.txt"

"""This is the main class representing a Password object and all associated methods"""
class Password_Obj:
   
    def __init__(self,account_description = None, user = None, _password = None, email = None, *encrypted_password):
        """
        Password Object constructor, it will init with default None values.

        Args:
            account_description: Describing the account associated with the password. Defaults to None.
            user: User account. Defaults to None.
            _password: Password for the associated password. Defaults to None.
            email: Email for the associated password. Defaults to None.
        """
        self.account_description = account_description
        self.user = user
        self.email = email
        self.password = _password
        self.encrypted_password = encrypted_password

    def get_password_info(self, cursor, sql_connection, account_description, fernet):
        '''
        Requesting account description from the user to then query the DB

        Args:
            cursor: SQL cursor object
            sql_connection: SQL object connection
            account_description: Account associated with the password
            fernet: Fernet object to encrypt or decrypt the password

        Returns:
            dict: password_data
        '''
        try:
            cursor.execute(
                f"""
                SELECT * FROM Passwords WHERE account_description == '{account_description}'
                """)
            password_data = cursor.fetchone()
            
        except sql_connection.Error as error:
            print(f"SQL database error: {error}")
            sql_connection.close()
        return self.format_password_data(password_data, fernet)
        
    def show_all_passwords(self, cursor, sql_connection, fernet):
        '''
        Function to retrieve all the passwords from the SQL DB

        Args:
            cursor: SQL cursor object
            sql_connection: SQL object connection
            fernet: Fernet object to encrypt or decrypt the password

        Returns:
            dict: password_data
        '''
        try:
            cursor.execute("""SELECT * FROM Passwords""")
            password_data= cursor.fetchall()
        except sql_connection.Error as error:
            print(f"SQL database error: {error}")
            sql_connection.close()

        return self.format_password_data(password_data, fernet)
    
    def delete_password(self, cursor, sql_connection, account_description):
        '''
        Deleting password based on the account description enter by the user

        Args:
            cursor: SQL cursor object
            sql_connection: SQL object connection
            account_description: Describing the account associated with the password. 

        Returns:
            bool: b_deleted if the password was deleted successfully
        '''
        password_to_delete = self.get_password_info(cursor, sql_connection, account_description)
        b_deleted = False
        if not password_to_delete:
            print(f"Password associated with with the account description: {account_description} was not found!")
        else:
            [print(password) for password in password_to_delete]
            confirmation = input("Please enter Y or Yes if you want to delete the password, enter C or Cancel to cancel the operation: ")
            if confirmation == "Y" or confirmation == "Yes":
                try:
                    cursor.execute(f"""DELETE FROM Passwords WHERE account_description == '{account_description}'""")
                    sql_connection.commit()
                    b_deleted = True
                except sql_connection.Error as error:
                    print(f"SQL database error: {error}")
                    sql_connection.close()
            elif confirmation == "C" or confirmation == "Cancel":
                print("Canceling operation")
        return b_deleted

    def request_password_info(self):
        '''
        Requesting data from users to instantiate the class/object representing a password
        
        Args:
            Password Object

        Returns:
            strings : account_description, user, _password, email
        '''

        print("\nPlease enter the following information to create a new password in the Lite Password Manager\n")

        # print("\nPlease enter a description:")
        account_description = input("Please enter a description:")

        # print("\nPlease enter the user name:")
        user = input("Please enter the user name:")

        print("Please enter the password for this account:")
        _password = getpass.getpass(prompt="")

        print("Please enter again the password to confirm is valid:")
        password_validation = getpass.getpass(prompt="")

        """Here we are validating the entered password is valid or that at least matches"""
        while True:
            if _password == password_validation:
                print("Password is valid\n")
                break
            else:
                print("Password is not valid, please try again:")
                password_validation = getpass.getpass(prompt="")

        # print("\nPlease enter the email associated to the account:")
        email = input("Please enter the email associated to the account:")

        return account_description, user,_password, email

    def format_password_data(self, password_data, fernet):
        """Here we are going to format the password data to a dict and also decrypt the password"""
        password_dict = []
        password_dict_keys = ["Account Description",
                        "User",
                        "Password",
                        "Email"]
        if type(password_data) == list:
            for password in password_data:
                password_dict.append(dict(zip(password_dict_keys,password)))
        if type(password_data) == tuple:
            password_dict.append(dict(zip(password_dict_keys,password_data)))
        return self.decrypt_password(password_dict, fernet)
    
    def init_encryption_keys(self, Fernet):
        """
        First we check if the file extist and if it is empty
        it could be possible the file exists but does not have a Fernet key stored    
        """
        b_file_exists = os.path.exists(KEY_PATH)
        
        #File exists on directory
        if b_file_exists:
            #File is not empty
            b_file_empty = os.stat(KEY_PATH).st_size != 0
            if b_file_empty:
                #Let's read the file and retrive the fernet key
                with open(KEY_PATH, "r") as file:
                    key = file.read()
                    key = key.encode()
        else:
            #If there is not a file holding the key, then let's create the file and generate the fernet key
            with open(KEY_PATH, "w") as file:
                key = Fernet.generate_key()
                file.write(key.decode("utf-8"))
        fernet = Fernet(key)
        return fernet

    def encrypt_password(self, _password, fernet):
        '''
        Encrypting password using the fernet object

        Args:
            _password: Password to encrypt
            fernet: Fernet object to encrypt or decrypt the password
        '''
        string = _password.encode()
        self.encrypted_password = fernet.encrypt(string)

    def decrypt_password(self, password_dict, fernet):
        '''
        Decrypting password using the fernet object, this function will be called 
        from the Format Data Function and return a dict containing the password data

        Args:
            password_dict : Dictionary containing the password data
            fernet: Fernet object to encrypt or decrypt the password

        Returns:
            dict: password_dict
        '''
        for data in password_dict:
            encrypted_password = data["Password"]
            encrypted_password = encrypted_password.strip("b'")
            encrypted_password = str.encode(encrypted_password)
            encrypted_password = fernet.decrypt(encrypted_password)
            data["Password"] = encrypted_password.decode()
        return password_dict 

    def init_SQL_Db(self, sql):
        """Intializing SQL Lite Data base"""
        try:
            sql_connection = sql.connect("db\sql.db")
            cursor = sql_connection.cursor()
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
                encrypted_password BLOB NOT NULL,
                email CHAR(255) NOT NULL);
                """
                )
        except table.Error as error:
            print(f"SQL database table error: {error}")
        return table

    def save_password_db(self, cursor, sql_connection):
        try:
            cursor.execute(f''' 
                INSERT INTO Passwords VALUES ("{self.account_description}", "{self.user}", "{self.encrypted_password}","{self.email}");
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

    fernet = Password.init_encryption_keys(Fernet)

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
            Password.encrypt_password(_password, fernet)

            """Saving Password to SQL Password DB"""
            Password.save_password_db(cursor, sql_connection)
            sys.exit(0)

        elif argv[argv_index] == "--showallpasswords":
            print("showing all passwords")
            all_passwords = Password.show_all_passwords(cursor, sql_connection, fernet)
            if not all_passwords:
                print("No passwords were found in the database")
            else:
                [print(passwords) for passwords in all_passwords]
            sys.exit(0)

        elif argv[argv_index] == "--getpassword":
            """For now lets just print the data stored on the password object"""
            print("\nPlease enter the account description")
            account_description = input("Account description: ")
            passwords = Password.get_password_info(cursor, sql_connection, account_description, fernet)
            if not passwords:
                print("Password was not found, try again")
            else:
               [print(password) for password in passwords] 
            sys.exit(0)
        
        elif argv[argv_index] == "--deletepassword":
            """Delete the password from the database based on the account description"""
            print("\nPlease enter the account description")
            account_description = input("Account description: ")
            b_success = Password.delete_password(cursor, sql_connection, account_description)
            if b_success:
                print(f"Password associated with {account_description} was deleted successfully")
            else:
                print(f"Password associated with {account_description} was not deleted, check the account description and try again")
            sys.exit(0)

        elif argv[argv_index] == "--help":
            print("Displaying usage options:\n")
            print("Option --newpassword: Creates a new password.\n")
            print("Option --showallpasswords: Retrieves all the passwords from the database.\n")
            print("Option --getpassword: Retrieves the password based on the account description.\n")
            sys.exit(0)

    else:
        print("Use --help to see options")
        sys.exit(0)
        
if __name__ == '__main__':
    """Main will receive the arguments"""
    main(sys.argv[1:])