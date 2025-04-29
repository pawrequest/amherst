import datetime
from dataclasses import dataclass, field
from decimal import Decimal

from amherst.actions.invoice_number import next_inv_num


@dataclass
class InventoryItem:
    name: str
    description: str


@dataclass
class FreeItem(InventoryItem):
    quantity: int

    def __str__(self):
        return f'{self.quantity} x {self.name}'


@dataclass
class Product(InventoryItem):
    price_each: Decimal

    def __str__(self):
        return f'{self.name} @ {self.price_each}'


@dataclass
class LineItem(Product):
    quantity: int

    @property
    def line_price(self):
        return self.price_each * int(self.quantity)

    def __str__(self):
        return f'{self.quantity} x {self.name} @ {self.price_each} = {self.line_price}'

    def __repr__(self):
        return f'LineItem({self.name} x {self.quantity})'


@dataclass
class Order:
    customer: dict
    line_items: list[LineItem] = field(default_factory=list)
    free_items: list[FreeItem] | None = None
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
class HireOrder(Order):
    duration: int = 1

    def __str__(self):
        return f'Order for {self.duration} weeks with {len(self.line_items)} lines for £{self.total}'


@dataclass
class HireDates:
    invoice: datetime.date
    start: datetime.date
    end: datetime.date

    @classmethod
    def from_hire(cls, hire: dict):
        date_inv = hire['Booked Date']
        date_start = hire['Send Out Date']
        date_end = hire['Due Back Date']
        return cls(invoice=date_inv, start=date_start, end=date_end)


@dataclass
class SaleInvoice:
    inv_num: str
    dates: datetime.date
    inv_add: 'Address1'
    del_add: 'Address1'
    order: Order


@dataclass
class HireInvoice(SaleInvoice):
    order: HireOrder
    dates: HireDates

    @classmethod
    def from_hire(cls, hire: dict, order: HireOrder, inv_num: str | None = None):
        inv_num = inv_num or next_inv_num()
        # del_add, inv_add = addresses_from_hire(hire)
        del_add, inv_add = Address1.from_hire(hire)
        dates = HireDates.from_hire(hire)
        return cls(inv_num=inv_num, dates=dates, inv_add=inv_add, del_add=del_add, order=order)


@dataclass
class Address1:
    add: str
    pc: str

    @classmethod
    def from_sale(cls, sale: dict):
        i_add = sale['Invoice Address']
        i_pc = sale['Invoice Postcode']
        d_add = sale['Delivery Address']
        d_pc = sale['Delivery Postcode']
        inv_add = cls(add=i_add, pc=i_pc)
        del_add = cls(add=d_add, pc=d_pc)
        return del_add, inv_add

    @classmethod
    def from_hire(cls, hire: dict):
        i_add = hire['customer']['Address']
        i_pc = hire['customer']['Postcode']
        d_add = hire['Delivery Address']
        d_pc = hire['Delivery Postcode']
        inv_add = cls(add=i_add, pc=i_pc)
        del_add = cls(add=d_add, pc=d_pc)
        return del_add, inv_add


def addresses_from_sale(sale: dict) -> (Address1, Address1):
    i_add = sale['Invoice Address']
    i_pc = sale['Invoice Postcode']
    d_add = sale['Delivery Address']
    d_pc = sale['Delivery Postcode']
    inv_add = Address1(add=i_add, pc=i_pc)
    del_add = Address1(add=d_add, pc=d_pc)
    return del_add, inv_add


def addresses_from_hire(hire: dict):
    i_add = hire['customer']['Address']
    i_pc = hire['customer']['Postcode']
    d_add = hire['Delivery Address']
    d_pc = hire['Delivery Postcode']
    inv_add = Address1(add=i_add, pc=i_pc)
    del_add = Address1(add=d_add, pc=d_pc)
    return del_add, inv_add
