"""
Internationalisation for Jharkhand Samadhan.

Design:
- English and Hindi are the two fully-translated UI languages. The language
  switcher offers exactly these two — nothing else.
- t(key) looks the key up in the active language and falls back to English,
  so the UI never shows a raw key.
"""

from flask import g
import translation

# (code, native_name, english_name, group, fallback_code)
# Only English and Hindi are offered — nothing else.
LANGUAGES = [
    ("en", "English", "English", "primary", None),
    ("hi", "हिन्दी", "Hindi", "primary", None),
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
    "hero_badge": "YOUR EVERY PROBLEM, SOLVED",
    "hero_intro": "Citizens report local problems with photo or video evidence. Road and infrastructure reports are automatically screened against recent satellite imagery; everything else is verified by an officer. Once accepted, officers must resolve the case within a set deadline — and a before/after image check decides whether it's really fixed before the case closes.",
    "btn_register_citizen": "Register as Citizen ›",
    "problems_title": "Problems this platform solves",
    "problems_sub": "From crumbling roads to garbage piles — snap a photo, file a report, and watch it get fixed. These are the everyday problems Samadhan is built for.",
    "p1_title": "Broken roads & potholes",
    "p1_desc": "Crumbling village lanes, dangerous potholes, and damaged culverts that make travel risky.",
    "p2_title": "Water & handpumps",
    "p2_desc": "Dry handpumps, leaking pipes, and unsafe drinking water reaching homes.",
    "p3_title": "Electricity & lighting",
    "p3_desc": "Dead streetlights, frequent power cuts, and villages still waiting for electrification.",
    "p4_title": "Sanitation & garbage",
    "p4_desc": "Garbage piles on streets, choked drains, and public spaces that are never cleaned.",
    "p5_title": "Healthcare access",
    "p5_desc": "Neglected health centres, missing doctors, and medical facilities far from home.",
    "p6_title": "Schools & education",
    "p6_desc": "Broken school buildings, no drinking water or toilets, and missing supplies for children.",
    "how_title": "How Samadhan works",
    "how_sub": "Three simple steps from a problem to a solution.",
    "s1_title": "Report with proof",
    "s1_desc": "Snap a photo or video of the problem and pin its location. Road reports even get an automatic satellite check.",
    "s2_title": "Verified & assigned",
    "s2_desc": "A field officer verifies your complaint and accepts the case with a fixed resolution deadline.",
    "s3_title": "Watch it get fixed",
    "s3_desc": "The officer uploads the after photo. Our AI compares before and after, then closes the case for good.",

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

    "reg_verify_title": "Verify your details",
    "reg_verify_body": "We sent a 6-digit code to your phone and another to your email. Enter both below within 10 minutes to create your account.",
    "phone_otp_label": "Phone OTP",
    "email_otp_label": "Email OTP",
    "btn_verify_create": "Verify & Create Account",
    "btn_resend": "Resend",
    "reg_otp_sent": "Verification codes sent to your phone and email.",
    "reg_welcome": "Welcome, {name}! Your citizen account is ready.",
    "otp_demo_note": "Demo (no SMS/email gateway): your code is",
    "otp_sent_phone": "OTP sent to your phone {phone}.",
    "otp_sent_email": "OTP sent to your email {email}.",
    "otp_invalid": "That OTP is wrong or has expired. Please request a new one.",
    "otp_phone_invalid": "The phone OTP is wrong or has expired.",
    "otp_email_invalid": "The email OTP is wrong or has expired.",
    "otp_label": "Mobile OTP",
    "otp_verify_title": "Verify it's you",
    "otp_account_hint": "To save any change here, first tap Send OTP, then enter the 6-digit code sent to your registered mobile number.",
    "send_otp": "Send OTP",

    "account_title": "My Account",
    "account_details": "Personal Details",
    "profile_photo": "Profile Photo",
    "photo_explain": "Upload your photo, or leave it empty and a picture will be fetched automatically from your email address.",
    "btn_upload_photo": "Upload Photo",
    "btn_remove_photo": "Remove Photo",
    "alternate_phone": "Alternate Phone Number",
    "home_address": "Home Address",
    "btn_save_changes": "Save Changes",
    "account_updated": "Your account details have been saved.",
    "photo_removed": "Profile photo removed — showing the one fetched from your email instead.",

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
    "evidence_gps_hint": "No GPS tag on the photo? No problem — we'll use the location you picked on the map.",
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
    "dist_chatra": "Chatra",
    "dist_garhwa": "Garhwa",
    "dist_godda": "Godda",
    "dist_jamtara": "Jamtara",
    "dist_khunti": "Khunti",
    "dist_koderma": "Koderma",
    "dist_latehar": "Latehar",
    "dist_lohardaga": "Lohardaga",
    "dist_pakur": "Pakur",
    "dist_palamu": "Palamu",
    "dist_ramgarh": "Ramgarh",
    "dist_sahibganj": "Sahibganj",
    "dist_saraikela_kharsawan": "Saraikela-Kharsawan",
    "dist_simdega": "Simdega",

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
    "hero_badge": "आपकी हर समस्या, हल",
    "hero_intro": "नागरिक फोटो या वीडियो प्रमाण के साथ स्थानीय समस्याएँ दर्ज करते हैं। सड़क और बुनियादी ढाँचे की शिकायतें ताज़ा सैटेलाइट तस्वीरों से अपने-आप जाँची जाती हैं; बाकी सबकी पुष्टि अधिकारी करते हैं। स्वीकृति के बाद अधिकारी को तय समय-सीमा में समाधान करना होता है — और पहले/बाद की तस्वीरों की तुलना से तय होता है कि मामला वाकई हल हुआ है या नहीं।",
    "btn_register_citizen": "नागरिक के रूप में पंजीकरण ›",
    "problems_title": "इस मंच से हल होने वाली समस्याएँ",
    "problems_sub": "टूटी सड़कों से लेकर कचरे के ढेर तक — फोटो खींचें, शिकायत दर्ज करें, और समाधान देखें। समाधान इन्हीं रोज़मर्रा की समस्याओं के लिए बना है।",
    "p1_title": "टूटी सड़कें व गड्ढे",
    "p1_desc": "जर्जर गाँव की गलियाँ, खतरनाक गड्ढे और क्षतिग्रस्त पुलिया जिनसे सफ़र जोखिम भरा हो।",
    "p2_title": "पानी व हैंडपंप",
    "p2_desc": "सूखे हैंडपंप, रिसती पाइपलाइनें और घरों तक पहुँचता असुरक्षित पेयजल।",
    "p3_title": "बिजली व रोशनी",
    "p3_desc": "बंद स्ट्रीटलाइटें, बार-बार बिजली कटौती और अब भी बिजली का इंतज़ार करते गाँव।",
    "p4_title": "सफ़ाई व कचरा",
    "p4_desc": "सड़कों पर कचरे के ढेर, जाम नालियाँ और कभी साफ़ न होने वाले सार्वजनिक स्थल।",
    "p5_title": "स्वास्थ्य सुविधाएँ",
    "p5_desc": "उपेक्षित स्वास्थ्य केंद्र, डॉक्टरों की कमी और घर से दूर चिकित्सा सुविधाएँ।",
    "p6_title": "स्कूल व शिक्षा",
    "p6_desc": "टूटे स्कूल भवन, पेयजल-शौचालय की कमी और बच्चों के लिए ज़रूरी सामान का अभाव।",
    "how_title": "समाधान कैसे काम करता है",
    "how_sub": "समस्या से समाधान तक तीन आसान चरण।",
    "s1_title": "प्रमाण के साथ दर्ज करें",
    "s1_desc": "समस्या की फोटो या वीडियो लें और उसका स्थान दर्ज करें। सड़क की शिकायतें सैटेलाइट जाँच से भी गुज़रती हैं।",
    "s2_title": "सत्यापित व सौंपा गया",
    "s2_desc": "क्षेत्रीय अधिकारी आपकी शिकायत की पुष्टि करते हैं और तय समय-सीमा के साथ मामला स्वीकार करते हैं।",
    "s3_title": "हल होते देखें",
    "s3_desc": "अधिकारी बाद की फोटो अपलोड करते हैं। हमारा AI पहले/बाद की तुलना करता है, फिर मामला हमेशा के लिए बंद होता है।",

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

    "reg_verify_title": "अपना विवरण सत्यापित करें",
    "reg_verify_body": "हमने आपके फ़ोन पर और एक आपके ईमेल पर 6 अंकों का कोड भेजा है। खाता बनाने के लिए 10 मिनट के भीतर दोनों दर्ज करें।",
    "phone_otp_label": "फ़ोन OTP",
    "email_otp_label": "ईमेल OTP",
    "btn_verify_create": "सत्यापित करें व खाता बनाएं",
    "btn_resend": "पुनः भेजें",
    "reg_otp_sent": "आपके फ़ोन और ईमेल पर सत्यापन कोड भेजे गए।",
    "reg_welcome": "स्वागत है, {name}! आपका नागरिक खाता तैयार है।",
    "otp_demo_note": "डेमो (कोई SMS/ईमेल गेटवे नहीं): आपका कोड है",
    "otp_sent_phone": "आपके फ़ोन {phone} पर OTP भेजा गया।",
    "otp_sent_email": "आपके ईमेल {email} पर OTP भेजा गया।",
    "otp_invalid": "वह OTP गलत है या समाप्त हो चुका है। कृपया नया मँगवाएँ।",
    "otp_phone_invalid": "फ़ोन OTP गलत है या समाप्त हो चुका है।",
    "otp_email_invalid": "ईमेल OTP गलत है या समाप्त हो चुका है।",
    "otp_label": "मोबाइल OTP",
    "otp_verify_title": "पुष्टि करें कि यह आप ही हैं",
    "otp_account_hint": "यहाँ कोई भी बदलाव सहेजने के लिए पहले OTP भेजें दबाएँ, फिर अपने पंजीकृत मोबाइल नंबर पर आया 6 अंकों का कोड दर्ज करें।",
    "send_otp": "OTP भेजें",

    "account_title": "मेरा खाता",
    "account_details": "व्यक्तिगत विवरण",
    "profile_photo": "प्रोफ़ाइल फ़ोटो",
    "photo_explain": "अपनी फ़ोटो अपलोड करें, या खाली छोड़ने पर आपके ईमेल से एक फ़ोटो अपने-आप ली जाएगी।",
    "btn_upload_photo": "फ़ोटो अपलोड करें",
    "btn_remove_photo": "फ़ोटो हटाएँ",
    "alternate_phone": "वैकल्पिक फ़ोन नंबर",
    "home_address": "घर का पता",
    "btn_save_changes": "बदलाव सहेजें",
    "account_updated": "आपके खाते का विवरण सहेज लिया गया है।",
    "photo_removed": "प्रोफ़ाइल फ़ोटो हटा दी गई — ईमेल वाली फ़ोटो दिखाई जाएगी।",

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
    "evidence_gps_hint": "फोटो में GPS टैग नहीं है? कोई बात नहीं — हम मानचित्र पर चुनी गई लोकेशन का उपयोग करेंगे।",
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
    "dist_chatra": "चतरा",
    "dist_garhwa": "गढ़वा",
    "dist_godda": "गोड्डा",
    "dist_jamtara": "जामताड़ा",
    "dist_khunti": "खूंटी",
    "dist_koderma": "कोडरमा",
    "dist_latehar": "लातेहार",
    "dist_lohardaga": "लोहरदग्गा",
    "dist_pakur": "पाकुड़",
    "dist_palamu": "पलामू",
    "dist_ramgarh": "रामगढ़",
    "dist_sahibganj": "साहिबगंज",
    "dist_saraikela_kharsawan": "सरायकेला-खरसावां",
    "dist_simdega": "सिमडेगा",

    "footer_note": "झारखंड समाधान — एक Smart India Hackathon प्रोटोटाइप।",
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
    "Bokaro": "dist_bokaro", "Chatra": "dist_chatra", "Deoghar": "dist_deoghar",
    "Dhanbad": "dist_dhanbad", "Dumka": "dist_dumka",
    "East Singhbhum": "dist_east_singhbhum", "Garhwa": "dist_garhwa",
    "Giridih": "dist_giridih", "Godda": "dist_godda", "Gumla": "dist_gumla",
    "Hazaribagh": "dist_hazaribagh", "Jamtara": "dist_jamtara",
    "Khunti": "dist_khunti", "Koderma": "dist_koderma", "Latehar": "dist_latehar",
    "Lohardaga": "dist_lohardaga", "Pakur": "dist_pakur", "Palamu": "dist_palamu",
    "Ramgarh": "dist_ramgarh", "Ranchi": "dist_ranchi", "Sahibganj": "dist_sahibganj",
    "Saraikela-Kharsawan": "dist_saraikela_kharsawan", "Simdega": "dist_simdega",
    "West Singhbhum": "dist_west_singhbhum",
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
    lang = current_lang()
    for code in _chain(lang):
        val = TR.get(code, {}).get(key)
        if val is not None:
            if code == "en" and lang != "en":
                # The active language has no translation yet — let the runtime
                # auto-translator produce one (and cache it), so new strings
                # get translated without re-running any process. If it can't
                # (network off, throttled, unsupported language) we keep the
                # English value — the UI never shows a raw key.
                auto = _auto_translate(lang, key, val)
                if auto is not None:
                    return auto.format(**kwargs) if kwargs else auto
            return val.format(**kwargs) if kwargs else val
    return key  # last resort — only hit for a genuinely undefined key (a bug)


# in-process memo: key -> translated value or None (avoid repeat network calls
# and repeated cache-file reads within one process)
_runtime_memo = {}


def _auto_translate(lang, key, en_val):
    """Translate the English value of a missing key into `lang` on the fly."""
    if "{" in en_val:  # has .format() placeholders — would get mangled
        return None
    memo_key = (lang, key)
    if memo_key in _runtime_memo:
        return _runtime_memo[memo_key]
    out = translation.translate(en_val, lang)
    _runtime_memo[memo_key] = out
    return out


def tr_text(text, lang=None):
    """
    Translate a piece of dynamic text (e.g. a complaint title, an officer's
    note, new data pushed into the app later) into the viewer's language on
    demand. Falls back to the original text when translation isn't possible.
    """
    lang = lang or current_lang()
    if lang == "en" or not text or not text.strip():
        return text
    if not any(ch.isalpha() for ch in text):  # IDs, timestamps, numbers...
        return text
    memo_key = ("text", lang, text)
    if memo_key in _runtime_memo:
        return _runtime_memo[memo_key]
    out = translation.translate(text, lang) or text
    _runtime_memo[memo_key] = out
    return out


def cat_label(category):
    return t(CATEGORY_KEYS.get(category, "cat_other"))


def dist_label(district):
    key = DISTRICT_KEYS.get(district)
    return t(key) if key else district
