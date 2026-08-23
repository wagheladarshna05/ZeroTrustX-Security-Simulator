from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Test12345",
    database="zerotrustx_db"
)


def get_policies():
    cursor = db.cursor()

    cursor.execute("""
        SELECT policy_name, enabled
        FROM policies
    """)

    rows = cursor.fetchall()
    cursor.close()

    return {
        policy_name: bool(enabled)
        for policy_name, enabled in rows
    }


@app.route("/")
def home():
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM access_requests")
    access_requests = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM access_requests
        WHERE decision = 'ALLOW'
    """)
    allowed = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM access_requests
        WHERE decision = 'BLOCK'
    """)
    blocked = cursor.fetchone()[0]

    cursor.execute("""
        SELECT AVG(risk_score)
        FROM access_requests
    """)
    avg_result = cursor.fetchone()[0]

    avg_risk_score = round(avg_result, 1) if avg_result is not None else 0.0

    cursor.execute("""
        SELECT resource, action, risk_score, decision
        FROM access_requests
        ORDER BY requested_at DESC
        LIMIT 5
    """)
    recent_activity = cursor.fetchall()

    cursor.execute("""
        SELECT alert_type, message, severity, created_at
        FROM alerts
        ORDER BY created_at DESC
        LIMIT 5
    """)
    alerts = cursor.fetchall()

    cursor.close()

    return render_template(
        "index.html",
        total_users=total_users,
        access_requests=access_requests,
        allowed=allowed,
        blocked=blocked,
        avg_risk_score=avg_risk_score,
        recent_activity=recent_activity,
        alerts=alerts
    )


@app.route("/network")
def network():
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM access_requests
        WHERE decision = 'ALLOW'
    """)
    allowed = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM access_requests
        WHERE decision = 'BLOCK'
    """)
    blocked = cursor.fetchone()[0]

    cursor.execute("""
        SELECT AVG(risk_score)
        FROM access_requests
    """)
    avg_result = cursor.fetchone()[0]

    avg_risk_score = round(avg_result, 1) if avg_result is not None else 0.0

    cursor.execute("""
        SELECT
            ar.user_id,
            u.username,
            u.role,
            ar.resource,
            ar.action,
            ar.risk_score,
            ar.decision,
            ar.reason,
            ar.requested_at
        FROM access_requests ar
        JOIN users u ON ar.user_id = u.id
        ORDER BY ar.id DESC
        LIMIT 1
    """)
    latest_request = cursor.fetchone()

    cursor.close()

    return render_template(
        "network.html",
        total_users=total_users,
        allowed=allowed,
        blocked=blocked,
        avg_risk_score=avg_risk_score,
        latest_request=latest_request
    )


@app.route("/alerts")
def alerts_page():
    cursor = db.cursor()

    cursor.execute("""
        SELECT alert_type, message, severity, created_at
        FROM alerts
        ORDER BY created_at DESC
    """)
    alerts = cursor.fetchall()

    cursor.execute("""
        SELECT COUNT(*)
        FROM alerts
        WHERE severity = 'CRITICAL'
    """)
    critical_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM alerts
        WHERE severity = 'WARNING'
    """)
    warning_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM alerts
        WHERE severity = 'INFO'
    """)
    info_count = cursor.fetchone()[0]

    cursor.close()

    return render_template(
        "alerts.html",
        alerts=alerts,
        critical_count=critical_count,
        warning_count=warning_count,
        info_count=info_count
    )


@app.route("/policies")
def policies():
    return render_template(
        "policies.html",
        policies=get_policies(),
        saved=False
    )


@app.route("/policies/update", methods=["POST"])
def update_policies():
    mfa_enabled = 1 if request.form.get("mfa") else 0
    risk_enabled = 1 if request.form.get("risk") else 0
    high_risk_enabled = 1 if request.form.get("high_risk") else 0
    continuous_enabled = 1 if request.form.get("continuous") else 0

    cursor = db.cursor()

    policies_to_update = [
        ("Multi-Factor Authentication", mfa_enabled),
        ("Risk-Based Access Control", risk_enabled),
        ("High-Risk Access Blocking", high_risk_enabled),
        ("Continuous Verification", continuous_enabled)
    ]

    for policy_name, enabled in policies_to_update:
        cursor.execute("""
            UPDATE policies
            SET enabled = %s
            WHERE policy_name = %s
        """, (enabled, policy_name))

    db.commit()
    cursor.close()

    return render_template(
        "policies.html",
        policies=get_policies(),
        saved=True
    )


