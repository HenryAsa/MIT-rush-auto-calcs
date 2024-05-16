import pint
import pint_pandas

u = pint.UnitRegistry()
Q_ = u.Quantity
u.define('percent = pct = dimensionless / 100')
u.define('gear = dimensionless')

pint_pandas.PintType.ureg = u
pint_pandas.PintType.ureg.setup_matplotlib()
