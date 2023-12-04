import sqlite3

class User:
    def __init__(self, user_id, username, password, role):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.role = role

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'password': self.password,
            'role': self.role
        }

    @staticmethod
    def login(cursor, username, password):
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        row = cursor.fetchone()
        if row:
            return User(row[0], row[1], row[2], row[3])
        else:
            return None

class Admin(User):
    def __init__(self, user_id, username, password):
        super().__init__(user_id, username, password, "Admin")

class Employee(User):
    def __init__(self, user_id, username, password):
        super().__init__(user_id, username, password, "Employee")

class Client(User):
    def __init__(self, user_id, username, password):
        super().__init__(user_id, username, password, "Client")

class Product:
    def __init__(self, product_id, name, category):
        self.product_id = product_id
        self.name = name
        self.category = category

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'name': self.name,
            'category': self.category
        }

class CartItem:
    def __init__(self, user_id, product_id, quantity):
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'product_id': self.product_id,
            'quantity': self.quantity
        }

def create_tables(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart_items (
            user_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id),
            PRIMARY KEY (user_id, product_id)
        )
    ''')

def save_user_to_db(cursor, user):
    cursor.execute('''
        INSERT INTO users (username, password, role) VALUES (?, ?, ?)
    ''', (user.username, user.password, user.role))
    return cursor.lastrowid

def save_product_to_db(cursor, product):
    cursor.execute('''
        INSERT INTO products (name, category) VALUES (?, ?)
    ''', (product.name, product.category))
    return cursor.lastrowid

def save_cart_item_to_db(cursor, cart_item):
    cursor.execute('''
        INSERT INTO cart_items (user_id, product_id, quantity) VALUES (?, ?, ?)
    ''', (cart_item.user_id, cart_item.product_id, cart_item.quantity))

def create_default_products(cursor):
    default_products = [
        Product(None, "Чизбургер", "Бургеры"),
        Product(None, "Гамбургер", "Бургеры"),
        Product(None, "Цезарь", "Салаты"),
        Product(None, "Греческий", "Салаты"),
        Product(None, "Кола", "Напитки"),
        Product(None, "Фанта", "Напитки")
    ]

    for product in default_products:
        save_product_to_db(cursor, product)

def load_users_from_db(cursor):
    cursor.execute('SELECT * FROM users')
    rows = cursor.fetchall()
    users = [User(row[0], row[1], row[2], row[3]) for row in rows]
    return users

def load_products_from_db(cursor):
    cursor.execute('SELECT * FROM products')
    rows = cursor.fetchall()
    products = [Product(row[0], row[1], row[2]) for row in rows]
    return products

def load_cart_items_from_db(cursor, user_id):
    cursor.execute('SELECT * FROM cart_items WHERE user_id = ?', (user_id,))
    rows = cursor.fetchall()
    cart_items = [CartItem(row[0], row[1], row[2]) for row in rows]
    return cart_items

def is_username_unique(cursor, username):
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    return cursor.fetchone() is None

def display_menu(products):
    print("\nМеню:")
    for i, product in enumerate(products, start=1):
        print(f"{i}. {product.name} ({product.category})")

def select_product(products):
    try:
        product_index = int(input("Выберите номер продукта: "))
        if 1 <= product_index <= len(products):
            return products[product_index - 1]
        else:
            print("Некорректный номер продукта.")
            return None
    except ValueError:
        print("Введите число.")
        return None

def registration_or_login_choice(cursor, role):
    while True:
        print("\nВыберите действие:")
        print("1. Регистрация")
        print("2. Авторизация")

        action_choice = input("Введите номер действия: ")

        if action_choice == "1":
            if role == "Admin":
                user = register_user(cursor, Admin)
            elif role == "Employee":
                user = register_user(cursor, Employee)
            elif role == "Client":
                user = register_user(cursor, Client)
            if user:
                return user
        elif action_choice == "2":
            user = login_user(cursor)
            if user:
                return user
        else:
            print("Некорректный выбор действия.")

def register_user(cursor, user_type):
    while True:
        username = input(f"Введите логин {user_type.__name__}: ")
        while not is_username_unique(cursor, username):
            print("Логин уже занят. Пожалуйста, выберите другой логин.")
            username = input(f"Введите логин {user_type.__name__}: ")

        password = input(f"Введите пароль {user_type.__name__}: ")
        user = user_type(None, username, password)
        save_user_to_db(cursor, user)
        print(f"Регистрация {user_type.__name__.lower()} прошла успешно!")

        return user

def login_user(cursor):
    username = input("Введите логин: ")
    password = input("Введите пароль: ")
    user = User.login(cursor, username, password)
    if user:
        print(f"Авторизация успешна! Добро пожаловать, {user.username}!")
        return user
    else:
        print("Неправильный логин или пароль.")
        return None

def main_menu(cursor, user):
    print(f"\nДобро пожаловать, {user.username}!")

    products = load_products_from_db(cursor)

    while True:
        display_menu(products)

        selected_product = select_product(products)
        if selected_product:
            quantity = int(input("Введите количество: "))
            cart_item = CartItem(user.user_id, selected_product.product_id, quantity)
            save_cart_item_to_db(cursor, cart_item)
            print(f"{quantity} {selected_product.name} добавлен в корзину!")

        user = registration_or_login_choice(cursor, user.role)  # Обновляем пользователя после выбора регистрации или авторизации
        if user is None:
            break

def main():
    connection = sqlite3.connect('store.db')
    cursor = connection.cursor()

    create_tables(cursor)
    connection.commit()

    users = load_users_from_db(cursor)

    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        create_default_products(cursor)
        connection.commit()

    print("Выберите роль:")
    print("1. Админ")
    print("2. Сотрудник")
    print("3. Клиент")

    role_choice = input("Введите номер роли: ")

    if role_choice in ["1", "2", "3"]:
        role = None
        if role_choice == "1":
            role = "Admin"
        elif role_choice == "2":
            role = "Employee"
        elif role_choice == "3":
            role = "Client"

        user = registration_or_login_choice(cursor, role)
        if user:
            main_menu(cursor, user)
    else:
        print("Некорректный выбор роли.")

    connection.close()

if __name__ == "__main__":
    main()
