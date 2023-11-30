from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField, DateField, TimeField, SearchField, TelField, TextAreaField, EmailField
from wtforms.validators import DataRequired, ValidationError, EqualTo
from app.models import Client

# авторизация
class LoginForm(FlaskForm):
    username = StringField('Логин/Эл.Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    role = BooleanField('Я администратор')
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Вход')

# регистрация клиента
class RegistrationForm(FlaskForm):
    #имя
    lastname = StringField('Фамилия', validators=[DataRequired()])
    firstname = StringField('Имя', validators=[DataRequired()])
    patronymic = StringField('Отчество', validators=[DataRequired()])

    #email
    email = EmailField('Электронная почта', validators=[DataRequired()])
    #пароль
    password1 = PasswordField('Задайте пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password1')])

    submit = SubmitField('Зарегистрироваться')

    def validate_email(self, email):
        user = Client.get_by_email(self.email.data)
        if user is not None:
            raise ValidationError('Клиент с такой почтой уже зарегистрирован!')
        return

class SearchForm(FlaskForm):
    search = SearchField('Поиск по названию')
    submit = SubmitField('Найти')

class AddToCartForm(FlaskForm):
    count = IntegerField('Количество')
    submit = SubmitField('Добавить в корзину')

    def validate_count(self, count):
        if int(self.count.data) < 1: 
            raise ValidationError('Количество позиций не может быть меньше 1!')
        return

class ChangeWorkingTImeForm(FlaskForm):
    start_time = TimeField('Новое время начала работы')
    end_time = TimeField('Новое время окончания работы')
    submit = SubmitField('Подтвердить изменения')

class UpdateSaleForm(FlaskForm):
    sale = IntegerField('Размер скидки', validators=[DataRequired()])
    submit = SubmitField('Подтвердить изменения')

    def validate_sale(self, sale):
        if int(self.sale.data) < 0: 
            raise ValidationError('Скидка не может быть отрицательного значения!')
        return

class UpdateCostForm(FlaskForm):
    cost = IntegerField('Новая цена', validators=[DataRequired()])
    submit = SubmitField('Подтвердить изменения')

    def validate_cost(self, cost):
        if int(self.cost.data) < 20: 
            raise ValidationError('Товар не может стоить менее 20 рублей!')
        return

class AddProductToMarketForm(FlaskForm):
    product = SelectField('Товар')
    submit = SubmitField('Подтвердить')

class NewOfferForm(FlaskForm):
    submit = SubmitField('Сделать заказ')

class OfferConditionsForm1(FlaskForm):
    taking_type = SelectField('Способ получения', choices=[(1, 'В аптеке'), (2, 'Доставить по адресу')])
    adress = StringField('Адрес для курьерской доставки (при получении не в аптеке)')
    submit = SubmitField('Продолжить')

class OfferConditionsForm2(FlaskForm):
    pay_type = SelectField('Форма оплаты', choices=[(1, 'Картой онлайн'), (2, 'При получении')])
    submit = SubmitField('Продолжить')

class PayForm(FlaskForm):
    number = StringField('Номер карты', validators=[DataRequired()])
    submit = SubmitField('Оплатить')

class SelectMarketForm(FlaskForm):
    market = SelectField('Выберите пункт самовывоза')
    submit = SubmitField('Продолжить')

class ChangeStatusForm(FlaskForm):
    status = SelectField('Статус', choices=[(1,'Доставляется'), (2, 'Ожидает в аптеке'), (3, 'Получен клиентом')])
    submit = SubmitField('Изменить статус')

class SetHoldingDateForm(FlaskForm):
    date = DateField('Хранение до')
    submit = SubmitField('Установить дату хранения')