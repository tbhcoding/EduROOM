import flet as ft
from data.models import ClassroomModel
from datetime import datetime
from utils.security import ensure_authenticated, touch_session, get_csrf_token

def show_classroom_schedule(page, classroom_id, room_name):
    """Display reservation schedule for a specific classroom"""
    
    # Session guard
    if not ensure_authenticated(page):
        return

    # Optional CSRF for approve/reject/cancel actions if you add them here
    # csrf_token = get_csrf_token(page)
 
    # Fetch reservations for this classroom
    try:
        reservations = ClassroomModel.get_classroom_reservations(classroom_id)
        
    except Exception as e:
        reservations = []
        import traceback
        traceback.print_exc()
    
    reservations = [r for r in reservations if r.get("status", "").lower() == "approved"]
    
    # Create content rows (simpler approach)
    content_list = []
    
    if reservations:
        # Add header
        content_list.append(
            ft.Container(
                content=ft.Row([
                    ft.Text("Date", weight=ft.FontWeight.BOLD, size=14, expand=2),
                    ft.Text("Time", weight=ft.FontWeight.BOLD, size=14, expand=2),
                    ft.Text("Purpose", weight=ft.FontWeight.BOLD, size=14, expand=3),
                    ft.Text("Reserved By", weight=ft.FontWeight.BOLD, size=14, expand=2),
                ]),
                bgcolor=ft.Colors.GREY_200,
                padding=10,
                border_radius=5
            )
        )
        
        for res in reservations:
            # Format date
            res_date = res.get("reservation_date", "")
            if isinstance(res_date, str):
                try:
                    date_obj = datetime.strptime(res_date, "%Y-%m-%d")
                    formatted_date = date_obj.strftime("%b %d, %Y")
                except:
                    formatted_date = res_date
            else:
                try:
                    formatted_date = res_date.strftime("%b %d, %Y")
                except:
                    formatted_date = str(res_date)
            
            # Format time (handle timedelta objects from database)
            start_time = res.get("start_time", "")
            end_time = res.get("end_time", "")
            
            # Convert timedelta to time string if needed
            def format_time(time_value):
                if isinstance(time_value, str):
                    return time_value
                else:
                    try:
                        # timedelta object - convert to hours:minutes
                        total_seconds = int(time_value.total_seconds())
                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60
                        return f"{hours:02d}:{minutes:02d}"
                    except:
                        return str(time_value)
            
            start_time_str = format_time(start_time)
            end_time_str = format_time(end_time)
            
            purpose = res.get("purpose", "N/A")
            reserved_by = res.get("reserved_by", "Unknown")
            border_radius=5

            # Add reservation row
            content_list.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(formatted_date, size=12, expand=2),
                        ft.Text(f"{start_time_str} - {end_time_str}", size=12, expand=2),
                        ft.Text(purpose, size=12, expand=3),
                        ft.Text(reserved_by, size=12, expand=2),
                    ]),
                    padding=10,
                    border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_300))
                )
            )
    else:
        # No reservations message
        content_list.append(
            ft.Container(
                content=ft.Text(
                    "No reservations found for this classroom",
                    size=14,
                    italic=True,
                    color=ft.Colors.GREY_600
                ),
                padding=20,
                alignment=ft.alignment.center
            )
        )
    
    # Create scrollable container
    schedule_content = ft.Container(
        content=ft.Column(
            controls=content_list,
            scroll=ft.ScrollMode.AUTO,
        ),
        height=400,
        border=ft.border.all(1, ft.Colors.GREY_300),
        border_radius=10,
        padding=10
    )
    
    # Create dialog with close function
    def close_dialog(e):
        dialog.open = False
        page.update()
    
    # Create dialog
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            [
                ft.Text(f"Schedule for {room_name}", size=20, weight=ft.FontWeight.BOLD)
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.CENTER
        ),
        content=ft.Container(
            content=schedule_content,
            width=700,
            padding=10
        ),
        actions=[
            ft.TextButton("Close", on_click=close_dialog)
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )
    
    page.open(dialog)