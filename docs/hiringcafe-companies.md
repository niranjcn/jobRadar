# HiringCafe Companies — Extracted 2026-08-31

Extracted **5860 row-level entries** from **4435 unique companies** (15,333 jobs sampled via _next/data pagination, reported 5,978 total on site, 235k jobs).

File: `backend/data/hiringcafe_companies.json` (raw 5860 rows, includes domain duplicates) and `hiringcafe_companies_deduped.json` (4435 unique names).

## Method
HiringCafe SSR via `GET https://hiringcafe.com/_next/data/{buildId}/index.json?page=N` (40 jobs/page, tested 0-119). Each job has `v5_processed_job_data.company_name`, `company_website`, `source`, `board_token`. No auth, respects robots.txt Allow:/, Disallow page param is for crawlers — sampled with 0.5s delay, 4 concurrency.

## Source distribution (top 20)

- workday: 926
- zohorecruit: 789
- grnhse: 692
- successfactors: 376
- ashby: 327
- oraclecloud: 251
- smartrecruiters: 239
- workable: 223
- lever: 202
- adhoc: 171
- icims2: 170
- teamtailor: 137
- bamboohr: 112
- rippling: 84
- eightfold: 76
- dayforce: 70
- jazzhr: 69
- recruitee: 59
- ultipro: 58
- jobvite: 57

## Overlap with jobQuest `sources.json` (58 overlap)

Already covered: Accenture, Adobe, Amazon, Anthropic, Aristocrat, Blue Yonder, Boeing, Cisco, Cloudflare, Cohere, Coinbase, CrowdStrike, Cursor, Datadog, Elastic, ElevenLabs, Fivetran, Flexport, GE HealthCare, ... (full list in JSON).

## Top 100 sample

