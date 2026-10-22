"""Materialize reviewed response mappings from the matching extracted codebook."""
import csv
import hashlib
import json
from pathlib import Path
import re
import sys
from audit_anes import blocks

text = Path(sys.argv[1])
book = blocks(text.read_text())
titles = {r['code']: r['description'] for r in csv.DictReader(open('data/processed/anes-20260205/variables.csv'))}
entries = {}

def add(codes, low, high, direction, reason, family=None, valid=None):
    for code in codes.split():
        page, fields = book[code]
        values = valid if valid is not None else range(low, high+1)
        weights = re.findall(r'VCF\d{4}z', fields.get('Weight',''))
        if len(set(weights)) != 1:
            raise ValueError((code, fields.get('Weight')))
        entries[code] = dict(code=code, title=titles[code], question=fields['Question'],
            scores={str(v): round(direction*(2*(v-low)/(high-low)-1), 12) for v in values},
            rationale=reason, family=family or code, priority=0, weight=weights[0],
            pdf_page=page, valid_definition=fields.get('Valid',''), missing_definition=fields.get('Missing',''),
            notes=fields.get('Notes',''))

add('VCF0803',1,7,-1,'Self-placement from liberal to conservative.', 'self_ideology')
add('VCF0804',1,3,-1,'Collapsed liberal to conservative self-placement.', 'self_ideology')
add('VCF0824 VCF0849',1,5,-1,'Liberal, moderate, conservative self-placement.', 'self_ideology', [1,3,5])
add('VCF0805',1,2,-1,'Government medical assistance is the liberal endpoint.', 'health_insurance')
add('VCF0806',1,7,-1,'Government insurance versus private insurance.', 'health_insurance')
add('VCF0808',1,2,-1,'Government guarantee of jobs/income is the liberal endpoint.', 'jobs_income')
add('VCF0809',1,7,-1,'Government guarantee versus individual responsibility.', 'jobs_income')
add('VCF0811',1,7,-1,'Address poverty rather than use force in response to urban unrest.')
add('VCF0814',1,3,-1,'Faster civil-rights progress is the liberal endpoint.')
add('VCF0815',1,3,-1,'Desegregation versus strict segregation.')
add('VCF0816',1,2,-1,'Government action for school integration.')
add('VCF0817',1,7,-1,'Busing to achieve integration is the liberal endpoint.')
add('VCF0818',1,5,-1,'Government assurance of fair jobs/housing; uncertain category 3 excluded.',valid=[1,2,4,5])
add('VCF0819',1,2,1,'Equal access to housing versus racial exclusion.')
add('VCF0828',1,2,-1,'Reduced military spending is the liberal endpoint.', 'defense_spending')
add('VCF0843',1,7,-1,'Reduced versus increased defense spending.', 'defense_spending')
add('VCF0830',1,7,-1,'Government assistance to Black Americans versus self-reliance.')
add('VCF0832',1,7,-1,'Protect rights of accused versus stopping crime regardless of rights.')
add('VCF0833',1,5,-1,'Approval of the Equal Rights Amendment.',valid=[1,5])
add('VCF0834',1,7,-1,'Equal roles for women and men is the liberal endpoint.')
add('VCF0836',1,2,1,'Disagreement that women should stay out of politics.')
add('VCF0837 VCF0838',1,4,1,'More permissive abortion policy is the liberal endpoint.', 'abortion')
add('VCF0839',1,7,1,'More government services/spending is the liberal endpoint.')
add('VCF0842',1,7,-1,'Stronger environmental regulation is the liberal endpoint.')
add('VCF0851 VCF0853',1,5,1,'Disagreement with traditionalist social-values statement.')
add('VCF0852 VCF0854',1,5,-1,'Agreement with acceptance of changing or differing moral standards.')
add('VCF0867',1,5,-1,'Support for affirmative action in hiring.', 'affirmative_action', [1,5])
add('VCF0867a',1,5,-1,'Strength of support for affirmative action.', 'affirmative_action', [1,2,4,5])
add('VCF0876',1,5,-1,'Support for gay/lesbian employment discrimination protections.', 'gay_discrimination', [1,5])
add('VCF0876a',1,5,-1,'Strength of support for discrimination protections.', 'gay_discrimination', [1,2,4,5])
add('VCF0877',1,5,-1,'Support for gays serving in the military.', 'gay_military', [1,5])
add('VCF0877a',1,5,-1,'Strength of support for gays serving in the military.', 'gay_military', [1,2,4,5])
add('VCF0878',1,5,-1,'Support for gay/lesbian adoption.',valid=[1,5])
add('VCF0879',1,5,-1,'Increased immigration is the liberal endpoint; unchanged is midpoint.', 'immigration')
add('VCF0879a',1,5,-1,'Increased versus decreased immigration.', 'immigration', [1,3,5])
add('VCF0886 VCF0887 VCF0889 VCF0890 VCF0891 VCF0893 VCF0894',1,3,-1,'Increased social-program spending is the liberal endpoint.')
add('VCF9013 VCF9015 VCF9018 VCF9039 VCF9042',1,5,-1,'Agreement with equal opportunity or structural-disadvantage statement.')
add('VCF9014 VCF9017 VCF9038 VCF9040 VCF9041',1,5,1,'Disagreement with opposition to equality measures or individual-blame statement.')
add('VCF9037',1,5,-1,'Federal action for fair employment of Black Americans.',valid=[1,5])
add('VCF9236',1,2,1,'Opposition to the death penalty is the liberal endpoint.')
add('VCF9238',1,3,-1,'More difficult gun purchases are liberal; easier are conservative; unchanged is midpoint.')
# Additional direct policy preferences; code 7 is a special category, not a
# numeric distance beyond decreased spending. Collapse both reductions to -1.
for code in ['VCF9046','VCF9047','VCF9049','VCF9050']:
    add(code,1,3,-1,'More social/environmental spending is liberal; decreased or eliminated spending is conservative.')
    entries[code]['scores']['7'] = -1
