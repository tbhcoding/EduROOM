"""
Analytics Dashboard View
========================
Displays comprehensive data visualizations and insights for admin users
"""

import flet as ft
from utils.config import ICONS, COLORS
from data.analytics import AnalyticsModel
from components.app_header import create_app_header
from utils.security import ensure_authenticated, get_csrf_token, touch_session

def show_analytics_dashboard(page, user_id, role, name):
    """Display analytics dashboard with charts and insights"""
    
    # Session guard
    if not ensure_authenticated(page):
        return
    
    # Only admin can access analytics
    if role != "admin":
        return
    
    # Create the header and drawer
    header, drawer = create_app_header(page, user_id, role, name, current_page="analytics")

    # Optional
    # csrf_token = get_csrf_token(page)
    
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
    
    # Fetch derived insights
    weekly_comparison = AnalyticsModel.get_weekly_comparison()
    busiest_day = AnalyticsModel.get_busiest_day()
    avg_daily = AnalyticsModel.get_average_daily_reservations()
    most_active = AnalyticsModel.get_most_active_faculty()
    room_recommendation = AnalyticsModel.get_room_recommendation()
    pending_status = AnalyticsModel.get_pending_bottleneck()
    
    # Row 1: Status Metrics (4 Columns)
    status_row = ft.Row([
        ft.Container(
            content=ft.Column([
                ft.Text("TOTAL", size=11, color="#6B7280", weight=ft.FontWeight.W_500),
                ft.Text(str(summary['total']), size=36, weight=ft.FontWeight.BOLD, color="#111827"),
                ft.Row([
                    ft.Icon(ICONS.CALENDAR_MONTH, size=16, color="#3B82F6"),
                    ft.Text("Total Reservations", size=13, color="#3B82F6"),
                ], spacing=5),
            ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=25,
            border=ft.border.all(1, "#E5E7EB"),
            border_radius=12,
            bgcolor="white",
            width=200,
        ),
        create_modern_stat_card(
            "APPROVED", 
            str(summary['approved']), 
            "Approved Requests",
            ICONS.CHECK_CIRCLE, 
            "#10B981"
        ),
        create_modern_stat_card(
            "PENDING", 
            str(summary['pending']), 
            "Awaiting Review",
            ICONS.HOURGLASS_EMPTY, 
            "#F59E0B"
        ),
        create_modern_stat_card(
            "REJECTED", 
            str(summary['rejected']), 
            "Declined Requests",
            ICONS.CANCEL, 
            "#EF4444"
        ),
    ], spacing=15, alignment=ft.MainAxisAlignment.CENTER)
    
    # Insights Section Header
    insights_header = ft.Container(
        content=ft.Text("Insights & Recommendations", size=20, weight=ft.FontWeight.BOLD, color="#111827"),
        padding=ft.padding.only(top=30, bottom=10),
    )
    
    # Weekly Trends (Full Width)
    weekly_trend_card = create_weekly_trends_card(weekly_comparison)
    
    # Peak Hour, Most Popular Room, Daily Average (3 Columns)
    peak_hour_text = f"{peak_hours[0]['hour']}:00" if peak_hours else "N/A"
    most_popular_room = popular_rooms[0]['room_name'] if popular_rooms else "N/A"
    
    secondary_row = ft.Row([
        create_metric_card("Peak Hour", peak_hour_text, "Highest booking activity", ICONS.ACCESS_TIME, "#F59E0B"),
        create_metric_card("Daily Average", str(avg_daily), "Reservations per day (30d)", ICONS.SHOW_CHART, "#F59E0B"),
        create_metric_card("Most Popular Room", most_popular_room, "Top requested classroom", ICONS.STAR, "#F59E0B"),
    ], spacing=15, alignment=ft.MainAxisAlignment.CENTER)
    
    # Most Active Faculty & Recommendation (2 Columns)
    bottom_row = ft.Row([
        create_info_card(
            "Most Active Faculty", 
            most_active['full_name'] if most_active else "N/A",
            f"{most_active['reservation_count']} reservations this month" if most_active else "No data",
        ),
        create_recommendation_card(
            "Recommendation",
            room_recommendation['room_name'] if room_recommendation else "N/A",
            room_recommendation['message'] if room_recommendation else "No recommendation available",
        ),
    ], spacing=15, alignment=ft.MainAxisAlignment.CENTER)
    
    page.controls.clear()
    page.add(
        ft.Column([
            header,
            
            # Title (Fixed)
            ft.Container(
                ft.Text("EduROOM Analytics", size=32, color="#4D4848",
                            font_family="Montserrat Bold", weight=ft.FontWeight.BOLD),width=850, alignment=ft.alignment.center
                ),
            
            # Scrollable Content Area
            ft.Column([
                
                # Status Metrics
                ft.Container(
                    content=ft.Text("Status Metrics", size=20, weight=ft.FontWeight.BOLD, color="#111827"),
                    padding=ft.padding.only(top=30, bottom=10),
                    width=850,
                    alignment=ft.alignment.center_left
                ),
                status_row,
                
                # Insights Section
                ft.Container(
                    content=ft.Text("Insights & Recommendations", size=20, weight=ft.FontWeight.BOLD, color="#111827"),
                    padding=ft.padding.only(top=30, bottom=10),
                    width=850,
                    alignment=ft.alignment.center_left
                ),
                weekly_trend_card,
                ft.Container(height=15),
                secondary_row,
                ft.Container(height=15),
                bottom_row,
                
                # Detailed Analytics Section (Original Tables)
                ft.Container(height=20),
                ft.Container(
                    content=ft.Text("Detailed Analytics", size=18, weight=ft.FontWeight.BOLD),
                    width=850,
                    alignment=ft.alignment.center_left
                ),
                
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
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            )
            
        ], 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True
        )
    )
    page.update()


def create_modern_stat_card(label, value, subtitle, icon, color):
    """Create modern status card matching the design"""
    return ft.Container(
        content=ft.Column([
            ft.Text(label, size=11, color="#6B7280", weight=ft.FontWeight.W_500),
            ft.Text(value, size=36, weight=ft.FontWeight.BOLD, color="#111827"),
            ft.Row([
                ft.Icon(icon, size=16, color=color),
                ft.Text(subtitle, size=13, color=color),
            ], spacing=5),
        ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=25,
        border=ft.border.all(1, "#E5E7EB"),
        border_radius=12,
        bgcolor="white",
        width=200,
    )

def create_weekly_trends_card(weekly):
    """Create weekly trends card matching the new design"""

    # Calculate percentage change
    if weekly['last_week'] > 0:
        percentage_change = round(((weekly['this_week'] - weekly['last_week']) / weekly['last_week']) * 100)
    else:
        # If last week was 0 but this week has data, show 100% increase
        percentage_change = 100 if weekly['this_week'] > 0 else 0
    
    # Determine trend badge color and text
    if percentage_change > 0:
        badge_color = "#10B981"
        badge_text = f"↑ {percentage_change}% vs last week"
    elif percentage_change < 0:
        badge_color = "#EF4444"
        badge_text = f"↓ {abs(percentage_change)}% vs last week"
    else:
        badge_color = "#6B7280"
        badge_text = "→ No change"
    
    return ft.Container(
        content=ft.Column([
            # Header row with title and badge
            ft.Row([
                ft.Row([
                    ft.Text("Weekly Trends", size=20, weight=ft.FontWeight.BOLD, color="#111827"),
                ], spacing=10),
                ft.Container(
                    content=ft.Text(badge_text, size=13, color="white", weight=ft.FontWeight.W_600),
                    bgcolor=badge_color,
                    padding=ft.padding.symmetric(horizontal=16, vertical=8),
                    border_radius=6,
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Container(height=20),
            
            # Metric cards row
            ft.Row([
                # This week card
                ft.Container(
                    content=ft.Column([
                        ft.Text("THIS WEEK", size=11, color="#6B7280", weight=ft.FontWeight.W_500),
                        ft.Container(height=8),
                        ft.Row([
                            ft.Text(str(weekly['this_week']), size=36, weight=ft.FontWeight.BOLD, color="#111827"),
                            ft.Text("reservations", size=14, color="#6B7280"),
                        ], spacing=8, alignment=ft.CrossAxisAlignment.END),
                    ], spacing=0),
                    bgcolor="#F9FAFB",
                    padding=20,
                    border_radius=12,
                    expand=True,
                ),
                
                # Last week card
                ft.Container(
                    content=ft.Column([
                        ft.Text("LAST WEEK", size=11, color="#6B7280", weight=ft.FontWeight.W_500),
                        ft.Container(height=8),
                        ft.Row([
                            ft.Text(str(weekly['last_week']), size=36, weight=ft.FontWeight.BOLD, color="#111827"),
                            ft.Text("reservations", size=14, color="#6B7280"),
                        ], spacing=8, alignment=ft.CrossAxisAlignment.END),
                    ], spacing=0),
                    bgcolor="#F9FAFB",
                    padding=20,
                    border_radius=12,
                    expand=True,
                ),
            ], spacing=15),
            
            ft.Container(height=25),
            
            # Bar chart visualization
            ft.Column([
                # This week bar
                ft.Row([
                    ft.Text("This Week", size=13, color="#6B7280", width=80),
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                bgcolor="#3B82F6",
                                border_radius=6,
                                height=35,
                                expand=True,
                            ),
                            ft.Text(str(weekly['this_week']), size=14, weight=ft.FontWeight.W_600, color="white"),
                        ], spacing=0),
                        bgcolor="#3B82F6",
                        border_radius=6,
                        padding=ft.padding.only(right=12),
                        expand=True,
                    ),
                ], spacing=15),
                
                ft.Container(height=10),
                
                # Last week bar
                ft.Row([
                    ft.Text("Last Week", size=13, color="#6B7280", width=80),
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                bgcolor="#8B5CF6",
                                border_radius=6,
                                height=35,
                                expand=True,
                                width=weekly['last_week'] / weekly['this_week'] * 100 if weekly['this_week'] > 0 else 100,
                            ),
                            ft.Text(str(weekly['last_week']), size=14, weight=ft.FontWeight.W_600, color="white"),
                        ], spacing=0),
                        bgcolor="#8B5CF6",
                        border_radius=6,
                        padding=ft.padding.only(right=12),
                        width=weekly['last_week'] / weekly['this_week'] * 600 if weekly['this_week'] > 0 else 600,
                    ),
                ], spacing=15),
            ], spacing=0),
            
        ], spacing=0),
        padding=30,
        border=ft.border.all(1, "#E5E7EB"),
        border_radius=12,
        bgcolor="white",
        width=850,
    )