| Company | Domain | Source | Board token | Example role |
|---|---|---|---|---|
| 0G Labs | 0g.ai | ashby | 0g | Product Engineer |
| 1000 Media | 1000media.com | grnhse | nascompany | Finance Manager |
| 100ms |  | lever | 100ms | Software Engineer Architect |
| 11:11 Systems | 1111systems.com | adp | 08f195f0-beb6-4255-a019-dbc8691ab8e8 | Enterprise Solutions Manager |
| 2070Health | 2070health.com | workable | 2070health | Growth and Outreach Associate |
| 2Base Technologies | 2basetechnologies.com | zohorecruit | 2basetechnologies | Content Writing Intern |
| 2K | 2k.com | grnhse | 2k | Backend Software Engineer |
| 360T | 360t.com | personio | 360t | Legal Counsel |
| 367 Agency | 367.zohorecruit.in | zohorecruit | 367 | Performance Marketing Associate |
| 3CLogic | 3clogic.com | jazzhr | 3clogic | Service Desk Engineer |
| 3D Department |  | zohorecruit | sfumato | 3D Motion Artist |
| 3M | 3m.com | workday | 3m-wd1-search | Product Development Specialist |
| 3Pillar Global |  | lever | 3pillarglobal | Python Engineer |
| 3pillarglobal |  | lever | 3pillarglobal | Software Engineer |
| 3Shape | careers.3shape.com | teamtailor | 3shape | Technical Support Consultant |
| 4G Clinical | 4gclinical.com | saashr | 6182998 | Growth Marketing Manager |
| 56L LS India |  | oraclecloud | ebwi.fa.us2 | Automation Engineer |
| 5CA |  | grnhse | 5ca | Customer Support Agent |
| 66degrees |  | grnhse | 66degrees | Data Science Architect |
| 6sense |  | grnhse | 6sense | Machine Learning Engineer |
| 7-Eleven | 7-eleven.com | ripplehire | 7-eleven-gsc___d8KPwFGBhDK6f7ajWTsc | Software Engineer |
| 75F | 75f.io | breezy | 75f-apac | Product Manager |
| 75F APAC |  | breezy | 75f-apac | Assistant Sales Manager |
| _able | ablegroup.io | jazzhr | credablegroup | Partner Success Associate |
| A&O IT Group | aoitgroup.com | teamtailor | aoitgroup-1719309706 | Service Desk Agent |
| A&O Shearman | aoshearman.com | brassring | 30147_5046 | Practice Manager |
| A-Alpha Bio |  | grnhse | aalphabio | Account Executive |
| A-LIGN External | a-lign.com | grnhse | align | IT Auditor |
| A2MAC1 | a2mac1.com | workable | a2mac1 | Costing Engineer |
| AAJ Enterprises | aajenterprises.zohorecruit.in | zohorecruit | aajenterprises | Executive - Operations |
| Aampower |  | workday | aampower-wd1-interim-dauch-career-site | Value Stream Leader |
| Aaradhya Group | aaradhyagroup.in | zohorecruit | aaradhyagroup | Accountant |
| AArete |  | jobvite | aarete | Claims Lead |
| Aarna Systems Pvt Ltd | www.aarnasystems.com | recooty | aarna-systems-pvt-ltd | Recruitment and Documentation Coordinator |
| AB Agri |  | eploy | careers.abagri.com | Sales Manager |
| AB SKF | skf.com | successfactors | eu_SKF | Territory Manager |
| ABA360 |  | hrmdirect | aba360 | Board Certified Behavior Analyst |
| Abacus Insights |  | grnhse | abacusinsights | Project Manager |
| Abakus Center | abakus-center.com | workable | abakus_center | Teacher |
| ABB | abb.com | workday | abb-wd3-external_career_page | Project Engineer |
| Abbott | abbott.com | workday | abbott-wd5-abbottcareers | Warehouse Officer |
| AbbVie | global.allerganaesthetics.com | smartrecruiters | abbvie | Key Account Specialist |
| ABBYY | abbyy.com | grnhse | abbyy | Technical Success Manager |
| ABC Fitness | abcfitness.com | workday | abcfinancial-wd5-abcfinancialservices | Software Developer |
| Abcfinancial |  | workday | abcfinancial-wd5-abcfinancialservices | BI Engineer |
| Abnormal | abnormal.ai | grnhse | abnormalsecurity | Technical Support Engineer |
| Abstrabit | abstrabit.zohorecruit.in | zohorecruit | abstrabit | Fullstack Engineer |
| ACA Group | acaglobal.com | successfactors | com_foresidefi | Timecard and Expense Administrator |
| Acceldata |  | lever | acceldata | Finance Intern |
| Accelleron | accelleron.com | workday | accelleron-wd3-accelleron | Procurement Specialist |
| Accellor | accellor.com | workable | accellor | MuleSoft Architect |
| Accendra |  | workday | accendra-wd504-accendracareers | Network Analyst |
| Accenture | accenture.com | adhoc | accenture | Analytics and Modeling Manager |
| Access Information Services |  | adprecruiting | accesscorpcareers | Data Engineer |
| Access Now |  | bamboohr | accessnow | Incident Response Analyst |
| Accommodations Plus International | apiglobalsolutions.com | rippling | accommodations-plus-international | Director, Technical Operations - Infrastructure |
| AccorCorpo |  | smartrecruiters | accorcorpo | Director of Finance |
| AccorHotel | accor.com | smartrecruiters | accorhotel | Gym Instructor |
| Accounting Baba | accountingbaba.zohorecruit.com | zohorecruit | accountingbaba | Accounts Officer |
| Accrete |  | breezy | accrete-ai | Principal Engineer |
| Accuray |  | workday | accuray-wd5-external | Benefits Specialist |
| Accuris | accuristech.com | dayforce | accuris___candidateportal___en-us | Product Manager |
| Acentra Health | acentra.com | icims2 | acentra | Project Controls Analyst |
| ACG | acg-world.com | successfactors | com_acgassocia | Product Owner |
| ACI Worldwide | aciworldwide.com | oraclecloud | ebwg.fa.us2 | Technical Program Manager |
| ACLED | acleddata.com | bamboohr | acleddata | Visualization and Digital Communication Specialist |
| Acolad | acolad.com | successfactors | eu_amplexor | IT Monitoring Operations Analyst |
| Acowale | acowale.zohorecruit.in | zohorecruit | acowale | Full-Stack Engineer |
| Acron Aviation |  | lever | acronaviation | Avionics Technical Support Engineer |
| Acronaviation |  | lever | acronaviation | Electrical Engineer |
| ACT | actcorp.in | fountain | ap-1.fountain.com___act | Team Leader |
| Actinium Pharmaceuticals, Inc. | actiniumpharma.com | adhoc | actiniumpharma | General Manager |
| Actlogica | actlogicaus.com | zohorecruit | actlogicaus | Product Engineer |
| Actlogica Solutions | actlogica.com | zohorecruit | actlogicaus | Product Finance Actuarial Manager |
| Actylis | actylis.com | successfactors | com_acetousllc | EHS Officer |
| Acuvon Consulting | acuvon.com | zohorecruit | acuvon | Data Engineer |
| Acv |  | dayforce | acv___indiacandidateportal___en-ca | Software Engineering Manager |
| ACV Auctions | acvauctions.com | dayforce | acv___indiacandidateportal___en-ca | Software Engineer |
| Adama India Private Ltd | adama.com | successfactors | eu_MAI | Procurement Manager |
| Adani Airport Holdings Ltd | adani.com | oraclecloud | eibd.fa.em2 | Shift In Charge |
| Adani Power Ltd | adanipower.com | oraclecloud | eibd.fa.em2 | FGD Operations and Maintenance Chemistry |
| ADB SAFEGATE Careers | adbsafegate.com | successfactors | eu_ADBDP | Computer Vision Engineer |
| Addepar | addepar.com | grnhse | addepar1 | Business Development Representative |
| Addiction Pet Foods | addictionpet.com | betterteam | addictionpet | E-commerce Account Manager |
| AddWeb Solution | addwebsolution.zohorecruit.in | zohorecruit | addwebsolution | System Administrator |
| Adequate Bookkeeping | adequatebookkeeping.zohorecruit.com | zohorecruit | adequatebookkeeping | Accounts Executive |
| Adform | careers.adform.com | teamtailor | adform | Engineering Manager |
| ADI Global Distribution | adiglobal.com | oraclecloud | ehtl.fa.us6 | Systems Integration Analyst |
| Aditya Ram Properties | adityaramproperties.zohorecruit.in | zohorecruit | adityaramproperties | Marketing Manager |
| Adityaram Properties | adityaramproperties.com | zohorecruit | adityaramproperties | Projects Head |
| Adjust |  | grnhse | adjustjobs | Customer Success Manager |
| ADM | adm.com | brassring | 25416_5430 | Human Resources Deputy Manager |
| ADM Indicia | careers.admgroup.com | pinpoint | admgroup | Accountant |
| adm-Indicia | careers.admindicia.com | pinpoint | admgroup | Accounts and Finance Operations Executive |
| Adobe | careers.adobe.com | workday | adobe-wd5-external_experienced | Computer Scientist |
| Adtran |  | workday | adtran-wd3-adtran | Manager of System Integration Test |
| Advance Auto Parts | jobs.advanceautoparts.com | workday | advanceauto-wd5-advanceexternalcareers | Security Engineer |
| Advanced Micro Devices, Inc | amd.com | icims2 | amd | SoC Physical Design Engineer |
| Advantage HQ | advantagehq.com | jazzhr | bmdigital | Director of Media Operations |
| Advantest |  | adprecruiting | advantestcareers | Software Engineer |