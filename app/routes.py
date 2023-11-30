from app import app
from flask import render_template, flash, redirect, url_for, session
from flask import request
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime

from app.forms import RegistrationForm, LoginForm, SearchForm, AddToCartForm, ChangeWorkingTImeForm, UpdateSaleForm, UpdateCostForm, AddProductToMarketForm
from app.forms import NewOfferForm, OfferConditionsForm1, OfferConditionsForm2, PayForm, SelectMarketForm, SetHoldingDateForm, ChangeStatusForm
from app.models import Administrator, Client, Medicament, Market, Cart, Position, Offer

# главная страница
@app.route("/", methods = ['GET', 'POST'])
@app.route("/index", methods = ['GET', 'POST'])
def index():
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(url_for('medicaments', search = form.search.data))
    return render_template('index.html', title = 'Главная страница', form=form)

#список аптек
@app.route('/markets', methods=['GET'])
def markets():
    markets = Market.get_list()
    return render_template('markets.html', title = 'Список аптек', markets=markets)

#режим работы аптеки
@app.route('/about_market/<id>', methods=['GET'])
def about_market(id):
    information = Market.get_info_by_id(id)
    return render_template('about_market.html', title='Об аптеке', information=information)

@login_required
@app.route("/registration", methods = ['GET', 'POST'])
def registration():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = Client(
                email = form.email.data,
                name = f'{form.lastname.data} {form.firstname.data} {form.patronymic.data}')
        user.set_password(form.password1.data)
        user.adduser()
        flash('Вы создали нового пользователя')
        user_id = Client.get_id_by_email(form.email.data)
        Cart.add(user_id, user.email)
        return redirect(url_for('login'))
    return render_template('registration.html', title = 'Регистрация аккаунта', form = form)

# вход пользователя
@app.route("/login", methods = ['GET', 'POST'])
def login():
    # если пользователь аутентифицирован
    if current_user.is_authenticated:
        return redirect("/index")
    # определяем необходимую форму из файла forms
    form = LoginForm()
    # если не возникло проблем с валидаторами, определенными в файле forms
    if form.validate_on_submit():
        # если поставлена галочка админ
        if form.role.data == True:
            # задаем переменной роль в сессии значение админ
            # это нужно для определения, из какой таблицы получать пользователя в методе loas user
            session['role'] = 'admin'
            user = Administrator.get_by_username(form.username.data)
        else:
            # если не поставлена галочка, значит роль пользователя - клиент
            session['role'] = 'client'
            user = Client.get_by_email(form.username.data)

        # если не нашелся пользователь с таким логином или пароль пользователя неверный
        if user is None or not user.check_password(form.password.data):
            # выдать ошибку на экран
            flash('Введен неправильный логин или пароль')
            return redirect("/login")
        print("имя найденного пользователя")
        print(user.name)
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            if session['role'] == 'client':
                next_page = "/index"
            elif session['role'] == 'admin':
                next_page = f'/admin/{user.username}'
        return redirect(next_page)
    return render_template('login.html', title = 'Вход в систему', form=form)

# страница админа
@app.route("/admin/<username>", methods = ['GET', 'POST'])
@login_required
def admin(username):
    market = Market.get_by_admin_username(username)
    user = Administrator.get_by_username(username)
    return render_template('admin.html', title = 'Администрирование', user=user, market=market)

#админ смотрит товары по типу получения
@app.route('/offers_for_delivery/<taking_type>', methods = ['GET'])
@login_required
def offers_for_delivery(taking_type):
    if taking_type == 'Курьерская доставка':
        offers = Offer.get_by_taking_type(taking_type)
    elif taking_type == 'Самовывоз':
        market = Market.get_by_admin_username(current_user.username)
        print(market[0][0])
        offers = Offer.get_uncomplited_by_admin(taking_type, market[0][0])
    return render_template('offers_admin.html', title = 'Список заказов', offers=offers, taking_type=taking_type)


#меняем статус заказа
@app.route('/change_offer_status/<offer_id>', methods=['GET', 'POST'])
@login_required
def change_offer_status(offer_id):
    new_status = ''
    form = ChangeStatusForm()
    if form.validate_on_submit():
        for s in form.status.choices:
            if int(s[0])==int(form.status.data):
                new_status = s[1]
                break
        Offer.update_status(new_status, offer_id)
        return redirect(url_for('admin', username=current_user.username))
    return render_template('change_offer_status.html', title = 'Изиенить статус заказа', form=form)

