from flask import Flask, request, render_template_string
import re

app = Flask(__name__)
def analyze_offer(text):

    text_lower = text.lower()

    score = 0
    warnings = []
    risk_categories = {
    "Payment Risk": "LOW",
    "Communication Risk": "LOW",
    "Selection Risk": "LOW",
    "Data Privacy Risk": "LOW",
    "Link Risk": "LOW",
    "Urgency Risk": "LOW"
}

    def add_warning(points, severity, title, explanation):
        nonlocal score
        score += points

        if title == "Payment request detected":
            risk_categories["Payment Risk"] = "HIGH"

        elif title == "Urgency-based language detected":
            risk_categories["Urgency Risk"] = "MEDIUM"

        elif title == "Unofficial communication detected":
            risk_categories["Communication Risk"] = "MEDIUM"

        elif title == "Unrealistic selection claim detected":
            risk_categories["Selection Risk"] = "MEDIUM"

        elif title in [
            "Sensitive information request detected",
            "Personal document request detected"
        ]:
            risk_categories["Data Privacy Risk"] = "HIGH"

        elif title in [
            "External link detected",
            "Potentially suspicious link pattern detected"
        ]:
            risk_categories["Link Risk"] = "HIGH"

        warnings.append({

       
            "points": points,
            "severity": severity,
            "title": title,
            "explanation": explanation
        })

    # PAYMENT
    payment_patterns = [
        "registration fee",
        "processing fee",
        "verification fee",
        "security deposit",
        "joining fee",
        "application fee",
        "training fee",
        "certificate fee",
        "pay to confirm",
        "pay ₹",
        "pay rs",
        "pay inr",
        "deposit",
        "upfront payment",
        "advance payment"
    ]

    safe_payment_phrases = [
        "no registration fee",
        "no payment required",
        "no fee required",
        "no payment is required",
        "without any payment",
        "does not require payment",
        "no registration or payment"
    ]

    has_payment_request = any(
        pattern in text_lower
        for pattern in payment_patterns
    )

    has_safe_payment_phrase = any(
        phrase in text_lower
        for phrase in safe_payment_phrases
    )

    if has_payment_request and not has_safe_payment_phrase:

        add_warning(
            35,
            "HIGH",
            "Payment request detected",
            "The offer appears to request money before the internship or job proceeds."
        )

    # URGENCY
    urgency_patterns = [
        "urgent",
        "immediately",
        "today only",
        "within 2 hours",
        "within 24 hours",
        "limited time",
        "act now",
        "last chance",
        "expires today",
        "respond now"
    ]

    if any(pattern in text_lower for pattern in urgency_patterns):

        add_warning(
            20,
            "MEDIUM",
            "Urgency-based language detected",
            "The message may be pressuring the applicant to make a quick decision."
        )

    # UNOFFICIAL COMMUNICATION
    communication_patterns = [
        "telegram",
        "whatsapp only",
        "contact me on whatsapp",
        "dm me",
        "message me personally",
        "contact hr on telegram"
    ]

    if any(pattern in text_lower for pattern in communication_patterns):

        add_warning(
            15,
            "MEDIUM",
            "Unofficial communication detected",
            "Verify the recruiter and company independently through official channels."
        )

    # GUARANTEED / UNREALISTIC CLAIMS
    guaranteed_patterns = [
        "guaranteed job",
        "guaranteed internship",
        "guaranteed work-from-home internship",
        "internship is guaranteed",
        "job is guaranteed",
        "100% selection",
        "guaranteed placement",
        "no interview required",
        "no interview is required",
        "without an interview",
        "direct selection",
        "directly selected",
        "job guaranteed",
        "instant selection",
        "100% job",
        "selection is guaranteed",
        "selection guaranteed"
    ]

    if any(pattern in text_lower for pattern in guaranteed_patterns):

        add_warning(
            20,
            "MEDIUM",
            "Unrealistic selection claim detected",
            "Guaranteed selection claims should be independently verified."
        )

    # SENSITIVE INFORMATION
    sensitive_patterns = [
        "otp",
        "bank details",
        "bank account",
        "card number",
        "cvv",
        "upi pin",
        "password",
        "login credentials",
        "net banking password"
    ]

    if any(pattern in text_lower for pattern in sensitive_patterns):

        add_warning(
            30,
            "HIGH",
            "Sensitive information request detected",
            "Never share OTPs, PINs, passwords or unnecessary financial information."
        )

    # PERSONAL DOCUMENTS
    document_patterns = [
        "send your aadhaar",
        "aadhaar card",
        "pan card",
        "send your pan",
        "passport copy",
        "identity proof",
        "id proof"
    ]

    if any(pattern in text_lower for pattern in document_patterns):

        add_warning(
            15,
            "MEDIUM",
            "Personal document request detected",
            "Verify why the document is required and whether the request comes from an official channel."
        )

    # URL ANALYSIS
    urls = re.findall(
        r'https?://[^\s]+|www\.[^\s]+',
        text,
        re.IGNORECASE
    )

    if urls:

        add_warning(
            10,
            "LOW",
            "External link detected",
            "Review the destination carefully and verify that it belongs to the official organization."
        )

        suspicious_words = [
            "bit.ly",
            "tinyurl",
            "shorturl",
            "redirect",
            "freegift",
            "claim",
            "verify-now",
            "login-now",
            "secure-login",
            "bonus"
        ]

        if any(word in text_lower for word in suspicious_words):

            add_warning(
                20,
                "HIGH",
                "Potentially suspicious link pattern detected",
                "The link contains a pattern that deserves additional verification before opening."
            )

    # PERSONAL EMAIL
    if (
        "gmail.com" in text_lower
        or "yahoo.com" in text_lower
        or "outlook.com" in text_lower
    ):

        add_warning(
            5,
            "LOW",
            "Personal email domain mentioned",
            "Check whether the sender is officially associated with the organization."
        )

    # FAKE INTERVIEW / CERTIFICATE
    fake_claim_patterns = [
        "pay for interview",
        "paid interview",
        "certificate guaranteed",
        "pay and get certificate",
        "pay for offer letter",
        "buy internship certificate"
    ]

    if any(pattern in text_lower for pattern in fake_claim_patterns):

        add_warning(
            25,
            "HIGH",
            "Suspicious employment claim detected",
            "Requests for payment in exchange for an interview, offer letter or certificate require strong verification."
        )
    # ---------------- VERIFICATION CHECKLIST ----------------

    verification_checks = [
        "Verify the company through its official website.",
        "Check whether the recruiter uses an official company email.",
        "Verify that the internship details exist on the official careers page.",
        "Do not pay unexpected registration or training fees.",
        "Do not share OTP, UPI PIN or passwords."
    ]
    # SCORE LIMIT
    score = min(score, 100)

    # RISK LEVEL
    if score >= 70:

        level = "HIGH RISK"
        level_class = "high"

    elif score >= 40:

        level = "MEDIUM RISK"
        level_class = "medium"

    else:

        level = "LOW RISK"
        level_class = "low"

    return score, level, level_class, warnings, urls, risk_categories, verification_checks
