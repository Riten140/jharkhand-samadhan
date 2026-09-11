"""
Internationalisation for Jharkhand Samadhan.

Design:
- English and Hindi are the two primary, fully-translated UI languages.
- A third dropdown lets a citizen pick any other language — Jharkhand's own
  regional/tribal languages, and other major Indian languages.
- Every language has a `fallback` chain that ends at Hindi or English, so
  picking a language with partial coverage never breaks the UI or shows a
  raw key — it just shows the best available translation.

Honesty note: full, review-quality translation of every string into all of
Jharkhand's tribal languages (Santali, Ho, Mundari, Kurukh, Kharia) and every
major Indian language needs native-speaker review before real deployment.
This file translates the core navigation, actions, and status vocabulary for
all listed languages, and falls back gracefully for anything not yet
translated — the architecture is ready, coverage can be filled in per
language without touching any template.
"""

from flask import g

# (code, native_name, english_name, group, fallback_code)
# group: "primary" | "jharkhand" | "india"
LANGUAGES = [
    ("en", "English", "English", "primary", None),
    ("hi", "हिन्दी", "Hindi", "primary", None),

    # Jharkhand's own regional / tribal languages
    ("nag", "नागपुरी", "Nagpuri", "jharkhand", "hi"),
    ("khr", "खोरठा", "Khortha", "jharkhand", "hi"),
    ("pnx", "पंचपरगनिया", "Panchpargania", "jharkhand", "hi"),
    ("sat", "ᱥᱟᱱᱛᱟᱲᱤ Santali", "Santali", "jharkhand", "hi"),
    ("hoc", "Ho", "Ho", "jharkhand", "hi"),
    ("unr", "Mundari", "Mundari", "jharkhand", "hi"),
    ("kru", "Kurukh (उराँव)", "Kurukh / Oraon", "jharkhand", "hi"),
    ("kha", "Kharia", "Kharia", "jharkhand", "hi"),

    # Other major Indian regional languages
    ("bn", "বাংলা", "Bengali", "india", "en"),
    ("or", "ଓଡ଼ିଆ", "Odia", "india", "en"),
    ("mr", "मराठी", "Marathi", "india", "hi"),
    ("gu", "ગુજરાતી", "Gujarati", "india", "hi"),
    ("pa", "ਪੰਜਾਬੀ", "Punjabi", "india", "hi"),
    ("ta", "தமிழ்", "Tamil", "india", "en"),
    ("te", "తెలుగు", "Telugu", "india", "en"),
    ("kn", "ಕನ್ನಡ", "Kannada", "india", "en"),
    ("ml", "മലയാളം", "Malayalam", "india", "en"),
    ("ur", "اردو", "Urdu", "india", "hi"),
    ("as", "অসমীয়া", "Assamese", "india", "bn"),
]

LANGUAGE_CODES = {code for code, *_ in LANGUAGES}
LANGUAGE_META = {code: {"native": native, "english": english, "group": group, "fallback": fb}
                  for code, native, english, group, fb in LANGUAGES}

DEFAULT_LANG = "en"


# ---------------------------------------------------------------------------
# translation strings
# ---------------------------------------------------------------------------

