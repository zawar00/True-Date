from rest_framework.views import APIView
from user_api.users.models import User
from admin_api.transaction_management.models import Subscription
from utils.response_helper import successResponse, errorResponse
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta, datetime

class DashboardView(APIView):
    def get(self, request):
        # Get the time period from query parameters
        period = request.query_params.get('period', '30days').lower()
        
        # Define time ranges based on the period
        today = timezone.now().date()
        if period == 'week':
            start_date = today - timedelta(days=7)
        elif period == 'month':
            start_date = today - timedelta(days=30)
        elif period == '3months':
            start_date = today - timedelta(days=90)
        elif period == '6months':
            start_date = today - timedelta(days=180)
        elif period == 'year':
            start_date = today - timedelta(days=365)
        else:
            # Default to the last 30 days
            start_date = today - timedelta(days=7)

        # Total users, total revenue, active users
        total_users = User.objects.count()
        total_revenue = Subscription.objects.filter(status='active').aggregate(
            total=Sum('plan__price')
        )['total'] or 0

        active_users = User.objects.filter(status='active', is_verified=True).count()
        active_users_subscription = Subscription.objects.filter(status='active').count()

        # Prepare chart data
        chart_data = {
            'revenue_by_day': [],
            'active_users_by_day': [],
            'new_users_by_day': [],
        }

        # Generate data for each day in the period
        days_count = (today - start_date).days
        for i in range(days_count + 1):
            day = today - timedelta(days=i)
            start_of_day = timezone.make_aware(datetime.combine(day, datetime.min.time()))
            end_of_day = timezone.make_aware(datetime.combine(day, datetime.max.time()))

            # Revenue for the day
            daily_revenue = Subscription.objects.filter(
                status='active', 
                created_at__range=[start_of_day, end_of_day]
            ).aggregate(daily_revenue=Sum('plan__price'))['daily_revenue'] or 0

            # Active users for the day
            daily_active_users = User.objects.filter(
                status='active', 
                is_verified=True,
                date_joined__range=[start_of_day, end_of_day]
            ).count()

            # New users for the day
            daily_new_users = User.objects.filter(
                date_joined__range=[start_of_day, end_of_day]
            ).count()

            # Append the data for each day to the chart data
            chart_data['revenue_by_day'].append({'date': day, 'revenue': daily_revenue})
            chart_data['active_users_by_day'].append({'date': day, 'active_users': daily_active_users})
            chart_data['new_users_by_day'].append({'date': day, 'new_users': daily_new_users})

        # Using successResponse for the response
        return successResponse({
            'total_users': total_users,
            'total_revenue': total_revenue,
            'active_users': active_users,
            'active_users_Subscription': active_users_subscription,
            'chart_data': chart_data  # Include chart data
        }, message=f"Dashboard data for period '{period}' retrieved successfully.")
