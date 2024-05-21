"""
Units-Handling and Units Definitions
====================================

Includes modules and classes from the `pint` Units package.
"""

import pint
import pint_pandas

u: pint.UnitRegistry = pint.UnitRegistry()
"""
Pint UnitRegistry object containing all of the units for the analysis
"""

u.define('percent = dimensionless / 100 = pct')
u.define('gear = dimensionless')

Q_: pint.Quantity = u.Quantity
"""
Generic Pint Quantity object, enabling simple unit assignment to
non-dimensioned values.
"""

pint_pandas.PintType.ureg = u
pint_pandas.PintType.ureg.setup_matplotlib()
