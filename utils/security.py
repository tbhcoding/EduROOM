from datetime import datetime, timedelta
import secrets

# How long a session can be idle before auto-logout
SESSION_TIMEOUT_MINUTES = 2


def _now():
    """Return current time as datetime."""
    return datetime.now()


def touch_session(page):
    """
    Update last_activity in the session.
    Call this on each significant user action.
    """
    page.session.set("last_activity", _now().isoformat())


def is_session_expired(page):
    """
    Check if the current session has been idle longer than SESSION_TIMEOUT_MINUTES.
    Returns True if expired, False otherwise.
    """
    last = page.session.get("last_activity")
    if not last:
        return False  # no record yet = treat as active

    try:
        last_dt = datetime.fromisoformat(last)
    except Exception:
        return False

    return _now() - last_dt > timedelta(minutes=SESSION_TIMEOUT_MINUTES)


def ensure_authenticated(page):
    """
    Guard for protected views.

    - If no user_id in session:
        -> clear session, go to login (silent, no message).
    - If session expired due to inactivity:
        -> clear session, set a friendly notice, go to login.
    - If OK:
        -> refresh last_activity and return True.
    """
    from views.login_view import show_login  # local import to avoid circular refs

    user_id = page.session.get("user_id")

    # Case 1: No user_id at all → not logged in
    if not user_id:
        page.session.clear()
        show_login(page)
        return False

    # Case 2: Session exists but is expired
    if is_session_expired(page):
        # Clear old session but immediately set a notice for the login screen
        page.session.clear()
        page.session.set(
            "login_notice",
            "Your session has expired due to inactivity. Please log in again."
        )
        show_login(page)
        return False

    # Case 3: Session valid → refresh last activity
    touch_session(page)
    return True


# ========== CSRF-LIKE PROTECTION (for destructive actions) ==========

def get_csrf_token(page):
    """
    Get or create a per-session CSRF token.
    """
    token = page.session.get("action_token")
    if not token:
        token = secrets.token_urlsafe(32)
        page.session.set("action_token", token)
    return token


def validate_csrf_token(page, token_from_ui):
    """
    Validate that the token passed from the UI matches the session token.
    """
    session_token = page.session.get("action_token")
    return bool(session_token and token_from_ui and token_from_ui == session_token)