@app.route("/analytics")
def analytics():
    cursor = db.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM access_requests
    """)
    total_requests = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM access_requests
        WHERE decision = 'ALLOW'
    """)
    allowed = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM access_requests
        WHERE decision = 'BLOCK'
    """)
    blocked = cursor.fetchone()[0]

    cursor.execute("""
        SELECT AVG(risk_score)
        FROM access_requests
    """)
    avg_result = cursor.fetchone()[0]

    avg_risk_score = round(avg_result, 1) if avg_result is not None else 0.0

    if total_requests:
        allowed_percentage = round((allowed / total_requests) * 100)
        blocked_percentage = round((blocked / total_requests) * 100)
    else:
        allowed_percentage = 0
        blocked_percentage = 0

    cursor.execute("""
        SELECT resource, action, risk_score, decision
        FROM access_requests
        ORDER BY requested_at DESC
        LIMIT 5
    """)
    recent_activity = cursor.fetchall()

    cursor.close()

    return render_template(
        "analytics.html",
        total_requests=total_requests,
        allowed=allowed,
        blocked=blocked,
        avg_risk_score=avg_risk_score,
        allowed_percentage=allowed_percentage,
        blocked_percentage=blocked_percentage,
        recent_activity=recent_activity
    )


@app.route("/access-request", methods=["GET", "POST"])
def access_request():
    if request.method == "GET":
        return render_template("access-request.html")

    username = request.form.get("username")
    resource = request.form.get("resource")
    action = request.form.get("action")

    policies = get_policies()

    cursor = db.cursor()

    cursor.execute("""
        SELECT id, role, mfa_enabled, device_trusted
        FROM users
        WHERE username = %s
    """, (username,))

    user = cursor.fetchone()

    if not user:
        cursor.close()
        return "User not found"

    user_id = user[0]
    role = user[1]
    mfa_enabled = user[2]
    device_trusted = user[3]

    risk_score = 0
    reasons = []

    mfa_policy = policies.get(
        "Multi-Factor Authentication",
        True
    )

    risk_policy = policies.get(
        "Risk-Based Access Control",
        True
    )

    high_risk_policy = policies.get(
        "High-Risk Access Blocking",
        True
    )

    continuous_policy = policies.get(
        "Continuous Verification",
        True
    )

    if not risk_policy:
        risk_score = 0
        decision = "ALLOW"
        reason = "Risk-Based Access Control is disabled"

    else:
        if mfa_policy and not mfa_enabled:
            risk_score += 50
            reasons.append("MFA verification required")

        if continuous_policy and not device_trusted:
            risk_score += 30
            reasons.append("Untrusted device")

        if role == "Guest":
            risk_score += 20
            reasons.append("Guest role")

        if action == "DELETE":
            risk_score += 25
            reasons.append("Sensitive DELETE action")

        if high_risk_policy and risk_score >= 50:
            decision = "BLOCK"
            reason = (
                " · ".join(reasons)
                if reasons
                else "Risk score too high"
            )

        elif not high_risk_policy:
            decision = "ALLOW"
            reason = (
                "Risk-based evaluation enabled, "
                "but high-risk blocking is disabled"
            )

        else:
            decision = "ALLOW"

            if risk_score == 0:
                reason = (
                    "Identity verified "
                    "and request is low risk"
                )
            else:
                reason = "Low risk access request"

    cursor.execute("""
        INSERT INTO access_requests
        (
            user_id,
            resource,
            action,
            risk_score,
            decision,
            reason
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        user_id,
        resource,
        action,
        risk_score,
        decision,
        reason
    ))

    db.commit()

    if decision == "BLOCK":
        severity = "CRITICAL" if risk_score >= 100 else "WARNING"

        message = (
            f"Access blocked for {username}: "
            f"{resource} / {action}. "
            f"Risk score {risk_score}. "
            f"{reason}"
        )

        cursor.execute("""
            INSERT INTO alerts
            (
                alert_type,
                message,
                severity
            )
            VALUES (%s, %s, %s)
        """, (
            "HIGH-RISK ACCESS",
            message,
            severity
        ))

        db.commit()

    cursor.close()

    return render_template(
        "access-result.html",
        decision=decision,
        risk_score=risk_score,
        reason=reason
    )


@app.route("/profile")
def profile():
    cursor = db.cursor()

    cursor.execute("""
        SELECT
            username,
            role,
            mfa_enabled,
            device_trusted
        FROM users
        WHERE username = 'admin'
        LIMIT 1
    """)

    user = cursor.fetchone()
    cursor.close()

    if not user:
        return "Admin user not found"

    return render_template(
        "profile.html",
        username=user[0],
        role=user[1],
        mfa_enabled=bool(user[2]),
        device_trusted=bool(user[3])
    )


if __name__ == "__main__":
    app.run(debug=True)