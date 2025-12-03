import flet as ft
from utils.config import ICONS, COLORS
from data.storage import get_user_reservations

def show_my_reservations(page, username, role, name):
    """Display faculty member's reservations"""
    
    if role != "faculty":
        return
    
    def back_to_dashboard(e):
        from views.dashboard_view import show_dashboard
        show_dashboard(page, username, role, name)
    
    reservations = get_user_reservations(username)
    
    # Create reservation cards
    reservation_cards = []
    if not reservations:
        reservation_cards.append(
            ft.Container(
                content=ft.Text("No reservations yet", color=COLORS.GREY if hasattr(COLORS, "GREY") else "grey"),
                padding=20
            )
        )
    else:
        for res in reservations:
            # Status color and icon
            status_config = {
                "pending": {"color": "orange", "icon": ICONS.HOURGLASS_EMPTY, "text": "Pending Approval"},
                "approved": {"color": COLORS.GREEN if hasattr(COLORS, "GREEN") else "green", "icon": ICONS.CHECK_CIRCLE, "text": "Approved"},
                "rejected": {"color": "red", "icon": ICONS.CANCEL, "text": "Rejected"}
            }
            config = status_config.get(res["status"], status_config["pending"])
            
            card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.ListTile(
                            leading=ft.Icon(ICONS.MEETING_ROOM),
                            title=ft.Text(res["classroom"], weight=ft.FontWeight.BOLD),
                            subtitle=ft.Text(f"{res['date']} • {res['start_time']} - {res['end_time']}"),
                        ),
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
                    ], spacing=0),
                    padding=10
                )
            )
            reservation_cards.append(card)
    
    page.controls.clear()
    page.add(
        ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.IconButton(icon=ICONS.ARROW_BACK, on_click=back_to_dashboard, tooltip="Back"),
                    ft.Text("My Reservations", size=24, weight=ft.FontWeight.BOLD),
                ]),
                padding=20,
                width=850
            ),
            ft.Divider(),
            ft.Column(
                reservation_cards,
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
                height=500
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )
    page.update()