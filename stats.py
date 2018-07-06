#STATISTICS
################################################################################

import scipy.stats.linregress as splr

x=all_po_avg.keys()
y=all_po_avg.values()

po_lin_regress=splr(x,y,1)