add('VCF9131',1,2,1,'More government activity is the liberal endpoint; less government is conservative.')
add('VCF9232',1,3,1,'Opposition to government torture is the liberal endpoint.', 'torture')
add('VCF9233',1,7,1,'Strength of opposition to government torture.', 'torture')
entries['VCF9233']['priority'] = 10
entries['VCF9236']['family'] = 'death_penalty'
add('VCF9237',1,5,1,'Strength of opposition to the death penalty.', 'death_penalty', [1,2,4,5])
entries['VCF9237']['priority'] = 10

# Prefer detailed scales, then the newer abortion wording when both exist.
for code in 'VCF0803 VCF0806 VCF0809 VCF0843 VCF0838 VCF0867a VCF0876a VCF0877a VCF0879'.split():
    entries[code]['priority'] = 10
# Explicitly partisan thermometers: preserve numeric degrees (97 is a top-coded 97-100 bin).
for code, sign, family in [('VCF0201',1,'dem_thermometer'),('VCF0218',1,'dem_thermometer'),('VCF0202',-1,'rep_thermometer'),('VCF0224',-1,'rep_thermometer'),('VCF0211',1,'liberal_thermometer'),('VCF0212',-1,'conservative_thermometer')]:
    add(code,0,100,sign,'Warmth toward the named partisan/ideological group; 97 top-coded to 100.',family,range(97))
    entries[code]['scores']['97'] = sign
for code in ['VCF0218','VCF0224']: entries[code]['priority']=10
# Inventory-wide review additions.
add('VCF0829',1,2,-1,'Acceptance of federal government power versus concern it is too powerful.')
add('VCF9016',1,5,1,'Disagreement that unequal chances in life are not a serious problem.')
add('VCF9043',1,4,-1,'Less state-sponsored school prayer is the liberal endpoint.', 'school_prayer')
add('VCF9051',1,5,1,'Opposition to public schools starting the day with prayer.', 'school_prayer', [1,5])
entries['VCF9043']['priority']=10
add('VCF9132',1,2,-1,'Government action versus free-market handling of economic problems.')
add('VCF9133',1,2,1,'Government growth justified by larger problems versus unnecessary intervention.')
add('VCF9240',0,10,-1,'Self-placement: left is liberal-positive, right conservative-negative.', 'self_ideology')
add('VCF0301',1,7,-1,'Explicit party-identification proxy: Democrat positive, Republican negative; not direct policy opinion.', 'party_identification')
add('VCF0303',1,3,-1,'Collapsed party-identification proxy: Democrat positive, Republican negative.', 'party_identification')
entries['VCF0301']['priority']=10
for code,sign,family in [('VCF0424',1,'dem_pres_affect'),('VCF0425',1,'dem_vp_affect'),('VCF0426',-1,'rep_pres_affect'),('VCF0427',-1,'rep_vp_affect'),('VCF9056',1,'dem_senate_affect'),('VCF9057',-1,'rep_senate_affect')]:
    topcoded=code.startswith('VCF04')
    add(code,0,100,sign,'Explicit partisan affect proxy; warmer Democratic ratings positive, Republican negative.',family,range(97 if topcoded else 101))
    if topcoded: entries[code]['scores']['97']=sign
    entries[code]['priority']=10
