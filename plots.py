import matplotlib.pyplot as plt

#public support for gay issues
plt.plot(gay_temp_yr_avg.keys(),gay_temp_yr_avg.values(),'g^',label='Gay/Lesbian Thermometer')
plt.plot(gay_mil_yr_avg.keys(),gay_mil_yr_avg.values(),'bs',label='Gays in the Military')

#supreme court decisions
plt.plot(sc_support.keys(),sc_support.values(),'ro',label='Supreme Court Supp. Vote Ratio')

plt.axhline(y=.5)

plt.legend()
plt.xlabel('Time (year)')
plt.ylabel('Support')
plt.title('SC v. PO for Gay/Lesbian Issues')
plt.grid(True)

min_yr=min(list(sc_support.keys())+list(gay_temp_yr_avg.keys())+list(gay_mil_yr_avg.keys()))
plt.axis([min_yr-4, CURRENT_YEAR, 0.0, 1.1])
