import matplotlib.pyplot as plt
import scipy.stats as stats
import scipy.optimize as opt
import numpy as np
from matplotlib import cm
from numpy.random import randn

#STATS & MODEL
################################################################################

#PO
x_po=list(po_polarity.keys())
y_po=list(po_polarity.values())

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
x_sc=list(sc_polarity.keys())
y_sc=list(sc_polarity.values())

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

#SUPREME COURT SUPPORT v. PUBLIC SUPPORT
################################################################################

fig = plt.figure()
ax = fig.add_subplot(111)

#average public opinion on issue
ax.scatter(x_po,y_po,c='b',marker="x",label='Public Opinion',vmin=-1, vmax=1)
#model for PO data
ax.plot(x_po,f1(x_po),'-b')

#supreme court decisions
sc_scatter=ax.scatter(x_sc,y_sc,c='r',marker="+",label='Supreme Court',vmin=-1, vmax=1)
#model for SC data
ax.plot(x_sc,g1(x_sc),'-r')

#include horizontal neutral opinion line
#purple='#551A8B'
ax.axhline(y=NEUTRAL,color='k')
#include vertical lines at paradigm shift moments
ax.plot([p_shift_po], [NEUTRAL], marker='|', markersize=7, color="black")
ax.plot([p_shift_sc], [NEUTRAL], marker='|', markersize=7, color="black")

ax.legend()
plt.xlabel('Time (year)')
plt.ylabel('Polarity')
plt.title('SC, PO Polarity on ' + ISSUE_NAME)
plt.grid(True)
plt.yticks(np.arange(-1,2,1),["Conservative","Neutral","Liberal"])

#fig.colorbar(sc_scatter)

min_yr=min(x_po+x_sc)
plt.axis([min_yr-2, CURRENT_YEAR, -1.1, 1.1])

plt.savefig('./plots/sc_v_po_gay_civil_rights.png', bbox_inches='tight')
#plt.show()
plt.gcf().clear()
