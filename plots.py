import matplotlib.pyplot as plt

#public support for gay issues
plt.plot(gay_temp_yr_avg.keys(),gay_temp_yr_avg.values(),'g^',label='Gay/Lesbian Thermometer')
plt.plot(gay_mil_yr_avg.keys(),gay_mil_yr_avg.values(),'bs',label='Gays in the Military')
plt.legend()
plt.title('Public Support for Gay/Lesbian Issues')

min_yr=min(list(gay_temp_yr_avg.keys())+list(gay_mil_yr_avg.keys()))
plt.axis([min_yr-4, CURRENT_YEAR, 0.0, 1.0])
