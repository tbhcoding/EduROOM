import flet as ft
from utils.config import ICONS, COLORS
from data.storage import CLASSROOMS

def show_dashboard(page, username, role, name):
    """Display the main dashboard with classroom list"""
    
    def logout_click(e):
        from views.login_view import show_login
        show_login(page)
    
    def reserve_classroom(classroom_id):
        from views.reservation_view import show_reservation_form
        show_reservation_form(page, username, role, name, classroom_id)
    
    def view_my_reservations(e):
        from views.my_reservations_view import show_my_reservations
        show_my_reservations(page, username, role, name)
    
    def view_admin_panel(e):
        from views.admin_view import show_admin_panel
        show_admin_panel(page, username, role, name)
    
    # Create classroom cards
    classroom_cards = []
    for room in CLASSROOMS:
        status_color = COLORS.GREEN if room["status"] == "Available" else "orange"
        
        # Determine button behavior based on role
        if role == "student":
            # Students can only view - no reserve button
            action_button = ft.Text("View Only", size=12, italic=True, color=COLORS.GREY if hasattr(COLORS, "GREY") else "grey")
        elif role == "faculty":
            # Faculty can reserve
            action_button = ft.ElevatedButton(
                "Reserve",
                icon=ICONS.BOOK_ONLINE,
                on_click=lambda e, rid=room["id"]: reserve_classroom(rid),
                disabled=(room["status"] != "Available")
            )
        else:  # admin
            # Admin can see status but reserves through approval system
            action_button = ft.Text("Manage via Admin Panel", size=11, italic=True)
        
        card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.ListTile(
                        leading=ft.Icon(ICONS.MEETING_ROOM),
                        title=ft.Text(room["name"], weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text(f"{room['building']} • Capacity: {room['capacity']}"),
                    ),
                    ft.Container(
                        content=ft.Row([
                            ft.Text(
                                room["status"], 
                                size=12, 
                                weight=ft.FontWeight.BOLD, 
                                color=status_color
                            ),
                            action_button
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=ft.padding.only(left=15, right=15, bottom=10)
                    )
                ], spacing=0),
                padding=10
            )
        )
        classroom_cards.append(card)

    # Role badge color
    role_colors = {
        "student": "blue",
        "faculty": "green", 
        "admin": "purple"
    }
    role_color = role_colors.get(role, "grey")

    page.controls.clear()
    page.add(
        ft.Column([
            # Header with user info
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Column([
                            ft.Text(f"Welcome, {name}!", size=24, weight=ft.FontWeight.BOLD),
                            ft.Container(
                                content=ft.Text(role.upper(), size=11, weight=ft.FontWeight.BOLD, color="white"),
                                bgcolor=role_color,
                                padding=ft.padding.symmetric(horizontal=10, vertical=3),
                                border_radius=5
                            )
                        ], spacing=5),
                        ft.IconButton(
                            icon=ICONS.LOGOUT, 
                            tooltip="Logout", 
                            on_click=logout_click
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    
                    # Action buttons based on role
                    ft.Container(height=10),
                    ft.Row([
                        ft.ElevatedButton(
                            "My Reservations",
                            icon=ICONS.LIST,
                            on_click=view_my_reservations
                        ) if role == "faculty" else ft.Container(),
                        ft.ElevatedButton(
                            "Admin Panel",
                            icon=ICONS.ADMIN_PANEL_SETTINGS,
                            on_click=view_admin_panel
                        ) if role == "admin" else ft.Container(),
                    ], spacing=10)
                ]),
                padding=20,
                width=850
            ),
            ft.Divider(),
            
            # Classroom list
            ft.Text("Available Classrooms", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            ft.Column(
                classroom_cards, 
                spacing=10, 
                scroll=ft.ScrollMode.AUTO, 
                height=400
            ),
            
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO)
    )
    page.update()