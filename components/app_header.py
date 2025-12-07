import flet as ft
from data.models import NotificationModel

def create_app_header(page, user_id, role, name, current_page="classrooms"):
    """Create the application header with navigation, notifications, and user drawer"""
    
    # Get photo from session or use default
    user_photo = page.session.get("user_photo") or "assets/images/default-user.png"
    
    # ==================== DRAWER ====================
    def logout_click(e):
        from views.login_view import show_login
        page.close(drawer)
        page.session.clear()
        show_login(page)

    def toggle_theme(e):
        page.theme_mode = (
            ft.ThemeMode.DARK 
            if page.theme_mode == ft.ThemeMode.LIGHT 
            else ft.ThemeMode.LIGHT
        )
        page.update()
    
    # Create the switch once
    theme_switch = ft.Switch(
        label="Dark Mode",
        value=page.theme_mode == ft.ThemeMode.DARK,
        on_change=toggle_theme
    )
    
    def open_profile(e):
        from views.profile_view import show_profile
        page.close(drawer)
        show_profile(page, user_id, role, name)
    
    drawer = ft.NavigationDrawer(
        position=ft.NavigationDrawerPosition.END,
        controls=[
            ft.Container(
                content=ft.Row([
                    ft.Image(
                        src=user_photo,
                        width=40,
                        height=40,
                        fit=ft.ImageFit.COVER,
                        border_radius=20  # circular
                    ),
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
                leading=ft.Icon(ft.Icons.DARK_MODE),
                title=ft.Text("Dark Mode"),
                on_click=lambda e: toggle_theme(e)
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.LOGOUT),
                title=ft.Text("Logout"),
                on_click=logout_click
            ),
            ft.Container(height=20),
        ],
    )
    
    # ==================== NOTIFICATIONS ====================
    def go_to_reservations(notif_id=None):
        """Navigate to reservations page and mark notification as read"""
        if notif_id:
            NotificationModel.mark_as_read(notif_id)
        
        if role == "faculty":
            from views.my_reservations_view import show_my_reservations
            show_my_reservations(page, user_id, role, name)
        elif role == "admin":
            from views.admin_view import show_admin_panel
            show_admin_panel(page, user_id, role, name)
    
    def create_notification_items():
        """Create notification menu items"""
        notifications = NotificationModel.get_user_notifications(user_id, limit=5)
        unread_count = NotificationModel.get_unread_count(user_id)
        
        menu_items = []
        
        # Header with unread count
        menu_items.append(
            ft.PopupMenuItem(
                content=ft.Container(
                    content=ft.Row([
                        ft.Text("Notifications", size=16, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=ft.Text(str(unread_count), size=12, color="white", weight=ft.FontWeight.BOLD),
                            bgcolor="#F44336",
                            border_radius=10,
                            padding=ft.padding.symmetric(horizontal=8, vertical=2),
                            visible=unread_count > 0,
                        )
                    ], spacing=10),
                    padding=ft.padding.only(left=10, top=5, bottom=5)
                ),
                disabled=True,
            )
        )
        
        menu_items.append(ft.Divider(height=1))
        
        if not notifications:
            menu_items.append(
                ft.PopupMenuItem(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.NOTIFICATIONS_NONE, size=40, color="grey"),
                            ft.Text("No notifications", color="grey", size=14)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                        padding=20,
                        width=320,
                    ),
                    disabled=True,
                )
            )
        else:
            for notif in notifications:
                # Determine icon and color based on notification type
                if "approved" in notif['message'].lower():
                    icon = ft.Icons.CHECK_CIRCLE
                    icon_color = "#4CAF50"
                elif "rejected" in notif['message'].lower():
                    icon = ft.Icons.CANCEL
                    icon_color = "#F44336"
                else:  # New reservation
                    icon = ft.Icons.EVENT_NOTE
                    icon_color = "#2196F3"
                
                # Format timestamp
                time_str = notif['created_at'].strftime('%b %d, %H:%M') if hasattr(notif['created_at'], 'strftime') else str(notif['created_at'])
                
                notif_content = ft.Container(
                    content=ft.Row([
                        ft.Icon(icon, size=20, color=icon_color),
                        ft.Column([
                            ft.Text(
                                notif['message'], 
                                size=13, 
                                weight=ft.FontWeight.BOLD if not notif['is_read'] else ft.FontWeight.NORMAL
                            ),
                            ft.Text(time_str, size=11, color="grey")
                        ], spacing=2, expand=True)
                    ], spacing=10),
                    padding=ft.padding.symmetric(horizontal=10, vertical=8),
                    bgcolor=ft.Colors.BLUE_50 if not notif['is_read'] else None,
                    width=320,
                    border_radius=5,
                )
                
                menu_items.append(
                    ft.PopupMenuItem(
                        content=notif_content,
                        on_click=lambda e, nid=notif['id']: go_to_reservations(nid)
                    )
                )
        
        # Divider and View All button
        menu_items.append(ft.Divider(height=1))
        menu_items.append(
            ft.PopupMenuItem(
                content=ft.Container(
                    content=ft.Row([
                        ft.Text("View All", size=14, weight=ft.FontWeight.BOLD, color="#2196F3"),
                        ft.Icon(ft.Icons.ARROW_FORWARD, size=18, color="#2196F3")
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
                    padding=5,
                ),
                on_click=lambda e: go_to_reservations()
            )
        )
        
        return menu_items
    
    # Notification badge - simple red dot
    notif_badge = ft.Container(
        width=10,
        height=10,
        bgcolor="#F44336",
        border_radius=5,
        visible=False,
        top=2,
        right=2,
    )
    
    # Update badge visibility
    unread_count = NotificationModel.get_unread_count(user_id)
    notif_badge.visible = unread_count > 0
    
    # Create notification button with badge - wrapped in container with padding for badge space
    notif_button = ft.PopupMenuButton(
        content=ft.Container(
            content=ft.Stack([
                ft.Icon(ft.Icons.NOTIFICATIONS, size=24, color="#DEC56B"),
                notif_badge
            ]),
            padding=ft.padding.only(top=5, right=5),  # Add padding so badge isn't cut off
        ),
        items=create_notification_items(),
        tooltip="Notifications",
        menu_position=ft.PopupMenuPosition.UNDER,  # Position menu below the button
    )
    
    # ==================== HEADER ====================
    logo = ft.Image(
        src="../assets/images/EduROOM-logo.png", 
        width=160,
        fit=ft.ImageFit.CONTAIN
    )

    def go_classrooms(e):
        from views.dashboard_view import show_dashboard
        show_dashboard(page, user_id, role, name)

    def go_reservations_nav(e):
        if role == "faculty":
            from views.my_reservations_view import show_my_reservations
            show_my_reservations(page, user_id, role, name)
        elif role == "admin":
            from views.admin_view import show_admin_panel
            show_admin_panel(page, user_id, role, name)

    def go_analytics(e):
        if role == "admin":
            from views.analytics_view import show_analytics_dashboard
            show_analytics_dashboard(page, user_id, role, name)

    def go_users(e):
        if role == "admin":
            from views.admin_users_view import show_admin_users
            show_admin_users(page, user_id, role, name)

    reservations_enabled = role in ("faculty", "admin")
    analytics_enabled = role == "admin"
    users_enabled = role == "admin"

    active_style = ft.ButtonStyle(
        color="#F5C518",
        text_style=ft.TextStyle(size=16, decoration=ft.TextDecoration.UNDERLINE),
    )

    inactive_style = ft.ButtonStyle(
        color="#FFFFFF",
    )

    navbar_block = ft.Row(
        [
            ft.TextButton(
                "Classrooms", 
                on_click=go_classrooms,
                style=active_style if current_page == "classrooms" else inactive_style,
            ),
            ft.TextButton(
                "Reservations", 
                on_click=go_reservations_nav, 
                disabled=not reservations_enabled,
                style=active_style if current_page == "reservations" else inactive_style
            ),
            ft.TextButton(
                "Users", 
                on_click=go_users, 
                disabled=not users_enabled,
                style=active_style if current_page == "users" else inactive_style
            ),
            ft.TextButton(
                "Analytics", 
                on_click=go_analytics, 
                disabled=not analytics_enabled,
                style=active_style if current_page == "analytics" else inactive_style
            )
        ],
        expand=True,
        alignment=ft.MainAxisAlignment.SPACE_AROUND,
    )

    settings_btn = ft.IconButton(
        icon=ft.Icons.SETTINGS, 
        icon_color="#DEC56B",
        tooltip="Settings", 
        on_click=lambda e: page.open(drawer)
    )

    header_row = ft.Row(
        [logo, navbar_block, notif_button, settings_btn],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )

    header_container = ft.Container(
        content=header_row,
        padding=ft.padding.symmetric(horizontal=20, vertical=15),
        bgcolor="#1E3A8A",
        border=ft.border.only(bottom=ft.BorderSide(2, ft.Colors.OUTLINE_VARIANT))
    )
    
    # ==================== WELCOME BANNER ====================
    role_color = "#ffffff"
    
    welcome_banner = ft.Container(
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
    
    # ==================== COMBINE ====================
    header_column = ft.Column(
        [header_container, welcome_banner],
        spacing=0
    )
    
    return header_column, drawer