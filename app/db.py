DB = {}

def create_product(product_id, signature):
    DB[product_id] = {
        "status": "CREATED",
        "owner": None,
        "signature": signature
    }

def get_product(product_id):
    return DB.get(product_id)

def update_product(product_id, updates):
    DB[product_id].update(updates)