TR = {

"en": {
    "app_name": "Jharkhand Samadhan",
    "app_tagline": "AI-Verified Civic Problem Reporting",
    "language": "Language",
    "govt_of_jharkhand": "Government of Jharkhand",

    "nav_home": "Home",
    "nav_register": "Register as Citizen",
    "nav_my_complaints": "My Complaints",
    "nav_report": "Report a Problem",
    "nav_queue": "Queue",
    "nav_overview": "Overview",
    "nav_logout": "Log out",
    "nav_back_home": "← Back to Home",

    "hero_title": "Report it. Track it. See it fixed.",
    "hero_body": "Citizens report local problems with photo or video evidence. An AI engine cross-checks each uploaded photo against the reported problem and verifies whether the issue is really there; everything is then confirmed by an officer. Once accepted, officers must resolve the case within a set deadline — and a before/after image check decides whether it's really fixed before the case closes.",
    "stat_reported": "Problems Reported",
    "stat_open": "Currently Open",
    "stat_resolved": "Resolved & Verified",
    "login_heading": "Log in",
    "login_choose_role": "Choose how you are signing in.",
    "login_select_role": "Select login type",
    "role_citizen": "Citizen",
    "role_citizen_desc": "Report a problem and track its progress through verification and resolution.",
    "role_officer": "Officer",
    "role_officer_desc": "Verify reports, accept cases, and upload resolution evidence within deadline.",
    "role_admin": "Admin",
    "role_admin_desc": "Oversee every complaint, manage officers, and reassign overdue cases.",
    "demo_logins": "Demo logins",
    "or_register": "or register your own",

    "login_title": "Login",
    "email": "Email",
    "password": "Password",
    "btn_login": "Log in",
    "new_here": "New here?",
    "create_citizen_account": "Create a citizen account",
    "already_registered": "Already registered?",

    "register_title": "Create your account",
    "register_body": "We'll use your name, email and phone to auto-fill every problem you report, and to keep you updated on its progress.",
    "full_name": "Full Name",
    "phone": "Phone Number",
    "btn_create_account": "Create Account",

    "my_complaints": "My Complaints",
    "btn_new_report": "+ Report New Problem",
    "no_complaints_yet": "You haven't reported any problems yet.",
    "report_first": "Report your first one →",

    "report_heading": "Report a Societal Problem",
    "reported_by": "Reported By",
    "autofill_note": "Auto-filled from your account — no need to re-enter your details.",
    "problem_title": "Problem Title",
    "problem_title_ph": "e.g. Broken road near school",
    "describe_problem": "Describe the Problem",
    "describe_problem_ph": "What is happening, and how is it affecting people?",
    "category": "Category",
    "category_hint": "The AI will cross-check your photo against the problem you describe below.",
    "district": "District",
    "location_details": "Location details",
    "location_ph": "Village / ward / landmark",
    "evidence_label": "Photo or Video Evidence",
    "evidence_click": "Click to upload a photo or video of the problem",
    "evidence_hint": "JPG, PNG, WEBP, or MP4/MOV — required for verification",
    "btn_submit_problem": "Submit Problem",

    "banner_ai_verified": "🤖 Your photo matches the reported problem — verified by AI ({conf}% confidence). Awaiting officer to begin resolution.",
    "banner_pending_officer": "🕵️ Awaiting manual verification by a field officer.",
    "banner_overdue": "⏰ This case is past its resolution deadline ({deadline}).",
    "banner_accepted": "✓ Accepted by {officer}. Resolution due by {deadline} ({days} days left).",
    "banner_reopened": "🔁 The uploaded resolution didn't show enough visible change — case has been reopened.",
    "banner_resolved": "✅ Resolved and verified on {date}.",
    "banner_rejected": "✕ This complaint was reviewed and rejected.",

    "problem_section": "Problem",
    "reported_by_section": "Reported By",
    "evidence_section": "Evidence",
    "evidence_before": "Before — submitted by citizen",
    "evidence_after_officer": "After — uploaded by officer",
    "evidence_after_pending": "Resolution photo not yet uploaded",
    "ai_resolution_check": "AI Resolution Check",
    "progress_timeline": "Progress Timeline",
    "change_score": "change score",

    "ai_verification_panel": "🤖 AI Verification",
    "ai_match": "Photo and description are consistent.",
    "ai_mismatch": "Photo could not confirm the description.",
    "ai_signals": "Signals analysed",
    "ai_warnings": "Quality note",

    "officer_queue_title": "Verification Queue",
    "needs_review": "Needs Review",
    "waiting": "waiting",
    "nothing_waiting": "Nothing waiting for review right now.",
    "my_active_cases": "My Active Cases",
    "in_progress": "in progress",
    "no_active_cases": "No active cases assigned to you.",
    "recently_resolved": "Recently Resolved by You",
    "no_resolved_yet": "No resolved cases yet.",
    "due": "Due",

    "take_action": "Take Action",
    "btn_verify_accept": "Verify & Accept Case",
    "btn_accept_begin": "Accept & Begin Resolution",
    "rejection_reason_label": "Rejection reason (if rejecting)",
    "rejection_reason_ph": "Explain why this isn't a valid / verifiable complaint",
    "btn_reject": "Reject Complaint",
    "upload_resolution": "Upload Resolution Evidence",
    "upload_resolution_hint": "Due by {deadline}. Upload an \"after\" photo of the same location — it will be automatically compared with the original.",
    "evidence_upload_after": "Click to upload the resolved-site photo",
    "evidence_after_hint": "JPG, PNG, or WEBP recommended for automated comparison",
    "btn_submit_resolution": "Submit Resolution for AI Verification",
    "case_resolved_on": "✅ Case resolved and verified on {date}.",
    "case_rejected": "✕ Rejected.",

    "admin_overview": "Admin Overview",
    "total_complaints": "Total Complaints",
    "open": "Open",
    "resolved": "Resolved",
    "overdue": "Overdue",
    "all_complaints": "All Complaints",
    "th_id": "ID",
    "th_title": "Title",
    "th_district": "District",
    "th_category": "Category",
    "th_officer": "Officer",
    "th_status": "Status",
    "no_complaints_filed": "No complaints filed yet.",
    "officers_count": "Officers",
    "no_officers_yet": "No officers yet.",
    "add_officer": "Add an Officer",
    "temp_password": "Temporary Password",
    "btn_create_officer": "Create Officer Account",
    "assignment": "Assignment",
    "currently": "Currently",
    "unassigned": "Unassigned",
    "due_label": "due",
    "assign_reassign": "Assign / reassign officer",
    "btn_assign": "Assign (resets a 5-day deadline)",
    "timeline": "Timeline",

    "status_submitted": "Submitted",
    "status_ai_verified": "🤖 AI Verified",
    "status_pending_officer": "Pending Officer Review",
    "status_accepted": "In Progress",
    "status_resolved": "✓ Resolved",
    "status_reopened": "Reopened",
    "status_rejected": "Rejected",
    "status_overdue": "⏰ Overdue",

    "cat_roads": "Roads & Infrastructure",
    "cat_water": "Water Resources",
    "cat_electricity": "Electricity",
    "cat_sanitation": "Sanitation",
    "cat_health": "Healthcare",
    "cat_education": "Education",
    "cat_safety": "Public Safety",
    "cat_other": "Other",

    "dist_ranchi": "Ranchi",
    "dist_dhanbad": "Dhanbad",
    "dist_dumka": "Dumka",
    "dist_bokaro": "Bokaro",
    "dist_gumla": "Gumla",
    "dist_deoghar": "Deoghar",
    "dist_hazaribagh": "Hazaribagh",
    "dist_giridih": "Giridih",
    "dist_east_singhbhum": "East Singhbhum",
    "dist_west_singhbhum": "West Singhbhum",

    "footer_note": "Jharkhand Samadhan — a Smart India Hackathon prototype.",
},

"hi": {
    "app_name": "झारखंड समाधान",
    "app_tagline": "AI-सत्यापित नागरिक समस्या रिपोर्टिंग",
    "language": "भाषा",
    "govt_of_jharkhand": "झारखंड सरकार",

    "nav_home": "मुखपृष्ठ",
    "nav_register": "नागरिक के रूप में पंजीकरण करें",
    "nav_my_complaints": "मेरी शिकायतें",
    "nav_report": "समस्या दर्ज करें",
    "nav_queue": "कतार",
    "nav_overview": "अवलोकन",
    "nav_logout": "लॉग आउट",
    "nav_back_home": "← मुखपृष्ठ पर वापस जाएँ",

    "hero_title": "दर्ज करें। ट्रैक करें। समाधान देखें।",
    "hero_body": "नागरिक फोटो या वीडियो प्रमाण के साथ स्थानीय समस्याएँ दर्ज करते हैं। AI इंजन हर अपलोड की गई फोटो को बताई गई समस्या से मिलाकर जाँचता है कि समस्या वाकई मौजूद है; फिर उसकी पुष्टि अधिकारी द्वारा की जाती है। स्वीकृति के बाद अधिकारी को तय समय-सीमा में समाधान करना होता है — और पहले/बाद की तस्वीरों की तुलना से तय होता है कि मामला वाकई हल हुआ है या नहीं।",
    "stat_reported": "दर्ज की गई समस्याएँ",
    "stat_open": "वर्तमान में खुली",
    "stat_resolved": "हल व सत्यापित",
    "login_heading": "लॉग इन करें",
    "login_choose_role": "चुनें कि आप किस रूप में लॉग इन कर रहे हैं।",
    "login_select_role": "लॉगिन प्रकार चुनें",
    "role_citizen": "नागरिक",
    "role_citizen_desc": "समस्या दर्ज करें और सत्यापन से लेकर समाधान तक उसकी प्रगति देखें।",
    "role_officer": "अधिकारी",
    "role_officer_desc": "शिकायतों की पुष्टि करें, मामले स्वीकार करें, और समय-सीमा के भीतर समाधान का प्रमाण अपलोड करें।",
    "role_admin": "एडमिन",
    "role_admin_desc": "सभी शिकायतों की निगरानी करें, अधिकारियों का प्रबंधन करें, और लंबित मामले पुनः सौंपें।",
    "demo_logins": "डेमो लॉगिन",
    "or_register": "या अपना खाता बनाएं",

    "login_title": "लॉगिन",
    "email": "ईमेल",
    "password": "पासवर्ड",
    "btn_login": "लॉग इन करें",
    "new_here": "नए हैं?",
    "create_citizen_account": "नागरिक खाता बनाएं",
    "already_registered": "पहले से पंजीकृत हैं?",

    "register_title": "अपना खाता बनाएं",
    "register_body": "आपके नाम, ईमेल और फ़ोन का उपयोग हर शिकायत में अपने-आप भरने और आपको प्रगति की जानकारी देने के लिए किया जाएगा।",
    "full_name": "पूरा नाम",
    "phone": "फ़ोन नंबर",
    "btn_create_account": "खाता बनाएं",

    "my_complaints": "मेरी शिकायतें",
    "btn_new_report": "+ नई समस्या दर्ज करें",
    "no_complaints_yet": "आपने अभी तक कोई समस्या दर्ज नहीं की है।",
    "report_first": "अपनी पहली शिकायत दर्ज करें →",

    "report_heading": "सामाजिक समस्या दर्ज करें",
    "reported_by": "शिकायतकर्ता",
    "autofill_note": "आपके खाते से अपने-आप भरा गया — विवरण दोबारा भरने की ज़रूरत नहीं।",
    "problem_title": "समस्या का शीर्षक",
    "problem_title_ph": "जैसे: स्कूल के पास टूटी सड़क",
    "describe_problem": "समस्या का विवरण दें",
    "describe_problem_ph": "क्या हो रहा है, और इससे लोगों पर क्या असर पड़ रहा है?",
    "category": "श्रेणी",
    "category_hint": "AI आपकी फोटो को नीचे बताई गई समस्या से मिलाकर जाँच करेगा।",
    "district": "ज़िला",
    "location_details": "स्थान विवरण",
    "location_ph": "गाँव / वार्ड / लैंडमार्क",
    "evidence_label": "फोटो या वीडियो प्रमाण",
    "evidence_click": "समस्या की फोटो या वीडियो अपलोड करने के लिए क्लिक करें",
    "evidence_hint": "JPG, PNG, WEBP, या MP4/MOV — सत्यापन के लिए आवश्यक",
    "btn_submit_problem": "समस्या दर्ज करें",

    "banner_ai_verified": "🤖 आपकी फोटो बताई गई समस्या से मेल खाती है — AI द्वारा सत्यापित ({conf}% विश्वास)। अधिकारी द्वारा समाधान शुरू होने की प्रतीक्षा है।",
    "banner_pending_officer": "🕵️ क्षेत्रीय अधिकारी द्वारा मैन्युअल सत्यापन की प्रतीक्षा है।",
    "banner_overdue": "⏰ यह मामला अपनी समाधान समय-सीमा ({deadline}) पार कर चुका है।",
    "banner_accepted": "✓ {officer} द्वारा स्वीकृत। समाधान की समय-सीमा {deadline} है ({days} दिन शेष)।",
    "banner_reopened": "🔁 अपलोड किए गए समाधान में पर्याप्त बदलाव नहीं दिखा — मामला फिर से खोला गया है।",
    "banner_resolved": "✅ {date} को हल और सत्यापित।",
    "banner_rejected": "✕ इस शिकायत की समीक्षा कर इसे अस्वीकार कर दिया गया।",

    "problem_section": "समस्या",
    "reported_by_section": "शिकायतकर्ता",
    "evidence_section": "प्रमाण",
    "evidence_before": "पहले — नागरिक द्वारा प्रस्तुत",
    "evidence_after_officer": "बाद में — अधिकारी द्वारा अपलोड",
    "evidence_after_pending": "समाधान की फोटो अभी अपलोड नहीं हुई है",
    "ai_resolution_check": "AI समाधान जाँच",
    "progress_timeline": "प्रगति समयरेखा",
    "change_score": "परिवर्तन स्कोर",

    "ai_verification_panel": "🤖 AI सत्यापन",
    "ai_match": "फोटो और विवरण मेल खाते हैं।",
    "ai_mismatch": "फोटो विवरण की पुष्टि नहीं कर सका।",
    "ai_signals": "आकलित संकेत",
    "ai_warnings": "गुणवत्ता टिप्पणी",

    "officer_queue_title": "सत्यापन कतार",
    "needs_review": "समीक्षा आवश्यक",
    "waiting": "प्रतीक्षारत",
    "nothing_waiting": "अभी समीक्षा हेतु कुछ भी प्रतीक्षारत नहीं है।",
    "my_active_cases": "मेरे सक्रिय मामले",
    "in_progress": "प्रगति में",
    "no_active_cases": "आपको कोई सक्रिय मामला नहीं सौंपा गया है।",
    "recently_resolved": "आपके द्वारा हाल में हल किए गए",
    "no_resolved_yet": "अभी तक कोई मामला हल नहीं हुआ है।",
    "due": "नियत तिथि",

    "take_action": "कार्रवाई करें",
    "btn_verify_accept": "सत्यापित करें व स्वीकार करें",
    "btn_accept_begin": "स्वीकार करें व समाधान शुरू करें",
    "rejection_reason_label": "अस्वीकृति का कारण (यदि अस्वीकार कर रहे हैं)",
    "rejection_reason_ph": "बताएं कि यह शिकायत मान्य / सत्यापन योग्य क्यों नहीं है",
    "btn_reject": "शिकायत अस्वीकार करें",
    "upload_resolution": "समाधान प्रमाण अपलोड करें",
    "upload_resolution_hint": "समय-सीमा: {deadline}। उसी स्थान की \"बाद की\" फोटो अपलोड करें — इसकी स्वतः तुलना मूल फोटो से की जाएगी।",
    "evidence_upload_after": "हल किए गए स्थान की फोटो अपलोड करने के लिए क्लिक करें",
    "evidence_after_hint": "स्वचालित तुलना के लिए JPG, PNG, या WEBP उपयुक्त है",
    "btn_submit_resolution": "AI सत्यापन हेतु समाधान जमा करें",
    "case_resolved_on": "✅ मामला {date} को हल व सत्यापित हुआ।",
    "case_rejected": "✕ अस्वीकृत।",

    "admin_overview": "एडमिन अवलोकन",
    "total_complaints": "कुल शिकायतें",
    "open": "खुली",
    "resolved": "हल हुईं",
    "overdue": "समय-सीमा पार",
    "all_complaints": "सभी शिकायतें",
    "th_id": "आईडी",
    "th_title": "शीर्षक",
    "th_district": "ज़िला",
    "th_category": "श्रेणी",
    "th_officer": "अधिकारी",
    "th_status": "स्थिति",
    "no_complaints_filed": "अभी तक कोई शिकायत दर्ज नहीं हुई।",
    "officers_count": "अधिकारी",
    "no_officers_yet": "अभी कोई अधिकारी नहीं है।",
    "add_officer": "अधिकारी जोड़ें",
    "temp_password": "अस्थायी पासवर्ड",
    "btn_create_officer": "अधिकारी खाता बनाएं",
    "assignment": "असाइनमेंट",
    "currently": "वर्तमान में",
    "unassigned": "असाइन नहीं किया गया",
    "due_label": "नियत",
    "assign_reassign": "अधिकारी असाइन / पुनः असाइन करें",
    "btn_assign": "असाइन करें (5-दिन की समय-सीमा फिर से शुरू होगी)",
    "timeline": "समयरेखा",

    "status_submitted": "दर्ज की गई",
    "status_ai_verified": "🤖 AI सत्यापित",
    "status_pending_officer": "अधिकारी समीक्षा लंबित",
    "status_accepted": "प्रगति में",
    "status_resolved": "✓ हल हुई",
    "status_reopened": "फिर से खोली गई",
    "status_rejected": "अस्वीकृत",
    "status_overdue": "⏰ समय-सीमा पार",

    "cat_roads": "सड़क व अवसंरचना",
    "cat_water": "जल संसाधन",
    "cat_electricity": "बिजली",
    "cat_sanitation": "स्वच्छता",
    "cat_health": "स्वास्थ्य सेवा",
    "cat_education": "शिक्षा",
    "cat_safety": "सार्वजनिक सुरक्षा",
    "cat_other": "अन्य",

    "dist_ranchi": "राँची",
    "dist_dhanbad": "धनबाद",
    "dist_dumka": "दुमका",
    "dist_bokaro": "बोकारो",
    "dist_gumla": "गुमला",
    "dist_deoghar": "देवघर",
    "dist_hazaribagh": "हज़ारीबाग",
    "dist_giridih": "गिरिडीह",
    "dist_east_singhbhum": "पूर्वी सिंहभूम",
    "dist_west_singhbhum": "पश्चिमी सिंहभूम",

    "footer_note": "झारखंड समाधान — एक Smart India Hackathon प्रोटोटाइप।",
},

# --- Core navigation/status/category vocabulary for other languages.
# Anything not listed here falls back along the chain defined in LANGUAGES
# (most Jharkhand languages -> Hindi, most others -> English) so the UI
# never breaks or shows a raw key.

"nag": {
    "app_name": "झारखंड समाधान", "language": "बोली",
    "nav_home": "घर", "nav_my_complaints": "हमार शिकायत", "nav_report": "समस्या लिखाईं",
    "btn_login": "लॉगिन करीं", "btn_submit_problem": "समस्या भेजीं",
    "role_citizen": "नागरिक", "role_officer": "अफसर", "role_admin": "एडमिन",
},

"khr": {
    "app_name": "झारखंड समाधान", "language": "बोली",
    "nav_home": "घर", "nav_my_complaints": "हमर शिकायत", "nav_report": "समस्या लिखो",
    "btn_login": "लॉगिन करो", "btn_submit_problem": "समस्या भेजो",
    "role_citizen": "नागरिक", "role_officer": "अफसर", "role_admin": "एडमिन",
},

"pnx": {
    "app_name": "झारखंड समाधान", "language": "भाषा",
    "nav_home": "घर", "nav_my_complaints": "हमर शिकायत", "nav_report": "समस्या लिखू",
    "btn_login": "लॉगिन करू", "btn_submit_problem": "समस्या पठाऊ",
    "role_citizen": "नागरिक", "role_officer": "अफसर", "role_admin": "एडमिन",
},

"sat": {
    "app_name": "ᱡᱷᱟᱨᱠᱷᱚᱸᱰ ᱥᱟᱢᱟᱫᱷᱟᱱ", "language": "ᱯᱟᱹᱨᱥᱤ",
    "nav_home": "ᱚᱲᱟᱜ", "role_citizen": "ᱦᱚᱲ",
},

"hoc": {"app_name": "झारखंड समाधान"},
"unr": {"app_name": "झारखंड समाधान"},
"kru": {"app_name": "झारखंड समाधान"},
"kha": {"app_name": "झारखंड समाधान"},

"bn": {
    "app_name": "ঝাড়খণ্ড সমাধান", "language": "ভাষা",
    "nav_home": "হোম", "nav_register": "নাগরিক হিসেবে নিবন্ধন করুন",
    "nav_my_complaints": "আমার অভিযোগ", "nav_report": "সমস্যা রিপোর্ট করুন",
    "nav_queue": "সারি", "nav_overview": "সংক্ষিপ্ত বিবরণ", "nav_logout": "লগ আউট",
    "login_title": "লগইন", "email": "ইমেল", "password": "পাসওয়ার্ড", "btn_login": "লগ ইন করুন",
    "full_name": "পূর্ণ নাম", "phone": "ফোন নম্বর", "btn_create_account": "অ্যাকাউন্ট তৈরি করুন",
    "my_complaints": "আমার অভিযোগ", "btn_new_report": "+ নতুন সমস্যা রিপোর্ট করুন",
    "role_citizen": "নাগরিক", "role_officer": "অফিসার", "role_admin": "অ্যাডমিন",
    "status_submitted": "জমা দেওয়া হয়েছে", "status_resolved": "✓ সমাধান হয়েছে",
    "status_pending_officer": "অফিসারের পর্যালোচনা বাকি", "status_rejected": "প্রত্যাখ্যাত",
},

"or": {
    "app_name": "ଝାଡ଼ଖଣ୍ଡ ସମାଧାନ", "language": "ଭାଷା",
    "nav_home": "ମୂଳପୃଷ୍ଠା", "nav_my_complaints": "ମୋର ଅଭିଯୋଗ", "nav_report": "ସମସ୍ୟା ରିପୋର୍ଟ କରନ୍ତୁ",
    "login_title": "ଲଗଇନ", "email": "ଇମେଲ", "password": "ପାସୱାର୍ଡ", "btn_login": "ଲଗ ଇନ",
    "role_citizen": "ନାଗରିକ", "role_officer": "ଅଧିକାରୀ", "role_admin": "ଆଡମିନ",
},

"mr": {
    "app_name": "झारखंड समाधान", "language": "भाषा",
    "nav_home": "मुख्यपृष्ठ", "nav_my_complaints": "माझ्या तक्रारी", "nav_report": "समस्या नोंदवा",
    "login_title": "लॉगिन", "email": "ईमेल", "password": "पासवर्ड", "btn_login": "लॉग इन करा",
    "full_name": "पूर्ण नाव", "phone": "फोन नंबर", "btn_create_account": "खाते तयार करा",
    "role_citizen": "नागरिक", "role_officer": "अधिकारी", "role_admin": "प्रशासक",
    "status_resolved": "✓ निकाली", "status_rejected": "नाकारले",
},

"gu": {
    "app_name": "ઝારખંડ સમાધાન", "language": "ભાષા",
    "nav_home": "હોમ", "nav_my_complaints": "મારી ફરિયાદો", "nav_report": "સમસ્યાની જાણ કરો",
    "login_title": "લૉગિન", "email": "ઇમેઇલ", "password": "પાસવર્ડ", "btn_login": "લૉગ ઇન કરો",
    "role_citizen": "નાગરિક", "role_officer": "અધિકારી", "role_admin": "એડમિન",
},

"pa": {
    "app_name": "ਝਾਰਖੰਡ ਸਮਾਧਾਨ", "language": "ਭਾਸ਼ਾ",
    "nav_home": "ਹੋਮ", "nav_my_complaints": "ਮੇਰੀਆਂ ਸ਼ਿਕਾਇਤਾਂ", "nav_report": "ਸਮੱਸਿਆ ਦਰਜ ਕਰੋ",
    "login_title": "ਲੌਗਇਨ", "email": "ਈਮੇਲ", "password": "ਪਾਸਵਰਡ", "btn_login": "ਲੌਗ ਇਨ ਕਰੋ",
    "role_citizen": "ਨਾਗਰਿਕ", "role_officer": "ਅਫ਼ਸਰ", "role_admin": "ਐਡਮਿਨ",
},

"ta": {
    "app_name": "ஜார்க்கண்ட் சமாதான்", "language": "மொழி",
    "nav_home": "முகப்பு", "nav_my_complaints": "எனது புகார்கள்", "nav_report": "பிரச்சனையைப் புகாரளிக்கவும்",
    "login_title": "உள்நுழைய", "email": "மின்னஞ்சல்", "password": "கடவுச்சொல்", "btn_login": "உள்நுழைக",
    "role_citizen": "குடிமகன்", "role_officer": "அதிகாரி", "role_admin": "நிர்வாகி",
},

"te": {
    "app_name": "ఝార్ఖండ్ సమాధాన్", "language": "భాష",
    "nav_home": "హోమ్", "nav_my_complaints": "నా ఫిర్యాదులు", "nav_report": "సమస్యను నివేదించండి",
    "login_title": "లాగిన్", "email": "ఇమెయిల్", "password": "పాస్‌వర్డ్", "btn_login": "లాగిన్ చేయండి",
    "role_citizen": "పౌరుడు", "role_officer": "అధికారి", "role_admin": "అడ్మిన్",
},

"kn": {
    "app_name": "ಝಾರ್ಖಂಡ್ ಸಮಾಧಾನ್", "language": "ಭಾಷೆ",
    "nav_home": "ಮುಖಪುಟ", "nav_my_complaints": "ನನ್ನ ದೂರುಗಳು", "nav_report": "ಸಮಸ್ಯೆ ವರದಿ ಮಾಡಿ",
    "login_title": "ಲಾಗಿನ್", "email": "ಇಮೇಲ್", "password": "ಪಾಸ್‌ವರ್ಡ್", "btn_login": "ಲಾಗಿನ್ ಮಾಡಿ",
    "role_citizen": "ನಾಗರಿಕ", "role_officer": "ಅಧಿಕಾರಿ", "role_admin": "ನಿರ್ವಾಹಕ",
},

"ml": {
    "app_name": "ഝാർഖണ്ഡ് സമാധാൻ", "language": "ഭാഷ",
    "nav_home": "ഹോം", "nav_my_complaints": "എന്റെ പരാതികൾ", "nav_report": "പ്രശ്നം റിപ്പോർട്ട് ചെയ്യുക",
    "login_title": "ലോഗിൻ", "email": "ഇമെയിൽ", "password": "പാസ്‌വേഡ്", "btn_login": "ലോഗിൻ ചെയ്യുക",
    "role_citizen": "പൗരൻ", "role_officer": "ഓഫീസർ", "role_admin": "അഡ്മിൻ",
},

"ur": {
    "app_name": "جھارکھنڈ سمادھان", "language": "زبان",
    "nav_home": "ہوم", "nav_my_complaints": "میری شکایات", "nav_report": "مسئلہ درج کریں",
    "login_title": "لاگ ان", "email": "ای میل", "password": "پاس ورڈ", "btn_login": "لاگ ان کریں",
    "role_citizen": "شہری", "role_officer": "افسر", "role_admin": "ایڈمن",
},

"as": {
    "app_name": "ঝাৰখণ্ড সমাধান", "language": "ভাষা",
    "nav_home": "হোম", "nav_my_complaints": "মোৰ অভিযোগ", "nav_report": "সমস্যা প্ৰতিবেদন কৰক",
    "login_title": "লগইন", "email": "ইমেইল", "password": "পাছৱৰ্ড", "btn_login": "লগ ইন কৰক",
    "role_citizen": "নাগৰিক", "role_officer": "বিষয়া", "role_admin": "প্ৰশাসক",
},

}


