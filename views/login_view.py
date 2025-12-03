import flet as ft
from utils.config import ICONS, COLORS
from data.models import UserModel, ActivityLogModel
from views.dashboard_view import show_dashboard

def show_login(page):
    """Display the login page with database authentication"""
    def on_focus(tf):
        tf.border_color = "#0097b2"
        tf.update()

    def on_blur(tf):
        tf.border_color = "#cccccc"
        tf.update()

    email_field = ft.TextField(
        label="CSPC Email",
        hint_text="yourname@my.cspc.edu.ph",
        width=460,
        height=60,
        border_radius=10,
        text_size=14,
        border_color="#cccccc",
        on_focus=lambda e: on_focus(email_field),
        on_blur=lambda e: on_blur(email_field)
    )
    
    id_number_field = ft.TextField(
        label="ID Number",
        hint_text="Enter your ID number",
        width=460,
        height=60,
        border_radius=10,
        text_size=14,
        border_color="#cccccc",
        on_focus=lambda e: on_focus(id_number_field),
        on_blur=lambda e: on_blur(id_number_field)
    )
    
    password_field = ft.TextField(
        label="Password",
        hint_text="Enter your password",
        password=True,
        can_reveal_password=True,
        width=460,
        height=60,
        border_radius=10,
        text_size=14,
        border_color="#cccccc",
        on_focus=lambda e: on_focus(password_field),
        on_blur=lambda e: on_blur(password_field)
    )
    
    error_text = ft.Text("", color="red", size=12)

    def login_click(e):
        email = email_field.value.strip()
        id_number = id_number_field.value.strip()
        password = password_field.value
        
        # Validate all fields are filled
        if not email or not id_number or not password:
            error_text.value = "Please fill in all fields"
            page.update()
            return
        
        # Authenticate using database - check both email AND id_number
        user = UserModel.authenticate_with_email(email, id_number, password)
        
        if user:
            # Log the login activity
            ActivityLogModel.log_activity(user['id'], "User logged in")
            
            # Store user info in page session
            page.session.set("user_id", user['id'])
            page.session.set("user_role", user['role'])
            page.session.set("user_name", user['full_name'])
            
            # Login successful
            show_dashboard(page, user['id'], user['role'], user['full_name'])
        else:
            error_text.value = "Invalid credentials. Please check your email, ID number, and password."
            page.update()

    logo = ft.Container(
        content=ft.Column(
            [
                ft.Image(
                    src="assets/images/cspc-logo.png",
                    width=120,
                    height=120,
                    fit=ft.ImageFit.CONTAIN
                ),
                ft.Image(
                    src="assets/images/EduROOM-logo.png",
                    width=260,
                    height=80,
                    fit=ft.ImageFit.CONTAIN
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5
        )
    )
    
    LOGIN_BUTTON_STYLE = ft.ButtonStyle(
        shape=ft.RoundedRectangleBorder(radius=30),
        bgcolor="#5A5A5A", 
        color="white",
        overlay_color="#0097b2",
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
                        width=360,
                        height=50,
                        style=LOGIN_BUTTON_STYLE,
                        on_click=login_click,
                ),
            ], 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5),
            padding=40,
            alignment=ft.alignment.center,
        )
    )
    page.update()