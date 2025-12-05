import flet as ft
from utils.config import ICONS, COLORS
from data.models import ClassroomModel
from views.schedule_view import show_classroom_schedule

def show_dashboard(page, user_id, role, name):
    """Display main dashboard based on roles"""

    def logout_click(e):
        from views.login_view import show_login
        close_drawer(e)
        page.session.clear()
        show_login(page)

    def open_drawer(e):
        page.open(drawer)
    
    def close_drawer(e):
        page.close(drawer)
    
    def toggle_theme(e):
        # Toggle between light and dark theme
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        page.update()
    
    def open_profile(e):
        close_drawer(e)
        # Add your profile view function here
        page.snack_bar = ft.SnackBar(ft.Text("Profile feature coming soon!"))
        page.snack_bar.open = True
        page.update()
    
    # Create settings drawer
    drawer = ft.NavigationDrawer(
        position=ft.NavigationDrawerPosition.END,
        controls=[
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.PERSON, size=40),
                    ft.Column([
                        ft.Text(name, size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(role.upper(), size=12, color=ft.Colors.GREY_600)
                    ], spacing=2)
                ], spacing=15),
                padding=20,
            ),
            ft.Divider(thickness=2),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.PERSON),
                title=ft.Text("Profile"),
                on_click=open_profile
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.PALETTE),
                title=ft.Text("Toggle Theme"),
                on_click=toggle_theme
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.LOGOUT),
                title=ft.Text("Logout"),
                on_click=logout_click
            ),
        ft.Container(height=20),
        ],
    )

    def open_reservation_form(classroom_id):
        from views.reservation_view import show_reservation_form
        show_reservation_form(page, user_id, role, name, classroom_id)

    def open_my_reservations(e):
        from views.my_reservations_view import show_my_reservations
        show_my_reservations(page, user_id, role, name)

    def open_admin_panel(e):
        from views.admin_view import show_admin_panel
        show_admin_panel(page, user_id, role, name)

    def open_analytics(e):
        from views.analytics_view import show_analytics_dashboard
        show_analytics_dashboard(page, user_id, role, name)

    def make_header_block(current_page="classrooms"):
        logo = ft.Image(
            src="../assets/images/EduROOM-logo.png", 
            width=160,
            fit=ft.ImageFit.CONTAIN
        )

        # nav button handlers
        def go_classrooms(e):
            show_dashboard(page, user_id, role, name)

        def go_reservations(e):
            if role == "faculty":
                open_my_reservations(e)
            elif role == "admin":
                open_admin_panel(e)

        def go_analytics(e):
            if role == "admin":
                open_analytics(e)

        # enable/disable nav items by role
        reservations_enabled = role in ("faculty", "admin")
        analytics_enabled = role == "admin"

        active_style = ft.ButtonStyle(
            color=ft.Colors.BLUE,
            bgcolor=ft.Colors.BLUE_100,
        )

        navbar_block = ft.Row(
            [
                ft.TextButton(
                    "Classrooms", 
                    on_click=go_classrooms,
                    style=active_style if current_page == "classrooms" else None
                ),
                ft.TextButton(
                    "Reservations", 
                    on_click=go_reservations, 
                    disabled=not reservations_enabled,
                    style=active_style if current_page == "reservations" else None
                ),
                ft.TextButton(
                    "Analytics", 
                    on_click=go_analytics, 
                    disabled=not analytics_enabled,
                    style=active_style if current_page == "analytics" else None
                )
            ],
            expand=True,
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
        )

        settings = ft.IconButton(icon=ft.Icons.SETTINGS, tooltip="Settings", on_click=open_drawer)

        header_row = ft.Row(
            [logo, navbar_block, settings],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        return ft.Container(
            content=header_row,
            padding=ft.padding.symmetric(horizontal=20, vertical=15),
            bgcolor=ft.Colors.GREY_200,
            border=ft.border.only(bottom=ft.BorderSide(2, ft.Colors.OUTLINE_VARIANT))
        )
    
    # Welcome block
    role_color = "#ffd141"

    welcome_block = ft.Container(
        content=ft.Row(
            [
                ft.Text(f"Welcome, {name}!", size=15),
                ft.Container(
                    content=ft.Text(role.upper(), size=11),
                    bgcolor=role_color,
                    padding=ft.padding.symmetric(horizontal=10, vertical=4),
                    border_radius=5
                )
            ],
            spacing=30,
            alignment=ft.MainAxisAlignment.START,
        ),
        padding=ft.padding.symmetric(vertical=10, horizontal=30),
        bgcolor=ft.Colors.GREY_400,
    )

    # Get classrooms from database
    try:
        classrooms = ClassroomModel.get_all_classrooms() or []
    except Exception:
        classrooms = []

    # Search state
    search_query = ft.Ref[ft.TextField]()
    classroom_list_ref = ft.Ref[ft.Column]()

    def create_classroom_card(room):
        """Helper function to create a classroom card"""
        status_color = COLORS.GREEN if room.get("status") == "Available" else "orange"

        # Classroom image (use default if none)
        image_src = room.get("image_url") or "../assets/images/classroom-default.png"

        def view_schedule_click(e):
            show_classroom_schedule(page, room["id"], room.get("room_name", "Unnamed Room"))

        reserve_enabled = (role == "faculty") and (room.get("status") == "Available")

        reserve_btn = ft.ElevatedButton(
            "Reserve",
            icon=ICONS.BOOK_ONLINE,
            on_click=lambda e, rid=room["id"]: open_reservation_form(rid),
            disabled=not reserve_enabled,
            height=35,
            expand=True
        )

        # For admin + student → disabled reserve button instead of text
        if role in ("admin", "student"):
            reserve_btn = ft.ElevatedButton(
                "Reserve",
                icon=ICONS.BOOK_ONLINE,
                disabled=True,
                height=35,
                expand=True
            )

        schedule_btn = ft.OutlinedButton(
            "View Schedule",
            icon=ft.Icons.CALENDAR_TODAY,
            on_click=view_schedule_click,
            height=35,
            expand=True
        )

        return ft.Card(
            width=320,  # perfect for 3-column grid
            elevation=3,
            content=ft.Container(
                padding=0,
                content=ft.Column(
                    [
                        # IMAGE
                        ft.Container(
                            content=ft.Image(
                                src=image_src,
                                fit=ft.ImageFit.COVER,
                                width=None,
                                height=200,
                            ),
                            border_radius=ft.border_radius.only(
                                top_left=8, top_right=8
                            ),
                            clip_behavior=ft.ClipBehavior.ANTI_ALIAS
                        ),

                        # TEXT BLOCK
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=12, vertical=8),
                            content=ft.Column(
                                [
                                    ft.Text(
                                        room.get("room_name", "Unnamed Room"),
                                        weight=ft.FontWeight.BOLD,
                                        size=14
                                    ),
                                    ft.Text(
                                        f"{room.get('building','')} • Capacity: {room.get('capacity','-')}",
                                        size=11,
                                        color=ft.Colors.GREY_600
                                    ),
                                    ft.Text(
                                        room.get("status", "Unknown"),
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                        color=status_color
                                    ),
                                ],
                                spacing=3
                            )
                        ),

                        # BUTTONS
                        ft.Container(
                            padding=ft.padding.all(12),
                            content=ft.Row(
                                [schedule_btn, reserve_btn],
                                spacing=10,
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        )
                    ],
                    tight=True,
                    spacing=0
                )
            )
        )

    def matches_search(text, query):
        """Check if query characters appear consecutively in text"""
        if not query:
            return True
        
        text = text.lower()
        query = query.lower()
        
        # Simple substring match for consecutive characters
        return query in text
    
    def filter_classrooms(e):
        """Filter classrooms based on search query"""
        query = search_query.current.value.strip()
        filtered_cards = []
        
        for room in classrooms:
            room_name = room.get("room_name", "")
            building = room.get("building", "")
            capacity = str(room.get("capacity", ""))
            status = room.get("status", "")
            
            # Search across multiple fields
            searchable_text = f"{room_name} {building} {capacity} {status}"
            
            # If query is empty or matches any field
            if matches_search(searchable_text, query):
                filtered_cards.append(create_classroom_card(room))
        
        # Show message if no results found
        if not filtered_cards and query:
            classroom_list_ref.current.controls = [
                ft.Container(
                    content=ft.Text(
                        "No classrooms found matching your search.",
                        size=16,
                        color=ft.Colors.GREY_600,
                        italic=True
                    ),
                    padding=20,
                    alignment=ft.alignment.center
                )
            ]
        else:
            # Organize filtered cards into grid rows
            classroom_list_ref.current.controls = create_grid_rows(filtered_cards)
        
        page.update()

    # Create initial classroom cards in grid layout
    def create_grid_rows(cards):
        """Organize cards into rows of 3"""
        rows = []
        for i in range(0, len(cards), 3):
            row_cards = cards[i:i+3]
            rows.append(
                ft.Row(
                    controls=row_cards,
                    spacing=20,
                    alignment=ft.MainAxisAlignment.CENTER,
                    wrap=False
                )
            )
        return rows

    classroom_cards = [create_classroom_card(room) for room in classrooms]
    grid_rows = create_grid_rows(classroom_cards)

    # Build page layout
    page.controls.clear()
    page.add(
        ft.Column([
            make_header_block(),
            welcome_block,
            ft.Container(
                content=ft.Text("Available Classrooms", size=32, font_family="Montserrat Bold", weight=ft.FontWeight.BOLD),
                padding=ft.padding.only(left=30, top=20), 
                alignment=ft.alignment.center
            ),
            ft.Container(height=10),
            # Search bar
            ft.Container(
                content=ft.TextField(
                    ref=search_query,
                    hint_text="Search for Classroom",
                    prefix_icon=ft.Icons.SEARCH,
                    on_change=filter_classrooms,
                    width=600,
                    border_radius=10,
                ),
                alignment=ft.alignment.center,
                padding=ft.padding.symmetric(horizontal=30)
            ),
            ft.Container(height=10),
            # Scrollable classroom grid
            ft.Container(
                content=ft.Column(
                    ref=classroom_list_ref,
                    controls=grid_rows,
                    spacing=20,
                    scroll=ft.ScrollMode.AUTO
                ),
                padding=ft.padding.symmetric(horizontal=30),
                expand=True
            )
        ], spacing=0, expand=True)
    )
    page.update()