for code,sign,family in [('VCF9201',1,'dem_thermometer'),('VCF9202',-1,'rep_thermometer'),('VCF9207',1,'dem_pres_affect'),('VCF9208',-1,'rep_pres_affect')]:
    add(code,0,10,sign,'Bipolar partisan affect proxy, normalized from the original 0–10 scale.',family)

# Expanded explicitly identified partisan traits and ideological movement affect.
# These are proxies, not direct policy preferences, and are labelled as such.
traits=['intelligence','compassion','decency','inspiration','knowledge','morality','leadership','care']
for start,party,direction in [(350,'dem',-1),(362,'rep',1)]:
    for offset,trait in enumerate(traits):
        code=f'VCF{start+offset:04}'
        add(code,1,4,direction,'Partisan candidate-trait proxy: favorable Democratic assessment positive; favorable Republican assessment negative.',f'{party}_candidate_{trait}')
        entries[code]['measurement_type']='partisan_proxy'
for start,party,direction in [(9209,'dem',-1),(9213,'rep',1)]:
    for offset,trait in enumerate(['leadership','care','knowledge','honesty']):
        code=f'VCF{start+offset:04}'
        add(code,1,5,direction,'Five-point partisan candidate-trait proxy; equal ordinal spacing assumed.',f'{party}_candidate_{trait}')
        entries[code]['measurement_type']='partisan_proxy'
        entries[code]['priority']=10
for code,sign,family in [('VCF0209',-1,'business_affect'),('VCF0210',1,'union_affect'),('VCF0216',1,'civil_rights_affect'),('VCF0225',1,'feminist_affect'),('VCF0229',1,'environmentalist_affect'),('VCF0230',-1,'anti_abortion_affect'),('VCF0253',1,'feminist_affect')]:
    add(code,0,100,sign,'Movement/economic-group affect proxy using the historical project orientation; warmth is not a direct policy position.',family,range(97))
    entries[code]['scores']['97']=sign
    entries[code]['measurement_type']='movement_proxy'
entries['VCF0253']['priority']=10
for code,e in entries.items():
    if 'proxy' in e['rationale'].lower() or 'partisan' in e['rationale'].lower():
        e.setdefault('measurement_type','partisan_proxy')
    elif 'thermometer' in e['title'].lower():
        e.setdefault('measurement_type','ideological_affect')
    else:
        e.setdefault('measurement_type','policy_or_self_placement')

# Bipolar comparative thermometer indices preserve their documented neutral point.
for code,family,dependencies in [('VCF0291','comparative_party_affect',['VCF0201','VCF0218','VCF0202','VCF0224','VCF9201','VCF9202']),('VCF0413','comparative_pres_affect',['VCF0424','VCF0426','VCF9207','VCF9208']),('VCF0415','comparative_vp_affect',['VCF0425','VCF0427'])]:
    add(code,0,100,1,'Comparative partisan thermometer index: preserve 50 as neutral; (code-50)/50.',family,range(2,100))
    entries[code]['measurement_type']='partisan_proxy'
    entries[code]['supersedes']=dependencies
add('VCF0801',0,97,-1,'Comparative liberal/conservative affect index; piecewise scaling preserves documented neutral code 49.','comparative_ideology_affect')
entries['VCF0801']['scores']={str(v):(49-v)/(49 if v<=49 else 48) for v in range(98)}
entries['VCF0801']['measurement_type']='ideological_affect'
entries['VCF0801']['supersedes']=['VCF0211','VCF0212']

path=Path('data/anes/response_mappings.json')
path.write_text(json.dumps(dict(version='explicit-anes-v1', codebook_sha256=hashlib.sha256(Path('data/raw/rebuild/anes-20260205/anes_timeseries_cdf_codebook_var_20260205.pdf').read_bytes()).hexdigest(),
    convention='positive liberal; negative conservative; uniform numeric spacing is an exploratory assumption',
    entries=list(entries.values())),indent=2)+'\n')
with open('data/anes/mapping_coverage.csv','w',newline='') as f:
    w=csv.writer(f);w.writerow(['code','description','status'])
    for code,title in titles.items():
        w.writerow([code,title,'mapped' if code in entries else 'excluded_pending_interpretation_or_not_a_directional_opinion'])
print(len(entries),'explicit mappings')
# Keep the full eligibility inventory synchronized with the generated mappings.
from review_anes_inventory import main as review_inventory
review_inventory()
