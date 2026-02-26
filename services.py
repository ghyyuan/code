from __future__ import annotations

import model
from model import OrderLine
from repository import AbstractRepository


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(line: OrderLine, repo: AbstractRepository, session) -> str:
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid sku {line.sku}")
    batchref = model.allocate(line, batches)
    session.commit()
    return batchref

# services.py

def deallocate(orderid: str, sku: str, qty: int, repo: AbstractRepository, session):
    batches = repo.list()
    line = model.OrderLine(orderid, sku, qty)
    
    for batch in batches:
        if line in batch._allocations:
            batch.deallocate(line)
            session.commit()
            return
            
    raise model.InvalidSku(f"No allocation found for order {orderid} with SKU {sku}")