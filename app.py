import sys
import sqlite3 as sql
from cryptography.fernet import Fernet

key = Fernet.generate_key()
fernet = Fernet(key)

"""This is the main class representing a Password object and all associated methods"""
class Password_Obj:
    encrypted_password = None

    def __init__(self,account_description = None, user = None, _password = None, email = None):
        """Password constructor method"""
        self.account_description = account_description
        self.user = user
        self.email = email
        self.password = _password

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
        _password = input()

        print("\nPlease enter again the password to confirm is valid:")
        password_validation = input()

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

def main(argv):
    """Instantiating the Password object as empty, we'll fill out the data later on"""
    Password = Password_Obj()

    """Arguments system"""
    if argv[1] == "--newpassword":
        """Requesting information to the user"""
        account_description, user, _password, email = Password.request_password_info()
    elif argv[1] == "--showallpasswords":
        print("showing all passwords")
    elif argv[1] == "--getpassword":
        print("getting password")
    else:
        print("Use --help to see options")
        return
        

    """Since we now have data from the user, let's fill up the empty Password Object"""   
    Password.__init__(account_description, user, _password, email)

    """Encrypting Password"""
    Password.encrypt_password()

    """For now lets just print the data stored on the password object"""
    Password.get_password_info()

if __name__ == '__main__':
    main(sys.argv)