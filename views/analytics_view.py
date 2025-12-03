"""
Analytics Dashboard View
========================
Displays comprehensive data visualizations and insights for admin users
"""

import flet as ft
from utils.config import ICONS, COLORS
from data.analytics import AnalyticsModel

def show_analytics_dashboard(page, user_id, role, name):
    """Display analytics dashboard with charts and insights"""
    
    # Only admin can access analytics
    if role != "admin":
        return
    
    def back_to_dashboard(e):
        from views.dashboard_view import show_dashboard
        show_dashboard(page, user_id, role, name)
    
    def refresh_dashboard(e):
        """Refresh all analytics data"""
        show_analytics_dashboard(page, user_id, role, name)
    
    # Fetch analytics data
    summary = AnalyticsModel.get_reservation_summary()
    status_data = AnalyticsModel.get_reservations_by_status()
    popular_rooms = AnalyticsModel.get_popular_classrooms(5)
    date_trends = AnalyticsModel.get_reservations_by_date(30)
    time_slots = AnalyticsModel.get_reservations_by_time_slot()
    faculty_activity = AnalyticsModel.get_faculty_activity()
    utilization = AnalyticsModel.get_classroom_utilization()
    approval_stats = AnalyticsModel.get_approval_rate()
    peak_hours = AnalyticsModel.get_peak_hours()
    
    # Summary Cards
    summary_cards = ft.Row([
        create_stat_card("Total Reservations", str(summary['total']), ICONS.CALENDAR_MONTH, "#2196F3"),
        create_stat_card("Pending", str(summary['pending']), ICONS.HOURGLASS_EMPTY, "#FF9800"),
        create_stat_card("Approved", str(summary['approved']), ICONS.CHECK_CIRCLE, "#4CAF50"),
        create_stat_card("Rejected", str(summary['rejected']), ICONS.CANCEL, "#F44336"),
    ], spacing=10, wrap=True)
    
    # Key Insights
    peak_hour_text = f"{peak_hours[0]['hour']}:00" if peak_hours else "N/A"
    approval_rate_text = f"{approval_stats['approval_rate']}%"
    most_popular_room = popular_rooms[0]['room_name'] if popular_rooms else "N/A"
    
    insights_cards = ft.Row([
        create_insight_card("Peak Hour", peak_hour_text, ICONS.ACCESS_TIME, "#9C27B0"),
        create_insight_card("Approval Rate", approval_rate_text, ICONS.THUMB_UP, "#00BCD4"),
        create_insight_card("Most Popular", most_popular_room, ICONS.STAR, "#FFC107"),
    ], spacing=10, wrap=True)
    
    page.controls.clear()
    page.add(
        ft.Column([
            # Header
            ft.Row([
                ft.Row([
                    ft.IconButton(icon=ICONS.ARROW_BACK, on_click=back_to_dashboard, tooltip="Back"),
                    ft.Text("Analytics Dashboard", size=24, weight=ft.FontWeight.BOLD),
                ]),
                ft.IconButton(icon=ICONS.REFRESH, on_click=refresh_dashboard, tooltip="Refresh Data"),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Divider(),
            
            # Summary Cards
            summary_cards,
            ft.Container(height=10),
            
            # Key Insights
            insights_cards,
            ft.Container(height=20),
            
            # Analytics Section Title
            ft.Text("Reservation Analytics", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            
            # Status Distribution
            create_status_table(status_data),
            ft.Container(height=20),
            
            # Popular Classrooms
            create_popular_rooms_table(popular_rooms),
            ft.Container(height=20),
            
            # Faculty Activity
            create_faculty_activity_table(faculty_activity),
            ft.Container(height=20),
            
            # Recent Trends
            create_trends_table(date_trends),
            ft.Container(height=20),
            
            # Time Slot Distribution
            create_time_slots_table(time_slots),
            ft.Container(height=20),
            
            # Utilization
            create_utilization_table(utilization),
            ft.Container(height=20),
            
        ], 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        scroll=ft.ScrollMode.ALWAYS,
        expand=True
        )
    )
    page.update()


def create_stat_card(title, value, icon, color):
    """Create a statistics card"""
    return ft.Container(
        content=ft.Row([
            ft.Icon(icon, size=40, color=color),
            ft.Column([
                ft.Text(title, size=12, color=COLORS.GREY if hasattr(COLORS, "GREY") else "grey"),
                ft.Text(value, size=24, weight=ft.FontWeight.BOLD),
            ], spacing=0)
        ], spacing=15),
        padding=20,
        border=ft.border.all(1, "#E0E0E0"),
        border_radius=10,
        width=250,
        bgcolor="white"
    )


def create_insight_card(title, value, icon, color):
    """Create an insight card"""
    return ft.Container(
        content=ft.Column([
            ft.Icon(icon, size=30, color=color),
            ft.Text(title, size=12, color=COLORS.GREY if hasattr(COLORS, "GREY") else "grey"),
            ft.Text(value, size=20, weight=ft.FontWeight.BOLD),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
        padding=20,
        border=ft.border.all(1, "#E0E0E0"),
        border_radius=10,
        width=250,
        bgcolor="white"
    )


def create_status_table(status_data):
    """Create table for status distribution"""
    if not status_data:
        return ft.Text("No data available", size=14, color="grey")
    
    status_colors = {
        'pending': '#FF9800',
        'approved': '#4CAF50',
        'rejected': '#F44336',
        'cancelled': '#9E9E9E'
    }
    
    rows = []
    total = sum(item['count'] for item in status_data)
    
    for item in status_data:
        percentage = (item['count'] / total * 100) if total > 0 else 0
        color = status_colors.get(item['status'], '#2196F3')
        
        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Container(
                        content=ft.Text(item['status'].title(), weight=ft.FontWeight.BOLD, color="white"),
                        bgcolor=color,
                        padding=5,
                        border_radius=5
                    )),
                    ft.DataCell(ft.Text(str(item['count']))),
                    ft.DataCell(ft.Text(f"{percentage:.1f}%")),
                    ft.DataCell(
                        ft.Container(
                            width=int(percentage * 2),
                            height=20,
                            bgcolor=color,
                            border_radius=3
                        )
                    ),
                ]
            )
        )
    
    return ft.Container(
        content=ft.Column([
            ft.Text("📊 Status Distribution", size=16, weight=ft.FontWeight.BOLD),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Status")),
                    ft.DataColumn(ft.Text("Count")),
                    ft.DataColumn(ft.Text("Percentage")),
                    ft.DataColumn(ft.Text("Visual")),
                ],
                rows=rows,
            ),
        ]),
        border=ft.border.all(1, "#E0E0E0"),
        border_radius=10,
        padding=15,
        bgcolor="white"
    )


