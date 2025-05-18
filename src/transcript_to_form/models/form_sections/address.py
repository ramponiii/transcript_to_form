from pydantic import BaseModel, Field

# assumed that clients live at same address. the address form field does not appear to be client specific. I think this is not robust.


class Address(BaseModel):
    """Represents an individual address"""

    ownership_status: str | None = Field(
        None, description="The ownership status of the property (e.g., Owned, Rented)."
    )
    postcode: str | None = Field(None, description="The postal code or ZIP code.")
    house_name_number: str | None = Field(
        None,
        description="The name or number of the house/building.",
    )
    street_name: str | None = Field(None, description="The name of the street.")
    address_line_3: str | None = Field(
        None, description="Optional third line of the address."
    )
    address_line_4: str | None = Field(
        None, description="Optional fourth line of the address."
    )
    town_city: str = Field(
        ..., alias="town_or_city", description="The town or city name."
    )
    county: str | None = Field(None, description="The county or administrative region.")
    country: str | None = Field(None, description="The country name.")
    move_in_date: str | None = Field(
        None, description="The date the resident moved into this address."
    )


class Addresses(BaseModel):
    address: Address | None = Field(None, description="Current Address")
    previous_addressess: list[Address] = Field(
        default_factory=list, description="Previous Addresses"
    )
