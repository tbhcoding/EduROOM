import flet as ft
from views.login_view import show_login

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
    "Roboto-Bold": "assets/fonts/Roboto-Bold.ttf",
    }
    page.theme = ft.Theme(font_family="Roboto")

    # Start with login page
    show_login(page)

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")