def create_metric_card(title, value, subtitle, icon, color):
    """Create metric card"""
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(icon, size=20, color=color),
                ft.Text(title, size=13, weight=ft.FontWeight.W_600, color="#111827"),
            ], spacing=8),
            ft.Container(height=10),
            ft.Text(value, size=28, weight=ft.FontWeight.BOLD, color="#111827"),
            ft.Text(subtitle, size=12, color="#6B7280"),
        ], spacing=3),
        padding=25,
        border=ft.border.all(1, "#E5E7EB"),
        border_radius=12,
        bgcolor="white",
        width=270,
    )


def create_info_card(title, main_text, subtitle):
    """Create info card for faculty/recommendations"""
    return ft.Container(
        content=ft.Column([
            ft.Text(title, size=13, weight=ft.FontWeight.W_600, color="#111827"),
            ft.Container(height=10),
            ft.Text(main_text, size=20, weight=ft.FontWeight.BOLD, color="#3B82F6"),
            ft.Text(subtitle, size=12, color="#6B7280"),
        ], spacing=5),
        padding=25,
        border=ft.border.all(1, "#E5E7EB"),
        border_radius=12,
        bgcolor="white",
        width=415,
    )


def create_recommendation_card(title, main_text, subtitle):
    """Create recommendation card with blue accent"""
    return ft.Container(
        content=ft.Column([
            ft.Text(title, size=13, weight=ft.FontWeight.W_600, color="#111827"),
            ft.Container(height=10),
            ft.Text(main_text, size=20, weight=ft.FontWeight.BOLD, color="#3B82F6"),
            ft.Text(subtitle, size=12, color="#6B7280"),
        ], spacing=5),
        padding=25,
        border=ft.border.all(1, "#E5E7EB"),
        border_radius=12,
        bgcolor="white",
        width=415,
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
                    ft.DataCell(
                        ft.Text(
                            item['status'].title(), 
                            weight=ft.FontWeight.BOLD, 
                            color=color,
                            size=14
                        )
                    ),
                    ft.DataCell(ft.Text(str(item['count']), size=14)),
                    ft.DataCell(ft.Text(f"{percentage:.1f}%", size=14)),
                    ft.DataCell(
                        ft.Container(
                            width=int(percentage * 4),
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
            ft.Text("Status Distribution", size=16, weight=ft.FontWeight.BOLD),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Count", weight=ft.FontWeight.BOLD), numeric=True),
                    ft.DataColumn(ft.Text("Percentage", weight=ft.FontWeight.BOLD), numeric=True),
                    ft.DataColumn(ft.Text("Visual", weight=ft.FontWeight.BOLD)),
                ],
                rows=rows,
                column_spacing=155,
                data_row_min_height=50,
                data_row_max_height=50,
                horizontal_margin=0,
            ),
        ]),
        border=ft.border.all(1, "#E0E0E0"),
        border_radius=10,
        padding=15,
        bgcolor="white",
        width=850,
    )


