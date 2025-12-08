import flet as ft
from utils.config import ICONS, COLORS
from data.models import ClassroomModel, ReservationModel, ActivityLogModel
from datetime import datetime
from components.app_header import create_app_header
from components.datetime_picker import DateTimePicker

def show_reservation_form(page, user_id, role, name, classroom_id):
    """Display the reservation form for faculty to book classrooms"""
    
    # Create the header and drawer
    header, drawer = create_app_header(page, user_id, role, name, current_page="reservations")

    # Only faculty can make reservations
    if role != "faculty":
        return
    
    classroom = ClassroomModel.get_classroom_by_id(classroom_id)
    if not classroom:
        return
    
    # Create datetime picker instance
    datetime_picker = DateTimePicker(page)
    
    # Reference for occupied slots display
    occupied_slots_ref = ft.Ref[ft.Column]()
    occupied_container_ref = ft.Ref[ft.Container]()
    
    def load_occupied_slots(selected_date=None):
        """Load and display occupied time slots for selected date"""
        if not selected_date:
            occupied_slots_ref.current.controls = []
            occupied_container_ref.current.visible = False
            page.update()
            return
        
        date_str = selected_date.strftime('%Y-%m-%d')
        occupied = ReservationModel.get_occupied_slots(classroom_id, date_str)
        
        if not occupied:
            occupied_slots_ref.current.controls = [
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, size=16, color="#4CAF50"),
                        ft.Text("No reservations on this date - all slots available!", 
                               size=13, color="#2E7D32", weight=ft.FontWeight.W_500)
                    ], spacing=8),
                    padding=10,
                    bgcolor="#E8F5E9",
                    border_radius=8,
                )
            ]
        else:
            slot_items = []
            for slot in occupied:
                status_color = "#FF9800" if slot["status"] == "pending" else "#4CAF50"
                status_bg = "#FFF3E0" if slot["status"] == "pending" else "#E8F5E9"
                slot_items.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Icon(ft.Icons.SCHEDULE, size=16, color=status_color),
                                width=30,
                            ),
                            ft.Column([
                                ft.Text(
                                    f"{str(slot['start_time'])[:5]} - {str(slot['end_time'])[:5]}",
                                    size=13,
                                    weight=ft.FontWeight.BOLD,
                                    color="#212121"
                                ),
                            ], spacing=2, alignment=ft.MainAxisAlignment.CENTER),
                        ], spacing=10, alignment=ft.MainAxisAlignment.START),
                        padding=5,
                        bgcolor=status_bg,
                        border_radius=8,
                    )
                )
            occupied_slots_ref.current.controls = slot_items
        
        occupied_container_ref.current.visible = True
        page.update()
    
    def on_date_selected(date):
        """When user selects a date, show occupied slots and update button text"""
        # Update date button text
        date_text_ref.current.value = date.strftime('%B %d, %Y')
        date_text_ref.current.color = "#212121"
        date_icon_ref.current.color = "#4A7BA7"
        page.update()
        load_occupied_slots(date)
    
    def on_start_time_selected(start_time):
        """When user selects start time, update button text"""
        start_time_text_ref.current.value = start_time
        start_time_text_ref.current.color = "#212121"
        start_time_icon_ref.current.color = "#4A7BA7"
        page.update()
    
    def on_end_time_selected(end_time):
        """When user selects end time, update button text"""
        end_time_text_ref.current.value = end_time
        end_time_text_ref.current.color = "#212121"
        end_time_icon_ref.current.color = "#4A7BA7"
        page.update()
    
    purpose = ft.TextField(
        label="Purpose", 
        hint_text="Enter the purpose of your reservation",
        multiline=True, 
        width=450,
        min_lines=3,
        max_lines=5,
        border_radius=10,
        text_size=14,
        border_color="#E0E0E0",
        focused_border_color="#4A7BA7",
        filled=True,
        bgcolor="#FAFAFA",
    )
    
    success_text = ft.Text("", size=13, weight=ft.FontWeight.W_500)
    availability_text = ft.Text("", size=13, weight=ft.FontWeight.W_500)
    submit_button_ref = ft.Ref[ft.ElevatedButton]()
    
    def validate_availability(date, start_time, end_time):
        """Validate if the selected time slot is available"""
        # Format date for database
        date_str = date.strftime('%Y-%m-%d')
        
        # Check availability
        is_available = ReservationModel.check_availability(
            classroom_id,
            date_str,
            start_time,
            end_time
        )
        
        if not is_available:
            availability_text.value = "⚠  This time slot is already booked! Please select a different time."
            availability_text.color = "#D32F2F"
            submit_button_ref.current.disabled = True
            page.update()
            return False
        else:
            availability_text.value = "✓  Time slot is available for booking"
            availability_text.color = "#2E7D32"
            page.update()
            return True
    
    def check_form_ready(*args):
        """Enable submit button when all fields are filled"""
        if datetime_picker.is_complete() and purpose.value:
            # Only enable if availability check passed
            values = datetime_picker.get_values()
            if values:
                is_available = validate_availability(
                    values["date"],
                    values["start_time"],
                    values["end_time"]
                )
                submit_button_ref.current.disabled = not is_available
        else:
            submit_button_ref.current.disabled = True
        page.update()
    
    def purpose_changed(e):
        """Handle purpose field changes"""
        check_form_ready()
    
    purpose.on_change = purpose_changed
    
    def submit_reservation(e):
        # Validate all fields
        if not datetime_picker.is_complete() or not purpose.value:
            success_text.value = "⚠  Please fill all required fields"
            success_text.color = "#D32F2F"
            page.update()
            return
        
        values = datetime_picker.get_values()
        
        # Format date for database (convert datetime to string)
        date_str = values["date"].strftime('%Y-%m-%d')
        
        # Double-check availability before submitting
        is_available = ReservationModel.check_availability(
            classroom_id,
            date_str,
            values["start_time"],
            values["end_time"]
        )
        
        if not is_available:
            success_text.value = "⚠  This time slot was just booked by someone else!"
            success_text.color = "#D32F2F"
            page.update()
            return
        
        # Create reservation in database
        reservation_id = ReservationModel.create_reservation(
            classroom_id,
            user_id,
            date_str,
            values["start_time"],
            values["end_time"],
            purpose.value
        )
        
        if reservation_id:
            # Log activity
            ActivityLogModel.log_activity(
                user_id, 
                "Created reservation", 
                f"Reserved {classroom['room_name']} on {date_str}"
            )
            
            # Navigate back to dashboard
            from views.dashboard_view import show_dashboard
            show_dashboard(page, user_id, role, name)
        else:
            success_text.value = "⚠  Failed to create reservation. Please try again."
            success_text.color = "#D32F2F"
            page.update()
    
    def back_to_dashboard(e):
        from views.dashboard_view import show_dashboard
        show_dashboard(page, user_id, role, name)
    
    # Set up datetime picker callbacks
    datetime_picker.set_callbacks(
        on_date_change=on_date_selected,      # Show occupied slots when date selected
        on_start_time_change=on_start_time_selected,  # Update start time button
        on_end_time_change=on_end_time_selected,      # Update end time button
        on_validation=validate_availability,  # Validate when all selected
        on_all_selected=check_form_ready      # Enable submit when all filled
    )
    
    # Create custom styled picker buttons with text refs
    date_text_ref = ft.Ref[ft.Text]()
    date_icon_ref = ft.Ref[ft.Icon]()
    start_time_text_ref = ft.Ref[ft.Text]()
    start_time_icon_ref = ft.Ref[ft.Icon]()
    end_time_text_ref = ft.Ref[ft.Text]()
    end_time_icon_ref = ft.Ref[ft.Icon]()
    
    date_button = ft.Container(
        ref=datetime_picker.date_button_ref,
        content=ft.Row([
            ft.Icon(ft.Icons.CALENDAR_TODAY_ROUNDED, size=20, color=ft.Colors.GREY_600, ref=date_icon_ref),
            ft.Text("Select Date", size=15, color=ft.Colors.GREY_600, ref=date_text_ref, weight=ft.FontWeight.W_500),
        ], spacing=12),
        padding=ft.padding.symmetric(horizontal=20, vertical=16),
        border=ft.border.all(2, "#E0E0E0"),
        border_radius=10,
        bgcolor="#FAFAFA",
        on_click=datetime_picker.open_date_picker,
        ink=True,
        width=450,
    )
    
    start_time_button = ft.Container(
        ref=datetime_picker.start_time_button_ref,
        content=ft.Row([
            ft.Icon(ft.Icons.ACCESS_TIME_ROUNDED, size=20, color=ft.Colors.GREY_600, ref=start_time_icon_ref),
            ft.Text("Start Time", size=15, color=ft.Colors.GREY_600, ref=start_time_text_ref, weight=ft.FontWeight.W_500),
        ], spacing=10),
        padding=ft.padding.symmetric(horizontal=18, vertical=16),
        border=ft.border.all(2, "#E0E0E0"),
        border_radius=10,
        bgcolor="#FAFAFA",
        on_click=datetime_picker.open_start_time_picker,
        ink=True,
        width=210,
    )
    
    end_time_button = ft.Container(
        ref=datetime_picker.end_time_button_ref,
        content=ft.Row([
            ft.Icon(ft.Icons.ACCESS_TIME_ROUNDED, size=20, color=ft.Colors.GREY_600, ref=end_time_icon_ref),
            ft.Text("End Time", size=15, color=ft.Colors.GREY_600, ref=end_time_text_ref, weight=ft.FontWeight.W_500),
        ], spacing=10),
        padding=ft.padding.symmetric(horizontal=18, vertical=16),
        border=ft.border.all(2, "#E0E0E0"),
        border_radius=10,
        bgcolor="#FAFAFA",
        on_click=datetime_picker.open_end_time_picker,
        ink=True,
        width=210,
    )
    
    # Store text refs in datetime_picker so it can update them
    datetime_picker.date_text_ref = date_text_ref
    datetime_picker.start_time_text_ref = start_time_text_ref
    datetime_picker.end_time_text_ref = end_time_text_ref
    
    page.controls.clear()
    page.add(
        ft.Column([
            header,
            ft.Column([
                # Main card container
                ft.Container(
                    content=ft.Column([
                        # Back button
                        ft.Container(
                            content=ft.Row([
                                ft.IconButton(
                                    icon=ICONS.ARROW_BACK,
                                    icon_size=24,
                                    on_click=back_to_dashboard,
                                    tooltip="Back to Dashboard",
                                    style=ft.ButtonStyle(
                                        color="#616161",
                                    )
                                ),
                            ]),
                            margin=ft.margin.only(bottom=10)
                        ),
                        
                        # Header section with improved spacing
                        ft.Column([
                            ft.Text(
                                f"Reserve {classroom['room_name']}", 
                                size=32, 
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER,
                                color="#212121"
                            ),
                            
                            ft.Container(height=5),
                            
                            ft.Row([
                                ft.Text(
                                    classroom['building'], 
                                    size=15,
                                    color="#757575",
                                    weight=ft.FontWeight.W_500
                                ),
                                ft.Container(
                                    content=ft.Text("•", color="#757575"),
                                    padding=ft.padding.symmetric(horizontal=5)
                                ),
                                ft.Text(
                                    f"Capacity: {classroom['capacity']}", 
                                    size=15,
                                    color="#757575",
                                    weight=ft.FontWeight.W_500
                                ),
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                        
                        ft.Container(height=20),
                        
                        # Warning banner with improved design
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ICONS.WARNING, color="#F57C00", size=20),
                                ft.Text(
                                    "Reservation requires admin approval",
                                    size=14,
                                    color="#E65100",
                                    weight=ft.FontWeight.W_500
                                )
                            ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
                            padding=15,
                            border_radius=10,
                            width=450
                        ),
                        
                        ft.Container(height=30),
                        
                        # Date section
                        ft.Column([
                            ft.Row([
                                ft.Text("Date", size=13, weight=ft.FontWeight.BOLD, color="#424242"),
                                ft.Text("*", size=13, color="#D32F2F"),
                            ], spacing=2),
                            ft.Container(height=8),
                            date_button,
                        ], spacing=0),
                        
                        # Occupied slots display with improved design
                        ft.Container(
                            ref=occupied_container_ref,
                            content=ft.Column([
                                ft.Row([
                                    ft.Text("Reserved Time Slots", size=14, weight=ft.FontWeight.BOLD, color="#424242")
                                ], spacing=8),
                                ft.Container(height=8),
                                ft.Column(
                                    ref=occupied_slots_ref,
                                    controls=[],
                                    spacing=8
                                ),
                            ], spacing=0),
                            padding=ft.padding.all(18),
                            bgcolor="#F5F5F5",
                            border_radius=10,
                            width=450,
                            visible=False,
                        ),
                        
                        ft.Container(height=25),
                        
                        # Time section
                        ft.Column([
                            ft.Row([
                                ft.Text("Time Range", size=13, weight=ft.FontWeight.BOLD, color="#424242"),
                                ft.Text("*", size=13, color="#D32F2F"),
                            ], spacing=2),
                            ft.Container(height=8),
                            ft.Row([
                                start_time_button,
                                end_time_button
                            ], spacing=30, alignment=ft.MainAxisAlignment.START),
                        ], spacing=0),
                        
                        # Availability message with better styling
                        ft.Container(
                            content=availability_text,
                            padding=ft.padding.only(top=12),
                            width=450
                        ),
                        
                        ft.Container(height=25),
                        
                        # Purpose section
                        ft.Column([
                            ft.Row([
                                ft.Text("Purpose", size=13, weight=ft.FontWeight.BOLD, color="#424242"),
                                ft.Text("*", size=13, color="#D32F2F"),
                            ], spacing=2),
                            ft.Container(height=8),
                            purpose,
                        ], spacing=0),
                        
                        ft.Container(
                            content=success_text,
                            padding=ft.padding.only(top=5)
                        ),
                        
                        ft.Container(height=30),
                        
                        # Submit button with improved styling
                        ft.ElevatedButton(
                            ref=submit_button_ref,
                            content=ft.Row([
                                ft.Text("Submit Reservation", size=16, weight=ft.FontWeight.BOLD)
                            ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
                            width=450,
                            height=56,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=10),
                                bgcolor={
                                    ft.ControlState.DEFAULT: "#4A7BA7",
                                    ft.ControlState.HOVERED: "#3D6A93",
                                    ft.ControlState.DISABLED: "#BDBDBD",
                                },
                                color={
                                    ft.ControlState.DEFAULT: "#FFFFFF",
                                    ft.ControlState.DISABLED: "#757575",
                                },
                            ),
                            on_click=submit_reservation,
                            disabled=True
                        ),
                        
                    ], 
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    spacing=0),
                    padding=30,
                    margin=ft.margin.symmetric(vertical=20, horizontal=20),
                    bgcolor="#FFFFFF",
                    border_radius=15,
                    shadow=ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=20,
                        color=ft.Colors.with_opacity(0.1, "#000000"),
                        offset=ft.Offset(0, 4),
                    ),
                    width=510,
                ),
                
                # Bottom padding for scroll
                ft.Container(height=40),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        ], spacing=0, expand=True)
    )
    page.update()