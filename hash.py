from werkzeug.security import generate_password_hash, check_password_hash


class User:
    def __init__(self, user, password):
        self.__username = user
        self.__password = password


    @property
    def username(self):
        raise AttributeError('NO!')


    @username.setter
    def username(self, new):
        self.__username = new
# Импортируем функции для хеширования и проверки пароля
# from werkzeug.security import generate_password_hash, check_password_hash

# class User(db.Model):
#    __tablename__ = 'users'

#    id = db.Column(db.Integer, primary_key=True)
#    username = db.Column(db.String(32), nullable=False, unique=True)
#    # Изменим название и длину поля для пароля
#    password_hash = db.Column(db.String(128), nullable=False)
#    role = db.Column(db.String(32), nullable=False)

#    @property
#    def password(self):
#        # Запретим прямое обращение к паролю
#        raise AttributeError("Вам не нужно знать пароль!")

#    @password.setter
#    def password(self, password):
#        # Устанавливаем пароль через этот метод
#    	self.password_hash = generate_password_hash(password)

#    def password_valid(self, password):
#        # Проверяем пароль через этот метод
#        # Функция check_password_hash превращает password в хеш и сравнивает с хранимым
#        return check_password_hash(self.password_hash, password)