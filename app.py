import json

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Integer, Column, Text, Date, Float
from helpers import load_users_data, load_orders_data, load_offers_data

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JSON_AS_ASCII"] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(150))
    last_name = Column(String(150))
    age = Column(Integer)
    email = Column(String)
    role = Column(String)
    phone = Column(String(12))

    def as_dict(self):
        return {'id': self.id,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'age': self.age,
                'email': self.email,
                'role': self.role,
                'phone': self.phone}


class Order(db.Model):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    name = Column(String(150))
    description = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    address = Column(String)
    price = Column(Float)
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    executor_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'address': self.address,
            'price': self.price,
            'customer_id': self.customer_id,
            'executor_id': self.executor_id
        }


class Offer(db.Model):
    __tablename__ = 'offers'
    id = Column(Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    executor_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def as_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'executor_id': self.executor_id
        }


db.create_all()

for item in load_users_data():
    db.session.add(
        User(id=item['id'],
             first_name=item['first_name'],
             last_name=item['last_name'],
             age=item['age'],
             email=item['email'],
             role=item['role'],
             phone=item['phone'])
    )

for item in load_orders_data():
    db.session.add(
        Order(id=item['id'],
              name=item['name'],
              description=item['description'],
              start_date=item['start_date'],
              end_date=item['end_date'],
              address=item['address'],
              price=item['price'],
              customer_id=item['customer_id'],
              executor_id=item['executor_id'])
    )

for item in load_offers_data():
    db.session.add(
        Offer(id=item['id'],
              order_id=item['order_id'],
              executor_id=item['executor_id'])
    )

db.session.commit()


@app.route("/")
def get_start():
    """Стартовая страничка"""
    return f"Привет, я работаю :)"


@app.route("/users/", methods=['GET', 'POST'])
def get_all_users():
    """Функция получает всех пользователей."""
    if request.method == 'GET':
        users = User.query.all()
        return jsonify([user.as_dict() for user in users])

    if request.method == 'POST':
        user = json.loads(request.data)
        new_user_obj = User(id=user['id'],
                            first_name=user['first_name'],
                            last_name=user['last_name'],
                            age=user['age'],
                            email=user['email'],
                            role=user['role'],
                            phone=user['phone'])
        db.session.add(new_user_obj)
        db.session.commit()
        db.session.close()
        return "Пользователь внесен", 200


@app.route("/users/<int:user_id>/", methods=['GET', 'PUT', 'DELETE'])
def get_one_user(user_id):
    """Функция одного одинешеньку пользователя"""
    if request.method == 'GET':
        user = User.query.get(user_id)
        if user is None:
            return "Нет такого пользователя"
        else:
            return jsonify(user.as_dict())
    elif request.method == 'PUT':
        user_data = json.loads(request.data)
        user = db.session.query(User).get(user_id)
        if user is None:
            return "Пользователь не найден", 404
        user.first_name = user_data['first_name']
        user.last_name = user_data['last_name']
        user.age = user_data['age']
        user.email = user_data['email']
        user.role = user_data['role']
        user.phone = user_data['phone']
        db.session.add(user)
        db.session.commit()
        return f"Объект с id {user_id} успешно изменен", 200
    elif request.method == 'DELETE':
        user = db.session.query(User).get(user_id)
        if user is None:
            return "Нет такого пользователя", 404
        db.session.delete(user)
        db.session.commit()
        db.session.close()
        return f"Пользователь с id {user_id} удален", 200


@app.route("/orders/", methods=['GET', 'POST'])
def get_all_orders():
    """Функция выводит все заказы."""
    if request.method == 'GET':
        result = []
        orders = Order.query.all()
        for order in orders:
            result.append(order.as_dict())
        return jsonify(result)
    if request.method == 'POST':
        order = json.loads(request.data)
        new_order_obj = Order(id=order['id'],
                              name=order['name'],
                              description=order['description'],
                              start_date=order['start_date'],
                              end_date=order['end_date'],
                              address=order['address'],
                              price=order['price'],
                              customer_id=order['customer_id'],
                              executor_id=order['executor_id'])
        db.session.add(new_order_obj)
        db.session.commit()
        db.session.close()
        return "Заказ создан", 200


@app.route("/orders/<int:order_id>/", methods=['GET', 'PUT', 'DELETE'])
def get_order_by_id(order_id):
    if request.method == 'GET':
        order = Order.query.get(order_id)
        if order is None:
            return "Нет заказа с таким номерком"
        else:
            return jsonify(order.as_dict())
    elif request.method == 'PUT':
        order_data = json.loads(request.data)
        order = db.session.query(Order).get(order_id)
        if order is None:
            return "Заказ не найден", 404
        order.name = order_data['name']
        order.description = order_data['description']
        order.start_date = order_data['start_date']
        order.end_date = order_data['end_date']
        order.address = order_data['address']
        order.price = order_data['price']
        order.customer_id = order_data['customer_id']
        order.executor_id = order_data['executor_id']

        db.session.add(order)
        db.session.commit()
        db.session.close()
        return f"Заказ {order_id} изменен", 200

    elif request.method == 'DELETE':
        order = db.session.query(Order).get(order_id)
        if order is None:
            return "Заказ не обнаружен"
        db.session.delete(order)
        db.session.commit()
        db.session.close()
        return f"Заказ {order_id} удален", 200


@app.route("/offers/", methods=['GET', 'POST'])
def get_all_offers():
    """Функция выводит все предложния"""
    if request.method == 'GET':
        result = []
        offers = Offer.query.all()
        for offer in offers:
            result.append(offer.as_dict())
        return jsonify(result)
    if request.method == 'POST':
        offer = json.loads(request.data)
        new_offer_obj = Offer(id=offer['id'],
                              order_id=offer['order_id'],
                              executor_id=offer['executor_id'])
        db.session.add(new_offer_obj)
        db.session.commit()
        db.session.close()
        return "Предложение создано", 200


@app.route("/offers/<int:offer_id>/", methods=['GET', 'PUT', 'DELETE'])
def get_offer_by_id(offer_id):
    if request.method == 'GET':
        offer = Offer.query.get(offer_id)
        if offer is None:
            return "Нет предложений с таким номерком"
        else:
            return jsonify(offer.as_dict())
    elif request.method == 'PUT':
        offer_data = json.loads(request.data)
        offer = db.session.query(Offer).get(offer_id)
        if offer is None:
            return "Предложение не найдено", 404
        offer.order_id = offer_data['order_id']
        offer.executor_id = offer_data['executor_id']

        db.session.add(offer)
        db.session.commit()
        db.session.close()
        return f"Предложение {offer_id} изменено", 200

    elif request.method == 'DELETE':
        offer = db.session.query(Offer).get(offer_id)
        if offer is None:
            return "Предложение не обнаружено"
        db.session.delete(offer)
        db.session.commit()
        db.session.close()
        return f"Предложение {offer_id} удалено", 200


if __name__ == '__main__':
    app.run()