def create_popular_rooms_table(popular_rooms):
    """Create table for popular classrooms"""
    if not popular_rooms:
        return ft.Text("No data available", size=14, color="grey")
    
    rows = []
    max_count = max(item['reservation_count'] for item in popular_rooms) if popular_rooms else 1
    
    for idx, item in enumerate(popular_rooms, 1):
        bar_width = int((item['reservation_count'] / max_count) * 250) if max_count > 0 else 0
        
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
            ft.Text("Most Popular Classrooms", size=16, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Rank")),
                        ft.DataColumn(ft.Text("Room")),
                        ft.DataColumn(ft.Text("Building")),
                        ft.DataColumn(ft.Text("Reservations")),
                        ft.DataColumn(ft.Text("Popularity")),
                    ],
                    rows=rows,
                    column_spacing=60,
                    data_row_min_height=50,
                    data_row_max_height=50,
                ),
                expand=True,
            ),
        ], expand=True),
        border=ft.border.all(1, "#E0E0E0"),
        border_radius=10,
        padding=15,
        bgcolor="white",
        width=850,
    )


def create_faculty_activity_table(faculty_activity):
    """Create table for faculty activity"""
    if not faculty_activity:
        return ft.Text("No data available", size=14, color="grey")
    
    rows = []
    max_count = max(item['reservation_count'] for item in faculty_activity) if faculty_activity else 1
    
    for item in faculty_activity[:10]:  # Top 10
        bar_width = int((item['reservation_count'] / max_count) * 350) if max_count > 0 else 0
        
        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(item['full_name'], size=14)),
                    ft.DataCell(ft.Text(str(item['reservation_count']), size=14)),
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
            ft.Text("Faculty Activity", size=16, weight=ft.FontWeight.BOLD),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Faculty Name", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Reservations", weight=ft.FontWeight.BOLD), numeric=True),
                    ft.DataColumn(ft.Text("Activity Level", weight=ft.FontWeight.BOLD)),
                ],
                rows=rows,
                column_spacing=150,
                data_row_min_height=50,
                data_row_max_height=50,
                horizontal_margin=0,
            ),
        ]),
        border=ft.border.all(1, "#E0E0E0"),
        border_radius=10,
        padding=15,
        bgcolor="white",
        width=850,
    )


