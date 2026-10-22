"""Inventory-wide eligibility review; explicit maps override exclusion categories."""
import csv,json,re
from collections import Counter
from pathlib import Path


def disposition(code,title):
    n=int(code[3:7]) if code.startswith('VCF') else 0
    t=title.lower()
    if code in ['VCF0906','VCF0907']:return 'source_correction_pending','Codebook reports 2016 House-candidate thermometer corrections in progress; withhold until resolved.'
    if code in ['VCF0302','VCF0305']:return 'partisan_variant','Nominal initial response or strength-only measure; use the mapped 7-point party-identification summary.'
    if 306<=n<=313:return 'family_or_interest','Parental political affiliation or political interest/attention is not the respondent’s directional policy preference.'
    if n in [873]:return 'personal_characteristic','Experience of medical affordability is not an expressed policy position.'
    if n in [9008,9010,9011,9012,9204,9205]:return 'party_competence','Perceived party competence/representation does not identify the respondent’s desired policy direction.'
    if 9021<=n<=9036 or 9054<=n<=9055 or 9063<=n<=9067 or 9260<=n<=9266:return 'electoral_behavior','Political participation, knowledge, campaign exposure or election context rather than a direct policy preference.'
    if n in [9070,9071,9072]:return 'unspecified_legislation','Agreement or recall about an unspecified incumbent/bill has no fixed policy direction without identifying the legislation.'
    if n in [822,9044,9052,9221]:return 'performance_or_conditions','Evaluation of government/economic performance depends on administration and is not a fixed ideological score.'
    if n in [9239]:return 'salience','Issue importance measures strength of attention, not support or opposition.'
    if n in [9244,9250,9251,9252,9253,9256,9257,9258,9259,9203]:return 'trust_efficacy_participation','Trust, representation, political efficacy/knowledge or civic participation does not have a fixed ideological sign.'
    if n<100 or code=='VCF9999':return 'administrative','Survey administration, identifier, weight, or interviewer assessment; not a respondent policy position.'
    if 100<=n<200 or 860<=n<=866 or code in ['VCF9001','VCF9002','VCF9224','VCF9243','VCF9277','VCF9278','VCF9279','VCF9280','VCF9281','VCF9282']:
        return 'personal_characteristic','Demographic, religious affiliation/practice, household circumstance or personal experience; do not infer ideology from identity.'
    if 'mention' in t and ('like about' in t or 'dislike about' in t or 'most important' in t):return 'nominal_response_topics','Topic identifiers from open-ended responses are not ordered ideological scores.'
    if 'thermometer' in t:return 'ambiguous_affect','Warmth toward a person/group/institution is not a stable ideological endpoint; only explicitly partisan/ideological targets are mapped.'
    if 501<=n<=550 or 9073<=n<=9121 or n in [9234,9235,9241,9242]:return 'perceived_position','Rates a party, candidate or government position rather than the respondent’s own preferred policy.'
    if 'salience' in t or 'number of mentions' in t or 'relative salience' in t:return 'salience','Attention or number of reasons mentioned does not encode liberal/conservative direction.'
    if 'affect' in t:return 'derived_affect','Derived party/candidate affect index; avoid duplicating direct feeling ratings without validating its construction.'
    if 338<=n<=373 or 9209<=n<=9216:return 'candidate_traits','Candidate competence, character or emotional reaction is not a direct ideological stance; excluded from topic policy averages.'
    if 600<=n<=675:return 'trust_efficacy_participation','Trust, efficacy, civic participation or protest approval is not consistently liberal/conservative across administrations and causes.'
    if 700<=n<=750:return 'electoral_behavior','Voting, registration, campaigning, media exposure or political knowledge; does not directly score a policy preference.'
    if 900<=n<=978 or 1004<=n<=1016 or 9122<=n<=9125 or 9149<=n<=9155:return 'election_contact_administration','Electoral context, constituency service, contact, recall or administration rather than ideological policy preference.'
    if any(x in t for x in ['approve','performance','satisfied','better','worse','right track','weaker/stronger','income kept','retrospective']):return 'performance_or_conditions','Evaluation of conditions/performance is not a fixed ideological direction; may depend on administration or context.'
    if 'likes anything' in t or 'dislikes anything' in t:return 'one_sided_affect','Absence of something liked/disliked does not establish the opposite ideology; prefer bipolar feeling ratings.'
    if n in [813,820,821,825,848,9223,9225,9226,9227,9228,9229,9270,9271,9272,9273,9274,9275]:return 'descriptive_belief','Belief about conditions, risks or groups is not itself a policy preference; no automatic ideological mapping.'
    if n in [823,826,827,840,841,844,888,892,9019,9020,9048,9134,9206,9230,9231]:return 'cross_cutting_policy','Policy trade-off does not have a stable liberal/conservative sign across this historical period; needs a period-specific interpretation.'
    if n in [845,846,847,850,9246,9247,9248,9249]:return 'religion_or_values_proxy','Religious belief or child-rearing preference is an indirect ideology proxy, not a direct political stance.'
    if n==9043 and code.endswith('a'):return 'strength_only_followup','Strength without direction; parent school-prayer question supplies direction and is already mapped.'
    return None


def main():
    variables=list(csv.DictReader(open('data/processed/anes-20260205/variables.csv')))
    mappings={e['code']:e for e in json.load(open('data/anes/response_mappings.json'))['entries']}
    rows=[];unknown=[]
    for r in variables:
        code,title=r['code'],r['description']
        if code in mappings:
            e=mappings[code];category,reason='mapped',e['rationale'];family=e['family']
        else:
            result=disposition(code,title)
            if result is None:unknown.append((code,title));continue
            category,reason=result;family=''
        rows.append(dict(code=code,description=title,status=category,family=family,reason=reason))
    if unknown:
        print('\n'.join(f'{c} {t}' for c,t in unknown));print('UNRESOLVED',len(unknown));return
    with open('data/anes/mapping_coverage.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summary=dict(variables=len(rows),mapped_variables=len(mappings),mapped_families=len({e['family'] for e in mappings.values()}),categories=dict(Counter(r['status'] for r in rows)))
    Path('data/anes/inventory_review.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
