from django import template
register = template.Library()

@register.filter
def get_stock_by_symbol(stocks, symbol):
    """
    Returns the Stock object from a list of stocks by its symbol.
    """
    return next((s for s in stocks if s.symbol == symbol), None)
