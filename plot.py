import matplotlib.pyplot as plt
import scipy.stats as stats
import scipy.optimize as opt
import numpy as np

#STATS & MODEL
################################################################################

#the line deciding which side of the issue
NEUTRAL = .5

#PO
x_po=list(all_po_avg.keys())
y_po=list(all_po_avg.values())

#get basic stats
slope, intercept, r_value, p_value, std_err = stats.linregress(x_po,y_po)

#degree 1 model for PO
po_deg1=np.polyfit(x_po,y_po,1)
f1 = np.poly1d(po_deg1)
#degree 3 model for PO
po_deg3=np.polyfit(x_po,y_po,3)
f3 = np.poly1d(po_deg3)

#find paradigm shift for PO
p_shift_po=opt.fsolve(f3-NEUTRAL,2000)

#SC
x_sc=list(sc_support.keys())
y_sc=list(sc_support.values())

#get basic stats
slope, intercept, r_value, p_value, std_err = stats.linregress(x_sc,y_sc)

#degree 1 model for SC
sc_deg1=np.polyfit(x_sc,y_sc,1)
g1 = np.poly1d(po_deg1)
#degree 3 model for SC
sc_deg3=np.polyfit(x_sc,y_sc,3)
g3 = np.poly1d(po_deg3)

#find paradigm shift for SC
p_shift_sc=opt.fsolve(f3-NEUTRAL,2000)

#SUPREME COURT SUPPORT v. PUBLIC SUPPORT
################################################################################

#average public opinion on issue
plt.plot(all_po_avg.keys(),all_po_avg.values(),'bo',label='Public Support')
#model for PO data
plt.plot(x_po,f3(x_po),'-b')

#supreme court decisions
plt.plot(sc_support.keys(),sc_support.values(),'ro',label='Supreme Court Support')
#model for SC data
plt.plot(x_sc,g3(x_sc),'-r')

#include horizontal neutral opinion line
plt.axhline(y=.5)

plt.legend()
plt.xlabel('Time (year)')
plt.ylabel('Support')
plt.title('SC v. PO Support for ' + ISSUE_NAME)
plt.grid(True)

min_yr=min(list(sc_support.keys())+list(all_po_avg.keys()))
plt.axis([min_yr-4, CURRENT_YEAR, 0.0, 1.1])

plt.savefig('./plots/sc_v_po.png', bbox_inches='tight')
#plt.show()
plt.gcf().clear()