# ---------------------------------------------------------------------------
# category / district canonical-value -> translation-key maps
# (form values stay in English for business logic; only the *label* shown
# to the user is translated)
# ---------------------------------------------------------------------------

CATEGORY_KEYS = {
    "Roads & Infrastructure": "cat_roads",
    "Water Resources": "cat_water",
    "Electricity": "cat_electricity",
    "Sanitation": "cat_sanitation",
    "Healthcare": "cat_health",
    "Education": "cat_education",
    "Public Safety": "cat_safety",
    "Other": "cat_other",
}

DISTRICT_KEYS = {
    "Ranchi": "dist_ranchi", "Dhanbad": "dist_dhanbad", "Dumka": "dist_dumka",
    "Bokaro": "dist_bokaro", "Gumla": "dist_gumla", "Deoghar": "dist_deoghar",
    "Hazaribagh": "dist_hazaribagh", "Giridih": "dist_giridih",
    "East Singhbhum": "dist_east_singhbhum", "West Singhbhum": "dist_west_singhbhum",
}


# ---------------------------------------------------------------------------
# lookup with fallback chain
# ---------------------------------------------------------------------------

def _chain(lang):
    """[lang, lang's fallback, that fallback's fallback, ..., 'en']"""
    seen, code, out = set(), lang, []
    while code and code not in seen:
        out.append(code)
        seen.add(code)
        code = LANGUAGE_META.get(code, {}).get("fallback")
    if "en" not in out:
        out.append("en")
    return out


def current_lang():
    return getattr(g, "lang", DEFAULT_LANG)


def t(key, **kwargs):
    for code in _chain(current_lang()):
        val = TR.get(code, {}).get(key)
        if val is not None:
            return val.format(**kwargs) if kwargs else val
    return key  # last resort — only hit for a genuinely undefined key (a bug)


def cat_label(category):
    return t(CATEGORY_KEYS.get(category, "cat_other"))


def dist_label(district):
    key = DISTRICT_KEYS.get(district)
    return t(key) if key else district
