import flet as ft
from utils.config import ICONS, COLORS
from data.models import ReservationModel, ActivityLogModel
from datetime import datetime
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
            title=ft.Text(f"Edit Reservation - {reservation['room_name']}"),
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
                padding=10
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton(
                    "Save Changes",
                    icon=ICONS.SAVE,
                    on_click=save_changes,
                    style=ft.ButtonStyle(bgcolor="#4CAF50", color="white")
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
                ft.Icon(ICONS.WARNING, color="#F44336"),
                ft.Text("Cancel Reservation?")
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
                padding=10
            ),
            actions=[
                ft.TextButton("Keep Reservation", on_click=close_dialog),
                ft.ElevatedButton(
                    "Yes, Cancel It",
                    icon=ICONS.DELETE,
                    on_click=confirm_cancel,
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
    
    # Create reservation cards
    reservation_cards = []
    if not reservations:
        reservation_cards.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ICONS.EVENT_BUSY, size=48, color="grey"),
                    ft.Text("No reservations yet", color="grey", size=16),
                    ft.Text("Your reservations will appear here", color="grey", size=12)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                padding=40,
                alignment=ft.alignment.center
            )
        )
    else:
        for res in reservations:
            status_config = {
                "pending": {"color": "orange", "icon": ICONS.HOURGLASS_EMPTY, "text": "Pending Approval", "can_edit": True, "can_cancel": True},
                "approved": {"color": COLORS.GREEN if hasattr(COLORS, "GREEN") else "green", "icon": ICONS.CHECK_CIRCLE, "text": "Approved", "can_edit": False, "can_cancel": True},
                "ongoing": {"color": "#2196F3", "icon": ICONS.PLAY_CIRCLE, "text": "Ongoing", "can_edit": False, "can_cancel": False},
                "done": {"color": "#9E9E9E", "icon": ICONS.TASK_ALT, "text": "Done", "can_edit": False, "can_cancel": False},
                "rejected": {"color": "red", "icon": ICONS.CANCEL, "text": "Rejected", "can_edit": False, "can_cancel": False},
                "cancelled": {"color": "grey", "icon": ICONS.BLOCK, "text": "Cancelled", "can_edit": False, "can_cancel": False}
            }
            config = status_config.get(res["status"], status_config["pending"])
            
            res_date = res["reservation_date"].strftime('%Y-%m-%d') if hasattr(res["reservation_date"], 'strftime') else str(res["reservation_date"])
            start = str(res["start_time"])[:5]
            end = str(res["end_time"])[:5]
            
            action_buttons = []
            if config["can_edit"]:
                action_buttons.append(
                    ft.IconButton(
                        icon=ICONS.EDIT,
                        icon_color="#2196F3",
                        tooltip="Edit Reservation",
                        on_click=lambda e, r=res: show_edit_dialog(r)
                    )
                )
            if config["can_cancel"]:
                action_buttons.append(
                    ft.IconButton(
                        icon=ICONS.DELETE_OUTLINE,
                        icon_color="#F44336",
                        tooltip="Cancel Reservation",
                        on_click=lambda e, r=res: show_cancel_dialog(r)
                    )
                )
            
            # FIXED CARD LAYOUT
            card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        # Header row with room name and action buttons
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ICONS.MEETING_ROOM, color="#5A5A5A"),
                                ft.Column([
                                    ft.Text(res["room_name"], weight=ft.FontWeight.BOLD, size=16),
                                    ft.Text(f"{res['building']} • {res_date} • {start} - {end}", size=12, color="grey"),
                                ], spacing=2, expand=True),
                                ft.Row(action_buttons, spacing=0) if action_buttons else ft.Container(),
                            ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            padding=ft.padding.only(left=15, right=10, top=10),
                        ),
                        
                        # Purpose and status
                        ft.Container(
                            content=ft.Column([
                                ft.Text(f"Purpose: {res['purpose']}", size=12),
                                ft.Container(height=5),
                                ft.Row([
                                    ft.Icon(config["icon"], size=16, color=config["color"]),
                                    ft.Text(config["text"], size=12, weight=ft.FontWeight.BOLD, color=config["color"])
                                ], spacing=5)
                            ]),
                            padding=ft.padding.only(left=15, right=15, bottom=10)
                        )
                    ], spacing=5),
                    padding=5,
                )
            )
            reservation_cards.append(card)
    
    page.controls.clear()
    page.overlay.clear()
    page.add(
        ft.Column([
            header, 
            ft.Container(
                content=ft.Row([
                    ft.Row([
                        ft.IconButton(icon=ICONS.ARROW_BACK, on_click=back_to_dashboard, tooltip="Back"),
                        ft.Text("My Reservations", size=24, weight=ft.FontWeight.BOLD),
                    ]),
                    ft.IconButton(icon=ICONS.REFRESH, on_click=lambda e: refresh_view(), tooltip="Refresh"),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=20,
                width=850
            ),
            ft.Divider(),
            
            # Legend
            ft.Container(
                content=ft.Row([
                    ft.Text("Actions: ", size=12, weight=ft.FontWeight.BOLD),
                    ft.Icon(ICONS.EDIT, size=16, color="#2196F3"),
                    ft.Text("Edit", size=12),
                    ft.Container(width=10),
                    ft.Icon(ICONS.DELETE_OUTLINE, size=16, color="#F44336"),
                    ft.Text("Cancel", size=12),
                ], spacing=5),
                padding=ft.padding.only(left=20, bottom=10)
            ),
            
            ft.Column(
                reservation_cards,
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
                height=500,
                width=850,
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )
    page.update()