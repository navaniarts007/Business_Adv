"""Starter knowledge base (India). Used offline and as context for the AI.

Amounts and limits change with each Union Budget - the AI is told to verify them with live
Google Search, and the UI always links to the official portal. Add your own local entries
(state schemes, co-operatives, local buyers) from the Knowledge tab; they are stored with custom=1.
"""

KNOWLEDGE = [
    # ---------------- Farmers ----------------
    {
        "segment": "farmer", "category": "scheme", "title": "PM-KISAN income support",
        "summary": "Direct income support of Rs 6,000 per year paid in three instalments of Rs 2,000 to landholding farmer families.",
        "eligibility": "Farmer families owning cultivable land; excludes income-tax payers, institutional landholders, serving/retired officials and professionals above set limits. e-KYC is mandatory.",
        "benefits": "Rs 6,000/year by DBT into an Aadhaar-seeded bank account.",
        "how_to_apply": "Register at pmkisan.gov.in (Farmer Corner) or through the village CSC / patwari; complete e-KYC with OTP or biometrics.",
        "url": "https://pmkisan.gov.in", "tags": "income support dbt kisan cash farmer land",
    },
    {
        "segment": "farmer", "category": "finance", "title": "Kisan Credit Card (KCC)",
        "summary": "Short-term crop loan and working capital for farmers, fishers and animal husbandry, with interest subvention for prompt repayment.",
        "eligibility": "Owner cultivators, tenant farmers, sharecroppers, SHGs/JLGs of farmers, fishers and livestock farmers.",
        "benefits": "Concessional interest (effective ~4% p.a. on prompt repayment within the subvention limit), collateral-free up to the RBI limit, RuPay card, crop insurance linkage.",
        "how_to_apply": "Apply at any commercial, regional rural or co-operative bank with land records, ID and crop plan; also via the PM-KISAN portal KCC form.",
        "url": "https://www.myscheme.gov.in/schemes/kcc", "tags": "loan credit crop working capital interest subvention bank",
    },
    {
        "segment": "farmer", "category": "scheme", "title": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "summary": "Crop insurance against yield loss from natural calamities, pests and diseases, including prevented sowing and post-harvest losses.",
        "eligibility": "All farmers growing notified crops in notified areas, including tenants and sharecroppers.",
        "benefits": "Farmer premium capped at 2% (kharif), 1.5% (rabi) and 5% (commercial/horticulture); the rest is paid by government.",
        "how_to_apply": "Enrol through your bank, CSC, insurance agent or pmfby.gov.in before the season cut-off date. Report crop loss within 72 hours on the Crop Insurance app.",
        "url": "https://pmfby.gov.in", "tags": "insurance crop loss flood drought pest risk premium",
    },
    {
        "segment": "farmer", "category": "market", "title": "e-NAM online mandi trading",
        "summary": "National Agriculture Market: an electronic trading portal linking APMC mandis so farmers can see prices and sell to buyers beyond their local mandi.",
        "eligibility": "Farmers registered at an e-NAM integrated APMC; FPOs can also trade.",
        "benefits": "Transparent price discovery, online payment, access to more buyers, live mandi price information.",
        "how_to_apply": "Register at enam.gov.in or the e-NAM mobile app with bank details and ID, or at the e-NAM mandi gate.",
        "url": "https://enam.gov.in", "tags": "mandi price sell market apmc online trading buyer",
    },
    {
        "segment": "farmer", "category": "market", "title": "Agmarknet daily mandi prices",
        "summary": "Government portal with daily arrivals and min/max/modal prices of commodities across Indian mandis - use it to compare where and when to sell.",
        "benefits": "Free price history and trends by commodity, state, district and market.",
        "how_to_apply": "Visit agmarknet.gov.in, choose commodity and market. Data is also available on data.gov.in as an API.",
        "url": "https://agmarknet.gov.in", "tags": "price mandi tomato onion rate sell trend market data",
    },
    {
        "segment": "farmer", "category": "practice", "title": "Soil Health Card",
        "summary": "Free soil testing that reports nutrient status and gives crop-wise fertiliser recommendations - helps cut input cost and raise yield.",
        "benefits": "Soil nutrient report and fertiliser dosage advice for your plot.",
        "how_to_apply": "Contact the local agriculture office / Krishi Vigyan Kendra or check soilhealth.dac.gov.in.",
        "url": "https://soilhealth.dac.gov.in", "tags": "soil test fertilizer yield nutrient crop choice",
    },
    {
        "segment": "farmer", "category": "scheme", "title": "PM-KUSUM solar pumps",
        "summary": "Subsidy for standalone solar irrigation pumps and solarisation of grid-connected pumps; farmers can also sell surplus solar power.",
        "eligibility": "Individual farmers, groups, FPOs, co-operatives and panchayats (state-specific rules).",
        "benefits": "Central and state subsidy covering a large share of pump cost; reduced diesel and power bills.",
        "how_to_apply": "Through your state renewable energy agency / agriculture department portal.",
        "url": "https://pmkusum.mnre.gov.in", "tags": "solar pump irrigation electricity diesel subsidy water",
    },
    {
        "segment": "farmer", "category": "finance", "title": "Agriculture Infrastructure Fund (AIF)",
        "summary": "Medium/long-term debt financing for post-harvest infrastructure and community farming assets such as warehouses, cold storage, sorting and processing units.",
        "eligibility": "Farmers, FPOs, PACS, SHGs, agri-entrepreneurs, startups and others.",
        "benefits": "3% interest subvention on loans up to Rs 2 crore and credit guarantee cover.",
        "how_to_apply": "Apply online at agriinfra.dac.gov.in and choose a lending bank.",
        "url": "https://agriinfra.dac.gov.in", "tags": "warehouse cold storage processing loan infrastructure post harvest",
    },
    {
        "segment": "farmer", "category": "practice", "title": "Join or form an FPO (Farmer Producer Organisation)",
        "summary": "Pooling with other farmers in an FPO gives bulk buying of inputs, better selling prices, access to credit and government support under the 10,000 FPO scheme.",
        "benefits": "Equity grant, credit guarantee and handholding support for new FPOs; collective bargaining power.",
        "how_to_apply": "Contact NABARD, SFAC or your district agriculture office for FPOs in your block.",
        "url": "https://sfacindia.com", "tags": "fpo group collective cooperative bulk buying selling",
    },
    {
        "segment": "farmer", "category": "scheme", "title": "PMKSY - Per Drop More Crop (micro-irrigation)",
        "summary": "Subsidy for drip and sprinkler irrigation to save water and improve yield.",
        "benefits": "Subsidy on drip/sprinkler systems, higher for small and marginal farmers (state-specific rates).",
        "how_to_apply": "Through the state horticulture / agriculture department micro-irrigation portal.",
        "url": "https://pmksy.gov.in", "tags": "drip sprinkler irrigation water subsidy",
    },

    # ---------------- MSME ----------------
    {
        "segment": "msme", "category": "compliance", "title": "Udyam Registration",
        "summary": "Free online MSME registration based on PAN and GST data. It is the gateway to almost every MSME benefit - priority lending, CGTMSE, delayed payment protection, tenders.",
        "eligibility": "Micro: investment up to Rs 2.5 cr and turnover up to Rs 10 cr; Small: up to Rs 25 cr / Rs 100 cr; Medium: up to Rs 125 cr / Rs 500 cr (limits revised in Budget 2025 - verify current figures).",
        "benefits": "Udyam certificate, priority-sector lending, MSME Samadhaan, government tender benefits.",
        "how_to_apply": "udyamregistration.gov.in with Aadhaar and PAN; no documents or fees. Informal micro units can use the Udyam Assist Platform.",
        "url": "https://udyamregistration.gov.in", "tags": "registration msme certificate udyam small business",
    },
    {
        "segment": "msme", "category": "finance", "title": "CGTMSE collateral-free loans",
        "summary": "Credit Guarantee Fund Trust for Micro and Small Enterprises guarantees bank loans so MSEs can borrow without collateral or third-party guarantee.",
        "eligibility": "New and existing micro and small enterprises (manufacturing, services, retail trade) borrowing from member lenders.",
        "benefits": "Guarantee cover on loans up to Rs 10 crore (limit raised in Budget 2025), typically 75-85% coverage.",
        "how_to_apply": "Ask your bank for a CGTMSE-covered term loan or working capital limit.",
        "url": "https://www.cgtmse.in", "tags": "loan collateral free guarantee bank credit working capital",
    },
    {
        "segment": "msme", "category": "finance", "title": "PMEGP - new enterprise subsidy",
        "summary": "Prime Minister's Employment Generation Programme: credit-linked capital subsidy for setting up new micro enterprises.",
        "eligibility": "Individuals above 18; Class 8 pass needed for larger projects; new units only.",
        "benefits": "Margin money subsidy of 15-35% of project cost (higher for rural, women, SC/ST and special categories). Max project cost Rs 50 lakh (manufacturing) / Rs 20 lakh (service).",
        "how_to_apply": "Apply online at the PMEGP e-portal (KVIC); bank sanctions the loan after interview/EDP training.",
        "url": "https://www.kviconline.gov.in/pmegpeportal", "tags": "subsidy new business start manufacturing service loan rural",
    },
    {
        "segment": "all", "category": "finance", "title": "PM MUDRA Yojana loans",
        "summary": "Collateral-free loans for non-farm income-generating micro enterprises in manufacturing, trading and services, including allied agriculture activities.",
        "eligibility": "Any Indian citizen with a business plan for a non-corporate, non-farm small/micro enterprise.",
        "benefits": "Shishu up to Rs 50,000; Kishore Rs 50,000-5 lakh; Tarun Rs 5-10 lakh; Tarun Plus Rs 10-20 lakh (for prompt repayers of Tarun).",
        "how_to_apply": "Any bank, NBFC, MFI or online via the JanSamarth portal.",
        "url": "https://www.mudra.org.in", "tags": "loan small business shop micro collateral free mudra shishu",
    },
    {
        "segment": "msme", "category": "market", "title": "GeM - sell to government",
        "summary": "Government e-Marketplace lets MSMEs, startups, artisans and SHGs sell goods and services directly to government buyers.",
        "benefits": "Access to central/state government demand, MSE purchase preference, timely payment norms.",
        "how_to_apply": "Register as a seller on gem.gov.in with Aadhaar/PAN, Udyam and bank details.",
        "url": "https://gem.gov.in", "tags": "government tender sell buyer procurement market orders",
    },
    {
        "segment": "msme", "category": "finance", "title": "TReDS invoice discounting",
        "summary": "Trade Receivables Discounting System lets MSMEs get paid early on invoices raised to large buyers, without collateral.",
        "benefits": "Faster cash flow at competitive discount rates set by bidding financiers.",
        "how_to_apply": "Register on an RBI-licensed TReDS platform (RXIL, M1xchange, Invoicemart, etc.).",
        "url": "https://www.rbi.org.in", "tags": "invoice cash flow payment receivable working capital delayed",
    },
    {
        "segment": "msme", "category": "compliance", "title": "Delayed payment protection (MSME Samadhaan & 45-day rule)",
        "summary": "Buyers must pay registered micro and small suppliers within 45 days (with a written agreement) or 15 days (without). Section 43B(h) of the Income Tax Act disallows the buyer's deduction for late payment.",
        "benefits": "Compound interest at three times the RBI bank rate on delayed amounts; online complaint to the MSE Facilitation Council.",
        "how_to_apply": "File a case at samadhaan.msme.gov.in using your Udyam number.",
        "url": "https://samadhaan.msme.gov.in", "tags": "delayed payment buyer late dues recovery 45 days",
    },
    {
        "segment": "msme", "category": "practice", "title": "ZED and LEAN certification",
        "summary": "Zero Defect Zero Effect and LEAN schemes help MSMEs improve quality and productivity, with heavy subsidy on certification cost.",
        "benefits": "Bronze/Silver/Gold ZED certification with subsidy; LEAN consultant support; improves export and large-buyer readiness.",
        "how_to_apply": "zed.msme.gov.in",
        "url": "https://zed.msme.gov.in", "tags": "quality certification productivity export",
    },
    {
        "segment": "msme", "category": "scheme", "title": "Stand-Up India",
        "summary": "Bank loans from Rs 10 lakh to Rs 1 crore for greenfield enterprises set up by SC/ST and/or women entrepreneurs.",
        "eligibility": "SC/ST and/or women entrepreneurs above 18; greenfield project in manufacturing, services, trading or agri-allied.",
        "benefits": "Composite loan (term + working capital) with handholding support.",
        "how_to_apply": "standupmitra.in or any scheduled commercial bank branch.",
        "url": "https://www.standupmitra.in", "tags": "women sc st loan new business",
    },

    # ---------------- Retail / shop / vendor ----------------
    {
        "segment": "retail", "category": "scheme", "title": "PM SVANidhi for street vendors",
        "summary": "Collateral-free working capital loans for street vendors, increasing in steps on timely repayment, with interest subsidy and digital-payment cashback.",
        "eligibility": "Urban street vendors with a vending certificate or letter of recommendation from the ULB/town vending committee.",
        "benefits": "Stepped loans with 7% interest subsidy and cashback for digital transactions.",
        "how_to_apply": "pmsvanidhi.mohua.gov.in or through a bank/CSC.",
        "url": "https://pmsvanidhi.mohua.gov.in", "tags": "street vendor hawker loan working capital",
    },
    {
        "segment": "retail", "category": "market", "title": "ONDC - sell online without big marketplace fees",
        "summary": "Open Network for Digital Commerce lets small shops and producers list products and reach buyers on many apps (Paytm, PhonePe Pincode, etc.) via a seller app.",
        "benefits": "Lower commissions than large marketplaces, hyper-local delivery, discoverability.",
        "how_to_apply": "Join through any ONDC seller network participant app listed on ondc.org.",
        "url": "https://ondc.org", "tags": "online selling ecommerce shop kirana delivery digital",
    },
    {
        "segment": "all", "category": "practice", "title": "Google Business Profile + WhatsApp Business",
        "summary": "A free Google Business Profile puts your shop/business on Google Maps and Search; WhatsApp Business adds a catalogue, quick replies and broadcast lists. Together they are the cheapest way to get local customers.",
        "benefits": "Free local discovery, reviews, calls and direction requests; repeat orders via WhatsApp.",
        "how_to_apply": "business.google.com and the WhatsApp Business app.",
        "url": "https://business.google.com", "tags": "marketing customers google maps whatsapp local reviews digital",
    },

    # ---------------- Artisans ----------------
    {
        "segment": "artisan", "category": "scheme", "title": "PM Vishwakarma",
        "summary": "Support for artisans and craftspeople in 18 traditional trades (carpenter, potter, tailor, blacksmith, cobbler, weaver-related trades, etc.).",
        "eligibility": "Self-employed artisans in the listed trades, 18+, one member per family, not availed similar credit schemes recently.",
        "benefits": "PM Vishwakarma certificate and ID, skill training with stipend, toolkit incentive of Rs 15,000, collateral-free loans of Rs 1 lakh then Rs 2 lakh at 5% concessional interest, digital and marketing support.",
        "how_to_apply": "Register at pmvishwakarma.gov.in through a CSC.",
        "url": "https://pmvishwakarma.gov.in", "tags": "artisan craft tools training loan carpenter potter tailor",
    },
    {
        "segment": "artisan", "category": "market", "title": "Selling crafts: GI tags, exhibitions and online",
        "summary": "Artisans earn more by selling under a Geographical Indication (GI) tag, at Development Commissioner (Handicrafts/Handlooms) exhibitions, via Tribes India / state emporia, GeM and ONDC.",
        "benefits": "Premium pricing, authentic branding, urban and export buyers.",
        "how_to_apply": "Register for an Artisan ID (Pehchan card) with the Office of DC Handicrafts; contact your nearest weavers'/handicrafts service centre.",
        "url": "https://handicrafts.nic.in", "tags": "craft handloom weaver gi tag exhibition sell online",
    },

    # ---------------- Startups ----------------
    {
        "segment": "startup", "category": "scheme", "title": "Startup India DPIIT recognition",
        "summary": "DPIIT recognition unlocks startup benefits: self-certification for labour/environment laws, fast-track patents with fee rebate, easier public procurement, and eligibility for tax and funding schemes.",
        "eligibility": "Private limited company, LLP or registered partnership, under 10 years old, turnover below Rs 100 crore in any year, working on innovation or a scalable model.",
        "benefits": "80% patent fee rebate, fast-track IP, Section 80-IAC tax holiday eligibility, access to Seed Fund and Fund of Funds.",
        "how_to_apply": "Register on startupindia.gov.in and apply for DPIIT recognition with incorporation certificate and a brief on innovation.",
        "url": "https://www.startupindia.gov.in", "tags": "startup recognition dpiit tax patent registration",
    },
    {
        "segment": "startup", "category": "finance", "title": "Startup India Seed Fund Scheme (SISFS)",
        "summary": "Early-stage funding through selected incubators for proof of concept, prototype, product trials and market entry.",
        "eligibility": "DPIIT-recognised startups incorporated not more than 2 years ago at application; not received more than Rs 10 lakh from other government schemes.",
        "benefits": "Up to Rs 20 lakh grant for PoC/prototype; up to Rs 50 lakh as convertible debentures or debt for market entry and scaling.",
        "how_to_apply": "seedfund.startupindia.gov.in - apply to up to three incubators.",
        "url": "https://seedfund.startupindia.gov.in", "tags": "seed funding grant incubator prototype early stage",
    },
    {
        "segment": "startup", "category": "finance", "title": "Startup funding ladder (bootstrapping to VC)",
        "summary": "Typical path: bootstrap / friends & family -> government grants (SISFS, BIRAC BIG for biotech, state startup policies) -> angel networks and incubators -> seed VC -> Series A. Venture debt and revenue-based financing suit startups with steady revenue.",
        "benefits": "Pick funding that matches stage: grants for prototype, angels for first customers, VC only when there is a large, fast-growing market.",
        "how_to_apply": "Prepare a 10-12 slide pitch deck, unit economics (CAC, LTV, gross margin) and a cap table before approaching investors.",
        "url": "https://www.startupindia.gov.in/content/sih/en/funding.html", "tags": "funding investor angel vc pitch deck valuation raise money",
    },
    {
        "segment": "startup", "category": "compliance", "title": "Section 80-IAC startup tax holiday",
        "summary": "Eligible DPIIT-recognised startups can claim 100% deduction of profits for any 3 consecutive years out of the first 10 years.",
        "eligibility": "Private limited company or LLP incorporated within the deadline set by the latest Finance Act (extended to 1 April 2030 in Budget 2025 - verify), with an Inter-Ministerial Board certificate.",
        "benefits": "Income tax exemption on profits for 3 years.",
        "how_to_apply": "Apply for the IMB certificate through the Startup India portal after DPIIT recognition.",
        "url": "https://www.startupindia.gov.in", "tags": "tax exemption income tax holiday",
    },
    {
        "segment": "startup", "category": "practice", "title": "Validate before you build",
        "summary": "Talk to 20-30 target customers, measure willingness to pay, launch a minimum viable product, then track retention and unit economics before scaling spend.",
        "benefits": "Avoids the most common startup failure: no market need.",
        "how_to_apply": "Use customer interviews, a landing-page waitlist, pre-orders or a pilot with 3-5 paying customers.",
        "tags": "mvp idea validation product market fit customer research",
    },

    # ---------------- Companies / larger businesses ----------------
    {
        "segment": "company", "category": "compliance", "title": "Core compliance calendar for Indian companies",
        "summary": "Private limited companies must hold board meetings, file AOC-4 (financial statements) and MGT-7/7A (annual return) with MCA, file income tax returns and tax audit if applicable, deduct and file TDS quarterly, and file GST returns (GSTR-1, GSTR-3B; annual GSTR-9 above threshold).",
        "benefits": "Avoids heavy late fees, director disqualification and loss of input tax credit.",
        "how_to_apply": "Use MCA V3 portal (mca.gov.in), GST portal (gst.gov.in) and the income tax e-filing portal; a CA/CS can manage the calendar.",
        "url": "https://www.mca.gov.in", "tags": "compliance roc mca gst tds filing annual return audit",
    },
    {
        "segment": "company", "category": "scheme", "title": "Production Linked Incentive (PLI) schemes",
        "summary": "Incentives on incremental sales of domestically manufactured goods in notified sectors (electronics, pharma, auto components, textiles, food processing, specialty steel, solar modules, and more).",
        "benefits": "Typically a 4-6% incentive on incremental sales over a base year for 4-6 years, subject to investment and sales thresholds.",
        "how_to_apply": "Through the nodal ministry/PMA for each sector during the application window.",
        "url": "https://www.investindia.gov.in/production-linked-incentives-schemes-india", "tags": "manufacturing incentive pli scale investment",
    },
    {
        "segment": "all", "category": "market", "title": "Exporting: IEC, RoDTEP and ECGC",
        "summary": "To export, get an Importer-Exporter Code (IEC) from DGFT, join an Export Promotion Council, claim RoDTEP duty remission on exports, and insure buyer payment risk with ECGC.",
        "benefits": "Access to global buyers, refund of embedded taxes, protection against buyer default; MSMEs can use e-commerce export hubs and India Post Dak Ghar Niryat Kendras.",
        "how_to_apply": "IEC at dgft.gov.in (online, same day); ECGC policies at ecgc.in.",
        "url": "https://www.dgft.gov.in", "tags": "export international overseas buyer iec rodtep ecgc",
    },
    {
        "segment": "company", "category": "practice", "title": "Scaling playbook for established businesses",
        "summary": "Grow through: (1) margin review by product/customer, (2) working-capital cycle reduction, (3) new channels (distributors, e-commerce, exports, GeM), (4) automation/ERP, (5) professional middle management and MIS dashboards, (6) growth capital from banks, private equity or SME IPO platforms (NSE Emerge, BSE SME).",
        "benefits": "Structured growth with controlled risk.",
        "tags": "growth scale expansion strategy ipo private equity erp margin",
    },

    # ---------------- Cross-cutting ----------------
    {
        "segment": "all", "category": "compliance", "title": "GST registration basics",
        "summary": "GST registration is mandatory when aggregate turnover crosses Rs 40 lakh (goods) or Rs 20 lakh (services) - Rs 20 lakh / Rs 10 lakh in special category states - or when selling inter-state / through most e-commerce operators. Composition scheme (turnover up to Rs 1.5 crore) gives low flat tax and simple returns.",
        "benefits": "Input tax credit, ability to sell to GST-registered businesses and online.",
        "how_to_apply": "gst.gov.in with PAN, Aadhaar, address proof and bank details.",
        "url": "https://www.gst.gov.in", "tags": "gst tax registration composition invoice turnover",
    },
    {
        "segment": "all", "category": "practice", "title": "Cash flow and pricing basics",
        "summary": "Keep business and personal money separate; record every sale and expense daily; price = full cost (materials + labour + overheads + transport + losses) + target margin; check competitor prices; keep 3 months of fixed costs as a buffer; collect dues before extending new credit.",
        "benefits": "Most small businesses fail from cash shortage, not from lack of profit.",
        "how_to_apply": "Use a free ledger app (Khatabook, OkCredit, Vyapar) or a notebook; review weekly.",
        "tags": "cash flow pricing profit margin cost accounting bookkeeping",
    },
    {
        "segment": "all", "category": "scheme", "title": "myScheme - find every scheme you qualify for",
        "summary": "Government portal that matches central and state schemes to your profile (age, state, occupation, caste, income).",
        "benefits": "One place to discover eligibility for thousands of schemes.",
        "how_to_apply": "Answer the eligibility questions at myscheme.gov.in.",
        "url": "https://www.myscheme.gov.in", "tags": "scheme eligibility search subsidy government benefit",
    },
    {
        "segment": "all", "category": "finance", "title": "Self-Help Groups and DAY-NRLM credit",
        "summary": "Women's Self-Help Groups under DAY-NRLM get revolving funds, bank linkage loans with interest subvention and enterprise support (Lakhpati Didi, SVEP).",
        "benefits": "Low-interest group credit, training, market linkage for rural women entrepreneurs.",
        "how_to_apply": "Contact the block-level NRLM / state rural livelihood mission office.",
        "url": "https://aajeevika.gov.in", "tags": "shg women group rural loan livelihood",
    },
]
