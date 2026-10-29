"""Sample module for analyzer tests."""


def calculate_total(price: float, quantity: int = 1) -> float:
    """Calculate the total price."""
    return price * quantity


async def fetch_record(record_id: str) -> dict:
    """Fetch a record by its ID."""
    return {"id": record_id}


class Calculator:
    """A simple calculator."""

    def add(self, a: int, b: int = 0) -> int:
        """Add two numbers."""
        return a + b