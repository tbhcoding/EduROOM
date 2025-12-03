import flet as ft
from utils.config import ICONS, COLORS
from data.storage import get_all_reservations, approve_reservation, reject_reservation

def show_admin_panel(page, username, role, name):
    """Display admin panel for managing reservations"""
    
    if role != "admin":
        return
    
    def back_to_dashboard(e):
        from views.dashboard_view import show_dashboard
        show_dashboard(page, username, role, name)
    
    def refresh_panel():
        """Refresh the admin panel to show updated data"""
        show_admin_panel(page, username, role, name)
    
    def handle_approve(reservation_id):
        approve_reservation(reservation_id)
        refresh_panel()
    
    def handle_reject(reservation_id):
        reject_reservation(reservation_id)
        refresh_panel()
    
    reservations = get_all_reservations()
    pending = [r for r in reservations if r["status"] == "pending"]
    approved = [r for r in reservations if r["status"] == "approved"]
    rejected = [r for r in reservations if r["status"] == "rejected"]
    
    def create_reservation_card(res, show_actions=True):
        """Create a reservation card with optional approve/reject buttons"""
        
        status_config = {
            "pending": {"color": "orange", "icon": ICONS.HOURGLASS_EMPTY},
            "approved": {"color": COLORS.GREEN if hasattr(COLORS, "GREEN") else "green", "icon": ICONS.CHECK_CIRCLE},
            "rejected": {"color": "red", "icon": ICONS.CANCEL}
        }
        config = status_config.get(res["status"], status_config["pending"])
        
        card_content = [
            ft.ListTile(
                leading=ft.Icon(ICONS.MEETING_ROOM),
                title=ft.Text(res["classroom"], weight=ft.FontWeight.BOLD),
                subtitle=ft.Text(f"By: {res['user']} • {res['date']} • {res['start_time']}-{res['end_time']}"),
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
                            on_click=lambda e, rid=res["id"]: handle_approve(rid)
                        ),
                        ft.OutlinedButton(
                            "Reject",
                            icon=ICONS.CLOSE,
                            on_click=lambda e, rid=res["id"]: handle_reject(rid)
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
    
    # Create tabs for different sections
    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(
                text=f"Pending ({len(pending)})",
                icon=ICONS.PENDING,
                content=ft.Container(
                    content=ft.Column([
                        ft.Column(
                            [create_reservation_card(r, show_actions=True) for r in pending] if pending 
                            else [ft.Container(
                                content=ft.Text("No pending reservations", color=COLORS.GREY if hasattr(COLORS, "GREY") else "grey"),
                                padding=20
                            )],
                            spacing=10,
                            scroll=ft.ScrollMode.AUTO
                        )
                    ]),
                    padding=10
                )
            ),
            ft.Tab(
                text=f"Approved ({len(approved)})",
                icon=ICONS.CHECK_CIRCLE,
                content=ft.Container(
                    content=ft.Column([
                        ft.Column(
                            [create_reservation_card(r, show_actions=False) for r in approved] if approved
                            else [ft.Container(
                                content=ft.Text("No approved reservations", color=COLORS.GREY if hasattr(COLORS, "GREY") else "grey"),
                                padding=20
                            )],
                            spacing=10,
                            scroll=ft.ScrollMode.AUTO
                        )
                    ]),
                    padding=10
                )
            ),
            ft.Tab(
                text=f"Rejected ({len(rejected)})",
                icon=ICONS.CANCEL,
                content=ft.Container(
                    content=ft.Column([
                        ft.Column(
                            [create_reservation_card(r, show_actions=False) for r in rejected] if rejected
                            else [ft.Container(
                                content=ft.Text("No rejected reservations", color=COLORS.GREY if hasattr(COLORS, "GREY") else "grey"),
                                padding=20
                            )],
                            spacing=10,
                            scroll=ft.ScrollMode.AUTO
                        )
                    ]),
                    padding=10
                )
            ),
        ],
        expand=1
    )
    
    page.controls.clear()
    page.add(
        ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.IconButton(icon=ICONS.ARROW_BACK, on_click=back_to_dashboard, tooltip="Back"),
                    ft.Text("Admin Panel - Manage Reservations", size=24, weight=ft.FontWeight.BOLD),
                ]),
                padding=20,
                width=850
            ),
            ft.Divider(),
            ft.Container(
                content=tabs,
                height=500,
                width=850
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )
    page.update()