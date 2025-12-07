import flet as ft
import datetime
from utils.config import ICONS, COLORS
from data.models import ClassroomModel, ReservationModel
from views.schedule_view import show_classroom_schedule
from components.app_header import create_app_header

def show_dashboard(page, user_id, role, name):
    """Display main dashboard with availability filtering"""

    # Auto-update reservation statuses (approved → ongoing → done)
    try:
        ReservationModel.update_reservation_statuses()
    except Exception:
        pass  # Silently fail if database is unavailable

    # Create header with photo
    header, drawer = create_app_header(page, user_id, role, name, current_page="classrooms")
    # State variables
    all_classrooms = []
    current_classrooms = [] 
    filtered_by_availability = False
    current_search_query = ""
    selected_date = None
    selected_start_time = None
    selected_end_time = None
    

    def open_reservation_form(classroom_id):
        from views.reservation_view import show_reservation_form
        page.controls.clear()
        page.overlay.clear()
        page.update()
        show_reservation_form(page, user_id, role, name, classroom_id)

    # Get classrooms from database
    try:
        all_classrooms = ClassroomModel.get_all_classrooms() or []
    except Exception:
        all_classrooms = []

    # Search and filter state
    search_query = ft.Ref[ft.TextField]()
    classroom_list_ref = ft.Ref[ft.Column]()
    result_count_ref = ft.Ref[ft.Text]()
    date_button_ref = ft.Ref[ft.Container]()
    start_time_button_ref = ft.Ref[ft.Container]()
    end_time_button_ref = ft.Ref[ft.Container]()
    apply_button_ref = ft.Ref[ft.ElevatedButton]()

    def create_classroom_card(room):
        """Helper function to create a classroom card"""
        status_color = COLORS.GREEN if room.get("status") == "Available" else "orange"
        image_src = room.get("image_url") or "../assets/images/classroom-default.png"

        def view_schedule_click(e):
            show_classroom_schedule(page, room["id"], room.get("room_name", "Unnamed Room"))

        reserve_enabled = (role == "faculty") and (room.get("status") == "Available")

        def on_reserve_click(e):
            open_reservation_form(room["id"])

        reserve_btn = ft.ElevatedButton(
            "Reserve",
            on_click=on_reserve_click,
            disabled=not reserve_enabled,
            height=35,
            expand=True
        )

        if role in ("admin", "student"):
            reserve_btn = ft.ElevatedButton(
                "Reserve",
                disabled=True,
                height=35,
                expand=True
            )

        schedule_btn = ft.OutlinedButton(
            "View Schedule",
            on_click=view_schedule_click,
            height=35,
            expand=True
        )

        return ft.Card(
            width=320,
            elevation=3,
            content=ft.Container(
                padding=0,
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Image(
                                src=image_src,
                                fit=ft.ImageFit.COVER,
                                width=None,
                                height=200,
                            ),
                            border_radius=ft.border_radius.only(
                                top_left=8, top_right=8
                            ),
                            clip_behavior=ft.ClipBehavior.ANTI_ALIAS
                        ),
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=12, vertical=8),
                            content=ft.Column(
                                [
                                    ft.Text(
                                        room.get("room_name", "Unnamed Room"),
                                        weight=ft.FontWeight.BOLD,
                                        size=14
                                    ),
                                    ft.Text(
                                        f"{room.get('building','')} • Capacity: {room.get('capacity','-')}",
                                        size=11,
                                        color=ft.Colors.GREY_600
                                    ),
                                    ft.Text(
                                        room.get("status", "Unknown"),
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                        color=status_color
                                    ),
                                ],
                                spacing=3
                            )
                        ),
                        ft.Container(
                            padding=ft.padding.all(12),
                            content=ft.Row(
                                [schedule_btn, reserve_btn],
                                spacing=10,
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        )
                    ],
                    tight=True,
                    spacing=0
                )
            )
        )

    def matches_search(text, query):
        """Check if query appears in text"""
        if not query:
            return True
        return query.lower() in text.lower()
    
    def apply_filters(classrooms_to_filter):
        """Apply search query to classroom list"""
        query = current_search_query.strip()
        filtered_cards = []
        
        for room in classrooms_to_filter:
            room_name = room.get("room_name", "")
            building = room.get("building", "")
            capacity = str(room.get("capacity", ""))
            status = room.get("status", "")
            
            searchable_text = f"{room_name} {building} {capacity} {status}"
            
            if matches_search(searchable_text, query):
                filtered_cards.append(create_classroom_card(room))
        
        return filtered_cards
    
    def update_classroom_display(classrooms_to_show):
        """Update the classroom grid with filtered results"""
        filtered_cards = apply_filters(classrooms_to_show)
        
        # Update result count
        result_count_ref.current.value = f"Showing {len(filtered_cards)} classroom(s)"
        
        if not filtered_cards:
            classroom_list_ref.current.controls = [
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.SEARCH_OFF, size=64, color=ft.Colors.GREY_400),
                        ft.Text(
                            "No classrooms found",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_600
                        ),
                        ft.Text(
                            "Try adjusting your search or filter criteria",
                            size=14,
                            color=ft.Colors.GREY_500,
                            italic=True
                        )
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=40,
                    alignment=ft.alignment.center
                )
            ]
        else:
            classroom_list_ref.current.controls = create_grid_rows(filtered_cards)
        
        page.update()
    
    def filter_by_availability(reservation_date, start_time, end_time):
        """Filter classrooms by availability on specific date/time"""
        nonlocal filtered_by_availability, current_classrooms
        filtered_by_availability = True
        
        try:
            # Get available classrooms from database
            available_classrooms = ReservationModel.get_available_classrooms(
                reservation_date,
                start_time,
                end_time
            )
            
            # Update current classrooms to the filtered set
            current_classrooms = available_classrooms
            update_classroom_display(current_classrooms) 
            
        except Exception as e:
            show_snackbar("Error loading available classrooms")
    
    def clear_availability_filter():
        """Clear availability filter and show all classrooms"""
        nonlocal filtered_by_availability, selected_date, selected_start_time, selected_end_time, current_classrooms
        filtered_by_availability = False
        selected_date = None
        selected_start_time = None
        selected_end_time = None
        current_classrooms = all_classrooms
        
        # Reset button texts
        date_button_ref.current.content.value = "Select Date"
        start_time_button_ref.current.content.value = "Start Time"
        end_time_button_ref.current.content.value = "End Time"
        apply_button_ref.current.disabled = True
        
        update_classroom_display(current_classrooms)
    
    def handle_date_change(e):
        """Handle date picker selection"""
        nonlocal selected_date
        selected_date = e.control.value
        date_button_ref.current.content.value = selected_date.strftime('%m/%d/%Y')
        check_filter_ready()
        page.update()
    
    def handle_start_time_change(e):
        """Handle start time picker selection"""
        nonlocal selected_start_time
        selected_start_time = e.control.value
        start_time_button_ref.current.content.value = selected_start_time
        check_filter_ready()
        page.update()
    
    def handle_end_time_change(e):
        """Handle end time picker selection"""
        nonlocal selected_end_time
        selected_end_time = e.control.value
        end_time_button_ref.current.content.value = selected_end_time
        check_filter_ready()
        page.update()
    
    def check_filter_ready():
        """Enable apply button when all filters are selected"""
        if selected_date and selected_start_time and selected_end_time:
            apply_button_ref.current.disabled = False
        else:
            apply_button_ref.current.disabled = True
        page.update()
    
    def open_date_picker(e):
        """Open the date picker dialog"""
        page.open(
            ft.DatePicker(
                first_date=datetime.datetime.now(),
                last_date=datetime.datetime.now() + datetime.timedelta(days=365),
                on_change=handle_date_change
            )
        )
    
    def open_start_time_picker(e):
        """Open the start time picker dialog"""
        page.open(
            ft.TimePicker(
                on_change=handle_start_time_change
            )
        )
    
    def open_end_time_picker(e):
        """Open the end time picker dialog"""
        page.open(
            ft.TimePicker(
                on_change=handle_end_time_change
            )
        )
    
    def apply_filter_click(e):
        """Apply the availability filter"""
        if selected_date and selected_start_time and selected_end_time:
            filter_by_availability(selected_date, selected_start_time, selected_end_time)
    
    def clear_filter_click(e):
        """Clear the availability filter"""
        clear_availability_filter()
    
    def search_classrooms(e):
        """Handle search query changes"""
        nonlocal current_search_query
        current_search_query = search_query.current.value.strip()
        
        # Apply search to current classroom list (filtered or all)
        update_classroom_display(current_classrooms)

    # Initialize current_classrooms at the start
    current_classrooms = all_classrooms 
    
    def show_snackbar(message):
        page.open(ft.SnackBar(content=ft.Text(message)))
        page.update()

    def create_grid_rows(cards):
        """Organize cards into rows of 3"""
        rows = []
        for i in range(0, len(cards), 3):
            row_cards = cards[i:i+3]
            rows.append(
                ft.Row(
                    controls=row_cards,
                    spacing=20,
                    alignment=ft.MainAxisAlignment.CENTER,
                    wrap=False
                )
            )
        return rows

    # Create dropdown-style picker buttons
    date_picker_button = ft.Container(
        ref=date_button_ref,
        content=ft.Text("Select Date", size=14),
        padding=ft.padding.symmetric(horizontal=15, vertical=12),
        border=ft.border.all(1, ft.Colors.GREY_400),
        border_radius=8,
        bgcolor=ft.Colors.WHITE,
        on_click=open_date_picker,
        ink=True,
        width=180
    )
    
    start_time_button = ft.Container(
        ref=start_time_button_ref,
        content=ft.Text("Start Time", size=14),
        padding=ft.padding.symmetric(horizontal=15, vertical=12),
        border=ft.border.all(1, ft.Colors.GREY_400),
        border_radius=8,
        bgcolor=ft.Colors.WHITE,
        on_click=open_start_time_picker,
        ink=True,
        width=150
    )
    
    end_time_button = ft.Container(
        ref=end_time_button_ref,
        content=ft.Text("End Time", size=14),
        padding=ft.padding.symmetric(horizontal=15, vertical=12),
        border=ft.border.all(1, ft.Colors.GREY_400),
        border_radius=8,
        bgcolor=ft.Colors.WHITE,
        on_click=open_end_time_picker,
        ink=True,
        width=150
    )
    
    apply_button = ft.ElevatedButton(
        ref=apply_button_ref,
        text="Apply",
        icon=ft.Icons.CHECK,
        on_click=apply_filter_click,
        disabled=True,
        height=45,
        bgcolor=ft.Colors.BLUE,
        color=ft.Colors.WHITE,
    )
    
    clear_button = ft.OutlinedButton(
        text="Clear",
        icon=ft.Icons.CLEAR,
        on_click=clear_filter_click,
        height=45,
    )

    # Initial classroom display
    classroom_cards = [create_classroom_card(room) for room in all_classrooms]
    grid_rows = create_grid_rows(classroom_cards)

    # Build page layout
    page.controls.clear()
    page.add(
        ft.Column([
            header,
            ft.Container(
                content=ft.Text("Available Classrooms", size=32, font_family="Montserrat Bold", weight=ft.FontWeight.BOLD),
                padding=ft.padding.only(left=30, top=20), 
                alignment=ft.alignment.center
            ),
            ft.Container(height=10),
            # Search bar
            ft.Container(
                content=ft.TextField(
                    ref=search_query,
                    hint_text="Search by name, building, capacity...",
                    prefix_icon=ft.Icons.SEARCH,
                    on_change=search_classrooms,
                    border_radius=10,
                ),
                padding=ft.padding.symmetric(horizontal=30),
            ),
            ft.Container(height=10),
            # Filter bar
            ft.Container(
                content=ft.Card(
                    elevation=2,
                    content=ft.Container(
                        padding=ft.padding.all(20),
                        content=ft.Row([
                            ft.Icon(ft.Icons.FILTER_LIST, size=20, color=ft.Colors.GREY_700),
                            date_picker_button,
                            start_time_button,
                            end_time_button,
                            apply_button,
                            clear_button
                        ], 
                        spacing=15, 
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER)
                    )
                ),
                padding=ft.padding.symmetric(horizontal=30)
            ),
            # Result count
            ft.Container(
                content=ft.Text(
                    ref=result_count_ref,
                    value=f"Showing {len(all_classrooms)} classroom(s)",
                    size=13,
                    color=ft.Colors.GREY_600
                ),
                padding=ft.padding.symmetric(horizontal=30, vertical=10)
            ),
            # Scrollable classroom grid
            ft.Container(
                content=ft.Column(
                    ref=classroom_list_ref,
                    controls=grid_rows,
                    spacing=20,
                    scroll=ft.ScrollMode.AUTO
                ),
                padding=ft.padding.symmetric(horizontal=30),
                expand=True
            )
        ], spacing=0, expand=True)
    )
    page.update()