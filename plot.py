import matplotlib.pyplot as plt
import scipy.stats as stats
import scipy.optimize as opt
import numpy as np

#the line deciding which side of the issue
NEUTRAL = .5

#STATS & MODEL
################################################################################

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

#find paradigm shift for PO.
#assuming one point of intersectionself.
#this is guaranteed for a linear fit.
p_shift_po=opt.fsolve(f1-NEUTRAL,2000)

#SC
x_sc=list(sc_support.keys())
y_sc=list(sc_support.values())

#get basic stats
slope, intercept, r_value, p_value, std_err = stats.linregress(x_sc,y_sc)

#degree 1 model for SC
sc_deg1=np.polyfit(x_sc,y_sc,1)
g1 = np.poly1d(sc_deg1)
#degree 3 model for SC
sc_deg3=np.polyfit(x_sc,y_sc,3)
g3 = np.poly1d(sc_deg3)

#find paradigm shift for SC.
#assuming one point of intersection.
#this is guaranteed for a linear fit.
p_shift_sc=opt.fsolve(g1-NEUTRAL,2000)

#find difference of paradigm shift
p_shift_diff = p_shift_sc - p_shift_po
p_shift_min = min(p_shift_sc,p_shift_po)

print(p_shift_diff)
print(p_shift_min)

#SUPREME COURT SUPPORT v. PUBLIC SUPPORT
################################################################################

#average public opinion on issue
plt.plot(all_po_avg.keys(),all_po_avg.values(),'bo',label='Public Support')
#model for PO data
plt.plot(x_po,f1(x_po),'-b')

#supreme court decisions
plt.plot(sc_support.keys(),sc_support.values(),'rs',label='Supreme Court Support')
#model for SC data
plt.plot(x_sc,g1(x_sc),'-r')

#include horizontal neutral opinion line
plt.axhline(y=NEUTRAL,color='#551A8B')
#include vertical lines at paradigm shift moments
plt.plot([p_shift_po], [NEUTRAL], marker='x', markersize=7, color="black")
plt.plot([p_shift_sc], [NEUTRAL], marker='x', markersize=7, color="black")

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
