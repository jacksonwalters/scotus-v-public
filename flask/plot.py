import matplotlib.pyplot as plt
import scipy.stats as stats
import scipy.optimize as opt
import numpy as np
from matplotlib import cm
from numpy.random import randn
import time, os

CURRENT_YEAR=2021
MIN_YEAR = 2000
NEUTRAL = 0 #the line deciding which side of the issue
IMG_PATH='./static/images/'

#create plot of both SCOTUS & public opinion polarity given {YEAR:POLARITY}
def scotus_v_public_plot(sc_polarity=None,po_polarity=None,title="ISSUE"):

    #create figure, axes
    fig = plt.figure()
    ax = fig.add_subplot(111)

    min_year = MIN_YEAR  #minimum year for t-axis on plot

    #PUBLIC OPINION
    if po_polarity: #check if po_polarity is None *or* an empty dictionary
        x_po=list(po_polarity.keys()) #get public opinion years
        y_po=list(po_polarity.values()) #get public opinion polarity values
        min_year = min(x_po+[min_year]) #update minimum year from public opinion data
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_po,y_po) #get basic stats
        po_deg1=np.polyfit(x_po,y_po,1); f1 = np.poly1d(po_deg1) #degree 1 model for PO
        p_shift_po=opt.fsolve(f1-NEUTRAL,2000) #find "paradigm shift" for PO. assuming one point of intersectionself. this is guaranteed for a linear fit.
        ax.plot([p_shift_po], [NEUTRAL], marker='|', markersize=7, color="black") #include vertical lines at crossover moments
        ax.scatter(x_po,y_po,c='b',marker="x",label='Public Opinion',vmin=-1, vmax=1) #average public opinion on issue
        ax.plot(x_po,f1(x_po),'-b') #plot model for PO data

    #SCOTUS OPINIONS
    if sc_polarity: #check if sc_polarity is None *or* an empty dictionary
        x_sc=list(sc_polarity.keys()) #get scotus years
        y_sc=list(sc_polarity.values()) #get scotus polarity values
        min_year = min(x_sc+[min_year]) #update minimum year from scotus data
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_sc,y_sc) #get basic stats
        sc_deg1=np.polyfit(x_sc,y_sc,1); g1 = np.poly1d(sc_deg1) #degree 1 model for SC
        p_shift_sc=opt.fsolve(g1-NEUTRAL,2000) #find "paradigm shift" for SC assuming one point of intersection. this is guaranteed for a linear fit.
        sc_scatter=ax.scatter(x_sc,y_sc,c='r',marker="+",label='Supreme Court',vmin=-1, vmax=1) #supreme court decisions
        ax.plot(x_sc,g1(x_sc),'-r') #plot model for SC data
        ax.plot([p_shift_sc], [NEUTRAL], marker='|', markersize=7, color="black") #include vertical lines at crossover moments

    ax.axhline(y=NEUTRAL,color='k') #include horizontal neutral opinion line. purple='#551A8B'

    ax.legend()
    plt.xlabel('Time (year)')
    plt.ylabel('Polarity')
    plt.title('SCOTUS v. Public Opinion on ' + title)
    plt.grid(True)
    plt.yticks(np.arange(-1,2,1),["Conservative","Neutral","Liberal"]) #y-ticks are -1, 0, +1

    plt.axis([min_year-2, CURRENT_YEAR, -1.1, 1.1])

    #remove previous plot and save new one with title corresponding to keywords
    plot_filename = "sc_v_po_" + title + ".png"
    for filename in os.listdir('./static/images/'):
        if filename.startswith('sc_v_po_'):
            os.remove('./static/images/' + filename)
    plt.savefig(IMG_PATH+plot_filename, bbox_inches='tight')
    plt.gcf().clear()

    return plot_filename
