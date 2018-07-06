#EXAMPLE PLOTS
################################################################################
################################################################################
################################################################################

#PUBLIC OPINION SUPPORT for three LGBTQ issues
################################################################################

#public support for LGBTQ issues
plt.plot(gay_temp_yr_avg.keys(),gay_temp_yr_avg.values(),'g^',label='Gay/Lesbian Thermometer')
plt.plot(gay_mil_yr_avg.keys(),gay_mil_yr_avg.values(),'bs',label='Gays in the Military')
plt.plot(gay_adopt_yr_avg.keys(),gay_adopt_yr_avg.values(),'m.',label='Gays Adopting')

plt.axhline(y=.5)

plt.legend()
plt.xlabel('Time (year)')
plt.ylabel('Support')
plt.title('Public Support for LGBTQ Issues')
plt.grid(True)

min_yr=min(list(sc_support.keys())+list(gay_temp_yr_avg.keys())+list(gay_mil_yr_avg.keys())+list(gay_adopt_yr_avg.keys()))
plt.axis([min_yr-4, CURRENT_YEAR, 0.0, 1.1])

plt.savefig('./plots/po_support.png', bbox_inches='tight')
#plt.show()
plt.gcf().clear()

#SUPREME COURT SUPPORT v. PUBLIC SUPPORT for three LGBTQ questions
################################################################################

#public support for gay issues
plt.plot(gay_temp_yr_avg.keys(),gay_temp_yr_avg.values(),'g^',label='Gay/Lesbian Thermometer')
plt.plot(gay_mil_yr_avg.keys(),gay_mil_yr_avg.values(),'bs',label='Gays in the Military')
plt.plot(gay_adopt_yr_avg.keys(),gay_adopt_yr_avg.values(),'m.',label='Gays Adopting')

#supreme court decisions
plt.plot(sc_support.keys(),sc_support.values(),'ro',label='Supreme Court Supp. Vote Ratio')

plt.axhline(y=.5)

plt.legend()
plt.xlabel('Time (year)')
plt.ylabel('Support')
plt.title('SC v. PO for Gay/Lesbian Issues')
plt.grid(True)

min_yr=min(list(sc_support.keys())+list(gay_temp_yr_avg.keys())+list(gay_mil_yr_avg.keys())+list(gay_adopt_yr_avg.keys()))
plt.axis([min_yr-4, CURRENT_YEAR, 0.0, 1.1])

plt.savefig('./plots/sc_v_po.png', bbox_inches='tight')
#plt.show()
plt.gcf().clear()