HTML = """
<!DOCTYPE html>
<html>

<head>

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>InternGuard</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #eef2f7;
    color: #172033;
}

.header {
    background: #101827;
    color: white;
    text-align: center;
    padding: 28px 15px;
}

.logo {
    font-size: 30px;
    font-weight: bold;
}

.tagline {
    color: #cbd5e1;
    margin-top: 7px;
    font-size: 14px;
}

.container {
    width: 92%;
    max-width: 850px;
    margin: 25px auto;
}

.card {
    background: white;
    border-radius: 16px;
    padding: 25px;
    margin-bottom: 20px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.07);
}

h2 {
    margin-top: 0;
}

textarea {
    width: 100%;
    height: 170px;
    resize: vertical;
    padding: 15px;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    font-size: 15px;
}

button {
    width: 100%;
    margin-top: 15px;
    padding: 15px;
    border: none;
    border-radius: 10px;
    background: #101827;
    color: white;
    font-size: 16px;
    font-weight: bold;
}

.result {
    text-align: center;
}

.score {
    font-size: 52px;
    font-weight: bold;
}

.risk {
    display: inline-block;
    padding: 8px 18px;
    border-radius: 30px;
    color: white;
    font-weight: bold;
    margin: 8px;
}

.high {
    background: #dc2626;
}

.medium {
    background: #d97706;
}

.low {
    background: #15803d;
}

.meter {
    width: 100%;
    height: 14px;
    background: #e5e7eb;
    border-radius: 20px;
    overflow: hidden;
    margin: 20px 0;
}

.meter-fill {
    height: 100%;
    background: #dc2626;
}

.warning {
    text-align: left;
    background: #f8fafc;
    border-left: 5px solid #101827;
    padding: 15px;
    margin: 12px 0;
    border-radius: 8px;
}

.warning-title {
    font-weight: bold;
    margin-bottom: 6px;
}

.points {
    float: right;
    font-weight: bold;
}

.link-box {
    text-align: left;
    background: #fff7ed;
    padding: 18px;
    border-radius: 12px;
    margin-top: 20px;
}

.checklist {
    text-align: left;
    background: #eef2ff;
    padding: 20px;
    border-radius: 12px;
    margin-top: 20px;
}

.checklist p {
    margin: 12px 0;
}

.note {
    font-size: 12px;
    color: #64748b;
    margin-top: 20px;
    line-height: 1.5;
}

.empty {
    text-align: center;
    color: #64748b;
}
.summary-box {
    text-align: left;
    background: #f1f5f9;
    padding: 18px;
    border-radius: 12px;
    margin: 20px 0;
    border-left: 5px solid #101827;
}

.summary-box p {
    margin-bottom: 0;
    line-height: 1.5;
}
.why-button {
    width: auto;
    margin-top: 10px;
    padding: 8px 12px;
    background: #e2e8f0;
    color: #172033;
    font-size: 13px;
    font-weight: bold;
    cursor: pointer;
}

.why-text {
    display: none;
    margin-top: 10px;
    padding: 12px;
    background: #f1f5f9;
    border-radius: 8px;
    line-height: 1.5;
}
</style>

</head>
<script>

function toggleWhy(button) {

    const explanation = button.nextElementSibling;

    if (explanation.style.display === "block") {

        explanation.style.display = "none";

        button.innerHTML = "🔍 Why this warning?";

    } else {

        explanation.style.display = "block";

        button.innerHTML = "🔼 Hide explanation";
    }
}
function fillExample(type) {

    const textarea = document.querySelector('textarea[name="offer"]');

    if (type === "safe") {

        textarea.value =
        "We are pleased to invite you for a Python Developer Internship at ABC Technologies. " +
        "The internship includes a technical interview and selection process. " +
        "No registration fee or payment is required. " +
        "Please apply through our official company website. " +
        "The internship details, duration and responsibilities are provided on the official portal.";

    } else {

        textarea.value =
        "Congratulations! You have been selected for a guaranteed work-from-home internship. " +
        "No interview is required. Pay a ₹999 registration fee today to confirm your position. " +
        "Contact HR on Telegram immediately. Send your Aadhaar and bank account details. " +
        "Click here: https://bit.ly/internship-verify-now";

    }
}
</script>
<body>

<div class="header">

<div class="logo">
🛡️ InternGuard
</div>

<div class="tagline">
Internship Safety & Risk Analysis Assistant
</div>

</div>


<div class="container">

<div class="card">

<h2>Analyze an Internship Offer</h2>

<p>
Paste an internship message, email or job description below.
</p>

<form method="POST">
<div class="demo-buttons">

<button
type="button"
onclick="fillExample('safe')">
🟢 Try Safe Example
</button>

<button
type="button"
onclick="fillExample('risky')">
🔴 Try Suspicious Example
</button>

</div>
<textarea
name="offer"
placeholder="Paste your internship offer here..."
required
>{{ offer }}</textarea>

<button type="submit">
🔍 ANALYZE OFFER
</button>

</form>

</div>


{% if result %}

<div class="card result">

<h2>Analysis Result</h2>

<div class="score">
{{ score }}/100
</div>

<div class="risk {{ level_class }}">
{{ level }}
</div>
<div class="summary-box">

<h3>📋 Risk Summary</h3>

<p>
{{ summary }}
</p>

</div>

<div class="meter">

<div
class="meter-fill"
style="width: {{ score }}%;">
</div>

</div>


<h3 style="text-align:left;">
🔎 Detected Risk Indicators
</h3>


{% if warnings %}

{% for warning in warnings %}

<div class="warning">

<span class="points">
+{{ warning.points }}
</span>

<div class="warning-title">
{{ warning.severity }} — {{ warning.title }}
</div>

<button
    type="button"
    class="why-button"
    onclick="toggleWhy(this)">
    🔍 Why this warning?
</button>

<div class="why-text">
{{ warning.explanation }}
</div>

</div>

{% endfor %}

{% else %}

<div class="empty">
No major warning pattern was detected by the current rules.
</div>

{% endif %}


{% if urls %}

<div class="link-box">

<h3>🔗 Link Detected</h3>

<p>
This offer contains an external link.
</p>

<p>
<strong>Recommended:</strong>
Verify the domain through the organization's official website before entering personal information.
</p>

{% for url in urls %}

<p style="word-break:break-all;">
{{ url }}
</p>

{% endfor %}

</div>

{% endif %}

<div class="checklist">

<h3>🔐 Verification Checklist</h3>

{% for check in verification_checks %}

<p>✓ {{ check }}</p>

{% endfor %}

</div>
<div class="checklist">

<h3>🛡️ What Should You Do?</h3>

<p>✓ Verify the company through its official website.</p>

<p>✓ Verify the recruiter's professional identity.</p>

<p>✓ Check the link/domain before submitting information.</p>

<p>✓ Be cautious about unexpected payment requests.</p>

<p>✓ Never share OTP, UPI PIN or passwords.</p>

<p>✓ Independently verify important claims.</p>

</div>


<div class="note">

⚠️ InternGuard provides an automated risk assessment.
A risk score is not proof that an opportunity is fraudulent.
Always independently verify the opportunity.

</div>

</div>

{% endif %}

</div>

</body>
</html>
"""
@app.route("/", methods=["GET", "POST"])
def home():

    offer = ""
    result = False
    score = 0
    level = ""
    level_class = ""
    warnings = []
    urls = []
    summary = ""
    recommendation = ""
    verification_checks = []
    risk_categories = {
    "Payment Risk": "LOW",
    "Communication Risk": "LOW",
    "Selection Risk": "LOW",
    "Data Privacy Risk": "LOW",
    "Link Risk": "LOW",
    "Urgency Risk": "LOW"
}
    if request.method == "POST":

        offer = request.form.get("offer", "")

        (
            score,
            level,
            level_class,
            warnings,
            urls,
            risk_categories,
            verification_checks
        ) = analyze_offer(offer)

        # Final recommendation
        if score >= 70:
            recommendation = (
                "🚨 HIGH RISK — Do not share sensitive information "
                "or make payments. Verify independently first."
            )

        elif score >= 40:
            recommendation = (
                "⚠️ VERIFY FIRST — Check the company, recruiter "
                "and offer details before proceeding."
            )

        else:
            recommendation = (
                "✅ LOW RISK PATTERN — No major warning pattern "
                "was detected. Continue normal verification."
            )

        result = True

        # Risk summary
        warning_count = len(warnings)

        if warning_count == 0:
            summary = "No major warning pattern was detected."

        elif score >= 70:
            summary = (
                f"{warning_count} warning signals were detected. "
                "Several indicators require careful verification before proceeding."
            )

        elif score >= 40:
            summary = (
                f"{warning_count} warning signals were detected. "
                "Verify the opportunity before taking further action."
            )

        else:
            summary = (
                f"{warning_count} minor warning signal(s) were detected. "
                "Continue with normal verification."
            )

    return render_template_string(
        HTML,
        offer=offer,
        result=result,
        score=score,
        level=level,
        level_class=level_class,
        warnings=warnings,
        urls=urls,
        summary=summary,
        verification_checks=verification_checks,
        recommendation=recommendation,
        risk_categories=risk_categories
          )
   


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
  )
