import datetime
from dataclasses import dataclass, field
from decimal import Decimal

from amherst.actions.invoice_number import next_inv_num


@dataclass
class AddressStrings:
    add: str
    pc: str


@dataclass
class LineItem:
    name: str
    description: str
    quantity: int
    price_each: Decimal

    @property
    def line_price(self):
        return self.price_each * int(self.quantity)

    def __str__(self):
        return f'{self.quantity} x {self.name} @ {self.price_each} = {self.line_price}'


@dataclass
class Order:
    line_items: list[LineItem] = field(default_factory=list)
    tax_percent: int = 20
    shipping: Decimal = 15.00
    charity_percent: int = 0

    def __str__(self):
        return f'Order with {len(self.line_items)} lines for £{self.total}'

    @property
    def total_goods(self):
        return Decimal(sum(itm.line_price for itm in self.line_items))

    @property
    def charity_discount(self):
        if not self.charity_percent:
            return 0
        return Decimal(self.total_goods * self.charity_percent / 100)

    @property
    def subtotal(self):
        sub = sum([self.total_goods, self.shipping]) - self.charity_discount
        return Decimal(sub)

    @property
    def tax(self):
        return Decimal(self.subtotal * self.tax_percent / 100)

    @property
    def total(self):
        return self.subtotal + self.tax


@dataclass
class Invoice:
    order: Order
    inv_add: AddressStrings
    del_add: AddressStrings
    invoice_date: datetime.date = field(default_factory=datetime.date.today)
    inv_num: str = field(default_factory=next_inv_num)
