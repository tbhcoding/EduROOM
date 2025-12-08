import flet as ft
from utils.config import ICONS, COLORS
from data.models import UserModel, ActivityLogModel
from views.dashboard_view import show_dashboard
from utils.security import touch_session, get_csrf_token


def show_login(page):
    """Display the enhanced login page with database authentication"""
    
    # State for password visibility and loading
    show_password = ft.Ref[ft.TextField]()
    login_button_ref = ft.Ref[ft.ElevatedButton]()
    error_text_ref = ft.Ref[ft.Text]()
    
    def on_focus(e, field):
        """Enhanced focus with animation"""
        field.border_color = "#3775a9"
        field.border_width = 2
        page.update()

    def on_blur(e, field):
        """Reset border on blur"""
        field.border_color = "#E5E7EB"
        field.border_width = 1
        page.update()

    # Email field with icon - responsive width
    email_field = ft.TextField(
        label="CSPC Email",
        hint_text="yourname@my.cspc.edu.ph",
        prefix_icon=ft.Icons.EMAIL_OUTLINED,
        height=65,
        border_radius=12,
        text_size=14,
        border_color="#E5E7EB",
        filled=True,
        bgcolor="#F9FAFB",
        expand=True,
        on_focus=lambda e: on_focus(e, email_field),
        on_blur=lambda e: on_blur(e, email_field)
    )
    
    # ID Number field with icon - responsive width
    id_number_field = ft.TextField(
        label="ID Number",
        hint_text="Enter your CSPC ID Number",
        prefix_icon=ft.Icons.PERSON_OUTLINE,
        height=65,
        border_radius=12,
        text_size=14,
        border_color="#E5E7EB",
        filled=True,
        bgcolor="#F9FAFB",
        expand=True,
        on_focus=lambda e: on_focus(e, id_number_field),
        on_blur=lambda e: on_blur(e, id_number_field)
    )
    
    # Password field with show/hide toggle - responsive width
    password_field = ft.TextField(
        ref=show_password,
        label="Password",
        hint_text="Enter your password",
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        password=True,
        can_reveal_password=True,
        height=65,
        border_radius=12,
        text_size=14,
        border_color="#E5E7EB",
        filled=True,
        bgcolor="#F9FAFB",
        expand=True,
        on_focus=lambda e: on_focus(e, password_field),
        on_blur=lambda e: on_blur(e, password_field)
    )
    
    # Enhanced error message - responsive width
    error_text = ft.Container(
        ref=error_text_ref,
        content=ft.Row([
            ft.Icon(ft.Icons.ERROR_OUTLINE, color="#EF4444", size=18),
            ft.Text("", color="#EF4444", size=12, weight=ft.FontWeight.W_500, expand=True)
        ], spacing=8),
        padding=12,
        bgcolor="#FEE2E2",
        border_radius=10,
        visible=False,
    )
    
    def show_error(message):
        """Display error message"""
        error_text.content.controls[1].value = message
        error_text.visible = True
        page.update()
    
    def hide_error():
        """Hide error message"""
        error_text.visible = False
        page.update()

    # --- Show notice if session expired due to inactivity ---
    login_notice = page.session.get("login_notice")
    if login_notice:
        # Reuse your existing error UI
        show_error(login_notice)
        # Clear it so it doesn't appear again next time
        page.session.set("login_notice", None)


    def login_click(e):
        hide_error()
        
        email = email_field.value.strip()
        id_number = id_number_field.value.strip()
        password = password_field.value
        
        # Validate all fields are filled
        if not email or not id_number or not password:
            show_error("Please fill in all fields")
            return

        # Check if account is deactivated
        is_active, message = UserModel.check_account_status(email, id_number)
        if not is_active:
            show_error(message)
            return
        
        page.update()
        
        # Authenticate using database (with lockout support)
        user, error_message = UserModel.authenticate_with_email(email, id_number, password)

        # If account is temporarily locked
        if error_message:
            # Reset button state
            login_button_ref.current.disabled = False
            login_button_ref.current.content.controls[1].value = "Login"
            login_button_ref.current.content.controls[0].visible = False

            show_error(error_message)

            # OPTIONAL: log lockout event
            # ActivityLogModel.log_activity(
            #     None,
            #     "Account lockout",
            #     f"Email: {email}, ID: {id_number}"
            # )

            page.update()
            return

        if user:
            # Log the login activity
            ActivityLogModel.log_activity(user['id'], "User logged in")

            # (Optional but nice) clear any stale session data
            page.session.clear()
            
            # Store user info in page session
            page.session.set("user_id", user['id'])
            page.session.set("user_role", user['role'])
            page.session.set("user_name", user['full_name'])
            page.session.set("user_photo", user.get('photo'))

            # NEW: initialize session activity + CSRF token
            touch_session(page)       # sets last_activity
            get_csrf_token(page)      # generates & stores action_token

            # Login successful - navigate to dashboard
            show_dashboard(page, user['id'], user['role'], user['full_name'])
        else:
            # Reset button state
            login_button_ref.current.disabled = False
            login_button_ref.current.content.controls[1].value = "Login"
            login_button_ref.current.content.controls[0].visible = False

            # OPTIONAL: log failed attempt
            # ActivityLogModel.log_activity(
            #     None,
            #     "Failed login",
            #     f"Email: {email}, ID: {id_number}"
            # )

            show_error("Invalid credentials. Please check your email, ID, and password.")

    # Logo section - responsive sizing
    logo = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Image(
                    src="assets/images/cspc-logo.png",
                    width=80,
                    height=80,
                    fit=ft.ImageFit.CONTAIN
                ),
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=15,
                    color=ft.Colors.with_opacity(0.1, "#3775a9"),
                    offset=ft.Offset(0, 4),
                )
            ),
            ft.Container(height=8),
            ft.Image(
                src="assets/images/EduROOM-logo.png",
                width=220,
                height=65,
                fit=ft.ImageFit.CONTAIN
            )
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0
        )
    )
    
    # login button - responsive width
    login_button = ft.ElevatedButton(
        ref=login_button_ref,
        content=ft.Row([
            ft.ProgressRing(width=20, height=20, stroke_width=2, visible=False),
            ft.Text("Login", size=16, weight=ft.FontWeight.W_600),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
        height=55,
        expand=True,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            bgcolor="#3775a9",
            color="white",
            shadow_color="#3775a9",
            elevation=3,
        ),
        on_click=login_click,
    )

    # Main card container with responsive sizing
    login_card = ft.Container(
        content=ft.Column([
            logo,
            ft.Text(
                "Classroom Reservation System",
                size=14,
                color="#6B7280",
                text_align=ft.TextAlign.CENTER
            ),
            ft.Container(height=15),
            
            # Form fields
            email_field,
            ft.Container(height=5),
            id_number_field,
            ft.Container(height=5),
            password_field,
            
            error_text,
            ft.Container(height=8),
            login_button,
        ], 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=5,
        scroll=ft.ScrollMode.AUTO),
        padding=ft.padding.symmetric(horizontal=30, vertical=35),
        bgcolor="white",
        border_radius=24,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=30,
            color=ft.Colors.with_opacity(0.1, "black"),
            offset=ft.Offset(0, 10),
        ),
        width=450,
    )
    
    # Responsive container wrapper
    responsive_card = ft.Container(
        content=login_card,
        width=450,
        alignment=ft.alignment.center,
    )
    
    # Footer
    footer = ft.Container(
        content=ft.Column([
            ft.Text(
                "© 2025 TechValks",
                size=12,
                color="#9CA3AF",
                text_align=ft.TextAlign.CENTER
            ),
        ], 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=5),
        padding=ft.padding.only(top=15)
    )

    page.controls.clear()
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    page.add(
        ft.Stack([
            ft.Container(
                image=ft.DecorationImage(
                    src="assets/images/gradient-bg.png",  
                    fit=ft.ImageFit.COVER,
                ),
                blur=10,  
                expand=True
            ),
            ft.Container(
                content=ft.Column([
                    responsive_card,
                    footer
                ], 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=0),
                alignment=ft.alignment.center,
                expand=True
            )
        ], expand=True)
    )
    page.update()