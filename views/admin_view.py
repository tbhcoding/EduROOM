import flet as ft
from utils.config import ICONS, COLORS
from data.models import ReservationModel, ActivityLogModel
from components.app_header import create_app_header

try:
    from utils.websocket_client import realtime
    REALTIME_ENABLED = True
except ImportError:
    REALTIME_ENABLED = False


def show_admin_panel(page, user_id, role, name):
    """Display admin panel for managing reservations from database"""

    # Create the header and drawer
    header, drawer = create_app_header(page, user_id, role, name, current_page="reservations")
  
    if role != "admin":
        return
    
    if REALTIME_ENABLED:
        def on_new_reservation(data):
            """Handle new reservation event"""
            page.open(ft.SnackBar(
                content=ft.Text(f"🔔 {data['payload'].get('message', 'New reservation!')}"),
                bgcolor=ft.Colors.BLUE,
                duration=4000
            ))
            page.update()
            # Auto-refresh the panel
            refresh_panel()
        
        # Register callback and connect
        realtime.on("new_reservation", on_new_reservation)
        if not realtime.connected:
            realtime.connect()
    
    def back_to_dashboard(e):
        from views.dashboard_view import show_dashboard
        show_dashboard(page, user_id, role, name)
    
    def refresh_panel():
        """Refresh the admin panel to show updated data"""
        show_admin_panel(page, user_id, role, name)
    
    def handle_approve(reservation_id, room_name, requester):
        ReservationModel.approve_reservation(reservation_id)
        ActivityLogModel.log_activity(
            user_id, 
            "Approved reservation", 
            f"Approved {room_name} reservation by {requester}"
        )
        refresh_panel()
    
    def handle_reject(reservation_id, room_name, requester):
        ReservationModel.reject_reservation(reservation_id)
        ActivityLogModel.log_activity(
            user_id, 
            "Rejected reservation", 
            f"Rejected {room_name} reservation by {requester}"
        )
        refresh_panel()
    
    # Get all reservations from database
    reservations = ReservationModel.get_all_reservations()
    pending = [r for r in reservations if r["status"] == "pending"]
    approved = [r for r in reservations if r["status"] == "approved"]
    ongoing = [r for r in reservations if r["status"] == "ongoing"]
    done = [r for r in reservations if r["status"] == "done"]
    rejected = [r for r in reservations if r["status"] == "rejected"]
    
    def create_reservation_card(res, show_actions=True):
        """Create a reservation card with optional approve/reject buttons"""
        
        status_config = {
            "pending": {"color": "orange", "icon": ICONS.HOURGLASS_EMPTY},
            "approved": {"color": COLORS.GREEN if hasattr(COLORS, "GREEN") else "green", "icon": ICONS.CHECK_CIRCLE},
            "ongoing": {"color": "#2196F3", "icon": ICONS.PLAY_CIRCLE},
            "done": {"color": "#9E9E9E", "icon": ICONS.TASK_ALT},
            "rejected": {"color": "red", "icon": ICONS.CANCEL}
        }
        config = status_config.get(res["status"], status_config["pending"])
        
        # Format date and time
        res_date = res["reservation_date"].strftime('%m/%d/%Y') if hasattr(res["reservation_date"], 'strftime') else str(res["reservation_date"])
        start = str(res["start_time"])
        end = str(res["end_time"])
        
        # Create room image path
        image_src = res.get("image_url") if res.get("image_url") else "../assets/images/classroom-default.png"
        
        # Left side - Room image
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
                ft.Text(f"Reserved by: {res['full_name']}", size=12, color=ft.Colors.GREY_700),
                ft.Text(f"Duration: {start} - {end}", size=12, color=ft.Colors.GREY_700),
                ft.Text(f"Date: {res_date}", size=12, color=ft.Colors.GREY_700),
                ft.Text(f"Purpose: {res['purpose']}", size=12, color=ft.Colors.GREY_700),
            ], spacing=2, tight=True),
            expand=True,
            padding=ft.padding.only(left=15)
        )
        
        # Right section - Action buttons
        if show_actions and res["status"] == "pending":
            right_section = ft.Container(
                content=ft.Row([
                    ft.ElevatedButton(
                        "Approve",
                        color="white", width=120,
                        bgcolor="#10B981",
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=16)),
                        on_click=lambda e, rid=res["id"], rn=res["room_name"], req=res["full_name"]: handle_approve(rid, rn, req)
                    ),
                    ft.ElevatedButton(
                        "Reject",
                        color="white", width=120,
                        bgcolor="#EF4444",
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=16)),
                        on_click=lambda e, rid=res["id"], rn=res["room_name"], req=res["full_name"]: handle_reject(rid, rn, req)
                    )
                ], spacing=40, tight=True),
                padding=ft.padding.all(50)
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
                    [create_reservation_card(r, show_actions=(r["status"] == "pending")) for r in reservation_list],
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=10,
                expand=True,
            )
        else:
            return ft.Container(
                content=ft.Text(empty_message, color=COLORS.GREY if hasattr(COLORS, "GREY") else "grey"),
                padding=20,
                expand=True,
            )
    
    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(
                text=f"Pending ({len(pending)})",
                content=create_scrollable_tab_content(pending, "No pending reservations"),
            ),
            ft.Tab(
                text=f"Approved ({len(approved)})",
                content=create_scrollable_tab_content(approved, "No approved reservations"),
            ),
            ft.Tab(
                text=f"Ongoing ({len(ongoing)})",
                content=create_scrollable_tab_content(ongoing, "No ongoing reservations"),
            ),
            ft.Tab(
                text=f"Done ({len(done)})",
                content=create_scrollable_tab_content(done, "No completed reservations"),
            ),
            ft.Tab(
                text=f"Rejected ({len(rejected)})",
                content=create_scrollable_tab_content(rejected, "No rejected reservations"),
            ),
        ],
        expand=True
    )
    
    page.controls.clear()
    page.add(
        ft.Column(
            [
                header,
                ft.Container(
                    ft.Text("Manage Reservations", size=32, color="#4D4848",
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