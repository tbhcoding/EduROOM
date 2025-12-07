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
        res_date = res["reservation_date"].strftime('%Y-%m-%d') if hasattr(res["reservation_date"], 'strftime') else str(res["reservation_date"])
        start = str(res["start_time"])
        end = str(res["end_time"])
        
        card_content = [
            ft.ListTile(
                leading=ft.Icon(ICONS.MEETING_ROOM),
                title=ft.Text(res["room_name"], weight=ft.FontWeight.BOLD),
                subtitle=ft.Text(f"By: {res['full_name']} ({res['email']}) • {res_date} • {start}-{end}"),
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text(f"Purpose: {res['purpose']}", size=12),
                    ft.Container(height=5),
                ]),
                padding=ft.padding.only(left=15, right=15, bottom=5)
            )
        ]
        
        # Add action buttons only for pending reservations
        if show_actions and res["status"] == "pending":
            card_content.append(
                ft.Container(
                    content=ft.Row([
                        ft.ElevatedButton(
                            "Approve",
                            icon=ICONS.CHECK,
                            color="white",
                            bgcolor=COLORS.GREEN if hasattr(COLORS, "GREEN") else "green",
                            on_click=lambda e, rid=res["id"], rn=res["room_name"], req=res["full_name"]: handle_approve(rid, rn, req)
                        ),
                        ft.OutlinedButton(
                            "Reject",
                            icon=ICONS.CLOSE,
                            on_click=lambda e, rid=res["id"], rn=res["room_name"], req=res["full_name"]: handle_reject(rid, rn, req)
                        )
                    ], spacing=10),
                    padding=ft.padding.only(left=15, right=15, bottom=10)
                )
            )
        else:
            # Show status badge for approved/rejected
            card_content.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(config["icon"], size=16, color=config["color"]),
                        ft.Text(res["status"].upper(), size=12, weight=ft.FontWeight.BOLD, color=config["color"])
                    ], spacing=5),
                    padding=ft.padding.only(left=15, right=15, bottom=10)
                )
            )
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column(card_content, spacing=0),
                padding=10
            )
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
    
    # Create tabs for different sections
    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(
                text=f"Pending ({len(pending)})",
                icon=ICONS.PENDING,
                content=create_scrollable_tab_content(pending, "No pending reservations")
            ),
            ft.Tab(
                text=f"Approved ({len(approved)})",
                icon=ICONS.CHECK_CIRCLE,
                content=create_scrollable_tab_content(approved, "No approved reservations")
            ),
            ft.Tab(
                text=f"Ongoing ({len(ongoing)})",
                icon=ICONS.PLAY_CIRCLE,
                content=create_scrollable_tab_content(ongoing, "No ongoing reservations")
            ),
            ft.Tab(
                text=f"Done ({len(done)})",
                icon=ICONS.TASK_ALT,
                content=create_scrollable_tab_content(done, "No completed reservations")
            ),
            ft.Tab(
                text=f"Rejected ({len(rejected)})",
                icon=ICONS.CANCEL,
                content=create_scrollable_tab_content(rejected, "No rejected reservations")
            ),
        ],
        expand=True
    )
    
    page.controls.clear()
    page.add(
        ft.Column([
            header, 
            ft.Container(
                content=ft.Row([
                    ft.Row([
                        ft.IconButton(icon=ICONS.ARROW_BACK, on_click=back_to_dashboard, tooltip="Back"),
                        ft.Text("Admin Panel - Manage Reservations", size=24, weight=ft.FontWeight.BOLD),
                    ]),
                    ft.IconButton(icon=ICONS.REFRESH, on_click=lambda e: refresh_panel(), tooltip="Refresh"),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=20,
                width=850
            ),
            ft.Divider(),
            ft.Container(
                content=tabs,
                expand=True,
                width=850
            )
        ], 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True
        )
    )
    page.update()