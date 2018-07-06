#EXMAPLE QUESTIONS

#question VCF0232 - from ANES "GROUP THERMOMETER: Gays and Lesbians"
#"Gay men and lesbians (that is), homosexuals -- thermometer"
#0-96 temp, 97 unclear, 98=DK, 99=NA, INAP=inappropriate
gay_temp_yr_avg=col_yr_avg('VCF0232')

#question VCF0877 - from ANES "Strength of Position on Gays in the Military"
#"Do you feel strongly or not strongly that homosexuals should be
#allowed to serve in the United States Armed forces?"
#1 - strongly, allowed  ---> 3
#2 - not strongly, allowed  ---> 2
#4 - not strongly, not be allowed   ---> 1
#5 - strongly, not allowed   ---> 0
#7 - DK if favor or oppose; depends (1988); ---> nan
#9 -  NA if favor or oppose ---> nan
#INAP - inappropriate ---> nan
gay_mil_yr_avg=col_yr_avg('VCF0877')

#question VCF0878 - ISSUES: Should Gays/Lesbians Be Able to Adopt Children
#---------
#VALID_CODES:
#------------
#1.  Yes -----> 1
#5.  No ------> 0
#8.  DK ------> nan
#MISSING_CODES:
#--------------
#9.  NA; no Post IW
#INAP. Inap. question not used
gay_adopt_yr_avg=col_yr_avg('VCF0878')

#=============================================================================
#VCF0876
#
#ISSUES: Law to Protect Homosexuals Against Discrimination
#
#Q:
#---------
#Do you favor or oppose laws to protect homosexuals against job
#discrimination?

#VALID_CODES:
#------------
#1.  Favor
#5.  Oppose
#8.  DK; depends (1988)
#
#MISSING_CODES:
#--------------
#9.  NA; no Post IW
#INAP. Inap. question not used
gay_protect_yr_avg=col_yr_avg('VCF0876')
