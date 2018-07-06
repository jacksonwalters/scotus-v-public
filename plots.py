import matplotlib.pyplot as plt

#SUPREME COURT SUPPORT v. PUBLIC SUPPORT
################################################################################

#public support for gay issues on average
plt.plot(all_po_avg.keys(),all_po_avg.values(),'bo',label='Public Support')

#supreme court decisions
plt.plot(sc_support.keys(),sc_support.values(),'ro',label='Supreme Court Supp. Support')

plt.axhline(y=.5)

plt.legend()
plt.xlabel('Time (year)')
plt.ylabel('Support')
plt.title('SC v. PO Support for LGBTQ Issues')
plt.grid(True)

min_yr=min(list(sc_support.keys())+list(all_po_avg.keys()))
plt.axis([min_yr-4, CURRENT_YEAR, 0.0, 1.1])

plt.savefig('./plots/avg_sc_v_po.png', bbox_inches='tight')
#plt.show()
plt.gcf().clear()
