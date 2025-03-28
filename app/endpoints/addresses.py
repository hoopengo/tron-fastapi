from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from tronpy.exceptions import ApiError, BadAddress, NotFound

from app import models, schemas
from app.instances import tron_client
from app.database import get_db

router = APIRouter(prefix="/addresses", tags=["addresses"])


@router.post("/", response_model=schemas.AddressInfo)
async def get_address_info(
    address_req: schemas.AddressRequest, db: Session = Depends(get_db)
):
    try:
        account = tron_client.get_account(address_req.address)

        # Получаем баланс в TRX
        balance_sun = account.get("balance", 0)
        balance_trx = balance_sun / 1_000_000

        # Получаем информацию о ресурсах
        resource = tron_client.get_account_resource(address_req.address)
        bandwidth = resource.get("freeNetLimit", 0) - resource.get("freeNetUsed", 0)
        energy_limit = resource.get("EnergyLimit", 0)
        energy_used = resource.get("EnergyUsed", 0)
        energy = energy_limit - energy_used

        # Сохраняем в базу данных
        db_record = models.AddressQuery(
            address=address_req.address,
            balance_trx=balance_trx,
            bandwidth=bandwidth,
            energy=energy,
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)

        return {
            "address": address_req.address,
            "balance_trx": balance_trx,
            "bandwidth": bandwidth,
            "energy": energy,
        }

    except (ApiError, BadAddress, NotFound) as e:
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка при получении информации о Tron адресе: {str(e)}",
        )


@router.get("/", response_model=schemas.PaginatedAddressQueries)
async def get_address_queries(
    page: int = Query(1, gt=0, description="Номер страницы"),
    page_size: int = Query(
        10, gt=0, le=100, description="Количество записей на странице"
    ),
    db: Session = Depends(get_db),
):
    offset = (page - 1) * page_size
    total = db.query(models.AddressQuery).count()

    items = (
        db.query(models.AddressQuery)
        .order_by(models.AddressQuery.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return {"total": total, "page": page, "page_size": page_size, "items": items}