def create_trends_table(date_trends):
    """Create table for reservation trends"""
    if not date_trends:
        return ft.Text("No data available", size=14, color="grey")
    
    rows = []
    max_count = max(item['count'] for item in date_trends) if date_trends else 1
    
    # Show last 10 days
    for item in date_trends[-10:]:
        bar_width = int((item['count'] / max_count) * 350) if max_count > 0 else 0
        
        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(item['date']), size=14)),
                    ft.DataCell(ft.Text(str(item['count']), size=14)),
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
            ft.Text("Recent Trends (Last 10 Days)", size=16, weight=ft.FontWeight.BOLD),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Date", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Reservations", weight=ft.FontWeight.BOLD), numeric=True),
                    ft.DataColumn(ft.Text("Volume", weight=ft.FontWeight.BOLD)),
                ],
                rows=rows,
                column_spacing=150,
                data_row_min_height=50,
                data_row_max_height=50,
                horizontal_margin=0,
            ),
        ]),
        border=ft.border.all(1, "#E0E0E0"),
        border_radius=10,
        padding=15,
        bgcolor="white",
        width=850,
    )


def create_time_slots_table(time_slots):
    """Create table for time slot distribution"""
    if not time_slots:
        return ft.Text("No data available", size=14, color="grey")
    
    rows = []
    max_count = max(item['count'] for item in time_slots) if time_slots else 1
    
    for item in time_slots:
        bar_width = int((item['count'] / max_count) * 350) if max_count > 0 else 0
        hour_str = f"{item['hour']:02d}:00 - {item['hour']:02d}:59"
        
        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(hour_str, size=14)),
                    ft.DataCell(ft.Text(str(item['count']), size=14)),
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
            ft.Text("Peak Hours Distribution", size=16, weight=ft.FontWeight.BOLD),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Time Slot", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Reservations", weight=ft.FontWeight.BOLD), numeric=True),
                    ft.DataColumn(ft.Text("Activity", weight=ft.FontWeight.BOLD)),
                ],
                rows=rows,
                column_spacing=160,
                data_row_min_height=50,
                data_row_max_height=50,
                horizontal_margin=0,
            ),
        ]),
        border=ft.border.all(1, "#E0E0E0"),
        border_radius=10,
        padding=15,
        bgcolor="white",
        width=850,
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
                    ft.DataCell(ft.Text(item['room_name'], size=14)),
                    ft.DataCell(ft.Text(item['building'], size=14)),
                    ft.DataCell(ft.Text(str(item['total_reservations']), size=14)),
                    ft.DataCell(ft.Text(str(item['approved_reservations']), size=14)),
                    ft.DataCell(ft.Text(f"{approval_rate:.1f}%", size=14)),
                ]
            )
        )
    
    return ft.Container(
        content=ft.Column([
            ft.Text("Classroom Utilization", size=16, weight=ft.FontWeight.BOLD),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Room", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Building", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Total", weight=ft.FontWeight.BOLD), numeric=True),
                    ft.DataColumn(ft.Text("Approved", weight=ft.FontWeight.BOLD), numeric=True),
                    ft.DataColumn(ft.Text("Rate", weight=ft.FontWeight.BOLD), numeric=True),
                ],
                rows=rows,
                column_spacing=140,
                data_row_min_height=50,
                data_row_max_height=50,
                horizontal_margin=0,
            ),
        ]),
        border=ft.border.all(1, "#E0E0E0"),
        border_radius=10,
        padding=15,
        bgcolor="white",
        width=850,
    )