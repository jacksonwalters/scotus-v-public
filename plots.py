import matplotlib.pyplot as plt

plt.plot(gay_temp_yr_avg.keys(),gay_temp_yr_avg.values(),'g^',label='Gay/Lesbian Thermometer')
plt.plot(gay_mil_yr_avg.keys(),gay_mil_yr_avg.values(),'bs',label='Gays in the Military')
plt.legend()
plt.title('Public Support for Gay/Lesbian Issues')
