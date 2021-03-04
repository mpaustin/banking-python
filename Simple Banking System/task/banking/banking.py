from random import seed
from random import randint
import sqlite3

done = False
logged_in = False
main_input = 0
secondary_input = 0
iin = "400000"
checksum = ""
acct_num = ""
full_card_num = ""
pin = ""
balance = 0

conn = sqlite3.connect('card.s3db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

create_table = "CREATE TABLE IF NOT EXISTS card (id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0);"

cursor.execute(create_table)
conn.commit()


def print_main():
    print("1. Create an account\n2. Log into account\n0. Exit")
    return int(input())


def create_acct():
    global acct_num, pin, full_card_num, checksum
    # create card number and pin
    seed()
    acct_num = str(randint(100000000, 999999999))
    pin = str(randint(1000, 9999))
    # set checksum based on Luhn Algo
    num_minus_checksum = iin + acct_num
    num_list = list(map(int, list(num_minus_checksum)))
    number_sum = 0
    for i in range(len(num_list)):
        if i % 2 == 0:
            num = num_list[i] * 2
            if num > 9:
                num -= 9
            num_list[i] = num
        number_sum += num_list[i]
    checksum = str(10 - (number_sum % 10))
    if checksum == "10":
        checksum = "0"
    full_card_num = num_minus_checksum + checksum
    save_acct_info(full_card_num, pin)
    print("\nYour card has been created")
    print("Your card number:\n{}\nYour card PIN:\n{}\n".format(full_card_num, pin))


def check_luhn(num: str):

    num_list = list(map(int, list(num[0:len(num) - 1])))
    last_digit = num[-1]
    number_sum = 0
    for i in range(len(num_list)):
        if i % 2 == 0:
            num = num_list[i] * 2
            if num > 9:
                num -= 9
            num_list[i] = num
        number_sum += num_list[i]
    this_checksum = str(10 - (number_sum % 10))
    if this_checksum == "10":
        this_checksum = "0"
    if this_checksum == last_digit:
        return False
    else:
        return True


def save_acct_info(num, this_pin):
    global conn, cursor
    query = "insert into card (id,number,pin) values ({},{},{})".format(randint(1, 100000), num, this_pin)
    cursor.execute(query)
    conn.commit()


def print_secondary():
    print("1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit")
    return int(input())


def login():
    global acct_num, pin, balance

    print("\nEnter your card number:")
    this_card_num = str(input())
    print("Enter your PIN:")
    this_pin = str(input())

    query = "select * from card where number = {} and pin = {}".format(this_card_num, this_pin)
    account = cursor.execute(query).fetchone()

    if not account:
        print("\nWrong card number or PIN!\n")
        return False
    else:
        print("\nYou have successfully logged in!\n")
        acct_num = account['number']
        pin = account['pin']
        balance = account['balance']
        return True


def print_balance():
    global balance
    print("\nBalance: {}\n".format(balance))


def add_income():
    global balance, acct_num
    print("\nEnter income:")
    income = int(input())
    balance += income
    query = "update card set balance = {} where number = {}".format(balance, acct_num)
    cursor.execute(query)
    conn.commit()
    print("Income was added!\n")


def transfer():
    global balance, acct_num
    print("\nTransfer\nEnter card number:")
    other_acct = str(input())
    count = cursor.execute("select count(*) from card where number = {}".format(other_acct)).fetchone()[0]
    if other_acct == acct_num:
        print("You can't transfer money to the same account!\n")
    elif check_luhn(other_acct):
        print("Probably you made a mistake in the card number. Please try again!\n")
    elif count == 0:
        print("Such a card does not exist.\n")
    else:
        other_acct_balance = cursor.execute("select * from card where number = {}".format(other_acct)).fetchone()['balance']
        # print("Other account balance:", other_acct_balance)
        print("Enter how much money you want to transfer:")
        trans_amt = int(input())
        if trans_amt > balance:
            print("Not enough money!\n")
        else:
            balance -= trans_amt
            other_acct_balance += trans_amt
            query1 = "update card set balance = {} where number = {}".format(balance, acct_num)
            query2 = "update card set balance = {} where number = {}".format(other_acct_balance, other_acct)
            cursor.execute(query1)
            cursor.execute(query2)
            conn.commit()
            print("Success!\n")


def delete_acct():
    global acct_num, logged_in
    query = "delete from card where number = {}".format(acct_num)
    cursor.execute(query)
    conn.commit()
    logged_in = False
    print("\nThe account has been closed!\n")


def logout():
    global logged_in
    logged_in = False
    print("\nYou have successfully logged out\n")


def leave():
    global logged_in, done
    logged_in = False
    done = True


while not done:

    main_input = print_main()

    if main_input == 1:
        create_acct()
    elif main_input == 2:
        success = login()
        if success:
            logged_in = True
            while logged_in:
                secondary_input = print_secondary()
                if secondary_input == 1:
                    print_balance()
                elif secondary_input == 2:
                    add_income()
                elif secondary_input == 3:
                    transfer()
                elif secondary_input == 4:
                    delete_acct()
                elif secondary_input == 5:
                    logout()
                else:
                    leave()
    else:
        done = True

print("\nBye!")
