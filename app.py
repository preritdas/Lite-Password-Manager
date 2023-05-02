'''
Lite Password Manager v1.0
Author: Jorge Cerdas Valverde
LinkedIn: https://www.linkedin.com/in/ing-jorgecerdas/
Description:
This is a Password Manager using SQL Lite to store the passwords on a relational table, also using the Fernet Library to encrypt and decrypt
the passwords once the user wants to see them. 
'''
import os, os.path
import sys, getpass
import sqlite3 as sql
from cryptography.fernet import Fernet
from Password.Password import Password_Obj
import typer as tp


"""Instantiating the Password object as empty, we'll fill out the data later on"""
Password = Password_Obj()

"""Let's init the DB"""
sql_connection, cursor = Password.init_SQL_Db(sql)

"""Creating table, otherwise returning an existing table"""
db_table = Password.create_check_db_table(cursor)

fernet = Password.init_encryption_keys(Fernet)

App = tp.Typer()

@App.command()
def new_password():
    account_description, user, _password, email = Password.request_password_info()
    Password.__init__(account_description, user, _password, email)
    Password.encrypt_password(_password, fernet)
    Password.save_password_db(cursor, sql_connection)
    sys.exit(0)

@App.command()
def show_all_passwords():
    print("Show all Passwords!")
    all_passwords = Password.show_all_passwords(cursor, sql_connection, fernet)
    [print(passwords) for passwords in all_passwords]
    sys.exit(0)

@App.command()
def get_password():
    print("\nPlease enter the account description")
    account_description = input("Account description: ")
    passwords = Password.get_password_info(cursor, sql_connection, account_description, fernet)
    if not passwords:
        print("Password was not found, try again")
    else:
        [print(password) for password in passwords] 
    sys.exit(0)    

@App.command()
def delete_password():
    """Delete the password from the database based on the account description"""
    print("\nPlease enter the account description")
    account_description = input("Account description: ")
    b_success = Password.delete_password(cursor, sql_connection, account_description)
    if b_success:
        print(f"Password associated with {account_description} was deleted successfully")
    else:
        print(f"Password associated with {account_description} was not deleted, check the account description and try again")
    sys.exit(0)

@App.command()
def help():
    print("Displaying usage options:\n")
    print("Option --newpassword: Creates a new password.\n")
    print("Option --showallpasswords: Retrieves all the passwords from the database.\n")
    print("Option --getpassword: Retrieves the password based on the account description.\n")
    print("Option --deletepassword: Deletes the password based on the account description.\n")

        
if __name__ == '__main__':
    """Main will receive the arguments"""
    App()