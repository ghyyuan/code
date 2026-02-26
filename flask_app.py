from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config
import model
import orm
import repository
import services


orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = Flask(__name__)

@app.route("/allocations", methods=["POST"])
def allocate_endpoint():
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    try:
        batchref = services.allocate(
            request.json["orderid"], 
            request.json["sku"], 
            request.json["qty"], 
            repo, 
            session
        )
    except (model.OutOfStock, services.InvalidSku) as e:
        return {"message": str(e)}, 400

    return {"batchref": batchref}, 201


@app.route("/allocations", methods=["DELETE"])
def deallocate_endpoint():
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    try:
        services.deallocate(
            request.json["orderid"], 
            request.json["sku"], 
            request.json["qty"], 
            repo, 
            session
        )
    except model.InvalidSku as e:
        return {"message": str(e)}, 404

    return {"message": "deallocated"}, 200

@app.route("/batches/<ref>", methods=["GET"])
def get_batch_endpoint(ref):
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    batch = repo.get(ref)
    if not batch:
        return {"message": "Not found"}, 404
    
    return {
        "reference": batch.reference,
        "sku": batch.sku,
        "available_quantity": batch.available_quantity,
    }, 200