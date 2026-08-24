def _brl(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "x").replace(".", ",").replace("x", ".")


def _date_br(value: str) -> str:
    y, m, d = value.split("-")
    return f"{d}/{m}/{y}"