def create_popular_rooms_table(popular_rooms):
    """Create table for popular classrooms"""
    if not popular_rooms:
        return ft.Text("No data available", size=14, color="grey")
    
    rows = []
    max_count = max(item['reservation_count'] for item in popular_rooms) if popular_rooms else 1
    
    for idx, item in enumerate(popular_rooms, 1):
        bar_width = int((item['reservation_count'] / max_count) * 200) if max_count > 0 else 0
        
        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(f"#{idx}")),
                    ft.DataCell(ft.Text(item['room_name'], weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Text(item['building'])),
                    ft.DataCell(ft.Text(str(item['reservation_count']))),
                    ft.DataCell(
                        ft.Container(
                            width=bar_width,
                            height=20,
                            bgcolor="#2196F3",
                            border_radius=3
                        )
                    ),
                ]
            )
        )
    
    return ft.Container(
        content=ft.Column([
            ft.Text("🏆 Most Popular Classrooms", size=16, weight=ft.FontWeight.BOLD),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Rank")),
                    ft.DataColumn(ft.Text("Room")),
                    ft.DataColumn(ft.Text("Building")),
                    ft.DataColumn(ft.Text("Reservations")),
                    ft.DataColumn(ft.Text("Popularity")),
                ],
                rows=rows,
            ),
        ]),
        border=ft.border.all(1, "#E0E0E0"),
        border_radius=10,
        padding=15,
        bgcolor="white"
    )


