import flet as ft
from data.models import ClassroomModel
from datetime import datetime

def show_classroom_schedule(page, classroom_id, room_name):
    """Display reservation schedule for a specific classroom"""
 
    # Fetch reservations for this classroom
    try:
        reservations = ClassroomModel.get_classroom_reservations(classroom_id)
    except Exception as e:
        reservations = []
        import traceback
        traceback.print_exc()
    
    # Status color mapping
    status_colors = {
        "approved": ft.Colors.GREEN,
        "pending": ft.Colors.ORANGE,
        "rejected": ft.Colors.RED
    }
    
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
                    ft.Text("Status", weight=ft.FontWeight.BOLD, size=14, expand=1),
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
            status = res.get("status", "unknown").lower()
            reserved_by = res.get("reserved_by", "Unknown")
            
            # Create status badge
            status_badge = ft.Container(
                content=ft.Text(
                    status.upper(),
                    size=10,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE
                ),
                bgcolor=status_colors.get(status, ft.Colors.GREY),
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                border_radius=5
            )
            
            # Add reservation row
            content_list.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(formatted_date, size=12, expand=2),
                        ft.Text(f"{start_time_str} - {end_time_str}", size=12, expand=2),
                        ft.Text(purpose, size=12, expand=3),
                        ft.Text(reserved_by, size=12, expand=2),
                        ft.Container(content=status_badge, expand=1),
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
                ft.Icon(ft.Icons.CALENDAR_MONTH, color=ft.Colors.BLUE),
                ft.Text(f"Schedule for {room_name}", size=20, weight=ft.FontWeight.BOLD)
            ],
            spacing=10
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