#установка срока хранения
@app.route('/set_holding_date/<offer_id>', methods = ['GET', 'POST'])
@login_required
def set_holding_date(offer_id):
    form = SetHoldingDateForm()
    if form.validate_on_submit():
        Offer.set_holding_date(offer_id, form.date.data)
        return redirect(url_for('admin', username = current_user.username))
    return render_template('set_holding_date.html', title = 'Установка срока хранения', form=form)


#список аптек, доступных администратору
@app.route('/change_working_time/<adres>', methods = ['GET', 'POST'])
@login_required
def change_working_time(adres):
    form = ChangeWorkingTImeForm()
    if form.validate_on_submit():
        Market.update_working_time_by_adres(adres, form.start_time.data, form.end_time.data)
        return redirect(url_for('admin', username=current_user.username))
    return render_template('change_working_time.html', title = 'Смена режима работы', form=form)

#список товаров, имеющихся в аптеке
@app.route('/products/<adres>', methods = ['GET'])
@login_required
def products(adres):
    products = Medicament.get_list_by_market_adres(adres)
    return render_template('products.html', title = 'Товары в аптеке', products=products)

#новый товар в наличии аптеки
@app.route('/new_product_in_market/<adres>', methods = ['GET', 'POST'])
@login_required
def new_product_in_market(adres):
    market_id = Market.get_id_by_adres(adres)
    form = AddProductToMarketForm()
    products = Medicament.get_missing_in_market(adres)
    if products is None:
        products = []
    form.product.choices = products
    if form.validate_on_submit():
        Market.add_new_product(market_id, form.product.data)
        return redirect(url_for('admin', username = current_user.username))
    return render_template('new_product_in_market.html', form=form, title = 'Добавить товар в аптеку')


#установка скидки на товар
@app.route('/update_sale/<product_id>', methods = ['GET', 'POST'])
@login_required
def update_sale(product_id):
    form = UpdateSaleForm()
    if form.validate_on_submit():
        Medicament.update_sale(product_id, form.sale.data)
        return redirect(url_for('admin', username = current_user.username))
    return render_template('update_sale.html', title = 'Установить скидку на товар', form=form)

#установка цены на товар
@app.route('/update_cost/<product_id>', methods = ['GET', 'POST'])
@login_required
def update_cost(product_id):
    form = UpdateCostForm()
    if form.validate_on_submit():
        Medicament.update_cost(product_id, form.cost.data)
        return redirect(url_for('admin', username = current_user.username))
    return render_template('update_cost.html', title = 'Установить стоимость товара', form=form)

# профиль клиента
@app.route("/client/<email>", methods = ['GET', 'POST'])
@login_required
def client(email):
    cart = Position.get_cart_by_user(email)

    cart_summ = 0
    for c in cart:
        cart_summ += (100-int(c[3]))/100*int(c[1])*int(c[2])
        print(int(cart_summ))

    user = Client.get_by_email(email)
    form = NewOfferForm()
    if form.validate_on_submit():

        Cart.add(current_user.id, current_user.email)
        return redirect(url_for('offer_conditions', cart_summ=int(cart_summ)))
    return render_template('client.html', title = 'Личный кабинет', user=user, cart=cart, cart_summ=cart_summ, form=form)

#неполученные заказы клиентом
@app.route('/uncomplited_offers/<email>', methods = ['GET'])
@login_required
def uncomplited_offers(email):
    offers = Offer.get_uncomplited_by_email(email)
    return render_template('client_offers.html', title='Список заказов', offers=offers)

#полученные заказы клиентом
@app.route('/offers_history/<email>', methods = ['GET'])
@login_required
def offers_history(email):
    offers = Offer.get_complited_by_email(email)
    return render_template('client_offers.html', title='Список заказов', offers=offers)

@app.route('/about_offer/<id>', methods = ['GET'])
@login_required
def about_offer(id):
    products = Offer.get_products_list_by_id(id)
    information = Offer.get_info_by_id(id)
    return render_template('about_offer.html', title = 'О заказе', information=information, products=products)

#установить параметры заказа
@app.route('/offer_conditions/<cart_summ>', methods = ['GET', 'POST'])
@login_required
def offer_conditions(cart_summ):
    taking_type = ''
    form = OfferConditionsForm1()
    if form.validate_on_submit():
        if int(form.taking_type.data) == 1:
            taking_type = 'Самовывоз'
            return redirect(url_for('select_market', cost = int(str(cart_summ)), taking_type = taking_type))
        else:
            taking_type = 'Курьерская доставка'
            receiving_adress = form.adress.data
            return redirect(url_for('select_pay', cost=int(str(cart_summ)), taking_type=taking_type, adress = receiving_adress))
    return render_template('offer_conditions1.html', title = 'Уточнение параметров заказа', form=form)

