from models import ProductInfo


def appraise_product(product_info: ProductInfo):
    price = product_info.price

    if price > 3000:
        return "expensive"
    elif 1000 <= price <= 3000:
        return "normal"
    else:
        return "cheap"
