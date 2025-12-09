import flet as ft
from data.models import UserModel, ActivityLogModel
from components.app_header import create_app_header


def show_admin_users(page, user_id, role, name):
    """Display admin user management panel"""
    
    # Only admin can access this view
    if role != "admin":
        from views.dashboard_view import show_dashboard
        show_dashboard(page, user_id, role, name)
        return
    
    # Create the header and drawer
    header, drawer = create_app_header(page, user_id, role, name, current_page="users")
    
    # State variables
    current_filter = "all"  # all, admin, faculty, student, active, inactive
    search_query = ""
    
    # References for dynamic updates
    user_list_ref = ft.Ref[ft.Column]()
    search_field_ref = ft.Ref[ft.TextField]()
    filter_buttons_ref = ft.Ref[ft.Row]()
    
    def show_snackbar(message, is_error=False):
        """Show a snackbar notification"""
        page.open(
            ft.SnackBar(
                content=ft.Text(message, color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED if is_error else ft.Colors.GREEN,
                duration=3000
            )
        )
        page.update()
    
    def refresh_panel():
        """Refresh the user management panel"""
        show_admin_users(page, user_id, role, name)
    
    def back_to_dashboard(e):
        from views.dashboard_view import show_dashboard
        show_dashboard(page, user_id, role, name)
    
    def go_to_reservations(e):
        from views.admin_view import show_admin_panel
        show_admin_panel(page, user_id, role, name)
    
    # ==================== USER STATS ====================
    def create_stat_card(title, value, icon, color):
        """Create a statistics card"""
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, size=30, color=color),
                ft.Column([
                    ft.Text(str(value), size=24, weight=ft.FontWeight.BOLD),
                    ft.Text(title, size=11, color=ft.Colors.GREY_600),
                ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
            padding=15,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10,
            width=140,
            bgcolor=ft.Colors.WHITE,
        )
    
    
    # ==================== CREATE USER MODAL ====================
    new_email = ft.TextField(label="Email", hint_text="user@cspc.edu.ph", width=350)
    new_id_number = ft.TextField(label="ID Number", hint_text="e.g., 20231001", width=350)
    new_full_name = ft.TextField(label="Full Name", hint_text="e.g., John Doe", width=350)
    new_password = ft.TextField(label="Password", password=True, can_reveal_password=True, width=350)
    new_role = ft.Dropdown(
        label="Role",
        width=350,
        options=[
            ft.dropdown.Option("faculty", "Faculty"),
            ft.dropdown.Option("student", "Student"),
            ft.dropdown.Option("admin", "Admin"),
        ],
        value="faculty"
    )
    create_status_text = ft.Text("", size=13)
    
    def close_create_modal(e):
        create_user_modal.open = False
        # Clear fields
        new_email.value = ""
        new_id_number.value = ""
        new_full_name.value = ""
        new_password.value = ""
        new_role.value = "faculty"
        create_status_text.value = ""
        page.update()
    
    def handle_create_user(e):
        """Handle user creation"""
        # Validate fields
        if not all([new_email.value, new_id_number.value, new_full_name.value, new_password.value]):
            create_status_text.value = "⚠ All fields are required"
            create_status_text.color = ft.Colors.ORANGE
            page.update()
            return
        
        # Check if email already exists
        if UserModel.check_email_exists(new_email.value.strip()):
            create_status_text.value = "✗ Email already exists"
            create_status_text.color = ft.Colors.RED
            page.update()
            return
        
        # Check if ID number already exists
        if UserModel.check_id_number_exists(new_id_number.value.strip()):
            create_status_text.value = "✗ ID Number already exists"
            create_status_text.color = ft.Colors.RED
            page.update()
            return
        
        # Create user
        try:
            new_user_id = UserModel.create_user(
                email=new_email.value.strip(),
                id_number=new_id_number.value.strip(),
                password=new_password.value,
                role=new_role.value,
                full_name=new_full_name.value.strip()
            )
            
            if new_user_id:
                # Log the action
                ActivityLogModel.log_activity(
                    user_id,
                    "Created user",
                    f"Created {new_role.value} account for {new_full_name.value.strip()}"
                )
                
                create_status_text.value = "✓ User created successfully!"
                create_status_text.color = ft.Colors.GREEN
                page.update()
                
                # Close modal and refresh after brief delay
                import time
                time.sleep(1)
                close_create_modal(e)
                refresh_panel()
            else:
                create_status_text.value = "✗ Error creating user"
                create_status_text.color = ft.Colors.RED
                page.update()
                
        except Exception as ex:
            create_status_text.value = f"✗ Error: {str(ex)}"
            create_status_text.color = ft.Colors.RED
            page.update()
    
    create_user_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Create New User", weight=ft.FontWeight.BOLD),
        content=ft.Container(
            content=ft.Column([
                create_status_text,
                new_full_name,
                new_email,
                new_id_number,
                new_password,
                new_role,
            ], spacing=15, tight=True),
            width=400,
            padding=10,
        ),
        actions=[
            ft.TextButton("Cancel", on_click=close_create_modal),
            ft.ElevatedButton(
                "Create User",
                icon=ft.Icons.PERSON_ADD,
                on_click=handle_create_user,
                bgcolor="#3B82F6",
                color=ft.Colors.WHITE,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    def open_create_modal(e):
        page.open(create_user_modal)
    
    # ==================== EDIT USER MODAL ====================
    edit_user_id = ft.Text("", visible=False)  # Hidden field to store user ID
    edit_full_name = ft.TextField(label="Full Name", width=350)
    edit_email = ft.TextField(label="Email", width=350)
    edit_role = ft.Dropdown(
        label="Role",
        width=350,
        options=[
            ft.dropdown.Option("faculty", "Faculty"),
            ft.dropdown.Option("student", "Student"),
            ft.dropdown.Option("admin", "Admin"),
        ],
    )
    edit_status_text = ft.Text("", size=13)
    
    def close_edit_modal(e):
        edit_user_modal.open = False
        edit_status_text.value = ""
        page.update()
    
    def handle_edit_user(e):
        """Handle user profile update"""
        target_user_id = int(edit_user_id.value)
        
        # Update profile fields
        success, message = UserModel.update_user_profile(
            target_user_id,
            full_name=edit_full_name.value.strip() if edit_full_name.value else None,
            email=edit_email.value.strip() if edit_email.value else None
        )
        
        if not success and "No fields" not in message:
            edit_status_text.value = f"✗ {message}"
            edit_status_text.color = ft.Colors.RED
            page.update()
            return
        
        # Update role
        role_success, role_message = UserModel.update_user_role(target_user_id, edit_role.value)
        
        if role_success or success:
            ActivityLogModel.log_activity(
                user_id,
                "Updated user",
                f"Updated user ID {target_user_id}"
            )
            edit_status_text.value = "✓ User updated successfully!"
            edit_status_text.color = ft.Colors.GREEN
            page.update()
            
            import time
            time.sleep(1)
            close_edit_modal(e)
            refresh_panel()
        else:
            edit_status_text.value = f"✗ {role_message}"
            edit_status_text.color = ft.Colors.RED
            page.update()
    
    edit_user_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Edit User", weight=ft.FontWeight.BOLD),
        content=ft.Container(
            content=ft.Column([
                edit_user_id,
                edit_status_text,
                edit_full_name,
                edit_email,
                edit_role,
            ], spacing=15, tight=True),
            width=400,
            padding=10,
        ),
        actions=[
            ft.TextButton("Cancel", on_click=close_edit_modal),
            ft.ElevatedButton(
                "Save Changes",
                on_click=handle_edit_user,
                bgcolor="#3B82F6",
                color=ft.Colors.WHITE,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    def open_edit_modal(user):
        """Open edit modal with user data pre-filled"""
        edit_user_id.value = str(user['id'])
        edit_full_name.value = user['full_name']
        edit_email.value = user['email']
        edit_role.value = user['role']
        edit_status_text.value = ""
        page.open(edit_user_modal)
    
    # ==================== RESET PASSWORD MODAL ====================
    reset_user_id = ft.Text("", visible=False)
    reset_user_name = ft.Text("", size=14)
    reset_new_password = ft.TextField(
        label="New Password", 
        password=True, 
        can_reveal_password=True, 
        width=350,
        hint_text="Enter new password"
    )
    reset_status_text = ft.Text("", size=13)
    
    def close_reset_modal(e):
        reset_password_modal.open = False
        reset_new_password.value = ""
        reset_status_text.value = ""
        page.update()
    
    def handle_reset_password(e):
        """Handle admin password reset"""
        if not reset_new_password.value or len(reset_new_password.value) < 6:
            reset_status_text.value = "⚠ Password must be at least 6 characters"
            reset_status_text.color = ft.Colors.ORANGE
            page.update()
            return
        
        target_user_id = int(reset_user_id.value)
        success, message = UserModel.admin_reset_password(target_user_id, reset_new_password.value)
        
        if success:
            ActivityLogModel.log_activity(
                user_id,
                "Reset password",
                f"Reset password for user ID {target_user_id}"
            )
            reset_status_text.value = "✓ Password reset successfully!"
            reset_status_text.color = ft.Colors.GREEN
            page.update()
            
            import time
            time.sleep(1.5)
            close_reset_modal(e)
        else:
            reset_status_text.value = f"✗ {message}"
            reset_status_text.color = ft.Colors.RED
            page.update()
    
    reset_password_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Reset User Password", weight=ft.FontWeight.BOLD),
        content=ft.Container(
            content=ft.Column([
                reset_status_text,
                reset_user_name,
                ft.Divider(),
                reset_new_password,
            ], spacing=15, tight=True),
            width=400,
            padding=10,
        ),
        actions=[
            ft.TextButton("Cancel", on_click=close_reset_modal),
            ft.ElevatedButton(
                "Reset Password",
                on_click=handle_reset_password,
                bgcolor=ft.Colors.ORANGE,
                color=ft.Colors.WHITE,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    def open_reset_modal(user):
        """Open reset password modal"""
        reset_user_id.value = str(user['id'])
        reset_user_name.value = f"Resetting password for: {user['full_name']} ({user['email']})"
        reset_new_password.value = ""
        reset_status_text.value = ""
        page.open(reset_password_modal)
    
    # ==================== DELETE CONFIRMATION MODAL ====================
    delete_user_id = ft.Text("", visible=False)
    delete_user_info = ft.Text("", size=14)
    
    def close_delete_modal(e):
        delete_confirm_modal.open = False
        page.update()
    
    def handle_delete_user(e):
        """Handle user deletion"""
        target_user_id = int(delete_user_id.value)
        
        # Prevent self-deletion
        if target_user_id == user_id:
            show_snackbar("You cannot delete your own account!", is_error=True)
            close_delete_modal(e)
            return
        
        success, message = UserModel.delete_user(target_user_id)
        
        if success:
            ActivityLogModel.log_activity(
                user_id,
                "Deleted user",
                f"Deleted user ID {target_user_id}"
            )
            close_delete_modal(e)
            show_snackbar(message)
            refresh_panel()
        else:
            show_snackbar(message, is_error=True)
            close_delete_modal(e)
    
    delete_confirm_modal = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Icon(ft.Icons.WARNING, color=ft.Colors.RED, size=30),
            ft.Text("Confirm Deletion", weight=ft.FontWeight.BOLD, color=ft.Colors.RED),
        ]),
        content=ft.Container(
            content=ft.Column([
                delete_user_id,
                delete_user_info,
                ft.Container(height=10),
                ft.Text(
                    "This action cannot be undone. All reservations by this user will also be deleted.",
                    size=12,
                    color=ft.Colors.GREY_600,
                    italic=True
                ),
            ], spacing=10, tight=True),
            width=400,
            padding=10,
        ),
        actions=[
            ft.TextButton("Cancel", on_click=close_delete_modal),
            ft.ElevatedButton(
                "Delete User",
                on_click=handle_delete_user,
                bgcolor=ft.Colors.RED,
                color=ft.Colors.WHITE,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    def open_delete_modal(user):
        """Open delete confirmation modal"""
        delete_user_id.value = str(user['id'])
        delete_user_info.value = f"Are you sure you want to delete:\n\n{user['full_name']}\n{user['email']}\nRole: {user['role'].upper()}"
        page.open(delete_confirm_modal)
    
    # ==================== TOGGLE STATUS ====================
    def handle_toggle_status(user):
        """Toggle user active/inactive status"""
        # Prevent self-deactivation
        if user['id'] == user_id:
            show_snackbar("You cannot deactivate your own account!", is_error=True)
            return
        
        success, message = UserModel.toggle_user_status(user['id'])
        
        if success:
            action = "Deactivated" if user['is_active'] else "Activated"
            ActivityLogModel.log_activity(
                user_id,
                f"{action} user",
                f"{action} user: {user['full_name']}"
            )
            show_snackbar(message)
            refresh_panel()
        else:
            show_snackbar(message, is_error=True)
    
    # ==================== USER CARD ====================
    def create_user_card(user):
        """Create a user card with actions"""
        role_colors = {
            'admin': "#FAB295",
            'faculty': "#FFE0B2",
            'student': "#BCDDF5",
        }
        role_color = role_colors.get(user['role'], ft.Colors.GREY)
        
        status_color = "#AED7A5" if user['is_active'] else "#D7A5A5"
        status_text = "Active" if user['is_active'] else "Inactive"
        
        # Format created date
        created = user['created_at'].strftime('%Y-%m-%d') if hasattr(user['created_at'], 'strftime') else str(user['created_at'])
        
        # Prevent actions on self
        is_self = user['id'] == user_id
        
        # Get user photo or use default
        user_photo = user.get('photo') or "assets/images/default-user.png"
        
        return ft.Card(
            content=ft.Container(
                content=ft.Row([
                    # Profile picture
                    ft.Container(
                        content=ft.Image(
                            src=user_photo,
                            width=60,
                            height=60,
                            fit=ft.ImageFit.COVER,
                            border_radius=ft.border_radius.all(30),
                        ),
                        width=60,
                        height=60,
                        border_radius=ft.border_radius.all(30),
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    ),
                    
                    # User info column
                    ft.Container(
                        content=ft.Column([
                            ft.Text(user['full_name'], weight=ft.FontWeight.BOLD, size=15),
                            ft.Text(f"CSPC Email: {user['email']}", size=12, color=ft.Colors.GREY_700),
                            ft.Text(f"ID: {user['id_number']}", size=12, color=ft.Colors.GREY_700),
                        ], spacing=3),
                        width=200,
                    ),
                    
                    # Role column
                    ft.Container(
                        content=ft.Container(
                            content=ft.Text(user['role'].upper(), size=11),
                            bgcolor=role_color,
                            padding=ft.padding.symmetric(horizontal=10, vertical=4),
                            border_radius=8,
                            alignment=ft.alignment.center,
                        ),
                        width=100,
                        alignment=ft.alignment.center,
                    ),
                    
                    # Status column
                    ft.Container(
                        content=ft.Container(
                            content=ft.Text(status_text, size=11),
                            bgcolor=status_color,
                            padding=ft.padding.symmetric(horizontal=10, vertical=4),
                            border_radius=8,
                            alignment=ft.alignment.center,
                        ),
                        width=100,
                        alignment=ft.alignment.center,
                    ),
                    
                    # Action buttons
                    ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.EDIT,
                            tooltip="Edit User",
                            icon_color="#3B82F6",
                            on_click=lambda e, u=user: open_edit_modal(u),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.LOCK_RESET,
                            tooltip="Reset Password",
                            icon_color=ft.Colors.ORANGE,
                            on_click=lambda e, u=user: open_reset_modal(u),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.BLOCK if user['is_active'] else ft.Icons.CHECK_CIRCLE,
                            tooltip="Deactivate" if user['is_active'] else "Activate",
                            icon_color=ft.Colors.RED if user['is_active'] else ft.Colors.GREEN,
                            on_click=lambda e, u=user: handle_toggle_status(u),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            tooltip="Delete User",
                            icon_color=ft.Colors.RED,
                            on_click=lambda e, u=user: open_delete_modal(u),
                        ),
                    ], spacing=0),
                ], alignment=ft.MainAxisAlignment.START, spacing=30),
                padding=15,
            ),
            elevation=2,
            width=800,
        )
    
    # ==================== FILTER & SEARCH ====================
    def get_filtered_users():
        """Get users based on current filter and search"""
        # Get all users first
        if current_filter == "all":
            users = UserModel.get_all_users()
        elif current_filter in ['admin', 'faculty', 'student']:
            users = UserModel.get_users_by_role(current_filter)
        elif current_filter == "active":
            users = [u for u in UserModel.get_all_users() if u['is_active']]
        elif current_filter == "inactive":
            users = [u for u in UserModel.get_all_users() if not u['is_active']]
        else:
            users = UserModel.get_all_users()
        
        # Apply search filter
        if search_query:
            query_lower = search_query.lower()
            users = [u for u in users if 
                     query_lower in u['full_name'].lower() or 
                     query_lower in u['email'].lower() or 
                     query_lower in u['id_number'].lower()]
        
        return users
    
    def get_user_counts():
        """Get counts for each filter category"""
        all_users = UserModel.get_all_users()
        counts = {
            'all': len(all_users),
            'active': len([u for u in all_users if u['is_active']]),
            'inactive': len([u for u in all_users if not u['is_active']]),
            'admin': len([u for u in all_users if u['role'] == 'admin']),
            'faculty': len([u for u in all_users if u['role'] == 'faculty']),
            'student': len([u for u in all_users if u['role'] == 'student']),
        }
        return counts
    
    def create_filter_button(label, filter_value, count):
        """Create a filter button with count"""
        is_selected = current_filter == filter_value
        return ft.TextButton(
            text=f"{label} ({count})",
            on_click=lambda e: on_filter_click(filter_value),
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE if is_selected else ft.Colors.GREY_700,
                bgcolor="#3B82F6" if is_selected else ft.Colors.GREY_200,
                padding=ft.padding.symmetric(horizontal=15, vertical=10),
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )
    
    def on_filter_click(filter_value):
        """Handle filter button click"""
        nonlocal current_filter
        current_filter = filter_value
        update_filter_buttons()
        update_user_list()
    
    def update_filter_buttons():
        """Update filter buttons appearance"""
        counts = get_user_counts()
        filter_buttons_ref.current.controls = [
            ft.Text("Filter by:", size=14, color=ft.Colors.GREY_700, weight=ft.FontWeight.BOLD),
            create_filter_button("All Users", "all", counts['all']),
            create_filter_button("Active", "active", counts['active']),
            create_filter_button("Inactive", "inactive", counts['inactive']),
            create_filter_button("Admin", "admin", counts['admin']),
            create_filter_button("Faculty", "faculty", counts['faculty']),
            create_filter_button("Student", "student", counts['student']),
        ]
        page.update()
    
    def on_filter_change(e):
        nonlocal current_filter
        current_filter = e.control.value
        update_user_list()
    
    def on_search_change(e):
        nonlocal search_query
        search_query = e.control.value
        update_user_list()
    
    def update_user_list():
        """Update the user list display"""
        users = get_filtered_users()
        
        if users:
            user_list_ref.current.controls = [create_user_card(u) for u in users]
        else:
            user_list_ref.current.controls = [
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.PERSON_OFF, size=64, color=ft.Colors.GREY_400),
                        ft.Text("No users found", size=18, color=ft.Colors.GREY_600),
                        ft.Text("Try adjusting your filters", size=14, color=ft.Colors.GREY_500),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=40,
                    alignment=ft.alignment.center,
                )
            ]
        page.update()
    
    # Get initial user list
    users = get_filtered_users()
    user_cards = [create_user_card(u) for u in users] if users else [
        ft.Container(
            content=ft.Text("No users found", color=ft.Colors.GREY),
            padding=20
        )
    ]
    
    # ==================== BUILD PAGE ====================
    page.controls.clear()
    page.add(
        ft.Column([
            header,
            ft.Container(
                content=ft.Column([
                    # Title row
                    ft.Row([
                        ft.Container(
                            ft.Text("User Management", size=32, color="#4D4848",
                                    font_family="Montserrat Bold", weight=ft.FontWeight.BOLD),
                                    alignment=ft.alignment.center
                        ),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    
                    # Search and create button row (centered)
                    ft.Row([
                        ft.TextField(
                            ref=search_field_ref,
                            hint_text="Search by Name, Email, or ID Number",
                            prefix_icon=ft.Icons.SEARCH,
                            on_change=on_search_change,
                            border_color="#C3C3C3",
                            fill_color="#C3C3C3", 
                            focused_border_color="#C3C3C3",
                            focused_bgcolor="#C3C3C3",
                            bgcolor="#C3C3C3",
                            width=600,
                        ),
                        ft.ElevatedButton(
                            text="Create New User",
                            icon=ft.Icons.ADD,
                            on_click=open_create_modal,
                            height=45,
                            bgcolor="#8F98AA",
                            color=ft.Colors.WHITE,
                            width=150,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=3),
                            ),
                        ),
                    ], spacing=15, alignment=ft.MainAxisAlignment.CENTER),
                    
                    ft.Container(height=10),
                    
                    # Filter buttons row
                    ft.Container(
                        content=ft.Row(
                            ref=filter_buttons_ref,
                            controls=[
                                ft.Text("Filter by:", size=14, color=ft.Colors.GREY_700, weight=ft.FontWeight.BOLD),
                                create_filter_button("All Users", "all", len(users)),
                                create_filter_button("Active", "active", len([u for u in UserModel.get_all_users() if u['is_active']])),
                                create_filter_button("Inactive", "inactive", len([u for u in UserModel.get_all_users() if not u['is_active']])),
                                create_filter_button("Admin", "admin", len([u for u in UserModel.get_all_users() if u['role'] == 'admin'])),
                                create_filter_button("Faculty", "faculty", len([u for u in UserModel.get_all_users() if u['role'] == 'faculty'])),
                                create_filter_button("Student", "student", len([u for u in UserModel.get_all_users() if u['role'] == 'student'])),
                            ],
                            spacing=20,
                            wrap=True,
                        ),
                        alignment=ft.alignment.center,
                    ),
                    
                    ft.Container(height=5),
                    
                    # Total users count
                    ft.Text(f"Total: {len(users)} user(s)", color=ft.Colors.GREY_600, size=14),
                    
                    ft.Container(height=5),
                    
                    # User list
                    ft.Container(
                        content=ft.Column(
                            ref=user_list_ref,
                            controls=user_cards,
                            spacing=10,
                            scroll=ft.ScrollMode.AUTO,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        expand=True,
                        alignment=ft.alignment.top_center,
                    ),
                ], spacing=10),
                padding=20,
                expand=True,
            ),
        ], spacing=0, expand=True)
    )
    page.update()