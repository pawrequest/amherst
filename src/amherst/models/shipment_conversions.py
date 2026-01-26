from pycommence.meta.meta import get_table_type
from shipaw.models.ship_types import ShipDirection

from amherst.models.amherst_models import AmherstShipableBase
from amherst.models.shipment import AmherstShipment


def record_to_shipment(
        record: AmherstShipableBase,
        direction: ShipDirection = ShipDirection.OUTBOUND
) -> AmherstShipment:
    context = record.model_dump(mode='json')
    context.update({'category': record.category, 'pk_key': record.pk_key})
    return AmherstShipment(
        recipient=record.full_contact,
        boxes=record.boxes,
        shipping_date=record.send_date,
        direction=direction,
        reference=record.customer_name,
        context=context,
    )


def shipment_to_record(shipment: AmherstShipment) -> AmherstShipableBase:
    category = shipment.context.get('category')
    model_type = get_table_type(category)
    return model_type.model_validate(shipment.context)
