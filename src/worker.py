from rq import Worker, Queue, Connection
from rq_settings import redis_conn

# Create an RQ queue
appraisal_queue = Queue('appraisal_queue', connection=redis_conn)


def process_scraping_task(product_id, appraisal_id):
    from scraper import scrape_and_append_to_mongodb
    scrape_and_append_to_mongodb(product_id, appraisal_id)


def process_appraising_task(existing_product):
    from appraisal import appraise_product
    appraise_product(existing_product)


if __name__ == '__main__':
    with Connection(redis_conn):
        worker = Worker([appraisal_queue])

        # Register the functions to be used by the worker
        worker.register_birth()
        worker.work()
