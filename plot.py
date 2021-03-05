import matplotlib.pyplot as plt
import scipy.stats as stats
import scipy.optimize as opt
import numpy as np
from matplotlib import cm
from numpy.random import randn
from load_public_data import anes_opinion_data
from search_scotus_opinions_by_keywords import relevant_cases_scdb_df
from search_public_opinions_by_keywords import relevant_questions_anes_df
from polarity_scotus import sc_polarity
from polarity_public import po_polarity

CURRENT_YEAR = 2021
MIN_YEAR = 2000
NEUTRAL = 0 #the line deciding which side of the issue
SURVEY_YEAR_VCF_CODE = 'VCF0004' #ANES code for survey year
IMG_PATH='.\\plots\\' #path to save plot image

#create plot of both SCOTUS & public opinion polarity given {YEAR:POLARITY}
def scotus_v_public_plot(sc_polarity=None,po_polarity=None,title="ISSUE"):

    #create figure, axes
    fig = plt.figure()
    ax = fig.add_subplot(111)

    min_year = MIN_YEAR  #minimum year for t-axis on plot

    #PUBLIC OPINION
    if po_polarity is not None:
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
    if sc_polarity is not None:
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
    ax.legend() #include legend
    plt.xlabel('Time (year)') #label the x-axis, time in years
    plt.ylabel('Polarity') #label the y-axis, liberal v. conservative polarity
    plt.title('SCOTUS v. Public Opinion on ' + title) #include a title
    plt.grid(True)
    plt.yticks(np.arange(-1,2,1),["Conservative","Neutral","Liberal"]) #y-ticks are -1, 0, +1
    plt.axis([min_year-2, CURRENT_YEAR, -1.1, 1.1])

    #save the plot
    plot_filename = "sc_v_po_" + title + ".png"
    plt.savefig(IMG_PATH+plot_filename, bbox_inches='tight')
    plt.gcf().clear()

    return plot_filename

if __name__ == "__main__":
    keywords=["civil","rights","black","negro","vote","free"]
    #get scotus polarity dict
    rel_cases=relevant_cases_scdb_df(keywords) #relevant cases from SCDB as df
    sc_polarity=sc_polarity(rel_cases) #scotus opinion polarity dict {year:polarity}
    #get public polarity dict
    rel_ques_df = relevant_questions_anes_df(keywords) #search the relevant q's & return ANES codebook sub-df
    rel_vcf_codes = [SURVEY_YEAR_VCF_CODE]+list(rel_ques_df['vcf_code']) #get relevant ANES VCF codes. first code gives year
    anes_df = anes_opinion_data() #load the full ANES response data
    rel_ans_df = anes_df.filter(items=rel_vcf_codes) #filter the relevant repsonses/answers by VCF code
    po_polarity=po_polarity(rel_ques_df,rel_ans_df) #dict {year:polarity} for public opinion
    #plot scotus opinions v. public opinions
    scotus_v_public_plot(sc_polarity,po_polarity,title="+".join(keywords))
