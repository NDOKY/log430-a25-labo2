"""
Orders (read-only model)
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

from collections import defaultdict
from db import get_sqlalchemy_session, get_redis_conn
from sqlalchemy import desc
from models.order import Order

def get_order_by_id(order_id):
    """Get order by ID from Redis"""
    r = get_redis_conn()
    return r.hgetall(order_id)

def get_orders_from_mysql(limit=9999):
    """Get last X orders"""
    session = get_sqlalchemy_session()
    return session.query(Order).order_by(desc(Order.id)).limit(limit).all()

def get_orders_from_redis(limit=9999):
    """Get last X orders"""
    # TODO: écrivez la méthode
    r = get_redis_conn()
    orders = []
    try:
        order_keys = r.keys("order:*")
        if not order_keys:
            print("No orders found in Redis.")
            return []
        for key in order_keys:
            order_data = r.hgetall(key)
            # Décodage bytes → str
            order = {k.decode("utf-8"): v.decode("utf-8") for k, v in order_data.items()}
            orders.append(order)
        print(limit)
        return orders
    except Exception as e:
        print(f"Error retrieving orders from Redis: {e}")
        return []


def get_highest_spending_users():
    """Get report of best selling products"""
    # TODO: écrivez la méthode
    # triez le résultat par nombre de commandes (ordre décroissant)

    r = get_redis_conn()
    expenses_by_user = defaultdict(float)

    orders = r.keys("order:*")

    for order in orders:
        expenses_by_user[order.user_id] += order.total

    highest_spending_users = sorted(expenses_by_user.items(), key=lambda item: item[1], reverse=True)

    return highest_spending_users[:10]

def get_highest_selling_products():
    r = get_redis_conn()
    products = []

    all_products = r.keys("product:*")

    for products_id in all_products:
        # Récupère la quantité vendue (stockée comme compteur incrémenté)
        quantity = int(r.get(products_id))
        products.append((products_id, quantity))

    products_sorted = sorted(products, key=lambda item: item[1], reverse=True)

    return products_sorted