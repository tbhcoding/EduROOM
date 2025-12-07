import flet as ft
from views.login_view import show_login

# Connect to WebSocket server on app start
try:
    from utils.websocket_client import realtime
    realtime.connect()
    print("✅ WebSocket client connecting...")
except Exception as e:
    print(f"⚠️ WebSocket not available: {e}")

def main(page: ft.Page):
    page.title = "Classroom Reservation System"
    try:
        page.window.width = 1920
        page.window.height = 1080
    except Exception:
        pass

    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    page.fonts = {
    "Roboto": "assets/fonts/Roboto-Regular.ttf",
    "Roboto-Medium": "assets/fonts/Roboto-Medium.ttf",
    "Roboto-Bold": "assets/fonts/Montserrat-Bold.ttf",
    }
    page.theme = ft.Theme(font_family="Roboto")

    # Start with login page
    show_login(page)

    # # Skip login for now - go directly to dashboard
    # from views.dashboard_view import show_dashboard
    # show_dashboard(page, user_id=1, role="admin", name="Admin User")

    # #Skip login for now - go directly to dashboard
    # from views.dashboard_view import show_dashboard
    # show_dashboard(page, user_id=2, role="faculty", name="Prof. John Smith")

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")