#выбрать аптеку для самовывоза
@app.route('/select_market/<cost>/<taking_type>', methods = ['GET', 'POST'])
@login_required
def select_market(cost, taking_type):
    adress = ''
    markets = Market.get_list()
    if markets is None:
        markets = []
    form = SelectMarketForm()
    form.market.choices = markets
    if form.validate_on_submit():
        for m in form.market.choices:
            if int(m[0]) == int(form.market.data):
                adress = m[1]
                break
        return redirect(url_for('select_pay', cost=cost, taking_type=taking_type, adress=adress))
    return render_template('select_market.html', title = 'Выбор пункта самовывоза', form=form)

#выбор способа оплаты
@app.route('/select_pay/<cost>/<taking_type>/<adress>', methods = ['GET', 'POST'])
@login_required
def select_pay(cost, taking_type, adress):
    form = OfferConditionsForm2()
    if form.validate_on_submit():
        if int(form.pay_type.data) == 1:
            return redirect(url_for('pay', cost=cost, taking_type=taking_type, adress=adress))
        else:
            cart_id = Cart.get_by_email(current_user.email)
            #оформить заказ
            offer_id = Offer.add(datetime.date(datetime.now()), taking_type, 'При получении', adress, cart_id, cost)
            Cart.add(current_user.id, current_user.email)
            Offer.set_offer(offer_id, current_user.email)
            return redirect(url_for('client', email=current_user.email))
    return render_template('select_pay.html', title = 'Выбор способа оплаты', form=form)

#форма оплаты на сайте
@app.route('/pay/<cost>/<taking_type>/<adress>', methods = ['GET', 'POST'])
@login_required
def pay(cost, taking_type, adress):
    form = PayForm()
    if form.validate_on_submit():
        cart_id = Cart.get_by_email(current_user.email)
        #оформить заказ
        offer_id = Offer.add(datetime.date(datetime.now()), taking_type, 'При получении', adress, cart_id, cost)
        Cart.add(current_user.id, current_user.email)
        Offer.set_offer(offer_id, current_user.email)
        return redirect(url_for('client', email=current_user.email))
    return render_template('pay_form.html', title = 'Оплата заказа', form=form, cost=cost)

#Каталог лекарств
@app.route('/medicaments_catalog', methods = ['GET', 'POST'])
def medicaments_catalog():
    types = Medicament.get_types()
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(url_for('medicaments', search=form.search.data))
    return render_template('medicaments_catalog.html', title = 'Каталог', types=types, form=form)

#список лекарств по запросу
@app.route('/medicaments/<search>', methods = ['GET', 'POST'])
def medicaments(search):
    medicaments = Medicament.get_list_by_search(search)
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(url_for('medicaments', search = form.search.data))
    return render_template('medicament_list.html', title = 'Список по запросу', form=form, medicaments = medicaments, search=search)


#список лекарств этой категории
@app.route('/about_type/<type>/<search>', methods = ['GET', 'POST'])
def about_type(type, search):
    if search == 'nothing':
        if type == 'sale':
            medicaments = Medicament.get_sale('')
            title = 'Товары со скидкой'
        else:
            medicaments = Medicament.get_list_by_type(type, '')
            title = type
    else:
        if type == 'sale':
            medicaments = Medicament.get_sale(search.lower())
            title = 'Товары со скидкой'
        else:
            medicaments = Medicament.get_list_by_type(type, search.lower())
            title = type
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(url_for('about_type', type=type, search = form.search.data))
    return render_template('medicament_list.html', title = title, form = form, medicaments=medicaments, type=type, search=search)

#информация о товаре
@app.route('/about_medicament/<type>/<search>/<id>', methods = ['GET', 'POST'])
def about_medicament(type, search, id):
    information = Medicament.get_information_by_id(id)
    summ = int(information[0][4]) * (1 - int(information[0][7])/100)
    markets = Medicament.get_market_by_id(id)
    print(markets)
    if information[0][2] == False:
        recept = 'без рецепта'
    else:
        recept = 'по рецепту'
    form = AddToCartForm()
    if form.validate_on_submit():
        cart_id = Cart.get_by_email(current_user.email)
        count = form.count.data
        Position.add(cart_id, id, count)
        return redirect(url_for('medicaments_catalog'))
    return render_template('about_medicament.html', title = str(information[0][1]), information=information, form=form, type=type, recept=recept, summ=summ, markets=markets, search=search)




# выйти из аккаунта
@app.route("/logout")
@login_required
def logout():
    logout_user()
    session['role'] = None
    return redirect("/index")
