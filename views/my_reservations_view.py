import flet as ft
from utils.config import ICONS, COLORS
from data.models import ReservationModel, ActivityLogModel
from datetime import datetime, date, time as datetime_time
from components.app_header import create_app_header

try:
    from utils.websocket_client import realtime
    REALTIME_ENABLED = True
except ImportError:
    REALTIME_ENABLED = False

def show_my_reservations(page, user_id, role, name):
    """Display faculty member's reservations from database"""
    
    # Create the header and drawer
    header, drawer = create_app_header(page, user_id, role, name, current_page="reservations")

    if role != "faculty":
        return
    
    def back_to_dashboard(e):
        from views.dashboard_view import show_dashboard
        show_dashboard(page, user_id, role, name)
    
    def refresh_view():
        """Refresh the reservations view"""
        show_my_reservations(page, user_id, role, name)
    
    # Real-time updates setup
    if REALTIME_ENABLED:
        def on_reservation_approved(data):
            """Handle reservation approved event"""
            if data['payload'].get('user_id') == user_id:
                page.open(ft.SnackBar(
                    content=ft.Text(f"✅ {data['payload'].get('message', 'Reservation approved!')}"),
                    bgcolor=ft.Colors.GREEN,
                    duration=4000
                ))
                page.update()
                refresh_view()
        
        def on_reservation_rejected(data):
            """Handle reservation rejected event"""
            if data['payload'].get('user_id') == user_id:
                page.open(ft.SnackBar(
                    content=ft.Text(f"❌ {data['payload'].get('message', 'Reservation rejected')}"),
                    bgcolor=ft.Colors.RED,
                    duration=4000
                ))
                page.update()
                refresh_view()
        
        realtime.on("reservation_approved", on_reservation_approved)
        realtime.on("reservation_rejected", on_reservation_rejected)
        if not realtime.connected:
            realtime.connect()
    
    def show_edit_dialog(reservation):
        """Show dialog to edit a reservation"""
        
        # Pre-fill with existing data
        res_date = reservation["reservation_date"]
        if hasattr(res_date, 'strftime'):
            date_value = res_date.strftime('%Y-%m-%d')
        else:
            date_value = str(res_date)
        
        start_value = str(reservation["start_time"])[:5]
        end_value = str(reservation["end_time"])[:5]
        
        date_field = ft.TextField(
            label="Date",
            hint_text="YYYY-MM-DD",
            value=date_value,
            width=300,
            border_radius=5
        )
        
        start_field = ft.TextField(
            label="Start Time",
            hint_text="HH:MM",
            value=start_value,
            width=140,
            border_radius=5
        )
        
        end_field = ft.TextField(
            label="End Time",
            hint_text="HH:MM",
            value=end_value,
            width=140,
            border_radius=5
        )
        
        purpose_field = ft.TextField(
            label="Purpose",
            value=reservation["purpose"],
            multiline=True,
            min_lines=2,
            max_lines=4,
            width=300,
            border_radius=5
        )
        
        error_text = ft.Text("", color="red", size=12)
        
        def validate_date(date_str):
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
                return True
            except ValueError:
                return False
        
        def validate_time(time_str):
            try:
                datetime.strptime(time_str, '%H:%M')
                return True
            except ValueError:
                return False
        
        def save_changes(e):
            if not date_field.value or not start_field.value or not end_field.value or not purpose_field.value:
                error_text.value = "⚠ Please fill all fields"
                page.update()
                return
            
            if not validate_date(date_field.value):
                error_text.value = "⚠ Invalid date format. Use YYYY-MM-DD"
                page.update()
                return
            
            if not validate_time(start_field.value) or not validate_time(end_field.value):
                error_text.value = "⚠ Invalid time format. Use HH:MM"
                page.update()
                return
            
            is_available = ReservationModel.check_availability(
                reservation["classroom_id"],
                date_field.value,
                start_field.value,
                end_field.value,
                exclude_reservation_id=reservation["id"]
            )
            
            if not is_available:
                error_text.value = "⚠ Time slot not available"
                page.update()
                return
            
            success = ReservationModel.update_reservation(
                reservation["id"],
                date_field.value,
                start_field.value,
                end_field.value,
                purpose_field.value
            )
            
            if success:
                ActivityLogModel.log_activity(
                    user_id,
                    "Updated reservation",
                    f"Modified reservation for {reservation['room_name']}"
                )
                dialog.open = False
                page.update()
                refresh_view()
            else:
                error_text.value = "⚠ Failed to update. Please try again."
                page.update()
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Edit Reservation: {reservation['room_name']}", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(f"{reservation['building']}", size=12, color="grey"),
                    ft.Container(height=10),
                    date_field,
                    ft.Container(height=10),
                    ft.Row([start_field, end_field], spacing=20),
                    ft.Container(height=10),
                    purpose_field,
                    error_text,
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ICONS.INFO, color="#FF9800", size=16),
                            ft.Text("Editing will reset status to pending", size=12, color="#FF9800", italic=True)
                        ], spacing=5),
                        margin=ft.margin.only(top=10)
                    )
                ], spacing=5),
                width=350,
                height=300,
                padding=10
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton(
                    "Save Changes",
                    on_click=save_changes, width=140,
                    style=ft.ButtonStyle(bgcolor="#4CAF50", color="white", shape=ft.RoundedRectangleBorder(radius=16))
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    def show_cancel_dialog(reservation):
        """Show confirmation dialog to cancel a reservation"""
        
        def confirm_cancel(e):
            success = ReservationModel.cancel_reservation(reservation["id"])
            
            if success:
                ActivityLogModel.log_activity(
                    user_id,
                    "Cancelled reservation",
                    f"Cancelled reservation for {reservation['room_name']}"
                )
                dialog.open = False
                page.update()
                refresh_view()
            else:
                dialog.open = False
                page.update()
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        res_date = reservation["reservation_date"]
        if hasattr(res_date, 'strftime'):
            date_str = res_date.strftime('%Y-%m-%d')
        else:
            date_str = str(res_date)
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Text("Cancel Reservation?", font_family="Montserrat Bold", weight=ft.FontWeight.BOLD)
            ], spacing=10),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(f"Room: {reservation['room_name']}", weight=ft.FontWeight.BOLD),
                    ft.Text(f"Date: {date_str}"),
                    ft.Text(f"Time: {str(reservation['start_time'])[:5]} - {str(reservation['end_time'])[:5]}"),
                    ft.Container(height=10),
                    ft.Text("This action cannot be undone.", color="red", italic=True),
                ], spacing=5),
                width=300,
                height=120,
                padding=10
            ),
            actions=[
                ft.TextButton("Keep Reservation", on_click=close_dialog),
                ft.ElevatedButton(
                    "Yes, Cancel It",
                    on_click=confirm_cancel, width=120,
                    style=ft.ButtonStyle(bgcolor="#F44336", color="white")
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    # Get reservations from database
    reservations = ReservationModel.get_user_reservations(user_id)
    
    # Separate into upcoming and past reservations
    today = date.today()
    now = datetime.now().time()
    
    upcoming = []
    past = []
    
    for res in reservations:
        res_date = res["reservation_date"]
        if hasattr(res_date, 'date'):
            res_date = res_date.date()
        elif isinstance(res_date, str):
            res_date = datetime.strptime(res_date, '%Y-%m-%d').date()
        
        # Parse end time
        end_time = res["end_time"]
        if isinstance(end_time, str):
            try:
                end_time = datetime.strptime(end_time, '%H:%M:%S').time()
            except ValueError:
                end_time = datetime.strptime(end_time, '%H:%M').time()
        elif hasattr(end_time, 'seconds'):  # timedelta object
            total_seconds = end_time.total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            seconds = int(total_seconds % 60)
            end_time = datetime_time(hours, minutes, seconds)
        elif not isinstance(end_time, datetime_time):
            # If it's a datetime object, extract time
            if hasattr(end_time, 'time'):
                end_time = end_time.time()
            else:
                # Default to end of day if parsing fails
                end_time = datetime_time(23, 59, 59)
        
        # Determine if reservation is past or upcoming
        if res_date < today or (res_date == today and end_time < now):
            past.append(res)
        else:
            upcoming.append(res)
    
    def create_reservation_card(res):
        """Create a reservation card following admin panel format"""
        # Debug: Print the reservation data to see what's being returned
        print(f"Reservation data: {res}")
        print(f"Image URL: {res.get('image_url')}")
        
        status_config = {
            "pending": {"color": "orange", "icon": ICONS.HOURGLASS_EMPTY, "can_edit": True, "can_cancel": True},
            "approved": {"color": COLORS.GREEN if hasattr(COLORS, "GREEN") else "green", "icon": ICONS.CHECK_CIRCLE, "can_edit": False, "can_cancel": True},
            "ongoing": {"color": "#2196F3", "icon": ICONS.PLAY_CIRCLE, "can_edit": False, "can_cancel": False},
            "done": {"color": "#9E9E9E", "icon": ICONS.TASK_ALT, "can_edit": False, "can_cancel": False},
            "rejected": {"color": "red", "icon": ICONS.CANCEL, "can_edit": False, "can_cancel": False},
            "cancelled": {"color": "grey", "icon": ICONS.BLOCK, "can_edit": False, "can_cancel": False}
        }
        config = status_config.get(res["status"], status_config["pending"])
        
        # Format date and time
        res_date = res["reservation_date"].strftime('%m/%d/%Y') if hasattr(res["reservation_date"], 'strftime') else str(res["reservation_date"])
        start = str(res["start_time"])[:5]
        end = str(res["end_time"])[:5]
        
        # Create room image path
        image_url = res.get("image_url")
        if image_url:
            # If it's already a full path, use it as-is
            image_src = image_url
        else:
            # Default image
            image_src = "assets/images/classroom-default.png"

        # Left section - Room image
        left_section = ft.Container(
            content=ft.Image(
                src=image_src,
                width=160,
                height=120,
                fit=ft.ImageFit.COVER,
                border_radius=ft.border_radius.all(8)
            ),
            padding=ft.padding.all(15)
        )
        
        # Middle section - Room details
        middle_section = ft.Container(
            content=ft.Column([
                ft.Text(res["room_name"], size=16, weight=ft.FontWeight.BOLD),
                ft.Text(f"Building: {res.get('building', 'N/A')}", size=12, color=ft.Colors.GREY_700),
                ft.Row([
                    ft.Text(f"Duration: {start} - {end}", size=12, color=ft.Colors.GREY_700),
                    ft.Text(f"Date: {res_date}", size=12, color=ft.Colors.GREY_700),
                ], spacing=15),
                ft.Text(f"Purpose: {res['purpose']}", size=12, color=ft.Colors.GREY_700),
            ], spacing=2, tight=True),
            expand=True,
            padding=ft.padding.only(left=15)
        )
        
        # Right section - Status and actions
        if config["can_edit"] or config["can_cancel"]:
            action_buttons = []
            if config["can_edit"]:
                action_buttons.append(
                    ft.ElevatedButton(
                        "Edit",
                        color="white",
                        width=120,
                        bgcolor="#2196F3",
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=16)),
                        on_click=lambda e, r=res: show_edit_dialog(r)
                    )
                )
            if config["can_cancel"]:
                action_buttons.append(
                    ft.ElevatedButton(
                        "Cancel",
                        color="white",
                        width=120,
                        bgcolor="#EF4444",
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=16)),
                        on_click=lambda e, r=res: show_cancel_dialog(r)
                    )
                )
            
            right_section = ft.Container(
                content=ft.Row([
                    ft.Row([
                        ft.Icon(config["icon"], size=20, color=config["color"]),
                        ft.Text(res["status"].upper(), size=12, weight=ft.FontWeight.BOLD, color=config["color"])
                    ], spacing=5),
                    ft.Container(width=20),  # Spacing between status and buttons
                    ft.Column(action_buttons, spacing=10, horizontal_alignment=ft.CrossAxisAlignment.END)
                ], alignment=ft.MainAxisAlignment.END, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.all(15)
            )
        else:
            right_section = ft.Container(
                content=ft.Row([
                    ft.Icon(config["icon"], size=20, color=config["color"]),
                    ft.Text(res["status"].upper(), size=12, weight=ft.FontWeight.BOLD, color=config["color"])
                ], spacing=5),
                padding=ft.padding.only(right=100)
            )
        
        return ft.Card(
            content=ft.Container(
                content=ft.Row([
                    left_section,
                    middle_section,
                    right_section
                ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=15,
                bgcolor=ft.Colors.WHITE
            ),
            elevation=2
        )

    def create_scrollable_tab_content(reservation_list, empty_message):
        """Create scrollable content for a tab"""
        if reservation_list:
            return ft.Container(
                content=ft.Column(
                    [create_reservation_card(r) for r in reservation_list],
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=10,
                expand=True,
            )
        else:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ICONS.EVENT_BUSY, size=48, color="grey"),
                    ft.Text(empty_message, color="grey", size=16),
                    ft.Text("Your reservations will appear here", color="grey", size=12)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                padding=40,
                expand=True,
                alignment=ft.alignment.center
            )
    
    # Create tabs
    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(
                text=f"Upcoming ({len(upcoming)})",
                content=create_scrollable_tab_content(upcoming, "No upcoming reservations"),
            ),
            ft.Tab(
                text=f"Past ({len(past)})",
                content=create_scrollable_tab_content(past, "No past reservations"),
            ),
        ],
        expand=True
    )
    
    page.controls.clear()
    page.overlay.clear()
    page.add(
        ft.Column(
            [
                header,
                ft.Container(
                    ft.Text("My Reservations", size=32, color="#4D4848",
                            font_family="Montserrat Bold", weight=ft.FontWeight.BOLD),
                    padding=5, width=850, alignment=ft.alignment.center
                ),
                ft.Container(
                    ft.Row([tabs], alignment=ft.MainAxisAlignment.CENTER),
                    width=1000,
                    expand=True,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True
        )
    )
    page.update()