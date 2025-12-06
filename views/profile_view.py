import flet as ft
from data.models import UserModel

def show_profile(page, user_id, role, name):
    """Display user profile with edit capabilities"""
    
    # Get user data from database
    try:
        user_data = UserModel.get_user_by_id(user_id)
        if not user_data:
            user_data = {
                "name": name,
                "email": "",
                "role": role,
            }
    except Exception:
        user_data = {
            "name": name,
            "email": "",
            "role": role,
        }
    
    # Password change fields
    current_password = ft.TextField(
        label="Current Password",
        password=True,
        can_reveal_password=True,
        width=400,
    )
    
    new_password = ft.TextField(
        label="New Password",
        password=True,
        can_reveal_password=True,
        width=400,
    )
    
    confirm_password = ft.TextField(
        label="Confirm New Password",
        password=True,
        can_reveal_password=True,
        width=400,
    )
    
    # Status messages for modal
    modal_status_text = ft.Text("", size=14)
    
    def go_back(e):
        from views.dashboard_view import show_dashboard
        show_dashboard(page, user_id, role, name)
    
    def close_password_modal(e):
        password_modal.open = False
        # Clear fields and status
        current_password.value = ""
        new_password.value = ""
        confirm_password.value = ""
        modal_status_text.value = ""
        page.update()
    
    def change_password(e):
        """Change user password"""
        try:
            success, message = UserModel.change_password(user_id, current_password.value, new_password.value)
            
            if success:
                modal_status_text.value = f"✓ {message}"
                modal_status_text.color = ft.Colors.GREEN
                page.update()
                
                # Close modal after 1.5 seconds
                import time
                time.sleep(1.5)
                close_password_modal(e)
            else:
                modal_status_text.value = f"✗ {message}"
                modal_status_text.color = ft.Colors.RED
                page.update()
                
        except Exception as ex:
            modal_status_text.value = f"✗ Error changing password: {str(ex)}"
            modal_status_text.color = ft.Colors.RED
            page.update()

    # Password change modal
    password_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Change Password"),
        content=ft.Container(
            content=ft.Column(
                [
                    modal_status_text,
                    current_password,
                    new_password,
                    confirm_password,
                ],
                spacing=15,
                tight=True,
            ),
            width=450,
        ),
        actions=[
            ft.TextButton("Cancel", on_click=close_password_modal),
            ft.ElevatedButton("Update Password", on_click=change_password),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    def open_password_modal(e):
        page.open(password_modal)
    
    # Header
    header = ft.Container(
        content=ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    tooltip="Back to Dashboard",
                    on_click=go_back
                ),
                ft.Text("Account Profile", size=24, weight=ft.FontWeight.BOLD),
            ],
            spacing=10
        ),
        padding=20,
        bgcolor=ft.Colors.GREY_200,
    )
    
    # Profile info section
    profile_section = ft.Container(
        content=ft.Column(
            [
                ft.Row([
                    ft.Icon(ft.Icons.PERSON, size=80, color=ft.Colors.BLUE),
                    ft.Column([
                        ft.Text(name, size=24, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=ft.Text(role.upper(), size=12, color=ft.Colors.WHITE),
                            bgcolor=ft.Colors.BLUE,
                            padding=ft.padding.symmetric(horizontal=12, vertical=6),
                            border_radius=5
                        )
                    ], spacing=5)
                ], spacing=20),
                ft.Divider(height=20, thickness=2),
                ft.Text("Personal Information", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                # Display fields without input boxes
                ft.Row([
                    ft.Text("Name:", size=14, weight=ft.FontWeight.BOLD, width=120),
                    ft.Text(user_data.get("name", name), size=14),
                ]),
                ft.Row([
                    ft.Text("CSPC Email:", size=14, weight=ft.FontWeight.BOLD, width=120),
                    ft.Text(user_data.get("email", "Not set"), size=14),
                ]),
                ft.Row([
                    ft.Text("Role:", size=14, weight=ft.FontWeight.BOLD, width=120),
                    ft.Text(role.upper(), size=14),
                ]),
                ft.Container(height=20),
                ft.Divider(height=1, thickness=1),
                ft.Container(height=10),
                ft.ElevatedButton(
                    "Change Password",
                    icon=ft.Icons.LOCK,
                    on_click=open_password_modal,
                    width=200
                ),
            ],
            spacing=15
        ),
        padding=30,
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
        )
    )
    
    # Build page
    page.controls.clear()
    page.add(
        ft.Column([
            header,
            ft.Container(
                content=ft.Column(
                    [
                        profile_section,
                    ],
                    spacing=20,
                    scroll=ft.ScrollMode.AUTO
                ),
                padding=30,
                expand=True
            )
        ], spacing=0, expand=True)
    )
    page.update()