from decimal import Decimal
from typing import Annotated
from annotated_types import Len
from pydantic import BaseModel, Field
from datetime import date

SLUG = r"^[\w-]+$"
DATE = r"^\d{4}-\d{2}-\d{2}$"


class Company(BaseModel):
    name: str = Field(max_length=100)
    description: str | None = Field(max_length=100)

    address: str | None = Field(max_length=100)
    tax_id: str | None = Field(max_length=100)

    email: str | None = Field(max_length=100)
    phone: str = Field(max_length=30, default=None)
    web: str = Field(max_length=30)

    bank: str | None = Field(max_length=100, default=None)
    bic: str | None = Field(max_length=100, default=None)
    iban: str | None = Field(max_length=100, default=None)


class Customer(BaseModel):
    name: str = Field(max_length=100)
    address: str | None = Field(max_length=100, default=None)
    email: str | None = Field(max_length=100, default=None)
    phone: str = Field(max_length=30, default=None)


class InvoicePosition(BaseModel):
    description: str | None = Field(max_length=100)
    quantity: Decimal = Field(max_digits=10, decimal_places=3, default=Decimal("1.00"))
    rate: Decimal = Field(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    amount: Decimal | None = Field(max_digits=10, decimal_places=2, default=None)


class Invoice(BaseModel):
    draft: bool | None = False
    language: str | None = Field(max_length=100, default='en')
    color: str | None = Field(max_length=100, default='000000')
    template: str | None = Field(max_length=100, default='default', pattern=SLUG)
    invoice_id: str | None = Field(max_length=100, default=None)
    created_date: date | None = Field(default=date.today())
    due_date: date | None = Field(default=None)

    tax: Decimal = Field(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    currency: str | None = Field(max_length=100, default="EUR")
    hourly_rate: Decimal = Field(decimal_places=2, max_digits=10, default=Decimal("0.00"))

    body: str | None = Field(max_length=200, default=None)
    footer: str | None = Field(max_length=200, default=None)

    company: Company
    customer: Customer
    # positions: list[InvoicePosition]
    positions: Annotated[list[InvoicePosition], Len(min_length=1, max_length=100)] | None = None
