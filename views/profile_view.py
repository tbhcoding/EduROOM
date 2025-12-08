import flet as ft
import os
import shutil
import uuid
from data.models import UserModel, ActivityLogModel
from utils.security import ensure_authenticated, touch_session, get_csrf_token

# ==================== CONFIGURATION ====================
# Allowed file extensions for profile pictures
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
# Maximum file size: 2MB
MAX_FILE_SIZE = 2 * 1024 * 1024
# Directory to store profile pictures
PROFILE_PICTURES_DIR = "storage/profile_pictures"


def validate_image_file(file_path):
    """
    Validate uploaded image file for type and size.
    
    Args:
        file_path: Path to the uploaded file
        
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    # Check file extension
    _, ext = os.path.splitext(file_path)
    if ext.lower() not in ALLOWED_EXTENSIONS:
        allowed = ', '.join(ALLOWED_EXTENSIONS)
        return False, f"Invalid file type. Allowed types: {allowed}"
    
    # Check file size
    try:
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            size_mb = MAX_FILE_SIZE / (1024 * 1024)
            return False, f"File too large. Maximum size is {size_mb:.0f}MB"
        if file_size == 0:
            return False, "File is empty"
    except OSError:
        return False, "Could not read file"
    
    return True, None


def show_profile(page, user_id, role, name):
    """Display user profile with edit capabilities and profile picture upload"""
    
    # Session guard
    if not ensure_authenticated(page):
        return
    
    # Get user data from database
    try:
        user_data = UserModel.get_user_by_id(user_id)
        if not user_data:
            user_data = {
                "full_name": name,
                "email": "",
                "role": role,
                "photo": None,
            }
    except Exception:
        user_data = {
            "full_name": name,
            "email": "",
            "role": role,
            "photo": None,
        }
    
    # Get current photo path or use default
    current_photo = user_data.get("photo") or "assets/images/default-user.png"
    
    # ==================== PROFILE PICTURE SECTION ====================
    
    # Reference for dynamic updates
    profile_image_ref = ft.Ref[ft.Container]()
    upload_status_ref = ft.Ref[ft.Text]()
    
    def show_upload_status(message, is_error=False):
        """Display upload status message"""
        upload_status_ref.current.value = message
        upload_status_ref.current.color = ft.Colors.RED if is_error else ft.Colors.GREEN
        upload_status_ref.current.visible = True
        page.update()
    
    def hide_upload_status():
        """Hide upload status message"""
        if upload_status_ref.current:
            upload_status_ref.current.visible = False
            page.update()
    
    def handle_file_picker_result(e: ft.FilePickerResultEvent):
        """Handle the file picker result for profile picture upload"""
        hide_upload_status()
        
        # Check if user selected a file
        if not e.files or len(e.files) == 0:
            return  # User cancelled the picker
        
        selected_file = e.files[0]
        file_path = selected_file.path
        
        # For web/some platforms, path might not be available
        if not file_path:
            show_upload_status("✗ Could not access the selected file", is_error=True)
            return
        
        # Validate the file (type and size)
        is_valid, error_message = validate_image_file(file_path)
        if not is_valid:
            show_upload_status(f"✗ {error_message}", is_error=True)
            return
        
        try:
            # Ensure the profile pictures directory exists
            os.makedirs(PROFILE_PICTURES_DIR, exist_ok=True)
            
            # Generate a unique filename to prevent conflicts
            _, ext = os.path.splitext(file_path)
            unique_filename = f"user_{user_id}_{uuid.uuid4().hex[:8]}{ext.lower()}"
            destination_path = os.path.join(PROFILE_PICTURES_DIR, unique_filename)
            
            # Copy the file to our storage directory
            shutil.copy2(file_path, destination_path)
            
            # Store path relative to assets for Flet to find it
            # Using ../ prefix since views are in a subdirectory
            relative_path = f"../{destination_path}"
            
            # Update database with new photo path
            success, message = UserModel.update_user_photo(user_id, relative_path)
            
            if success:
                # Update the displayed image
                profile_image_ref.current.content.src = relative_path
                page.update()
                
                # Log the activity
                ActivityLogModel.log_activity(
                    user_id, 
                    "Profile picture updated",
                    f"User uploaded a new profile picture"
                )
                
                show_upload_status("✓ Profile picture updated successfully!")
                
                # Update session photo if stored there
                try:
                    page.session.set("user_photo", relative_path)
                except Exception:
                    pass
                    
            else:
                show_upload_status(f"✗ {message}", is_error=True)
                # Clean up the copied file if database update failed
                if os.path.exists(destination_path):
                    os.remove(destination_path)
                    
        except PermissionError:
            show_upload_status("✗ Permission denied. Cannot save file.", is_error=True)
        except Exception as ex:
            show_upload_status(f"✗ Error uploading file: {str(ex)}", is_error=True)
    
    # Create the file picker and add to page overlay
    file_picker = ft.FilePicker(on_result=handle_file_picker_result)
    page.overlay.append(file_picker)
    
    def open_file_picker(e):
        """Open file picker dialog for image selection"""
        hide_upload_status()
        file_picker.pick_files(
            allowed_extensions=["png", "jpg", "jpeg", "gif", "webp"],
            allow_multiple=False,
            dialog_title="Select Profile Picture (Max 2MB)"
        )
    
    def remove_profile_picture(e):
        """Remove current profile picture and reset to default"""
        try:
            default_photo = "assets/images/default-user.png"
            success, message = UserModel.update_user_photo(user_id, default_photo)
            
            if success:
                # Update the displayed image
                profile_image_ref.current.content.src = default_photo
                page.update()
                
                # Log the activity
                ActivityLogModel.log_activity(
                    user_id,
                    "Profile picture removed",
                    "User removed their profile picture"
                )
                
                show_upload_status("✓ Profile picture removed")
                
                # Update session
                try:
                    page.session.set("user_photo", default_photo)
                except Exception:
                    pass
            else:
                show_upload_status(f"✗ {message}", is_error=True)
                
        except Exception as ex:
            show_upload_status(f"✗ Error: {str(ex)}", is_error=True)
    
    # ==================== PASSWORD CHANGE SECTION ====================
    
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
        hint_text="Minimum 8 characters",
    )
    
    confirm_password = ft.TextField(
        label="Confirm New Password",
        password=True,
        can_reveal_password=True,
        width=400,
    )
    
    modal_status_text = ft.Text("", size=14)
    
    def go_back(e):
        """Navigate back to dashboard"""
        # Clean up file picker from overlay
        if file_picker in page.overlay:
            page.overlay.remove(file_picker)
        from views.dashboard_view import show_dashboard
        show_dashboard(page, user_id, role, name)
    
    def close_password_modal(e):
        """Close password change modal and reset fields"""
        password_modal.open = False
        current_password.value = ""
        new_password.value = ""
        confirm_password.value = ""
        modal_status_text.value = ""
        page.update()
    
    def change_password(e):
        """Change user password with validation"""
        # Validate current password is provided
        if not current_password.value:
            modal_status_text.value = "✗ Please enter your current password"
            modal_status_text.color = ft.Colors.RED
            page.update()
            return
        
        # Validate new password is provided
        if not new_password.value:
            modal_status_text.value = "✗ Please enter a new password"
            modal_status_text.color = ft.Colors.RED
            page.update()
            return
        
        # Validate password length
        if len(new_password.value) < 8:
            modal_status_text.value = "✗ New password must be at least 8 characters"
            modal_status_text.color = ft.Colors.RED
            page.update()
            return
        
        # Validate passwords match
        if new_password.value != confirm_password.value:
            modal_status_text.value = "✗ New passwords do not match"
            modal_status_text.color = ft.Colors.RED
            page.update()
            return
        
        # Attempt to change password
        try:
            success, message = UserModel.change_password(
                user_id, 
                current_password.value, 
                new_password.value
            )
            
            if success:
                modal_status_text.value = f"✓ {message}"
                modal_status_text.color = ft.Colors.GREEN
                page.update()
                
                # Log the activity
                ActivityLogModel.log_activity(
                    user_id,
                    "Password changed",
                    "User changed their password"
                )
                
                # Close modal after brief delay
                import time
                time.sleep(1.5)
                close_password_modal(e)
            else:
                modal_status_text.value = f"✗ {message}"
                modal_status_text.color = ft.Colors.RED
                page.update()
                
        except Exception as ex:
            modal_status_text.value = f"✗ Error: {str(ex)}"
            modal_status_text.color = ft.Colors.RED
            page.update()

    # Password change modal dialog
    password_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Change Password", weight=ft.FontWeight.BOLD),
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
            ft.ElevatedButton(
                "Update Password", 
                on_click=change_password,
                bgcolor=ft.Colors.BLUE,
                color=ft.Colors.WHITE,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    def open_password_modal(e):
        """Open password change modal"""
        page.open(password_modal)
    
    # ==================== BUILD UI COMPONENTS ====================
    
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
    
    # Profile picture with upload controls
    profile_picture_section = ft.Container(
        content=ft.Column(
            [
                ft.Text("Profile Picture", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                ft.Row(
                    [
                        # Profile image in a circular container
                        ft.Container(
                            ref=profile_image_ref,
                            content=ft.Image(
                                src=current_photo,
                                width=120,
                                height=120,
                                fit=ft.ImageFit.COVER,
                                border_radius=ft.border_radius.all(60),
                            ),
                            width=120,
                            height=120,
                            border_radius=ft.border_radius.all(60),
                            border=ft.border.all(3, ft.Colors.BLUE_200),
                            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                        ),
                        ft.Container(width=20),
                        # Upload controls
                        ft.Column(
                            [
                                ft.ElevatedButton(
                                    "Upload New Picture",
                                    icon=ft.Icons.UPLOAD,
                                    on_click=open_file_picker,
                                    bgcolor=ft.Colors.BLUE,
                                    color=ft.Colors.WHITE,
                                ),
                                ft.OutlinedButton(
                                    "Remove Picture",
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    on_click=remove_profile_picture,
                                ),
                                ft.Text(
                                    "Allowed: PNG, JPG, GIF, WebP (Max 2MB)",
                                    size=11,
                                    color=ft.Colors.GREY_600,
                                    italic=True,
                                ),
                                # Status message for upload feedback
                                ft.Text(
                                    ref=upload_status_ref,
                                    value="",
                                    size=13,
                                    visible=False,
                                ),
                            ],
                            spacing=10,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
            spacing=5,
        ),
        padding=20,
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        border=ft.border.all(1, ft.Colors.GREY_300),
    )
    
    # Personal information section
    personal_info_section = ft.Container(
        content=ft.Column(
            [
                ft.Text("Personal Information", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(height=15),
                # Name row
                ft.Row([
                    ft.Container(
                        content=ft.Text("Full Name:", size=14, weight=ft.FontWeight.BOLD),
                        width=120,
                    ),
                    ft.Text(user_data.get("full_name", name), size=14),
                ]),
                ft.Container(height=10),
                # Email row
                ft.Row([
                    ft.Container(
                        content=ft.Text("CSPC Email:", size=14, weight=ft.FontWeight.BOLD),
                        width=120,
                    ),
                    ft.Text(user_data.get("email", "Not set"), size=14),
                ]),
                ft.Container(height=10),
                # ID Number row
                ft.Row([
                    ft.Container(
                        content=ft.Text("ID Number:", size=14, weight=ft.FontWeight.BOLD),
                        width=120,
                    ),
                    ft.Text(user_data.get("id_number", "N/A"), size=14),
                ]),
                ft.Container(height=10),
                # Role row
                ft.Row([
                    ft.Container(
                        content=ft.Text("Role:", size=14, weight=ft.FontWeight.BOLD),
                        width=120,
                    ),
                    ft.Container(
                        content=ft.Text(role.upper(), size=12, color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.BLUE,
                        padding=ft.padding.symmetric(horizontal=12, vertical=4),
                        border_radius=5,
                    ),
                ]),
            ],
            spacing=5,
        ),
        padding=20,
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        border=ft.border.all(1, ft.Colors.GREY_300),
    )
    
    # Security section (password change)
    security_section = ft.Container(
        content=ft.Column(
            [
                ft.Text("Security", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                ft.Text(
                    "Keep your account secure by using a strong password.",
                    size=13,
                    color=ft.Colors.GREY_600,
                ),
                ft.Container(height=15),
                ft.ElevatedButton(
                    "Change Password",
                    icon=ft.Icons.LOCK,
                    on_click=open_password_modal,
                    width=200,
                ),
            ],
            spacing=5,
        ),
        padding=20,
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        border=ft.border.all(1, ft.Colors.GREY_300),
    )
    
    # ==================== BUILD PAGE ====================
    
    page.controls.clear()
    page.add(
        ft.Column([
            header,
            ft.Container(
                content=ft.Column(
                    [
                        profile_picture_section,
                        ft.Container(height=15),
                        personal_info_section,
                        ft.Container(height=15),
                        security_section,
                    ],
                    spacing=0,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=30,
                expand=True,
            )
        ], spacing=0, expand=True)
    )
    page.update()