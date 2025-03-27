import mysql.connector
from datetime import datetime

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",  
        password="password",  
        database="finace_record_project"
    )

def setup_db():
    db = connect_db()
    cursor = db.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        balance FLOAT NOT NULL DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        amount FLOAT,
        transaction_type VARCHAR(50),  -- Ensure this column is present
        timestamp DATETIME,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    db.commit()
    db.close()


def register_user():
    name = input("Enter your name: ")
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO users (name, balance) VALUES (%s, %s)", (name, 0))
    cursor.execute("SELECT id FROM users WHERE name = %s", (name,))
    user_id = cursor.fetchone() 
    db.commit()
    print("User registered successfully!")
    print(f'Your user ID is {user_id[0]}')
    db.close()

def add_money():
    user_id = int(input("Enter user ID: "))
    amount = float(input("Enter amount to add: "))
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("UPDATE users SET balance = balance + %s WHERE id = %s", (amount, user_id))
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  
    cursor.execute("INSERT INTO transactions (user_id, amount, transaction_type, timestamp) VALUES (%s, %s, %s,%s)", 
                   (user_id, amount, "Deposit", timestamp))

    db.commit()
    print("Money added successfully!")
    db.close()

def withdraw_money():
    user_id = int(input("Enter user ID: "))
    amount = float(input("Enter withdrawal amount: "))
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT balance FROM users WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    if result:
        balance = result[0]
        if amount > balance:
            print("Insufficient funds!")
        else:
            new_balance = balance - amount
            cursor.execute("UPDATE users SET balance = %s WHERE id = %s", (new_balance, user_id))
            cursor.execute("INSERT INTO transactions (user_id, amount, transaction_type, timestamp) VALUES (%s, %s, %s, %s)", (user_id, -amount, "Withdrawal", datetime.now()))
            db.commit()
            print("Withdrawal successful!")
            check_balance_alerts(new_balance, balance)
    else:
        print("User not found!")
    db.close()

def check_balance_alerts(new_balance, old_balance):

    print(old_balance)
    print(new_balance)
    if new_balance == 0:
        print("Alert: Your balance is completely exhausted!")
    elif new_balance <= old_balance * 0.25:
        print("Alert: Balance below 25%!")
    elif new_balance <= old_balance * 0.5:
        print("Alert: Balance below 50%!")

def check_balance():
    user_id = int(input("Enter user ID: "))
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT balance FROM users WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    if result:
        print(f"Current balance: {result[0]}")
    else:
        print("User not found!")
    db.close()

def check_last_10_transactions():
    user_id = int(input("Enter user ID: "))
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT amount, transaction_type, timestamp FROM transactions WHERE user_id = %s ORDER BY timestamp DESC LIMIT 10", (user_id,))
    transactions = cursor.fetchall()
    if transactions:
        for transaction in transactions:
            print(f"{transaction[1]}: {transaction[0]} on {transaction[2]}")
    else:
        print("No transactions found.")
    db.close()

def delete_account():
    user_id = int(input("Enter user ID to delete: "))
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM transactions WHERE user_id = %s", (user_id,))
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    db.commit()
    print("Account deleted successfully!")
    db.close()

def main():
    setup_db()
    while True:
        print("\nExpense Tracker Menu")
        print("1. Register new user")
        print("2. Add money")
        print("3. Withdraw money")
        print("4. Check balance")
        print("5. View last 10 transactions")
        print("6. Delete account")
        print("7. Exit")
        choice = input("Enter choice: ")
        if choice == "1":
            register_user()
        elif choice == "2":
            add_money()
        elif choice == "3":
            withdraw_money()
        elif choice == "4":
            check_balance()
        elif choice == "5":
            check_last_10_transactions()
        elif choice == "6":
            delete_account()
        elif choice == "7":
            print("Exiting... Goodbye!")
            break
        else:
            print("Invalid choice! Please try again.")

main()