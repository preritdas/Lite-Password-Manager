"""Create the main Password object."""
import os, os.path
import sys, getpass
import sqlite3 as sql
from cryptography.fernet import Fernet


KEY_PATH = "key//fernet_key.txt"


class Password:
    """This is the main class representing a Password object and all associated methods."""
    def __init__(self, account_description = None, user = None, _password = None, email = None, encrypted_password = None):
        """
        Password Object constructor, it will initiliaze with default None values.
        Args:
            account_description: Describing the account associated with the password. Defaults to None.
            user: User account. Defaults to None.
            _password: Password for the associated account. Defaults to None.
            email: Email for the associated account. Defaults to None.
            encrypted_password: Is an optional argument for the constructor, we just really need a place holder for the encrypted password
        """
        self.account_description = account_description
        self.user = user
        self.email = email
        self.password = _password
        self.encrypted_password = encrypted_password

    def get_password_info(self, cursor, sql_connection, account_description, fernet):
        """
        Requesting account description from the user to then query the DB to retrive
        the password for the associated account
        Args:
            cursor: SQL cursor object
            sql_connection: SQL connection object
            account_description: Account associated with the password
            fernet: Fernet object to encrypt or decrypt the password
        Returns:
            dict: password_data
        """
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
        """
        Function to retrieve all the passwords from the SQL DB
        Args:
            cursor: SQL cursor object
            sql_connection: SQL connection object
            fernet: Fernet object to encrypt or decrypt the password
        Returns:
            dict: password_data
        """
        try:
            cursor.execute("""SELECT * FROM Passwords""")
            password_data= cursor.fetchall()
        except sql_connection.Error as error:
            print(f"SQL database error: {error}")
            sql_connection.close()

        return self.format_password_data(password_data, fernet)
    
    def delete_password(self, cursor, sql_connection, account_description, fernet):
        """
        Deleting password based on the account description enter by the user
        Args:
            cursor: SQL cursor object
            sql_connection: SQL connection object
            account_description: Describing the account associated with the password. 
        Returns:
            bool: b_deleted if the password was deleted successfully
        """
        password_to_delete = self.get_password_info(cursor, sql_connection, account_description, fernet)
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
        """
        Requesting data from users to instantiate the object representing a Password
        
        Args:
            Password Object
        Returns:
            strings : account_description, user, _password, email
        """
        print("\nPlease enter the following information to create a new password in the Lite Password Manager\n")

        # print("\nPlease enter a description:")
        account_description = input("Please enter an account description:")

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
        """
        Here we are going to format the password data to a dictionary and also decrypt the encrypted password
        Args:
            password_data: Password data to be formatted
            fernet: Fernet object to encrypt or decrypt the password
        Returns:
            dict: Already formatted password data and decrypted password
        """
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
        First we check if the file extist and if it is empty, 
        if not then create the file to stored the Fernet key
        it could be possible the file exists but does not have a Fernet key stored  
        Args:
            Fernet: Fernet object to decrypt and encrypt the password
        Returns:
            Object: fernet object associated with the Fernet key
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
        """
        Encrypting password using the fernet object
        Args:
            _password: Password to encrypt
            fernet: Fernet object to encrypt or decrypt the password
        """
        string = _password.encode()
        self.encrypted_password = fernet.encrypt(string)

    def decrypt_password(self, password_dict, fernet):
        """
        Decrypting password using the fernet object, this function will be called 
        from the Format Data Function and return a dict containing the password data
        Args:
            password_dict : Dictionary containing the password data
            fernet: Fernet object to encrypt or decrypt the password
        Returns:
            dict: password_dict
        """
        for data in password_dict:
            encrypted_password = data["Password"]
            encrypted_password = encrypted_password.strip("b'")
            encrypted_password = str.encode(encrypted_password)
            encrypted_password = fernet.decrypt(encrypted_password)
            data["Password"] = encrypted_password.decode()
        return password_dict 

    def init_SQL_Db(self, sql):
        """
        Intializing SQL Lite Data base
        Args:
            sql: imported SQL object from the SQL Lite module
        Returns:
            sql_connection: SQL connection object
            cursor: SQL cursor object
        """
        try:
            sql_connection = sql.connect("db\sql.db")
            cursor = sql_connection.cursor()
        except sql.Error as error:
            print(f"SQL database error: {error}")
        
        return sql_connection, cursor
    
    def create_check_db_table(self, cursor):
        """
        Create table if not already, otherwise return existing table
        Args:
            cursor: SQL cursor object
        Returns:
            table: Table object representing the Password table on the DB.
        """
        """"""
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
        """
        Saving password to DB, notice it is saving the encrypted password
        Args:
            cursor: SQL cursor object
            sql_connection: SQL connection object
        """
        try:
            cursor.execute(f""" 
                INSERT INTO Passwords VALUES ("{self.account_description}", "{self.user}", "{self.encrypted_password}","{self.email}");
            """)
            print("Password has been saved successfully")
        except sql_connection.Error as error:
            print(f"SQL database error: {error}")
        sql_connection.commit()
        sql_connection.close()