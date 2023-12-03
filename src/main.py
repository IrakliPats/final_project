from fastapi import FastAPI, HTTPException
from models import ProductInfo, ProductUpdate
from db import get_mongo_client
from scraper import scrape_and_append_to_mongodb, extract_number_from_url
from worker import appraisal_queue
from appraisal import appraise_product
import logging


app = FastAPI()
logger = logging.getLogger(__name__)


@app.get("/api/product/{product_id}")
async def check_product_in_database(product_id: str):
    try:
        with get_mongo_client() as client:
            db = client['mymarket']
            collection = db['phone']
            product_info = collection.find_one({'product_id': product_id})

            if product_info:
                return {"message": "Product found in the database",
                        "product_info": product_info}
            else:
                return {"message": "Product not found in the database"}

    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Internal server error: {e}")


@app.post("/api/product")
async def add_product_to_database(product_info: ProductInfo):
    try:
        with get_mongo_client() as client:
            db = client['mymarket']
            collection = db['phone']
            existing_product = collection.find_one(
                {'product_id': product_info.product_id}
            )

            if existing_product:
                return {
                    "message": "Product already exists in the database",
                    "product_info": existing_product
                }
            else:
                appraisal_queue.enqueue(scrape_and_append_to_mongodb,
                                        product_info.product_id,
                                        product_info.appraisal_id)
                return {"message": "Adding to database, in progress"}

    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Internal server error: {e}")


@app.post("/api/appraisal/{url}")
async def add_appraisal(url: str, appraisal_id: str):
    try:
        product_id = extract_number_from_url(url)

        with get_mongo_client() as client:
            db = client['mymarket']
            collection = db['phone']
            existing_product = collection.find_one({'product_id': product_id})

            if existing_product:
                # Update the existing product with the provided appraisal_id
                collection.update_one(
                    {'product_id': product_id},
                    {'$set': {'appraisal_id': appraisal_id}}
                )

                # Create a ProductInfo object
                product_info = ProductInfo(
                    user_id=existing_product.get('user_id'),
                    user=existing_product.get('user'),
                    username=existing_product.get('username'),
                    order_date=existing_product.get('order_date'),
                    loc_id=existing_product.get('loc_id'),
                    price=existing_product.get('price'),
                    currency_id=existing_product.get('currency_id'),
                    quantity=existing_product.get('quantity'),
                    weight=existing_product.get('weight'),
                    views=existing_product.get('views'),
                    rating=existing_product.get('rating'),
                    product_id=existing_product.get('product_id'),
                    title=existing_product.get('title'),
                    description=existing_product.get('description'),
                    appraisal_id=appraisal_id  # Set the new appraisal_id
                )

                # Enqueue the appraising task
                appraisal_queue.enqueue(appraise_product, product_info)

                return {"message": "Appraisal ID added to the product and "
                        "appraisal task enqueued"}
            else:
                appraisal_queue.enqueue(scrape_and_append_to_mongodb,
                                        product_id, appraisal_id)
                return {"message": "Product not found in the database, "
                        "scraped and added, and appraisal task enqueued"}

    except HTTPException as http_exception:
        raise http_exception

    except Exception as e:
        logger.exception(f"Error in add_appraisal: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/appraisal/{appraisal_id}")
async def get_appraisal(appraisal_id: str):
    try:
        with get_mongo_client() as client:
            db = client['mymarket']
            collection = db['phone']
            existing_product = collection.find_one(
                {'appraisal_id': appraisal_id}
            )

            if existing_product:
                product_price = existing_product.get('price', 0)
                appraisal_result = appraise_product(product_price)

                return {
                    "message": "Product found in the database",
                    "product_info": existing_product,
                    "appraisal_result": appraisal_result
                }
            else:
                return {"message": "Product not found in the database"}

    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Internal server error: {e}")


@app.delete("/api/product/{product_id}")
async def delete_product_by_id(product_id: str):
    try:
        with get_mongo_client() as client:
            db = client['mymarket']
            collection = db['phone']

    # Check if the product with the given product_id exists in the collection
            product_info = collection.find_one({'product_id': product_id})

            if product_info:
                # Product found, delete it
                result = collection.delete_one({'product_id': product_id})
                if result.deleted_count == 1:
                    return {"message": "Product deleted successfully"}
                else:
                    raise HTTPException(status_code=500,
                                        detail="Failed to delete product")
            else:
                raise HTTPException(status_code=404,
                                    detail="Product not found")

    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Internal server error: {e}")


@app.put("/api/product/{product_id}")
async def update_product_by_id(
    product_id: str, updated_product: ProductUpdate
):
    try:
        with get_mongo_client() as client:
            db = client['mymarket']
            collection = db['phone']

    # Check if the product with the given product_id exists in the collection
            existing_product = collection.find_one({'product_id': product_id})

            if existing_product:
                # Product found, update it
                update_data = updated_product.dict(exclude_unset=True)
                result = collection.update_one(
                    {'product_id': product_id},
                    {'$set': update_data}
                )

                if result.modified_count == 1:
                    return {"message": "Product updated successfully"}
                else:
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to update product"
                    )
            else:
                raise HTTPException(status_code=404,
                                    detail="Product not found")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {e}"
        )