def create_faculty_activity_table(faculty_activity):
    """Create table for faculty activity"""
    if not faculty_activity:
        return ft.Text("No data available", size=14, color="grey")
    
    rows = []
    max_count = max(item['reservation_count'] for item in faculty_activity) if faculty_activity else 1
    
    for item in faculty_activity[:10]:  # Top 10
        bar_width = int((item['reservation_count'] / max_count) * 150) if max_count > 0 else 0
        
        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(item['full_name'])),
                    ft.DataCell(ft.Text(str(item['reservation_count']))),
                    ft.DataCell(
                        ft.Container(
                            width=bar_width,
                            height=20,
                            bgcolor="#9C27B0",
                            border_radius=3
                        )
                    ),
                ]
            )
        )
    
    return ft.Container(
        content=ft.Column([
            ft.Text("👥 Faculty Activity", size=16, weight=ft.FontWeight.BOLD),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Faculty Name")),
                    ft.DataColumn(ft.Text("Reservations")),
                    ft.DataColumn(ft.Text("Activity Level")),
                ],
                rows=rows,
            ),
        ]),
        border=ft.border.all(1, "#E0E0E0"),
        border_radius=10,
        padding=15,
        bgcolor="white"
    )


def create_trends_table(date_trends):
    """Create table for reservation trends"""
    if not date_trends:
        return ft.Text("No data available", size=14, color="grey")
    
    rows = []
    max_count = max(item['count'] for item in date_trends) if date_trends else 1
    
    # Show last 10 days
    for item in date_trends[-10:]:
        bar_width = int((item['count'] / max_count) * 150) if max_count > 0 else 0
        
        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(item['date']))),
                    ft.DataCell(ft.Text(str(item['count']))),
                    ft.DataCell(
                        ft.Container(
                            width=bar_width,
                            height=20,
                            bgcolor="#4CAF50",
                            border_radius=3
                        )
                    ),
                ]
            )
        )
    
    return ft.Container(
        content=ft.Column([
            ft.Text("📈 Recent Trends (Last 10 Days)", size=16, weight=ft.FontWeight.BOLD),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Date")),
                    ft.DataColumn(ft.Text("Reservations")),
                    ft.DataColumn(ft.Text("Volume")),
                ],
                rows=rows,
            ),
        ]),
        border=ft.border.all(1, "#E0E0E0"),
        border_radius=10,
        padding=15,
        bgcolor="white"
    )


def create_time_slots_table(time_slots):
    """Create table for time slot distribution"""
    if not time_slots:
        return ft.Text("No data available", size=14, color="grey")
    
    rows = []
    max_count = max(item['count'] for item in time_slots) if time_slots else 1
    
    for item in time_slots:
        bar_width = int((item['count'] / max_count) * 150) if max_count > 0 else 0
        hour_str = f"{item['hour']:02d}:00 - {item['hour']:02d}:59"
        
        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(hour_str)),
                    ft.DataCell(ft.Text(str(item['count']))),
                    ft.DataCell(
                        ft.Container(
                            width=bar_width,
                            height=20,
                            bgcolor="#FF9800",
                            border_radius=3
                        )
                    ),
                ]
            )
        )
    
    return ft.Container(
        content=ft.Column([
            ft.Text("⏰ Peak Hours Distribution", size=16, weight=ft.FontWeight.BOLD),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Time Slot")),
                    ft.DataColumn(ft.Text("Reservations")),
                    ft.DataColumn(ft.Text("Activity")),
                ],
                rows=rows,
            ),
        ]),
        border=ft.border.all(1, "#E0E0E0"),
        border_radius=10,
        padding=15,
        bgcolor="white"
    )


def create_utilization_table(utilization):
    """Create table for classroom utilization"""
    if not utilization:
        return ft.Text("No data available", size=14, color="grey")
    
    rows = []
    
    for item in utilization[:10]:  # Top 10
        approval_rate = (item['approved_reservations'] / item['total_reservations'] * 100) if item['total_reservations'] > 0 else 0
        
        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(item['room_name'])),
                    ft.DataCell(ft.Text(item['building'])),
                    ft.DataCell(ft.Text(str(item['total_reservations']))),
                    ft.DataCell(ft.Text(str(item['approved_reservations']))),
                    ft.DataCell(ft.Text(f"{approval_rate:.1f}%")),
                ]
            )
        )
    
    return ft.Container(
        content=ft.Column([
            ft.Text("📍 Classroom Utilization", size=16, weight=ft.FontWeight.BOLD),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Room")),
                    ft.DataColumn(ft.Text("Building")),
                    ft.DataColumn(ft.Text("Total")),
                    ft.DataColumn(ft.Text("Approved")),
                    ft.DataColumn(ft.Text("Rate")),
                ],
                rows=rows,
            ),
        ]),
        border=ft.border.all(1, "#E0E0E0"),
        border_radius=10,
        padding=15,
        bgcolor="white"
    )