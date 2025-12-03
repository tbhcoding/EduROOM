import flet as ft
from utils.config import ICONS, COLORS
from data.storage import authenticate_user
from views.dashboard_view import show_dashboard

def show_login(page):
    """Display the login page matching the wireframe design"""
    
    # Text fields matching wireframe
    email_field = ft.TextField(
        label="CSPC Email",
        hint_text="yourname@my.cspc.edu.ph",
        width=460,
        height=60,
        border_radius=10,
        text_size=14
    )
    
    id_number_field = ft.TextField(
        label="ID Number",
        hint_text="Enter your ID number",
        width=460,
        height=60,
        border_radius=10,
        text_size=14
    )
    
    password_field = ft.TextField(
        label="Password",
        hint_text="Enter your password",
        password=True,
        can_reveal_password=True,
        width=460,
        height=60,
        border_radius=10,
        text_size=14
    )
    
    error_text = ft.Text("", color="red", size=12)
    
    # Helper text (remove this when deploying)
    helper_text = ft.Text(
    "Test accounts (Email | ID Number | Password):\n"
    "• admin@cspc.edu.ph | 00000000 | admin123\n"
    "• profsmith@my.cspc.edu.ph | 20231001 | faculty123\n"
    "• johndoe@my.cspc.edu.ph | 25123456 | student123",
    size=10,
    color=COLORS.GREY if hasattr(COLORS, "GREY") else "grey",
    text_align=ft.TextAlign.CENTER,
    italic=True
)

    def login_click(e):
        id_number = id_number_field.value.strip()
        password = password_field.value
        
        if not id_number or not password:
            error_text.value = "Please fill in all required fields"
            page.update()
            return
        
        # Authenticate using ID number
        username, user_data = authenticate_user(id_number, password)
        
        if user_data:
            # Login successful
            show_dashboard(page, username, user_data["role"], user_data["name"])
        else:
            error_text.value = "Invalid ID number or password"
            page.update()

    # Logo placeholder
    logo = ft.Container(
        content=ft.Column([
            ft.Icon(ICONS.SCHOOL, size=80, color="#004B87"),
            ft.Text(
                "EduROOM",
                size=48,
                weight=ft.FontWeight.BOLD,
                spans=[
                    ft.TextSpan("Edu", style=ft.TextStyle(color="#7BC043")),
                    ft.TextSpan("ROOM", style=ft.TextStyle(color="#00A0DF"))
                ]
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
    )
    
    page.controls.clear()
    page.add(
        ft.Container(
            content=ft.Column([
                logo,
                ft.Text(
                    "Classroom Reservation System",
                    size=20,
                    weight=ft.FontWeight.W_500,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=30),
                email_field,
                id_number_field,
                password_field,
                error_text,
                ft.Container(height=10),
                ft.ElevatedButton(
                    "Login",
                    width=460,
                    height=50,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        bgcolor="#5A5A5A",
                        color="white"
                    ),
                    on_click=login_click
                ),
                ft.Container(height=10),
                helper_text
            ], 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5),  # THIS IS THE KEY - SMALL SPACING!
            padding=40,
            expand=True,
            alignment=ft.alignment.center
        )
    )
    page.update()