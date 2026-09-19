# HiringCafe — Yet To Add

Generated: 2026-09-08

Source data: `backend/data/hiringcafe_companies_deduped.json` (4435 unique companies sampled from HiringCafe).
Compared against: `backend/sources.json` (964 sources). Match key: normalized `company_name` (case-insensitive, trimmed).

**Overlap (already added): 892** | **Remaining (yet to add): 3543**

## Summary by adapter

| # | Adapter (`ats_type`) | HiringCafe `source` value(s) | Remaining | Status |
|---|----------------------|-------------------------------|-----------|--------|
| 1 | `greenhouse` | `grnhse` | 6 | ✅ ready — `board_token` is the board id |
| 2 | `lever` | `lever`, `eu_lever` | 21 | ✅ ready — `board_token` is the board id |
| 3 | `ashby` | `ashby` | 18 | ✅ ready — `board_token` is the board id |
| 4 | `workday` | `workday` | 639 | ⚠️ adapter exists — needs full URL probe |
| 5 | `successfactors` | `successfactors` | 349 | ⚠️ adapter exists — needs full URL probe |
| 6 | `oracle` | `oraclecloud`, `oraclepeoplesoft`, `taleo_careersection`, `taleo_rss`, `taleo_selectminds` | 235 | ⚠️ adapter exists — needs full URL probe |
| 7 | `icims` | `icims`, `icims2` | 135 | ⚠️ adapter exists — needs full URL probe |
| 8 | `avature` | `avature` | 36 | ⚠️ adapter exists — needs full URL probe |
| 9 | `phenom` | `phenompeople` | 11 | ⚠️ adapter exists — needs full URL probe |
| 10 | *(no adapter yet)* | 71 other `source` values (see below) | 2093 | ❌ needs new adapter per `AGENTS.md` §5 |

Ready now: **45** (greenhouse/lever/ashby). Needs URL work: **1405** (workday/successfactors/oracle/icims/avature/phenom). No adapter: **2093**.

> Note: `board_token` below is the raw HiringCafe token. For READY adapters it maps 1:1 to `board_identifier` in `sources.json` (e.g. `grnhse` token `2k` → greenhouse `2k`). For NEEDS-URL adapters the token is NOT a usable URL — it must be resolved to a full careers URL and probed (see `docs/hiringcafe-expansion-plan.md` §3 Phase 3) before adding.

---

## A. Ready now — adapter exists, token directly usable (45)

### Greenhouse — ready (direct board token) — 6 companies

`ats_type="greenhouse"` ← HiringCafe `source` in `grnhse`. Add as `{"company_name": "<Name>", "ats_type": "greenhouse", "board_identifier": "<board_token>"}`.

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Careers at Tide |  | `grnhse` | `tide` | Analyst |
| Global Career Website |  | `grnhse` | `astoundcommerce` | QA Engineer |
| SingleStore-LinkedIn |  | `grnhse` | `singlestore-linkedin` | Revenue Operations Analyst |
| Skillz |  | `grnhse` | `firy` | Product Marketing Manager |
| SpaceX_Global |  | `grnhse` | `spacexglobal` | Supplier Development Engineer |
| Study.com C |  | `grnhse` | `studycontractors` | TOEFL Assessment Consultant |

### Lever — ready (direct board token) — 21 companies

`ats_type="lever"` ← HiringCafe `source` in `lever`, `eu_lever`. Add as `{"company_name": "<Name>", "ats_type": "lever", "board_identifier": "<board_token>"}`.

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| 3pillarglobal |  | `lever` | `3pillarglobal` | Software Engineer |
| Acronaviation |  | `lever` | `acronaviation` | Electrical Engineer |
| Aleph Group | alephdigital.com | `lever` | `aleph` | Client Partner |
| Ampd-energy |  | `lever` | `ampd-energy` | Engineer - Platform & Data Infrastructure |
| Asapp-2 |  | `lever` | `asapp-2` | Product Manager |
| Bpmcpa |  | `lever` | `bpmcpa` | Corporate Tax |
| e.l.f. Beauty | elfbeauty.com | `lever` | `elfbeauty` | SAP Master Data Specialist |
| Endpoint Clinical |  | `lever` | `endpointclinical` | Business Development |
| Extreme Networks | extremenetworks.com | `lever` | `extremenetworks` | Salesforce Programmer |
| Galepartners |  | `lever` | `galepartners` | Quality Assurance Manager |
| KingfishGroup |  | `lever` | `KingfishGroup` | Research Delivery |
| Model N | modeln.com | `lever` | `modeln` | Education Services Consultant |
| Parallel Wireless |  | `lever` | `parallelwireless` | Automation Intern |
| Paytm Payment Services Limited | paytmpayments.com | `lever` | `paytmpayments` | Team Leader |
| PDI Technologies | pdi.com | `lever` | `pditechnologies` | Software Engineer |
| Spin.AI | spin.ai | `lever` | `spinai` | Marketing Manager |
| Stable-money1 |  | `lever` | `stable-money1` | User Acquisition and Growth |
| TTEC Digital |  | `lever` | `ttecdigital` | Reporting Analyst |
| Upscale-ai |  | `lever` | `upscale-ai` | Engineer |
| Warner Music Group | wmg.com | `lever` | `wmg` | Forward Deployed Engineer |
| Z1tech |  | `lever` | `z1tech` | Account Executive |

### Ashby — ready (direct board token) — 18 companies

`ats_type="ashby"` ← HiringCafe `source` in `ashby`. Add as `{"company_name": "<Name>", "ats_type": "ashby", "board_identifier": "<board_token>"}`.

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Amperos Health |  | `ashby` | `amperos` | Quality Assurance Specialist |
| Better Mortgage | better.com | `ashby` | `better-mortgage` | Marketing Operations & AI Automation Coordinator |
| Bolna.ai | bolna.ai | `ashby` | `bolna` | HR Intern |
| Gen Digital Inc. | gendigital.com | `ashby` | `gen-digital` | Software Engineer - iOS |
| Glomopay |  | `ashby` | `glomo` | Mobile Engineer |
| Gradera Inc. | gradera.ai | `ashby` | `gradera` | Data Engineer |
| Joist AI |  | `ashby` | `kantiv` | Product Marketing Manager |
| Libra AI, Inc |  | `ashby` | `libra` | Product Manager |
| Meraki Labs | merakilabs.com | `ashby` | `meraki-labs` | Computational Fusion Scientist / Engineer |
| Netspend Corporation |  | `ashby` | `netspend-careers-page` | Director Observability Response & Reliability |
| Noon (via Ashby) |  | `ashby` | `noon-design` | Backend Architect |
| Noon Design |  | `ashby` | `noon-design` | Fullstack Frontend Architect |
| Pravāh | pravah.com | `ashby` | `pravah` | Weather Data Scientist |
| Skylo Technologies | skylo.tech | `ashby` | `skylo` | Cloud Architect |
| Terra Localizations | terra-translations.com | `ashby` | `terra` | Video Game Localizer |
| Valerie Group | valeriegroup.com | `ashby` | `valerie-group` | Design Director |
| ZURU Edge | zuruedge.com | `ashby` | `zuru` | Influencer Research Executive |
| ZURU Tech | www.zurutech.com | `ashby` | `zuru` | IT Executive |

## B. Adapter exists but needs URL reconstruction / probing (1405)

### Workday — adapter exists, needs URL reconstruction — 639 companies

`ats_type="workday"` ← HiringCafe `source` in `workday`. Do NOT add `board_token` directly — resolve to full careers URL first (see expansion plan Phase 3).

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Abcfinancial |  | `workday` | `abcfinancial-wd5-abcfinancialservices` | BI Engineer |
| Airliquidehr | www.airliquide.com | `workday` | `airliquidehr-wd3-airliquideexternalcareer` | Engineer - Electrical |
| Alexion Pharmaceuticals | alexion.com | `workday` | `astrazeneca-wd3-alexion` | Business Coordinator |
| Allegromicro | www.allegromicro.com | `workday` | `allegromicro-wd5-allegrocareers` | Channel Partner Manager |
| Allstate India | allstateindia.com | `workday` | `allstate-wd5-allstate_careers` | Customer Service Team Lead |
| ALS | alsglobal.com | `workday` | `alsglobal-wd103-external` | IT Support Executive |
| Alsglobal | www.alsglobal.com | `workday` | `alsglobal-wd103-external` | Microbiologist |
| Altera | altera.com | `workday` | `altera-wd1-altera` | Analog Circuit Design Engineer |
| Alteryx |  | `workday` | `alteryx-wd108-alteryxcareers` | Customer Success Manager |
| Alvotech |  | `workday` | `alvotech-wd103-alvotech_careers` | Director, Statistical Programming |
| Amadeus | jobs.amadeus.com | `workday` | `amadeus-wd502-jobs` | Software Development Engineer |
| Aman |  | `workday` | `aman-wd103-amangroupexternal` | Food and Beverage Manager |
| American Express Global Business Travel | amexglobalbusinesstravel.com | `workday` | `travelhrportal-wd1-jobs` | ETL Developer |
| Ameriprise |  | `workday` | `ameriprise-wd5-ameriprise` | Cisco Contact Center Manager |
| Ameriprise Financial, Inc. | ameriprise.com | `workday` | `ameriprise-wd5-ameriprise` | Financial Advisory Support Analyst |
| Amgen | amgen.com | `workday` | `amgen-wd1-careers` | Software Engineer |
| Amherst Group | www.amherst.com | `workday` | `amherstgroup-wd1-amherst_holdings_careers` | Portfolio Management Analyst |
| AML RightSource |  | `workday` | `amlrightsource-wd1-amlrightsource` | AML Trainer |
| Amlrightsource |  | `workday` | `amlrightsource-wd1-amlrightsource` | AML Trainer |
| Analog Devices | www.analog.com | `workday` | `analogdevices-wd1-external` | Analyst |
| Apex Group | apexgroup.com | `workday` | `theapexgroup-wd3-apexgroupcareers` | Process Associate |
| Appliedis | www.ais.com | `workday` | `appliedis-wd5-ais_careers_india` | Business Analyst |
| ApplyBoard | www.applyboard.com | `workday` | `applyboard-wd3-applyboardnh` | Slate Administrator |
| Aptiv | aptiv.com | `workday` | `aptiv-wd5-aptiv_careers` | Design Engineer |
| Arabelle Solutions | arabelle-solutions.com | `workday` | `arabellesolutions-wd3-arabelle_solutions` | Systems Engineering Arrangement and Piping Engineer |
| Arctic Wolf | arcticwolf.com | `workday` | `arcticwolf-wd1-external` | Developer |
| Ares Management Corporation | aresmgmt.com | `workday` | `aresmgmt-wd1-external` | Data Architect |
| Areteir |  | `workday` | `areteir-wd1-arete-careers` | Forensic Analyst |
| Armacell | www.armacell.com | `workday` | `armacell-wd3-career-armacell` | Shift Leader |
| Armanino India LLP | armaninollp.com | `workday` | `armaninollp-wd1-armanino_india` | Procurement Analyst |
| Arrow |  | `workday` | `arrow-wd1-ec` | Lab Technician |
| Ascend Performance Materials |  | `workday` | `ascendperformancematerials-wd1-ascend` | Simulation Engineer |
| Ascensus | careers.ascensus.com | `workday` | `ascensushr-wd1-ascensuscareers` | Financial Analyst |
| AspenTech |  | `workday` | `aspentech-wd5-aspentech` | Solution Consultant |
| Assurant | assurant.com | `workday` | `assurant-wd1-assurant_careers` | Payroll Manager |
| Astreya |  | `workday` | `astreya-wd5-life-at-astreya-opportunities` | M365 Engineer |
| athenahealth | athenahealth.com | `workday` | `athenahealth-wd1-external` | Billing Operations Analyst |
| AtkinsRéalis | atkinsrealis.com | `workday` | `slihrms-wd3-careers` | Mechanical Engineer |
| Autodesk | autodesk.com | `workday` | `autodesk-wd1-ext` | Implementation Consultant |
| Automation Anywhere | automationanywhere.com | `workday` | `automationanywhere-wd5-automationanywherejobs` | Technical Support Manager |
| Availity |  | `workday` | `availity-wd1-availity_careers_india` | Client Services Support Specialist |
| Avantor | careers.avantorsciences.com | `workday` | `vwr-wd1-avantorjobs` | Solution Architect |
| Aveva | www.rib-software.com | `workday` | `aveva-wd3-rib_careers` | Product Designer |
| Aviagen | aviagencareers.com | `workday` | `aviagen-wd1-aviagen-careers` | Creche Teacher |
| Aviareps | www.aviareps.com | `workday` | `aviareps-wd103-aviareps_careers` | Finance Officer |
| Avid | avid.com | `workday` | `avid-wd5-avid` | Salesforce Platform Engineer |
| Avnet | www.avnet.com | `workday` | `avnet-wd1-external` | Middleware Developer |
| Axis | www.axis.com | `workday` | `axis-wd3-external_career_site` | HR Manager |
| Ayvens |  | `workday` | `ayvens-wd3-sg-ayvens` | Sales Support Officer |
| Azelis |  | `workday` | `azelis-wd3-azelis_careers` | Process Lead |
| Baker Hughes | bakerhughes.com | `workday` | `bakerhughes-wd5-bakerhughes` | Geophysicist |
| Baker Tilly | bakertilly.com | `workday` | `bakertilly-wd5-btcareers` | Associate |
| Bank of America | about.bankofamerica.com | `workday` | `ghr-wd1-lateral-apac` | Service Delivery Analyst |
| Barclays | home.barclays | `workday` | `barclays-wd3-external_career_site_barclays` | Full Stack Engineer |
| Barry-Wehmiller | barrywehmiller.com | `workday` | `barrywehmiller-wd1-bwcareers` | Controls Engineer |
| Bdx |  | `workday` | `bdx-wd1-external_career_site_singapore` | IT Business Partner - Logistics & Distribution |
| Bf |  | `workday` | `bf-wd5-international` | Territory Manager |
| Bill Gosling Outsourcing | billgosling.com | `workday` | `billgosling-wd5-global` | Customer Service Representative |
| Biogen | biogen.com | `workday` | `biibhr-wd3-external` | Techno-Functional Analyst |
| Blackbaud | www.blackbaud.com | `workday` | `blackbaud-wd1-externalcareers` | Security Engineer |
| BlackLine | blackline.com | `workday` | `blackline-wd108-blacklinecareers` | Engineering Manager |
| BlackRock | blackrock.com | `workday` | `blackrock-wd1-blackrock_professional` | RFP Specialist |
| Blackstone |  | `workday` | `blackstone-wd1-x_ghostsite_aurion` | Vice President Reporting and Filings |
| Bloom Energy | bloomenergy.com | `workday` | `bloomenergy-wd1-bloomenergycareers` | Test Engineer |
| Bloomenergy | www.bloomenergy.com | `workday` | `bloomenergy-wd1-bloomenergycareers` | Engineer - Mechanical Design |
| Bluehost | bluehost.com | `workday` | `web-wd1-externalcareersite` | Technical Support Engineer |
| Boydcorp | boydcorp.com | `workday` | `boydcorp-wd12-boyd_careers` | Procurement and Supply Chain Executive |
| BP | bp.com | `workday` | `bpinternational-wd3-bpcareers` | Accounts Receivable Analyst |
| Brenntag | corporate.brenntag.com | `workday` | `brenntag-wd3-brenntag_jobs` | Innovation and Application Technical Manager |
| Brightstone | brightstone.co.in | `workday` | `jll-wd1-brightstonecareers` | Customer Relations Executive |
| British Columbia Investment Management Corporation | bci.ca | `workday` | `bci-wd10-bci_careers` | Analyst |
| Broadridge | www.broadridge.com | `workday` | `broadridge-wd5-careers` | Technology Delivery Manager |
| Brookfield | www.brookfield.com | `workday` | `brookfield-wd5-brookfield` | Financial Analyst |
| BSI |  | `workday` | `bsigroup-wd3-bsi_careers` | Workday Functional Consultant |
| BSI Group |  | `workday` | `bsigroup-wd3-bsi_careers` | Certification Manager |
| Bydeluxe |  | `workday` | `bydeluxe-wd5-deluxe_external` | Team Lead |
| C.H. Robinson | chrobinson.com | `workday` | `chrobinson-wd5-chrobinson` | Deputy Manager |
| CAI | careers.cai.io | `workday` | `cai-wd5-computer_aid` | AI Data Product Owner |
| Calix | calix.com | `workday` | `calix-wd1-externalinternational` | Staff Engineer Solution Test |
| Calyx | www.perceptive.com | `workday` | `calyx-wd1-perceptive` | Software Quality and Test Manager |
| CANPACK Group | canpack.com | `workday` | `giorgiglobal-wd3-canpack` | SAP Project Manager |
| Cardinal Health |  | `workday` | `cardinalhealth-wd1-ext` | Cloud Platforms Engineer |
| Carrier | jobs.carrier.com | `workday` | `carrier-wd5-jobs` | Service Sales |
| Caterpillar Inc. |  | `workday` | `cat-wd5-solarturbines` | Field Service Representative |
| Cencora | cencora.com | `workday` | `myhrabc-wd5-global` | Customer Experience Coordinator |
| Cengage | www.cengagegroup.com | `workday` | `cengage-wd5-cengageindiacareers` | Media Designer |
| Centific |  | `workday` | `centific-wd1-centific_ecs_sea` | Automation Engineer |
| Centricsoftware | www.centricsoftware.com | `workday` | `centricsoftware-wd501-centric` | Sales Manager |
| Cgm | www.cgm.com | `workday` | `cgm-wd3-cgm` | Quality Assurance Automation Engineer |
| Chatham Financial | chathamfinancial.com | `workday` | `chathamfinancial-wd501-chathamfinancial` | IT Operations Administrator |
| Chegg | chegg.com | `workday` | `osv_chegg-wd5-chegg` | Software Engineer |
| Chevron | chevron.com | `workday` | `chevron-wd5-jobs` | M365 Design Engineer |
| Chubb Fire & Security | chubbfs.com | `workday` | `chubbfiresecurity-wd3-chubbfs` | Integration Engineer |
| Ciena |  | `workday` | `ciena-wd5-careers` | Java Developer |
| CIP Fund Solutions | cip.com | `workday` | `cip-wd103-cipfs_careers` | IT Service Desk Supporter |
| Circle | circle.com | `workday` | `circle-wd1-circle` | Product Manager |
| Circle K |  | `workday` | `circlek-wd3-circlekstorejobs` | Chargeback Specialist |
| Circlek |  | `workday` | `circlek-wd3-circlekstorejobs` | Logistics Data Analyst |
| Citi | jobs.citi.com | `workday` | `citi-wd5-2` | ITRS Monitoring and Observability Specialist |
| CITIC CLSA |  | `workday` | `citicclsa-wd3-external` | Securities Settlement Manager |
| Citicclsa | clsa.com | `workday` | `citicclsa-wd3-external` | Associate Director, Middle Office |
| Clario | clario.com | `workday` | `clarioclinical-wd1-clarioclinical_careers` | Medical Writer |
| Clarioclinical |  | `workday` | `clarioclinical-wd1-clarioclinical_careers` | Data Manager |
| Clarivate | clarivate.com | `workday` | `clarivate-wd3-jobs` | Software Engineer |
| Clearwater Analytics | clearwateranalytics.com | `workday` | `clearwateranalytics-wd1-clearwater_analytics_careers` | Salesforce Developer |
| Clio | clio.com | `workday` | `clio-wd3-cliocareersite` | Payroll Specialist |
| CME Group | cmegroup.com | `workday` | `cmegroup-wd1-cme_careers` | Platform Engineer |
| Cmegroup | www.cmegroup.com | `workday` | `cmegroup-wd1-cme_careers` | Post-Trade Services & Risk Associate |
| Coke | careers.coca-colacompany.com | `workday` | `coke-wd1-coca-cola-careers` | Production Operator |
| Collins Aerospace | collinsaerospace.com | `workday` | `globalhr-wd5-rec_rtx_ext_gateway` | Engineer |
| Collinson Group | collinsongroup.com | `workday` | `collinsongroup-wd103-the_collinson_group_external` | Actuarial Analyst |
| Collinsongroup |  | `workday` | `collinsongroup-wd103-the_collinson_group_external` | Software Engineer |
| Columbia Sportswear Company | columbia.com | `workday` | `columbiasportswearcompany-wd5-columbia_career_site` | Material Quality Engineer |
| Columbiasportswearcompany |  | `workday` | `columbiasportswearcompany-wd5-columbia_career_site` | Lease Portfolio Analyst |
| Comcast |  | `workday` | `comcast-wd115-comcast_careers` | Machine Learning Engineer |
| Commercial Vehicle Group |  | `workday` | `cvgrp-wd5-cvg` | Production Manager |
| Communitybrands | momentivesoftware.com | `workday` | `communitybrands-wd1-momentive_external_careers` | Payroll Analyst |
| Conde Nast |  | `workday` | `condenast-wd115-condecareers` | Software Engineer |
| Condenast | condenast.com | `workday` | `condenast-wd115-condecareers` | Order-to-Cash Manager |
| Confluentmedical |  | `workday` | `confluentmedical-wd503-confluent_medical` | Customer Solutions Specialist |
| Consertus | www.consertus.com | `workday` | `consertus-wd501-consertuscareers` | Industrial Electrician |
| Convatec | convatecgroup.com | `workday` | `convatec-wd1-convatec` | Data Governance Analyst |
| Cooper Standard |  | `workday` | `cooperstandard-wd1-cooperstandard` | System Developer |
| Copart | www.copart.com | `workday` | `copart-wd12-copart` | Network Engineer |
| Coperion | coperion.com | `workday` | `hillenbrand-wd3-global` | Apprentice |
| Corrohealth |  | `workday` | `corrohealth-wd1-corrohealthindia` | Trainer |
| Cotality | cotality.com | `workday` | `cotality-wd115-global` | Data Consulting Analyst |
| Criteo | careers.criteo.com | `workday` | `criteo-wd3-criteo_career_site` | Ad Operations Trafficking Specialist |
| Crowe | careers.crowe.com | `workday` | `crowe-wd12-external_careers` | DevOps Engineering Manager |
| CSA Group | csagroup.org | `workday` | `csagroup-wd3-csagroup` | Technical Lead |
| Csagroup | www.csagroup.org | `workday` | `csagroup-wd3-csagroup` | Field Evaluation Representative |
| CSG | csgi.com | `workday` | `csgi-wd5-csgcareers` | Java Software Development Engineer |
| Cubic | www.cubic.com | `workday` | `cubic-wd1-cubic_global_careers` | Financial Services Analyst |
| Curriculumassociates |  | `workday` | `curriculumassociates-wd5-external` | Tax Manager |
| Curtiss Wright | curtisswright.com | `workday` | `curtisswright-wd1-cw_external_career_site` | Sales Engineer |
| Curtiss-Wright | curtiss-wright.com | `workday` | `curtisswright-wd1-cw_external_career_site` | Supplier Quality Engineer |
| Curtisswright | httpswww.curtisswright.com | `workday` | `curtisswright-wd1-cw_external_career_site` | Assistant Manager Design & Engineering |
| Cushman & Wakefield | cushmanwakefield.com | `workday` | `cw-wd1-external` | Transport Executive |
| Cytiva | cytiva.com | `workday` | `danaher-wd1-danaherjobs` | Account Manager |
| Danaher | danaher.com | `workday` | `danaher-wd1-danaherjobs` | AI Engineer |
| DBS Bank India Limited | www.dbs.com | `workday` | `dbs-wd3-dbs_careers` | Client Service Manager |
| Deluxe | bydeluxe.com | `workday` | `bydeluxe-wd5-deluxe_external` | Quality Control Specialist |
| Demegroup |  | `workday` | `demegroup-wd3-careers_external` | Middleware Developer |
| Diageo | diageo.com | `workday` | `diageo-wd3-diageo_careers` | Customer Marketing Assistant Manager |
| Diconium | embitel.com | `workday` | `diconium-wd3-embitel_technologies` | Control Software Engineer |
| Disney | www.disneycareers.com | `workday` | `disney-wd5-disneycareer` | Platform Engineer |
| Djeholdings | www.edelman.com | `workday` | `djeholdings-wd5-edelman-careers-e200` | Creative Director |
| Donaldson | donaldson.com | `workday` | `donaldson-wd115-donaldsoncareers` | Financial Analysis Manager |
| Dowjones |  | `workday` | `dowjones-wd1-news_corp_careers` | Analyst, Indirect Sourcing Generalist |
| DP Architects | dpa.com.sg | `workday` | `dpgroup-wd102-careers_dp` | Systems Administrator |
| DS Smith |  | `workday` | `dssmith-wd3-careers` | Account Manager |
| Dssmith |  | `workday` | `dssmith-wd3-careers` | Commercial Pricing Analyst |
| DuPont |  | `workday` | `dupont-wd5-jobs` | Dispute Analyst |
| DWS | db.com | `workday` | `db-wd3-dwswebsite` | Business Management Specialist |
| DWS Group | dws.com | `workday` | `db-wd3-dwswebsite` | Know Your Client Analyst |
| DXC Technology |  | `workday` | `dxctechnology-wd1-dxcjobs` | Software Engineer |
| Dynata |  | `workday` | `dynata-wd108-careers` | Accounts Payable Coordinator |
| Dyson | careers.dyson.com | `workday` | `dyson-wd3-dyson_careers` | Cloud and Enterprise Infrastructure Specialist |
| eBay | careers.ebayinc.com | `workday` | `ebay-wd5-apply` | Machine Learning Engineer |
| Edwards |  | `workday` | `edwards-wd5-edwardscareers` | Territory Manager |
| Edwards Lifesciences |  | `workday` | `edwards-wd5-edwardscareers` | Data Service Excellence Specialist |
| eInfochips | einfochips.com | `workday` | `arrow-wd1-ec` | Java Engineer |
| Electrolux | career.electroluxgroup.com | `workday` | `electrolux-wd3-electroluxcareersite` | Data Engineer |
| Elemica |  | `workday` | `elemica-wd501-elemica_careers` | Salesforce Administrator |
| Eli Lilly and Company | lilly.com | `workday` | `lilly-wd115-lly` | Agentic Engineer |
| Empower | empower.com | `workday` | `empower-wd12-empower` | Investment Setup Specialist |
| Endo |  | `workday` | `endo-wd1-external` | Research Associate |
| Enovis | enovis.com | `workday` | `enovis-wd5-enovis` | Process Executive |
| Enovix | enovix.com | `workday` | `enovix-wd12-external` | Internal Audit and Risk Management Manager |
| Entrust | entrust.com | `workday` | `entrust-wd1-entrustcareers` | Customer Support Engineer |
| Envista | envistaco.com | `workday` | `envista-wd1-envistacareers` | Marketing Manager |
| Eppendorf | corporate.eppendorf.com | `workday` | `eppendorf-wd502-eppendorf` | Director Channel Sales |
| Equifax | careers.equifax.com | `workday` | `equifax-wd5-external` | Operations Manager |
| Equiniti |  | `workday` | `equiniti-wd3-opportunities` | Service Desk Trainee |
| ERM | erm.com | `workday` | `erm-wd3-erm_careers` | Strategic Sourcer |
| Esab |  | `workday` | `esab-wd5-esabcareers` | Head of Commercial Excellence |
| Esko | esko.com | `workday` | `veralto-wd1-eskojobs` | Software Development Engineer in Test |
| Evolent |  | `workday` | `evolent-wd1-external` | Staff Accountant |
| Evonik | evonik.com | `workday` | `evonik-wd3-external_careers` | Security Supervisor |
| Evotecgroup | evotec.com | `workday` | `evotecgroup-wd3-evotec_career_site` | Business Development Director |
| Evs | evs-eng.com | `workday` | `evs-wd108-evsengineeringcareers` | Automation Engineer |
| Exclusive Networks | exclusive-networks.com | `workday` | `exclusivenetworks-wd103-exclusive-networks-career` | Solution Engineer |
| Exclusivenetworks | www.exclusive-networks.com | `workday` | `exclusivenetworks-wd103-exclusive-networks-career` | Operation Executive |
| Exos | www.teamexos.com | `workday` | `exos-wd501-exoscareers` | Zumba Instructor |
| Expedia Group | expediagroup.com | `workday` | `expedia-wd108-search` | Crisis Operations Manager |
| Experity | experityhealth.com | `workday` | `experity-wd108-experity_careers` | Machine Learning Engineer |
| FactSet | factset.com | `workday` | `factset-wd108-factsetcareers` | Client Solutions Advisor |
| Farnell | farnell.com | `workday` | `avnet-wd1-external` | Product Segment Leader |
| FC Global Services India LLP |  | `workday` | `svb-wd5-firstcitizensindia` | Analyst |
| FC Global Services India LLP (First Citizens India) |  | `workday` | `svb-wd5-firstcitizensindia` | Analyst - Hardware Asset Management |
| FedEx | enterprisecareers.fedex.com | `workday` | `fedex-wd1-ftn-apac_cross_opco` | Finance Apprentice |
| Ferring | ferring.com | `workday` | `ferring-wd3-ferring` | Key Account Manager |
| Fico | fico.com | `workday` | `fico-wd1-external` | AI/ML Engineer |
| Fidelity International | fidelityinternational.com | `workday` | `fil-wd3-001` | Technical Specialist |
| First Advantage | fadv.com | `workday` | `firstadvantage-wd5-firstadvantage` | Salesforce Data Engineer |
| First Citizens Bank | firstcitizens.com | `workday` | `svb-wd5-firstcitizensindia` | Data Engineer |
| Firstam | firstam.co.in | `workday` | `firstam-wd1-faicareers` | Software Engineer |
| FirstRand | firstrand.co.za | `workday` | `firstrand-wd3-frb` | Wealth Advisor |
| Fiserv | fiserv.com | `workday` | `fiserv-wd5-ext` | Associate, Disputes and Fraud Analysis |
| Flex | flex.com | `workday` | `flextronics-wd1-careers` | Procurement Analyst |
| Flexerasoftware | www.revenera.com | `workday` | `flexerasoftware-wd1-revenera` | Manager, Billing Operations |
| FLSmidth |  | `workday` | `flsmidth-wd3-fls_global` | Proposal and Order Execution Specialist |
| Flsmidthcement | fullertechnologies.com | `workday` | `flsmidthcement-wd103-fuller_global` | Process Optimization Specialist |
| Fluence Energy | fluenceenergy.com | `workday` | `fluenceenergy-wd12-fluenceenergy-jobs` | Product Owner |
| Flutter Entertainment | careers.fluttergroup.com | `workday` | `flutterbe-wd3-group_external` | AI Developer |
| FMC Corporation | jobs.fmc.com | `workday` | `fmc-wd12-fmc` | Territory Manager |
| Fmr | httpsclientjobs.fidelity.com | `workday` | `fmr-wd1-fidelitycareers` | Director |
| Forcepoint | www.forcepoint.com | `workday` | `forcepoint-wd1-external-careers` | Technical Support Engineer |
| Forrester | www.forrester.com | `workday` | `forrester-wd501-careers` | Portfolio Marketing Coordinator |
| Fortrea | fortrea.com | `workday` | `fortrea-wd1-fortrea` | Clinical Data Analyst |
| Fourseasons | careers.fourseasons.com | `workday` | `fourseasons-wd3-search` | Demi Chef de Partie |
| Fractal |  | `workday` | `fractal-wd1-careers` | Data Scientist |
| Fragomen | fragomen.com | `workday` | `fragomen-wd115-fragomencareers` | Business Immigration Analyst |
| Franklin Templeton | franklintempletoncareers.com | `workday` | `franklintempleton-wd5-invitation-only` | Client Relationship Specialist |
| Fresenius Medical Care | freseniusmedicalcare.com | `workday` | `freseniusmedicalcare-wd3-fme` | Master Data Governance & Migration Expert |
| Freseniusmedicalcare |  | `workday` | `freseniusmedicalcare-wd3-fme` | Dialysis Technician |
| Freudenberg Gala Household Product Pvt. Ltd. | freudenberg.com | `workday` | `freudenberg-wd3-freudenberg-group` | National Sales Manager |
| Fronius |  | `workday` | `fronius-wd3-job_board` | System Engineer |
| Galderma | galderma.com | `workday` | `galderma-wd3-external` | Territory Business Executive |
| Gartner | gartner.com | `workday` | `gartner-wd5-ext` | Test Engineer |
| GE Aerospace | careers.geaerospace.com | `workday` | `geaerospace-wd5-ge_externalsite` | HR Business Partner |
| GE Vernova | careers.gevernova.com | `workday` | `gevernova-wd5-vernova_externalsite` | Buying Procurement Specialist |
| GEA |  | `workday` | `gea-wd3-geacareers` | Validation and Testing Engineer |
| Generac | careers.generac.com | `workday` | `generac-wd5-externalcareers` | Engineering Manager |
| General Mills | generalmills.com | `workday` | `genmills-wd1-gmi_external_careers` | Business Activator |
| General Motors |  | `workday` | `generalmotors-wd5-careers_gm` | Manufacturing Engineer |
| Generalmotors |  | `workday` | `generalmotors-wd5-careers_gm` | Paint Simulation Engineer |
| Genesys | genesys.com | `workday` | `genesys-wd1-2_genesys_jobs` | Visual and Multimedia Designer |
| Georg Fischer | georgfischer.com | `workday` | `georgfischer-wd103-georgfischer_careers` | Project Execution |
| Gia |  | `workday` | `gia-wd1-giaservices` | Security Officer |
| Giant Eagle |  | `workday` | `gianteagle-wd503-gebexternalcareers` | Merchandising Data Operations Specialist |
| Gianteagle |  | `workday` | `gianteagle-wd503-gebexternalcareers` | Software Engineer |
| Giorgiglobal |  | `workday` | `giorgiglobal-wd3-canpack` | IT Support Specialist |
| Global Payments | jobs.globalpayments.com | `workday` | `tsys-wd1-tsys` | Information Security Analyst |
| GlobalFoundries | gf.com | `workday` | `globalfoundries-wd1-external` | SoC Design Engineer |
| GN |  | `workday` | `gn-wd3-resoundcareers` | Sales Manager |
| GN Group | resound.com | `workday` | `gn-wd3-resoundcareers` | Finance Executive |
| Goodyear |  | `workday` | `goodyear-wd1-goodyearcareers` | Product Management Manager |
| Google Operations Center | googleoperationscenter.com | `workday` | `google-wd501-gocjobs` | Technical Delivery Manager |
| GoTo | goto.com | `workday` | `goto-wd5-gotocareers` | Vulnerability Management and Incident Response Analyst |
| Grant Thornton UK |  | `workday` | `ukgrantt-wd3-careersgrantthornton` | Ethics and Independence Manager |
| Greif | greif.com | `workday` | `greif-wd5-greif` | Regulatory Compliance Manager |
| GSK | jobs.gsk.com | `workday` | `gsk-wd5-gskcareers` | Publications Lead |
| Gtt | www.gtt.net | `workday` | `gtt-wd3-external` | Vendor Coordinator |
| Guardant Health | httpsomationplaceholder.com | `workday` | `gh-wd1-gh` | Medical Lead |
| Guardian Life | guardianlife.com | `workday` | `guardianlife-wd5-guardian-life-careers` | MLOps Engineer |
| Guidewire Software | guidewire.com | `workday` | `guidewire-wd5-external` | QA Engineer |
| Gutor | gutor.com | `workday` | `gutor-wd3-gutor_career_site` | Area Sales Manager |
| GX Bank Berhad |  | `workday` | `gxs-wd3-gx_bank` | Infrastructure Engineer |
| Gxs |  | `workday` | `gxs-wd3-grxst` | Software Engineer |
| GXS Bank | gxs.com.sg | `workday` | `gxs-wd3-grxst` | Data Engineer |
| Harman | jobs.harman.com | `workday` | `harman-wd3-harman` | Embedded Software Engineer |
| Harman International | harman.com | `workday` | `harman-wd3-harman` | Intern |
| Harriscomputer | alterahealth.com | `workday` | `harriscomputer-wd3-altera` | Procurement Specialist |
| Havas | havas.com | `workday` | `havas-wd3-mediaexternalcareersite` | Art Director |
| Heidelberg | heidelberg.com | `workday` | `heidelberg-wd502-careersheidelberg` | Sales Account Manager |
| Heinz | jobs.kraftheinz.com | `workday` | `heinz-wd1-kraftheinz_careers` | Analyst |
| Hempel | www.hempel.com | `workday` | `hempel-wd3-hempelcareers` | Cash Application Specialist |
| Hewlett Packard Enterprise | hpe.com | `workday` | `hpe-wd5-wfmathpe` | Sales Support Analyst |
| Hillenbrand | hillenbrand.com | `workday` | `hillenbrand-wd3-global` | Process Associate |
| Hindustan Unilever Limited | hul.co.in | `workday` | `unilever-wd3-unilever_experienced_professionals` | Key Account Executive |
| Hiscox |  | `workday` | `hiscox-wd3-hiscox_external_site` | Syndicate Accounting and Reporting Manager |
| Hitachi Energy India Limited |  | `workday` | `hitachi-wd1-hitachi` | Mechanical Simulation Engineer |
| HITACHI ENERGY TECHNOLOGY SERVICES PRIVATE LIMITED |  | `workday` | `hitachi-wd1-hitachi` | Computer-Aided Design and Drafting Professional |
| Hl | hl.com | `workday` | `hl-wd1-corporate` | Platform Engineer |
| HP Inc. | hp.com | `workday` | `hp-wd5-exteu-ac-careersite` | Technical Support Supervisor |
| Huron |  | `workday` | `huron-wd1-huroncareers` | Analytics Engineer |
| Husqvarnagroup | www.husqvarnagroup.com | `workday` | `husqvarnagroup-wd3-external_career_site` | IAM Solution Architect |
| Hyster-Yale Materials Handling |  | `workday` | `hysteryale-wd1-hyster-yalecareers` | Cost Engineering Associate |
| Hyster-Yale Materials Handling, Inc. |  | `workday` | `hysteryale-wd1-hyster-yalecareers` | Data Governance Analyst |
| Hysteryale |  | `workday` | `hysteryale-wd1-hyster-yalecareers` | Procurement Engineer |
| ICF | icf.com | `workday` | `icf-wd5-icfexternal_career_site` | Project Finance Controller |
| IDEX Corporation | idexcorp.com | `workday` | `idexcorp-wd5-idexuk` | Accountant |
| Idexx |  | `workday` | `idexx-wd115-idexx` | Radiologist |
| IFF |  | `workday` | `iff-wd5-iff_careers` | Specialist |
| IG Group |  | `workday` | `ig-wd103-ext_ig` | Cloud PAM Engineer |
| Illumina | www.illumina.com | `workday` | `illumina-wd1-illumina-careers` | Product Complaints Analyst |
| Imerys | imerys.com | `workday` | `imerys-wd3-imerys-careers` | Quality Manager |
| Indovinya |  | `workday` | `ivlglobaliod-wd1-indovinya` | Process Engineer |
| Infios | www.koerber-supplychain-software.com | `workday` | `infios-wd502-infios` | Software Engineer |
| Infobip | infobip.com | `workday` | `infobip-wd3-infobipcareers` | Demand Generation Manager |
| Ingram Micro | careers.ingrammicro.com | `workday` | `ingrammicro-wd5-ingrammicro` | Software Engineer |
| Ingredion | www.ingredion.com | `workday` | `ingredion-wd1-ingredioncareers` | Technical Sales Executive |
| Innocap | innocap.com | `workday` | `innocap-wd10-innocap-external-career-site` | Analyst |
| insightsoftware | insightsoftware.com | `workday` | `magnitudesoftware-wd1-external` | Customer Success Analyst |
| Integra LifeSciences | jobs.integralife.com | `workday` | `integralife-wd1-careers` | Account Manager |
| Integral Ad Science | integralads.com | `workday` | `integralads-wd1-iascareers` | Sales Director |
| International Flavors & Fragrances | iff.com | `workday` | `iff-wd5-iff_careers` | Product Experience Researcher |
| International Schools Partnership | internationalschoolspartnership.com | `workday` | `internationalschools-wd3-ispcareers` | Art Teacher |
| Interpublic Group | omc.com | `workday` | `interpublic-wd5-omc` | Data Operations and Reporting Manager |
| Invesco |  | `workday` | `invesco-wd1-ivz` | Business Analyst |
| IQVIA | jobs.iqvia.com | `workday` | `iqvia-wd1-iqvia` | Software Development Engineer |
| Itron | itron.com | `workday` | `itron-wd5-itron` | Apprentice |
| Ivlglobaliod |  | `workday` | `ivlglobaliod-wd1-indovinya` | Mechanical Engineer |
| Jabil | careers.jabil.com | `workday` | `jabil-wd5-jabil_careers` | Test Engineer |
| Jadeglobal |  | `workday` | `jadeglobal-wd5-jade_careers` | Technical Architect |
| Jbtm |  | `workday` | `jbtm-wd108-jbt_marel_career_site` | Industry Sales Manager |
| JCI |  | `workday` | `jci-wd5-jci` | Integrated Solutions Service Technician |
| Jiostar | www.jiostar.com | `workday` | `jiostar-wd102-jiostar` | Assistant Manager - Direct Tax |
| Johnson & Johnson Vision | jjvision.com | `workday` | `jj-wd5-jj` | Assistant Manager, Customer Training |
| Jotun |  | `workday` | `jotun-wd3-jotun_careers` | Executive - Planning and Distribution |
| Julius Baer | juliusbaer.com | `workday` | `juliusbaer-wd3-finance_careers` | Night Desk Officer |
| Kaleris |  | `workday` | `kaleris-wd501-kaleris_careers` | Business Development Representative |
| Kantar |  | `workday` | `kantar-wd3-kantar` | Research Manager |
| Keystone Human Services | khs.org | `workday` | `keystonehumanservices-wd5-khs_careers` | Behavior Guidance Specialist |
| Kimberly-Clark | kimberly-clark.com | `workday` | `kimberlyclark-wd1-global` | Plant Logistics Manager |
| Kimberlyclark |  | `workday` | `kimberlyclark-wd1-global` | Key Accounts Executive |
| Kognitivinc | kognitivinc.com | `workday` | `kognitivinc-wd1-kognitiv-careers` | Adaptive Consultant |
| KONE | kone.com | `workday` | `kone-wd3-careers` | Software Developer |
| KSB | ksb.com | `workday` | `ksb-wd3-ksb_externalcareersite` | Executive |
| Labcorp | careers.labcorp.com | `workday` | `labcorp-wd1-external` | Site Initiation & Kit Inventory Coordinator |
| Lattice Semiconductor | www.latticesemi.com | `workday` | `latticesemi-wd5-latticesemiconductorscareers` | Export Control Coordinator |
| Lbg |  | `workday` | `lbg-wd3-lloyds_technology_centre` | Mobile Developer |
| Leica Microsystems | leica-microsystems.com | `workday` | `danaher-wd1-danaherjobs` | Area Sales Manager |
| LexisNexis Legal & Professional | lexisnexis.com | `workday` | `relx-wd3-relx` | Machine Learning Engineer |
| Lifung | www.lifung.com | `workday` | `lifung-wd3-lifung` | Quality Control Manager |
| Likewize |  | `workday` | `likewize-wd1-external` | IT Security Engineer |
| Lilly | careers.lilly.com | `workday` | `lilly-wd115-cmp` | IT Analyst |
| Linxens | linxens.com | `workday` | `onelinxens-wd3-external_careers` | EHS Engineer |
| Linxon | linxon.com | `workday` | `slihrms-wd3-linxon` | Financial Analyst |
| Live Nation Entertainment |  | `workday` | `livenation-wd503-tmexternalsite` | 3D Designer |
| Livenation |  | `workday` | `livenation-wd503-tmexternalsite` | Abuse Operations Engineering Lead |
| LiveRamp | liveramp.com | `workday` | `liveramp-wd5-liverampcareers` | Implementation Consultant |
| Lloyds Technology Centre | lloydstechnologycentre.com | `workday` | `lbg-wd3-lloyds_technology_centre` | Software Engineer |
| Logitech |  | `workday` | `logitech-wd5-logitech` | Product Owner |
| Lonza | lonza.com | `workday` | `lonza-wd3-lonza_careers` | Integration Engineer |
| Lowe's | talent.lowes.com | `workday` | `lowes-wd5-lws_external_cs` | Associate Director |
| LPL Financial | lpl.com | `workday` | `lplfinancial-wd1-india_ext` | Learning and Development Consultant |
| Luminegrp |  | `workday` | `luminegrp-wd3-tomia` | Support Engineer |
| Lytx | www.lytx.com | `workday` | `lytx-wd1-lytx` | Data Engineer |
| Maersk | careers.maersk.com | `workday` | `maersk-wd3-maersk_careers` | Inventory Controller |
| Magna | magnacareers.com | `workday` | `magna-wd3-magna` | Engineer |
| Magna Steyr | magna.com | `workday` | `magna-wd3-magna` | Designer |
| Makse Group | maksegroup.com | `workday` | `maksegroup-wd12-openings` | Accountant |
| Maksegroup | www.maksegroup.com | `workday` | `maksegroup-wd12-openings` | Assistant Accounting Manager |
| Manh | manh.com | `workday` | `manh-wd5-external` | Administrator - Systems |
| MarketStar | www.marketstar.com | `workday` | `wasatchproperty-wd1-marketstarcareers` | Team Lead - Operations |
| Marmon Technologies India Private Limited | marmon.com | `workday` | `marmon-wd501-marmon_careers` | Lab Engineer |
| Mars | bettertogethercareers.com | `workday` | `mars-wd3-bettertogether` | Finance Business Partner |
| Marsh | corporate.marsh.com | `workday` | `mmc-wd1-careers` | Compliance Specialist |
| Masco | jobs.masco.com | `workday` | `masco-wd1-behr` | Chemist |
| MassMutual | careers.massmutual.com | `workday` | `massmutual-wd1-mmindcareersite` | Operations Associate |
| Mavenir | mavenir.com | `workday` | `mavenir-wd1-mavenir_careers` | Operations Engineer |
| McKesson | careers.mckesson.com | `workday` | `mckesson-wd3-external_careers` | Software Engineer |
| Medline | www.medline.com | `workday` | `medline-wd5-medline` | Accounts Payable Analyst |
| Medtronic | www.medtronic.com | `workday` | `medtronic-wd1-redeploymentmedtroniccareers` | IT Technologist |
| Merative | merative.com | `workday` | `merative-wd12-external_career_site` | Technical Consultant |
| Mercer | mercer.com | `workday` | `mmc-wd1-mmc` | Investment Data Specialist |
| Meredith |  | `workday` | `meredith-wd5-ext_india` | Analyst |
| MFS |  | `workday` | `mfs-wd1-mfs-careers` | Business Systems Analyst |
| Michelin | michelin.com | `workday` | `michelinhr-wd3-michelin` | Legal Counsel |
| Michelinhr |  | `workday` | `michelinhr-wd3-michelin` | Application Reliability Engineer |
| Microchip Technology Inc. | microchip.com | `workday` | `microchiphr-wd5-external` | Hardware Engineer |
| MillerKnoll | millerknoll.com | `workday` | `millerknoll-wd1-millerknoll` | Software Engineer |
| Minor | minor.com | `workday` | `minor-wd102-careers` | Director of Finance |
| Miqdigital | www.wearemiq.com | `workday` | `miqdigital-wd3-miq_careers` | Data Scientist |
| MKS Instruments | mks.com | `workday` | `mksinst-wd1-mkscareersemea` | Associate Chemist |
| Mksinst | www.mks.com | `workday` | `mksinst-wd1-mkscareersemea` | Engineering Applications Administrator |
| Mobility |  | `workday` | `mobility-wd503-mobility` | Automotive Market Analyst |
| Modaxo | modaxo.com | `workday` | `modaxo-wd3-trellint` | Software Development Engineer |
| ModMed | modmed.com | `workday` | `modmed-wd501-india_career_site` | Site Reliability Engineer |
| Mondelēz International | mondelezinternational.com | `workday` | `mdlz-wd3-external` | Techno Lead |
| Monolithic Power Systems, Inc. |  | `workday` | `monolithicpower-wd12-mps_careers` | Field Application Engineer |
| Monotype |  | `workday` | `monotype-wd1-monotype` | Market Intelligence Trainee |
| Montblanc | montblanc.com | `workday` | `richemont-wd3-richemont` | Sales Associate |
| Moog | www.moog.com | `workday` | `moog-wd5-moog_external_career_site` | EHS Engineer |
| Morningstar | www.morningstar.com | `workday` | `morningstar-wd5-morningstar` | Technical Product Manager |
| Motorola Solutions | motorolasolutions.com | `workday` | `motorolasolutions-wd5-careers` | Software Engineer |
| Movado Group |  | `workday` | `movadogroup-wd1-careers` | Shopify Site Content Manager |
| Movadogroup |  | `workday` | `movadogroup-wd1-careers` | DevOps Engineer |
| MRI Software | mrisoftware.com | `workday` | `mrisoftware-wd501-external_careersite` | Systems Administrator |
| Mrisoftware |  | `workday` | `mrisoftware-wd501-external_careersite` | Software Engineer |
| MSD | jobs.msd.com | `workday` | `msd-wd5-searchjobs` | Quality Specialist |
| MUFG Global Service Private Limited | mufg.jp | `workday` | `mufgub-wd3-mufg-careers` | Vice President, Professional Practices |
| Multitude |  | `workday` | `multitude-wd103-careers_multitude` | Full-Stack Engineer |
| Nationwide |  | `workday` | `nationwide-wd1-nationwide_career_india` | Data Engineer |
| NatWest Group | jobs.natwestgroup.com | `workday` | `rbs-wd3-rbs` | Software Engineer |
| NCR Voyix | ncrvoyix.com | `workday` | `ncr-wd1-ext_apac` | Software Engineer |
| Newfold Digital | newfold.com | `workday` | `web-wd1-externalcareersite` | Abuse Mitigation and Compliance Associate |
| Newperkinelmer |  | `workday` | `newperkinelmer-wd1-external` | Director, Master Data Management |
| Nexperia | nexperia.com | `workday` | `nexperia-wd3-careers` | AI Engineer |
| Nextgen | www.nextgen.com | `workday` | `nextgen-wd5-nextgen_careers` | Client Support Operations Manager |
| Nissan |  | `workday` | `alliance-wd3-nissanjobs` | Product Marketing Manager |
| NN Group |  | `workday` | `nngroup-wd3-wdexternal` | Domain Architect |
| Nordson | nordson.com | `workday` | `nordsonhcm-wd501-nordsoncareers` | Purchasing and Procurement Specialist |
| Normet | www.normet.com | `workday` | `normet-wd502-normetcareers` | Sales Support Executive |
| Novartis | novartis.com | `workday` | `novartis-wd3-novartis_careers` | Director |
| Novonesis | www.novonesis.com | `workday` | `novonesis-wd103-novonesis_careers` | Technical Service Specialist |
| NTT DATA |  | `workday` | `nttlimited-wd3-ntt_careers` | Network Security Engineer |
| NTT Global Data Centers | ntt.com | `workday` | `nttglobaldatacenters-wd501-external` | Procurement Specialist |
| Nttlimited |  | `workday` | `nttlimited-wd3-ntt_careers` | MS Engineer - SQL |
| nVent | nvent.com | `workday` | `nvent-wd5-nvent` | Creative Design Project Specialist |
| NXP Semiconductors | nxp.com | `workday` | `nxp-wd3-careers` | Data Engineer |
| O9solutions | o9solutions.com | `workday` | `o9solutions-wd5-o9solutionsexternal` | Associate Customer Success Manager |
| Ohmium | ohmium.com | `workday` | `ohmium-wd12-ohmium_careers` | Engineer |
| Oliver Wyman | oliverwyman.com | `workday` | `mmc-wd1-mmc` | Administrative Assistant |
| OMERS |  | `workday` | `omers-wd3-omers_external` | Executive Assistant |
| Omnissa | omnissa.com | `workday` | `omnissa-wd501-omnissa_external_career_site` | Backend Software Developer |
| Onehealthineers |  | `workday` | `onehealthineers-wd3-ijmhrms` | Business Marketing Manager |
| Onemagnify |  | `workday` | `onemagnify-wd5-onemagnify_careers` | Analytics Engineer |
| Ontario Teachers' Pension Plan | otpp.com | `workday` | `otppb-wd3-ontarioteachers_careers` | Investment Intern |
| Opella | opella.com | `workday` | `chloe-wd3-opellacareers` | Customer MDM Architect |
| Optiv | www.optiv.com | `workday` | `optiv-wd5-optiv_careers` | Engineer |
| Organon |  | `workday` | `organon-wd5-search_jobs` | ERP Finance Solution Architect |
| Oshkosh Corporation | oshkoshcorp.com | `workday` | `oshkoshcorporation-wd5-oshkosh` | Finance Manager |
| Oshkoshcorporation | www.oshkoshcorp.com | `workday` | `oshkoshcorporation-wd5-oshkosh` | Systems Designer |
| Osv-chegg | www.chegg.com | `workday` | `osv_chegg-wd5-chegg` | FP&A Director |
| Otto International | ottoint.com | `workday` | `ottoint-wd116-careers` | Corporate Responsibility Specialist |
| OutSystems | outsystems.com | `workday` | `outsystems-wd503-outsystems` | Field Marketing Manager |
| Owens & Minor |  | `workday` | `owensminor-wd1-omcareers` | Business Development Manager |
| Owensminor |  | `workday` | `owensminor-wd1-omcareers` | System Analyst |
| P&G | pgcareers.com | `workday` | `pg-wd5-1000` | Medical Manager |
| Pae | amentumcareers.com | `workday` | `pae-wd1-amentum_careers` | Port Control Tower Watch |
| Pall Corporation | pall.com | `workday` | `danaher-wd1-danaherjobs` | SAP Security Engineer |
| Palo Alto Networks | jobs.paloaltonetworks.com | `workday` | `paloaltonetworks-wd5-panwexternalcareers` | Staff Software Engineer |
| Parexel | jobs.parexel.com | `workday` | `parexel-wd1-parexel_external_careers` | Biometrics Delivery Lead |
| PATH | path.org | `workday` | `path-wd1-external` | Community Coordinator |
| Pentair | pentair.com | `workday` | `pentair-wd5-pentair_careers` | Customer Master Data |
| People Inc. | people.inc | `workday` | `meredith-wd5-ext_india` | Product Manager |
| Pepperl+Fuchs | career.pepperl-fuchs.com | `workday` | `pepperlfuchs-wd103-pepperlfuchs` | Engineering Assistant |
| Perceptive | perceptive.com | `workday` | `calyx-wd1-perceptive` | Software Validation Engineer |
| Pfizer | pfizer.com | `workday` | `pfizer-wd1-pfizercareers` | Healthcare Executive |
| Phcgroup |  | `workday` | `phcgroup-wd3-ascensia_careers` | Regional Business Manager |
| Philips | careers.philips.com | `workday` | `philips-wd3-jobs-and-careers` | Software Technologist |
| Phinia | phinia.com | `workday` | `phinia-wd5-phinia_careers` | Material Planner |
| Pibgroup |  | `workday` | `pibgroup-wd3-pib` | System Analyst |
| Pinebridge |  | `workday` | `pinebridge-wd5-pinebridge_career_site` | Analyst - Collateral & Margin Operations |
| Pinnacle | pinnaclereliability.com | `workday` | `pinnacle-wd1-pinnacle` | Project Manager |
| Pinnacle Group | pinnacle1.com | `workday` | `pinnaclegroup-wd1-pinnaclegroup` | Recruiter |
| Pinnaclegroup | www.pinnacle1.com | `workday` | `pinnaclegroup-wd1-pinnaclegroup` | GTM Lead |
| Piramal Pharma Solutions | piramalpharmasolutions.com | `workday` | `piramalpharma-wd102-piramal_external_careers` | Human Resources Manager |
| Pitney Bowes | pitneybowes.com | `workday` | `pitneybowes-wd1-pbcareers` | SAP Consultant |
| Plante Moran | plantemoran.com | `workday` | `plantemoran-wd1-pmexternalcareers` | Site Reliability Engineer |
| Plantemoran | www.plantemoran.com | `workday` | `plantemoran-wd1-pmexternalcareers` | U.S. Tax Staff |
| Plug Power |  | `workday` | `plugpower-wd5-plug_power_inc` | Planner |
| Pluxee | pluxeegroup.com | `workday` | `pluxee-wd3-pluxee_career_site` | Field Sales Executive |
| Polaris | polaris.com | `workday` | `polaris-wd5-polarisjobs` | Global Trade Specialist |
| Porch Group | porchgroup.com | `workday` | `porch-wd1-careers` | Administrative Assistant |
| Pratt & Whitney | prattwhitney.com | `workday` | `globalhr-wd5-rec_rtx_ext_gateway` | Analyst |
| Premierresearch | premier-research.com | `workday` | `premierresearch-wd12-premierresearch` | Associate Data Manager |
| Pretium Enterprise Services |  | `workday` | `pretiumenterpriseservices-wd1-pretium-enterprise-services` | Residential Credit Team Lead |
| Procore | careers.procore.com | `workday` | `procore-wd12-procore_external_careers` | Software Engineer |
| Prodege | www.prodege.com | `workday` | `prodege-wd108-prodege_careers` | Associate Project Manager |
| Proofpoint |  | `workday` | `proofpoint-wd5-proofpointcareers` | Named Account Manager |
| Propharmagroup | propharmagroup.com | `workday` | `propharmagroup-wd1-ppgcareers` | Pharmacovigilance Specialist |
| Prudential |  | `workday` | `prudential-wd3-prudential` | Associate |
| PT Japfa Food Indonesia | japfa.com | `workday` | `japfa-wd102-external` | Production Operator |
| PTC | ptc.com | `workday` | `ptc-wd1-ptc` | Channel Account Manager |
| Puma | about.puma.com | `workday` | `puma-wd502-jobs_at_puma` | Software Engineer (Quality) |
| PVH |  | `workday` | `pvh-wd1-pvh_careers` | Accountant |
| Q2 | q2.com | `workday` | `q2ebanking-wd5-q2` | Operations Project Manager |
| Q2ebanking |  | `workday` | `q2ebanking-wd5-q2` | Quality Assurance Engineer |
| QIAGEN |  | `workday` | `qiagen-wd502-qiagen` | HR Manager |
| Qnity |  | `workday` | `qnity-wd503-jobs` | Procurement Data Analytics & Reporting Analyst |
| Qualys | qualys.com | `workday` | `qualys-wd5-careers` | DevOps Engineer |
| Quantiphi | quantiphi.com | `workday` | `quantiphi-wd1-careers_at_quantiphi` | Business Analyst |
| Quickbase | careers.quickbase.com | `workday` | `quickbase-wd504-external` | Product Manager |
| Quickenloans |  | `workday` | `quickenloans-wd5-rocket_india` | Software Engineer |
| R1 RCM | r1rcm.com | `workday` | `r1rcm-wd1-r1rcm` | Software Engineer |
| Rackspace | rackspace.jobs | `workday` | `rackspace-wd1-external` | Windows Systems Engineer |
| Randstad | randstad.com | `workday` | `randstad-wd502-randstadcareers` | Talent Sourcing Associate |
| Rapid7 | rapid7.com | `workday` | `mymoose-wd1-careers` | Atlassian Systems Administrator |
| Red Hat | redhat.com | `workday` | `redhat-wd5-jobs` | Delivery Manager |
| Redaptive |  | `workday` | `redaptive-wd12-redaptive-careers` | Business Development Specialist |
| Regal Rexnord | careers.regalrexnord.com | `workday` | `regalrexnord-wd1-careers` | .NET Backend Engineer |
| Regeneron | careers.regeneron.com | `workday` | `regeneron-wd1-careers` | Scientist |
| Regeneron Pharmaceuticals | regeneron.com | `workday` | `regeneron-wd1-careers` | Facilities Manager |
| Regnology | www.regnology.net | `workday` | `regnology-wd103-regnology` | Hubspot Administrator |
| Rehlko | www.rehlko.com | `workday` | `rehlko-wd12-reh` | Assistant Manager, Manufacturing Engineering |
| RELX | rxglobal.com | `workday` | `relx-wd3-reedexhibitions` | Software Engineering Lead |
| Renault Group | renaultgroup.com | `workday` | `alliancewd-wd3-renault-group-careers` | System Architecture Leader |
| Renishaw |  | `workday` | `renishaw-wd3-renishaw` | Project Manager |
| Reputation |  | `workday` | `reputation-wd1-external` | Product Manager |
| Revantage | www.revantage.com | `workday` | `revantage-wd1-revantage` | Legal Counsel |
| Revenera | revenera.com | `workday` | `flexerasoftware-wd1-revenera` | Product Owner |
| Revvity |  | `workday` | `revvity-wd103-external` | SAP S/4HANA Central Finance AIF Support Analyst |
| Rhe | rhenus.group | `workday` | `rhe-wd3-r1111` | Business Development Manager |
| Richemont | www.richemont.com | `workday` | `richemont-wd3-richemont` | Sales Associate |
| RingCentral | ringcentral.com | `workday` | `ringcentral-wd1-ringcentral_careers` | Engineering Manager |
| Rio Tinto | www.riotinto.com | `workday` | `riotinto-wd3-riotinto_careers` | Payroll Systems Analyst |
| Roche | careers.roche.com | `workday` | `roche-wd3-roche-ext` | Delivery Service Manager |
| Rocket | rocketsoftware.com | `workday` | `rocket-wd5-rocket_careers` | Software Engineer |
| Rockwell Automation | rockwellautomation.com | `workday` | `rockwellautomation-wd1-external_rockwell_automation` | Engineering Excellence Manager |
| Rockwoolgroup |  | `workday` | `rockwoolgroup-wd3-rockwool` | Assistant Manager, Warehouse |
| Rohlig | rohlig.com | `workday` | `rohlig-wd103-rohlig_careers` | Data Analyst |
| Room to Read | roomtoread.org | `workday` | `osv_rtr-wd5-roomtoread` | Social Mobilizer |
| Roquette | roquette.com | `workday` | `roquette-wd3-external` | Operator |
| Royal IHC | royalihc.com | `workday` | `royalihc-wd103-external_career` | Engineer |
| Royal Philips | philips.com | `workday` | `philips-wd3-jobs-and-careers` | Software Leader |
| Royalihc |  | `workday` | `royalihc-wd103-external_career` | Finance Manager |
| RSM | jobs.rsmus.com | `workday` | `rsm-wd1-rsmcareers` | Cyber Security Strategy Associate |
| Ruder Finn | ruderfinn.com | `workday` | `ruderfinn-wd5-ruderfinn` | Account Executive |
| Russell | russellinvestments.com | `workday` | `russell-wd5-russellinvestments` | Accountant |
| Russell Investments |  | `workday` | `russell-wd5-russellinvestments` | Marketing Automation Specialist |
| Ryan | ryan.com | `workday` | `ryan-wd1-ryancareers` | Finance Associate |
| Saab | saab.com | `workday` | `saabgroup-wd116-saab_careers` | Ultrasonic Test Operator |
| Saabgroup |  | `workday` | `saabgroup-wd116-saab_careers` | Assembler |
| Sabre | www.sabre.com | `workday` | `sabre-wd1-sabrejobs` | Data Science Engineer |
| Safeguard Global |  | `workday` | `safeguardglobal-wd3-external_careers` | Payroll Specialist |
| Safeguardglobal |  | `workday` | `safeguardglobal-wd3-external_careers` | Implementation Project Specialist |
| SailPoint | sailpoint.com | `workday` | `sailpoint-wd1-sailpoint` | Software Engineer |
| Saison | creditsaison.in | `workday` | `saison-wd102-credit_saison_india` | Financial Planning and Analysis Manager |
| Saks |  | `workday` | `saks-wd1-careers_at_saks` | Payroll Processing Trainee |
| Samsung Electronics |  | `workday` | `sec-wd3-samsung_careers` | Post-Silicon Validation Engineer |
| Sandvik |  | `workday` | `sandvik-wd3-sandvik-jobs` | Quality Assurance Engineer |
| Sandvik Coromant | sandvik.coromant.com | `workday` | `sandvik-wd3-coromant-jobs` | Internal Auditor |
| Sanofi | sanofi.com | `workday` | `sanofi-wd3-sanoficareers` | Data and Process Management Manager |
| Sartorius | sartorius.com | `workday` | `sartorius-wd3-sartoriuscareers` | Service Support |
| Saxobank | home.saxo | `workday` | `saxobank-wd3-careeratsaxobank` | Trading Surveillance Officer |
| Sbdinc |  | `workday` | `sbdinc-wd1-stanley_black_decker_career_site` | PMO Manager |
| Scientific Games |  | `workday` | `sglottery-wd5-scientificgamesexternalcareers` | Accounting Manager |
| Sec |  | `workday` | `sec-wd3-samsung_careers` | Firmware Engineer |
| Seic | seic.com | `workday` | `seic-wd1-sei_global_services` | Software Engineer |
| Semtech | semtech.com | `workday` | `semtech-wd1-semtechcareers` | Staff Engineer - Analog IC |
| Sensata Technologies | sensata.com | `workday` | `sensata-wd1-sensata-careers` | Computer Operations Specialist |
| ServiceTitan |  | `workday` | `servicetitan-wd1-servicetitan` | Site Reliability Engineer |
| Sglottery |  | `workday` | `sglottery-wd5-scientificgamesexternalcareers` | Infrastructure Delivery Manager |
| Siemens Healthineers |  | `workday` | `onehealthineers-wd3-shsjb` | Business Marketing Manager |
| Sifive | www.sifive.com | `workday` | `sifive-wd1-sifivecareers` | Product Power Engineer |
| Signify | careers.signify.com | `workday` | `lighting-wd3-jobs-and-careers` | Digital Technical Engineer |
| Silabs |  | `workday` | `silabs-wd1-experiencedjobs` | Software Quality Assurance Manager |
| Silicon Labs | silabs.com | `workday` | `silabs-wd1-siliconlabscareers` | Modem Verification Engineer |
| SimCorp | simcorp.com | `workday` | `simcorp-wd3-simcorp_jobs` | Software Engineer |
| Skechers | about.skechers.com | `workday` | `skechers-wd5-one-career-site` | Quality Assurance Supervisor |
| SM-Cyclo France S.A.S. |  | `workday` | `sumitomoheavyindustries-wd103-external` | Sales Manager |
| SMEC | smec.com | `workday` | `surbanajurong-wd3-careersatsmec` | Social Safeguards Specialist |
| Smith+Nephew | smith-nephew.com | `workday` | `smithnephew-wd5-external` | Business Continuity Analyst |
| Smithweb | smithweb.com | `workday` | `smithweb-wd108-smith2` | Accountant |
| Solera | solera.com | `workday` | `solera-wd5-global_career_site` | Software Engineer |
| Solventum | solventum.com | `workday` | `healthcare-wd1-search` | Audit Supervisor |
| Spectris |  | `workday` | `spectris-wd3-pms_careers` | Sales Manager |
| Speedcast | www.speedcast.com | `workday` | `speedcast-wd1-speedcastcareers` | Edge Network Engineer |
| Sphera |  | `workday` | `sphera-wd1-careers` | Database Administrator |
| Springer Nature | springernature.com | `workday` | `springernature-wd3-springernaturecareers` | Change Manager |
| SS&C Technologies |  | `workday` | `ssctech-wd1-ssctechnologies` | Financial Services Operations Associate |
| Stanley Black & Decker | stanleyblackanddecker.com | `workday` | `sbdinc-wd1-stanley_black_decker_career_site` | Payroll and Benefits Specialist |
| Stellantis | stellantis.com | `workday` | `stellantis-wd3-external_career_site_id01` | Design Convergence |
| Streamlinehealthcare |  | `workday` | `streamlinehealthcare-wd501-streamline_healthcare_external_careers` | Software Engineer |
| Stryker | stryker.com | `workday` | `stryker-wd1-strykercareers` | Staff Engineer |
| Sulzer | sulzer.com | `workday` | `sulzer-wd502-sulzerjobs` | Industrial Engineer |
| Surbana Jurong | surbana.jurong | `workday` | `surbanajurong-wd3-sj_careers` | Infrastructure Manager |
| Surbanajurong | surbanajurong.com | `workday` | `surbanajurong-wd3-sj_careers` | BIM Associate |
| SUSE |  | `workday` | `suse-wd3-jobsatsuse` | Data Scientist |
| Svitzer | svitzer.com | `workday` | `svitzer-wd3-svitzer_careers` | Head of Commercial Excellence and Commercial Operations |
| Swarovski | swarovski.com | `workday` | `swarovski-wd3-swarovski` | Sales Consultant |
| Synechron | synechron.com | `workday` | `synechron-wd1-synechroncareers` | Java Developer |
| Syneos Health | syneoshealth.com | `workday` | `syneoshealth-wd12-syneos_health_external_site` | Safety Physician |
| Syniverse | www.syniverse.com | `workday` | `syniverse-wd1-syniversecareers` | Operations Engineer |
| T-Mobile | t-mobile.careers | `workday` | `tmobile-wd1-external` | Mobile Associate |
| Takeda | jobs.takeda.com | `workday` | `takeda-wd502-external` | Transition Manager |
| Takraf | www.takraf.com | `workday` | `takraf-wd103-takraf_external_careers` | Engineer |
| Target | target.com | `workday` | `target-wd5-targetcareers` | Procurement Manager |
| Tbc | lyric.ai | `workday` | `tbc-wd12-lyriccareers` | Software Engineer |
| TD | careers.td.com | `workday` | `td-wd3-td_bank_careers` | Data Engineer |
| TD SYNNEX | tdsynnex.com | `workday` | `synnex-wd5-tdsynnexcareers` | SAP IBP Consultant |
| TD Williamson | tdwilliamson.com | `workday` | `tdwilliamson-wd1-tdwcareers` | Administrative Assistant and Receptionist |
| Teciem | teciem.com | `workday` | `teciem-wd107-teciem` | Accounting Operations |
| Teleperformance | tp.com | `workday` | `onetp-wd1-teleperformance` | Desktop and Site Support Engineer |
| Telstra | www.telstra.com.au | `workday` | `telstra-wd3-telstra_careers` | Social Media Content Creator |
| Thales | careers.thalesgroup.com | `workday` | `thales-wd3-equest` | Mechanical Design Engineer |
| The Access Group | careers.theaccessgroup.com | `workday` | `theaccessgroup-wd103-access_group_external_careers` | Software Engineer |
| The Coca-Cola Company | coca-colacompany.com | `workday` | `coke-wd1-coca-cola-careers` | Scientist, Product Development |
| The Goodyear Tire & Rubber Company | goodyear.com | `workday` | `goodyear-wd1-goodyearcareers` | MRO Specialist |
| The Kraft Heinz Company | kraftheinzcompany.com | `workday` | `heinz-wd1-kraftheinz_careers` | Associate Manager ESG |
| The Nature Conservancy India Solutions | nature.org | `workday` | `nature-wd108-externalcareers` | Business Development Associate Director |
| The Toro Company | jobs.thetorocompany.com | `workday` | `ttc-wd1-toro_external_careers` | Software Developer |
| The Walt Disney Company | thewaltdisneycompany.com | `workday` | `disney-wd5-disneycareerdc` | Database Engineering Manager |
| Thermo Fisher Scientific | thermofisher.com | `workday` | `thermofisher-wd5-thermofishercareers` | Software Architect |
| Thomson Reuters | thomsonreuters.com | `workday` | `thomsonreuters-wd5-external_career_site` | Project Manager |
| Thornton Tomasetti | careers.thorntontomasetti.com | `workday` | `tt-wd503-thorntontomasetti` | Project Engineer |
| Tieto | vivicta.com | `workday` | `tieto-wd3-tieto_careers_external_site` | Salesforce Developer |
| TJX | jobs.tjx.com | `workday` | `tjx-wd1-tjx_external` | IT Engineering Manager |
| Tnsi | tnsi.com | `workday` | `tnsi-wd1-search` | Customer Service Representative |
| Toppanmerrill |  | `workday` | `toppanmerrill-wd5-toppan_merrill` | Executive - Administration & Facilities |
| Toyota Automated Logistics | toyota-automated-logistics.com | `workday` | `vanderlande-wd3-careers` | Data Visualization & Reporting Engineer |
| Trafigura | trafigura.com | `workday` | `trafigura-wd3-trafiguracareersite` | Executive Assistant |
| Trane Technologies | tranetechnologies.com | `workday` | `tranetechnologies-wd12-trane_technologies_careers` | AI/ML Research Engineer |
| TransUnion | transunion.com | `workday` | `transunion-wd5-transunion` | Business Operations Representative |
| Trend Micro |  | `workday` | `trendmicro-wd3-external` | Solutions Engineer |
| Trendmicro |  | `workday` | `trendmicro-wd3-external` | Account Manager |
| Trimble | careers.trimble.com | `workday` | `trimble-wd1-trimblecareers` | Support Engineer |
| Trinity Life Sciences | trinitylifesciences.com | `workday` | `trinitylifesciences-wd108-trinity` | Solutions Analyst |
| Trintech | trintech.com | `workday` | `trintech-wd501-trintech` | Application Support |
| Trumpf | www.trumpf.com | `workday` | `trumpf-wd3-trumpf_graduates_and_professionals` | Zonal Sales Manager |
| TVH | jobs.tvh.com | `workday` | `tvh-wd3-jobsattvh` | Technical Researcher |
| TVH India Private Ltd | tvh.com | `workday` | `tvh-wd3-jobsattvh` | Data Quality Officer |
| Tysonfoods |  | `workday` | `tysonfoods-wd5-tsn` | IT Project Specialist |
| U.S. Bank | careers.usbank.com | `workday` | `usbank-wd1-us_bank_careers` | Automation Engineer |
| Unilever |  | `workday` | `unilever-wd3-unilever_experienced_professionals` | Safety Executive |
| Unisys | unisys.com | `workday` | `unisys-wd5-external` | Experience Delivery |
| United Overseas Bank | www.uobgroup.com | `workday` | `uobgroup-wd3-uobexternal` | Technical Development Lead |
| Unitytech | unity.com | `workday` | `unitytech-wd1-unity` | Manager, Governance Risk and Compliance |
| University of Washington | washington.edu | `workday` | `uw-wd5-uwhires` | Research Scientist/Engineer |
| UPS | ups.com | `workday` | `hcmportal-wd5-search` | Application Developer |
| Valeo | valeo.com | `workday` | `valeo-wd3-valeo_jobs` | Area Sales Manager |
| Vanderlande | www.vanderlande.com | `workday` | `vanderlande-wd3-careers` | Controls Project Engineer |
| Vantage Data Centers | vantagedatacenters.com | `workday` | `vantagedc-wd1-vantage` | Vice President, Procurement Operations |
| Vantagedc |  | `workday` | `vantagedc-wd1-vantage` | Electrical Category Manager |
| Vantiva | vantiva.com | `workday` | `vantiva-impl-wd103-vantiva` | New Product Introduction Manager |
| Vantive |  | `workday` | `vantive-wd108-vantive` | Engineer |
| Varex Imaging | vareximaging.com | `workday` | `vareximaging-wd103-external_career_site` | Warehouse Incharge |
| Vareximaging |  | `workday` | `vareximaging-wd103-external_career_site` | FPGA Embedded Firmware Engineer |
| Veradigm | veradigm.com | `workday` | `veradigm-wd12-vr` | Customer Service Agent |
| Veralto |  | `workday` | `veralto-wd1-videojetjobs` | Software Engineer |
| VeriPark | veripark.com | `workday` | `veripark-wd103-veripark` | Software Development Manager |
| Verizon | mycareer.verizon.com | `workday` | `verizon-wd12-verizon-careers` | Network Operations Manager |
| Viavisolutions |  | `workday` | `viavisolutions-wd1-careers` | Platform Engineer |
| Victaulic | careers.victaulic.com | `workday` | `victaulic-wd1-victaulic_careers` | Piping Coordinator |
| Videojet | veralto.com | `workday` | `veralto-wd1-videojetjobs` | Business Analyst |
| VIRA Insight | virainsight.com | `workday` | `virainsight-wd108-vira_insight` | Project Planner |
| Vishay | jobs.vishay.com | `workday` | `vishay-wd3-vishaycareers` | Operator |
| Vxi | vxi.com | `workday` | `vxi-wd12-careers` | Site Reliability Engineer |
| Walmart | walmart.com | `workday` | `walmart-wd504-walmartexternal` | Software Engineer |
| Warner Bros. Discovery | wbd.com | `workday` | `warnerbros-wd5-global` | Director, International Controllership |
| Wattswater | watts.com | `workday` | `wattswater-wd5-external` | Field and Technical Support |
| Weareeverise | weareeverise.com | `workday` | `weareeverise-wd1-everisecareers` | Operations Manager |
| WEX | wexinc.com | `workday` | `wexinc-wd5-wexinc` | Database Architect |
| Wexinc |  | `workday` | `wexinc-wd5-wexinc` | Software Engineer |
| Wiley | wiley.com | `workday` | `wiley-wd1-wiley_careers` | Assistant Editor |
| Wilhelmsen |  | `workday` | `wilhelmsen-wd3-wilhelmsen` | Technical Lead |
| Wilsonhcg | www.wilsonhr.com | `workday` | `wilsonhcg-wd5-wilson_careers` | Recruitment Consultant |
| Wind River | windriver.com | `workday` | `aptiv-wd5-aptiv_careers` | Member of Technical Staff |
| Wood Mackenzie | woodmac.com | `workday` | `woodmac-wd3-woodmaccareers` | Product Manager |
| Woodmac | www.woodmac.com | `workday` | `woodmac-wd3-woodmaccareers` | Research Analyst |
| Woodward | www.woodward.com | `workday` | `woodward-wd5-woodward` | Supply Chain Manager |
| World Courier | worldcourier.com | `workday` | `myhrabc-wd5-global` | Logistics Operator |
| World Resources Institute | wri.org | `workday` | `wri-wd501-wri` | Budget Analyst |
| Worldvision | wvi.org | `workday` | `worldvision-wd1-worldvisioninternational` | Project Officer |
| Worldwide Clinical Trials | worldwide.com | `workday` | `worldwide-wd1-external` | Data Intelligence Analyst |
| WRI India | wri-india.org | `workday` | `wri-wd501-wri_india` | Communications Intern |
| Xpel | www.xpel.com | `workday` | `xpel-wd5-xpel_careers` | Operations Manager |
| Yokogawa | yokogawa.com | `workday` | `yokogawa-wd3-yokogawa-career-site` | Full Stack Developer |
| YouGov | jobs.yougov.com | `workday` | `yougov-wd103-yougov_external_careers` | Record to Report Accountant |
| Zebra | zebra.com | `workday` | `zebra-wd501-zebra_careers` | Software Engineer |
| ZEISS Group | zeiss.com | `workday` | `zeissgroup-wd3-external` | Software Engineer |
| Zendesk |  | `workday` | `zendesk-wd1-zendesk` | Account Executive |
| Zentiva | zentiva.com | `workday` | `zentiva-wd3-zentiva` | Quality Assurance Specialist |
| Zillow |  | `workday` | `zillow-wd5-zillow_group_external` | Director of Engineering |
| Zoetis | zoetis.com | `workday` | `zoetis-wd5-zoetis_intl` | CRM Manager |

### SuccessFactors — adapter exists, needs URL reconstruction — 349 companies

`ats_type="successfactors"` ← HiringCafe `source` in `successfactors`. Do NOT add `board_token` directly — resolve to full careers URL first (see expansion plan Phase 3).

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| AB SKF | skf.com | `successfactors` | `eu_SKF` | Territory Manager |
| ACA Group | acaglobal.com | `successfactors` | `com_foresidefi` | Timecard and Expense Administrator |
| ACG | acg-world.com | `successfactors` | `com_acgassocia` | Product Owner |
| Acolad | acolad.com | `successfactors` | `eu_amplexor` | IT Monitoring Operations Analyst |
| Actylis | actylis.com | `successfactors` | `com_acetousllc` | EHS Officer |
| Adama India Private Ltd | adama.com | `successfactors` | `eu_MAI` | Procurement Manager |
| ADB SAFEGATE Careers | adbsafegate.com | `successfactors` | `eu_ADBDP` | Computer Vision Engineer |
| ADVANZ PHARMA SERVICES (INDIA) | advanzpharma.com | `successfactors` | `com_AdvanzPharma` | Project Manager |
| Afcons Infrastructure Limited | afcons.com | `successfactors` | `com_afconsinfr` | Site Engineer |
| Agiliad |  | `successfactors` | `com_agiliad` | Software Engineer |
| Air India Limited | airindia.com | `successfactors` | `com_airindiali` | Cadet Pilot |
| Ajanta Pharma | ajantapharma.com | `successfactors` | `com_ajantaphar` | Production Officer |
| Aker Solutions | akersolutions.com | `successfactors` | `eu_akersoluti` | Application Portfolio Manager |
| AKT Solutions Ltd | aktglobal.com | `successfactors` | `eu_aktsolltd` | Application Consultant |
| Akzo Nobel Sourcing B.V. | akzonobel.com | `successfactors` | `eu_akzonobelsP2` | FP&A Analyst |
| alfanar | alfanar.com | `successfactors` | `eu_AlFanarP` | Branch Sales Manager |
| allnex | allnex.com | `successfactors` | `eu_allnexbelg` | IT GBS Head |
| Alstom | alstom.com | `successfactors` | `eu_ALSTOM` | V&V Designer |
| Alter Domus Participations SARL | alterdomus.com | `successfactors` | `eu_alterdomus` | Site Reliability Engineer |
| AMETEK, Inc. | ametek.com | `successfactors` | `com_ametekinc` | Software Engineer |
| ANZ Banking Group Limited | anz.com | `successfactors` | `com_anzbanking` | Site Reliability Engineer |
| Apotex Inc. | apotex.com | `successfactors` | `com_Apotex` | Quality and Compliance Manager |
| Aramark | aramarkcareers.com | `successfactors` | `com_ARAMARKPROD` | Food Service Manager |
| ArisGlobal Careers | arisglobal.com | `successfactors` | `com_arisglobalP2` | Quality Engineer |
| Arjo | arjo.com | `successfactors` | `eu_arjohuntle` | Rental Operations Manager |
| Asian Paints Ltd | asianpaints.com | `successfactors` | `com_C0013041173P` | Executive - Sales Commercial |
| ASSA ABLOY | assaabloy.com | `successfactors` | `eu_assaabloya` | BI Developer |
| ATC Tires Pvt. Ltd. | yokohama-atg.com | `successfactors` | `com_atctirespv` | Entity Reporting and Audit Specialist |
| Atlas Copco (India) Private Ltd. | atlascopco.com | `successfactors` | `eu_atlascopcoP` | Service Engineer |
| Atlas Corp. | atlascorporation.com | `successfactors` | `com_atlascorp` | Fleet Personnel Officer |
| Atos | atos.net | `successfactors` | `eu_Atos` | Application Packager |
| ATS Automation Tooling Systems Inc. | atsautomation.com | `successfactors` | `eu_atsP2` | Business Systems Analyst |
| AUO Mobility Solutions | auo.com | `successfactors` | `rmk_custom_careers.bhtc.com` | Industrialization Engineer |
| Aurigo Software Technologies Private | aurigo.com | `successfactors` | `com_aurigosoft` | Proposal Writer |
| Auro Textiles (Processing I) |  | `successfactors` | `eu_vardhmante` | Officer - Sustainability |
| Avaya Corporation | avaya.com | `successfactors` | `eu_C0000211211P` | Manager, Global Revenue Accounting |
| Avenue Supermart Ltd | dmartindia.com | `successfactors` | `com_avenuesupe` | Executive Floor General Manager |
| Axis Max Life Insurance Limited | axismaxlife.com | `successfactors` | `com_maxlifeins` | Relationship Associate |
| Axtria | axtria.com | `successfactors` | `com_axtriaindiP` | Project Leader |
| B. Braun Medical (India) | bbraun.com | `successfactors` | `eu_bbraunprd` | Territory Sales Executive |
| Ball Corporation | ball.com | `successfactors` | `com_ballcorpor` | Electrical & Instrumentation Engineer |
| Barco | barco.com | `successfactors` | `eu_Barco` | Technology Engineer |
| Barry Callebaut | barry-callebaut.com | `successfactors` | `eu_BARCALPRD` | Food Safety and Sanitation Manager |
| BASF Catalysts | basf-catalystsmetals.com | `successfactors` | `eu_basfcataly` | Key Accounts Manager |
| BASF India Limited | basf.com | `successfactors` | `eu_C0000159936P` | Product Development |
| Bayer | bayer.com | `successfactors` | `eu_C0003153479P` | Payroll and Accounting Executive |
| BCD Meetings & Events | bcdme.com | `successfactors` | `eu_bcdtravels` | Business Automation and AI Analyst |
| BCD Travel Services B.V. | bcdtravel.com | `successfactors` | `eu_bcdtravels` | Travel Consultant |
| Bechtel | bechtel.com | `successfactors` | `com_Bechtel` | Dashboard and Analytics |
| Belden Inc | belden.com | `successfactors` | `com_beldeninc` | Engineering Manager |
| Bell Microsystems Ltd | bell-integration.com | `successfactors` | `eu_bellmicros` | Contracts Manager |
| Bentley Systems | bentley.com | `successfactors` | `com_bentleyprod` | Manager, Human Resources Shared Services |
| BHTC GmbH |  | `successfactors` | `rmk_custom_careers.bhtc.com` | Software Architect |
| Birlasoft Limited | birlasoft.com | `successfactors` | `com_birlasoftl` | Oracle Finance Functional Consultant |
| Black & Veatch Family of Companies | bv.com | `successfactors` | `com_blackveatch2` | Engineer - Instrumentation & Controls |
| BMW AG | bmwgroup.com | `successfactors` | `eu_bmwag` | Credit Manager |
| Boehringer Ingelheim GmbH | boehringer-ingelheim.com | `successfactors` | `eu_BoehringerPRD` | Regulatory Affairs Manager |
| Brandix Apparel Limited | brandix.com | `successfactors` | `com_brandixapp` | Production Executive |
| British American Tobacco | bat.com | `successfactors` | `eu_C0007596015P` | Business Analyst |
| British Telecommunications PLC | bt.com | `successfactors` | `eu_britisht01P1` | Cloud Engineering Specialist |
| Brose Fahrzeugteile SE & Co. | brose.com | `successfactors` | `eu_brosefahrz` | Patent Clerk |
| Bunge | bunge.com | `successfactors` | `eu_Bunge` | Territory Sales Executive |
| Caldic B.V. | caldic.com | `successfactors` | `eu_caldicbv` | Application Development Executive |
| CAPGEMINI SERVICE SAS | capgemini.com | `successfactors` | `eu_capgemitecP3` | Software Engineer |
| Cargill | cargill.com | `successfactors` | `eu_cargill` | Sales Executive |
| Celeros Flow Technology, LLC | celerosft.com | `successfactors` | `com_celerosflo` | Supply Chain Specialist |
| Celestica | celestica.com | `successfactors` | `eu_celesticaiP1` | Data Engineer |
| Chain IQ Group AG | chainiq.com | `successfactors` | `eu_chainiqgro` | Sourcing Specialist |
| Charles River Laboratories | criver.com | `successfactors` | `com_charlesrivP` | Data and DevOps Engineer |
| Chart Industries | chartindustries.com | `successfactors` | `com_ChartUrCourse` | Production Engineer |
| Cipla Limited | cipla.com | `successfactors` | `com_C0001172882P` | Team Member - Microbiology |
| Clariant International Ltd. | clariant.com | `successfactors` | `eu_Clariant` | IT Business Consultant FICO |
| CMA CGM | cmacgm-group.com | `successfactors` | `eu_C0002716868P` | Customer Care Professional |
| CNH Industrial Italia S.p.A. | cnh.com | `successfactors` | `eu_cnhindustr` | Engineering Method Specialist |
| Colgate-Palmolive | colgatepalmolive.com | `successfactors` | `com_colgate` | Territory Business Lead |
| Colt Technology Services | colt.net | `successfactors` | `eu_colttechnoP` | Engineer, IP Delivery |
| Columbus McKinnon Corporation | cmco.com | `successfactors` | `com_columbusmc` | Electrical Design Engineer |
| CommScope Inc. | commscope.com | `successfactors` | `com_CommScope` | Strategic Sourcing Specialist |
| Computacenter AG & Co. oHG | computacenter.com | `successfactors` | `eu_C0000167518P` | Software Developer |
| Corning | corning.com | `successfactors` | `com_CNGPROD` | Business Development Specialist |
| COWI | cowi.com | `successfactors` | `eu_cowiholdinP2` | Accountant |
| CPL Aromas FZE | cplaromas.com | `successfactors` | `com_cplaromasf` | Trainee |
| CRH | crh.com | `successfactors` | `eu_CRH` | Business Development Manager |
| Daikin | daikin.com | `successfactors` | `cloud_sap_daikinai01` | Assistant Manager |
| Dana Incorporated | dana.com | `successfactors` | `com_DanaLimitedP` | AP Analyst |
| Danfoss A/S | danfoss.com | `successfactors` | `eu_danfossas` | Business Analyst |
| Darshana Industries Pvt. Ltd. | darshanaindustries.com | `successfactors` | `com_SOUTHCO` | Sales Engineer |
| Deloitte | deloitte.ca | `successfactors` | `com_CADeloitte` | Commercialization Manager |
| Deloitte US \| Together Makes Progress | deloitte.com | `successfactors` | `com_deloittesh` | Consultant |
| DENODO SL | denodo.com | `successfactors` | `eu_denodosl` | Partner and Channel Sales Director |
| Dentsply Sirona, Inc | dentsplysirona.com | `successfactors` | `eu_DENTSPLY` | Service Engineer |
| DiaSorin S.p.A. | diasorin.com | `successfactors` | `eu_diasorinsp` | System Specialist |
| Dishman Carbogen Amcis Limited | imdcal.com | `successfactors` | `eu_dishmancar` | Finance Manager |
| Dorman Products | dormanproducts.com | `successfactors` | `com_S000008602P` | Field Support Specialist |
| DSV | dsv.com | `successfactors` | `eu_dsvas` | Business Development Manager |
| Dufry International AG | avoltaworld.com | `successfactors` | `eu_avoltaP` | Account Receivable Associate |
| DynatraceLLC | dynatrace.com | `successfactors` | `com_dynatracel` | QA Engineer |
| Eastman Chemical | eastman.com | `successfactors` | `com_eastmanprd` | Business Intelligence Analyst |
| EDAG Engineering GmbH | edag.com | `successfactors` | `eu_edagengine` | Automotive Diagnostics Software Test Engineer |
| Edrington | edrington.com | `successfactors` | `eu_C0008751175P` | Business Development Assistant |
| Edwards India Private Ltd | homeofindustrialideas.com | `successfactors` | `eu_atlascopcoP` | Order Management Executive |
| Element Solutions Inc | elementsolutionsinc.com | `successfactors` | `com_elementsol` | Quality Manager |
| Embassy Property Developments |  | `successfactors` | `rmk_custom_careers.embassygroup.com` | Assistant Manager |
| Endress+Hauser InfoServe GmbH+Co. KG | endress.com | `successfactors` | `eu_endress` | Business Development Manager |
| Epiroc Rock Drills AB | epiroc.com | `successfactors` | `eu_epirocP` | Central Planner |
| Equiti Labs Private Limited | successfactors.eu | `successfactors` | `eu_egmmarketiP2` | Backend Developer |
| EssilorLuxottica Group | essilorluxottica.com | `successfactors` | `eu_LUXGRP` | Mechanical Engineer |
| ExxonMobil | exxonmobil.com | `successfactors` | `com_exxonmobilP` | Supply Coordinator |
| EY | ey.com | `successfactors` | `eu_EYHRISPRD1` | Regulatory Reporting Professional |
| Fall Creek |  | `successfactors` | `com_fallcreekf` | Director of Breeding |
| Ficosa | ficosa.com | `successfactors` | `eu_C0001123112P` | Software Product Engineer |
| FIVES | fivesgroup.com | `successfactors` | `eu_fives` | Project Head |
| Fleet Management India Private Limited | caravel-group.com | `successfactors` | `com_caravelprod` | Buyer |
| FOLKS | folksvfx.com | `successfactors` | `com_artistesfo` | SAP SuccessFactors Analyst |
| FORVIA | faurecia.com | `successfactors` | `eu_adpllcP3` | Digital Data Engineer |
| FORVIA SE | forvia.com | `successfactors` | `eu_adpllcP3` | PLM Engineer |
| Foundever® | foundever.com | `successfactors` | `com_SitelPROD` | Team Leader |
| G R Infraprojects Limited | grinfra.com | `successfactors` | `com_grinfraproP2` | Engineer |
| Gainwell Technologies LLC | gainwelltechnologies.com | `successfactors` | `com_gainwellte` | Data Scientist |
| Gates Corporation | gates.com | `successfactors` | `com_1131442P` | Area Sales Manager |
| Generali Central Life Insurance Company Limited | gclife.com | `successfactors` | `com_futurege01` | Sales Manager |
| Getinge Holding B.V. & Co. KG | getinge.com | `successfactors` | `eu_GetingeProd` | Automation Manager |
| Givaudan | givaudan.com | `successfactors` | `eu_givaudan` | Application Chemist |
| Glanbia PLC | glanbia.com | `successfactors` | `eu_glanbiaplc` | Customer Service Representative |
| Gradiant India Private Limited | gradiant.com | `successfactors` | `rmk_custom_careers.gradiant.com` | Civil and Structural Engineer |
| GRIFOLS, S.A. | grifols.com | `successfactors` | `eu_Grifols` | Sales Specialist |
| Grundfos Management A/S | grundfos.com | `successfactors` | `eu_grundfosP1` | Supplier Quality Engineer |
| GXO Logistics | gxo.com | `successfactors` | `com_xpologisti` | Internal Auditor |
| Hafele India Private Limited | hafeleindia.com | `successfactors` | `com_hafeleindi` | Area Manager |
| Hanwha Ocean Energy Plant Unit | hanwhaocean.com | `successfactors` | `com_hanwhaocean` | PDMS Designer |
| HARTING Stiftung & Co. KG | harting.com | `successfactors` | `eu_hartingsti` | AI Application & Prompt Specialist |
| HatchD1 | hatch.com | `successfactors` | `com_hatchassocP` | P&ID Designer |
| Hatsun Agro Product Ltd | hap.in | `successfactors` | `com_hatsunagro` | Electrical |
| HCG Hospitals | hcghospitals.in | `successfactors` | `com_hcgprd` | General Job |
| HCLTech | hcltech.com | `successfactors` | `eu_HCLPRD` | Technical Lead |
| Heineken International B.V. | theheinekencompany.com | `successfactors` | `eu_C0000032666P` | Area Sales Manager |
| Hero MotoCorp | heromotocorp.com | `successfactors` | `com_Hero` | Team Manager |
| HID Global | hidglobal.com | `successfactors` | `eu_assaabloya` | Test Engineer |
| Hinduja Global Solutions Ltd | joinhgs.com | `successfactors` | `com_hindujagloP` | Process Consultant |
| Hindustan Coca-Cola Beverages | hccb.in | `successfactors` | `com_hindustancP` | Quality Assurance Executive |
| HKT Services Limited | pccw.com | `successfactors` | `com_hktservice` | Content Curator |
| HOERBIGER | hoerbiger.com | `successfactors` | `eu_HOEProd` | ABAP Consultant |
| Hollister Global Business Services India Private Limited | hollister.com | `successfactors` | `com_Hollister` | RPA Developer |
| Houghton Mifflin Harcourt | hmhco.com | `successfactors` | `com_houghtonmiP` | DevOps Engineer |
| Hyperion Materials & Technologies | hyperionmt.com | `successfactors` | `eu_hyperionmaP2` | Manufacturing Engineering Manager |
| ICICI Lombard | icicilombard.com | `successfactors` | `com_icicilomba` | Unit Sales Manager |
| IDEMIA | idemia.com | `successfactors` | `eu_OPTaMIS` | Functional Business Analyst |
| IDP Education Limited | idp.com | `successfactors` | `com_idpeducati` | Education Counsellor |
| IFFCOTECH Limited FZC | iffco.com | `successfactors` | `eu_iffcotechlP` | Finance Manager |
| IGT, a Nevada Corporation | igt.com | `successfactors` | `eu_igtanevadaP2` | Software Engineer |
| Incedo | incedo.com | `successfactors` | `com_incedotech` | Technical Lead |
| Indegene Private limited | indegene.com | `successfactors` | `com_indegenepr` | Business Solutions and Presales Manager |
| Indian Hotels Company Limited | ihcltata.com | `successfactors` | `cloud_sap_theindianhP2` | Guest Service Associate |
| Industria de Turbo Propulsores S.A.U. | itpaero.com | `successfactors` | `eu_ITP` | HR Operations |
| Info Edge (India) Limited | infoedge.com | `successfactors` | `com_infoedgein` | Customer Success Manager |
| Ingersoll Rand | irco.com | `successfactors` | `com_C0000164178P` | Design Engineer |
| Innomotics | innomotics.com | `successfactors` | `eu_InnoProd` | Portfolio Sales Professional |
| Intas Pharmaceuticals Limited | intasaccordcareers.com | `successfactors` | `com_intaspharm` | Training and Development Manager |
| InterGlobe | interglobe.com | `successfactors` | `cloud_sap_interglobe` | Data Analyst |
| InterGlobe Enterprises | career-in10.hr.cloud.sap | `successfactors` | `cloud_sap_interglobe` | Quality Assurance Associate |
| Intergraph Corporation dba Octave | octave.com | `successfactors` | `eu_intergraphP2` | Vice President, Global Channel Sales and Alliances |
| Intrepid Group | intrepidtravel.com | `successfactors` | `com_intrepidgr` | Reservations Supervisor |
| IRIS Software Inc | irissoftware.com | `successfactors` | `com_irissoftwa` | .NET Lead |
| ISUZU MOTORS LTD. | co.jp | `successfactors` | `com_isuzumotor` | SAP PP and QM Functional Consultant |
| itelligence | nttdata-solutions.com | `successfactors` | `eu_itelliP` | PMO |
| ITU International | itu.int | `successfactors` | `eu_ituinterna` | Innovation Ecosystem Consultant |
| Jaquar Group | jaquar.com | `successfactors` | `cloud_sap_jaquarandc` | Business Development Manager |
| JCB India Limited | jcb.com | `successfactors` | `com_jcbindiali` | Deputy Manager |
| JENOPTIK AG | jenoptik.com | `successfactors` | `eu_jenoptikag` | DevOps and Platform Engineer |
| Jindal Steel & Power | jindalsteel.in | `successfactors` | `com_jindalstee` | Mechanical Incharge |
| John Cockerill India Limited | johncockerill.com | `successfactors` | `eu_CMI` | Site Electrical Manager |
| John Deere | deere.com | `successfactors` | `com_1161975P` | Excavator Hydraulic Design Engineer |
| K Raheja Corp Pvt Ltd | krahejacorp.com | `successfactors` | `com_krahejacor` | Recovery and Collection Executive |
| Karl Storz SE & Co. KG | karlstorz.com | `successfactors` | `eu_karlstor01` | Territory Manager |
| KEC International | kecrpg.com | `successfactors` | `com_C0014469929P` | Engineer - Quality |
| Kemira Oyj | kemira.com | `successfactors` | `eu_kemira` | Application Specialist |
| Kennametal | kennametal.com | `successfactors` | `com_C0000160740P` | Product Design Engineer |
| Kerry Luxembourg S.a.r.l. | kerry.com | `successfactors` | `eu_kerryluxemP` | Technical Support Specialist |
| Khatib & Alami | khatibalami.com | `successfactors` | `eu_khatibalam` | Electrical Engineer |
| Kirloskar Brothers Limited | kirloskarpumps.com | `successfactors` | `com_kirloskarb` | Fabrication Procurement Manager |
| Komax AG | komaxgroup.com | `successfactors` | `eu_komaxag` | Software Developer |
| Kühne + Nagel (AG & Co.) KG | kuehne-nagel.com | `successfactors` | `eu_khnenagela` | Sales Representative |
| LABORATORIOS HIPRA, S.A. | hipra.com | `successfactors` | `eu_laboratoriP` | Area Sales Manager |
| Landis+Gyr AG | landisgyr.com | `successfactors` | `eu_LandisGyrPROD` | Technical Lead, Software Development (PLSQL) |
| LANXESS | lanxess.com | `successfactors` | `eu_lanxessP` | Sales Manager |
| Leister AG | leister-group.com | `successfactors` | `eu_leisterag` | Corporate Legal Specialist |
| Leviat | leviat.com | `successfactors` | `eu_CRH` | Sales Engineer |
| Liebherr-International S.A. | liebherr.com | `successfactors` | `eu_LiMySLive` | Engineer - PCB Layout |
| Lincoln Electric | lincolnelectric.com | `successfactors` | `eu_LEPROD` | IT Site Support Associate |
| Lindström | lindstromgroup.com | `successfactors` | `eu_lindstrmoy` | Sales Manager |
| Lloyds Register Group Services Limited | lr.org | `successfactors` | `eu_lloydsregiP` | Business Analyst |
| LRQA | lrqa.com | `successfactors` | `eu_LRQAP` | Administrative Specialist |
| Lubrizol Corporation | lubrizol.com | `successfactors` | `com_Lubrizolprod` | Customer Service Representative |
| Luminous | luminousindia.com | `successfactors` | `com_luminouspo` | Engineer |
| Lupin Limited | lupin.com | `successfactors` | `com_C0001119306P` | Executive |
| LyondellBasell North America | lyondellbasell.com | `successfactors` | `com_LBI` | Project Control Engineer |
| MacDermid Enthone Industrial Solutions | macdermidenthone.com | `successfactors` | `com_elementsol` | Field Service Officer |
| Mahindra & Mahindra Limited | mahindra.com | `successfactors` | `com_Mahindra` | GAT - Engine PU |
| MAHLE International GmbH | mahle.com | `successfactors` | `eu_mahleinter` | CAD Administrator |
| Mastek Limited | mastek.com | `successfactors` | `com_masteklimi` | Oracle HCM Functional Consultant |
| Max Life Insurance Company Limited | maxlifeinsurance.com | `successfactors` | `com_maxlifeins` | Manager |
| McCain Foods | mccain.com | `successfactors` | `com_mccainfood` | Governance and Operations Lead |
| Metso | metso.com | `successfactors` | `eu_C0001225248P` | Production Planning Engineer |
| Milann | milann.co.in | `successfactors` | `com_hcgprd` | Registered Nurse |
| Mindray | mindray.com | `successfactors` | `eu_Mindray` | Sales Manager |
| Mott MacDonald | mottmac.com | `successfactors` | `eu_MMPROD` | Talent Development Adviser |
| Munich Re | munichre.com | `successfactors` | `eu_mnchenerrc` | Compensation and Benefits Specialist |
| Narayana Hrudayalaya Limited | narayanahealth.org | `successfactors` | `com_narayanahr` | Medical Officer |
| NATIONAL GRID UK LIMITED | nationalgrid.com | `successfactors` | `com_natgridProd` | Financial Systems and ERP Director |
| NEC Corporation India Private Limited | nec.com | `successfactors` | `eu_neccorpo01P2` | DevOps Engineer |
| Nedspice Services B.V. | nedspice.com | `successfactors` | `eu_nedspiceP` | Electrical Maintenance and Utility Manager |
| Nespresso | nespresso.com | `successfactors` | `eu_nestleHRprdBX` | Observability Expert |
| Nestle Operational Services Worldwide SA | nestle.com | `successfactors` | `eu_nestleHRprdBX` | Sales Officer |
| NIIT | niit.com | `successfactors` | `com_niitlimite` | LMS Support Executive |
| NKT Cables Group A/S | nkt.com | `successfactors` | `eu_nktcablesg` | Document Controller |
| Nomura Holdings, inc. | nomura.com | `successfactors` | `com_nomurahold` | Group Tax |
| Nord Anglia Education Ltd | nordangliaeducation.com | `successfactors` | `eu_C0019617072P` | Secondary ICT Teacher |
| Nordex Group | nordex-online.com | `successfactors` | `eu_nordexse` | Training Coordinator |
| Norsk Hydro ASA | hydro.com | `successfactors` | `eu_norskhydro` | CRM Services Intern |
| Nouryon | nouryon.com | `successfactors` | `eu_nouryonP` | SAP Integration Analyst |
| Novo Nordisk | novonordisk.com | `successfactors` | `eu_novonordisk` | Clinical Data Scientist |
| NTT DATA Services | nttdata.com | `successfactors` | `com_4171430P` | Helpdesk Analyst |
| NUVOCO VISTAS CORPORATION LIMITED | nuvoco.com | `successfactors` | `com_nuvocovist` | Quality Shift In-Charge |
| Nuvoton Technology Corporation | nuvoton.com | `successfactors` | `com_nuvotontec` | Sales Representative |
| Oakridge International School | oakridge.in | `successfactors` | `eu_C0019617072P` | Teacher |
| Oberoi Realty |  | `successfactors` | `com_oberoireal` | Architecture Manager |
| Oerlikon | oerlikon.com | `successfactors` | `eu_OERLIKONP` | SAP Consultant |
| OIA Global | oiaglobal.com | `successfactors` | `com_oiagloball` | Operations Coordinator |
| Olam Agri | olamagri.com | `successfactors` | `com_olamglobal` | General Manager - Consolidation and Financial Reporting |
| OLAM INTERNATIONAL LTD | ofi.com | `successfactors` | `com_OLAMP1` | Internal Audit Manager |
| OMRON Corporation | omron.com | `successfactors` | `eu_omroncorpo` | Application Engineer |
| Orica Australia Pty Ltd | orica.com | `successfactors` | `com_oricaaus01` | Mechanical Technician |
| Orkla Foods Sverige AB | orkla.com | `successfactors` | `eu_C0001151091P` | Production Manager |
| Oxfam Novib | oxfamnovib.nl | `successfactors` | `eu_OxfamNovibP` | Programme Legacy and Knowledge Package Consultant |
| PayU |  | `successfactors` | `cloud_sap_payupaymen` | Software Engineer |
| PayU Digital Labs | payu.com | `successfactors` | `cloud_sap_payupaymen` | Business Solutions Manager |
| Pegasystems | pegasystems.com | `successfactors` | `com_pegasystem` | Architecture Engineer |
| Penguin Solutions | penguinsolutions.com | `successfactors` | `com_smartmodul` | Software Engineer |
| Phillips Carbon Black Ltd | pcblltd.com | `successfactors` | `com_phillipsca` | Lab Chemist |
| PI Industries |  | `successfactors` | `com_PI` | Research Scientist |
| Pitch Black Creative Canada Inc. | pitchblackcompany.com | `successfactors` | `com_artistesfo` | People and Culture Business Partner |
| Providence Global Center LLP | providence.in | `successfactors` | `com_providence` | IT Consulting Director |
| QualityAI | quality-ai.com | `successfactors` | `com_qualitesti` | Data Analyst |
| Rain Industries Limited | rain-industries.com | `successfactors` | `com_RAINCARBON` | Assistant General Manager - Logistics |
| RATIONAL Group | rational-online.com | `successfactors` | `eu_rationalag` | Technical Service Manager |
| Raychem RPG | rpggroup.com | `successfactors` | `com_C0014469929P` | Planning Executive |
| Reckitt Benckiser Corporate Services Ltd | reckitt.com | `successfactors` | `eu_reckittb01` | R&D Associate |
| ReNew Power Private Limited | renew.com | `successfactors` | `com_renewpower` | Assistant Manager |
| RHI Magnesita GmbH | rhimagnesita.com | `successfactors` | `eu_rhimagnesi` | Equipment Maintenance Technician |
| Rina S.p.A. | rina.org | `successfactors` | `eu_rinaspaP2` | Solar Photovoltaic Consultant |
| Rovensa | rovensa.com | `successfactors` | `eu_rovensa` | Sales Representative |
| Rubamin Private Limited | rubamin.com | `successfactors` | `com_rubaminpri` | Executive - Research and Development |
| Ruhrpumpen | ruhrpumpen.com | `successfactors` | `com_corporac07P2` | Corporate Counsel |
| Ryanair DAC | ryanair.com | `successfactors` | `eu_ryanairdac` | Aircraft Maintenance Engineer |
| SABIC | sabic.com | `successfactors` | `com_SABIC` | Electrical Maintenance Technician |
| SAP | sap.com | `successfactors` | `eu_SAP` | IT Technology Services Specialist |
| Sapiens | sapiens.com | `successfactors` | `eu_SapiensPRD` | Revenue Accountant |
| SBM Offshore Group | sbmoffshore.com | `successfactors` | `eu_singlebuoy` | Information Management Manager |
| Schaeffler Technologies AG & Co. KG | schaeffler.com | `successfactors` | `eu_schaeffler` | SAP S/4HANA Fullstack Developer |
| Schindler Group | schindler.com | `successfactors` | `eu_Schindler` | Layout and Sales Support |
| Schlumberger | career2.successfactors.eu | `successfactors` | `eu_Schlumberger` | Measurements Performance Live Specialist |
| Seagate Technology, LLC | seagatecareers.com | `successfactors` | `com_seagatetec` | Financial Modeling Analyst |
| Sealed Air Corporation | sealedair.com | `successfactors` | `com_sealedaircP1` | IT Business Analyst |
| SEEBURGER AG | seeburger.com | `successfactors` | `eu_seeburgera` | EDI Support |
| Sennheiser electronic SE & Co. KG | sennheiser.com | `successfactors` | `eu_sennheiser` | Business Development Manager |
| SES | ses.com | `successfactors` | `eu_SES` | SuccessFactors Application Analyst |
| Shangri-La Eros, New Delhi | shangri-la.com | `successfactors` | `com_ShangriLa` | Sous Chef |
| Shell Information Technology - Infineum | infineum.com | `successfactors` | `eu_C0000031504P` | HR Digital Leader |
| Shriram Farm Solutions Limited | shriramfarmsolutions.com | `successfactors` | `com_dcmshriramP` | Area Manager |
| Shyam Steel Industries Limited | shyamsteel.com | `successfactors` | `com_shyamsteel` | Melter |
| SIG Information Technology GmbH | sig.biz | `successfactors` | `eu_SIGProd` | Accounting Specialist |
| Simplot Company | simplot.com | `successfactors` | `com_simplotP` | Packing Operator |
| Sistemas Globales S.A | globant.com | `successfactors` | `com_globant` | AWS Data Engineer |
| SIX Group Services AG | six-group.com | `successfactors` | `eu_sixgroupse` | Software Engineer |
| Skyworks | skyworksinc.com | `successfactors` | `com_skyworks` | Firmware Engineering Director |
| SMR Automotive Systems India Ltd | smr-automotive.com | `successfactors` | `eu_smrautomot` | Executive |
| Sony Pictures Networks India | sonypicturesnetworks.com | `successfactors` | `com_sonypictur` | Ad Sales Manager |
| SPX Flow | spxflow.com | `successfactors` | `com_spxflowP` | Logistics Specialist |
| Standard Chartered | sc.com | `successfactors` | `eu_standardch` | Backend Engineer |
| STERIS | steris.com | `successfactors` | `com_steriscorpP` | Sales Executive |
| Sterlite Power Transmission Limited | sterlitepower.com | `successfactors` | `com_sterlitepo` | Civil Design Engineer |
| Straumann Group | straumann.com | `successfactors` | `eu_StraumannPROD` | Product Owner |
| Sun Chemical Corporation | sunchemical.com | `successfactors` | `com_sunchemical` | Packaging Technologist |
| Sun Pharmaceutical Industries Ltd | sunpharma.com | `successfactors` | `com_sunpharma` | Engineering Technician |
| Suntory Global Spirits | suntoryglobalspirits.com | `successfactors` | `com_C0017733204P` | Sourcing Manager |
| Super Micro Computer | supermicro.com | `successfactors` | `com_supermicro` | Sales Manager |
| SUSONITY | vibrantm.com | `successfactors` | `eu_merckgroup` | Analyst |
| Swiss Reinsurance Company Ltd. | swissre.com | `successfactors` | `eu_SwissRe` | Community Engagement Specialist |
| Syensqo | syensqo.com | `successfactors` | `eu_syensqo` | SAP EHS Expert |
| Syntax | syntax.com | `successfactors` | `com_C0002633795P` | System Analyst |
| Tata AIG General Insurance | tataaig.com | `successfactors` | `com_tataaiggen` | Channel Sales Manager |
| Tata AutoComp Systems Ltd. | tataautocomp.com | `successfactors` | `com_tataautoco` | Assistant Manager - Purchase |
| Tata Consulting Engineers Limited | tataconsultingengineers.com | `successfactors` | `com_tatacons02` | Contracts and Billing Specialist |
| Tata Consumer Products Limited | tataconsumer.com | `successfactors` | `eu_C0000175975P` | Territory Sales Executive |
| Tata Electronics Private Limited | tataelectronics.com | `successfactors` | `com_TEPLP` | IC Technology Development Program Management |
| Tata International Ltd | tatainternational.com | `successfactors` | `com_tataintern` | Direct Tax Manager |
| Tata Projects Limited | tataprojects.com | `successfactors` | `com_tataprojec` | Engineering Manager |
| Tata Starbucks Private Limited | starbucks.in | `successfactors` | `com_tatastarbucks` | Barista |
| TDB Trade Asset Management Company | tdbgroup.org | `successfactors` | `eu_ESATDB` | Consultant |
| TE Connectivity | te.com | `successfactors` | `com_TEConnect` | Product Development Engineer |
| TechnipFMC | technipfmc.com | `successfactors` | `com_fmctechno` | Accounts Payable Associate |
| Temasek Capital Management Pte Ltd | temasek.com.sg | `successfactors` | `eu_temasekcapP2` | Associate |
| Tenneco Automotive | tenneco.com | `successfactors` | `com_TennecoP1` | HR Manager |
| Teradyne Inc | teradyne.com | `successfactors` | `com_teradynein` | Software Quality Assurance Engineer |
| Terma | terma.com | `successfactors` | `eu_termaas` | Programme and PMO Support Officer |
| Terumo BCT, Inc. | terumobct.com | `successfactors` | `eu_terumobct` | Factory Buyer |
| Tetra Pak | tetrapak.com | `successfactors` | `eu_abtetrap01` | Recruitment Specialist |
| Teva | tevapharm.com | `successfactors` | `eu_1080030P` | Finance Operations Administrator |
| Teva Pharmaceuticals | teva.com | `successfactors` | `eu_1080030P` | Finance Operations Administrator |
| The George Institute for Global Health | georgeinstitute.org | `successfactors` | `eu_georgeinst` | Data Scientist |
| The Hershey Company | thehersheycompany.com | `successfactors` | `com_Hersheys` | Technical Executive |
| The Oberoi Group | oberoihotels.com | `successfactors` | `com_oberoireal` | Executive - Payments |
| The Tata Power Company Limited | tatapower.com | `successfactors` | `com_tatapower` | Team Member |
| Tractebel | engie.com | `successfactors` | `eu_engieinforP3` | Electrical Design Engineer |
| TSI, Inc. | tsi.com | `successfactors` | `com_tsi` | Field Service Engineer |
| TÜV Rheinland | tuv.com | `successfactors` | `eu_tvrheinlan` | Team Leader Scheme Management |
| TÜV SÜD South Asia Pvt. Ltd. | tuvsud.com | `successfactors` | `eu_tvsdag` | Business Development Manager |
| UNIDO | unido.org | `successfactors` | `eu_unidounind` | Gender Expert |
| UPL Limited | upl-ltd.com | `successfactors` | `com_upllimited` | Salesforce Analyst |
| Valvoline Global | valvolineglobal.com | `successfactors` | `com_vgpholding` | SAP SD Consultant |
| Vardhman Textiles | vardhman.com | `successfactors` | `eu_vardhmante` | Processing Maintenance Executive |
| VE Commercial Vehicles | vecv.in | `successfactors` | `com_vecommerci` | Dealership Sales Manager |
| Vistra Corporate Services (Sea) Pte. Ltd | vistra.com | `successfactors` | `eu_vistracorp` | Finance Controller |
| Vitesco Technologies GmbH | vitesco-technologies.com | `successfactors` | `eu_VitescoProd` | ASIC Digital Design Verification Engineer |
| Vodafone Idea Limited | vodafoneidea.com | `successfactors` | `eu_vodafoneinP2` | Territory Sales Manager |
| Voith GmbH | voith.com | `successfactors` | `eu_VOITH` | Project Planning Manager |
| Volkswagen | volkswagen.com | `successfactors` | `com_volkswag04` | Executive |
| Volkswagen Group |  | `successfactors` | `com_volkswag04` | IT Auditor |
| Volvo Car Corporation | volvocars.com | `successfactors` | `eu_C0000870892P` | Software Engineer |
| Volvo Group | volvogroup.com | `successfactors` | `eu_volvoinfor` | Product Owner |
| Voya India | voyaindia.com | `successfactors` | `com_vfislkglob` | Project Management Office Executive |
| W. L. Gore & Associates, Inc. | wlgore.com | `successfactors` | `com_WLGore` | SAP Integration Developer |
| Wacker Chemie AG | wacker.com | `successfactors` | `eu_wackerchem` | Assistant Manager - Sales |
| Westinghouse Electric Company, LLC | westinghousenuclear.com | `successfactors` | `com_WestinghouseP` | Electrician |
| Whirlpool of India | whirlpoolindia.com | `successfactors` | `com_whirlpoolc` | Supervisor in Training |
| Whirlpool of India Limited | india.whirlpool.in | `successfactors` | `com_whirlpoolc` | Manager, Software Engineering |
| William O'Neil India PVT. Ltd | daicompanies.com | `successfactors` | `com_dataanalys` | Accounts Payable Specialist |
| Wipro | wipro.com | `successfactors` | `eu_wiprolimitP2` | Developer |
| Wipro Enterprises Private Limited | wiproenterprises.com | `successfactors` | `com_wiproenter` | Quality Engineer |
| Worldline | worldline.com | `successfactors` | `eu_Worldline` | Consultant |
| WuXi Biologics | wuxibiologics.com | `successfactors` | `eu_wuxibiolog` | Head of WBSO |
| Würth Group | witglobal.net | `successfactors` | `eu_wrthitinteP2` | SAP SD Consultant |
| XPO Logistics | xpo.com | `successfactors` | `com_xpoenterprP` | Time and Attendance Specialist |
| Yash Technologies Private Limited | yash.com | `successfactors` | `com_yashtechnoP` | Analytics Team Lead |
| Yokohama India Pvt. Ltd |  | `successfactors` | `com_atctirespv` | Shift Engineer |
| Yusuf Alghanim & Sons W.L.L | alghanim.com | `successfactors` | `eu_yusufalgha` | Quality Assurance Engineer |
| Zalaris ASA | zalaris.com | `successfactors` | `eu_ZalarisProd` | Accounts Receivable |
| ZF Friedrichshafen AG | zf.com | `successfactors` | `eu_zffriedric` | Software Test Engineer |
| Zimmer Biomet | zimmerbiomet.com | `successfactors` | `com_zimmerin01` | Full Stack Engineer |

### Oracle — adapter exists, needs full careers URL (Fusion/Taleo) — 235 companies

`ats_type="oracle"` ← HiringCafe `source` in `oraclecloud`, `oraclepeoplesoft`, `taleo_careersection`, `taleo_rss`, `taleo_selectminds`. Do NOT add `board_token` directly — resolve to full careers URL first (see expansion plan Phase 3).

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| 56L LS India |  | `oraclecloud` | `ebwi.fa.us2` | Automation Engineer |
| ACI Worldwide | aciworldwide.com | `oraclecloud` | `ebwg.fa.us2` | Technical Program Manager |
| Adani Airport Holdings Ltd | adani.com | `oraclecloud` | `eibd.fa.em2` | Shift In Charge |
| Adani Power Ltd | adanipower.com | `oraclecloud` | `eibd.fa.em2` | FGD Operations and Maintenance Chemistry |
| ADI Global Distribution | adiglobal.com | `oraclecloud` | `ehtl.fa.us6` | Systems Integration Analyst |
| Akamai |  | `oraclecloud` | `fa-extu-saasfaprod1.fa.ocs` | Technical Account Manager |
| Akamai Career Site |  | `oraclecloud` | `fa-extu-saasfaprod1.fa.ocs` | Data Engineer |
| Al Shirawi Contracting Co. LLC | climaunoglobal.com | `oraclecloud` | `eijc.fa.em2` | Application Engineer |
| Alithya | alithya.com | `oraclecloud` | `effx.fa.ca2` | Manufacturing Consultant |
| Alithya Careers Site |  | `oraclecloud` | `effx.fa.ca2` | .NET/BI Analytics Developer |
| Alorica | alorica.com | `oraclecloud` | `fa-euxw-saasfaprod1.fa.ocs` | Team Manager |
| American Express | americanexpress.com | `oraclecloud` | `egug.fa.us2` | Software Engineer |
| AMMEGA |  | `oraclecloud` | `fa-eugx-saasfaprod1.fa.ocs` | Territory Sales Manager |
| Amneal Pharmaceuticals | amneal.com | `oraclecloud` | `hcfa.fa.us2` | Key Account Manager |
| Amplifon |  | `oraclecloud` | `efuf.fa.em2` | Audiologist |
| Anywhere | anywhere.re | `oraclecloud` | `ibmqjb.fa.ocs` | Associate Consultant |
| APLL External Career Site |  | `oraclecloud` | `hcut.fa.ap2` | Applications Development Specialist |
| Apps Associates Careers |  | `oraclecloud` | `ebdt.fa.us2` | Oracle Finance Consultant |
| Apraava Career Site |  | `oraclecloud` | `iaarcp.fa.ocs` | Contracts and Commercial Manager |
| Argano | argano.com | `oraclecloud` | `fa-eyau-saasfaprod1.fa.ocs` | Managing Consultant |
| Arup | arup.com | `taleo_selectminds` | `arupjobs.referrals` | Controls Engineer |
| Asian Development Bank | adb.org | `taleo_careersection` | `adb` | Project Assistant |
| AutoZone |  | `oraclecloud` | `egud.fa.us2` | Data Architect |
| Avient | avient.com | `oraclecloud` | `fa-eqzh-saasfaprod1.fa.ocs` | Order Management Specialist |
| BDO USA Experienced Career Site |  | `oraclecloud` | `ebqb.fa.us2` | Energy Portfolio Utility Specialist |
| Black Box Careers |  | `oraclecloud` | `eoje.fa.us2` | Desktop Support Engineer |
| BNY | bny.com | `oraclecloud` | `eofe.fa.us2` | Production Services Application Support |
| Bristlecone | bcone.com | `oraclecloud` | `iaagiz.fa.ocs` | SAP ABAP Developer |
| Burns & McDonnell | burnsmcd.com | `taleo_careersection` | `burnsmcdonn` | Electrical Designer |
| Calderys Career Opportunities | calderys.com | `oraclecloud` | `egmk.fa.us6` | QPC Manager |
| Catholic Relief Services |  | `oraclecloud` | `eipn.fa.us2` | Project Officer |
| Centric Consulting |  | `taleo_rss` | `phe.tbe_phe02_EDUV6K_38` | Agentic AI Architect |
| Chubb | www.chubb.com | `oraclecloud` | `fa-ewgu-saasfaprod1.fa.ocs` | Principal Engineer |
| Clean Harbors | cleanharbors.com | `oraclecloud` | `epyc.fa.us2` | Onboarding Associate |
| CLP |  | `oraclecloud` | `iabhtj.fa.ocs` | Corporate Affairs Executive |
| Cognizant | cognizant.com | `taleo_careersection` | `cognizant` | Architect |
| Coherent Corp. | coherent.com | `oraclecloud` | `hcwp.fa.us2` | SQL Server Database Administrator |
| Conduent |  | `oraclecloud` | `egua.fa.us2` | IT Project Management Consultant |
| CooperCompanies | coopersurgical.com | `oraclecloud` | `hcjy.fa.us2` | Design Quality Engineer |
| CORSAIR |  | `oraclecloud` | `edix.fa.us2` | Partnerships Specialist |
| CRS |  | `oraclecloud` | `eipn.fa.us2` | Humanitarian Operations Technical Advisor |
| CSB |  | `oraclecloud` | `iaamcp.fa.ocs` | Relationship Manager |
| CSB Career Site |  | `oraclecloud` | `iaamcp.fa.ocs` | Financial Institutions Group Manager |
| CSC | cscglobal.com | `oraclecloud` | `hczw.fa.us2` | Finance Business Partner |
| Cummins Inc. | cummins.com | `oraclecloud` | `fa-espx-saasfaprod1.fa.ocs` | Mechanical Maintenance Technician |
| Cyncly |  | `oraclecloud` | `fa-ewdg-saasfaprod1.fa.ocs` | AI/ML Specialist |
| Cyncly Careers |  | `oraclecloud` | `fa-ewdg-saasfaprod1.fa.ocs` | Content QA Engineer |
| Cytel |  | `oraclecloud` | `iblyjb.fa.ocs` | Statistical Programmer |
| Daimler Truck | daimlertruck.com | `oraclecloud` | `fa-exdu-saasfaprod1.fa.ocs` | IAM Principal Consultant |
| Dalmia Bharat Group | dalmiabharat.com | `oraclecloud` | `fa-ekwr-saasfaprod1.fa.ocs` | Territory Sales Manager |
| DAMAC |  | `oraclecloud` | `ejwe.fa.em2` | Finance Executive |
| Danske Bank |  | `oraclecloud` | `ejqi.fa.ocs.oraclecloud.eu` | Business Analyst |
| Datavail Infotech Pvt. Ltd. |  | `oraclecloud` | `eifn.fa.us6` | PeopleSoft Finance Functional Consultant |
| Dell | dell.com | `oraclecloud` | `iawmqy.fa.ocs` | Production and Assembly Representative |
| Devyani Food Industries Limited | creambell.com | `oraclecloud` | `rjcorphcm-iacbiz.fa.ocs` | Area Sales Manager |
| Devyani Food Industries Limited (DFIL) |  | `oraclecloud` | `rjcorphcm-iacbiz.fa.ocs` | Legal Assistant |
| Diebold Nixdorf |  | `oraclecloud` | `eeug.fa.us6` | Cash Management Coordinator |
| Digitide Solutions | digitide.com | `oraclecloud` | `iaceiz.fa.ocs` | Project Executive |
| DNV | dnv.com | `oraclecloud` | `ecyq.fa.em2` | Project Manager |
| DP World | dpworld.com | `oraclecloud` | `ehpv.fa.em2` | Cyber Engineering Automation Specialist |
| DT Global Asia Pacific | dt-global.com | `taleo_rss` | `lde.tbe_lde01_URSAUS_39` | Strategic Communications Manager |
| DTCC | dtcc.com | `oraclecloud` | `ebxr.fa.us2` | Software Development Engineer in Test |
| eClerx |  | `oraclecloud` | `fa-ewji-saasfaprod1.fa.ocs` | Analyst |
| eClerx Career Site |  | `oraclecloud` | `fa-ewji-saasfaprod1.fa.ocs` | Process Manager |
| Emerson | emerson.com | `oraclecloud` | `hdjq.fa.us2` | Product Design Engineer |
| Emirates NBD | emiratesnbd.com | `oraclecloud` | `fa-evlo-saasfaprod1.fa.ocs` | Infosec and Threat Assessment Manager |
| ENBD India Recruitment Team |  | `oraclecloud` | `fa-evlo-saasfaprod1.fa.ocs` | Technology Engineer |
| Engineering Projects (India) Limited | epi.gov.in | `oraclecloud` | `fa-epba-saasfaprod1.fa.ocs` | Corporate Finance Manager |
| Essar Group | essar.com | `oraclecloud` | `ekjy.fa.em2` | Assistant Manager - Mechanical |
| EXL Service | exlservice.com | `oraclecloud` | `fa-ewjt-saasfaprod1.fa.ocs` | Application Engineer |
| First Solar India |  | `oraclecloud` | `fa-esbv-saasfaprod1.fa.ocs` | Technician |
| Food and Agriculture Organization of the United Nations | fao.org | `taleo_careersection` | `fao` | Banana Value Chain Specialist |
| Ford | ford.com | `oraclecloud` | `efds.fa.em5` | Software Development Engineer |
| Fortinet | fortinet.com | `oraclecloud` | `edel.fa.us2` | Global Alliances Director |
| Fortinet Inc. |  | `oraclecloud` | `edel.fa.us2` | Professional Services Consultant |
| Fortis Healthcare |  | `oraclecloud` | `fa-ermg-saasfaprod1.fa.ocs` | Registrar |
| Fortive Careers |  | `oraclecloud` | `ejta.fa.us6` | AI-ML Engineer |
| Garrett Advancing Motion | garrettmotion.com | `oraclecloud` | `ehth.fa.em2` | Engineering |
| GEDU CAREERS |  | `oraclecloud` | `geduglobal-iabmbn.fa.ocs` | Graphic Designer |
| Gilbarco Veeder-Root | gilbarco.com | `taleo_careersection` | `vontier` | Solution Architect |
| Goldman Sachs Asset Management | gs.com | `oraclecloud` | `hdpc.fa.us2` | Global Data and Reporting Associate |
| Hanover Company | hanoverco.com | `taleo_rss` | `phg.tbe_phg03_HANORSLI_39` | Scheduling Department Manager |
| Hansen Technologies | hansencx.com | `oraclecloud` | `eoja.fa.ap1` | AI Platform Engineer |
| Hapag-Lloyd | hapag-lloyd.com | `oraclecloud` | `fa-etuy-saasfaeuraprod1.fa.ocs` | Cargo Operations Coordinator |
| Harmonic Inc. | www.harmonicinc.com | `oraclecloud` | `egmn.fa.us2` | Software Development Engineer |
| Hengstler | hengstler.com | `oraclecloud` | `ibwujb.fa.ocs` | Territory Manager |
| HERMES INDIA RETAIL AND DISTRIBUTORS PVT LTD |  | `oraclecloud` | `fa-eoic-saasfaprod1.fa.ocs` | Sales Associate |
| Hermès India Retail and Distributors Pvt Ltd |  | `oraclecloud` | `fa-eoic-saasfaprod1.fa.ocs` | Store Manager |
| Hill International | hillintl.com | `oraclecloud` | `hcib.fa.us2` | Project Director |
| Hill Minimal 112022 |  | `oraclecloud` | `hcib.fa.us2` | Quantity Surveyor |
| Hilton | hilton.com | `oraclecloud` | `efet.fa.us2` | Front Office Associate |
| Honeywell | honeywell.com | `oraclecloud` | `ibqbjb.fa.ocs` | Software Engineer |
| Honeywell Aerospace | honeywellaerospace.com | `oraclecloud` | `icfcjb.fa.ocs` | Systems Engineer |
| HOYA Vision Care | hoya.com | `oraclecloud` | `fa-esta-saasfaprod1.fa.ocs` | Accounts Receivable Assistant |
| HR |  | `oraclecloud` | `fa-epba-saasfaprod1.fa.ocs` | Project Execution Manager |
| Hyatt Place | hyatt.com | `taleo_careersection` | `hyatt` | Materials Assistant |
| IBS Career Portal |  | `oraclecloud` | `fa-etbm-saasfaprod1.fa.ocs` | Technical Architect |
| IBS Software |  | `oraclecloud` | `fa-etbm-saasfaprod1.fa.ocs` | Java Developer |
| Icertis |  | `oraclecloud` | `iaaviz.fa.ocs` | Software Engineer |
| IEEE | ieee.org | `taleo_careersection` | `ieee` | Global Tax Accountant |
| IHG Hotels & Resorts | ihgplc.com | `oraclecloud` | `fa-evax-saasfaprod1.fa.ocs` | Campaigns and Social Specialist |
| II-VI Aerospace & Defense \| Coherent |  | `oraclecloud` | `hcwp.fa.us2` | Data Science and AI Manager |
| IIMB |  | `oraclecloud` | `fa-erno-saasfaprod1.fa.ocs` | Librarian |
| IKS Health |  | `oraclecloud` | `eiyi.fa.ap1` | Business Intelligence Developer |
| Infiniti Retail Ltd | croma.com | `oraclecloud` | `fa-eryk-saasfaprod1.fa.ocs` | Sales Executive |
| Infoblox | infoblox.com | `oraclecloud` | `efpv.fa.us6` | Software Engineer |
| Infoblox Careers |  | `oraclecloud` | `efpv.fa.us6` | Treasury Analyst |
| Jefferies | jefferies.com | `oraclecloud` | `hdid.fa.us2` | Platform Reliability Engineer |
| JPMorgan Chase | jpmorganchase.com | `oraclecloud` | `jpmc.fa` | Product Marketing Associate |
| Jubilant Corporate |  | `oraclecloud` | `fa-exph-saasfaprod1.fa.ocs` | Finance Analyst |
| Jubilant FoodWorks | jubilantfoodworks.com | `oraclecloud` | `fa-exph-saasfaprod1.fa.ocs` | Cluster Manager |
| Kautex | textron.com | `taleo_careersection` | `textron` | Quality Engineer |
| Kearney | kearney.com | `taleo_careersection` | `atkcareers` | Summer Intern |
| Kent Careers |  | `oraclecloud` | `fa-emqh-saasfaprod1.fa.ocs` | SQS Engineer |
| KGSDP |  | `taleo_careersection` | `xoriant` | Software Engineer |
| KLDiscovery |  | `oraclecloud` | `ekug.fa.us6` | Infrastructure Operations Engineer |
| Kotak Mahindra Bank Ltd | kotak.bank.in | `oraclecloud` | `hcbt.fa.em2` | Grievance Redressal Team Leader |
| KPMG Global Services |  | `oraclecloud` | `ejgk.fa.em2` | Associate |
| Kroll | kroll.com | `oraclecloud` | `hcxs.fa.us2` | Analyst |
| Kuwait Food Co. AMERICANA L.L.C. |  | `oraclecloud` | `fa-eucb-saasfaprod1.fa.ocs` | Accountant |
| Legrand | legrand.com | `oraclecloud` | `iadugs.fa.ocs` | Credit Control Deputy Manager |
| Liquidity Services | liquidityservices.com | `oraclecloud` | `ebwi.fa.us2` | Mobile Application Developer |
| LogixHealth |  | `oraclecloud` | `fa-exql-saasfaprod1.fa.ocs` | Executive - Administration |
| Lucy Group |  | `oraclecloud` | `hdga.fa.em3` | Procurement Engineer |
| Mace | macegroup.com | `taleo_careersection` | `macecareers` | Structural Design |
| Majesco Software and Solutions India Private Limited | majesco.com | `oraclecloud` | `fa-emad-saasfaprod1.fa.ocs` | Engineer, Testing |
| Malomatia | malomatia.com | `oraclecloud` | `fa-eyhb-saasfaprod1.fa.ocs` | Full Stack Developer |
| Mashreq | mashreq.com | `oraclecloud` | `hcld.fa.em2` | Digital Marketing Manager |
| Mashreq Careers |  | `oraclecloud` | `hcld.fa.em2` | Financial Reporting |
| McDermott |  | `oraclecloud` | `edsv.fa.us2` | Expeditor |
| Medusind | medusind.com | `oraclecloud` | `medusind-ibzajb.fa.ocs` | Operations Coach |
| Medusind Careers |  | `oraclecloud` | `medusind-ibzajb.fa.ocs` | Operations Manager |
| Mercedes-Benz Research and Development India Private Limited | mercedes-benz-group.com | `taleo_careersection` | `tas-daimler` | Technical Program Manager |
| Metalsa Career Site |  | `oraclecloud` | `hcun.fa.us2` | Quality Specialist |
| Metalsa Structural Products, Inc. |  | `oraclecloud` | `hcun.fa.us2` | Process Engineering Specialist |
| Milestone Technologies | milestone.tech | `taleo_rss` | `phf.tbe_phf01_COVESTIC2_40` | Salesforce Developer |
| Mouser Electronics | mouser.com | `oraclecloud` | `eabw.fa.us2` | QA Team Lead |
| MUFG Pension & Market Services | mufg.com | `oraclecloud` | `hcmn.fa.ap1` | Data Modeller |
| Nabors Career Site |  | `oraclecloud` | `fa-eyem-saasfaprod1.fa.ocs` | QHSE Manager |
| NAMI |  | `oraclecloud` | `fa-eqgo-saasfaprod1.fa.ocs` | Relationship Manager |
| Nayara Energy | nayaraenergy.com | `oraclecloud` | `fa-escq-saasfaprod1.fa.ocs` | Category Buyer |
| Newmark |  | `oraclecloud` | `hdow.fa.us6` | Analyst |
| NMIMS Centre for Distance and Online Education | online.nmims.edu | `oraclecloud` | `fa-elxu-saasfaprod1.fa.ocs` | Coordinator - Assessment Quality Assurance |
| Nokia | nokia.com | `oraclecloud` | `fa-evmr-saasfaprod1.fa.ocs` | Systems Architect |
| NOV | nov.com | `oraclecloud` | `egay.fa.us6` | EDI Support Analyst |
| Novotech Global | novotech-cro.com | `oraclecloud` | `fa-euzi-saasfaprod1.fa.ocs` | Group Tax Manager |
| NSF |  | `oraclecloud` | `hcnz.fa.us2` | Auditor |
| Oceaneering |  | `oraclecloud` | `ebfr.fa.us2` | Pipeline Integrity Engineer |
| Ocwen Financial Solutions Private Limited | onitygroup.com | `oraclecloud` | `ebhz.fa.us2` | Associate, Servicing Transaction Management |
| Onity Group Inc. | onity.com | `oraclecloud` | `ebhz.fa.us2` | Data Scientist |
| onsemi | onsemi.com | `oraclecloud` | `hctz.fa.us2` | Analog Layout Engineer |
| Optum | optum.com | `taleo_careersection` | `uhg` | Marketing Operations and Sales Enablement Manager |
| Optum Rx | optumrx.com | `taleo_careersection` | `uhg` | Growth Marketing Enablement Specialist |
| Opus |  | `oraclecloud` | `iaaxiz.fa.ocs` | Data Engineer |
| Oracle | oracle.com | `oraclecloud` | `eeho.fa.us2` | Core Infrastructure Engineer |
| Orion Pharma | orion.fi | `oraclecloud` | `fa-esaq-saasfaprod1.fa.ocs` | Product Information Specialist |
| Pathways School Gurgaon | pathways.in | `oraclepeoplesoft` | `erp.pathways.in:8093/psc/HRPRDCC/EMPLOYEE/HRMS` | Psychology Teacher |
| Pathways School Noida | pathwaysnoida.edu.in | `oraclepeoplesoft` | `erp.pathways.in:8093/psc/HRPRDCC/EMPLOYEE/HRMS` | Special Education Teacher |
| Perficient | perficient.com | `oraclecloud` | `fa-etqd-saasfaprod1.fa.ocs` | Technical Consultant |
| Petrofac | petrofac.com | `taleo_selectminds` | `petrofac.referrals` | Electrical Manager |
| Phoenix |  | `oraclecloud` | `egeg.fa.em3` | Electrical Manager |
| Photon Career Site |  | `oraclecloud` | `fa-ertb-saasfaprod1.fa.ocs` | Integration Engineer |
| Pluckk | pluckk.in | `oraclecloud` | `ekjy.fa.em2` | Last Mile Executive |
| Quess Career site |  | `oraclecloud` | `fa-eumz-saasfaprod1.fa.ocs` | Recruitment Consultant |
| Quess Corp | quesscorp.com | `oraclecloud` | `fa-eumz-saasfaprod1.fa.ocs` | Recruiter |
| Quess Corp Limited |  | `oraclecloud` | `fa-eumz-saasfaprod1.fa.ocs` | Sourcing Executive |
| Resideo | resideo.com | `oraclecloud` | `ehtl.fa.us6` | Marketing Specialist |
| Rice Global India | rice.edu | `oraclecloud` | `emdz.fa.us2` | Associate Director of Graduate Recruitment |
| Samsonite | samsonite.com | `oraclecloud` | `ekkf.fa.em2` | Sales Promoter |
| SBI Card | sbicard.com | `oraclecloud` | `edox.fa.ap1` | Manager |
| Sensient Careers | sensient.com | `oraclecloud` | `eour.fa.us2` | Inside Sales Representative |
| Sensient Technologies |  | `oraclecloud` | `eour.fa.us2` | Application Technologist |
| Sherwin-Williams | sherwin-williams.com | `oraclecloud` | `ejhp.fa.us6` | Chemist |
| Sinch |  | `oraclecloud` | `iaings.fa.ocs` | Implementation Analyst |
| Sinch AB (publ) |  | `oraclecloud` | `iaings.fa.ocs` | Salesforce Developer I |
| Societe Generale Securities India | societegenerale.com | `taleo_careersection` | `socgen` | Analyst |
| Socomec | socomec.com | `oraclecloud` | `iahxgs.fa.ocs` | After Sales Officer |
| Solstice Advanced Materials |  | `oraclecloud` | `ibzdjb.fa.ocs` | Account Manager |
| SSAB |  | `oraclecloud` | `iaacwm.fa.ocs.oraclecloud.eu` | Design and Nesting Programmer |
| Startek |  | `oraclecloud` | `fa-evuf-saasfaprod1.fa.ocs` | Customer Support Representative |
| Stolt-Nielsen |  | `oraclecloud` | `eclo.fa.em2` | Travel and Expense Analyst |
| SVKM enterprize Career Site |  | `oraclecloud` | `fa-elxu-saasfaprod1.fa.ocs` | Librarian |
| SVKM’s College of Pharmacy, Shirpur |  | `oraclecloud` | `fa-elxu-saasfaprod1.fa.ocs` | Assistant Professor |
| Tata Capital | tatacapital.com | `oraclecloud` | `eofh.fa.em2` | Customer Service Executive |
| TATA Cummins Private Limited |  | `oraclecloud` | `fa-evwy-saasfaprod1.fa.ocs` | Electrician |
| Tata Tele Business Services | tatatelebusiness.com | `oraclecloud` | `fa-evmm-saasfaprod1.fa.ocs` | IT Infrastructure Operations Team Member |
| Technip Energies | ten.com | `oraclecloud` | `hcxg.fa.em2` | Offshore Structural Engineer |
| Tejas Networks |  | `oraclecloud` | `iablcp.fa.ocs` | Supply Chain Manager |
| Tetra Tech | tetratech.com | `taleo_selectminds` | `tetratech.referrals` | Investment Security Screening Expert |
| Texas Instruments | ti.com | `oraclecloud` | `edbz.fa.us2` | Layout Engineer |
| The Bridgespan Group | thebridgespan.org | `taleo_rss` | `phh.tbe_phh01_THEBRIDG12_40` | Associate Consultant |
| The Citco Group Limited | citco.com | `oraclecloud` | `fa-euxc-saasfaprod1.fa.ocs` | Operations Analyst |
| The Hackett Group |  | `oraclecloud` | `eeih.fa.us2` | Consultant |
| The Manitowoc Company | manitowoc.com | `oraclecloud` | `fda.fa.us1` | Operations Intern |
| The Manitowoc Company, Inc. |  | `oraclecloud` | `fda.fa.us1` | Field Service Technician I |
| The Phoenix Mills Limited | thephoenixmills.com | `oraclecloud` | `egeg.fa.em3` | Office Executive |
| Tradeweb Europe Limited |  | `oraclecloud` | `ecnf.fa.us2` | Data Analyst |
| Tradeweb Markets LLC |  | `oraclecloud` | `ecnf.fa.us2` | Market Operations Administrator |
| TriNet | trinet.com | `oraclecloud` | `fa-etgw-saasfaprod1.fa.ocs` | Content Management Consultant |
| TTEC | teletech.com | `taleo_careersection` | `teletech` | Principal Engineer |
| TWE Global Careers |  | `oraclecloud` | `ebpm.fa.us2` | Sales Manager |
| Uber | uber.com | `oraclecloud` | `iaziqy.fa.ocs` | Staff Backend Engineer |
| UFlex | uflexltd.com | `taleo_careersection` | `aa193` | Assistant Manager |
| UL Solutions |  | `oraclecloud` | `fa-eups-saasfaprod1.fa.ocs` | IT Technical Specialist |
| UL Solutions External Career Site |  | `oraclecloud` | `fa-eups-saasfaprod1.fa.ocs` | Learning and Development Specialist |
| UN Women |  | `oraclecloud` | `estm.fa.em2` | Protection Against Sexual Exploitation and Abuse and Sexual Harassment Analyst |
| UNFPA |  | `oraclecloud` | `estm.fa.em2` | Consultant |
| United Airlines | united.com | `taleo_careersection` | `ual-pro` | Automation Test Engineer |
| United Nations Development Programme | undp.org | `oraclecloud` | `estm.fa.em2` | Operations Associate |
| UnitedLex | unitedlex.com | `oraclecloud` | `ekkk.fa.us6` | Associate |
| Universal Sompo General Insurance | universalsompo.com | `oraclecloud` | `usgi-iacoiz.fa.ocs` | Relationship Manager |
| USGI Career Portal |  | `oraclecloud` | `usgi-iacoiz.fa.ocs` | Data Analytics |
| Varun Beverages Limited | varunbeverages.com | `oraclecloud` | `rjcorphcm-iacbiz.fa.ocs` | Customer Executive |
| Verint | www.verint.com | `oraclecloud` | `fa-epcb-saasfaprod1.fa.ocs` | SQL Server Database Administrator |
| Verisk |  | `oraclecloud` | `fa-ewmy-saasfaprod1.fa.ocs` | Software Engineer |
| Verisk Analytics | verisk.com | `oraclecloud` | `fa-ewmy-saasfaprod1.fa.ocs` | Software Architect |
| Vertiv | vertiv.com | `oraclecloud` | `egup.fa.us2` | Engineer |
| Vikram Solar | vikramsolar.com | `oraclecloud` | `iabqiz.fa.ocs` | Corporate Communication Manager |
| Virtusa |  | `taleo_selectminds` | `virtusapolaris.referrals` | AWS Node.js Developer |
| VSL Renewable Services Private Limited |  | `oraclecloud` | `iabqiz.fa.ocs` | Production Planning and Control Manager |
| vsl repower Career Site |  | `oraclecloud` | `iabqiz.fa.ocs` | Assistant Manager |
| Weatherford |  | `oraclecloud` | `fa-exmi-saasfaprod1.fa.ocs` | Electrical Design Engineer |
| Weatherford International | weatherford.com | `oraclecloud` | `fa-exmi-saasfaprod1.fa.ocs` | Procurement Engineer |
| Wesco | wescomfg.com | `oraclecloud` | `eklm.fa.us2` | Developer |
| Westin | marriott.com | `oraclecloud` | `ejwl.fa.us2` | Assistant Housekeeping Manager |
| Williams-Sonoma | williams-sonoma.com | `oraclecloud` | `ehac.fa.us6` | Infrastructure Engineering Operations Manager |
| WM |  | `oraclecloud` | `emcm.fa.us2` | Process Analyst |
| Wood | woodgroup.com | `oraclecloud` | `ehif.fa.em2` | Project Engineer |
| World Health Organization | who.int | `taleo_careersection` | `who` | Public Health Laboratory Consultant |
| WSP | wsp.com | `oraclecloud` | `emit.fa.ca3` | Assistant Engineer |
| WTW | wtwco.com | `oraclecloud` | `eedu.fa.em3` | Pension Administrator |
| Xoriant | xoriant.com | `taleo_careersection` | `xoriant` | Automation / Manual Testing Engineer |
| Yum! |  | `oraclecloud` | `eczd.fa.us2` | Finance Analyst |
| Zamil Industrial | zamilindustrial.com | `oraclecloud` | `elzx.fa.em2` | Integration and API Developer |
| Zensar |  | `oraclecloud` | `fa-etvl-saasfaprod1.fa.ocs` | Ignition Developer |

### iCIMS — adapter exists, needs careers-site URL — 135 companies

`ats_type="icims"` ← HiringCafe `source` in `icims`, `icims2`. Do NOT add `board_token` directly — resolve to full careers URL first (see expansion plan Phase 3).

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Acentra Health | acentra.com | `icims2` | `acentra` | Project Controls Analyst |
| Advanced Micro Devices, Inc | amd.com | `icims2` | `amd` | SoC Physical Design Engineer |
| AIT Worldwide Logistics | aitworldwide.com | `icims2` | `emea-external-aitworldwide` | Business Development Manager |
| Allvue Systems | allvuesystems.com | `icims2` | `allvuesystems` | AI and Knowledge Management Analyst |
| Annalect | omnicommedia.com | `icims2` | `annalect` | Investment Support Analyst |
| Annalect, Omnicom Media Group India Private Limited. | indiacareers.omnicomglobalsolutions.com | `icims` | `annalectomnicommediagroupindiaprivatelimited` | Media Investment Analyst |
| Aon Corporation | jobs.aon.com | `icims` | `aoncorporation` | Data Engineer |
| Applied Systems India Private Limited | www.appliedsystems.com | `icims2` | `globalcareers-appliedsystems` | Operations Engineer |
| Aptean | careers.aptean.com | `icims2` | `aptean` | Project Coordinator |
| Assembly Global | assemblyglobal.com | `icims2` | `careers-assemblyindia` | Analyst, Performance Marketing |
| Atlassian | atlassian.com | `icims2` | `atlassian` | Security Testing Engineer |
| AVI-SPL | careers.avispl.com | `icims2` | `avispl` | Project Engineer |
| AXA XL | axaxl.com | `icims2` | `axa` | Capital Actuary |
| Blackhawk Network | bhn.com | `icims2` | `blackhawknetwork` | Software Engineer |
| BlueCloud |  | `icims2` | `ibex` | AI/ML Architect |
| Booking Holdings | bookingholdings-coe.com | `icims` | `bookingholdings` | Recruitment Ops Specialist |
| Booking Holdings Inc. | bookingholdings.com | `icims2` | `workingatbooking` | Platform Engineer |
| Booking.com | booking.com | `icims2` | `workingatbooking` | Platform Engineer |
| Bruker | www.bruker.com | `icims2` | `internalcareers-bruker` | Accountant |
| Cactus Communications Services Pte. Ltd. | cactuslifesciences.com | `icims2` | `cactusglobal` | Project Manager |
| Catalyst Brands | catalystbrands.com | `icims2` | `jcpenney` | Merchandising Analyst |
| CDM Smith | careers.cdmsmith.com | `icims` | `cdmsmith` | Service Desk Specialist |
| Celanese International Corporation | celanese.com | `icims2` | `celanese` | Intern |
| Certara | certara.com | `icims2` | `certara` | Test Automation Engineer |
| Charles Schwab | schwab.com | `icims2` | `career-ind-schwab` | Software Development Manager |
| Consilio LLC | discoverready.com | `icims` | `consiliollc` | Solutions Architect |
| Cook Medical | cookgroup.com | `icims2` | `apac-cookmedical` | Territory Manager |
| Cordis | cordis.com | `icims2` | `cordis` | Supply Chain Operations and Planning Specialist |
| Cotiviti | www.cotiviti.com | `icims` | `cotiviti` | Implementation Consultant |
| Cvent | cvent.com | `icims2` | `cvent` | Cloud Operations Intern |
| DocuSign | www.docusign.com | `icims2` | `hubcareers-docusign` | Product Manager |
| EagleView | www.eagleview.com | `icims` | `eagleview` | Network Engineer |
| EchoStar | jobs.dish.com | `icims2` | `dish` | Engineer |
| Eide Bailly LLP | careers.eidebailly.com | `icims2` | `eidebailly` | Business Valuation Associate |
| Elektrobit Automotive GmbH | elektrobit.com | `icims` | `elektrobitautomotivegmbh` | VMware & Virtualization Engineer |
| Ellucian | careers.ellucian.com | `icims2` | `referral-ellucian` | AI Platform Analyst |
| Emmes Group | theemmesgroup.com | `icims2` | `emmes` | Biostatistician Manager |
| Enerpac Tool Group Corporation | enerpactoolgroup.com | `icims2` | `enerpac` | Buyer |
| Epsilon | epsilon.com | `icims2` | `publicisgroupe` | Software Engineer |
| Expleo | expleo.com | `icims2` | `expleo-jobs-apac` | Railway Signaling System and Software Technical Lead |
| FM Global | fm.com | `icims2` | `fm` | Claims Adjuster |
| Gallagher | jobs.ajg.com | `icims` | `gallagher` | Process Excellence Specialist |
| Granicus India | granicus.com | `icims` | `granicusindia` | Technical Support Representative |
| HealthEdge | www.healthedge.com | `icims2` | `wellframe-healthedge` | Software Engineer |
| Herbalife | herbalife.com | `icims2` | `careersen-herbalife` | Assistant Manager, Indirect Sourcing |
| Hines | www.karba.com | `icims` | `hines` | Real Estate Summer Analyst |
| HireRight | www.hireright.com | `icims2` | `careersintl-hireright1` | Researcher |
| Hyland | www.hyland.com | `icims2` | `careers-hyland` | Experience Designer |
| ibex | ibex.com | `icims2` | `ibex` | Data Engineer |
| iCIMS |  | `icims2` | `customer0` | Talent Systems Specialist |
| iCIMS Talent Acquisition |  | `icims2` | `customer0` | Product Manager |
| Ideagen | www.ideagen.com | `icims2` | `careers-ideagen` | React Native Developer |
| Indeed | indeed.com | `icims2` | `careers-indeed` | Client Success Specialist |
| Intercontinental Exchange Holdings, Inc. | ice.com | `icims2` | `ice` | Trade Operations Analyst |
| IPS-Integrated Project Services | ipsdb.com | `icims2` | `ipsdb` | Manager of Projects |
| JAGGAER | jaggaer.com | `icims2` | `incareers-jaggaer` | Principal Developer |
| JCPenney | jcpenney.com | `icims2` | `jcpenney` | Planning Analyst |
| Jhpiego | www.jhpiego.org | `icims2` | `jobs-jhpiego` | Program Officer |
| Kemin Industries | kemin.com | `icims2` | `careers-kemin` | Associate Manager, Financial Planning and Analysis |
| KEO International Consultants | keoic.com | `icims` | `keointernationalconsultants` | Electrical Engineer |
| Keysight Technologies, Inc. | jobs.keysight.com | `icims` | `keysighttechnologiesinc` | R&D Engineer |
| Kinaxis | kinaxis.com | `icims2` | `kinaxis` | HR Services Associate |
| Lennox International | www.lennoxinternational.com | `icims2` | `globalcareers-lennox` | Technical Consultant |
| Linesight | linesight.com | `icims` | `linesight` | Assistant Cost Manager |
| Lutron Electronics Co., Inc | lutron.com | `icims2` | `lutron` | CPS Representative |
| M.C. Dean, Inc | mcdean.com | `icims2` | `mcdean` | Project Leader |
| Mammoet | mammoet.com | `icims2` | `mammoet` | Accountant |
| MaxLinear | www.maxlinear.com | `icims2` | `careersintl-maxlinear` | Systems Integration & Test Engineer |
| McAfee | careers.mcafee.com | `icims2` | `mcafee` | Development Engineer |
| McGraw Hill LLC. | careers.mheducation.com | `icims2` | `mheducation` | Automation Engineer |
| Medallia | medallia.com | `icims2` | `medallia` | Product Management Director |
| Medpace | www.medpace.com | `icims2` | `careershub-medpace` | Clinical Research Project Coordinator |
| Medpace, Inc. | medpace.com | `icims2` | `medpace` | Clinical Project Coordinator |
| MSCI | msci.com | `icims2` | `msci` | Analytics Client Service Specialist |
| N-able | careers.n-able.com | `icims2` | `n-able` | Architect |
| Natural Resources Defense Council | nrdc.org | `icims2` | `careers-nrdc` | Litigation Intern |
| Nikkiso Clean Energy & Industrial Gases | nikkisoceig.com | `icims2` | `allcareers-nikkiso` | Process Engineer |
| Nikkiso Cryogenic Industries | nikkiso.com | `icims2` | `nikkiso` | Commissioning Engineer |
| Omnicom Global Solutions | omnicomglobalsolutions.com | `icims2` | `careers-omnicomglobalsolutions` | Finance Operations Associate |
| Omnicom Global Solutions India Private Limited | omnicom.com | `icims2` | `annalect` | Finance Operations Associate |
| One Identity | oneidentity.com | `icims2` | `careers-oneidentity` | Accounts Payable Advisor |
| OneAdvanced | careers.oneadvanced.com | `icims` | `oneadvanced` | Bid Manager |
| Options | publicisgroupe.com | `icims2` | `careers-publicisgroupetest` | Director |
| Orange Business | orange-business.com | `icims2` | `careers-orange` | Sales Development Representative |
| OSI Optoelectronics | osioptoelectronics.com | `icims2` | `intranet-osi-systems` | Process and Production Engineer |
| OSI Systems, Inc | osi-systems.com | `icims2` | `osi-systems` | Quality Assurance Engineer |
| Overview | www.axway.com | `icims2` | `careers-axway` | Software Security Engineer |
| Oxford Policy Management | opml.co.uk | `icims2` | `careers-opml` | Assistant Consultant |
| Panasonic Avionics Corporation | panasonic.aero | `icims2` | `napanasonic` | Inventory Coordinator |
| Paychex | paychex.com | `icims2` | `indiacareers-paychex` | Talent Development Manager |
| PepsiCo | pepsicojobs.com | `icims` | `pepsico` | Data Governance Manager |
| Phastar | phastar.com | `icims2` | `phastar` | Data Operations Programmer |
| Pinkerton | pinkerton.com | `icims2` | `pinkerton` | Security Support Executive |
| Planview Incorporated | planview.com | `icims2` | `planview` | GTM Engineer |
| PM Group | pmgroup-global.com | `icims2` | `pmgroup-global` | Accounts Payable Executive |
| PowerSchool |  | `icims2` | `careers3-powerschool` | Cloud Operations Engineer |
| Principal Global Services | principal.com | `icims2` | `principal` | Software Engineer |
| Prodapt | careers.prodapt.com | `icims2` | `prodapt` | SDWAN Service Assurance Engineer |
| Quest Software | quest.com | `icims` | `questsoftware` | HR Operations Advisor |
| Rambus | www.rambus.com | `icims2` | `careers-rambus` | Design Engineer |
| RealPage, Inc. | realpagepms.jibeapply.com | `icims2` | `realpagepms` | Application Architect |
| Riverbed Technology, Inc. | careers.riverbed.com | `icims` | `riverbedtechnologyinc` | Escalation Engineer |
| RM Education Limited | rmindia.co.in | `icims2` | `rmeducation` | Record-to-Report Accountant |
| RWS | www.rws.com | `icims2` | `careers-rws` | Developer |
| S&P Global Market Intelligence | spglobal.com | `icims2` | `spglobal` | Operations Specialist |
| Saft | saft.com | `icims2` | `careers-saft` | Mechanical Engineering Manager |
| SAS | www.sas.com | `icims` | `sas` | ServiceNow Developer |
| SBS | sbs-software.com | `icims2` | `careers-sbs` | DevOps Engineer |
| Schneider Electric | careers.se.com | `icims` | `schneiderelectric` | Senior Manager Commercial Finance |
| Seismic | seismic.com | `icims2` | `in-careers-seismic` | Software Engineer |
| SITA | www.sita.aero | `icims2` | `globalhub2-sita` | Software Developer |
| SITA Switzerland Sarl | careers.sita.aero | `icims` | `sitaswitzerlandsarl` | Project Financial Controller |
| SoftwareOne | www.softwareone.com | `icims2` | `softwareone` | Security Assurance Specialist |
| Spacelabs Healthcare | spacelabshealthcare.com | `icims2` | `intranet-osi-systems` | Quality Assurance Engineer |
| SSOE, Inc. | ssoe.com | `icims` | `ssoeinc` | Manager |
| StoneX Group | stonex.com | `icims2` | `stonex` | Staff Engineer/SDET |
| Susquehanna International Group, LLP | sig.com | `icims2` | `sig` | Platform Compliance Engineer |
| SymphonyAI | symphonyai.com | `icims2` | `jobs-symphonyai` | Platform Engineer |
| symplr | www.symplr.com | `icims` | `symplr` | Quality Engineer |
| SYSTRA | systra.com | `icims` | `systra` | Junior Engineer |
| TeKnowledge | everty.com | `icims2` | `ynvgroup` | WordPress Developer |
| The Company | www.granicus.com | `icims2` | `globalcareers-granicus` | Business Intelligence Architect |
| TRC Companies, Inc. | trccompanies.com | `icims2` | `trccompanies` | GIS Platform Engineer |
| Velocity Clinical Research, Inc. | velocityclinical.com | `icims` | `velocityclinicalresearchinc` | Regulatory Specialist |
| Ventra Health | ventrahealth.com | `icims2` | `globalcareers-ventrahealth` | Denials Supervisor |
| Viasat, Inc. | viasat.com | `icims2` | `viasat` | Site Reliability Engineer |
| Walter P Moore | www.walterpmoore.com | `icims2` | `careers-walterpmoore` | Tekla Support and Systems Technician |
| Waters Corporation | www.waters.com | `icims2` | `internationalcareers-waters` | Product Owner |
| What Drives Success | lennoxinternational.com | `icims2` | `employee-lennox` | Technical Consultant |
| Wipfli Advisory LLC | www.wipfli.com | `icims` | `wipfliadvisoryllc` | Engineer |
| WJCF | clintonhealthaccess.org | `icims2` | `careers-chai` | Program Manager |
| Xactly | xactlycorp.com | `icims2` | `xactlycorp` | UX Designer |
| Xactly Corporation | xactly.com | `icims2` | `xactlycorp` | Forward Deployed Engineer |
| Your job | www.indeed.jobs | `icims2` | `careers-indeed` | Product Manager |
| ZS | zs.com | `icims2` | `zs` | Business Technology Solutions Manager |

### Avature — adapter exists, needs portal URL — 36 companies

`ats_type="avature"` ← HiringCafe `source` in `avature`. Do NOT add `board_token` directly — resolve to full careers URL first (see expansion plan Phase 3).

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Bain & Company | bain.com | `avature` | `bain` | Analyst |
| Bloomberg | bloomberg.com | `avature` | `bloomberg` | Process Automation and Data Operations Team Leader |
| BMC Software | bmc.com | `avature` | `bmcrecruit` | Data Engineer |
| Bravura Solutions | bravurasolutions.com | `avature` | `bravura` | SOC Analyst |
| CBRE | cbre.com | `avature` | `cbreglobal` | Financial Analyst |
| DB Engineering & Consulting | db-engineering-consulting.com | `avature` | `jobs.deutschebahngroup.careers` | Talent Acquisition Manager |
| Delta Global Technology Hub |  | `avature` | `dth` | Software Development Engineer |
| DHL | dpdhlgroup.com | `avature` | `dpdhlgroup` | Business Development Executive |
| DHL Express | dhl.com | `avature` | `dpdhlgroup` | Tele-Sales Executive |
| Electronic Arts | www.ea.com | `avature` | `ea` | Security Engineer |
| Enel Green Power India Private Limited | jobs.enel.com | `avature` | `enel` | Planning & Control Specialist |
| Heartstream |  | `avature` | `heartstream` | Localization Engineer |
| IBM Consulting | ibm.com | `avature` | `ibmglobal` | Application Developer |
| IKEA | ikea.com | `avature` | `ikea` | Business Risk and Compliance Leader |
| Intralox | intralox.com | `avature` | `laitram` | Account Manager |
| Jacobs | careers.jacobs.com | `avature` | `jacobs` | Apprentice Engineer |
| Koch | kochind.com | `avature` | `koch` | MDM Analyst |
| L'Oréal | careers.loreal.com | `avature` | `loa` | Industrial Quality Manager |
| Laitram Machinery India | laitram.com | `avature` | `laitram` | Optimization Engineer/Account Manager |
| Lenovo | lenovo.com | `avature` | `lenovo` | Managed Service Desk Engineer |
| Macquarie Asset Management | macquarie.com | `avature` | `recruitment.macquarie.com` | Trade Settlement Operations Associate |
| MetLife | metlife.com | `avature` | `www.metlifecareers.com` | Software Platform Engineer |
| Mettler Toledo | mt.com | `avature` | `mt` | Collections Manager |
| Molex | molex.com | `avature` | `koch` | Quality Engineer |
| Qatar Airways | careers.qatarairways.com | `avature` | `careers.qatarairways.com` | Accountant |
| Qatar Airways Cargo | qrcargo.com | `avature` | `careers.qatarairways.com` | Cargo Customer Service Agent |
| Qatar Airways Group | qatarairways.com | `avature` | `qatarairways` | Cargo Operations Agent |
| Rohde & Schwarz India Private Limited | jobs.rohde-schwarz.com | `avature` | `rohdeschwarz` | Cybersecurity Specialist |
| Siemens Energy AB | siemens-energy.com | `avature` | `siemensenergy` | Group Manager, Electrical Systems |
| Siemens Healthcare Private Limited | siemens-healthineers.com | `avature` | `jobs.siemens.com` | Quality Engineer |
| Siemens Limited | siemens.com | `avature` | `jobs.siemens.com` | EHS Manager |
| Synopsys | synopsys.com | `avature` | `synopsys` | Staff Engineer |
| Tesco India | tesco.com | `avature` | `tesco` | Technical Programme Manager |
| TMF Group | tmf-group.com | `avature` | `tmf` | Client Accountant |
| United Nations Office for Project Services | unops.org | `avature` | `careers.unops.org` | Quality Assurance Associate |
| Xerox Holdings Corporation | xerox.com | `avature` | `xerox` | Intern |

### Phenom — adapter exists, needs careers root URL — 11 companies

`ats_type="phenom"` ← HiringCafe `source` in `phenompeople`. Do NOT add `board_token` directly — resolve to full careers URL first (see expansion plan Phase 3).

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Bureau Veritas | www.bureauveritas.com | `phenompeople` | `bureauveritas.phenompro.com` | FP&A Analyst |
| Conduent Business Services India LLP | conduent.com | `phenompeople` | `conduent.phenompro.com` | Accounting Services Associate |
| IDFC FIRST Bank | idfcfirst.bank.in | `phenompeople` | `idfcfirstbankcareers.phenompro.com` | Associate Relationship Manager |
| Kalpataru | kalpataru.com | `phenompeople` | `kalpataru.phenompro.com` | Safety Coordinator |
| Merck KGaA | merckgroup.com | `phenompeople` | `careers.emdgroup.com` | Accounting Business Partner |
| Open Text Technologies India Pvt Ltd | opentext.com | `phenompeople` | `careers.opentext.com` | Software Developer |
| Phenom People Pvt Ltd | careers.phenompeople.com | `phenompeople` | `bluetech.phenompro.com` | Product Development Engineer |
| Quest Global |  | `phenompeople` | `questglobal.phenompro.com` | CMMS Equipment Master |
| Route Mobile | proximusglobal.com | `phenompeople` | `proximus.phenompro.com` | Product Manager |
| Rubicon Research Limited | rubicon.co.in | `phenompeople` | `rubiconresearchlimited.phenompro.com` | Officer |
| Titan Company Limited | titan.co.in | `phenompeople` | `titan.phenompro.com` | SCM Executive |

---

## C. No adapter yet — needs new adapter (2093 companies, 71 sources)

Each subsection below is one HiringCafe `source` value. Per `AGENTS.md` §5 each needs a dedicated adapter (`backend/app/adapters/<ats>.py` + registration + interval + migration + probe) — budget 1–2 days per ATS. Preferred shortcut: single HiringCafe aggregator instead of 12+ adapters.

| HiringCafe `source` | Remaining | Example company / token |
|---|---|---|
| `zohorecruit` | 550 | 2Base Technologies / `2basetechnologies` |
| `workable` | 197 | 2070Health / `2070health` |
| `smartrecruiters` | 174 | AbbVie / `abbvie` |
| `adhoc` | 137 | Actinium Pharmaceuticals, Inc. / `actiniumpharma` |
| `bamboohr` | 98 | Access Now / `accessnow` |
| `teamtailor` | 90 | 3Shape / `3shape` |
| `jazzhr` | 68 | 3CLogic / `3clogic` |
| `rippling` | 67 | Accommodations Plus International / `accommodations-plus-international` |
| `dayforce` | 56 | Accuris / `accuris___candidateportal___en-us` |
| `eightfold` | 56 | Albemarle / `albemarle` |
| `ultipro` | 47 | Advarra / `adv1023avr_6051d363-03fe-4650-945e-f836306a8388` |
| `breezy` | 38 | 75F / `75f-apac` |
| `jobvite` | 38 | AArete / `aarete` |
| `pinpoint` | 36 | ADM Indicia / `admgroup` |
| `adp` | 33 | 11:11 Systems / `08f195f0-beb6-4255-a019-dbc8691ab8e8` |
| `recruitee` | 32 | Aftershoot / `aftershoot` |
| `csod` | 29 | Apollo Tyres Ltd / `apollotyres___1` |
| `dover` | 25 | Aerobotics7 / `22cf9f28-8406-4aca-af1d-64721c418007` |
| `freshteam` | 23 | Anaxee Digital Runners Pvt Ltd / `anaxee` |
| `personio` | 22 | 360T / `360t` |
| `sparkhire` | 21 | Aitech / `aitechsystems/88.004` |
| `hibob` | 17 | Aspire Pharma / `aspirepharma` |
| `trakstar` | 15 | BookMyShow / `bookmyshow` |
| `join` | 14 | Allocator One Group / `allocator` |
| `paylocity` | 13 | Associations International LLC / `da8e893b-19ea-4829-8420-b3fb56f7e332` |
| `recooty` | 13 | Aarna Systems Pvt Ltd / `aarna-systems-pvt-ltd` |
| `ripplehire` | 13 | 7-Eleven / `7-eleven-gsc___d8KPwFGBhDK6f7ajWTsc` |
| `paycom` | 12 | AVEVA DRUG DELIVERY SYSTEMS INC / `d6e5d048b8cb6dceda49d47ac70a226a` |
| `deel` | 11 | Cablex / `cablex` |
| `hirebridge` | 10 | Applause / `Applause` |
| `hrmdirect` | 9 | ABA360 / `aba360` |
| `pageup` | 9 | Crew - Shake Shack / `619` |
| `brassring` | 8 | A&O Shearman / `30147_5046` |
| `csodsaba` | 8 | Alexander Mann Solutions / `Q9VFK026203F3VBQBLOLO79V4` |
| `salesforce` | 8 | Allison Transmission / `d58000000domeeau___allisontransmission` |
| `gem` | 7 | Amelia Global Services Private Ltd / `soundhound` |
| `paycor` | 7 | AG&E Structural Engenuity / `8a7883c669b7efc80169c1351c0f0c44` |
| `adprecruiting` | 6 | Access Information Services / `accesscorpcareers` |
| `betterteam` | 5 | Addiction Pet Foods / `addictionpet` |
| `puck` | 5 | Avalara / `avalara` |
| `digitalrecruiters` | 4 | Decathlon / `joinus.decathlon.in` |
| `eploy` | 4 | AB Agri / `careers.abagri.com` |
| `fountain` | 4 | ACT / `ap-1.fountain.com___act` |
| `jobsoid` | 4 | Aimtron Electronics Pvt. Ltd. / `aimtron` |
| `njoyn` | 4 | CGI / `21001` |
| `saashr` | 4 | 4G Clinical / `6182998` |
| `applicantpro` | 3 | Mycronic USA / `mycronicusa` |
| `applicantstack` | 3 | CST Industries / `tanks` |
| `beesite` | 3 | Daimler Truck Innovation Center India Private Limited / `daimler-truck` |
| `gr8people` | 3 | AgileOne Global / `agileoneglobal___workgr8.com` |
| `jobscore` | 3 | Cendyn / `cendyn` |
| `acquiretm` | 2 | Amphenol Communications Solutions / `amphenol-tcs` |
| `factorial` | 2 | Opplane Portugal Unipessoal Lda / `opplane` |
| `hrsmart` | 2 | PSA BDP / `mua_bdpinternational` |
| `pereless` | 2 | Contiem / `contiem` |
| `polymer` | 2 | PinSec.Ai / `pinsec-ai` |
| `silkroad` | 2 | Graebel Companies, Inc. / `graebel` |
| `usagov` | 2 | Department of State / `ST-ST00` |
| `applicantpool` | 1 | Loparex LLC / `loparex` |
| `brightmove` | 1 | Congruex / `brt_35314_27155` |
| `earcu` | 1 | Menzies Aviation - Central Functions / `careers.jmenzies.com___aviation` |
| `gusto` | 1 | International Council for Helplines, Inc / `international-council-for-helplines-inc-225ef756-0967-4049-8d6a-5451fc6c37bd` |
| `harri` | 1 | Harri - India / `harriglobal` |
| `higherme` | 1 | Netchex / `69dfb615598eb` |
| `hireology` | 1 | The Ghoman Group / `chicagomarriottnorthwest` |
| `hiringthing` | 1 | Monetary Metals & Co / `monetary-metals-co` |
| `paradox` | 1 | Inspire Brands / `inspirebrands` |
| `peopleadmin` | 1 | University of North Carolina at Chapel Hill / `unc_com` |
| `talentlyft` | 1 | PXP Financial / `pxp-financial` |
| `ttcportals` | 1 | Syneos - Commercial & Clinical/Corporation / `syneoshealthcareers` |
| `virecruit` | 1 | Winston Taylor / `careers-winstontaylor-americas` |

### `zohorecruit` — 550 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| 2Base Technologies | 2basetechnologies.com | `zohorecruit` | `2basetechnologies` | Content Writing Intern |
| 367 Agency | 367.zohorecruit.in | `zohorecruit` | `367` | Performance Marketing Associate |
| 3D Department |  | `zohorecruit` | `sfumato` | 3D Motion Artist |
| AAJ Enterprises | aajenterprises.zohorecruit.in | `zohorecruit` | `aajenterprises` | Executive - Operations |
| Aaradhya Group | aaradhyagroup.in | `zohorecruit` | `aaradhyagroup` | Accountant |
| Abstrabit | abstrabit.zohorecruit.in | `zohorecruit` | `abstrabit` | Fullstack Engineer |
| Accounting Baba | accountingbaba.zohorecruit.com | `zohorecruit` | `accountingbaba` | Accounts Officer |
| Acowale | acowale.zohorecruit.in | `zohorecruit` | `acowale` | Full-Stack Engineer |
| Actlogica | actlogicaus.com | `zohorecruit` | `actlogicaus` | Product Engineer |
| Actlogica Solutions | actlogica.com | `zohorecruit` | `actlogicaus` | Product Finance Actuarial Manager |
| Acuvon Consulting | acuvon.com | `zohorecruit` | `acuvon` | Data Engineer |
| AddWeb Solution | addwebsolution.zohorecruit.in | `zohorecruit` | `addwebsolution` | System Administrator |
| Adequate Bookkeeping | adequatebookkeeping.zohorecruit.com | `zohorecruit` | `adequatebookkeeping` | Accounts Executive |
| Aditya Ram Properties | adityaramproperties.zohorecruit.in | `zohorecruit` | `adityaramproperties` | Marketing Manager |
| Adityaram Properties | adityaramproperties.com | `zohorecruit` | `adityaramproperties` | Projects Head |
| Advenser | advenser.zohorecruit.in | `zohorecruit` | `advenser` | MEP BIM Engineer |
| Aertsen | aertsen.in | `zohorecruit` | `aertsen` | Project Manager |
| Aertsen Living | aertsen.zohorecruit.in | `zohorecruit` | `aertsen` | Interior Designer |
| Agivant |  | `zohorecruit` | `agivant` | Backend Engineer |
| Agivant Technologies | agivant.com | `zohorecruit` | `agivant` | Engineering Director |
| Agnikul Cosmos | www.agnikulcosmos.com | `zohorecruit` | `agnikul` | RF Systems Engineer |
| AKMV Consultants | akmv.co.in | `zohorecruit` | `akmv` | Chief Operating Officer |
| Alien | thealien.zohorecruit.in | `zohorecruit` | `thealien` | Operations Intern |
| Alien Design | thealien.design | `zohorecruit` | `thealien` | Visual Designer |
| Alite Projects |  | `zohorecruit` | `aliteprojects` | WordPress Developer |
| AliteProjects | aliteprojects.zohorecruit.com | `zohorecruit` | `aliteprojects` | MERN Stack Developer |
| alliantgroup | alliantgroup.com | `zohorecruit` | `alliantgroup` | Associate |
| alliantgroup India Talent Pvt. Ltd | alliantgroup.zohorecruit.in | `zohorecruit` | `alliantgroup` | Energy Modeler |
| alliantgroup India Talent Pvt. Ltd. | alliantglobal.com | `zohorecruit` | `alliantgroup` | Security Operations Center Analyst |
| Altois | altois.zohorecruit.com | `zohorecruit` | `altois` | Pre-Sales Tele-Caller |
| Amardeep Aggregates | amardeepaggregates.zohorecruit.in | `zohorecruit` | `amardeepaggregates` | Lab Chemist |
| Amardeep Aggregates Pvt. Ltd. | amardeepaggregates.com | `zohorecruit` | `amardeepaggregates` | Production Supervisor |
| Amardeep Group |  | `zohorecruit` | `amardeepaggregates` | Technical Quality Officer |
| Ample Group | ample.co.in | `zohorecruit` | `ample` | HR Operations Apprentice |
| Ananant Systems | ananantsys.com | `zohorecruit` | `ananantsys` | Technical Program Manager |
| ANSATA | ansata.com | `zohorecruit` | `ansata` | Service Engineer |
| Anthrobyte | anthrobyte.com | `zohorecruit` | `anthrobyte` | AI Delivery |
| Anthrobyte AI Solutions |  | `zohorecruit` | `carrers` | AI DevOps Engineer |
| APCER Life Sciences | apcerls.com | `zohorecruit` | `apcerls` | Assistant Manager, Medical Information |
| APD | apd-india.zohorecruit.in | `zohorecruit` | `apd-india` | Administration Officer |
| Apistride | apistride.zohorecruit.in | `zohorecruit` | `apistride` | Full-Stack Developer |
| Appex Innovation | appexinnovation.com | `zohorecruit` | `appexinnovation` | Java Developer |
| Arc Consulting | arcconsulting.zohorecruit.com | `zohorecruit` | `arcconsulting` | Analyst - Operations Support |
| Arcedior | arcedior.zohorecruit.in | `zohorecruit` | `arcedior` | Accounts Manager |
| Ardex Endura | ardexendura.zohorecruit.in | `zohorecruit` | `ardexendura` | Executive - Sales |
| ArivuPro Academy | arivuproacademy.zohorecruit.in | `zohorecruit` | `arivuproacademy` | Graphic Designer |
| Arriello | arriello.com | `zohorecruit` | `arriello` | Drug Safety Project and Account Manager |
| Arrise | arrise.com | `zohorecruit` | `arrise` | Frontend Software Development Engineer |
| Art X Company | art-x.co | `zohorecruit` | `art-x` | Recruitment Associate |
| Arting Digital | artingdigital.zohorecruit.in | `zohorecruit` | `artingdigital` | Marketing Manager |
| Ascentis | ascentis.com | `zohorecruit` | `ascentis` | Assistant Manager - Cost & Quantity Surveying |
| Ashvita's | ashvitas.com | `zohorecruit` | `art-x` | Graphic Designer |
| Aspire Textiles LLP | aspiretextiles.zohorecruit.in | `zohorecruit` | `aspiretextiles` | Production Supervisor |
| At the Table |  | `zohorecruit` | `cloudnowtech` | Operations Manager |
| Atlanta Systems | atlantasys.zohorecruit.com | `zohorecruit` | `atlantasys` | Ecommerce Executive |
| Atlanta Systems Pvt. Ltd. | atlantasys.com | `zohorecruit` | `atlantasys` | Mechanical CAD Design Intern |
| Atlysone Multispeciality Hospital | atlysone.com | `zohorecruit` | `atlysone` | General Surgeon |
| Aurnex Tech |  | `zohorecruit` | `adequatebookkeeping` | Zoho Developer |
| Aurodo |  | `zohorecruit` | `aurodo` | 3D Animator |
| AutoPrint | autoprint.zohorecruit.com | `zohorecruit` | `autoprint` | Electrical Engineering Consultant |
| Autoprint Machinery Manufacturers | autoprint.net | `zohorecruit` | `autoprint` | Technical Engineer |
| AuxoAI | auxoai.zohorecruit.com | `zohorecruit` | `auxoai` | Data Engineer |
| Aviotron Aerospace Pvt. Ltd. | aerobay.in | `zohorecruit` | `aerobay` | STEM Lab Implementation Specialist |
| Axiamatic | axiamatic.zohorecruit.in | `zohorecruit` | `axiamatic` | Software Development Engineer in Test |
| Axis My India | axismyindia.org | `zohorecruit` | `axismyindia` | Operations Manager |
| Axis My India Limited | axismyindia.com | `zohorecruit` | `axismyindia` | Technical Project Delivery Manager |
| Axium Global | axiumglobal.com | `zohorecruit` | `axiumglobal` | Engineer Trainee |
| AXL Labs | axllabs.com | `zohorecruit` | `axllabs` | Graphic Designer |
| BALAJI RAILROAD SYSTEMS PVT LTD |  | `zohorecruit` | `barsyl` | Signaling and Telecommunication Designer |
| BARSiL | barsyl.in | `zohorecruit` | `barsyl` | Structural Engineer |
| Barsyl | barsyl.zohorecruit.in | `zohorecruit` | `barsyl` | Resource Executive |
| BB Insight | bbinsight.com | `zohorecruit` | `bbinsight` | Application Support Engineer |
| BCE Global Technology Centre | bceglobaltech.com | `zohorecruit` | `bceglobaltech` | Fullstack Developer |
| BDO EDGE India Private Limited | bdoedge.zohorecruit.in | `zohorecruit` | `bdoedge` | Consultant |
| Beforest Lifestyle Solutions Private Limited | beforest.co | `zohorecruit` | `beforest` | Field Officer |
| BeWild Produce Pvt. Ltd. | bewild.life | `zohorecruit` | `beforest` | Sales Partnerships Lead |
| Bharat Intelligence | bharatintelligence.zohorecruit.in | `zohorecruit` | `bharatintelligence` | Labour Sourcing Manager |
| Bhoodhan Agriventures Pvt. Ltd. | bhoodhan.com | `zohorecruit` | `aaradhyagroup` | Sales Officer |
| Bhumi | bhumi.ngo | `zohorecruit` | `bhumi` | Consultant |
| Biome |  | `zohorecruit` | `biome` | Graphic Designer |
| Blue Ocean Academy | blueoceanacademy.zohorecruit.com | `zohorecruit` | `blueoceanacademy` | Sales Associate |
| Blue Ocean Corporation | blueoceancorporation.zohorecruit.in | `zohorecruit` | `blueoceancorporation` | Sales Manager |
| Blue Ripples Technologies |  | `zohorecruit` | `blueripples` | Sales & Marketing Intern |
| BlueRipples | blueripples.zohorecruit.com | `zohorecruit` | `blueripples` | Power System Engineer |
| Blufig | blufig.com | `zohorecruit` | `blufig` | Growth Specialist |
| Bolt Cargo | boltcargo.com | `zohorecruit` | `boltcargo` | Deputy General Manager |
| Boltcargo |  | `zohorecruit` | `boltcargo` | Vice President |
| Bose |  | `zohorecruit` | `ample` | Demonstration Specialist |
| BoxUp Gifting | boxupgifting.zohorecruit.in | `zohorecruit` | `boxupgifting` | Business Development Manager |
| Brand Arbor |  | `zohorecruit` | `brandarbor` | Area Sales Manager |
| Brandarbor | brandarbor.zohorecruit.in | `zohorecruit` | `brandarbor` | Area Sales Manager |
| CADFEM | cadfem.zohorecruit.in | `zohorecruit` | `cadfem` | Application Engineer |
| Calibration |  | `zohorecruit` | `rndinstruments` | Calibration Engineer |
| Calpion Inc. | calpion.zohorecruit.in | `zohorecruit` | `calpion` | Python Developer |
| CAMP Systems | campsystems.com | `zohorecruit` | `campsystems` | Marketing Event Manager |
| CanKids KidsCan | cankidsindia.zohorecruit.in | `zohorecruit` | `cankidsindia` | Social Worker |
| Carry You | carryyou.zohorecruit.in | `zohorecruit` | `carryyou` | Data Entry Operator |
| Catalyx Space | catalyxspace.zohorecruit.in | `zohorecruit` | `catalyxspace` | CAE Simulation Engineer |
| CCTech | cctech.co.in | `zohorecruit` | `cctech` | Electrical Consultant |
| Cedar Group | cedar-consulting.com | `zohorecruit` | `cedar-consulting` | Human Resources Manager |
| Cedar Hill Capital | cedar-consulting.zohorecruit.com | `zohorecruit` | `cedar-consulting` | Associate |
| Centre for Entrepreneurship Development, Madhya Pradesh | mp.gov.in | `zohorecruit` | `cedmapindia` | Lab Technician |
| Chaosology | chaosology.zohorecruit.com | `zohorecruit` | `chaosology` | Piano Instructor |
| Chargeback Gurus | chargebackgurus.zohorecruit.com | `zohorecruit` | `chargebackgurus` | Network and Security Administrator |
| Chess Gaja | chessgaja.com | `zohorecruit` | `chessgaja` | Student Success Executive |
| ChiStats | chistats.zohorecruit.in | `zohorecruit` | `chistats` | AI Integration & Data Validation QA Analyst |
| City Greens | citygreens.co | `zohorecruit` | `citygreens` | Agronomist |
| CityGreens | citygreens.zohorecruit.in | `zohorecruit` | `citygreens` | F&V Intern |
| Climate Collective Foundation | climatecollective.zohorecruit.in | `zohorecruit` | `climatecollective` | Impact Analyst |
| Cloudester | cloudester.com | `zohorecruit` | `cloudester` | Data Analyst |
| CloudLIMS | cloudlims.com | `zohorecruit` | `cloudlims` | AI and Product Specialist |
| CloudNow Technologies | cloudnowtech.com | `zohorecruit` | `cloudnowtech` | HR Generalist |
| CMSS | engage.cmss.in | `zohorecruit` | `cmss-org60031353858` | Sales Executive |
| CodeNxt Web Technologies | codenxt.com | `zohorecruit` | `codenxt` | Intern |
| CodeStore Solutions | codestoresolutions.zohorecruit.com | `zohorecruit` | `codestoresolutions` | HR Trainee |
| Codezyng | codezyng.com | `zohorecruit` | `codezyng` | QA Engineer |
| Coditas | coditas.zohorecruit.in | `zohorecruit` | `coditas` | Dotnet Developer |
| Cognus Technology | cognustechnology.zohorecruit.in | `zohorecruit` | `cognustechnology` | Sales Intern |
| Collabrix Inc. | collabrix.zohorecruit.in | `zohorecruit` | `collabrix` | Product Analyst |
| Collective Newsroom | collectivenewsroom.com | `zohorecruit` | `collectivenewsroom` | Video Producer |
| Colruyt Group | colruytgroup.com | `zohorecruit` | `colruytgroup` | Consultant - Client Infrastructure |
| CometChat | cometchat.com | `zohorecruit` | `cometchat` | Marketing Intern |
| Concord Technologies |  | `zohorecruit` | `concordtech` | Site Incharge |
| Contour Education | contoureducation.zohorecruit.in | `zohorecruit` | `contoureducation` | HubSpot Developer |
| Corker | corker.zohorecruit.in | `zohorecruit` | `corker` | 3D Visualizer |
| CosmoChute | cosmochute.zohorecruit.in | `zohorecruit` | `cosmochute` | Avionics Engineer |
| Couchdeck | couchdeck.com | `zohorecruit` | `couchdeck` | Video Editor Intern |
| CRA | cra.zohorecruit.com | `zohorecruit` | `cra` | Design Engineer |
| CRA Energy |  | `zohorecruit` | `cra` | Commissioning and Installation Engineer |
| Crossbow Labs | crossbowlabs.com | `zohorecruit` | `crossbowlabs` | Full Stack Developer |
| CSC Travel | csc.zohorecruit.in | `zohorecruit` | `csc` | Application Support Executive |
| Cyber Square |  | `zohorecruit` | `baabte` | Head of Human Resources and Administration |
| Cyient DLM | cyientdlm.com | `zohorecruit` | `cyientdlm` | PCBA Inspection Operator |
| Daiviksoft | daiviksoft.com | `zohorecruit` | `daiviksoft` | Finance Manager |
| Datahash | datahash.com | `zohorecruit` | `datahash` | Technical Operations Engineer |
| Delveio | delveio.zohorecruit.in | `zohorecruit` | `delveio` | Sales Development Representative |
| Design & Fabrication |  | `zohorecruit` | `gsourcedata` | Graphic Designer |
| Design Department |  | `zohorecruit` | `sfumato` | Graphic Designer |
| DinePalace.com / Foodme.Mobi |  | `zohorecruit` | `fudme` | Sales Consultant |
| Discreet | discreet.in | `zohorecruit` | `discreet` | HR Intern |
| Divami | divami.com | `zohorecruit` | `divami` | Talent Acquisition Specialist |
| Doors Studio | doorsstudio.zohorecruit.com | `zohorecruit` | `doorsstudio` | Social Media Strategist |
| DotSolved | dotsolved.zohorecruit.in | `zohorecruit` | `dotsolved` | HRIS Analyst |
| DriveTech Intelligence | drivetech-ai.zohorecruit.in | `zohorecruit` | `drivetech-ai` | Project Engineer |
| DriveX | drivex.in | `zohorecruit` | `drivex` | Facility Manager |
| Duratuf | duratufproducts.com | `zohorecruit` | `duratufproducts` | Outbound Qualifier Executive |
| DuraTuf Products | duratufproducts.zohorecruit.com | `zohorecruit` | `duratufproducts` | Customer Experience Executive |
| Earthood | earthood.zohorecruit.in | `zohorecruit` | `earthood` | ESG Sustainability Intern |
| ECOG Core Technologies | ecogproducts.zohorecruit.in | `zohorecruit` | `ecogproducts` | Digital Creative Production |
| Ecog Products & Ecog Core Technologies Pvt. Ltd. | ecogproducts.com | `zohorecruit` | `ecogproducts` | HR Executive |
| Edmingle | edmingle.zohorecruit.com | `zohorecruit` | `edmingle` | Customer Support Executive |
| ekincare | ekincare.zohorecruit.in | `zohorecruit` | `ekincare` | Sales Development Representative |
| Eleven Int Service Private Limited | www.elevenispl.com | `zohorecruit` | `pubninja` | Video Editor |
| Eleven Int Service Pvt Ltd | elevenispl.com | `zohorecruit` | `pubninja` | Video Producer |
| ElevenX |  | `zohorecruit` | `exc` | Chief of Staff |
| ElevenX Capital |  | `zohorecruit` | `exc` | CFO |
| Elfonze |  | `zohorecruit` | `elfonze` | DevOps Engineer |
| Elfonze Technologies | elfonze.com | `zohorecruit` | `elfonze` | Oracle Fusion Tax Functional |
| Embark GCC | embarkgcc.zohorecruit.in | `zohorecruit` | `embarkgcc` | Strategic Account Manager |
| Embrace Software, Inc. | embracesoftwareinc.com | `zohorecruit` | `embracesoftwareinc` | Controller |
| ENERGDIVE | energ dive.com | `zohorecruit` | `itenmedia` | Media Sales Executive |
| Enking International | enkingint.com | `zohorecruit` | `enkingint` | Sales Coordinator |
| Ennuviz | ennuviz.com | `zohorecruit` | `ennuviz` | Account Manager |
| Escher Labs | escher-labs.com | `zohorecruit` | `escher-labs` | MEP BIM Modeller |
| EsyaSoft | esyasoft.zohorecruit.in | `zohorecruit` | `esyasoft` | Software Engineer |
| ETPL |  | `zohorecruit` | `esyasoft` | Engineer |
| Evnek Technologies | evnek.com | `zohorecruit` | `evnek` | AI/ML Architect |
| EXC Managed Services |  | `zohorecruit` | `exc` | Chief Operating Officer |
| Excelsoft Technologies |  | `zohorecruit` | `excelsoftcorp` | Social Media Executive |
| Excelsoft Technology | excelsoftcorp.zohorecruit.com | `zohorecruit` | `excelsoftcorp` | Project Manager |
| Execo | execo.zohorecruit.com | `zohorecruit` | `execo` | Migration Specialist |
| Exito | exito-e.zohorecruit.com | `zohorecruit` | `exito-e` | Inside Sales Executive |
| Facctum IT Solutions India Private Limited | zohorecruit.in | `zohorecruit` | `facctum` | Fenergo KYC SaaS Developer / Configuration Engineer |
| Famyo | famyo.zohorecruit.in | `zohorecruit` | `famyo` | PPC Manager |
| FCI | fci-ccm.zohorecruit.in | `zohorecruit` | `fci-ccm` | Production Support Engineer |
| FCI-CCM | fci-ccm.com | `zohorecruit` | `fci-ccm` | Assistant Manager, Production Support |
| Feathersoft | feathersoft.zohorecruit.com | `zohorecruit` | `feathersoft` | Data Engineer |
| FINANCE |  | `zohorecruit` | `vmsbgoa` | Equity Research Analyst |
| Finnovate | finnovate.zohorecruit.in | `zohorecruit` | `finnovate` | Business Development / Relationship Manager |
| Finovest Group | finovestgroup.zohorecruit.in | `zohorecruit` | `finovestgroup` | Business Development Manager |
| Fireblaze AI School | fireblazeaischool.zohorecruit.in | `zohorecruit` | `fireblazeaischool` | HR Operations |
| FIRKI |  | `zohorecruit` | `unborefoods` | Sales Executive |
| Fishman Healthcare | fishmanhealthcare.com | `zohorecruit` | `fishmanhealthcare` | Medical Representative |
| flydocs | flydocs.com | `zohorecruit` | `flydocs` | Associate Engineer |
| Fold Health |  | `zohorecruit` | `fold` | DevOps Engineer |
| Foodme / Dinepalace |  | `zohorecruit` | `fudme` | E-Commerce Sales Executive |
| Fortunize | fortunize.zohorecruit.in | `zohorecruit` | `fortunize` | Data Operations Associate |
| Fountain Forward |  | `zohorecruit` | `fountainforward` | Director of Growth Systems |
| Four Ess Synergy |  | `zohorecruit` | `fouresssynergy` | Accountant |
| Fouress Synergy | fouresssynergy.zohorecruit.com | `zohorecruit` | `fouresssynergy` | Purchase Coordinator |
| Freyr Energy | freyrenergy.com | `zohorecruit` | `freyrenergy` | Solar Installer |
| Fulcrum Digital | fulcrumdigital.com | `zohorecruit` | `fulcrumdigital` | GRC/SOC Analyst |
| Funai Consulting | funaiconsulting.zohorecruit.com | `zohorecruit` | `funaiconsulting` | GCP and Zoho Catalyst Engineer |
| GalaxEye | galaxeye.space | `zohorecruit` | `galaxeye-pranitgalaxeyespace` | Full Stack Engineer |
| Garden City Games | gardencity.games | `zohorecruit` | `gardencity` | Data Analyst |
| Gist Impact | gistimpact.com | `zohorecruit` | `gistimpact` | Data Engineer |
| Gladowl | gladowl.com | `zohorecruit` | `gladowl` | Content Lead |
| Global Market Insights | gminsights.com | `zohorecruit` | `gminsights` | Business Development Associate |
| Global Sports Travel | globalsportstravel.com | `zohorecruit` | `globalsports` | Sales Executive |
| Globals | globals.com | `zohorecruit` | `globals` | Offensive Security Researcher |
| Globals ITES Pvt Ltd | globals.zohorecruit.in | `zohorecruit` | `globals` | Pre-Sales Consultant |
| Gnapitech | gnapitech.zohorecruit.in | `zohorecruit` | `gnapitech` | Software Engineer |
| Good Shepherd International School | gsis.ac.in | `zohorecruit` | `gsis` | Chef de Partie |
| Grainville India Private Limited | grainvilleindia.com | `zohorecruit` | `grainville` | Executive Assistant |
| Great Place To Work | greatplacetowork.com | `zohorecruit` | `greatplacetowork` | Analyst, Sales Intelligence |
| Great Place To Work India | greatplacetowork.in | `zohorecruit` | `greatplacetowork` | Consultant |
| Green Living | greenliving.in | `zohorecruit` | `greenliving` | PPC Executive |
| Greendzine | greendzine.com | `zohorecruit` | `greendzine` | Product Development Intern |
| Gsource Technologies | gsourcedata.com | `zohorecruit` | `gsourcedata` | Digital Marketing Intern |
| Guardian Angel Homecare Pvt. Ltd. |  | `zohorecruit` | `gahc` | Patient Care Assistant |
| Guardian Capital |  | `zohorecruit` | `gcia` | Investment Operations Manager |
| Guardian Capital Investment Advisors | www.gcia.in | `zohorecruit` | `gcia` | Business Development Manager |
| Gurukul High School |  | `zohorecruit` | `baabte` | Computer Teacher |
| GXP Technologies | gxp-technologies-india.zohorecruit.in | `zohorecruit` | `gxp-technologies-india` | Field Service Engineer |
| GxP Technologies India | gxp-technologies-india.com | `zohorecruit` | `gxp-technologies-india` | Technical Manager |
| Haldren | haldren.com | `zohorecruit` | `haldren` | Client Consultant |
| Harvest International School |  | `zohorecruit` | `harvestinternationalschool` | Photographer |
| HD Supply | hdsupply.zohorecruit.in | `zohorecruit` | `hdsupply` | Software Engineer |
| HealthMinds | healthminds.zohorecruit.in | `zohorecruit` | `healthminds` | Marketing Chief of Staff |
| HealthMinds Consulting Private Limited | healthminds.easyapply.co | `zohorecruit` | `healthminds` | Graphic Designer |
| HECS | hecs.zohorecruit.com | `zohorecruit` | `hecs` | Architect |
| HelpAge India | helpageindia.org | `zohorecruit` | `helpageindia` | Project Coordinator |
| Hemfa |  | `zohorecruit` | `hemfa` | Administrative Officer |
| Heritage Foods | heritagefoods.zohorecruit.in | `zohorecruit` | `heritagefoods` | Anaplan Model Developer |
| Holistic Services | billedright.com | `zohorecruit` | `billedright` | Patient Caller |
| Hydromax Engineering | hydromaxengineering.zohorecruit.in | `zohorecruit` | `hydromaxengineering` | Account Assistant |
| Hykon India | hykonindia.zohorecruit.in | `zohorecruit` | `hykonindia` | Service Engineer |
| Hyosung T&D India | hyosungtndindia.zohorecruit.in | `zohorecruit` | `hyosungtndindia` | Structural Engineer |
| IBS Intelligence | ibsinternational.com | `zohorecruit` | `cedar-consulting` | Inside Sales and Presales Intern |
| ID Solutions India | idsolutionsindia.zohorecruit.in | `zohorecruit` | `idsolutionsindia` | Customer Relationship Intern |
| Idexmedia | idexmedia.com | `zohorecruit` | `idexmedia` | Graphic Designer |
| Ignatiuz | ignatiuz.zohorecruit.in | `zohorecruit` | `ignatiuz` | AI Infrastructure and Platform Architect |
| IITM C-DOT Samgnya Technologies Foundation | samgnya.zohorecruit.in | `zohorecruit` | `samgnya` | Optoelectronics Engineer |
| Incture | incture.com | `zohorecruit` | `incture` | SAP ABAP Developer |
| Incubyte | incubyte.com | `zohorecruit` | `incubyte-incubyte` | Business Analyst |
| Indbank Global Support Services Limited | igssl.co.in | `zohorecruit` | `igssl` | Field Sales Officer |
| Indea Design Systems | indeadesignsystems.com | `zohorecruit` | `indeadesignsystems` | Software Developer |
| IndeaDesignSystems | indeadesignsystems.zohorecruit.com | `zohorecruit` | `indeadesignsystems` | QA Intern |
| India Market Entry | indiamarketentry.com | `zohorecruit` | `indiamarketentry` | Area Sales Manager |
| Indian Designs | indian-designs.zohorecruit.in | `zohorecruit` | `indian-designs` | Merchandiser |
| Indovance | indovance.com | `zohorecruit` | `indovance` | Design Engineer |
| IndustryPro | industrypro.in | `zohorecruit` | `industrypro` | Service Engineer |
| Infarsight | infarsight.zohorecruit.in | `zohorecruit` | `infarsight` | UI/UX Engineer |
| Innefu Lab | innefu.zohorecruit.in | `zohorecruit` | `innefu` | Python Developer |
| Innefu Labs |  | `zohorecruit` | `innefu` | Product Manager |
| Innefu Labs Limited | innefu.com | `zohorecruit` | `innefu` | Manager |
| INNOW8 | innow8.com | `zohorecruit` | `innow8` | Operations and Inventory Management Executive |
| Inspiria Knowledge Campus | inspiria.zohorecruit.com | `zohorecruit` | `inspiria` | Assistant Professor |
| Institute for What Works to Advance Gender Equality (IWWAGE) | ifmrlead.zohorecruit.in | `zohorecruit` | `ifmrlead` | Policy Associate |
| Integrella | integrella.zohorecruit.in | `zohorecruit` | `integrella` | Software Engineer |
| Intelehealth | intelehealth.zohorecruit.com | `zohorecruit` | `intelehealth` | Tech Lead |
| INTELEX | intelexoutsourcing.zohorecruit.com | `zohorecruit` | `intelexoutsourcing` | Medical Interpreter |
| Intelex Outsourcing | intelexoutsourcing.com | `zohorecruit` | `intelexoutsourcing` | Interpreter |
| Intellisoft Technologies | intellisoft.zohorecruit.in | `zohorecruit` | `intellisoft` | SAP Basis Consultant |
| International Potato Center |  | `zohorecruit` | `cgiar` | Associate Scientist - Agronomist |
| International Potato Center (CIP) | cip.cgiar.org | `zohorecruit` | `cgiar` | Associate Scientist |
| Interscripts | interscriptsus.zohorecruit.com | `zohorecruit` | `interscriptsus` | International Voice Support Specialist |
| InterScripts Software Pvt. Ltd. |  | `zohorecruit` | `interscriptsus` | Associate Software Developer |
| Intglobal | intglobal.zohorecruit.in | `zohorecruit` | `intglobal` | Partner Growth Associate |
| Intuit Consultancy | intuitconsultancy.zohorecruit.com | `zohorecruit` | `intuitconsultancy` | Accounts & Finance Executive |
| Intuit Management Consultancy | intuitconsultancy.com | `zohorecruit` | `intuitconsultancy` | Tax Manager |
| Iridium Cloud Systems |  | `zohorecruit` | `iridiumsystems` | System Administrator |
| Iridium Systems | iridiumsystems.zohorecruit.in | `zohorecruit` | `iridiumsystems` | Engineering Manager |
| iServeU | iserveu.in | `zohorecruit` | `iserveu` | Customer Retention Executive |
| IT NVRON |  | `zohorecruit` | `fishmanhealthcare` | Graphic Designer |
| Italia Group | italiagroup.com | `zohorecruit` | `italiagroup` | Chemist |
| Iten Media | itenmedia.zohorecruit.in | `zohorecruit` | `itenmedia` | Sales Intern |
| iTENmedia | itenmedia.com | `zohorecruit` | `itenmedia` | Graphic Designer |
| JGC India | jgc.zohorecruit.in | `zohorecruit` | `jgc` | Building Engineer |
| Jungleworks | jungleworks.com | `zohorecruit` | `jungleworks` | Software Engineer |
| Kadel Labs | kadellabs.com | `zohorecruit` | `kadellabs` | MuleSoft Developer |
| Karomi | karomi.zohorecruit.in | `zohorecruit` | `karomi` | Implementation |
| Kasa Eshna Private Limited | kasaeshna.com | `zohorecruit` | `kasaeshna` | Full Stack Developer |
| Kavi Global | kaviglobal.com | `zohorecruit` | `kaviglobal` | Power BI Architect |
| Keystone Universe | keystoneuniverse.zohorecruit.com | `zohorecruit` | `keystoneuniverse` | Mathematics Teacher |
| KeyValue Software Systems | keyvalue.systems | `zohorecruit` | `keyvalue` | Prompt Engineer |
| Kheyti | kheyti.com | `zohorecruit` | `kheyti` | Customer Support-Farmer Success Associate |
| Koantek | koantek.com | `zohorecruit` | `koantek` | Data Scientist |
| Kores India | kores.in | `zohorecruit` | `kores` | HR Recruiter |
| KOTS Renting Pvt Ltd |  | `zohorecruit` | `kots` | Cluster Manager |
| Kraftshala | kraftshala.com | `zohorecruit` | `kraftshala` | AI Product Builder |
| Krishidhan Agri Business Pvt. Ltd. | krishidhanagro.in | `zohorecruit` | `aaradhyagroup` | Counter Sales Executive |
| Kriya NextWealth | kriyanxw.com | `zohorecruit` | `kriyanxw` | Application Support Analyst |
| KSBakers | ksbakers.zohorecruit.in | `zohorecruit` | `ksbakers` | Production Executive |
| Kshema General Insurance Limited | kshema.zohorecruit.in | `zohorecruit` | `kshema` | Learning and Development General Manager |
| Kumaran Systems | kumaran.com | `zohorecruit` | `kumaran` | Full Stack Developer |
| Kushal's Fashion Jewellery | kushals.com | `zohorecruit` | `kushals` | Style Associate |
| Ladybird Web Solution Pvt. Ltd. | faveohelpdesk.com | `zohorecruit` | `faveohelpdesk` | Digital Marketing Specialist |
| Latent Bridge | latent-bridge.zohorecruit.in | `zohorecruit` | `latent-bridge` | AI/ML Engineer |
| LatentBridge |  | `zohorecruit` | `latent-bridge` | AI Architect |
| LeapSurge | leapsurge.zohorecruit.in | `zohorecruit` | `leapsurge` | Business Intelligence Developer |
| Leegality | leegality.com | `zohorecruit` | `leegality` | DevOps Engineer |
| LeewayHertz | leewayhertz.zohorecruit.in | `zohorecruit` | `leewayhertz` | Data Engineer |
| Lend A Hand India | lendahandindia.org | `zohorecruit` | `lendahandindia` | Assistant Manager |
| LevelX Micro | levelxmicro.zohorecruit.in | `zohorecruit` | `levelxmicro` | Digital Marketing Executive |
| Liabilities |  | `zohorecruit` | `igssl` | Executive |
| LINC | linceducation.com | `zohorecruit` | `linceducation` | Online Facilitator |
| Liquidnitro Games | liquidnitro.zohorecruit.in | `zohorecruit` | `liquidnitro` | Game Designer |
| Loom Solar | loomsolar.com | `zohorecruit` | `loomsolar` | Contact Center Manager |
| Lotus Technicals | lotustechnicals.zohorecruit.in | `zohorecruit` | `lotustechnicals` | Engineer |
| LSD Open | lsdopen.com | `zohorecruit` | `lsdopen` | Platform Engineer |
| Ludic | ludic.co | `zohorecruit` | `ludic` | HR Generalist |
| M-Agro | m-agro.zohorecruit.in | `zohorecruit` | `m-agro` | Agri Marketing Executive |
| M.E.P. Centre | mepcentre.zohorecruit.in | `zohorecruit` | `mepcentre` | Electrical Designer |
| MacTech |  | `zohorecruit` | `mactech` | Sales Engineer |
| MacTech Engineers | career.mactechenginerers.com | `zohorecruit` | `mactech` | Driver |
| Make Your Own Perfume | myop.in | `zohorecruit` | `careers.myop.in` | Sales Executive |
| Makers' Muse | makersmuse.in | `zohorecruit` | `makersmuse` | Sales Professional |
| Mangalassery Agro Chemicals Pvt. Ltd. | m-agro.in | `zohorecruit` | `m-agro` | Agri Marketing Executive |
| Marketing |  | `zohorecruit` | `whitelion1` | Video Editor |
| MASS Tech LLC | masstechllc.com | `zohorecruit` | `masstechllc` | Deployment Lead |
| Medical Departures Inc. | medicaldepartures.com | `zohorecruit` | `medicaldepartures` | Talent Acquisition Specialist |
| MEIDEFSEC |  | `zohorecruit` | `meidefsec` | Technical Business Development & Program Coordination Associate |
| Meinigar Technologies Pvt Ltd | stockarea.zohorecruit.in | `zohorecruit` | `stockarea` | Warehouse Supervisor |
| MEL Systems and Services Limited | melss.com | `zohorecruit` | `melss` | Sales Manager |
| Metalegal |  | `zohorecruit` | `metalegal` | Legal Content Writer |
| Metalegal Advocates | metalegal.zohorecruit.in | `zohorecruit` | `metalegal` | Associate |
| MicroSave Consulting | microsave.net | `zohorecruit` | `microsave` | Associate Manager |
| Miles Education | mileseducation.zohorecruit.com | `zohorecruit` | `mileseducation` | Content Strategist |
| mindZvue Technologies Pvt. Ltd. | mindzcloud.zohorecruit.com | `zohorecruit` | `mindzcloud` | Head of Finance |
| Mobavenue | mobavenue.com | `zohorecruit` | `mobavenue` | Executive - Social Media |
| Model Institute of Engineering & Technology (MIET), Jammu | mietjammu.zohorecruit.in | `zohorecruit` | `mietjammu` | Professor of Practice |
| Moeen Global Talent | jobify.zohorecruit.com | `zohorecruit` | `jobify` | Business Development Representative |
| Money Forward | moneyforward.zohorecruit.in | `zohorecruit` | `moneyforward` | Fullstack Engineer |
| Moring |  | `zohorecruit` | `moring` | AI Engineer |
| Moring.ai | moring.ai | `zohorecruit` | `moring` | Social Media Manager |
| MostEdge | aboveo.zohorecruit.in | `zohorecruit` | `aboveo` | POD Supervisor |
| MSC Transformers | msctransformers.zohorecruit.in | `zohorecruit` | `msctransformers` | Testing Engineer |
| Multiplier AI | multiplierai.com | `zohorecruit` | `multiplierai` | MIS Executive |
| MyComms Global |  | `zohorecruit` | `mycommsglobal` | PR Intern |
| MyOperator | myoperator.com | `zohorecruit` | `myoperator` | Front Deployed Engineer |
| MySIPonline |  | `zohorecruit` | `cognustechnology` | Sales Executive |
| National Payments Corporation of India |  | `zohorecruit` | `npci` | Deputy Incharge |
| National Skill Development Corporation | nsdcindia.org | `zohorecruit` | `nsdcindia` | Analyst |
| NBSSPL | nbsspl.zohorecruit.in | `zohorecruit` | `nbsspl` | Accountant |
| Newgenmax | newgenmax.zohorecruit.com | `zohorecruit` | `newgenmax` | Customer Support Executive |
| Nexivo Consulting | nexivo.co | `zohorecruit` | `nexivo` | Inside Sales Executive |
| NextGen Business Support Services Pvt. Ltd. |  | `zohorecruit` | `nbsspl` | Executive Assistant |
| NextGen Group |  | `zohorecruit` | `accountsnextgen` | Head of Sales and Marketing |
| nHRMS | nhrms.com | `zohorecruit` | `nhrms` | Solution Architect |
| NIIT Foundation | niitfoundation.org | `zohorecruit` | `niitfoundation` | Center Head |
| Nirmitee | nirmitee.com | `zohorecruit` | `nirmitee` | Guidewire Integration Developer |
| Nirmitee.io | nirmitee.zohorecruit.in | `zohorecruit` | `nirmitee` | QA Engineer |
| Nivetha E-Academy |  | `zohorecruit` | `newgenmax` | Growth Manager |
| NoPo Nanotechnologies | noponano.com | `zohorecruit` | `noponano` | Principal Engineer |
| Noponano | noponano.zohorecruit.in | `zohorecruit` | `noponano` | Engineer |
| Notion Press | notionpress.com | `zohorecruit` | `notionpress` | Technical Project Manager |
| NotionPress | notionpress.zohorecruit.com | `zohorecruit` | `notionpress` | Social Media Content Creator |
| Nova Benefits | novabenefits.zohorecruit.in | `zohorecruit` | `novabenefits` | Demand Generation |
| NPCI | npci.org.in | `zohorecruit` | `npci` | Associate |
| NPCI International Payments Limited | nipl.com | `zohorecruit` | `npci` | Product Design Associate |
| Nucleus Software | nucleussoftware.com | `zohorecruit` | `nucleussoftware` | Test Lead |
| null | null.domain | `zohorecruit` | `cakrishna` | CA Article |
| NurtureSpark | nurturespark.zohorecruit.com | `zohorecruit` | `nurturespark` | Zoho Widget Developer |
| Nvron Life Science Limited | nvronlifescience.com | `zohorecruit` | `nvronlifescience` | Videographer and Video Editor |
| Om Ak Solutions |  | `zohorecruit` | `omaksolutions` | AI Video Content Creator |
| One Touch Comsec |  | `zohorecruit` | `discreet` | Area Sales Manager |
| OptimoShell Global Private Limited | omaksolutions.zohorecruit.in | `zohorecruit` | `omaksolutions` | Manual Tester |
| Osmos | osmos.ai | `zohorecruit` | `osmos` | iOS Developer |
| Overqualified Housewives | overqualifiedhousewives.zohorecruit.in | `zohorecruit` | `overqualifiedhousewives` | Operations Manager |
| Padink Engineering |  | `zohorecruit` | `padink` | Design Site Engineer |
| Pakka |  | `zohorecruit` | `pakka` | Learning and Development Head |
| Pakka Limited | pakka.com | `zohorecruit` | `pakka` | Intern |
| Parikshak.ai | parikshak.ai | `zohorecruit` | `edunova` | Talent Acquisition Intern |
| Peepul | peepulindia.org | `zohorecruit` | `peepulindia` | Finance Advisor |
| Peerless Financial Products Distribution Limited | peerlessfpd.com | `zohorecruit` | `peerless` | Business Development Manager |
| Perry Street Software | perrystreet.com | `zohorecruit` | `perrystreet` | UI Designer |
| Phensa Engineering | phensaengineering.zohorecruit.in | `zohorecruit` | `phensaengineering` | HVAC Designer |
| Pierian Services | pierianservices.com | `zohorecruit` | `pierianservices` | Accounts Manager |
| Plastics For Change India Foundation | plasticsforchange.org | `zohorecruit` | `plasticsforchange` | Operations Driver |
| PlaySimple | playsimple.com | `zohorecruit` | `playsimple` | QA Engineer |
| PlaySimple Games | playsimple.zohorecruit.in | `zohorecruit` | `playsimple` | Product Manager |
| Plum | teampureplay.zohorecruit.in | `zohorecruit` | `teampureplay` | Management Trainee |
| Poornatha | poornatha.zohorecruit.in | `zohorecruit` | `poornatha` | Internship |
| PowerBridge | powerbridge.org | `zohorecruit` | `powerbridge-org60025989370` | Associate Sales Executive |
| Priority Commerce | prioritycommerce.zohorecruit.com | `zohorecruit` | `prioritycommerce` | Analyst |
| Profitroom |  | `zohorecruit` | `profitroom` | Marketing Executive |
| Prolifics Corporation Limited | prolifics.com | `zohorecruit` | `prolifics` | Marketing and Software Coordinator |
| Prop Solutions 4U | propsolutions4u.zohorecruit.in | `zohorecruit` | `propsolutions4u` | MIS Manager |
| PropSolutions4U | propsolutions4u.com | `zohorecruit` | `propsolutions4u` | Front Desk and Administrative Executive |
| PSC Biotech | pscbiotech.com | `zohorecruit` | `biotech` | Validation Engineer |
| QBrainX | qbrainx.zohorecruit.com | `zohorecruit` | `qbrainx` | Software Engineer |
| Quadeye | quadeye.zohorecruit.in | `zohorecruit` | `quadeye` | Linux Engineer |
| Quatrro Business Support Solutions Private Limited | quatrrobss.com | `zohorecruit` | `quatrrobss` | Manager, Finance and Accounting |
| QUEST Alliance | questalliance.org | `zohorecruit` | `questalliance` | Program Associate |
| Quicko | quicko.zohorecruit.in | `zohorecruit` | `quicko` | Social Media Analyst |
| Qure.ai | qure.ai | `zohorecruit` | `qure` | Program Coordinator |
| R&D Instrument Services | rndinstruments.zohorecruit.in | `zohorecruit` | `rndinstruments` | Calibration Engineer |
| RAKwireless | rakwireless.com | `zohorecruit` | `rakwireless` | Embedded Systems Engineer |
| Rama Mining Tools Private Limited | rminingtools.zohorecruit.in | `zohorecruit` | `rminingtools` | Assistant Manager |
| Rayda | rayda.zohorecruit.com | `zohorecruit` | `rayda` | Data Analyst |
| Re'equil | reequil.com | `zohorecruit` | `reequil` | Assistant Manager |
| Recode Solutions | recodesolutions.zohorecruit.in | `zohorecruit` | `recodesolutions` | AI/ML Architect |
| Reequil |  | `zohorecruit` | `reequil` | Visual Designer |
| Regolith Ecological Solutions |  | `zohorecruit` | `beforest` | Project Architect |
| Regolith Ecological Solutions Pvt. Ltd. | beforest.in | `zohorecruit` | `beforest` | Site Supervisor |
| retailcloud | retailcloud.com | `zohorecruit` | `retailcloud` | Java Architect |
| Rigel Networks | rigelnetworks.com | `zohorecruit` | `rigelnetworks` | Android Developer |
| Rioconn | rioconn.zohorecruit.in | `zohorecruit` | `rioconn` | Business Development Executive |
| RMCL-Branches |  | `zohorecruit` | `rootsindia` | Territory Service Executive |
| RMCL-FAC | rootsindia.zohorecruit.in | `zohorecruit` | `rootsindia` | Associate Head EHS |
| RMCL-HO |  | `zohorecruit` | `rootsindia` | Robotics Engineer |
| Robro Systems | robrosystems.com | `zohorecruit` | `robrosystems` | Social Media Intern |
| Robro Systems Pvt. Ltd. | www.robrosystems.com | `zohorecruit` | `robrosystems` | Engineer Trainee |
| Rocket Learning | rocketlearning.org | `zohorecruit` | `rocketlearning` | District Coordinator |
| Roundglass | roundglass.zohorecruit.com | `zohorecruit` | `roundglass` | Procurement Associate |
| Royal Cyber | royalcyber.com | `zohorecruit` | `royalcyber` | Architect |
| RRD |  | `zohorecruit` | `rrd` | Document Specialist |
| RRD GO Creative | rrd.com | `zohorecruit` | `rrd` | Document Specialist |
| Saahas | saahas.org | `zohorecruit` | `saahas` | Field Research Intern |
| Saajha | saajha.org | `zohorecruit` | `saajha` | Fundraising Manager |
| Saburi Ply | saburiply.zohorecruit.in | `zohorecruit` | `saburiply` | Branch Manager |
| Sacred Heart Senior Secondary School |  | `zohorecruit` | `baabte` | Computer Science Teacher |
| Sakar Robotics | sakarrobotics.com | `zohorecruit` | `sakarrobotics` | Finance Manager |
| Sameeksha Capital Private Limited | sameeksha.zohorecruit.in | `zohorecruit` | `sameeksha` | Accounts Executive |
| SarvaGram | sarvagram.zohorecruit.in | `zohorecruit` | `sarvagram` | Product Support Intern |
| SAS Partners | saspartners.zohorecruit.com | `zohorecruit` | `saspartners` | B2B Marketing Executive |
| SAS Partners Corporate Advisors Private Limited |  | `zohorecruit` | `saspartners` | Sales and Client Acquisition Executive |
| Scaleupally | scaleupally.com | `zohorecruit` | `scaleupally` | Data and BI Engineer |
| Scopic | scopicsoftware.com | `zohorecruit` | `scopicsoftware` | Product Owner |
| SecNinjaz Technologies LLP | secninjaz.com | `zohorecruit` | `secninjaz` | Finance Manager |
| Sectona | sectona.zohorecruit.com | `zohorecruit` | `sectona` | Manager |
| Securin | securin.zohorecruit.in | `zohorecruit` | `securin` | Product Manager |
| seoClarity | seoclarity.com | `zohorecruit` | `seoclarity` | Talent Acquisition Partner |
| SgurrEnergy | sgurrenergy.com | `zohorecruit` | `sgurrenergy` | Structural Design Engineer |
| SHAI | shai.health | `zohorecruit` | `shai` | Team Coordinator |
| Sharp & Tannan | sharpandtannan.com | `zohorecruit` | `sharpandtannan` | Audit |
| Sharp and Tannan | sharpandtannan.zohorecruit.com | `zohorecruit` | `sharpandtannan` | Account Executive |
| Shetty & Bhat |  | `zohorecruit` | `shettybhat` | Articled Assistant |
| Shetty & Bhat, Chartered Accountants | shettybhat.zohorecruit.in | `zohorecruit` | `shettybhat` | Audit Associate |
| Shetty and Bhat |  | `zohorecruit` | `shettybhat` | Bookkeeper |
| Shift Boolean | shiftboolean.zohorecruit.in | `zohorecruit` | `shiftboolean` | Automation Test Engineer |
| Shuru Technologies | shurutech.com | `zohorecruit` | `shurutech` | Backend Engineer |
| SIDGS | sidgs.com | `zohorecruit` | `sidgs` | Cloud Administrator |
| Signalmash | signalmash.com | `zohorecruit` | `signalmash` | Customer Support Engineer |
| Simbian | simbian.zohorecruit.in | `zohorecruit` | `simbian` | Product Marketing Director |
| SKILLX | teaminterval.zohorecruit.in | `zohorecruit` | `teaminterval` | Graphic Designer |
| Sociowash | sociowash.zohorecruit.com | `zohorecruit` | `sociowash` | Legal Associate |
| SoftTech Engineers | softtech-engr.zohorecruit.in | `zohorecruit` | `softtech-engr` | Technical Delivery Manager |
| Softworld India Pvt. Ltd. |  | `zohorecruit` | `swindia` | Sales and Business Development Executive |
| Spektra Systems | spektrasystems.zohorecruit.com | `zohorecruit` | `spektrasystems` | Demand Generation Manager |
| Spocto | go-yubi.com | `zohorecruit` | `go-yubi` | Financial Reporting Associate |
| SriLankan Airlines | srilankan.com | `zohorecruit` | `srilankan` | Finance Officer |
| SRM Technologies | srmtech.com | `zohorecruit` | `srmtech` | PL/SQL Developer |
| SSS Grameen | sssgrameen.zohorecruit.in | `zohorecruit` | `sssgrameen` | Computer System Validation Team Member |
| StarClinch | starclinch.com | `zohorecruit` | `starclinch` | Inside Sales Representative |
| Station Satcom |  | `zohorecruit` | `stationsatcom` | Customer Success Manager |
| Stockarea | stockarea.com | `zohorecruit` | `stockarea` | Infrastructure and Partnership Manager |
| STRATIST | stratist.zohorecruit.in | `zohorecruit` | `stratist` | Client Relationship Manager |
| StratJuris | stratjuris.zohorecruit.com | `zohorecruit` | `stratjuris` | Legal Intern |
| Stratjuris Partners |  | `zohorecruit` | `stratjuris` | Patent Filing Associate |
| Subscribili | subscribili.com | `zohorecruit` | `subscribili` | QA |
| Suffescom Solutions | suffescom.in | `zohorecruit` | `suffescom` | Junior DevOps Engineer |
| SUN360 | sun360.co.in | `zohorecruit` | `sun360` | HR Intern |
| Sunday Design | sundaydesign.zohorecruit.in | `zohorecruit` | `sundaydesign` | College Ambassador |
| SunShell Power | sunshellpower.zohorecruit.in | `zohorecruit` | `sunshellpower` | Accounts Executive |
| Support Tech LLC |  | `zohorecruit` | `supporttech` | ServiceNow Developer |
| Suraasa | suraasa.zohorecruit.com | `zohorecruit` | `suraasa` | Product Sales Specialist |
| SVASTEK | svastek.zohorecruit.in | `zohorecruit` | `svastek` | Key Account Manager |
| Swaniti Initiative | swaniti.zohorecruit.in | `zohorecruit` | `swaniti` | Finance Officer |
| SwitchOn | joinswitchon.com | `zohorecruit` | `joinswitchon` | Account Executive |
| SwitchOn.io | switchon.io | `zohorecruit` | `joinswitchon` | Sales Engineer |
| Symbroj Solar Pvt. Ltd. | symbrojsolar.zohorecruit.in | `zohorecruit` | `symbrojsolar` | Diploma Engineer Trainee |
| Talking Lands | talkinglands.com | `zohorecruit` | `talkinglands` | Enterprise Sales Manager |
| Tata Play Fiber | tataplayfiber.zohorecruit.in | `zohorecruit` | `tataplayfiber` | Sales |
| TATTI | tatti.zohorecruit.com | `zohorecruit` | `tatti` | Teaching Staff |
| Taxpert Pro ACC | taxpertproacc.zohorecruit.com | `zohorecruit` | `taxpertproacc` | Accounts Executive |
| Tazapay | tazapay.com | `zohorecruit` | `tazapay` | Analytics Manager |
| TeamFicient | teamficient.zohorecruit.com | `zohorecruit` | `teamficient` | Financial Analyst |
| Tech First Gulf | techfirstgulf.com | `zohorecruit` | `techfirstgulf` | Channel Account Manager |
| TechFirst Gulf | techfirstgulf.zohorecruit.com | `zohorecruit` | `techfirstgulf` | Order Management Executive |
| TechForce Services | techforceservices.com | `zohorecruit` | `careers.techforceservices.com` | Salesforce Developer |
| Technology |  | `zohorecruit` | `csc` | Executive Software Engineer |
| TecVesten | tecvesten.zohorecruit.in | `zohorecruit` | `tecvesten` | Facility Cleaning Supervisor |
| TekFriday Processing Solutions | tekfriday.com | `zohorecruit` | `tekfriday` | Production Support Engineer |
| Teleradiology Solutions | telradsol.com | `zohorecruit` | `telradsol` | Research Assistant |
| Teleradiology Solutions (TRS) |  | `zohorecruit` | `telradsol` | Technical Recruiter |
| Tempsens Instruments | tempsens.com | `zohorecruit` | `tempsens` | Assistant Regional Manager |
| Tempsens Instruments (India) Limited |  | `zohorecruit` | `tempsens` | Engineer |
| Tenet | wearetenet.com | `zohorecruit` | `wearetenet` | SEO Executive |
| Thanal | thanal.org | `zohorecruit` | `thanal` | Administrative Assistant |
| The ePlane Company | eplane.ai | `zohorecruit` | `eplane` | Aircraft Maintenance Engineer |
| Theos | theos.zohorecruit.in | `zohorecruit` | `theos` | Interior Designer |
| ThinkBio.AI |  | `zohorecruit` | `feathersoft` | Computational Biologist |
| thinkbridge | thinkbridge.com | `zohorecruit` | `thinkbridge` | Data Engineer |
| Threatcop Inc. | threatcop.com | `zohorecruit` | `kratikal` | Graphic and Motion Designer |
| Torq Commodities | careers.torqcommodities.com | `zohorecruit` | `careers.torqcommodities.com` | Finance and Accounting Manager |
| Touchstone Infotech | touchstoneinfotech.com | `zohorecruit` | `touchstoneinfotech` | Influencer Marketing Intern |
| Touchstone Infotech LLP | touchstoneinfotech.zohorecruit.in | `zohorecruit` | `touchstoneinfotech` | Performance Marketing Specialist |
| Training Basket | trainingbasket.in | `zohorecruit` | `trainingbasket` | Business Development Associate |
| TravelWings | travelwings.zohorecruit.com | `zohorecruit` | `travelwings` | Corporate Travel Consultant |
| Travelwings.com | travelwings.com | `zohorecruit` | `travelwings` | Travel Consultant |
| Tristone Partners | tristone-partners.zohorecruit.in | `zohorecruit` | `tristone-partners` | AI Engineer |
| Tristone Strategic Partners LLP | tristone-partners.com | `zohorecruit` | `tristone-partners` | AI Engineer |
| Truviq Systems | truviqsystems.zohorecruit.in | `zohorecruit` | `truviqsystems` | Generative AI Developer |
| Tsaaro | tsaaro.zohorecruit.in | `zohorecruit` | `tsaaro` | Legal Intern |
| UAV Marketplace | uavmarketplace.zohorecruit.in | `zohorecruit` | `uavmarketplace` | Zoho Application Developer |
| UCAM | ucamco.com | `zohorecruit` | `ucamind` | HR Generalist |
| UCAM Pvt. Ltd. (Nimble Machines) | ucam.co.in | `zohorecruit` | `ucamind` | Electrical Harnessing and Panel Wiring Supervisor |
| Ultraviolette | ultraviolette.zohorecruit.in | `zohorecruit` | `ultraviolette` | CRM Associate |
| Ultraviolette Automotive | ultraviolette.com | `zohorecruit` | `ultraviolette` | Systems Engineering Intern |
| Unbore Foods | unborefoods.zohorecruit.in | `zohorecruit` | `unborefoods` | Sales Executive |
| unknown | powerbridge-org60025989370.zohorecruit.in | `zohorecruit` | `powerbridge-org60025989370` | Field Services Engineer |
| Upstaff | upstaff.ca | `zohorecruit` | `sereneaid` | Accountant |
| Valenta | valentabpo.zohorecruit.com | `zohorecruit` | `valentabpo` | RPA Managed Services Lead |
| Valenta BPO | valentabpo.com | `zohorecruit` | `valentabpo` | HR Operations and People Lead |
| VASA Denticity | dentalkart.com | `zohorecruit` | `dentalkart` | Talent Acquisition Manager |
| vCommission Media | vcommission.zohorecruit.com | `zohorecruit` | `vcommission` | MIS Executive |
| Veerix Biotech | veerixbiotech.in | `zohorecruit` | `veerixbiotech` | Medical Representative |
| VergeCloud | vergecloud.zohorecruit.in | `zohorecruit` | `vergecloud` | System Developer |
| VerifiTech | verifitech.zohorecruit.in | `zohorecruit` | `verifitech` | SAP Analytics Cloud Consultant |
| Verizol |  | `zohorecruit` | `zipnom` | Backend Engineer |
| VideoSDK | videosdk.live | `zohorecruit` | `zujonow` | Product Associate |
| Virima | virima.com | `zohorecruit` | `virima` | Product Manager |
| Vitu Realty | viturealty.zohorecruit.in | `zohorecruit` | `viturealty` | Site Engineer |
| Vivusoft | vivusoft.com | `zohorecruit` | `vivusoft` | Web Developer |
| Vserve Solution | vservesolution.com | `zohorecruit` | `vservesolution` | E-commerce Executive |
| Vulcury | vulcury.com | `zohorecruit` | `vulcury` | Applied AI Research Intern |
| Wadhwani AI | wadhwaniai.org | `zohorecruit` | `wadhwaniai` | Program Officer |
| Wadhwani Foundation | wadhwanifoundation.org | `zohorecruit` | `wfglobal` | Ecosystem Activation Lead |
| Walls To Home Interiors | wallstohomeinteriors.zohorecruit.com | `zohorecruit` | `wallstohomeinteriors` | Business Development Pre-Sales Executive |
| Webbee Global | webbeeglobal.com | `zohorecruit` | `webbeeglobal` | MIS Executive |
| Webgility | webgility.com | `zohorecruit` | `webgility` | Product Manager |
| WebIndia Inc | webindiainc.com | `zohorecruit` | `webindiainc` | Accountant |
| WEN - Accelerate | wfglobal.com | `zohorecruit` | `wfglobal` | Programme Manager |
| Wenodo | wenodo.com | `zohorecruit` | `wenodo` | IT Support Specialist |
| WhiteLion | whitelion1.zohorecruit.in | `zohorecruit` | `whitelion1` | Marketing Manager |
| Wissen Technology | wissen.com | `zohorecruit` | `wissen` | Azure Fabric Architect |
| Without | without.live | `zohorecruit` | `ashaya` | Graphic Design Intern |
| Workmates | cloudworkmates.com | `zohorecruit` | `cloudworkmates` | AWS, Python, and AI/ML Engineer |
| WWF-India | wwfindia.zohorecruit.com | `zohorecruit` | `wwfindia` | Sales Trainee |
| Xapads Media | xapads.com | `zohorecruit` | `xapads` | Talent Acquisition |
| Xempla | xempla.ai | `zohorecruit` | `xempla` | Backend Developer |
| XenonStack | xenonstack.ai | `zohorecruit` | `xenonstack` | Digital Marketing |
| XT Global | xtglobal.zohorecruit.in | `zohorecruit` | `xtglobal` | Revenue Accounting Manager |
| XTGlobal | xtglobal.com | `zohorecruit` | `xtglobal` | DevOps Engineer |
| Yadimen | yadimen.zohorecruit.eu | `zohorecruit` | `yadimen` | Network Engineer |
| Yakka Services | yakkaservices.zohorecruit.com | `zohorecruit` | `yakkaservices` | Network Engineer |
| Yakkaspace Services Private Limited |  | `zohorecruit` | `yakkaservices` | Project Engineer |
| Yogini Tradex | yoginitradex.zohorecruit.in | `zohorecruit` | `yoginitradex` | Audit Executive |
| YR Gaitonde Medical Educational & Research Foundation | yrgcare.zohorecruit.in | `zohorecruit` | `yrgcare` | Cluster Block Coordinator |
| Yubi | go-yubi.zohorecruit.in | `zohorecruit` | `go-yubi` | Associate - Financial Reporting |
| Zen Technologies | zentechnologies.zohorecruit.in | `zohorecruit` | `zentechnologies` | EW Coordinator |
| Zifup |  | `zohorecruit` | `sellergize` | PHP Laravel Developer |
| Zinca Advisory | zincaadvisory.zohorecruit.in | `zohorecruit` | `zincaadvisory` | Vice President |
| ZipNom | zipnom.zohorecruit.in | `zohorecruit` | `zipnom` | Data Engineer |
| ZM Technologies | zmtechnologies.zohorecruit.in | `zohorecruit` | `zmtechnologies` | HR Associate |
| Zybisys | zybisys.com | `zohorecruit` | `zybisys` | Engineer |
| Zyeta | zyeta.com | `zohorecruit` | `zyeta` | Construction Manager |
| Zylu | zylu.zohorecruit.in | `zohorecruit` | `zylu` | Head of Growth |

### `workable` — 197 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| 2070Health | 2070health.com | `workable` | `2070health` | Growth and Outreach Associate |
| A2MAC1 | a2mac1.com | `workable` | `a2mac1` | Costing Engineer |
| Abakus Center | abakus-center.com | `workable` | `abakus_center` | Teacher |
| Accellor | accellor.com | `workable` | `accellor` | MuleSoft Architect |
| Allucent | www.allucent.com | `workable` | `allucent` | Clinical Data Manager |
| Anglo-Eastern Ship Management | angloeastern.com | `workable` | `anglo-eastern_ship_management` | Technical Officer |
| Apna | apna.co | `workable` | `apna` | QA |
| Arbor Education | arbor-education.com | `workable` | `arbor_education` | Migrations Operations Manager |
| Arena Investors / i Quaestor Advisors |  | `workable` | `arena_investors_i_quaestor_advisors` | Risk Manager |
| Arena Investors I Quaestor Advisors | arenaco.com | `workable` | `arena_investors_i_quaestor_advisors` | Business Analyst |
| Articore Group | articore.com | `workable` | `articore_group` | Design Specialist |
| Ascendis Pharma | ascendispharma.com | `workable` | `ascendis_pharma` | Market Access Manager |
| Astrome Technologies | astrome.co | `workable` | `astrome_technologies` | Project Manager |
| AUGO | augolife.com | `workable` | `augo` | Director of TikTok Shop |
| Auxilium Skills Academy | auxiliumskillsacademy.in | `workable` | `auxilium_skills_academy` | Hospitality Management Trainer |
| Awesome Motive | awesomemotive.com | `workable` | `awesome_motive` | Growth Manager |
| Babcock Power APAC Pvt. Ltd. | babcockpower.com | `workable` | `babcock_power_apac_pvt._ltd.` | Buyer / Global Sourcing Specialist |
| BeamNG GmbH | beamng.gmbh | `workable` | `beamng_gmbh` | Rendering Programmer |
| Benchmark Utility Services | benchmarkutilityservices.com | `workable` | `benchmark_utility_services` | Candidate Sourcing Specialist |
| BlackStone eIT | www.blackstoneeit.com | `workable` | `blackstone_eit` | Project Coordinator |
| Blankstate | blankstate.ai | `workable` | `blankstate` | InfoSec Manager |
| Blitzed | blitzed.io | `workable` | `blitzed` | Community Manager |
| Blue Machines AI | bluemachines.ai | `workable` | `blue_machines_ai` | Forward Deployed Engineer |
| blueAPACHE | blueapache.com | `workable` | `blueapache` | Sales Support Specialist |
| Botsync | www.botsync.co | `workable` | `botsync` | Robotics Operations Engineer |
| Brand MIZ | brandmiz.com | `workable` | `brand_miz` | Business Development Executive |
| BreachLock | breachlock.com | `workable` | `breachlock` | Director of Customer Success and Support |
| Bridge33 Capital | bridge33capital.com | `workable` | `bridge33_capital` | Paralegal |
| British Ecological Society | britishecologicalsociety.org | `workable` | `british_ecological_society` | Blog Editor |
| BuzzyBooth.com | buzzybooth.com | `workable` | `buzzybooth.com` | Sales Development Representative |
| Celestile | celestile.com | `workable` | `celestile` | Sales Executive |
| CEQUENS | cequens.com | `workable` | `cequens` | Head of Wholesale - Business Sales |
| Chemin | chemin.com | `workable` | `chemin` | Audio Transcription Reviewer |
| CIMMYT | www.cimmyt.org | `workable` | `cimmyt` | Business Services Manager |
| Civica | civica.com | `workable` | `civica` | Head of Finance Operations |
| Control Risks | controlrisks.com | `workable` | `control_risks` | FP&A Analyst |
| Coretek Services | coretek.com | `workable` | `coretek_services` | Data Platform Engineer |
| Creative Chaos | creativechaos.co | `workable` | `creative_chaos` | AI Engineer |
| Crop.photo | www.crop.photo | `workable` | `crop.photo` | QA Automation Engineer |
| Datamark, Inc. | datamark.net | `workable` | `datamark,_inc.` | Manager |
| DBSync Inc | mydbsync.com | `workable` | `dbsync_inc` | Solution Sales Engineer |
| Decentralized Masters | decentralizedmasters.com | `workable` | `decentralized_masters` | Graphic Designer |
| Decision Foundry | decisionfoundry.com | `workable` | `decision_foundry` | Finance Manager |
| Deep Sea Media | deepseamedia.ca | `workable` | `deep_sea_media` | Appointment Setter |
| Delta Exchange | delta.exchange | `workable` | `delta_exchange` | Cloud Security Engineer |
| Demo S.A. | demo.gr | `workable` | `demo_s.a.` | Regulatory Affairs Associate |
| Destinus | destinus.eu | `workable` | `destinus` | Business Development Manager |
| division50 | division50.com | `workable` | `division50` | Recruiter |
| Dodge Construction Network | construction.com | `workable` | `dodge_construction_network` | Revenue Operations Reporting Specialist |
| Egon Zehnder | www.egonzehnder.com | `workable` | `egon_zehnder` | Business Analyst |
| Emerging Travel Group | www.emergingtravel.com | `workable` | `emerging_travel_group` | DevOps Engineer |
| Emoha Eldercare | emoha.com | `workable` | `emoha_eldercare` | Doctor |
| EnerMech | enermech.com | `workable` | `enermech` | Contracts Specialist |
| Enfinity Global | enfinity.global | `workable` | `enfinity_global` | SOC Specialist |
| Envalior | envalior.com | `workable` | `envalior` | Customer Service Representative |
| Erbity Private Limited | erbity.com | `workable` | `erbity_private_limited` | DFT Engineer |
| Eriez | www.eriez.com | `workable` | `eriez` | Product Line Manager |
| Euromonitor | euromonitor.com | `workable` | `euromonitor` | AI Tech Lead |
| Euronet Worldwide, Inc. | euronetworldwide.com | `workable` | `euronet_worldwide,_inc.` | Fraud Strategy Director |
| Evidence Action | evidenceaction.org | `workable` | `evidence_action` | Regional Coordinator |
| Excelya | excelya.com | `workable` | `excelya` | Technical Data Manager |
| Exely | exely.com | `workable` | `exely` | Customer Success Manager |
| Exponent Energy | exponent.energy | `workable` | `exponent_energy` | Test Engineer |
| FairMoney | fairmoney.io | `workable` | `fairmoney` | Relationship Officer |
| FE fundinfo | fefundinfo.com | `workable` | `fe_fundinfo` | Data Onboarding Manager |
| First Principles | firstprinciples.la | `workable` | `first_principles` | Training Program Manager |
| FlexEnergi | flexenergi.com | `workable` | `accurant_international` | Software Engineer |
| Flosum | flosum.com | `workable` | `flosum` | Director of Revenue Operations |
| Fortanix | fortanix.com | `workable` | `fortanix` | Software Engineer |
| Freedx | freedx.com | `workable` | `freedx` | Affiliate Manager |
| Fulfillment IQ | fulfillmentiq.com | `workable` | `fulfillment_iq` | Manhattan Scale Developer |
| Funding Societies \| Modalku Group | fundingsocieties.com | `workable` | `funding_societies_\|_modalku_group` | Data Intern |
| Genesis Analytics | genesis-analytics.com | `workable` | `genesis_analytics` | PFM Consultant |
| Genetec | genetec.com | `workable` | `genetec` | Regional Manager |
| Gigmo Solutions | gigmos.com | `workable` | `gigmo_solutions` | Data Operations Associate |
| GoGlobal | goglobal.com | `workable` | `goglobal` | Account Manager |
| GoTymeX |  | `workable` | `gotymex` | Product Engineer |
| Gridlines | gridlines.com | `workable` | `gridlines` | Commercial Director |
| GroundTruth | groundtruth.com | `workable` | `groundtruth` | Billing Analyst |
| Gunnebo Entrance Control | gunneboentrancecontrol.com | `workable` | `gunnebo_entrance_control` | BI Analyst |
| heuristech | heuristech.io | `workable` | `heuristech` | Back-end Developer |
| Hey Savi | www.heysavi.com | `workable` | `hey_savi` | Marketing Intern |
| Horizontal Digital | horizontaldigital.com | `workable` | `horizontal_digital` | Technical Lead |
| Human Made | humanmade.com | `workable` | `human_made,_makers_of_altis_dxp` | Agile Delivery Lead |
| Innovaccer | innovaccer.com | `workable` | `innovaccer_analytics` | Product Manager |
| InnovationTeam | innovationteam.com | `workable` | `innovationteam` | Pega Engineer |
| Intellect | www.intellect.co | `workable` | `intellect` | Care Excellence Lead |
| International Water Management Institute | iwmi.org | `workable` | `international_water_management_institute` | Communications Specialist |
| Intertek | intertek.com | `workable` | `intertek` | Supply Chain Coordinator |
| Intuitive Psychiatry |  | `workable` | `2070health` | Mindfulness and Wellness Skills Coach |
| iSupport Worldwide | isupportworldwide.com | `workable` | `isupport_worldwide` | AI Solutions Architect |
| JoVE | jove.com | `workable` | `jove` | Product Manager |
| Kaizen Asset Management Services | kaizenams.com | `workable` | `kaizen_asset_management_services` | Internal Process Auditor |
| Karbon Business | karboncard.com | `workable` | `karbon_business` | Digital Performance Marketer |
| Kaufman Rossin | kaufmanrossin.com | `workable` | `kaufman_rossin` | Fund Accountant |
| Keywords Studios | keywordsstudios.com | `workable` | `keywords_studios` | Implementation Engineer |
| KNOREX | knorex.com | `workable` | `knorex` | Channel Performance Strategist |
| Label Your Data | labelyourdata.com | `workable` | `label_your_data` | Account Manager |
| Lakshya Digital | lakshyadigital.com | `workable` | `lakshya_digital` | 3D Animator |
| Laundryheap | laundryheap.com | `workable` | `laundryheap` | Customer Support Executive |
| Learnlight | learnlight.com | `workable` | `learnlight` | Test Engineer |
| Leucine | leucine.ai | `workable` | `leucine` | Solution Architect Intern |
| Living in a Bubble | livinginabubble.com.au | `workable` | `living_in_a_bubble` | Marketing Coordinator |
| Lokal App | www.lokalapps.com | `workable` | `lokal_app` | HR Business Partner |
| LRN Corporation | lrn.com | `workable` | `lrn_corporation` | Billing Associate |
| LUXASIA | luxasia.com | `workable` | `luxasia` | Purchase Process Associate |
| Maker Lab | wearemakerlab.com | `workable` | `maker_lab` | Advertising Operations Assistant |
| Marcura | marcura.com | `workable` | `marcura` | Maritime Data Analyst |
| Matar Al Baqmi Holding Company | matarcompany.com | `workable` | `matar_al_baqmi_holding_company` | Hatchery Technician |
| Maxwell Energy System Pvt Ltd | maxwellenergy.co | `workable` | `maxwell_energy_system_pvt_ltd` | Hardware Design Engineer |
| Measured | measured.com | `workable` | `measured` | Technical Operations Specialist |
| MediaRadar | mediaradar.com | `workable` | `mediaradar` | Assistant Controller |
| Mellow Sleep | mellowsleep.com | `workable` | `mellow_sleep` | Shopify Developer |
| Mercari, Inc. (India) | careers.mercari.com | `workable` | `mercari,_inc._(india)` | Platform Engineer |
| Messe Muenchen India | mm-india.in | `workable` | `messe_muenchen_india` | Organizational Development and Transformation Manager |
| Micro:bit Educational Foundation | microbit.org | `workable` | `micro:bit_educational_foundation` | Head of Partnerships |
| Mindera | mindera.com | `workable` | `mindera` | Software Engineer |
| Mindrift - Data annotation | toloka.ai | `workable` | `mindrift_-_data_annotation` | Bilingual Voice Recording Speaker |
| MODIFI GmbH | modifi.com | `workable` | `modifi_gmbh` | Head of Accounting & Tax |
| Mozn | mozn.ai | `workable` | `mozn` | Engineering Manager |
| Mrsool | mrsool.co | `workable` | `mrsool` | Engineering Manager |
| Nacre Capital | nacrecapital.com | `workable` | `nacre_capital` | AI Engineer |
| New Energy Nexus | newenergynexus.com | `workable` | `new_energy_nexus` | Director of Development Strategy and Operations |
| Novo Holdings | novoholdings.dk | `workable` | `novo_holdings` | Accountant |
| Oddyssey Proprietary Food Pvt Ltd | odysseyfoods.in | `workable` | `oddyssey_proprietary_food_pvt_ltd` | Machine Operator |
| Omilia | omilia.com | `workable` | `omilia` | Sales Development Representative |
| One Of Us | weacceptyou.com | `workable` | `one_of_us` | Production Coordinator |
| Opalus Investments LLC | opalusinvestments.com | `workable` | `opalus_investments_llc` | Scrum Master / Delivery Manager |
| Origin | origin.tech | `workable` | `origin` | Electrical Technician |
| OXY Exhaust Service | oxyexhaustservice.com | `workable` | `oxy_exhaust_service` | Business Development Intern |
| Packt | packt.com | `workable` | `packt` | Product Lead |
| People Powered | peoplepowered.org | `workable` | `people_powered` | Resource Mobilization Director |
| PEOPLECERT | peoplecert.org | `workable` | `peoplecert` | Dynamics 365 Finance & Operations Developer |
| Pitchbox | pitchbox.com | `workable` | `pitchbox` | Link Building and Outreach Specialist |
| Pixaera | www.pixaera.com | `workable` | `pixaera` | Level Designer |
| Platinumlist | platinumlist.net | `workable` | `platinumlist` | Project Manager |
| Prezent AI | prezent.ai | `workable` | `prezent_ai` | Program Lead |
| PriceLabs | pricelabs.co | `workable` | `pricelabs` | Solutions Consultant |
| ProArch | proarch.com | `workable` | `proarch` | Product Owner |
| Proficio | proficio.com | `workable` | `proficio` | Threat Engineer |
| Protera | protera.com | `workable` | `protera` | Service Desk Engineer |
| Quadric, Inc | quadric.io | `workable` | `quadric,_inc` | Design Verification Engineer |
| Quanticate | quanticate.com | `workable` | `quanticate` | Programmer |
| Rapidomes LLC | rapidomes.com | `workable` | `rapidomes_llc` | Digital Marketing Specialist |
| Rapyuta Robotics | rapyuta-robotics.com | `workable` | `rapyuta_robotics` | Talent Acquisition Partner |
| RateHawk | ratehawk.com | `workable` | `ratehawk` | Reservation Manager |
| Rentokil Initial | careers.rentokil-initial.com | `workable` | `rentokil_initial` | Product Sales Executive |
| Reveal Health Tech | revealhealthtech.com | `workable` | `reveal_health_tech` | Full Stack Developer |
| Richpanel | richpanel.com | `workable` | `richpanel` | Head of Operations |
| Rolling Arrays - Consulting | rollingarrays.com | `workable` | `rolling_arrays_-_consulting` | Workday Functional Consultant |
| Sago | sago.com | `workable` | `sago` | Panel Helpdesk Trainee |
| SAP Fioneer | fioneer.com | `workable` | `sap_fioneer` | Head, Finance Shared Service Center |
| Sedona Digital | sedona.digital | `workable` | `sedona_digital` | Customer Success Associate |
| Seekho | seekho.in | `workable` | `seekho` | Security Engineer |
| Seeq | seeq.com | `workable` | `seeq` | Account Executive |
| Serko Ltd | serko.com | `workable` | `serko_ltd` | Data Engineer |
| Seydeltech India Pvt Ltd | seydeltech.com | `workable` | `seydeltech_india_pvt_ltd` | Customer Support Executive |
| SHIELD | shield.com | `workable` | `shield` | Account Executive |
| Shiksharthi Educational Institute | shiksharthi.org | `workable` | `shiksharthi_educational_institute` | Chemistry Teacher |
| Side | side.inc | `workable` | `side` | AI Quality Engineer |
| Sleek | sleek.com | `workable` | `sleek` | Compliance Officer |
| Smart Apartment Data | smartapartmentdata.com | `workable` | `smart_apartment_data` | Team Coach |
| SmartBuyGlasses | smartbuyglasses.com | `workable` | `smartbuyglasses` | Catalogue Visuals Coordinator |
| Smartstream Limited | smart.stream | `workable` | `smartstream_limited` | Security Engineering Manager |
| Solplanet | solplanet.net | `workable` | `solplanet` | Service Engineer |
| Stadium | www.bystadium.com | `workable` | `stadium` | JavaScript Developer |
| Statistics & Data Corporation (SDC) | sdcclinical.com | `workable` | `statistics_&_data_corporation_(sdc)` | Clinical Programmer |
| Stranger Soccer | www.strangersoccer.com | `workable` | `stranger_soccer` | Operator & License Owner |
| Studio 1 | rajivthakkar.com | `workable` | `studio_1` | 3D Visualizer and Interior Designer |
| SupportYourApp | supportyourapp.com | `workable` | `supportyourapp` | Administration & Operations Specialist |
| Syntiant | syntiant.com | `workable` | `syntiant` | Digital Design Engineer |
| Sécheron Hasler Group | www.secheron.com | `workable` | `sécheron_hasler_group` | Power BI Engineer |
| Teleport | teleport.it | `workable` | `teleport` | Product Specialist |
| Teltonika Group | teltonika-iot-group.com | `workable` | `teltonika` | Sales Manager |
| Tentworks Interactive | tentworks.io | `workable` | `tentworks_interactive` | Game Developer |
| Thixpro Technologies Pvt Ltd | thixpro.com | `workable` | `thixpro_technologies_pvt_ltd` | Sales Executive |
| Tiger Analytics Inc. | tigeranalytics.com | `workable` | `tiger_analytics_inc.` | Forward Deployed Engineer |
| Trackier | trackier.com | `workable` | `trackier` | Graphic Design Intern |
| Trident | trident.works | `workable` | `trident` | Process Engineer |
| Triptease | triptease.com | `workable` | `triptease` | Market Director / Market Director |
| Tryzens Global | tryzens.com | `workable` | `tryzens_global` | Project Manager |
| UMAEZ LLC | umaez.co | `workable` | `umaez_llc` | E-commerce Copywriter |
| Unosecur | unosecur.com | `workable` | `unosecur` | Finance Manager |
| UWorld, LLC | careers.uworld.com | `workable` | `uworld,_llc` | UI/UX Designer |
| Valsoft Corporation | aspiresoftware.com | `workable` | `valsoft_corporation` | Cloud and Infrastructure Specialist |
| Virallens | virallens.com | `workable` | `virallens` | Full Stack Developer |
| VSI Infotech LLP | vsiinfotech.com | `workable` | `vsi_infotech_llp` | Full Stack Developer |
| Wisevu | wisevu.com | `workable` | `wisevu` | Direct Response Copywriter/Editor |
| WPT Global | wptglobal.com | `workable` | `wpt_global` | Strategy and Growth Manager |
| Wrisk | wrisk.co | `workable` | `wrisk` | Front-End Engineer |
| X-PHY | flexxon.com | `workable` | `x-phy` | Product Marketing Manager |
| YouTrip | you.co | `workable` | `youtrip` | IT System Administrator |
| ZainTECH | zaintech.com | `workable` | `zaintech` | Data Scientist |
| Zeal Group | zeal-holdings.com | `workable` | `zeal_group` | Quantitative Analyst |
| Zenara Health | zenarahealth.com | `workable` | `zenara_health` | HR and Executive Assistant |
| Zifo | zifo.com | `workable` | `zifo` | Data Engineer |
| Zyte | zyte.com | `workable` | `zyte` | IT Automation and Platform Engineer |

### `smartrecruiters` — 174 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| AbbVie | global.allerganaesthetics.com | `smartrecruiters` | `abbvie` | Key Account Specialist |
| AccorCorpo |  | `smartrecruiters` | `accorcorpo` | Director of Finance |
| AccorHotel | accor.com | `smartrecruiters` | `accorhotel` | Gym Instructor |
| AFRY | afry.com | `smartrecruiters` | `afry` | HR Operations |
| AireSpring | airespring.com | `smartrecruiters` | `airespring1` | Business Analyst |
| Allegis Global Solutions |  | `smartrecruiters` | `allegisglobalsolutions` | Accounts Receivable Associate |
| Altisource | altisource.com | `smartrecruiters` | `altisource` | Software Engineer |
| Anton Paar | anton-paar.com | `smartrecruiters` | `antonpaar1` | Field Sales |
| Applied Cloud Computing | appliedcloudcomputing.com | `smartrecruiters` | `appliedcloudcomputing` | Cloud Network Security Engineer |
| Applus IDIADA | idiada.com | `smartrecruiters` | `applusidiada1` | Sales Manager |
| Arista Networks | arista.com | `smartrecruiters` | `aristanetworks` | Account Manager |
| Assent | assent.com | `smartrecruiters` | `assent` | Finance Assistant Manager |
| ASSYSTEM | assystemstup.com | `smartrecruiters` | `assystem` | Accountant |
| Aumovio | aumovio.com | `smartrecruiters` | `aumovio` | Mechanical Development Engineer |
| Avaloq | avaloq.com | `smartrecruiters` | `avaloq1` | WAF/IAM Engineer |
| Avery Dennison | averydennison.com | `smartrecruiters` | `averydennison` | Industrial Relations and HR Manager |
| Axiado |  | `smartrecruiters` | `axiado` | Physical Design Engineer |
| Believe | believe.com | `smartrecruiters` | `believe` | Sage X3 Developer |
| BETSOL | betsol.com | `smartrecruiters` | `betsol` | Technical Architect |
| Blend360 | blend360.com | `smartrecruiters` | `blend360` | Campaign Data and Operations Analyst |
| BlueOptima | blueoptima.com | `smartrecruiters` | `blueoptima` | Product Manager |
| Bosch Global Software Technologies Private Limited | bosch.com | `smartrecruiters` | `boschgroup` | ServiceNow Service Portal Developer |
| Bosch Home Comfort India Limited | hitachiaircon.com | `smartrecruiters` | `bosch-homecomfort` | Embedded Software Testing Engineer |
| Bosch-HomeComfort | bosch-homecomfortgroup.com | `smartrecruiters` | `bosch-homecomfort` | Information & Cyber Security Expert |
| Brainwonders |  | `smartrecruiters` | `brainwonders` | Psychology Intern |
| Canva | www.canva.com | `smartrecruiters` | `canva` | Project Manager |
| Check Point Software Technologies | checkpoint.com | `smartrecruiters` | `checkpointsoftwaretechnologies2` | Software Engineer |
| Cielo | cielotalent.com | `smartrecruiters` | `cielo2` | Recruitment Marketing Consultant |
| Cielo Projects |  | `smartrecruiters` | `cieloprojects` | DevOps Engineer |
| Cint | cint.com | `smartrecruiters` | `cint` | Trust and Safety Analyst |
| Clifford Chance | cliffordchance.com | `smartrecruiters` | `cliffordchance` | AI Engineer |
| Coface | coface.com | `smartrecruiters` | `coface` | Accountant |
| Colliers | corporate.colliers.com | `smartrecruiters` | `colliers1` | SuccessFactors Engineer |
| Continental | continental | `smartrecruiters` | `continental` | IT Engineer Data Lakehouse |
| Continental Group Sector ContiTech | continental.com | `smartrecruiters` | `continentalgroupsectorcontitech` | Salesforce IT Engineer |
| Continental India Private Limited |  | `smartrecruiters` | `continental` | Technical Service Engineer |
| ContiTech | continental-industry.com | `smartrecruiters` | `continentalgroupsectorcontitech` | IT System and Application Architect |
| Customized Energy Solutions |  | `smartrecruiters` | `customizedenergysolutions` | Data Engineer |
| DataKrew Pvt. Ltd. |  | `smartrecruiters` | `datakrewpvtltd` | Pre-Sales Specialist |
| Domino's | dominos.com | `smartrecruiters` | `dominos` | Vice President, International Business |
| Dr Reddy's Laboratories Limited | drreddys.com | `smartrecruiters` | `drreddyslaboratorieslimited` | Treasury Banking Compliance Specialist |
| Eclick Softwares and Solutions Pvt Ltd |  | `smartrecruiters` | `eclicksoftwaresandsolutionspvtltd` | Website Consultant |
| EcoVadis |  | `smartrecruiters` | `ecovadis` | Worker Engagement Specialist |
| Egis Group | egis-group.com | `smartrecruiters` | `egisgroup` | Marine & Ports Engineer |
| Endava | endava.com | `smartrecruiters` | `endava` | Cloud Platform Engineer |
| Endeavour Group | endeavourgroupcareers.com.au | `smartrecruiters` | `endeavourgroupcareers` | Accountant |
| Entain |  | `smartrecruiters` | `entain` | Head of Engineering |
| Enviri Corporation | enviri.com | `smartrecruiters` | `enviricorporation` | Assistant Manager Operations and Maintenance |
| Ergomed | ergomed.com | `smartrecruiters` | `ergomed` | Quality Manager |
| Eurofins | eurofins.com | `smartrecruiters` | `eurofins` | Product Support Engineer |
| EVERSANA |  | `smartrecruiters` | `eversana1` | .NET Backend Developer |
| Exinity |  | `smartrecruiters` | `exinity` | Business Development Manager |
| Experian | experian.com | `smartrecruiters` | `experian` | Product Manager |
| Facility Performance Consulting Limited |  | `smartrecruiters` | `facilityperformanceconsultinglimited` | Civil / CSA Data Center QA/QC Specialist |
| Fastmarkets | fastmarkets.com | `smartrecruiters` | `fastmarkets` | Platform Administrator |
| Flywire | flywire.com | `smartrecruiters` | `flywire1` | QA Engineer |
| Freshworks | freshworks.com | `smartrecruiters` | `freshworks` | Business Analyst |
| Fusion Consulting |  | `smartrecruiters` | `fusionconsulting` | IT Project Controller |
| Ghobash Group |  | `smartrecruiters` | `ghobashgroup` | Product Specialist |
| Grab | grab.com | `smartrecruiters` | `grab` | Data Scientist |
| Gracenote | gracenote.com | `smartrecruiters` | `thenielsencompany` | Content Operations Editor |
| Grantek Systems Integration |  | `smartrecruiters` | `granteksystemsintegration` | Systems Designer |
| H&M Group | hmgroup.com | `smartrecruiters` | `hmgroup` | Department Manager |
| HAMMOQ |  | `smartrecruiters` | `hammoq` | Receptionist and Telecaller |
| Harsco Rail | harscorail.com | `smartrecruiters` | `enviricorporation` | Maintenance Support Administrator |
| Hitachi Solutions | www.hitachisolutions.com | `smartrecruiters` | `hitachisolutions` | Finance Functional Consultant |
| IAZI | iazicifi.ch | `smartrecruiters` | `smgswissmarketplacegroup` | Real Estate Valuation Working Student |
| ib vogt GmbH |  | `smartrecruiters` | `ib-vogt-gmbh` | Tax Executive |
| IFS | ifs.com | `smartrecruiters` | `ifs1` | Demo Infrastructure Engineer |
| IN-VR | in-vr.co | `smartrecruiters` | `in-vr` | Communications and Marketing |
| Informa Group Plc. | taylorandfrancisgroup.com | `smartrecruiters` | `informagroupplc` | Full Stack Engineer |
| IntegriChain | integrichain.com | `smartrecruiters` | `integrichain1` | Product Analyst |
| Inter IKEA Group |  | `smartrecruiters` | `interikeagroup` | Supply Planner |
| Intuitive | www.intuitive.com | `smartrecruiters` | `intuitive` | Executive Projects and Communication Manager |
| IQ-EQ | iqeq.com | `smartrecruiters` | `iqeq` | Accounts Payable Associate |
| ixigo | ixigo.com | `smartrecruiters` | `ixigo` | DevOps Engineer |
| J.S. Held LLC | jsheld.com | `smartrecruiters` | `jsheldllc` | Associate Director |
| Jitterbit |  | `smartrecruiters` | `jitterbit` | Software QA Engineer |
| John Crane | johncrane.com | `smartrecruiters` | `smithsgroup2` | Global Engineering Manager |
| Konecranes | konecranes.com | `smartrecruiters` | `konecranes` | Engineer Trainee |
| lastminute.com |  | `smartrecruiters` | `lastminutecom` | Telesales Agent |
| Lesaffre |  | `smartrecruiters` | `lesaffre` | Process Automation Engineer |
| LGC Group | lgcgroup.com | `smartrecruiters` | `lgcgroup` | Alliance and Market Expansion Manager |
| LinkedIn |  | `smartrecruiters` | `linkedin3` | Automation Developer |
| Lokal |  | `smartrecruiters` | `lokal` | Admin Executive |
| Louis Dreyfus Company | www.ldc.com | `smartrecruiters` | `louisdreyfuscompany` | Executive SHE |
| M3USA |  | `smartrecruiters` | `m3usa` | Zendesk Administrator |
| Maskoid Technologies | maskoidtechnologies.com | `smartrecruiters` | `maskoidtechnologies` | Human Resources Executive |
| Masters India Private Limited | mastersindia.co | `smartrecruiters` | `mastersindiaprivatelimited` | GST Customer Success Executive |
| Mattel | mattel.com | `smartrecruiters` | `mattelinc` | Service Desk Agent |
| METRO AG | metroag.de | `smartrecruiters` | `metromakro` | Team Lead - Indirect Procurement |
| METRO Global Solution Center | metro-gsc.in | `smartrecruiters` | `metromakro` | IT Infrastructure Team Lead |
| METRO.digital | metro.digital | `smartrecruiters` | `metromakro` | Solution Expert |
| Microchip |  | `smartrecruiters` | `microchip` | Technical Staff Engineer |
| MicroStrategy | www.microstrategy.com | `smartrecruiters` | `microstrategy1` | Software Engineer |
| Mirantis | mirantis.com | `smartrecruiters` | `mirantis` | Automation Software Tester |
| Miratech | miratech.com | `smartrecruiters` | `miratech1` | AI Specialist |
| Mountfitchet Group |  | `smartrecruiters` | `mountfitchetgroup` | Charter Sales Consultant |
| MSX International | msxi.com | `smartrecruiters` | `msxinternational` | Diagnostic Software Support Engineer |
| Nagarro | nagarro.com | `smartrecruiters` | `nagarro1` | AI Architect |
| NEC Software Solutions India | necsws.com | `smartrecruiters` | `necsws` | Test Lead |
| Nexthink | nexthink.com | `smartrecruiters` | `nexthink` | Professional Services Consultant |
| Nielsen | nielsen.com | `smartrecruiters` | `thenielsencompany` | Data Engineer |
| NielsenIQ | nielseniq.com | `smartrecruiters` | `nielseniq` | Software Engineer |
| NopAdvance LLP |  | `smartrecruiters` | `nopadvancellp` | Business Development Executive |
| Oetiker |  | `smartrecruiters` | `oetiker` | Tool Manufacturing Process |
| Outpost VFX |  | `smartrecruiters` | `outpostvfx` | Environment Generalist |
| PetroBot Technologies Pvt Ltd |  | `smartrecruiters` | `petrobottechnologiespvtltd` | Mechanical Design Engineer |
| Petsfolio |  | `smartrecruiters` | `petsfolio2` | Recruiter Intern |
| PHONEPE LIMITED | phonepe.com | `smartrecruiters` | `phonepelimited` | Engineering Manager |
| PhonePe Wealth Broking | share.market | `smartrecruiters` | `phonepelimited` | Product Designer |
| Pixel Web Solutions | pixelwebsolutions.com | `smartrecruiters` | `pixelwebsolutions` | Business Development Executive |
| Playto Labs |  | `smartrecruiters` | `playtolabs` | Business Development Representative |
| Pramira Inc | pramira.com | `smartrecruiters` | `pramirainc` | Finance Executive |
| Primark | primark.com | `smartrecruiters` | `primark` | FP&A Manager |
| Progress Rail | progressrail.com | `smartrecruiters` | `progressrail` | Maintenance Technician |
| PromptCloud |  | `smartrecruiters` | `promptcloud` | Content & Growth Associate |
| PSI CRO |  | `smartrecruiters` | `psicro` | Project Finance Manager |
| QAD, Inc. | qad.com | `smartrecruiters` | `qadinc` | AI Specialist |
| Qantas Group | qantas.com | `smartrecruiters` | `qantasgroup` | Safety Manager |
| QIMA | qima.com | `smartrecruiters` | `qima` | Compliance Associate |
| Quantazone |  | `smartrecruiters` | `quantazone` | Sales Intern |
| Radisson Hotel Group | radissonhotels.com | `smartrecruiters` | `rhg` | Sales Manager |
| Ramboll | ramboll.com | `smartrecruiters` | `ramboll3` | Waste Engineer |
| Rede Consulting Services | rede-consulting.com | `smartrecruiters` | `redeconsultingservices` | Business Development Executive |
| Renesas Electronics | www.renesas.com | `smartrecruiters` | `renesaselectronics` | Analog Engineer |
| Rexel India Private Limited | rexel.com | `smartrecruiters` | `rexel1` | Design Engineer |
| RMgX Technologies LLP | rmgx.in | `smartrecruiters` | `rmgxtechnologiesllp` | Product Manager |
| Rock and Art UK |  | `smartrecruiters` | `rockandartuk` | Cultural Content Writer |
| Rodeo FX | rodeofx.com | `smartrecruiters` | `rodeofx` | Open Application |
| Rotork | rotork.com | `smartrecruiters` | `rotork1` | D365 Operations Subject Matter Expert |
| SanDisk | sandisk.com | `smartrecruiters` | `sandisk` | VLSI Design Engineer |
| Sara Infoway.in | addiwise.com | `smartrecruiters` | `sarainfowayin` | Clinical Digital Process Specialist |
| Sectigo | sectigo.com | `smartrecruiters` | `sectigo` | Salesforce Administrator |
| SGS | sgs.com | `smartrecruiters` | `sgs` | Data Management Specialist |
| Sia | sia-partners.com | `smartrecruiters` | `sia` | Backend Engineer |
| Sia Partners |  | `smartrecruiters` | `sia` | ML-Ops |
| Sika AG | sika.com | `smartrecruiters` | `sikaag` | Program Manager |
| Silvaco | silvaco.com | `smartrecruiters` | `silvaco1` | Total Rewards Analyst |
| SIXT | sixt.com | `smartrecruiters` | `sixt` | Security Engineer |
| SmartDev |  | `smartrecruiters` | `smartdev1` | Business Development Manager |
| Smiths Group | smiths.com | `smartrecruiters` | `smithsgroup2` | Software Test Engineer |
| Sociabble | www.sociabble.com | `smartrecruiters` | `sociabble` | Customer Account Manager |
| SOMFY Group | somfy.com | `smartrecruiters` | `somfygroup` | Solution Architect |
| Sopra Steria |  | `smartrecruiters` | `soprasteria1` | Command Centre Operator |
| Stäubli | staubli.com | `smartrecruiters` | `staubligroup` | Sales Engineer |
| Sutherland | sutherlandglobal.com | `smartrecruiters` | `sutherland` | CyberArk Architect |
| SW Group | swgroup.com | `smartrecruiters` | `swgroup` | Architect |
| Swiggy | swiggy.com | `smartrecruiters` | `swiggy` | Sales Manager |
| Syngenta Group | syngenta.com | `smartrecruiters` | `syngentagroup` | Data Solutions Architect |
| T-Systems ICT India Pvt. Ltd. | t-systems.com | `smartrecruiters` | `t-systemsictindiapvtltd1` | Full Stack Architect |
| TAPI |  | `smartrecruiters` | `tapi` | EHS Specialist |
| Tawazon Chemical Co. LLC | tawazon.com | `smartrecruiters` | `ghobashgroup` | Finance Manager |
| Techfaya Innovations Pvt Ltd | fayausa.com | `smartrecruiters` | `techfayainnovationspvtltd` | QA |
| TechVedika | www.techvedika.com | `smartrecruiters` | `techvedika` | Cloud Native Architect |
| Telefonica Tech | telefonicatech.com | `smartrecruiters` | `telefonicatech` | Dynamics 365 Support Engineer |
| Tieto Caretech | tieto.com | `smartrecruiters` | `tieto2` | Software Engineer |
| TRS Forms & Services Pvt Ltd |  | `smartrecruiters` | `trsformsservicespvtltd` | Scanning Operator |
| Trustonic | trustonic.com | `smartrecruiters` | `trustonic` | Technical Account Manager |
| TSS Consultancy Pvt. Ltd. | trackwizz.com | `smartrecruiters` | `tssconsultancypvtltd` | IT Administrator |
| Turner & Townsend | turnerandtownsend.com | `smartrecruiters` | `turnertownsend` | Assistant Project Manager |
| Ubisoft | ubisoft.com | `smartrecruiters` | `ubisoft2` | R&D Engineer |
| Umdasch Group |  | `smartrecruiters` | `umdaschgroup` | Procurement and Quality Engineer |
| Unify Dots |  | `smartrecruiters` | `unifydots` | Accounting Manager |
| Velotic | velotic.com | `smartrecruiters` | `cieloprojects` | HR Operations Analyst |
| Veolia Water Technologies | veoliawatertechnologies.com | `smartrecruiters` | `veoliaenvironnementsa` | Design Engineer |
| Version 1 | version1.com | `smartrecruiters` | `version1` | Oracle Fusion Data Intelligence Support Consultant |
| Wabtec | wab­teccorp.com | `smartrecruiters` | `wabtec` | M365 |
| Western Sydney University | westernsydney.edu.au | `smartrecruiters` | `westernsydneyuniversity` | Chief Operating Officer |
| Wise | wise.com | `smartrecruiters` | `wise` | Internal Audit Manager |
| Wizikey |  | `smartrecruiters` | `wizikey` | Sales Manager |
| WNS Global Services |  | `smartrecruiters` | `wnsglobalservices144` | Assistant Manager - Operations |
| XP Power |  | `smartrecruiters` | `xppower2` | Applications Engineer |
| Xplor | xplor.com | `smartrecruiters` | `xplor` | Software Engineer |

### `adhoc` — 137 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Actinium Pharmaceuticals, Inc. | actiniumpharma.com | `adhoc` | `actiniumpharma` | General Manager |
| AECOM | aecom.com | `adhoc` | `aecom` | Project Engineer |
| Aerogen | aerogen.com | `adhoc` | `aerogen` | Territory Manager |
| Alfa Laval | alfalaval.com | `adhoc` | `alfalaval` | Unit Manager |
| Alibaba Cloud | alibabacloud.com | `adhoc` | `alibaba` | AI Agent Research and Development Engineer |
| Allergan Aesthetics, an AbbVie company | www.allerganaesthetics.com | `adhoc` | `abbvie` | Key Account Specialist |
| ALPLA | alpla.com | `adhoc` | `alpla` | Administration Executive |
| Amentum | amentum.com | `adhoc` | `amentumcareers` | Custodial Crew Leader |
| Angel One | angelone.in | `adhoc` | `angleone` | Product Analyst |
| Angleone | www.angelone.in | `adhoc` | `angleone` | Software Development Engineer |
| AO Kaspersky Lab | kaspersky.com | `adhoc` | `ao_kaspersky_lab` | Customer Success Engineer |
| APM Terminals | apmterminals.com | `adhoc` | `maersk` | Inventory Controller |
| Apple | apple.com | `adhoc` | `apple` | Site Reliability Engineer |
| ARaymond | www.araymond.com | `adhoc` | `araymond` | Team Member |
| Arm | arm.com | `adhoc` | `arm` | Design Engineer |
| ASUSTeK Computer Inc. | asus.com | `adhoc` | `asus` | Supply Chain Manager |
| ATS Global | ats-global.com | `adhoc` | `ats_global` | Presales and Proposals |
| Bacardi Limited | bacardilimited.com | `adhoc` | `bacardilimited` | Advocacy Manager |
| Baxter | baxter.com | `adhoc` | `baxter` | Regulatory Affairs Specialist |
| Becton Dickinson & Company | bd.com | `adhoc` | `bd` | Quality Continuous Improvement Partner |
| Beiersdorf | beiersdorf.com | `adhoc` | `beiersdorf` | Business Analyst |
| BLEND | getblend.com | `adhoc` | `getblend_freelancers` | Translator |
| BoomerangFX | boomerangfx.com | `adhoc` | `boomerangfx` | Account Executive |
| Brown-Forman | brown-forman.com | `adhoc` | `brown_forman` | Field Sales Manager |
| ByteDance | www.bytedance.com | `adhoc` | `bytedance` | HR Business Partner Intern |
| Capital One | capitalone.com | `adhoc` | `capitalonecareers` | Business Analyst |
| Casepoint | casepoint.com | `adhoc` | `casepoint` | Software Tester |
| Catalyst Now | catalystnow.net | `adhoc` | `catalystnow` | Learning Initiatives Fellow |
| Caterpillar | caterpillar.com | `adhoc` | `caterpillar` | Procurement Engineer |
| CCL Design | ccldesign.com | `adhoc` | `ccldesign` | Process Engineer |
| ChopArt | chopart.org | `adhoc` | `chopart` | Management Intern |
| CleanStart | cleanstart.com | `adhoc` | `cleanstart` | Finance Executive |
| Concentrix | concentrix.com | `adhoc` | `concentrix` | Quality Analyst |
| Cotecna | www.cotecna.com | `adhoc` | `cotecna` | Testing Engineer |
| Coursera | www.coursera.org | `adhoc` | `coursera` | Channel Sales Manager |
| Crisil | www.crisil.com | `adhoc` | `crisil` | Intern |
| DoorDash | www.doordash.com | `adhoc` | `doordash` | IT Support Specialist |
| Dow Jones | dowjones.jobs | `adhoc` | `newscorp` | Software Engineer |
| eGain Corporation | egain.com | `adhoc` | `egain` | Software Engineer |
| Eightfold AI | eightfold.ai | `adhoc` | `eightfold` | Agentic Adoption Partner |
| EisnerAmper | eisneramper.com | `adhoc` | `eisneramper` | Tax Administration Coordinator |
| EPAM Systems, Inc. | epam.com | `adhoc` | `epam_systems` | Software Engineer |
| Equinix, Inc. | equinix.com | `adhoc` | `equinix` | Software Engineer |
| Fidelity Investments | fidelity.com | `adhoc` | `fidelity` | Product Manager |
| Fine Organic Industries | fineorganics.com | `adhoc` | `fineorganics` | Sales Manager |
| Flowserve Corporation | flowserve.com | `adhoc` | `flowserve` | Engineering Supervisor |
| Foxconn | www.foxconn.com | `adhoc` | `foxconn` | Network Engineer |
| Fugro | fugro.com | `adhoc` | `fugro` | Business Information Security Officer |
| Fusion CX | fusioncx.com | `adhoc` | `fusion_cx` | Small Business Owner |
| Gap Inc. | gapinc.com | `adhoc` | `gap` | Data Engineer |
| Global Affairs Canada | international.gc.ca | `adhoc` | `global_affairs_canada_les` | Program Assistant |
| GlobalData | globaldata.com | `adhoc` | `globaldata` | Customer Success Executive |
| GlobalLogic Inc. | www.globallogic.com | `adhoc` | `globallogic` | Hebrew Language Expert |
| Goldman Sachs | goldmansachs.com | `adhoc` | `goldman_sachs` | Compensation Accounting Analyst |
| Grove Labs | grove.finance | `adhoc` | `grove` | Legal Counsel |
| Guntner Asia Pacific Pte Ltd | guntner.com | `adhoc` | `guntner` | Sales Manager |
| H&M | hm.com | `adhoc` | `hm` | Department Manager |
| H.B. Fuller | hbfuller.com | `adhoc` | `hbfuller` | Sales Professional |
| Halliburton | halliburton.com | `adhoc` | `halliburton` | Payroll Specialist |
| Hemmersbach GmbH & Co. KG | hemmersbach.com | `adhoc` | `hemmersbach` | Project Assistant |
| Hitachi Energy | hitachienergy.com | `adhoc` | `hitachienergy` | Contract Manager |
| Hitachi Vantara | hitachivantara.com | `adhoc` | `hitachivantara` | Salesforce Support and Administration Analyst |
| IMC | imc.com | `adhoc` | `imc` | Operations Trader |
| IMI | www.imiplc.com | `adhoc` | `imiplc` | Project Planner and Production Controller |
| IntelliCAD Technology Consortium | intellicad.org | `adhoc` | `intellicad` | Developer/Programmer |
| Intuit | intuit.com | `adhoc` | `intuit` | Staff Engineer |
| iQor | iqor.com | `adhoc` | `iqor` | Agent |
| IxDF | ixdf.org | `adhoc` | `ixdf` | Course Writer and Editor |
| Johnson Controls | johnsoncontrols.com | `adhoc` | `johnsoncontrols` | CAD PLM Lead |
| Key AI | key.ai | `adhoc` | `key` | UI/UX Designer |
| Korn Ferry | kornferry.com | `adhoc` | `korn_ferry` | Recruiter |
| Linedata | www.linedata.com | `adhoc` | `linedata` | Digital Marketing Manager |
| Lionbridge | lionbridge.com | `adhoc` | `lionbridge` | Cloud Engineer |
| Louis Vuitton | louisvuitton.com | `adhoc` | `louis_vuitton` | Client Relations and Experience Manager |
| MediaTek | mediatek.com | `adhoc` | `mediatek` | RTL Design |
| Merck KGaA, Darmstadt, Germany | emdgroup.com | `adhoc` | `merck_bewerbung` | Statistical Programmer |
| Meta | meta.com | `adhoc` | `meta` | Silicon Power Architect |
| Mitsui & Co., Ltd. | mitsui.com | `adhoc` | `mitsui_japan_career` | Trading Operations Specialist |
| Moody's | moodys.com | `adhoc` | `moodys` | Data Engineering Manager |
| MoveInSync | moveinsync.com | `adhoc` | `moveinsync` | Site Lead |
| Moët Hennessy |  | `adhoc` | `lvmh` | Marketing Executive |
| Network Innovations | networkinnovations.com | `adhoc` | `networkinnovations` | Director of Business Development |
| News Corp | newscorp.com | `adhoc` | `newscorp` | Analyst, Indirect Sourcing Generalist |
| Nobel Biocare | nobelbiocare.com | `adhoc` | `envistaco` | HR Executive |
| NRI Group | www.nri.com | `adhoc` | `jposting` | Management Consultant |
| Nutreco | nutreco.com | `adhoc` | `nutreco` | Factory Lead |
| OMNITAAS | omnitaas.com | `adhoc` | `omnitaas` | Software Engineer |
| Paperguide | paperguide.ai | `adhoc` | `paperguide_reviewer_program` | Research Reviewer |
| Park Hyatt | park.hyatt.com | `adhoc` | `park_hyatt` | Chef de Cuisine |
| Paylocity |  | `adhoc` | `paylocity_careers` | Test Engineer |
| Pearson | plc.pearson.com | `adhoc` | `pearson` | Program Coordinator Operations |
| Playrix | playrix.com | `adhoc` | `playrix` | Game Designer |
| Point72 | point72.com | `adhoc` | `point72` | Cloud Computing Engineer |
| PRACTICING MUSICIAN, S.P.C. | practicingmusician.com | `adhoc` | `practicing_musician` | Music Teacher |
| Pratham | pratham.org | `adhoc` | `pratham` | Content and Training Associate |
| Quaker Houghton | quakerhoughton.com | `adhoc` | `quakerhoughton` | Marketing Assistant |
| REA Group |  | `adhoc` | `newscorp` | Account Manager |
| Red Bull | www.redbull.com | `adhoc` | `redbull` | Territory Sales Manager |
| Rengo Studio | rengo.studio | `adhoc` | `rengo` | Voice Actor |
| Rolls-Royce | www.rolls-royce.com | `adhoc` | `rolls_royce` | Accounts Payable Team Lead |
| rtCamp Inc. | rtcamp.com | `adhoc` | `rtcamp` | Manager, Founder's Office |
| Safran | safran-group.com | `adhoc` | `safran_group` | Tooling Design and Manufacturing Engineer |
| Sagility | sagilityhealth.com | `adhoc` | `sagilityhealth` | Executive - Clinical |
| Semrush | semrush.com | `adhoc` | `semrush` | Account Executive |
| Sephora | sephora.com | `adhoc` | `lvmh` | Supply Chain Business Partner |
| ServiceNow | servicenow.com | `adhoc` | `servicenow` | UX Researcher |
| Shopify | shopify.com | `adhoc` | `shopify` | Event Marketing Lead |
| Signzy | www.signzy.com | `adhoc` | `signzy` | PMO Manager |
| SMS group | www.sms-group.com | `adhoc` | `sms_group` | Automation Engineer |
| Sodexo India | in.sodexo.com | `adhoc` | `sodexo_india` | Housekeeping Associate |
| Stantec | stantec.com | `adhoc` | `stantec` | Civil 3D Designer |
| TaskUs | taskus.com | `adhoc` | `taskus` | Director of Operations |
| Tata Consultancy Services | tcs.com | `adhoc` | `tcs_ibegin` | Full Stack Developer |
| Tencent | www.tencent.com | `adhoc` | `tencent` | Public Affairs Manager |
| Tesla | tesla.com | `adhoc` | `tesla` | Management Trainee |
| The Cinema Spot | thecinemaspot.com | `adhoc` | `thecinemaspot` | Reporter |
| The Hartford | thehartford.com | `adhoc` | `the_hartford` | Quality Engineer |
| TherapyMantra | therapymantra.co | `adhoc` | `therapymantra` | HR Intern |
| thyssenkrupp nucera | thyssenkrupp-nucera.com | `adhoc` | `new_era_is_you` | Instrumentation Engineer |
| TIAA | tiaa.org | `adhoc` | `tiaa` | Financial Planning and Analysis Analyst |
| TikTok | www.tiktok.com | `adhoc` | `tiktok` | Network Performance Lead |
| Topsoe | topsoe.com | `adhoc` | `topsoe` | Specialist |
| Trilogy | trilogy.com | `adhoc` | `crossover` | Enterprise Renewals Executive |
| Umicore | umicore.com | `adhoc` | `umicore` | Machine Learning Engineer |
| United Nations | un.org | `adhoc` | `united_nations` | Consultant |
| United Nations Volunteers (UNV) | www.unv.org | `adhoc` | `unv` | Programme Officer |
| Vanguard | corporate.vanguard.com | `adhoc` | `vanguardjobs` | Application Engineering Technical Lead |
| Vera Solutions | verasolutions.org | `adhoc` | `vera_solutions` | Product Intern |
| Verbling | verbling.com | `adhoc` | `verbling` | Language Teacher |
| Verdantas | verdantas.com | `adhoc` | `keka` | Data Analyst |
| VoiceLessons | voicelessons.com | `adhoc` | `voicelessons` | Voice Teacher |
| Welocalize |  | `adhoc` | `welo_global_manatal` | AI Translation Trainer |
| Whole Mission | mmnfp.com | `adhoc` | `mmnfp` | Marquette Method Teacher |
| Wingify Software Pvt. Ltd. | wingify.com | `adhoc` | `wingify` | Customer Success Manager |
| Worldpay | worldpay.com | `adhoc` | `worldpay` | Development Manager |
| YAGEO Group | yageogroup.com | `adhoc` | `yageogroup` | Information Technology Support Engineer |
| Yum Brands | www.yum.com | `adhoc` | `yum_brands` | Finance Analyst |

### `bamboohr` — 98 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Access Now |  | `bamboohr` | `accessnow` | Incident Response Analyst |
| ACLED | acleddata.com | `bamboohr` | `acleddata` | Visualization and Digital Communication Specialist |
| AIM Solder | aimsolder.com | `bamboohr` | `aimsolder` | Technical Support Engineer |
| Alkira | alkira.com | `bamboohr` | `alkira` | Software Engineer |
| Anaqua | anaqua.com | `bamboohr` | `anaqua` | Product Owner |
| Atlas Systems | atlassystems.com | `bamboohr` | `atlas` | MySQL Database Administrator |
| Avantpage, Inc. |  | `bamboohr` | `avantpage` | Project Manager |
| Axios International |  | `bamboohr` | `axiosint` | Patient Care Coordinator |
| BARE International | bareinternational.in | `bamboohr` | `bare` | Mystery Evaluator |
| Benchmark Gensuite |  | `bamboohr` | `benchmarkgensuite` | Product Developer Associate |
| Bits In Glass |  | `bamboohr` | `bitsinglassca` | Databricks Solution Architect |
| Brave Bison |  | `bamboohr` | `bravebison` | Business Manager |
| Caribou | caribou.global | `bamboohr` | `caribou` | Director, Measurement & Impact |
| Channelscaler |  | `bamboohr` | `channelscaler` | Vice President of Engineering |
| Cineverse |  | `bamboohr` | `cineverse` | Financial Reporting Analyst |
| CLARITY |  | `bamboohr` | `claritycx` | QA Consultant |
| Climate Policy Initiative | climatepolicyinitiative.org | `bamboohr` | `climatepolicy` | Partnerships Coordinator |
| Cornelis Networks, Inc. |  | `bamboohr` | `cornelisnetworks` | Technical Support Engineer |
| CXM |  | `bamboohr` | `cxm` | CRM Marketing Manager |
| CXM Group | cxm.com | `bamboohr` | `cxm` | Account Executive |
| Cybeats |  | `bamboohr` | `cybeats` | Technical Customer Success Manager |
| Digital.ai | digital.ai | `bamboohr` | `digitalai` | Business Development Representative |
| Duelbits |  | `bamboohr` | `duelbits` | Director of VIP |
| E3G | e3g.org | `bamboohr` | `e3g` | Programme Lead |
| EdgeCortix |  | `bamboohr` | `edgecortix` | UCIe Verification Engineer |
| Exa |  | `bamboohr` | `exa` | Telco NMS Developer |
| Exaze |  | `bamboohr` | `exaze` | Full Stack Developer |
| Fika |  | `bamboohr` | `fika` | Portfolio Operations and Planning Manager |
| Fresche Solutions |  | `bamboohr` | `freschesolutions` | Head of Lead Generation |
| Fueling Brains & FB Academies |  | `bamboohr` | `kidsu` | Sales & Admissions Advisor |
| Fulkrum |  | `bamboohr` | `fulkrum` | QC Coordinator |
| Funds-Axis |  | `bamboohr` | `fundsaxis` | SOC & Compliance Analyst |
| Gamingtec |  | `bamboohr` | `gamingtec` | Business Development Manager |
| Gentrack | gentrack.com | `bamboohr` | `gentrack` | Software Engineer |
| Giti2c |  | `bamboohr` | `hrforyou` | Data Analyst |
| GoCharting |  | `bamboohr` | `gocharting` | Integrated Marketing Manager |
| Good Business Lab |  | `bamboohr` | `gblhr` | Field Consultant |
| GoSaaS | gosaas.ai | `bamboohr` | `gosaas` | Solution Architect |
| GreenTomatoMedia LLC |  | `bamboohr` | `greentomatomedialimited` | UI/UX and Visual Designer |
| Hapana |  | `bamboohr` | `hapana` | Onboarding Specialist |
| HeadSpin |  | `bamboohr` | `headspin` | Software Engineer |
| ID Medical |  | `bamboohr` | `idmedical` | Recruiting Assistant |
| Illumynt |  | `bamboohr` | `illumynt` | Technician |
| ILSC Education Group |  | `bamboohr` | `ilsc` | Administrative Coordinator |
| Index Engines |  | `bamboohr` | `indexengines` | Software Engineering Manager |
| Infotechtion |  | `bamboohr` | `infotechtion` | Power Platform Developer |
| JMT Consultants |  | `bamboohr` | `jmtconsultants` | Human Resources Manager |
| Jord International |  | `bamboohr` | `jord` | Project Engineer |
| Keystone Bookkeepers | keystonebookkeepers.com | `bamboohr` | `keystonebookkeepers` | Software Engineer |
| LATRO |  | `bamboohr` | `latro` | Product Manager |
| Law In Order |  | `bamboohr` | `lawinorder` | LPO Associate |
| Longulf Trading |  | `bamboohr` | `longulf` | Business Development Manager |
| Loyalty Juggernaut, Inc | www.lji.io | `bamboohr` | `lji` | Analyst |
| LXT | lxt.ai | `bamboohr` | `lxt` | Language Freelancer |
| M&S Logistics |  | `bamboohr` | `mslogisticsltd` | Customer Operations Coordinator |
| Malbek |  | `bamboohr` | `malbek` | CLM Consultant |
| MarcoPolo Learning |  | `bamboohr` | `marcopololearning` | Product Marketer |
| Marrina Decisions |  | `bamboohr` | `marrinadecisions` | Project Coordinator |
| Navitas | navitas.com | `bamboohr` | `navitasgsm` | Admissions Officer |
| Noora Health |  | `bamboohr` | `noorahealth` | Program Coordinator |
| Olea |  | `bamboohr` | `olea` | Associate Director, Trade Operations |
| OLR |  | `bamboohr` | `olr` | Delivery Director |
| Operative |  | `bamboohr` | `operative` | IT Engineer |
| Outseer |  | `bamboohr` | `outseer` | Director, Software Engineering |
| Pink Elephant | pink-elephant.co | `bamboohr` | `pinkelephant` | CFO |
| Precision Development |  | `bamboohr` | `precisiondev` | Technical Program Manager |
| Prescient Healthcare Group |  | `bamboohr` | `prescienthg` | AI Engineer |
| Prescient Security |  | `bamboohr` | `prescientsecurity` | ISO Lead Auditor |
| Pula |  | `bamboohr` | `pula` | Field Coordinator |
| QS Quacquarelli Symonds | qs.com | `bamboohr` | `qs` | TNE Project Manager |
| Quvia | quvia.ai | `bamboohr` | `quvia` | Data Science Engineer |
| Red Nucleus |  | `bamboohr` | `rednucleus` | Consultant |
| Relief International |  | `bamboohr` | `ri` | Data Analytics and ERP Consultant |
| SAI Group Ltd |  | `bamboohr` | `saigroups` | Python API Developer |
| SAI360 | sai360.com | `bamboohr` | `sai360` | Solution Developer |
| Scorpio Group |  | `bamboohr` | `scorpiogroup` | Internal Communications Consultant |
| SeeCubic | seecubic.com | `bamboohr` | `seecubic` | Human Resources Executive |
| SiGMA Group |  | `bamboohr` | `sigmaworld` | FX Sales Manager |
| Sistema.bio |  | `bamboohr` | `sistemaaccount` | Business Development Manager |
| Sitero LLC |  | `bamboohr` | `sitero` | Medical Reviewer |
| Smile Train | smiletrain.org | `bamboohr` | `smiletrain` | Education and Training Intern |
| Snic Solutions |  | `bamboohr` | `snicsolutions` | Customer Success Lead |
| Stellar Tech |  | `bamboohr` | `stellartech` | User Acquisition Manager |
| STS | sts-certified.com | `bamboohr` | `stscertified` | Inspector |
| Summa Linguae Technologies |  | `bamboohr` | `datamundi` | Business Email Contributor |
| Sunpan |  | `bamboohr` | `sunpan` | CRM & Marketing Automation Specialist |
| systemsGo |  | `bamboohr` | `systemsgo` | AV Consultant |
| Telum Media Group Pte Ltd |  | `bamboohr` | `telummedia` | Automation QA Engineer |
| The Earthshot Prize |  | `bamboohr` | `earthshotprize` | Social Media Manager |
| The Straits Network |  | `bamboohr` | `tsn` | Client Solutions Analyst/Associate |
| Tricon Energy |  | `bamboohr` | `triconenergy` | Operations Analyst |
| Valocity |  | `bamboohr` | `valocityglobal` | Operations Manager |
| Vendasta | vendasta.com | `bamboohr` | `vendasta` | SEO Services Team Lead |
| Virtuozzo | virtuozzo.com | `bamboohr` | `virtuozzo` | BI Specialist |
| Volante Technologies |  | `bamboohr` | `volanteoneteam` | Director, Cloud Infrastructure |
| Waystone | waystone.com | `bamboohr` | `waystone` | Company Secretarial Associate |
| Welldoc Inc |  | `bamboohr` | `welldoc` | Business Development |
| ZeroFOX |  | `bamboohr` | `zerofox` | Platform Support Specialist |

### `teamtailor` — 90 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| 3Shape | careers.3shape.com | `teamtailor` | `3shape` | Technical Support Consultant |
| A&O IT Group | aoitgroup.com | `teamtailor` | `aoitgroup-1719309706` | Service Desk Agent |
| Adform | careers.adform.com | `teamtailor` | `adform` | Engineering Manager |
| AG Solution | agsolutiongroup.com | `teamtailor` | `sofyne-ag-solution` | OT Project Manager |
| Agrocorp International | agrocorpinternational.com | `teamtailor` | `agrocorpinternational` | Commodity Accountant |
| Apex Operations | careers.apexops.sa | `teamtailor` | `taeyenhrservices` | Cleaner |
| Archetype | archetype.co | `teamtailor` | `archetype.na` | Consultant |
| Argus Media | careers.argusmedia.com | `teamtailor` | `argusmedia` | HRIS |
| Autoliv Group | careerindia.autoliv.com | `teamtailor` | `autolivgroup` | Production Specialist |
| Avenga | avenga.com | `teamtailor` | `avenga` | Kony Engineer |
| BearingPoint India | bearingpoint.com | `teamtailor` | `bearingpointindia` | SAP BRIM Functional Consultant |
| Bernhard Schulte Shipmanagement | bs-shipmanagement.com | `teamtailor` | `bsm` | Fleet Personnel Officer |
| Betolar India Private Limited | betolar.com | `teamtailor` | `betolaroyj` | Technical Sales Executive |
| Brut India | brutindia.teamtailor.com | `teamtailor` | `brutindia` | Accountant |
| BSM Cruise | bsm-cruise.com | `teamtailor` | `bsm-bsm-cruise` | Fleet Personnel Officer |
| Busuu |  | `teamtailor` | `busuu` | Online Teacher |
| C Teleport | careers.cteleport.com | `teamtailor` | `cteleport` | Customer Support Agent |
| Causeway Technologies |  | `teamtailor` | `causeway-1588594217` | Consultant |
| Charcoalblue | charcoalblue.com | `teamtailor` | `charcoalblue` | Technical Producer |
| Clicks Talent | clickstalent.com | `teamtailor` | `clickstalentbv-1749060007` | Talent Agent |
| Clinisys | clinisys.com | `teamtailor` | `clinisys` | Regulatory Affairs Analyst |
| Collinson | collinsongrouptalent.com | `teamtailor` | `collinsongroup` | SecOps Engineer |
| Corsearch | corsearch.com | `teamtailor` | `corsearch` | Investigation Support Analyst |
| Crimson Education | jobs.crimsoneducation.org | `teamtailor` | `crimsoneducation` | Alumni Network |
| DataForce by TransPerfect | transperfect.com | `teamtailor` | `dataforcebytransperfect.na` | Marathi Voice Data Contributor |
| DermaDream | mydermadream.com | `teamtailor` | `dermadream.na` | Outbound Sales Customer Service |
| DrDoctor | drdoctor.teamtailor.com | `teamtailor` | `drdoctor` | Designer |
| Ensto | ensto.com | `teamtailor` | `ensto` | Category Sourcing Specialist |
| Ethena Labs | ethena.fi | `teamtailor` | `ethenalabs` | Engineering Manager |
| Etraveli Group | etraveligroup.com | `teamtailor` | `etraveligroup` | Team Lead |
| Eurofragance | careers.eurofragance.com | `teamtailor` | `eurofragance` | Quality Control Team Lead |
| Fergas Group |  | `teamtailor` | `skillrekryteringbemanningab` | Product Manager |
| Fortaegis Technologies | fortaegis.com | `teamtailor` | `fortaegis` | Firmware Security Engineer |
| Full Potential Solutions | fpsinc.com | `teamtailor` | `fullpotentialsolutionslive-1746534510` | Customer Retention Advisor |
| Global University Systems | globaluniversitysystems.com | `teamtailor` | `gusglobaluniversitysystems-global-university-systems` | Creative Copywriter |
| Global University Systems (GUS) |  | `teamtailor` | `gusglobaluniversitysystems` | Marketing Project Coordinator |
| group.one | group.one | `teamtailor` | `groupone` | SEO Manager |
| Holafly | holafly.com | `teamtailor` | `holafly` | Network Operations Manager |
| Humana Spain | humana-spain.org | `teamtailor` | `humanaespana` | International Volunteer |
| Hupo | hupo.co | `teamtailor` | `hupocareers` | Account Executive |
| iLogos Game Studios |  | `teamtailor` | `ilogos` | Business Development Manager |
| Indigo Research | indigoresearch.org | `teamtailor` | `indigoresearch` | General Manager |
| ISMG Careers | ismg.io | `teamtailor` | `ismg.na` | Accountant |
| ISS International SpA |  | `teamtailor` | `issinternational` | I&A (EX) Inspector |
| ITP Media Group | itp.com | `teamtailor` | `itpmediagroup` | Event Sponsorship Sales Manager |
| JATO Dynamics | jato.com | `teamtailor` | `jato-1719413905` | Data Research Specialist |
| Keyrus UK | jobs.keyrus.co.uk | `teamtailor` | `keyrusuk` | Production Support / DevOps Engineer |
| Keywordio | keywordio.com | `teamtailor` | `keywordio` | API Developer |
| Knauf MEASA | careers.knauf.com | `teamtailor` | `knaufoman` | Procurement Specialist |
| LotusFlare | lotusflare.com | `teamtailor` | `careers.lotusflare.com` | Sales Director |
| M+C Saatchi Group | careers.mcsaatchi.com | `teamtailor` | `mcsaatchiltd` | Search Planner |
| Mexens | mexens.com | `teamtailor` | `techniquesolairesarl` | Project Manager |
| MKS PAMP GROUP | mkspamp.com | `teamtailor` | `mkspampgroup` | Technical Drawing and Tooling Warehouse Specialist |
| Moonfrog Labs |  | `teamtailor` | `moonfroglabsbystillfront` | Data Analyst |
| Moove | moove.io | `teamtailor` | `mooveafrica` | Customer Success Executive |
| Mumzworld | mumzworld.com | `teamtailor` | `mumzworld` | E-Commerce Associate |
| NeoXam | www.neoxam.com | `teamtailor` | `careers.neoxam.com` | Service Analyst |
| Nextory | nextory.com | `teamtailor` | `nextory` | Product Analyst |
| Nomia | careers.nomia.com | `teamtailor` | `nomia-1748337075` | AI Engineer |
| Onecom | onecom.co.uk | `teamtailor` | `onecom-1726827950` | Technical Support Specialist |
| Orbia | duraline.com | `teamtailor` | `orbia` | Regional Sales Manager |
| OSOME | careers.osome.com | `teamtailor` | `osome` | Product Marketing Specialist |
| Pentland Brands | careers.pentland.com | `teamtailor` | `pentlandbrandsuk` | DAM Tech Specialist |
| PolyPeptide Group | careers.polypeptide.com | `teamtailor` | `polypeptide` | Mechanical Engineering Apprentice |
| Qureos Inc | qureos.com | `teamtailor` | `qureosinc` | DevOps and Site Reliability Engineer |
| Rejlers Abu Dhabi | rejlers.com | `teamtailor` | `rejlersabudhabi` | Engineer - Rotating and Packages |
| ReOrbit | reorbit.space | `teamtailor` | `reorbit` | Head of Talent Acquisition |
| Sage | sagepub.com | `teamtailor` | `sagepublishing` | Customer Operations Manager |
| Samyak Equipments Pvt. Ltd. |  | `teamtailor` | `qureosinc` | Sales Executive |
| Securitas | securitas.teamtailor.com | `teamtailor` | `securitas` | Proposal Manager |
| SocialPilot | socialpilot.co | `teamtailor` | `saasglobal` | SEO Manager |
| South Pole | southpole.com | `teamtailor` | `southpole` | Compliance Markets Specialist |
| Stark Future | careers.starkfuture.com | `teamtailor` | `starkfuture` | Homologation Engineer |
| Stats Perform | statsperform.com | `teamtailor` | `statsperform` | Salesforce Analyst and Administrator |
| Stillfront |  | `teamtailor` | `stillfrontgroup` | Data Analyst |
| Sumsub | sumsub.com | `teamtailor` | `careers.sumsub.com` | Legal Counsel |
| Tap Payments |  | `teamtailor` | `tappayments` | Plugins Expert |
| TeamViewer Germany GmbH | teamviewer.com | `teamtailor` | `teamviewer` | Software Engineer |
| TEOCO | teoco.com | `teamtailor` | `teoco.na` | Cost Analyst |
| The Customization Group | thecustomizationgroup.com | `teamtailor` | `picanova` | CRM Expert |
| TLC Worldwide |  | `teamtailor` | `tlcworldwide` | Backend Developer |
| TM Forum | tmforum.org | `teamtailor` | `tmforum-1690453371` | Membership Engagement Manager |
| Tripstack | tripstack.com | `teamtailor` | `etraveligroup-tripstack` | Software Engineer |
| Untold Studios | untoldstudios.tv | `teamtailor` | `untoldstdfg1324556` | Production Coordinator |
| Veoneer Safety Systems |  | `teamtailor` | `veoneercareers` | Global Category Manager |
| Veoneer Safety Systems, India | veoneer.com | `teamtailor` | `veoneerin` | Software Development Engineer |
| WirelessCar | wirelesscar.com | `teamtailor` | `wirelesscar-1601021574` | Java Backend Engineer |
| WS Audiology | wsa.com | `teamtailor` | `wsa3` | Technical Project Manager |
| Yodo1 | careers.yodo1.com | `teamtailor` | `yodo` | Game Designer |
| Zanders | zandersgroup.com | `teamtailor` | `zanders` | SAP Treasury Consultant |

### `jazzhr` — 68 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| 3CLogic | 3clogic.com | `jazzhr` | `3clogic` | Service Desk Engineer |
| _able | ablegroup.io | `jazzhr` | `credablegroup` | Partner Success Associate |
| Advantage HQ | advantagehq.com | `jazzhr` | `bmdigital` | Director of Media Operations |
| America & Beyond | americaandbeyond.com | `jazzhr` | `americaandbeyond` | Head Designer |
| Anatta Design | anatta.io | `jazzhr` | `anattadesigninc` | Backend Engineer |
| Antler | antler.co | `jazzhr` | `antler` | Capital Partner |
| Arango | arango.ai | `jazzhr` | `arangodb` | HR Generalist |
| Avasant | avasant.com | `jazzhr` | `avasant` | Research Analyst |
| Bose Professional | bose.com | `jazzhr` | `boseprofessional` | Channel Marketing Specialist |
| Branch International | branch.co | `jazzhr` | `branchinternational` | Machine Learning Engineer |
| BuzzBoard | buzzboard.com | `jazzhr` | `buzzboard` | AI Engineer |
| Centroid Systems, Inc. |  | `jazzhr` | `centroid` | JDE CNC Administrator |
| CG Infinity | cginfinity.com | `jazzhr` | `cginfinity` | Front Desk Receptionist |
| Childcare Marketing Group | childcare.marketing | `jazzhr` | `nojokemarketing1f` | Graphic Designer |
| Concord USA | concordusa.com | `jazzhr` | `concordusa` | Salesforce Data Cloud Developer |
| CPM Holdings, Inc. | onecpm.com | `jazzhr` | `cpmholdingsinc` | Aftermarket Territory Manager |
| CrossBoundary Advisory | crossboundary.com | `jazzhr` | `crossboundary` | Associate Principal |
| Cyzerg | cyzerg.com | `jazzhr` | `cyzerg` | Digital Marketing & Content Specialist |
| Datamatics Technologies | datamaticstechnologies.com | `jazzhr` | `datamaticstechnologies` | Data Architect |
| Digital Green | digitalgreen.org | `jazzhr` | `digitalgreen` | Engineering Manager |
| DiligenceVault | diligencevault.com | `jazzhr` | `diligencevault` | Data Engineer Consultant |
| Ebizon | ebizondigital.com | `jazzhr` | `ebizon` | Frontend React Consultant |
| efficiently | efficiently.com | `jazzhr` | `efficiently` | BIM Mechanical Engineer |
| Finn Partners | finnpartners.com | `jazzhr` | `joinus` | Account Executive |
| Forms+Surfaces Inc | forms-surfaces.com | `jazzhr` | `formssurfaces` | Project Sales Coordinator |
| Foundation AI | foundationai.com | `jazzhr` | `foundationai` | Document Review Analyst |
| Fusemachines | fusemachines.com | `jazzhr` | `fusemachines` | Android Engineer |
| fusionSpan | fusionspan.com | `jazzhr` | `fusionspan` | IT Recruiter |
| Geolog | geolog.com | `jazzhr` | `geologinternationalbvnl817417813b01` | Product Champion for Data Management Services |
| Global LT | global-lt.com | `jazzhr` | `globallt` | Language Teacher |
| H2O.ai | h2o.ai | `jazzhr` | `h2oai` | AI Engineer |
| Hypersonix | hypersonix.ai | `jazzhr` | `hypersonix` | Google Ads Expert |
| iManage | imanage.com | `jazzhr` | `imanagecom` | Full Stack Engineer |
| Innovapptive | innovapptive.com | `jazzhr` | `innovapptive` | Solution Architect |
| IRIUM - Spain |  | `jazzhr` | `iriumspain` | Network Transition and Operations Manager |
| KMK Consulting, Inc. | kmkconsultinginc.com | `jazzhr` | `kmkconsultinginc` | Associate Manager, Incentive Compensation |
| Kramer | kramerav.com | `jazzhr` | `kramerelectronics` | Business Development Manager |
| Kraymer Art |  | `jazzhr` | `kraymerart` | Affiliate Marketing Manager |
| Landmark Group | landmarkgroup.com | `jazzhr` | `rnaresourcegrouplimited` | Assistant Manager |
| Lapmaster Wolters | lapmaster-wolters.com | `jazzhr` | `lapmasterwolters` | Human Resources Executive |
| Learntastic | learntastic.com | `jazzhr` | `learntastic` | Executive Assistant |
| Liberty Mutual | libertymutual.com | `jazzhr` | `libertyinsurance` | Human Resources Manager |
| Lumenci | lumenci.com | `jazzhr` | `lumenci` | Technical Product Lead |
| Measure Marketing Results Inc. | measuremarketing.com | `jazzhr` | `measuremarketingresultsinc` | Link Builder Specialist |
| MyAdvice | myadvice.com | `jazzhr` | `advicemedia` | Web Platform Engineer |
| Neolytix | neolytix.com | `jazzhr` | `neolytix` | Accounts Receivable Team Lead |
| NPS Prism | npsprism.com | `jazzhr` | `npsprism` | Engineering Manager |
| Nucleus Security | nucleussec.com | `jazzhr` | `nucleussecurity` | Site Reliability Engineer |
| Pearl Consulting Group | pearlconsultinggroup.com | `jazzhr` | `pearlconsultinggroup` | Technical Project Manager |
| Pipecare Group | pipecaregroup.com | `jazzhr` | `pipecaregroup` | Chief Accountant |
| PrismHR | prismhr.com | `jazzhr` | `prismhr` | Client Solutions Associate |
| Productive Playhouse | productiveplayhouse.com | `jazzhr` | `productiveplayhouse` | AI Model Rater |
| Qube Cinema | qubecinema.com | `jazzhr` | `qubecinema` | Language Typist |
| Regent College London | ac.uk | `jazzhr` | `regentcollegelondon` | SEO Specialist |
| ServerHub | serverhub.com | `jazzhr` | `serverhubhr` | Linux System Engineer |
| Simeio | simeio.com | `jazzhr` | `simeio` | Identity Engineer |
| Storm Ideas | stormideas.com | `jazzhr` | `stormideas` | Account Executive |
| SweetRush | sweetrush.com | `jazzhr` | `sweetrush` | Workday Techno-Functional Consultant |
| Systel Inc | systelusa.com | `jazzhr` | `systelusa` | CFD Analyst / Designer |
| Translated | translated.com | `jazzhr` | `translated` | Project Manager |
| TRG TECH RESEARCH GROUP Limited | trgint.com | `jazzhr` | `trgintelligencerdsrl` | Sales Manager |
| Trusted Media Brands | trustedmediabrands.com | `jazzhr` | `tmb` | Content Acquisitions Coordinator |
| TurnPoint Technology | turnpoint.tech | `jazzhr` | `turnpointtechnology` | Azure Cloud Engineer |
| Valnet Inc. | valnetinc.com | `jazzhr` | `valnetconcept` | Image Specialist |
| Varel Energy Solutions | varel.com | `jazzhr` | `varelenergysolutions` | Manufacturing Engineering Manager |
| Workplace Options | workplaceoptions.com | `jazzhr` | `workplaceoptions` | EAP Counsellor |
| WRS Health | wrshealth.com | `jazzhr` | `wrshealth` | Strategic Sales Executive |
| Zappsec Inc. | zappsec.com | `jazzhr` | `zappsec` | Growth Marketing & Revenue Operations Manager |

### `rippling` — 67 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Accommodations Plus International | apiglobalsolutions.com | `rippling` | `accommodations-plus-international` | Director, Technical Operations - Infrastructure |
| Advisor360°, LLC |  | `rippling` | `advisor360-llc` | DevOps Engineer |
| Aerospike, Inc. |  | `rippling` | `aerospike-inc` | Solutions Architect |
| Agility PR Solutions | agilitypr.com | `rippling` | `agilitypr` | Talent & Culture Specialist |
| AlaanPay Technology FZCO | alaan.com | `rippling` | `alaan-careers` | Customer Success Manager |
| Ampliwork, Inc |  | `rippling` | `ampliwork-inc` | Production Support Engineer |
| apexanalytix | apexanalytix.com | `rippling` | `apexanalytix-careers` | Architect |
| Ascentt |  | `rippling` | `ascentt-india` | Java Developer |
| Asite |  | `rippling` | `asite` | IT Support Technician |
| Athos Commerce |  | `rippling` | `athos-commerce-careers` | QA Engineer |
| Aubrant Digital |  | `rippling` | `epic-software` | Full Stack Engineer |
| Ayr Energy, Inc. | ayr.energy | `rippling` | `ayr-careers` | Supply Chain Management Engineer |
| Benchmark Construction Technology |  | `rippling` | `benchmark-construction-technology` | Machine Learning Engineer |
| Better Cotton |  | `rippling` | `better-cotton-careers` | Consultant, Climate Change and Natural Resource Management |
| CBTS | cbts.com | `rippling` | `cbtsindia` | DevOps Engineer |
| CData Software |  | `rippling` | `cdata-software` | Principal Software Engineer |
| CData Software, Inc. |  | `rippling` | `cdata-software` | Quality Assurance Automation |
| Clearsulting | clearsulting.com | `rippling` | `clearsultingcareers` | Consulting Analyst |
| Cloud SynApps Inc. |  | `rippling` | `cloud-synapps-inc` | Proposal Analyst |
| CommandLink | commandlink.com | `rippling` | `commandlink` | Software Engineer |
| Consolidated Analytics Private Limited |  | `rippling` | `consolidated-analytics-inc` | Investor Claims Document Specialist |
| Copado | copado.com | `rippling` | `copado` | Customer Success Engineer |
| Current Openings |  | `rippling` | `glengroup` | Graphic Designer |
| Decisions | decisions.com | `rippling` | `decisions` | Software Engineer |
| DESRI | desri.com | `rippling` | `desri-careers` | Risk Management and Insurance Analyst |
| DuploCloud | duplocloud.com | `rippling` | `duplocloud` | Accounts Receivable Specialist |
| EdgeConneX | edgeconnex.com | `rippling` | `edgeconnex` | Financial Planning and Analysis Director |
| Evotix Limited | evotix.com | `rippling` | `evotix-limited` | Finance Administrator |
| Forbes Advisor | forbes.com | `rippling` | `forbes-advisor` | Talent Acquisition Specialist |
| GLEN GROUP | glengroup.ca | `rippling` | `glengroup` | Marketing Director |
| ICP | icpnet.com | `rippling` | `icp-globalcareers` | Digital Asset Coordinator |
| Integrate.com, Inc. |  | `rippling` | `integratecom-inc` | QA Technical Lead |
| iVigee Services |  | `rippling` | `ivigee-services-as` | Software Developer |
| Kore.ai, Inc. | kore.ai | `rippling` | `koreai-india-careers` | Business Development Representative |
| Leo Berwick, LP |  | `rippling` | `leoberwick` | Vice President, M&A Tax |
| loanDNA Private Limited |  | `rippling` | `consulting-and-advisorytechnologyloandna` | Network Support and Asset Management Engineer |
| logcat.ai |  | `rippling` | `logcat-ai` | Member of Technical Staff |
| Logile | logile.com | `rippling` | `logile` | Data Engineer |
| MoneyHash | moneyhash.com | `rippling` | `moneyhash` | Technical Support Engineer |
| Motion |  | `rippling` | `motion` | Customer Support Representative |
| MoxiWorks |  | `rippling` | `moxiworks-careers` | Implementation Specialist |
| MoxiWorks Careers |  | `rippling` | `moxiworks-careers` | Engineering Manager |
| myKaarma | mykaarma.com | `rippling` | `mykaarma` | Software Developer |
| NeoSigma |  | `rippling` | `neosigma` | Product Design Engineer |
| Nomni |  | `rippling` | `nomni` | Full-Stack Engineer |
| Open Positions |  | `rippling` | `vcheck` | Pre-Employment Analyst |
| PCMI, LLC | pcmicorp.com | `rippling` | `pcmi` | Vice President of Operations |
| Perle |  | `rippling` | `perle` | AI Model Training Expert |
| Pythian | pythian.com | `rippling` | `pythian` | AI/ML Engineer |
| Q4 Inc | q4inc.com | `rippling` | `q4_careers` | Data Collection Analyst |
| Radian Generation | radiangen.com | `rippling` | `radian-generation` | Reporting Administrator |
| Rippling |  | `rippling` | `rippling` | Sales Development Representative |
| RSA Security | rsa.com | `rippling` | `rsa-security` | Technical Support Engineer |
| Sibros Technologies | sibros.tech | `rippling` | `sibros-technologies` | Solutions Architect |
| Supplier.io | www.supplier.io | `rippling` | `supplierio` | Business Intelligence Developer |
| TalentNeuron, LLC | talentneuron.com | `rippling` | `talentneuroncareers` | Revenue Operations and Salesforce Analyst |
| ThoughtSpot | www.thoughtspot.com | `rippling` | `thoughtspot` | Founding GTM |
| Tilda Research, Inc. |  | `rippling` | `tilda-research-inc` | AI Harness Engineer |
| TYLsemi, Inc. | tylsemi.com | `rippling` | `tylsemi` | Design Verification Engineer |
| upstream |  | `rippling` | `upstream-tech` | UI/UX Developer |
| VB Spine |  | `rippling` | `vbspineco` | Privacy and GRC Lead |
| Vcheck |  | `rippling` | `vcheck` | Content Writer |
| WEConnect International |  | `rippling` | `weconnect-international` | Business Development Lead |
| WorkSpan |  | `rippling` | `workspan-inc` | HR Operations Executive |
| WorkSpan Inc. |  | `rippling` | `workspan-inc` | Customer Success Manager |
| Workstreet |  | `rippling` | `workstreet` | Internal Auditor |
| Zealie LLC |  | `rippling` | `zealie-llc` | Assistant Director, Payor Relations |

### `dayforce` — 56 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Accuris | accuristech.com | `dayforce` | `accuris___candidateportal___en-us` | Product Manager |
| Acv |  | `dayforce` | `acv___indiacandidateportal___en-ca` | Software Engineering Manager |
| ACV Auctions | acvauctions.com | `dayforce` | `acv___indiacandidateportal___en-ca` | Software Engineer |
| Allyn |  | `dayforce` | `allyn___allynintl___en-us` | IT Developer |
| Amphenol |  | `dayforce` | `amphenol___interconnectproductscareers___en-us` | Financial Analyst |
| Andrew | andrew.com | `dayforce` | `andrew___candidateportal___en-us` | Mechanical Drafter |
| APG & Co | apgandco.com | `dayforce` | `apgandco___124390___en-au` | Production Coordinator |
| CACI Ltd | caci.co.uk | `dayforce` | `caciltd___candidateportal___en-gb` | Network Engineer |
| Caciltd |  | `dayforce` | `caciltd___candidateportal___en-gb` | Data Engineer |
| Chemelex |  | `dayforce` | `chemelex___candidateportal___en-ca` | Construction Manager |
| Converge |  | `dayforce` | `converge___candidateportal___en-ca` | Kafka and Streaming Engineer |
| Corpay | corpay.com | `dayforce` | `corpay___candidateportal___en-ca` | Product Management Director |
| Dayforce | dayforce.com | `dayforce` | `mydayforce___indeedjobs___en-au` | Customer Success Manager |
| Diversified |  | `dayforce` | `diversified___candidateportal___en-us` | Service Desk Agent |
| ECI |  | `dayforce` | `eci___candidateportal___en-us` | Network Operations Center Engineer |
| Elessent Clean Technologies |  | `dayforce` | `dct___candidateportal___en-us` | Inside Sales and Product Support Engineer |
| EQI |  | `dayforce` | `eqi___candidateportal___en-us` | General Manager |
| Esentire |  | `dayforce` | `esentire___candidateportal___en-us` | Sales Operations and Proposal Specialist |
| FinThrive | finthrive.com | `dayforce` | `finthrive___candidateportalindia___en-us` | Analyst, Reimbursement Solutions |
| Fng |  | `dayforce` | `fng___candidateportal___en-us` | Product Engineer |
| Fossil |  | `dayforce` | `fossil___candidateportal___en-gb` | SAP CPI Software Engineer |
| Gligroup |  | `dayforce` | `gligroup___gli___en-us` | Test Engineer |
| Hhglobal |  | `dayforce` | `hhglobal___candidateportal___en-sg` | Digital Communications Assistant |
| Interactive Brokers | interactivebrokers.com | `dayforce` | `ibgllc___candidateportal___en-us` | Buyer |
| Interactive Brokers Group |  | `dayforce` | `ibgllc___candidateportal___en-us` | Security Engineer |
| Interactive Brokers Group, Inc. |  | `dayforce` | `ibgllc___candidateportal___en-us` | Document Processor |
| IntouchCX | intouchcx.com | `dayforce` | `intouchcx___candidateportal___en-us` | Human Resources Executive |
| JCB |  | `dayforce` | `jcb___candidateportal___en-us` | IT Integration Consultant |
| Kestra | kestrafinancial.com | `dayforce` | `kestra___kestraholdings___en-us` | Director of Cloud |
| Kidde Global Solutions | kiddeglobalsolutions.com | `dayforce` | `kiddeglobal___candidateportal___en-us` | Sales Manager |
| Kiddeglobal |  | `dayforce` | `kiddeglobal___candidateportal___en-us` | Pre-Sales Engineer |
| LevelBlue |  | `dayforce` | `twh___candidateportal___en-us` | Accounts Receivable & Collections Analyst |
| Loomis Sayles |  | `dayforce` | `loomissayles___candidateportal___en-us` | Business Analyst |
| Mediakind | jobs.dayforcehcm.com | `dayforce` | `mediakind___candidateportal___en-ie` | Accounts Receivable Analyst |
| Medmetrix |  | `dayforce` | `medmetrix___candidateportal___en-us` | Quality Analysis Supervisor |
| Milacron India Pvt Ltd | milacron.com | `dayforce` | `mymilacron___candidateportal___en-us` | Accounts Receivable Senior Officer |
| Mydayforce |  | `dayforce` | `mydayforce___indeedjobs___en-gb` | Delivery Manager |
| Mymilacron |  | `dayforce` | `mymilacron___candidateportal___en-us` | Electronics and Control Engineer |
| Natus |  | `dayforce` | `natus___candidateportalsensory___en-us` | Legal Counsel |
| NAVEX | navex.com | `dayforce` | `navex___jobopenings___en-us` | Implementation Specialist |
| OEC |  | `dayforce` | `oec___indiacandidateportal___en-gb` | Service Management Specialist |
| OSB India | osb-india.com | `dayforce` | `peoplespace___candidateportal2___en-gb` | Strategic People Business Partner and Head of People |
| OSTTRA | osttra.com | `dayforce` | `osttrahcm___candidateportal___en-sg` | Business Analyst |
| Osttrahcm |  | `dayforce` | `osttrahcm___candidateportal___en-us` | Network Engineer |
| Peoplespace |  | `dayforce` | `peoplespace___candidateportal2___en-gb` | Talent Acquisition Partner |
| Pivotree |  | `dayforce` | `pivotree___candidateportal___en-ca` | Business Analyst |
| Prounlimited |  | `dayforce` | `prounlimited___candidateportal___en-gb` | Human Resource Business Partner |
| SGGG Fund Services |  | `dayforce` | `sgggfsi___candidateportal___en-us` | Fund Accountant |
| Shamrock Trading Corporation |  | `dayforce` | `shamrocktc___candidateportal___en-us` | Business Development Manager |
| Signant Health | signanthealth.com | `dayforce` | `signanthealth___candidateportal___en-ie` | Director Delivery Management |
| Signanthealth |  | `dayforce` | `signanthealth___candidateportal___en-ie` | Applications Engineer |
| Simon & Schuster, LLC | simonandschuster.com | `dayforce` | `simonschustr___candidateportal___en-ie` | Shipping Manager |
| Sirva | sirva.com | `dayforce` | `sirva___candidateportal___en-us` | Compensation Support Coordinator |
| Twh | dayforcehcm.com | `dayforce` | `twh___candidateportal___en-us` | Security Engineer |
| Veranex |  | `dayforce` | `veranex___candidateportal___en-us` | Controller |
| Watlow |  | `dayforce` | `watlow___watlowcareersite___en-gb` | Platform Engineering Manager |

### `eightfold` — 56 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Albemarle | albemarle.com | `eightfold` | `albemarle` | Digital and AI Governance Manager |
| Applied Materials | appliedmaterials.com | `eightfold` | `appliedmaterials` | Project Manager |
| Arcadis | arcadis.com | `eightfold` | `arcadis` | BIM Coordinator |
| Ascendion | ascendion.com | `eightfold` | `ascendion` | AI/ML/Gen AI Engineer |
| Aspire Lifestyles | aspirelifestyles.com | `eightfold` | `internationalsos` | Finance Executive |
| AstraZeneca | astrazeneca.com | `eightfold` | `astrazeneca` | Analyst - Forecasting |
| Bobbi Brown Cosmetics | bobbibrowncosmetics.com | `eightfold` | `elcompanies` | Marketing Manager |
| Boston Consulting Group | bcg.com | `eightfold` | `experiencedtalent.bcg.com` | Data Engineer |
| Boston Scientific | bostonscientific.com | `eightfold` | `bostonscientific` | Platform Engineer |
| Bristol Myers Squibb | bms.com | `eightfold` | `bms` | Data Engineer |
| British Council | britishcouncil.eightfold.ai | `eightfold` | `britishcouncil` | Support Service Hub Agent |
| Corteva | corteva.com | `eightfold` | `corteva` | Commercialization Manager |
| Curriculum Associates | careers.curriculumassociates.com | `eightfold` | `curriculumassociates` | Tax Manager |
| Dexcom | dexcom.com | `eightfold` | `dexcom` | Software Development Engineer |
| Dolby | jobs.dolby.com | `eightfold` | `dolby` | Audio AI Researcher |
| Dolby Laboratories | dolby.com | `eightfold` | `dolby` | Data & AI Platform Manager |
| dsm-firmenich | dsm-firmenich.com | `eightfold` | `dsm-firmenich` | Pricing Specialist |
| Eaton | eaton.com | `eightfold` | `eaton` | Supplier Quality Engineer |
| Eightfold.ai | www.eightfold.ai | `eightfold` | `app` | Staff Engineer |
| Ericsson | ericsson.com | `eightfold` | `ericsson` | Control Tower Operation Specialist |
| Faurecia |  | `eightfold` | `faurecia` | Digital Data Engineer |
| Fluor Corporation | fluor.com | `eightfold` | `fluor` | Project Manager |
| Fortive Corporation | fortive.com | `eightfold` | `fortive` | Talent Acquisition Leader |
| Haleon | haleon.com | `eightfold` | `haleon` | Trade Compliance Services Manager |
| HSBC Holdings plc | hsbc.com | `eightfold` | `hsbc` | Financial Accounting Manager |
| Infineon Technologies | infineon.com | `eightfold` | `infineon` | Product Owner |
| Insight | insight.com | `eightfold` | `insight` | SAP Commerce Developer |
| International SOS | www.internationalsos.com | `eightfold` | `internationalsos` | Security Manager |
| Johns Hopkins University | jhu.edu | `eightfold` | `jhu` | Research Data Analyst |
| Lam Research | lamresearch.com | `eightfold` | `lamresearch` | Materials Planner |
| Mayo Clinic | jobs.mayoclinic.org | `eightfold` | `mc` | Supervisor |
| Micron Technology | micron.com | `eightfold` | `micron` | Engineer |
| Microsoft | microsoft.com | `eightfold` | `microsoft` | Product Manager |
| Millennium | mlp.com | `eightfold` | `mlp` | Data Center Operations Analyst |
| National Australia Bank | nab.com.au | `eightfold` | `nab` | Associate Vice President |
| NetApp | netapp.com | `eightfold` | `netapp` | Technical Marketing Engineer |
| Netflix | netflix.com | `eightfold` | `apply.eyelinestudios.com` | Head of GenFX |
| Omnicell | omnicell.com | `eightfold` | `omnicell` | Software Engineer |
| Qlik | qlik.com | `eightfold` | `qlik` | Account Executive |
| Qualcomm India Private Limited | qualcomm.com | `eightfold` | `qualcomm` | 5G Systems Engineer |
| Qualitrol | qualitrol.com | `eightfold` | `ralliant` | Systems Architect |
| Ralliant | ralliant.com | `eightfold` | `ralliant` | Territory Manager |
| SLB | slb.com | `eightfold` | `slb` | Data Analyst |
| Softtek | softtek.com | `eightfold` | `softtek` | Database Administrator |
| STMicroelectronics | stmicroelectronics.com | `eightfold` | `stmicroelectronics` | Digital Learning Experience |
| Strada | www.stradaglobal.com | `eightfold` | `stradaglobal` | Payroll Team Leader |
| Teva Pharmaceutical | careers.teva | `eightfold` | `tevapharm` | Finance Operations Administrator |
| The Estée Lauder Companies | elcompanies.com | `eightfold` | `elcompanies` | Beauty Advisor |
| The Hongkong and Shanghai Banking Corporation Limited | hsbc.com.hk | `eightfold` | `hsbc` | Head of West India IMM |
| Twilio | twilio.com | `eightfold` | `twilio` | Marketing Analyst |
| UKG | ukg.com | `eightfold` | `ukg` | Software Engineer |
| Vialto Partners | vialtopartners.com | `eightfold` | `vialto` | Specialist |
| VOIS (Vodafone Intelligent Solutions) | vodafone.com | `eightfold` | `vodafone` | Cloud & DevOps Engineer |
| Vylor | vylor.com | `eightfold` | `vylor` | Category Manager |
| Whirlpool Corporation | whirlpoolcorp.com | `eightfold` | `whirlpool` | Engineer |
| Worley | worley.com | `eightfold` | `worley` | Project Planner |

### `ultipro` — 47 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Advarra | www.advarra.com | `ultipro` | `adv1023avr_6051d363-03fe-4650-945e-f836306a8388` | Strategic India Operations Specialist |
| American Chemical Society | acs.org | `ultipro` | `ame1095achm_c52f9a39-fdc5-4ae2-9eaf-cb8a7bda923e` | Marketing Operations Manager |
| AppLogic Networks | applogicnetworks.com | `ultipro` | `pro1053proc_d6eed263-4950-420d-b9f8-5b1a441c931e` | Software Engineering Manager |
| Archer | archerirm.com | `ultipro` | `gusea1p01_arc1037archt_7b869dcd-0d1e-4fe4-be7d-df83dc5a593a` | Associate Advisory Consultant |
| Barr Brands |  | `ultipro` | `barrbrands_bar1504babr_72ed5f69-2009-467f-810d-e90ea87d3bef` | Business Development Manager |
| Bluberi | bluberi.com | `ultipro` | `bluberigaming_blu1505bbgi_123caf10-d427-4561-86d8-62a4818902b8` | QA Automation Engineer II |
| CAI Software | caisoft.com | `ultipro` | `epr1000epsus_10653576-f6a1-4d69-8a9c-a0a96124abda` | Software Developer |
| CIBT | corporate.cibt.com | `ultipro` | `cib1001cbtho_651e26e3-d67c-4622-8ee3-62b19eab9aa9` | Visa Support Specialist |
| Circana | www.circana.com | `ultipro` | `inf1019irinc_17a8d008-9efe-4e51-8460-47ee205d5229` | Software Engineer |
| CIRCOR | www.circor.com | `ultipro` | `cir1001circr_5545d8b0-2410-46b9-a6df-dec8f891b6ee` | Technical Sales Engineer |
| CIRCOR International | circor.com | `ultipro` | `cir1001circr_5545d8b0-2410-46b9-a6df-dec8f891b6ee` | Technical Sales Engineer |
| Communications & Power Industries | cpii.com | `ultipro` | `com1009cpii_f2810c91-940b-4229-97c7-a49ed4bb8286` | Commercial and Defense Sales Manager |
| Convergix Automation Solutions | convergixautomation.com | `ultipro` | `convergix_con1096cvau_52250257-f25d-4ad3-b69e-53bc735d981a` | Engineer - Simulation |
| Crane Worldwide Logistics | craneww.com | `ultipro` | `cra1009crwl_755fc3a5-077f-4395-ad9a-01ffdc6dea89` | Operations Coordinator |
| DGA Group | albrightstonebridge.com | `ultipro` | `dgahr_den1502dgbv_bd705179-4fa0-45fd-b98b-bf71a7e1de91` | Managing Director |
| eProductivity Software | epssw.com | `ultipro` | `epack_eps1500epsp_99876882-5314-40ba-9044-904ae76a629c` | NetSuite Administrator |
| Everest Clinical Research | everestclinical.com | `ultipro` | `eve5000ecrc_0bec1c5f-4038-4ecd-a0fe-2e9d8620c772` | Open-Source Application Developer |
| Exostar | exostar.com | `ultipro` | `exo1000exo_a74089e3-a720-eb42-08c6-31c7d206b3ea` | Scrum Master |
| GetixHealth |  | `ultipro` | `get1002gex_1c4c6809-36bf-4834-adce-fc1c93fb7f10` | Patient Scheduler |
| Hammond Power Solutions Inc. | hammondpowersolutions.com | `ultipro` | `ham5000hamm_d886e470-2a21-498f-9532-54d7b09cb302` | Legal Counsel |
| HYTORC | hytorc.com | `ultipro` | `hytorc_une1500unex_2b7d8849-589b-4d34-a9c1-dd2ff2b8d9ff` | Mechanical Design Engineer |
| InvestCloud | investcloud.com | `ultipro` | `teg1001tegr_ad4204e8-c7f7-47f1-8177-c9f64730dccc` | Release Engineer |
| Jeppesen ForeFlight | jeppesenforeflight.com | `ultipro` | `for1029fref_64ac66bb-52b9-46df-9a34-49db2308f2fe` | Counsel and Company Secretary |
| MarketCast | marketcast.com | `ultipro` | `gusea1p01_mar1053mkcl_c806547d-78ef-4b93-bcae-4a4a835ab542` | Survey Programming Manager |
| Microban |  | `ultipro` | `gusea1p01_bar1504babr_72ed5f69-2009-467f-810d-e90ea87d3bef` | Business Development Manager |
| Milliman | careers.milliman.com | `ultipro` | `mil1017_f54234e9-dfde-b183-fd20-4fbdb19cba7a` | IT Infrastructure and Cloud Services Manager |
| MNP | www.mnp.ca | `ultipro` | `mnp5000mnpl_062c8fba-7371-4cd7-9e8a-94a0b8019ffc` | Engineering Manager |
| MRO Corporation | mrocorp.com | `ultipro` | `mro1000mroc_84de441e-f248-432e-9857-ba2a003c4f55` | Analyst |
| NetSPI | netspi.com | `ultipro` | `gusea1p01_net1500nspi_944d4e9c-f503-4e74-bb8b-f79214e2a5e1` | Software Engineer |
| Park Place Technologies | www.parkplacetechnologies.com | `ultipro` | `par1035pptl_e104637a-c3c6-4682-96d2-d7cc2662dc13` | Software Engineer |
| Presidio | presidio.com | `ultipro` | `pre1019prsd_4c05f321-903e-43d5-a4c0-5d9dd55dc34d` | Vice President - Delivery |
| Propelis | propelis.com | `ultipro` | `sgs1000sgsi_863de151-7dc2-4525-b3f7-e0a69895ee02` | Print Production Manager |
| Quantum Corp. | www.quantum.com | `ultipro` | `qua1014quam_ca0ab154-0d7f-47e3-af84-cd9bd79768dc` | Software Engineer |
| Quantum Corporation | quantum.com | `ultipro` | `qua1014quam_ca0ab154-0d7f-47e3-af84-cd9bd79768dc` | Software Quality Assurance Engineer |
| Rainforest Alliance | rainforest-alliance.org | `ultipro` | `rai1015fores_82609d43-a7fe-4523-abd0-0237b1a37596` | Landscape Finance Consultant |
| RubinBrown | rubinbrown.com | `ultipro` | `rub1001rubin_3688e7ba-ac29-44a9-9775-cbd291bb6fa7` | Tax Production Specialist |
| SC&H | httpswwwschgroup.com | `ultipro` | `sch1020schg_32dd4149-e41d-45e4-afe3-e24f7220d3bf` | Human Resources Manager |
| Supply Technologies | www.supplytechnologies.com | `ultipro` | `gusea1p01_par1048poii_bf75d22e-0799-448d-b549-f0200d2fb3d4` | Functional Lead |
| Talogy | talogy.com | `ultipro` | `psi1000psis_03e015f1-553a-43b2-a3c9-2f22a1f2cea2` | Project Administrator |
| Trimont | trimont.com | `ultipro` | `tri1039tres_551314d5-926b-4475-808f-39d0e0248aed` | Data Analytics Associate |
| TTI, Inc. | ttiinc.com | `ultipro` | `tti1000tti_17573315-0f39-4be7-b82a-2deaa977586c` | Deployment Manager |
| U.S. Pharmacopeial Convention | usp.jobs | `ultipro` | `uni1066_7edcf3b7-2288-c99a-0ece-44b0a1e5cfe9` | Data Engineer |
| Upland Software | uplandsoftware.com | `ultipro` | `upl1000usi_c34cd0cf-aee3-47f1-bc4b-530112a37fed` | Software Engineer |
| Vistex | vistex.com | `ultipro` | `vis1012visx_82577aef-95df-401f-9dc1-71ebcd5068db` | Human Resources Specialist |
| Weaver | weaver.com | `ultipro` | `wea1003weav_c4b626ed-a455-433e-9e34-c877b04aedb4` | Tax Associate |
| WebPros | webpros.com | `ultipro` | `webpros_web1501webp_1c6cf7c0-2d14-4575-906b-78213c1ced24` | Application Support Engineer |
| WebPT | webpt.com | `ultipro` | `web1004webin_fa0645b9-5811-4462-9e10-cb354ce0bd56` | Support Specialist |

### `breezy` — 38 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| 75F | 75f.io | `breezy` | `75f-apac` | Product Manager |
| 75F APAC |  | `breezy` | `75f-apac` | Assistant Sales Manager |
| Accrete |  | `breezy` | `accrete-ai` | Principal Engineer |
| Anovia |  | `breezy` | `anovia` | Marketing Operations Manager |
| Cloverleaf Care |  | `breezy` | `cloverleaf-care` | Customer Success Operations Coordinator |
| Codebase |  | `breezy` | `codebase` | QA Automation Engineer |
| Commutatus | commutatus.com | `breezy` | `commutatus` | Salesforce Developer |
| FAAC Technologies |  | `breezy` | `faac-group` | Regional Sales Manager |
| HIKINEX |  | `breezy` | `recruiting` | Accounting Specialist |
| IIX Global |  | `breezy` | `iix-global` | Associate Vice President |
| Incubator Lab |  | `breezy` | `incubator-lab` | Creative Coordinator |
| ISHIR |  | `breezy` | `ishir` | Digital Advertising Operations Coordinator |
| Kredivo Group |  | `breezy` | `kredivo-group` | Backend Engineer |
| LESTARS MANAGEMENT CONSULTANCY |  | `breezy` | `lestars-management-consultancy-l-l-c` | Google SEO Specialist |
| Lexlegis AI |  | `breezy` | `xanadustudio-ai` | Generative Workflow Developer |
| NationsBenefits, LLC |  | `breezy` | `nationsbenefits` | Talent Acquisition Specialist |
| NationsHearing | nationsbenefits.com | `breezy` | `nationsbenefits` | Data Engineer |
| Netpoleon |  | `breezy` | `netpoleon-nssg` | Channel Account Manager |
| Norima Consulting |  | `breezy` | `norima-consulting` | Guidewire Business Analyst |
| NucleusTeq |  | `breezy` | `nucleusteq` | Production Support |
| RenewCO₂ | renewco2.com | `breezy` | `renewco2` | Marketing Manager |
| Respond.io | respond.io | `breezy` | `respond-io` | Business Development Representative |
| Reveleer | reveleer.com | `breezy` | `reveleer` | Operations Analyst |
| sa.global | saglobal.com | `breezy` | `sa-global` | Dynamics 365 and Power Platform Administrator |
| Scarpel Telecom |  | `breezy` | `scarpel-telecom` | Business Assistant |
| SimWell |  | `breezy` | `simwell-inc` | Simulation Consultant |
| SkySpecs |  | `breezy` | `skyspecs` | Data Infrastructure & Integration Engineer |
| Social Discovery Group | socialdiscoverygroup.com | `breezy` | `social-discovery-ventures` | Data Engineer |
| Stake |  | `breezy` | `stake` | SMSF Accountant |
| Streamhub Limited |  | `breezy` | `streamhub` | Technical Account Manager |
| Super Dispatch |  | `breezy` | `superdispatch` | Engineering Manager |
| Talentuch |  | `breezy` | `talentuch` | Talent Pool Candidate |
| Transak | transak.com | `breezy` | `transak-inc` | Customer Support Associate |
| Unifocus | unifocus.com | `breezy` | `knowcross` | Technical Consultant |
| Uvation |  | `breezy` | `uvation` | Product Catalog Research Analyst |
| YallaPlay |  | `breezy` | `yallaplay` | Head of Product & Monetization |
| Zact Inc. |  | `breezy` | `zact-inc` | Project Manager |
| Zinier | zinier.com | `breezy` | `zinier` | SDET |

### `jobvite` — 38 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| AArete |  | `jobvite` | `aarete` | Claims Lead |
| AliveCor | alivecor.com | `jobvite` | `alivecor` | Product Designer |
| AmeriSave Mortgage Corp. | amerisave.com | `jobvite` | `amerisavecareers` | Chief Technology Officer |
| Ant Group |  | `jobvite` | `antfinancial` | Treasury Manager |
| Barracuda Networks Inc. | barracuda.com | `jobvite` | `barracuda-networks-inc` | Software Engineer |
| Buckman | buckman.com | `jobvite` | `buckman-por` | Corporate Communications Specialist |
| DNEG | dneg.com | `jobvite` | `double-negative-visual-effects-fr` | Animator |
| Egnyte | egnyte.com | `jobvite` | `egnyte` | Sales Strategy & Operations Analyst |
| Enphase Energy | enphase.com | `jobvite` | `enphase-energy` | Data Scientist |
| Entrepreneurs' Organization |  | `jobvite` | `eonetwork` | Growth Manager |
| Enverus |  | `jobvite` | `enverus` | QA Engineer/Analyst |
| FieldCore |  | `jobvite` | `fieldcore` | I&C Technician |
| FiltaGlobal |  | `jobvite` | `filtaglobal-careers` | Graphic Designer |
| Gigamon | www.gigamon.com | `jobvite` | `gigamon` | Software Quality Assurance Engineer |
| Heifer International | www.heifer.org | `jobvite` | `heifer` | Consultant |
| Imagine Learning |  | `jobvite` | `imagine-learning` | Learning Architect |
| Information Services Group | isg-one.com | `jobvite` | `isg-one` | Business Development Executive |
| IP Infusion US Inc. |  | `jobvite` | `ip-infusion` | Revenue Accounting and Billing Manager |
| LegalZoom | legalzoom.com | `jobvite` | `legalzoom` | Technology Auditor |
| LHH | lhh.com | `jobvite` | `lhhcareers` | Global Shared Services Coordinator |
| LHH CareersLHH logo | www.lhh.com | `jobvite` | `lhhcareers` | Talent Promoter |
| Ness Digital Engineering | ness.com | `jobvite` | `ness` | Java Selenium Web Automation Engineer |
| NinjaOne |  | `jobvite` | `ninjaone` | Data Engineer |
| Northern Tool + Equipment |  | `jobvite` | `northerntool` | Integrations Developer |
| Nutanix |  | `jobvite` | `nutanix` | Integration Developer |
| Optimas International | optimas.com | `jobvite` | `optimas-international` | Key Account Manager |
| Progress |  | `jobvite` | `progress` | Software Engineer |
| Relatient | www.relatient.com | `jobvite` | `relatient` | Site Reliability Engineer |
| Resolver |  | `jobvite` | `resolver` | General Analyst |
| Saama Technologies Inc | saama.com | `jobvite` | `saama` | Azure Databricks Administrator |
| Sikich | www.sikich.com | `jobvite` | `sikichcareers` | Palantir Foundry Developer/Analyst |
| TiVo |  | `jobvite` | `tivo` | Network Engineer |
| TiVo Careers \| Jobs at TiVo |  | `jobvite` | `tivo` | IT Support Engineer |
| Varonis | varonis.com | `jobvite` | `varonis` | Cloud Security Architect |
| WD Partners | www.wdpartners.com | `jobvite` | `wdpartners` | Electrical Designer |
| Xperi | xperi.com | `jobvite` | `xperi` | Software Quality Engineer |
| Xperi (TiVo) |  | `jobvite` | `xperi` | IT Support Engineer |
| Ziff Davis | j2global.com | `jobvite` | `ziffdavis` | Associate Director, Scientific Affairs |

### `pinpoint` — 36 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| ADM Indicia | careers.admgroup.com | `pinpoint` | `admgroup` | Accountant |
| adm-Indicia | careers.admindicia.com | `pinpoint` | `admgroup` | Accounts and Finance Operations Executive |
| Align Technology | jobs.aligntech.com | `pinpoint` | `jobs-aligntech` | Clinical Liaison Specialist |
| Anthesis Group | anthesisgroup.com | `pinpoint` | `anthesisgroup` | AI Engineer |
| Aurora Energy Research | auroraer.com | `pinpoint` | `auroraer` | Accounts Payable Assistant |
| Blue Mantis | bluemantis.com | `pinpoint` | `bluemantis` | Financial Planning and Analysis Manager |
| Brivo | brivo.com | `pinpoint` | `brivo` | Sales Development Representative |
| CFRA Research | cfraresearch.com | `pinpoint` | `cfra` | Data Scientist |
| Contego | contegosearch.com | `pinpoint` | `contegosearch` | HR Operations Manager |
| Davies | davies-group.com | `pinpoint` | `davies` | Responsible Business Assistant Manager |
| Energy Aspects | careers.energyaspects.com | `pinpoint` | `energyaspects` | Geospatial Data Annotator |
| Equinox Engineering Ltd. | careers.equinox-eng.com | `pinpoint` | `equinox-eng` | Piping Material Engineer |
| Forterro | forterro.com | `pinpoint` | `forterro` | Applications Developer |
| Franklin Electric | franklin-electric.com | `pinpoint` | `franklin-electric` | Area Sales Manager |
| GLORY |  | `pinpoint` | `gloryglobal` | Finance Executive |
| Hiver | hiverhq.com | `pinpoint` | `hiverhq` | Principal Engineer |
| Holland America Line & Seabourn |  | `pinpoint` | `hollandamericagroup` | Waiter |
| Infor | infor.com | `pinpoint` | `infor` | Software Engineer |
| Jobs at adm-Indicia \| adm-Indicia Careers | httpshttps--careers.admindicia.com | `pinpoint` | `admgroup` | Accounts and Finance Operations Executive |
| Jobs at Aurora Energy Research \| Aurora Energy Research Careers | careers.auroraer.com | `pinpoint` | `auroraer` | Billing & Invoicing Assistant |
| Jobs at Brivo \| Brivo Careers | careers.brivo.com | `pinpoint` | `brivo` | AI Product Intern |
| Jobs at Scan-Group \| Scan-Group Careers | careers.scan-group.com | `pinpoint` | `scan-group` | Business Analyst |
| Meliore Foundation | careers.meliorefoundation.org | `pinpoint` | `meliore` | Executive Director |
| MMR Research | careers.mmr-research.com | `pinpoint` | `mmr-research` | Motion Designer |
| OnePlan Solutions | oneplan.ai | `pinpoint` | `oneplan` | Visual Content Designer |
| Oxford International Education Group | joinus.oxfordinternational.com | `pinpoint` | `oxfordinternational` | Human Resources Associate |
| ParentPay Group | careers.parentpaygroup.com | `pinpoint` | `parentpaygroup` | Software Consultant |
| Reconomy | reconomy.com | `pinpoint` | `reconomy` | Take Back and Logistics Operations Manager |
| Rethink Priorities | rethinkpriorities.org | `pinpoint` | `rethinkpriorities` | AI Integration Lead |
| Shipco IT | shipco-it.com | `pinpoint` | `scan-group` | Finance Associate |
| Snap Analytics | snapanalytics.co.uk | `pinpoint` | `snapanalytics` | Technical Project Manager |
| Sun King | sunking.com | `pinpoint` | `sunking` | Associate Regional Manager |
| Trading Technologies | tradingtechnologies.com | `pinpoint` | `tradingtechnologies` | Platform Engineer |
| Utilities One | utilitiesone.com | `pinpoint` | `utilitiesone` | OSP Designer |
| V.Group | vgrouplimited.com | `pinpoint` | `vgroup` | Able Seaman |
| Vena Solutions | venasolutions.com | `pinpoint` | `vena` | Professional Services Manager |

### `adp` — 33 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| 11:11 Systems | 1111systems.com | `adp` | `08f195f0-beb6-4255-a019-dbc8691ab8e8` | Enterprise Solutions Manager |
| AGDATA | agdata.com | `adp` | `a42f2e0b-2d4a-4df5-a7d9-43a8b36fe9f3` | Software Engineer |
| Alvaria | alvaria.com | `adp` | `7120c628-221c-4769-b7e7-8ab11b78b67f` | Quotation Specialist |
| Arise Virtual Solutions Inc. | arise.com | `adp` | `da85f37f-cd12-4d20-8d3f-16b23f5c1a58` | Resource Planner |
| Arterex | arterexmedical.com | `adp` | `fd2d095e-7720-4581-a32a-65316672078c` | Business Development Director |
| Aviat Networks | aviatnet.com | `adp` | `0ec0c5a4-f3ba-4be4-be2b-5d725d77f8ed` | Territory Sales Manager |
| BetaNXT | betanxt.com | `adp` | `21b5e71b-5e64-4d33-b8de-26ea145e664a` | Software Engineering Manager |
| BNI | bni.com | `adp` | `47319cd5-5177-4288-85d2-d8661c094339` | Accounting Analyst |
| CSafe | csafe.com | `adp` | `d3023170-5358-4496-8f4d-a9ab7fa530b4` | Customer Service Representative |
| CU Rise Analytics Pvt. Ltd. | trellance.com | `adp` | `d6cb9e80-f827-43e7-8834-84752ac03f5a` | DevOps Engineer |
| Dimerco Express Group | dimerco.com | `adp` | `3820971e-32b6-4611-be0d-caa125afd06c` | Sales Executive |
| Elevate Healthcare | elevatehealth.net | `adp` | `5fc0b4f7-0110-48f9-8f9b-1876dad903c8` | Solutions Sales Consultant |
| ELLKAY | www.ellkay.com | `adp` | `5154a6eb-14d1-4663-b31c-c91a4fc4a51a` | Data Migration Engineer |
| Fair Labor Association | fairlabor.org | `adp` | `c6f14a31-8de0-45d7-b429-a90525d403c0` | Project Manager |
| Ideal Tridon Group |  | `adp` | `16a8d35a-b15c-4a8c-86eb-d1e3200772a7` | Director for Health, Safety and Environmental |
| IGS |  | `adp` | `f9f4457a-db7c-409d-a79a-958e68c851da` | Project Administrator |
| IGS Brasil Soluções Industriais Ltda |  | `adp` | `f9f4457a-db7c-409d-a79a-958e68c851da` | Project Supervisor |
| KiddeFenwal |  | `adp` | `9c811143-29d4-4b53-a728-29426c33870e` | Master Data Specialist |
| Lighthouse | lighthouseglobal.com | `adp` | `7f4d718d-fbb0-4f5f-87f5-c2c0598c7277` | Operations Analyst |
| Mastercam | mastercam.com | `adp` | `b35545bc-d131-467c-a046-2ba0f85874f6` | Channel Order Processor |
| Meazure Learning | meazurelearning.com | `adp` | `80476592-d857-4207-83c6-fe66444a7e3b` | Manager, Client Satisfaction Operations |
| NewAge Products | newageproducts.com | `adp` | `5d6cf95f-9040-42ae-bb40-b504818c9d7e` | Design |
| NOLS | nols.edu | `adp` | `a87ec8da-7dfe-4840-967e-19cbed49ce35` | Director of Custom Education |
| ORBCOMM | orbcomm.com | `adp` | `b9e6f585-387b-496e-8b63-bee5bed64c3e` | Customer Success Operations Partner |
| Pizza Hut | pizzahut.com | `adp` | `931b0842-1be6-43d9-9649-f7c49d151ad6` | Procurement Manager |
| Rightsline | www.rightsline.com | `adp` | `f93572d0-23af-4fc8-978b-3dc51f63c8fa` | Support Manager |
| Riskonnect |  | `adp` | `8781b54c-a13e-4584-93c7-fc74cce40486` | Software Engineer |
| Riskonnect, Inc. | riskonnect.com | `adp` | `8781b54c-a13e-4584-93c7-fc74cce40486` | Business Development Representative |
| Shell Recharge Solutions | shell.com | `adp` | `a5602c94-c189-42e4-a777-0c089c2c329e` | Data Engineer |
| Smart Data Solutions | sdata.us | `adp` | `58758dfc-14f0-4c27-ab28-426c1122d8c0` | Claims Examiner |
| SMC India |  | `adp` | `0c7313dc-36b1-4539-a52e-fb2eefb02130` | Warehouse and Stores Officer |
| TechnoMile | technomile.com | `adp` | `0098a12d-bb3f-475c-a5ef-8c03da44e81c` | Customer Success Manager |
| VitalEdge |  | `adp` | `c4000cb1-a39c-438d-94c7-ba150b897644` | Database Administrator |

### `recruitee` — 32 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Aftershoot |  | `recruitee` | `aftershoot` | Product Designer |
| BeingUser |  | `recruitee` | `beinguser` | Design Director |
| Brainsquare | brainsquare.recruitee.com | `recruitee` | `brainsquare` | Enterprise Integration Support Engineer |
| Bright River India Private Limited | brightriverindia.recruitee.com | `recruitee` | `brightriverindia` | Video Editor & Colorist |
| Castolin Eutectic | castolin.recruitee.com | `recruitee` | `castolin` | QC Engineer |
| Cefetra Group BV | cefetragroup.recruitee.com | `recruitee` | `cefetragroup` | Quality Administrator |
| DeepHealth |  | `recruitee` | `deephealth` | Finance Manager |
| Deerns Groep BV | jobs.deerns.com | `recruitee` | `jobsdeerns` | IT Systems Engineer |
| FlexTrade | careers.flextrade.com | `recruitee` | `flextrade` | Dashboard Automation Engineer |
| Framestore | framestore.recruitee.com | `recruitee` | `framestore` | Compositing Supervisor |
| FULL Creative | fullcreative.recruitee.com | `recruitee` | `fullcreative` | Financial Analyst |
| Gain | gain.recruitee.com | `recruitee` | `gain` | Sales Engineer |
| GRID eSports GmbH |  | `recruitee` | `grid` | Sales Manager |
| Gusti Leder GmbH | gusti-leder.de | `recruitee` | `gustileder` | E-Commerce Assistant |
| Infopro Learning | infoprolearning.com | `recruitee` | `infoprolearning` | Instructional Designer |
| KC Overseas Education | kcoverseaseducation.recruitee.com | `recruitee` | `kcoverseaseducation` | Career Consultant |
| Kinly | kinly.com | `recruitee` | `kinly` | Audio Visual Subject Matter Expert |
| Kuoni Tumlare | careers.kuonitumlare.com | `recruitee` | `kuonitumlare` | Lead Backend Developer |
| Lenskart |  | `recruitee` | `lenskartcareers` | Business Head |
| LUXHOLD INVEST S.A. | ozeol.recruitee.com | `recruitee` | `ozeol` | International Buyer |
| Marcus Evans | marcusevanscareers.recruitee.com | `recruitee` | `marcusevanscareers` | Junior .NET Developer |
| MedMe Health |  | `recruitee` | `medmehealth` | Full-Stack Engineer |
| Metyis AG | metyisag.recruitee.com | `recruitee` | `metyisag` | Data Engineer |
| Natuvion GmbH |  | `recruitee` | `natuvion` | Chief Operating Officer |
| One Mobility | onemobility.recruitee.com | `recruitee` | `onemobility` | Logistics Executive |
| Signode | signode.com | `recruitee` | `signode` | Assistant Manager - Sales |
| Sioux High Tech Software Ltd. |  | `recruitee` | `sioux` | Electrical/Electronics Engineer |
| SkyCell AG | skycell.ch | `recruitee` | `skycellag` | Product Designer |
| Tether Operations Limited | tether.io | `recruitee` | `tether` | AI Research Engineer |
| Toku Ltd | careers.toku.co | `recruitee` | `tokultd` | Services Engineer |
| Vencomatic Group |  | `recruitee` | `vencomaticgroup` | Area Sales Manager |
| Xogene Services LLC | xogene.recruitee.com | `recruitee` | `xogene` | Clinical Trial Transparency Specialist |

### `csod` — 29 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Apollo Tyres Ltd | apollotyres.com | `csod` | `apollotyres___1` | Group Manager, Talent Acquisition |
| CHIREC International School | chirec.edu.in | `csod` | `cognitapeople___1` | Marketing Assistant Manager |
| Cognita |  | `csod` | `cognitapeople___1` | Behavioral Counselor |
| Cognita Schools |  | `csod` | `cognitapeople___1` | Admissions Counsellor |
| Cornerstone |  | `csod` | `cornerstone___2` | AI Engineer |
| Cornerstone OnDemand |  | `csod` | `cornerstone___2` | Business Consultant |
| deugro | deugro.com | `csod` | `deugro-group___1` | Customer Service Executive |
| FORVIA HELLA |  | `csod` | `hella___1` | Opex and IE Specialist |
| Gen Re |  | `csod` | `genre___1` | Technical Accounting Specialist |
| General Reinsurance AG | genre.com | `csod` | `genre___1` | Underwriter |
| HELLA India Automotive Pvt Ltd |  | `csod` | `hella___1` | Industrial Technician |
| HELLA India Automotive Pvt Ltd. | hella.com | `csod` | `hella___3` | Machine Operator |
| Henkel | henkel.com | `csod` | `henkel___1` | Process Safety Manager |
| Linde South Asia Services Pvt. Ltd. | linde.com | `csod` | `linde___25` | Associate Manager Operations & Maintenance |
| MCTC | mctc.com | `csod` | `mctc___4` | Purchasing Administrator |
| Mediterranean Shipping Company | msc.com | `csod` | `msc___4` | Customer Service |
| Mediterranean Shipping Company (MSC) |  | `csod` | `msc___4` | Customer Service Assistant |
| NNE | nne.com | `csod` | `nne___4` | DevOps Engineer |
| Proximus Global |  | `csod` | `proximus___11` | Full Stack Developer |
| Proximus Group | proximus.com | `csod` | `proximus___11` | Product Manager |
| RSA Engineered Products LLC |  | `csod` | `trimascorp___16` | Business Systems Analyst |
| Sidel | sidelgroup.com | `csod` | `sidelgroup___2` | Field Service Engineer |
| Sidel Group |  | `csod` | `sidelgroup___3` | Field Service Engineer |
| Simon-Kucher | simon-kucher.com | `csod` | `simon-kucher___10` | Consultant |
| Spirax Group | spiraxgroup.com | `csod` | `sseacademy___19` | Quality Inspector |
| TriMas Center of Excellence Private Limited |  | `csod` | `trimascorp___16` | IT Infrastructure Engineer |
| WIK Academy |  | `csod` | `wikacademy___1` | Engineer |
| Wikacademy | wikacademy.com | `csod` | `wikacademy___1` | Sales Executive |
| World Bank | worldbank.org | `csod` | `worldbankgroup___6` | Infrastructure Finance Specialist |

### `dover` — 25 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Aerobotics7 | aerobotics7.com | `dover` | `22cf9f28-8406-4aca-af1d-64721c418007` | Machine Learning Engineer |
| Careerflow.ai | careerflow.ai | `dover` | `c9a9b77b-6a08-408d-a99a-251c1444c1b0` | Voice Actor |
| Cheat Code LLC | cheatcode.gg | `dover` | `e4709c96-1a83-4d02-8681-46eaa2b3eb82` | Game Producer |
| Codingal | codingal.com | `dover` | `9d19c96c-5e33-4332-8c9a-623e55540671` | Pre-Sales Associate |
| DATACLAP DIGITAL | dataclapdigital.com | `dover` | `a8dcde25-fad5-4bab-a45f-ebe8fd0b9767` | Lead Generation Associate |
| Dextra Labs | dextralabs.com | `dover` | `200e25d2-ea0f-4583-a8be-3cb74767686a` | MIS Team Lead |
| Discovered | discoveredlabs.com | `dover` | `a4044564-83b1-4700-9726-e9020da4f44e` | Content Engineer |
| Docket Inc | docketai.com | `dover` | `d4897651-97c7-450a-862c-45ca51b9b7b7` | Customer Success Manager |
| EazyApp Tech Pvt Ltd (RentOk) | rentok.com | `dover` | `07e9a93d-e75d-4568-a007-eab3deba58e5` | Human Resources Generalist |
| Emetlab | emetlab.com | `dover` | `d0bce587-d412-4c45-8e37-4bd404104988` | Software Engineer |
| Factor HQ | usefactor.app | `dover` | `2b32bb93-5749-4f50-897b-15d353dfa763` | Sales Development Representative |
| Infy HR Pvt. Ltd. | infyhr.com | `dover` | `bad0a39e-aa64-434c-97c6-27c0c7682e7b` | Accountant |
| JCiTL | jcitl.com | `dover` | `ec624890-f311-4792-9984-b3a45fd92788` | Business Development Manager |
| LitLab | litlab.ai | `dover` | `1dcb9c8e-ce64-4c2d-94b6-6754a420fd03` | District Partnerships Manager |
| Mimidentalclinic | mimidentalclinic.com | `dover` | `d0c79f62-b2d4-4b9a-960c-2f722d3c5e78` | Software Engineer |
| PAARVISION AUTONOMY PRIVATE LIMITED | paar-autonomy.com | `dover` | `21129adf-3d83-49d7-894a-f309d3066130` | Talent Acquisition Intern |
| Peakflo | peakflo.co | `dover` | `edd5019c-5b79-4b5b-9978-4bd65180111f` | Human Resources Intern |
| Perfora | perforacare.com | `dover` | `5289f72e-1570-4890-a9f8-be6f5a308539` | Content Lead |
| QL2 Software | ql2.com | `dover` | `e837fe6e-0851-45d8-93fa-e3b2ca7e1813` | Data Scientist |
| SemiAnalysis | semianalysis.com | `dover` | `ddbb65b5-1f71-4c20-835f-7c6860ed5d7f` | Research Analyst |
| Tingu | tingu.app | `dover` | `cdd07ae3-7886-4fcb-9e9b-8fe21b5a0924` | Social Media Intern |
| Volcora | volcora.com | `dover` | `01b35bc8-2f7b-44aa-83af-73a382e6d76a` | Marketing and Community Specialist |
| Volopay | volopay.co | `dover` | `ebed3959-fa8a-4719-b143-0730e1223ec8` | Sales Development Representative |
| Wavelength Network | wavelength.now | `dover` | `6aa8a211-99f7-4bb5-8c1b-bd1735af6c1f` | Brand Licensing Agent |
| Xperteez Technology | xperteez.co.in | `dover` | `3e115d99-9ee5-4619-b98b-5e4e44c06679` | MCP Expert |

### `freshteam` — 23 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Anaxee Digital Runners Pvt Ltd | anaxee.com | `freshteam` | `anaxee` | Legal Associate |
| Aurochs Software |  | `freshteam` | `aurochs` | Solutions Developer |
| Cambridge Technology | cambridgetechnology.com | `freshteam` | `cambridgetechnology` | Database Engineer |
| CashFlo | cashflo.com | `freshteam` | `cashflo-talent` | ABAP Developer |
| Digitap.ai | digitap.ai | `freshteam` | `digitap` | Customer Success Executive |
| ECS \| Enterprise Change Specialists | ecsme.com | `freshteam` | `ecsme` | Business Analyst |
| Ensemble Health Partners, India | ensemblehealthpartners.com | `freshteam` | `ensemblehp-hr` | Business Intelligence Engineer |
| Everstage Inc. | everstage.com | `freshteam` | `everstage` | QA Automation Engineer |
| FieldAssist | fieldassist.com | `freshteam` | `flick2know` | Customer Success |
| Intugine Technologies | intugine.com | `freshteam` | `intugine` | Associate Director - Implementation |
| LiveLike | livelike.com | `freshteam` | `livelike-hris` | Software Engineer |
| Locus.sh | locus.sh | `freshteam` | `locus` | Software Development Engineer |
| Noise | gonoise.com | `freshteam` | `gonoise` | Sales Operations Intern |
| OJ Commerce | careers.ojcommerce.com | `freshteam` | `ojcommerce` | Finance Analyst |
| Payatu | jobs.payatu.io | `freshteam` | `payatu` | Social Media Marketer |
| Quantela Inc. | quantela.com | `freshteam` | `quantela-team` | Application Developer |
| Sattva Consulting | sattva.co.in | `freshteam` | `sattva-talent` | Consultant |
| Scapia | scapia.com | `freshteam` | `scapia` | Product Support Engineer |
| Sequoia Applied Technologies Inc. | sequoiaat.com | `freshteam` | `sequoiaat` | Field Sales Executive |
| Tazapay Pte Ltd |  | `freshteam` | `tazapay` | Treasury Operations Team Lead |
| Udhyam Learning Foundation | udhyam.org | `freshteam` | `udhyam` | Product Intern |
| Yogabar | yogabar.com | `freshteam` | `yogabars` | Influencer Marketing Intern |
| Zerodha Asset Management Pvt Ltd | zerodhafundhouse.com | `freshteam` | `zerodhafundhouse` | Operations Manager |

### `personio` — 22 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| 360T | 360t.com | `personio` | `360t` | Legal Counsel |
| AMINA Bank | amina.com | `personio` | `amina` | Social Media Marketing Manager |
| B&B Analytics Private Limited | amina.jobs.personio.com | `personio` | `amina` | Management Trainee |
| Cuculus GmbH | cuculus-gmbh.jobs.personio.de | `personio` | `cuculus-gmbh` | Load & Performance Engineer |
| Cuculus India |  | `personio` | `cuculus-gmbh` | Project Operations |
| Evora Group | evora.com | `personio` | `evorait-in` | SAP Data Engineer |
| Evora IT Solutions Pvt. Ltd. | evorait.com | `personio` | `evorait` | SAP Data Engineer |
| financial.com AG | financial.com | `personio` | `financialcom` | Client and Application Manager |
| HARKE International India Private Limited | harke.com | `personio` | `harke` | Sales Manager |
| IKN czech s.r.o. | ikn-gmbh.jobs.personio.de | `personio` | `ikn-gmbh` | Project Manager |
| IKN GmbH |  | `personio` | `ikn-gmbh` | Engineer |
| IPG Information Process Group GmbH Deutschland | timetoact-group.com | `personio` | `timetoact-group` | Service Manager |
| Kaso |  | `personio` | `elkaso` | Software Engineer |
| Kinet Railway Solutions Ltd. | kinetrailwaysolutions.com | `personio` | `vande-bharat-project` | Buyer |
| Loesche Services S.R.L. | loesche.com | `personio` | `loesche-gmbh-1` | Buyer |
| Loesche Services S.R.L. (Romania) |  | `personio` | `loesche-gmbh-1` | Procurement Performance & Category Analyst |
| newboxes GmbH | newboxes.com | `personio` | `newboxes` | Frontend Engineer |
| Peratera UK Ltd | peratera.com | `personio` | `peratera` | QA Automation Engineer |
| Smart Freight Centre India Private Limited | smartfreightcentre.org | `personio` | `sfc` | Communications Manager |
| Torchbox | torchbox.com | `personio` | `torchbox` | Web Analyst |
| Transforma Travel Group | transformatravelgroup.com | `personio` | `transforma-travel-group` | Educational Tours Specialist |
| ZINKPOWER Services GmbH & Co. KG | zinkpower.com | `personio` | `zinkpower` | Plant Manager |

### `sparkhire` — 21 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Aitech | aitechsystems.com | `sparkhire` | `aitechsystems/88.004` | Quality Engineer |
| AlgoSec | algosec.com | `sparkhire` | `algosec/71.006` | DevOps Engineer |
| Allot | www.allot.com | `sparkhire` | `allot/C4.009` | Technical Support Engineer |
| Ceragon | ceragon.com | `sparkhire` | `Ceragon/D3.003` | Sales Operations Coordinator |
| Cognyte | cognyte.com | `sparkhire` | `cognyte/F2.009` | Java Big Data Developer |
| CommIT | comm-it.com | `sparkhire` | `comm-it/76.008` | Professional Services Engineer |
| HyperGuest | hyperguest.com | `sparkhire` | `hyperguest/09.00B` | Hotel Onboarding and Support Agent |
| Indero | inderocro.com | `sparkhire` | `innovaderm/15.003` | Clinical Data Manager |
| INTECH Process Automation | intechww.com | `sparkhire` | `intech/B5.008` | Process Engineer |
| Investing | investing.com | `sparkhire` | `investing/42.002` | Affiliation Manager |
| Lumenis | lumenis.com | `sparkhire` | `lumenis/A1.00C` | Business Development Manager |
| Matrix Global | matrix-ifs.com | `sparkhire` | `matrix-ifs/19.00F` | Actimize SAM Developer |
| MAX Security Solutions | max-security.com | `sparkhire` | `max_security/2B.004` | Geopolitical Risk Analyst |
| Mize | mize.tech | `sparkhire` | `mize/88.000` | Customer Support Specialist |
| Papaya Global | papayaglobal.com | `sparkhire` | `papayaglobal/16.005` | Implementation Consultant |
| Personetics | personetics.com | `sparkhire` | `personetics/83.00A` | Account Executive |
| U.P.PRO | uppro.biz | `sparkhire` | `uppro/18.003` | Accountant |
| VAST Data | vastdata.com | `sparkhire` | `vastdata/43.001` | Alliances Director |
| Vishay Precision Group | vpgsensors.com | `sparkhire` | `vpgsensors/C8.009` | Cost Analyst |
| Zenity | www.zenity.io | `sparkhire` | `zenity/19.000` | Solutions Architect |
| ZIM | www.zim.com | `sparkhire` | `zim/72.008` | Business Development Representative |

### `hibob` — 17 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Aspire Pharma |  | `hibob` | `aspirepharma` | Operations Executive |
| Blancco Technology Group | blancco.com | `hibob` | `blanccotechno-d3e7bd` | Sales Account Manager |
| Entrepreneurs First | entrepreneursfirst.careers.hibob.com | `hibob` | `entrepreneursfirst` | Events & Operations Associate |
| Fortaegis |  | `hibob` | `fortaegis` | Firmware Security Engineer |
| Gresham |  | `hibob` | `gresham` | Application Specialist |
| IGEL Technology | igel.com | `hibob` | `igeltechnology` | Cloud Dev Engineer |
| IREN | iren.com | `hibob` | `iren` | Vice President of Construction |
| Itineris | itineris.net | `hibob` | `itineris-careers` | AI Research Engineer |
| KodeKloud | kodekloud.careers.hibob.com | `hibob` | `kodekloud` | Platform Architect |
| MCO |  | `hibob` | `mco` | Infrastructure Operations Engineer |
| MyComplianceOffice | mycomplianceoffice.com | `hibob` | `mco` | Product Owner |
| Piab Group | piabgroup.com | `hibob` | `piabgroup` | Area Sales Manager |
| Productsup |  | `hibob` | `productsup` | Full-Stack CMS Developer |
| Sumo Digital Ltd. |  | `hibob` | `sumodigitalltd` | Level Designer |
| Synpulse |  | `hibob` | `synpulse` | PL/SQL Developer |
| Top Employers Institute | top-employers.com | `hibob` | `top-employers` | QA Automation Engineer |
| Traydstream |  | `hibob` | `traydstream` | Client Solutions Consultant |

### `trakstar` — 15 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| BookMyShow | bookmyshow.com | `trakstar` | `bookmyshow` | Finance Assistant Manager |
| Drip Capital | dripcapital.com | `trakstar` | `dripcapital` | Regional Sales Manager |
| Exotel Techcom Pvt Ltd | exotel.in | `trakstar` | `exotel` | Growth Marketing Manager |
| Frontline Managed Services | frontlinems.com | `trakstar` | `frontlinems` | NOC Engineer |
| IMI Process Automation | imi-critical.com | `trakstar` | `imicriticalengineering` | FP&A Lead |
| Kool Home Builders | leamseducation.com | `trakstar` | `leamseducation` | HR Executive |
| Lattice Technologies Pvt Ltd | 1lattice.com | `trakstar` | `1lattice` | Associate Director |
| LogiNext |  | `trakstar` | `loginext` | Product Delivery Manager |
| MoEngage Inc | moengage.com | `trakstar` | `moengage` | Software Engineer |
| Planate Management Group | www.planate.net | `trakstar` | `planate` | Chief Growth Officer |
| Signeasy | signeasy.com | `trakstar` | `signeasy` | Growth Manager |
| Srijan Technologies PVT LTD | srijan.net | `trakstar` | `srijantech` | DevOps Engineer |
| Trusting Social | trustingsocial.com | `trakstar` | `trustingsocial` | HR Manager |
| WebEngage | webengage.com | `trakstar` | `webengage` | Sales Development Representative |
| Whatfix | whatfix.com | `trakstar` | `whatfix101` | Product Designer |

### `join` — 14 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Allocator One Group | allocator.one | `join` | `allocator` | Business Operations and Analytics |
| Associate Allied Chemicals India Pvt Ltd | aacipl.com | `join` | `aacipl` | Data Processing and Information Entry Executive |
| Auditorium Works | auditoriumworks.com | `join` | `auditoriumworks` | Civil Engineer |
| BigilToks | bigiltoks.com | `join` | `bigiltoks` | VJ and Model |
| BR Balaji LLP | brbalajillp.com | `join` | `brbalajillpcom` | Accessories Manager |
| Clairfield International GmbH | clairfield.com | `join` | `clairfield` | Associate Partner |
| Darwaza | darwaza.org | `join` | `darwazaorg` | Curator |
| Health Bloom Wellness Clinics | thehealthbloom.in | `join` | `healthbloom` | Corporate Marketing Manager |
| Leadership & Sustainability | leadership-sustainability.com | `join` | `leadership-sustainability` | Higg FEM & SLCP Verifier |
| Lyto Brands Group | lyto.group | `join` | `lyto` | US Market Marketing Manager |
| MGID | mgid.com | `join` | `mgid` | Talent Pool Applicant |
| Naveera Technology LLC | join.com | `join` | `naveeratechcom` | ETL Test Engineer |
| SRITRIMS (FAR EAST) LIMITED | sritrims.com | `join` | `speedgrouplk` | Digital Marketing Specialist |
| Zime AI | zime.ai | `join` | `zimeai` | AI Engineer |

### `paylocity` — 13 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Associations International LLC |  | `paylocity` | `da8e893b-19ea-4829-8420-b3fb56f7e332` | Regional Manager |
| BirdEye Inc |  | `paylocity` | `96eadb0c-2c7e-4683-9df8-3718e7381570` | Organic Marketing Manager |
| BN, an Augeo company | brandnetworks.com | `paylocity` | `0eed7c03-694e-454b-8e29-7abbbc8e65b5` | Staff Accountant |
| Celona Inc | celona.io | `paylocity` | `2a4006b3-b639-4728-bbf6-8058cf72a3a6` | WiFi Test Engineer |
| CloudBees Inc | cloudbees.com | `paylocity` | `a432d829-f701-4cf3-9108-56ef703b2ac5` | SOC Analyst |
| CloudHQ LLC | cloudhq.com | `paylocity` | `d38e9867-3cd9-4254-b3ff-46e251ca1eee` | Manager, Energy |
| Nerdy | nerdy.com | `paylocity` | `b58b3c84-43fd-43b1-8299-4ba02bd8b78e` | AI Design Engineer |
| Nimble Solutions |  | `paylocity` | `3cb31b47-df35-44a0-9592-a322ad0b2915` | Accounts Receivable Associate |
| otelier.io | otelier.io | `paylocity` | `e08e6f7c-5a53-481d-a947-58eaf4a4d67b` | Technical Customer Operations Associate |
| Patrick OConnor & Associates LP |  | `paylocity` | `e0a955ab-15d7-45b8-b128-cdc6dfdd3c9e` | Human Resources Manager |
| Repario Data LLC |  | `paylocity` | `aa3ae221-186f-4b88-987e-d8880ebe912a` | Storage Engineer |
| Unilode Aviation Solutions | unilode.com | `paylocity` | `ee9db45e-97f3-4183-afeb-3447d508dd0a` | HR Shared Services Administrator |
| Veryon | veryon.com | `paylocity` | `eaf316dd-b54d-49a6-b1d8-1ab594e6a319` | Project Manager |

### `recooty` — 13 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Aarna Systems Pvt Ltd | www.aarnasystems.com | `recooty` | `aarna-systems-pvt-ltd` | Recruitment and Documentation Coordinator |
| Developer Bazaar Technologies | developerbazaar.com | `recooty` | `developer-bazaar-technologies` | SEO Executive |
| Dintellects Solutions Private Limited | dintellects.com | `recooty` | `dintellects-solutions-private-limited` | Full Stack Web Developer |
| Dsifd | dsifd.com | `recooty` | `dsifd` | Communication Trainer |
| GEM Hospital | chennaigemhospital.in | `recooty` | `gem-hospital` | Front Office Executive |
| Gururo | gururo.com | `recooty` | `gururo-private-limited` | PMP Trainer |
| MM International School | mmis.ac.in | `recooty` | `mm-international-school` | Vice Principal |
| Phyllo | www.getphyllo.com | `recooty` | `phyllo` | Technical Content Writer |
| PIPEx | pipex.ai | `recooty` | `f60host` | SEO Executive |
| RChilli | www.rchilli.com | `recooty` | `rchilli` | Demand Generation Specialist |
| Sofueled | sofueled.com | `recooty` | `sofueled` | Social Media & Reels Content Executive |
| Urban Talkies | urbantalkies.com | `recooty` | `urban-talkies` | Copywriter |
| Welo Data | welodata.ai | `recooty` | `welo-data` | AI Training Quality Specialist |

### `ripplehire` — 13 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| 7-Eleven | 7-eleven.com | `ripplehire` | `7-eleven-gsc___d8KPwFGBhDK6f7ajWTsc` | Software Engineer |
| Axis Bank | axis.bank.in | `ripplehire` | `axisbank___1oaTh6RXXNJAqeu5G9gD` | Branch Operations Head |
| Bahwan CyberTek | bahwancybertek.com | `ripplehire` | `bahwancybertek___ncskoGgjoqYnuqre7tUl` | Company Secretary |
| Cimpress | cimpress.com | `ripplehire` | `cimpress___48lajznRS4jlLHbK4C7W` | Automation Engineer |
| Grant Thornton INDUS |  | `ripplehire` | `gtssc___0k0jVPsRUUOMwnATzTJ0` | Procurement Manager |
| HDFC Bank | hdfcbank.com | `ripplehire` | `hdfcbank___1HAhxKKlc5W7zqAKxc2s` | Legal Advisor |
| Mphasis | mphasis.com | `ripplehire` | `mphasis___01zDXztjsKxiR1EuZvx3` | Delivery Project Lead |
| Myridius |  | `ripplehire` | `myridius___BjIJBBQAWnZWESmhKjaX` | SDET |
| Tata AIA Life Insurance | tataaia.com | `ripplehire` | `tataaia___0SxIpKiGtIMFVm1MwbXk` | Corporate Account Manager |
| Tata Steel Limited | tatasteel.com | `ripplehire` | `tatasteel___08kER5NfYhuko4TrE8Q3` | Manager |
| Tata Technologies |  | `ripplehire` | `tatatechnologies___00Uxgs69ZaCPpeWLx6y7` | Engineer |
| Tredence | tredence.com | `ripplehire` | `tredence___3Fl9YhAUYAHwmIS53uYj` | AI Engineer |
| TresVista | tresvista.com | `ripplehire` | `tresvista___bf5TnKSLKxah1XJnw3j0` | Procurement Specialist |

### `paycom` — 12 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| AVEVA DRUG DELIVERY SYSTEMS INC |  | `paycom` | `d6e5d048b8cb6dceda49d47ac70a226a` | Intern |
| CADEX |  | `paycom` | `ec910be695419b5826f27a55bd1290eb` | Collector |
| Cadex Solutions Corporation |  | `paycom` | `ec910be695419b5826f27a55bd1290eb` | Business Development Representative |
| CERES |  | `paycom` | `334139b5ff1a0207fd72e5e97b58ae16` | Quantity Surveyor |
| CERES ENVIRONMENTAL INDIA PRIVATE LIMITED |  | `paycom` | `693149af28d10ff96eecad541a17b703` | Quantity Surveyor |
| DIFGEN PHARMACEUTICALS PRIVATE LIMITED |  | `paycom` | `858ce9892ae00f5caf62866abf5637b7` | IT Trainee |
| EMPLOYEE RELATIONS ASSOCIATES TECHNOLOGY PRIVATE LIMITED | talentbridge.com | `paycom` | `a25cebdecc9aea5d35a01b3eae1501a6` | Business Development Specialist |
| Navitas Semiconductor USA, Inc. |  | `paycom` | `3c27575bd9ba1c74b2dffccac98e3f6d` | Systems Engineer |
| Shoals Technologies | shoals.com | `paycom` | `aded8546f6fa54813f8611f51e1a1e1d` | IT Developer |
| TalentBridge |  | `paycom` | `41f1627752b13f2ee5b79788d0e61e45` | Business Development Specialist |
| UCC Environmental | uccenvironmental.com | `paycom` | `3dcb6de0043aea2357b16ef2b616995a` | Engineer Intern |
| WIREMASTERS INC |  | `paycom` | `0c97da1ceedbdcd089ad7e9963798e34` | Inside Sales Representative |

### `deel` — 11 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Cablex |  | `deel` | `cablex` | Strategic Procurement Specialist |
| CellPoint Digital | cellpointdigital.com | `deel` | `cellpoint-digital` | Software Engineer |
| Cochrane |  | `deel` | `Cochrane` | Chief Community Officer |
| ComplianceQuest | compliancequest.com | `deel` | `compliancequest` | UX/UI Designer |
| Offsec Services |  | `deel` | `offsec` | Channel Manager |
| Shufti |  | `deel` | `shufti` | Customer Success Manager |
| Skylink |  | `deel` | `skylink` | Marketing Manager |
| Walker Digital Table Systems | wdtablesystems.com | `deel` | `walker-digital-table-systems` | Software Analyst |
| Water For People |  | `deel` | `water-for-people` | Project Supervisor |
| Water For People India Trust |  | `deel` | `water-for-people` | Project Officer |
| Zema Global |  | `deel` | `zema.global` | Customer Experience Agent |

### `hirebridge` — 10 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Applause | www.applause.com | `hirebridge` | `Applause` | Partner Manager |
| Aunalytics | www.aunalytics.com | `hirebridge` | `Aunalytics` | Network Operations Center Tech |
| Greenway Health | www.greenwayhealth.com | `hirebridge` | `Greenway Health` | GTM Engineer |
| Kibo Commerce | kibocommerce.com | `hirebridge` | `Tribute Technology` | UI Developer |
| Naviga Inc. | navigaglobal.com | `hirebridge` | `CentralSquare Technologies` | HR Coordinator |
| Numerator | www.numerator.com | `hirebridge` | `Numerator` | Account Manager |
| Sovos Compliance | sovos.com | `hirebridge` | `Sovos Compliance` | AI Platform Tech Lead |
| Tribute Technology |  | `hirebridge` | `Applause` | Data Analyst |
| Vertafore | vertafore.com | `hirebridge` | `Vertafore` | Information Security Analyst |
| Viventium Software | recruit.hirebridge.com | `hirebridge` | `Viventium Software` | Software Engineer |

### `hrmdirect` — 9 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| ABA360 |  | `hrmdirect` | `aba360` | Board Certified Behavior Analyst |
| Glassworks London | glassworkslondon.com | `hrmdirect` | `glassworkslondon` | Business Systems & AI Operations Lead |
| Global Health Strategies |  | `hrmdirect` | `globalhealthstrategies` | Associate, Communications and Advocacy |
| Inviso |  | `hrmdirect` | `inviso` | Digital Sales Operations Program Manager |
| Project Experts India Pvt. Ltd. |  | `hrmdirect` | `projectp` | Oracle Integration & Primavera Technical Consultant |
| Project Partners, LLC | projectp.com | `hrmdirect` | `projectp` | Oracle Integration and Primavera Technical Consultant |
| Slipstream |  | `hrmdirect` | `slipstream-it` | Systems Engineer |
| Slipstream IT |  | `hrmdirect` | `slipstream-it` | Veeva Network Consultant |
| Slipstream Life Sciences | slipstream-it.com | `hrmdirect` | `slipstream-it` | Solution Architect |

### `pageup` — 9 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Crew - Shake Shack |  | `pageup` | `619` | Assistant Merchandise Specialist |
| Deakin University | deakin.edu.au | `pageup` | `949` | Training and Placement Manager |
| FCM Travel | fcmtravel.com | `pageup` | `889` | Systems Enablement Specialist |
| Flight Centre Travel Group |  | `pageup` | `889` | Travel Consultant |
| Leighton Asia | leightonasia.com | `pageup` | `434` | Resident Engineer |
| Thiess | thiess.com | `pageup` | `399` | Service Desk Analyst |
| UNICEF |  | `pageup` | `671` | Impact Evaluation Consultant |
| United Nations Children's Fund (UNICEF) | unicef.org | `pageup` | `671` | International Consultant |
| University of the Sunshine Coast | usc.edu.au | `pageup` | `1167` | Regional Manager |

### `brassring` — 8 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| A&O Shearman | aoshearman.com | `brassring` | `30147_5046` | Practice Manager |
| ADM | adm.com | `brassring` | `25416_5430` | Human Resources Deputy Manager |
| Aga Khan Schools | akdn.org | `brassring` | `30025_5750` | Language Development Practitioner |
| Deltek | www.deltek.com | `brassring` | `25397_5259` | Implementation Consultant |
| EdgeVerve Systems Ltd | edgeverve.com | `brassring` | `26209_5179` | Computer Scientist |
| Infinite | infinite.com | `brassring` | `26656_5008` | System Engineer |
| Infosys Limited | infosys.com | `brassring` | `25633_5439` | AI Developer |
| UBS | ubs.com | `brassring` | `25008_5048` | Sustainability and Climate Risk Specialist |

### `csodsaba` — 8 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Alexander Mann Solutions | alexandermannsolutions.com | `csodsaba` | `Q9VFK026203F3VBQBLOLO79V4` | Recruiter |
| Cathay Pacific | cathaypacific.com | `csodsaba` | `QM1FK026203F3VBQBLO797VAG` | Customer Contact Team Lead |
| EXEO Global | exeo-global.com | `csodsaba` | `Q7RFK026203F3VBQB688M7VW6` | Supply Chain Manager |
| Haskoning | royalhaskoningdhv.com | `csodsaba` | `QA7FK026203F3VBQBQW6G8MT0` | Field Engineer |
| International Rice Research Institute | irri.org | `csodsaba` | `Q7LFK026203F3VBQB79QWQWAS` | Director |
| Symrise | symrise.com | `csodsaba` | `QCAFK026203F3VBQB68V7V7HX` | Key Account Director |
| tk accelis IT Services India Pvt Ltd | karriere.thyssenkrupp.com | `csodsaba` | `QYEFK026203F3VBQB7V8MF6GM` | Data Scientist |
| TKMS GmbH | jobs.thyssenkrupp.com | `csodsaba` | `QYEFK026203F3VBQB7V8MF6GM` | Planning Advisor |

### `salesforce` — 8 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Allison Transmission | allisontransmission.com | `salesforce` | `d58000000domeeau___allisontransmission` | Unified Endpoint Management Engineer |
| Dyninno | dyninno.com | `salesforce` | `dyninno___recruit` | Sales Agent |
| Shearwater GeoServices | shearwatergeo.com | `salesforce` | `swpeople___recruit` | Operations Support Specialist |
| SHL | shl.com | `salesforce` | `shl-hr___recruit` | Technical Support Specialist |
| Systal | systaltech.com | `salesforce` | `systal___recruit` | Software Asset Analyst |
| TECHNOLOGIES INDIA PRIVATE LIMITED | radial.my.salesforce-sites.com | `salesforce` | `radial___careers` | Shopify Engineer |
| Unique Group | uniquegroup.com | `salesforce` | `uniquegroup___careers` | Service Technician |
| VGroup |  | `salesforce` | `vgroup-peopleconnect___Recruit` | Systems Support Officer |

### `gem` — 7 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Amelia Global Services Private Ltd | amelia.ai | `gem` | `soundhound` | Cognitive Technical Lead |
| CloudRaft | cloudraft.io | `gem` | `cloudraft` | Site Reliability Engineer |
| Fireflies.ai | fireflies.ai | `gem` | `fireflies` | Video Editor |
| Index Exchange | indexexchange.com | `gem` | `index-exchange` | Software Engineer |
| Practice by Numbers |  | `gem` | `practice-by-numbers` | Software Engineer |
| PureSpectrum | purespectrum.com | `gem` | `purespectrum` | Project Management Associate Director |
| Sequencing Inc. | sequencing.com | `gem` | `sequencing` | Quality Bioinformatics Engineer |

### `paycor` — 7 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| AG&E Structural Engenuity |  | `paycor` | `8a7883c669b7efc80169c1351c0f0c44` | Structural Engineer |
| Ayar Labs |  | `paycor` | `8a7883c66a3387ef016a468ba9d104e6` | Analog/Mixed-Signal Modelling and Verification Engineer |
| Dura Automotive |  | `paycor` | `8a7883d0798f66af0179f25c87a9230f` | OneStream Administrator |
| Kipsu |  | `paycor` | `8a7883c685eb8d250186049787400869` | Accounts Receivable Collection Specialist |
| Midtronics | midtronics.com | `paycor` | `8a788260592a6a170159415ded832f37` | Product Manager |
| Mohr Partners | mohrpartners.com | `paycor` | `8a7883c693dc38f1019408e4b2530bac` | Content Strategist |
| Rotary International | rotary.org | `paycor` | `8a42a12b3538c68501353a3b0cad2928` | Assistant |

### `adprecruiting` — 6 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Access Information Services |  | `adprecruiting` | `accesscorpcareers` | Data Engineer |
| Advantest |  | `adprecruiting` | `advantestcareers` | Software Engineer |
| Astellas | astellas.com | `adprecruiting` | `astellas` | Data Platforms Operations Expert |
| Data Axle | data-axle.com | `adprecruiting` | `dataaxleindia` | Delivery Manager |
| Toyota Industries |  | `adprecruiting` | `talcareers` | Application Engineer |
| World Wide Technology Holding, LLC |  | `adprecruiting` | `confidentialwwt` | Data Engineer |

### `betterteam` — 5 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Addiction Pet Foods | addictionpet.com | `betterteam` | `addictionpet` | E-commerce Account Manager |
| Futurearth Group | futurearthgroup.com | `betterteam` | `futurearthgroup` | Telesales Executive |
| SamTech Group | samtech-me.com | `betterteam` | `samtech-me` | Telesales Agent |
| The Ardee School | theardeeschool.com | `betterteam` | `theardeeschool` | Mathematics and Computer Science Mentor |
| Williams-Sonoma Inc. | williams-sonomainc.com | `betterteam` | `wsgc-2` | Forklift Operator |

### `puck` — 5 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Avalara | careers.avalara.com | `puck` | `avalara` | Engineering Director |
| BlinkRx | www.blinkrx.com | `puck` | `blinkhealth` | Product Manager |
| Domino Data Lab | dominodatalab.com | `puck` | `domino-data-lab` | Vulnerability Engineer |
| TrueFoundry | truefoundry.com | `puck` | `truefoundry` | Partner Sales Manager |
| Udemy | www.udemy.com | `puck` | `udemy` | Customer Success Specialist |

### `digitalrecruiters` — 4 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Decathlon | decathlon.com | `digitalrecruiters` | `joinus.decathlon.in` | Omnichannel Sales Advisor |
| DECATHLON Retail Omnichannel | joinus.decathlon.in | `digitalrecruiters` | `joinus.decathlon.in` | Omnichannel Sales Advisor |
| Kersia | kersia-group.com | `digitalrecruiters` | `jobs.kersia-group.com` | Instructional Designer |
| Segula Technologies | careers.segulatechnologies.com | `digitalrecruiters` | `careers.segulatechnologies.com` | Wiring Harness Design Engineer |

### `eploy` — 4 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| AB Agri |  | `eploy` | `careers.abagri.com` | Sales Manager |
| Gleeds |  | `eploy` | `gleedsweb.eploy.net` | Cost Manager |
| James Fisher and Sons plc | james-fisher.com | `eploy` | `jamesfisherweb.eploy.net` | Business Service Lead |
| Zellis | zellis.com | `eploy` | `zellisweb.eploy.net` | Product Manager |

### `fountain` — 4 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| ACT | actcorp.in | `fountain` | `ap-1.fountain.com___act` | Team Leader |
| Atria Convergence Technologies Ltd. |  | `fountain` | `ap-1.fountain.com___act` | Network Engineer |
| CMS |  | `fountain` | `ap-1.fountain.com___cms` | Zonal Coordinator |
| Curefoods | curefoods.in | `fountain` | `ap-1.fountain.com___curefoods` | Chief of Staff |

### `jobsoid` — 4 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Aimtron Electronics Pvt. Ltd. |  | `jobsoid` | `aimtron` | Electronics Engineer |
| Buoyancy Consultants & Engineering |  | `jobsoid` | `buoyancy-consultants` | Design Engineer |
| hr-tactics |  | `jobsoid` | `hr-1` | HR Intern |
| Xeluxe Fire Safety Consultancy |  | `jobsoid` | `xeluxefiresafety` | Bid and Business Development Coordinator |

### `njoyn` — 4 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| CGI | cgi.com | `njoyn` | `21001` | GPP Consultant |
| CIBC Mellon | cibcmellon.com | `njoyn` | `51330` | Specialist, Custody Services |
| CUSM - Institut de Recherche | rimuhc.ca | `njoyn` | `55242` | Assistant |
| University of the Fraser Valley | ufv.ca | `njoyn` | `56144` | Web Content Strategist |

### `saashr` — 4 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| 4G Clinical | 4gclinical.com | `saashr` | `6182998` | Growth Marketing Manager |
| Ajaia | secure7.saashr.com | `saashr` | `6214087` | IT Manager |
| Collectivus Holdings | collectivusholdings.com | `saashr` | `6207834` | Product Owner |
| Conrad N. Hilton Foundation | hiltonfoundation.org | `saashr` | `6198075` | Program Associate |

### `applicantpro` — 3 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Mycronic USA | mycronic.com | `applicantpro` | `mycronicusa` | Sales and Applications Engineer |
| Strittmatter Wealth Management Group |  | `applicantpro` | `swmgphilippines` | Enrolled Agent |
| TRIGO Global Quality Solutions | www.trigo-group.com | `applicantpro` | `trigogroup` | Quality Inspector |

### `applicantstack` — 3 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| CST Industries |  | `applicantstack` | `tanks` | Commodity Buyer |
| Eurostampa |  | `applicantstack` | `eurostampa` | Account Manager |
| Innovatia | innovatia.com | `applicantstack` | `innovatia` | Technical Illustrator |

### `beesite` — 3 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Daimler Truck Innovation Center India Private Limited | jobsearch.daimlertruck.com | `beesite` | `daimler-truck` | Program Manager |
| Lufthansa Group Business Services GmbH | apply.lufthansagroup.careers | `beesite` | `lufthansa` | Head of Medical Services |
| MHP India | mhp.com | `beesite` | `porsche` | Consultant |

### `gr8people` — 3 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| AgileOne Global | agileoneglobal.workgr8.com | `gr8people` | `agileoneglobal___workgr8.com` | Data Analyst |
| Randstad Enterprise | rsremeacareers.gr8people.eu | `gr8people` | `rsremeacareers___gr8people.eu` | Data Security Project & Change Management Analyst |
| Teradata | teradata.com | `gr8people` | `careers.teradata.com` | Cloud Operations Analyst |

### `jobscore` — 3 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Cendyn | www.cendyn.com | `jobscore` | `cendyn` | Vice President, Software Engineering |
| Finalsite | finalsite.com | `jobscore` | `finalsite` | Client Success Manager |
| MAQ Software | maqsoftware.com | `jobscore` | `maqsoftware` | Business Operations Executive |

### `acquiretm` — 2 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Amphenol Communications Solutions | amphenol-cs.com | `acquiretm` | `amphenol-tcs` | Application Development Engineer |
| Amphenol ICC |  | `acquiretm` | `amphenol-icc` | Quality Systems Engineer |

### `factorial` — 2 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Opplane Portugal Unipessoal Lda |  | `factorial` | `opplane` | Network Software Engineer |
| Pygio | factorialhr.com | `factorial` | `pigyo` | Product and Solutions Architect |

### `hrsmart` — 2 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| PSA BDP | bdpinternational.com | `hrsmart` | `mua_bdpinternational` | Import Documentation Executive |
| Sanmina Corporation | sanmina.com | `hrsmart` | `mua_sanminacareers` | Team Lead |

### `pereless` — 2 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Contiem | con​​tiem.com | `pereless` | `contiem` | Program Manager |
| ETS GCC | ets.org | `pereless` | `etscareers-global` | Quality Invigilator |

### `polymer` — 2 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| PinSec.Ai | pinsec.ai | `polymer` | `pinsec-ai` | Software Development Engineer |
| PopVax | popvax.com | `polymer` | `popvax` | Scientist |

### `silkroad` — 2 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Graebel Companies, Inc. | graebel.com | `silkroad` | `graebel` | Compensation Services Supervisor |
| Tungsten Automation |  | `silkroad` | `kofax` | Payroll Specialist |

### `usagov` — 2 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Department of State | state.gov | `usagov` | `ST-ST00` | Human Resources Officer |
| Library of Congress | loc.gov | `usagov` | `LL-LC00` | Deputy Field Director |

### `applicantpool` — 1 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Loparex LLC |  | `applicantpool` | `loparex` | Human Resources Generalist |

### `brightmove` — 1 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Congruex | congruex.com | `brightmove` | `brt_35314_27155` | Business Development Director |

### `earcu` — 1 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Menzies Aviation - Central Functions | careers.jmenzies.com | `earcu` | `careers.jmenzies.com___aviation` | Learning Content Developer |

### `gusto` — 1 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| International Council for Helplines, Inc | councilforhelplines.org | `gusto` | `international-council-for-helplines-inc-225ef756-0967-4049-8d6a-5451fc6c37bd` | Director of Accreditation and Credentialing |

### `harri` — 1 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Harri - India |  | `harri` | `harriglobal` | Assistant Manager |

### `higherme` — 1 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Netchex |  | `higherme` | `69dfb615598eb` | Head of Legal |

### `hireology` — 1 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| The Ghoman Group | ghomangroup.com | `hireology` | `chicagomarriottnorthwest` | Hotel Sales Manager |

### `hiringthing` — 1 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Monetary Metals & Co | monetarymetals.com | `hiringthing` | `monetary-metals-co` | Financial Analyst |

### `paradox` — 1 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Inspire Brands | inspirebrands.com | `paradox` | `inspirebrands` | Supervisor, Credit & Collections |

### `peopleadmin` — 1 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| University of North Carolina at Chapel Hill |  | `peopleadmin` | `unc_com` | Project Coordinator |

### `talentlyft` — 1 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| PXP Financial | careers.pxpfinancial.com | `talentlyft` | `pxp-financial` | AI Intern |

### `ttcportals` — 1 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Syneos - Commercial & Clinical/Corporation | syneoshealthcareers.ttcportals.com | `ttcportals` | `syneoshealthcareers` | Financial Associate |

### `virecruit` — 1 companies (no adapter)

| Company | Domain | HiringCafe source | Board token | Example role |
|---|---|---|---|---|
| Winston Taylor | winstontaylor.com | `virecruit` | `careers-winstontaylor-americas` | Financial Analyst |

---

## Method / reproducibility

- `remaining = deduped[company_name.lower() not in sources.json[company_name.lower()]]` (name-overlaps excluded; board-token duplicates not collapsed in this report).
- When adding READY boards, dedupe by `(ats_type, board_identifier.lower())` first: HiringCafe lists the same board under name variants (e.g. `Tide` / `Careers at Tide` → `tide`). Keep one (shortest name) and skip the rest, plus any board already tracked — otherwise the same board gets polled twice under two `source_id`s.
- HiringCafe `source` → jobQuest `ats_type`: `grnhse→greenhouse`, `lever/eu_lever→lever`, `ashby→ashby`, `workday→workday`, `successfactors→successfactors`, `oraclecloud/oraclepeoplesoft/taleo_*→oracle`, `icims/icims2→icims`, `avature→avature`, `phenompeople→phenom`. All else → no adapter.
- Regenerate: re-run the generator against `backend/data/hiringcafe_companies_deduped.json` + `backend/sources.json`.
