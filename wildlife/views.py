from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import  HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import User, Announcements, Claims, Ticket
from .forms import UserProfileForm
from .forms import TicketForm, AdminTicketForm, AdminClaimForm
from django.contrib import messages
from .forms import NotificationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import UserProfileForm
from django.db import IntegrityError
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.shortcuts import render, reverse
from .forms import ClaimForm
import json
from django.http import JsonResponse
from django.db.models.functions import TruncMonth
from django.db.models import Count
from django.utils import timezone
import datetime
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import requests
import os
from django.conf import settings

#get custom user
from django.contrib.auth import get_user_model
User = get_user_model()



# Create your views here.
def home_view(request):
    return render(request, "home.html")

# Create your views here.
def dashboard_view(request):
    return render(request, "dashboard.html")

def login_view(request):
    if request.method == "GET":
        return render(request, "index.html")
    elif request.method == "POST":
        # Attempt to sign user in
        username = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        # Check if authentication successful
        if user is not None:
            login(request, user)
            if (user.is_staff):
                return HttpResponseRedirect(reverse("wildlife:dashboard"))
            else:
                return HttpResponseRedirect(reverse("wildlife:home"))
        else:
            messages.error(request, 'Incorrect username/ password.')
            return redirect('wildlife:index')
    else:
        return render(request, "index.html")
    
def google_oauth_login_view(request):
    # After successful Google OAuth authentication and user creation, you can obtain the user.
    user = User.objects.get(username=request.user.username)
    
    # Log in the user using Django's authentication system.
    login(request, user)
    
    # Define the URL where you want to redirect the user after Google OAuth login.
    redirect_url = '/wildlife:home/'  # Replace with your desired URL
    
    # Redirect the user to the specified URL.
    return redirect(redirect_url)

def logout_view(request):
    logout(request)
    return render(request, "login.html")


def user_signup(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["password_confirm"]
        
        if password != confirmation:
        
            messages.error(request, 'Passwords must match.')
            return redirect('wildlife:user_signup')
        else:
            try:
                # Create a new user and save to the database
                user = User.objects.create_user(username=email,email=email, password=password)
            except IntegrityError:
                messages.error(request, 'Username already taken.')
                return redirect('wildlife:user_signup')
             
            # Log in the user
            login(request, user,  backend='django.contrib.auth.backends.ModelBackend')
            # Redirect to the user's profile page
            return render(request, "profile.html")
    else:
        return render(request, "user_signup.html")
    


@login_required
def profile(request):
    # Retrieve user profile data and any other necessary logic here
    user = request.user
    # ... (other profile-related logic) ...

    return render(request, 'profile.html', {
        # Pass context data to the profile template if needed
        'user': user,
        # ... (other context data) ...
    })

@login_required
def update_profile(request):
    user = request.user

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('wildlife:profile')  # Redirect to the profile page after a successful update
    else:
        form = UserProfileForm(instance=user)

    return render(request, 'update_profile.html', {
        'form': form,
    })


def admin_announcements(request):
    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Announcement posted.')
            return redirect('wildlife:admin_announcements')
    else:
        form = NotificationForm()

    announcements = Announcements.objects.all().order_by('-timestamp')
    claims = Claims.objects.select_related('user').all().order_by('-timestamp')
    claim_form = AdminClaimForm()
    return render(request, 'admin_announcements.html', {
        'form': form,
        'announcements': announcements,
        'claims': claims,
        'claim_form': claim_form,
    })


@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def admin_edit_announcement(request, ann_id):
    announcement = get_object_or_404(Announcements, pk=ann_id)
    if request.method == 'POST':
        form = NotificationForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Announcement updated.')
    return redirect('wildlife:admin_announcements')


@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def admin_delete_announcement(request, ann_id):
    if request.method == 'POST':
        get_object_or_404(Announcements, pk=ann_id).delete()
        messages.success(request, 'Announcement deleted.')
    return redirect('wildlife:admin_announcements')


@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def admin_create_claim(request):
    if request.method == 'POST':
        form = AdminClaimForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Claim created.')
    return redirect('wildlife:admin_announcements')


@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def admin_edit_claim(request, claim_id):
    claim = get_object_or_404(Claims, pk=claim_id)
    if request.method == 'POST':
        form = AdminClaimForm(request.POST, request.FILES, instance=claim)
        if form.is_valid():
            form.save()
            messages.success(request, 'Claim updated.')
    return redirect('wildlife:admin_announcements')


@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def admin_delete_claim(request, claim_id):
    if request.method == 'POST':
        claim = get_object_or_404(Claims, pk=claim_id)
        claim.delete()
        messages.success(request, 'Claim deleted.')
    return redirect('wildlife:admin_announcements')


# Create a custom function to check if the user is an admin
def is_admin(user):
    return user.is_superuser  # You can customize this condition based on your user model.

def is_staff(user):
    return user.is_staff  # You can customize this condition based on your user model.

@user_passes_test(lambda u: is_staff(u) or is_admin(u))
def admin_claims_list(request):
    claims = Claims.objects.all()
    return render(request, 'admin_claims_list.html', {'claims': claims})


def admin_claim_view(request):
    # Retrieve claims submitted by the currently logged-in user
    user_claims = Claims.objects.filter(user=request.user)  # Assuming you have a ForeignKey to User in Claims model

    return render(request, 'admin_claim_view.html', {'user_claims': user_claims})

def admin_support(request):
    all_tickets = Ticket.objects.all().order_by('-submission_timestamp')
    return render(request, "admin_support.html", {'all_tickets': all_tickets})

def ticket_set_status(request, ticket_id, status):
    if request.method == 'POST':
        ticket = get_object_or_404(Ticket, pk=ticket_id)
        if status in ('pending', 'assigned', 'fixed'):
            ticket.status = status
            if status == 'assigned':
                ticket.support_officer = request.user
            ticket.save()
    return redirect('wildlife:admin_support')

def admin_support_detail(request, claim_id):
    ticket = get_object_or_404(Ticket, pk=claim_id)
    
    if request.method == 'POST':
        form = AdminTicketForm(request.POST, instance=ticket)
        if form.is_valid():
            ticket.support_officer = request.user  # Update the support_officer field
            form.save()  # Save the updated ticket to the database

            messages.success(request, 'Ticket updated successfully.')
            return redirect('wildlife:admin_support')

    else:
        form = AdminTicketForm(instance=ticket)

    return render(request, 'admin_support_detail.html', {'form': form, 'ticket': ticket})

def client_claims_list(request):
    user_claims = Claims.objects.filter(user=request.user).order_by('-timestamp')  
    
    return render(request, 'client_claims_list.html',{'user_claims': user_claims})



@login_required
def client_new_claim(request):
    if request.method == 'POST':
        form = ClaimForm(request.POST, request.FILES)
        if form.is_valid():
            selected_claim_id = form.cleaned_data['claim']
            details = form.cleaned_data['details']
            claim_image = form.cleaned_data['claim_image']

            # Create a new Claim object in the database and associate it with the logged-in user
            new_claim = Claims.objects.create(
                claims=selected_claim_id,
                details=details,
                claim_image=claim_image,
                user=request.user  # Set the 'user' field to the logged-in user
            )

            # Additional processing...

            return redirect(reverse('wildlife:client_new_claim') + '?submitted=1')
    else:
        form = ClaimForm()

    return render(request, 'client_new_claim.html', {'form': form})

def client_announcements_list(request):
    announcements = Announcements.objects.all().order_by('-timestamp')  
    return render(request, "client_announcements_list.html", {'announcements': announcements})

def client_announcement_view(request):
    return render(request, "client_announcement_view.html")

def client_support(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.status = 'pending'
            ticket.response = ''
            ticket.save()
            messages.success(request, 'Ticket submitted successfully.')
            return redirect('wildlife:client_support')
    else:
        form = TicketForm()

    user_tickets = Ticket.objects.filter(user=request.user).order_by('-submission_timestamp')
    return render(request, 'client_support.html', {'form': form, 'user_tickets': user_tickets})


def client_support_detail(request, claim_id):
    ticket = get_object_or_404(Ticket, pk=claim_id)
    return render(request, 'client_support_detail.html', {'ticket': ticket})

#API
class GetNationalParksView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query=national+park+in+South+Africa&type=national_park&key=AIzaSyCQv4vAE2o4FJRPTneTl_5AfOxoWEl9sCM'

        try:
            response = requests.get(url)
            response_data = response.json()
            return JsonResponse({'data': response_data['results']})
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)
        


class GetCityNearParkView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query=towns near national parks+in+South+Africa&key=AIzaSyCQv4vAE2o4FJRPTneTl_5AfOxoWEl9sCM'

        try:
            response = requests.get(url)
            response_data = response.json()
            return JsonResponse({'data': response_data['results']})
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)

from pathlib import Path

class GetBorderView(View):

    def get(self, request, *args, **kwargs):
        # Construct the correct path to the JSON file using pathlib
        json_file_path = Path(settings.BASE_DIR) / 'wildlife' / 'static' / 'assets' / 'js' / 'countryBorders.geo.json'

        try:
            with open(json_file_path, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            # Get a list of all files and directories in the specified directory
            directory_contents = [str(p) for p in json_file_path.parent.iterdir()]
            return JsonResponse({'error': 'JSON file not found', 'directory_contents': directory_contents}, status=404)

        country_code = request.GET.get('countryCode', '')

        poly = None
        for feature in data['features']:
            if feature['properties']['iso_a2'] == country_code:
                poly = feature['geometry']
                break

        if poly:
            return JsonResponse(poly)
        else:
            return JsonResponse({'error': 'Country code not found'}, status=404)


def admin_claim_detail(request, claim_id):
    claim = get_object_or_404(Claims, pk=claim_id)
    return render(request, 'admin_claim_detail.html', {'claim': claim})



def approve_claim(request, claim_id):
    # Assuming you have a 'status' field in your Claims model to track the claim status
    claim = Claims.objects.get(pk=claim_id)
    claim.status = 'approved'  # Update the status to 'approved'
    claim.save()

    # Redirect to a page for approved claims (you can change the URL as needed)
    return redirect('wildlife:approved_claims_page')

def decline_claim(request, claim_id):
    # Assuming you have a 'status' field in your Claims model to track the claim status
    claim = Claims.objects.get(pk=claim_id)
    claim.status = 'declined'  # Update the status to 'declined'
    claim.save()

    # Redirect to a page for declined claims (you can change the URL as needed)
    return redirect('wildlife:declined_claims_page')

def approved_claims_page(request):
    approved_claims = Claims.objects.filter(status='approved')
    return render(request, 'approved_claims_page.html', {'approved_claims': approved_claims})

def declined_claims_page(request):
    declined_claims = Claims.objects.filter(status='declined')
    return render(request, 'declined_claims_page.html', {'declined_claims': declined_claims})

# views.py

def pending_claims_page(request):
    # Filter claims with a status other than 'approved' or 'declined'
    pending_claims = Claims.objects.exclude(status__in=['approved', 'declined'])

    return render(request, 'pending_claims_page.html', {'pending_claims': pending_claims})


def client_claim_detail(request, claim_id):
    claim = get_object_or_404(Claims, pk=claim_id)
    context = {'claim': claim}
    return render(request, 'client_claim_detail.html', context)

def information_view(request):
    return render(request, 'information.html')

class DashboardView(View):
    template_name = 'dashboard.html'  # Update with your dashboard template

    def get(self, request, *args, **kwargs):
        # Retrieve statistics from the models
        total_users = User.objects.count()
        total_active_users = User.objects.filter(status=True).count()
        total_blocked_users = User.objects.filter(status=False).count()
        total_users_with_profile_picture = User.objects.exclude(profilePicture='images/placeholder_img.jpg').count()
        total_announcements = Announcements.objects.count()
        total_tickets = Ticket.objects.count()
        total_fixed_tickets = Ticket.objects.filter(status='fixed').count()
        total_tickets_with_support_officers = Ticket.objects.exclude(support_officer=None).count()
        total_tickets_without_support_officers = Ticket.objects.filter(support_officer=None).count()
        total_claims = Claims.objects.count()
        total_approved_claims = Claims.objects.filter(status='approved').count()
        total_declined_claims = Claims.objects.filter(status='declined').count()
        total_pending_claims = Claims.objects.exclude(status__in=['approved', 'declined']).count()
        total_image_attachments = sum(
            [
             Claims.objects.filter(claim_image__isnull=False).count(),
             User.objects.exclude(profilePicture='images/placeholder_img.jpg').count()])

        # Calculate average ticket response time (sample value, replace with your logic)
        # Assuming submission_timestamp and response_timestamp fields in Ticket model
        average_ticket_response_time = 3.5  # Replace with actual calculation

        # Same queryset as admin_claims_list
        from django.db.models import Q
        all_claims = Claims.objects.all()

        # Helper: build monthly trend data for a given queryset
        # "pending" = anything that is not approved or declined (mirrors admin_claims_list {% else %})
        def monthly_trend(qs):
            rows = (
                qs.annotate(month=TruncMonth('timestamp'))
                .values('month')
                .annotate(
                    total=Count('id'),
                    approved=Count('id', filter=Q(status='approved')),
                    declined=Count('id', filter=Q(status='declined')),
                )
                .order_by('month')
            )
            return {
                'labels':   [r['month'].strftime('%b %Y') for r in rows],
                'total':    [r['total']    for r in rows],
                'approved': [r['approved'] for r in rows],
                'declined': [r['declined'] for r in rows],
            }

        now = timezone.now()
        trend_3m  = monthly_trend(all_claims.filter(timestamp__gte=now - datetime.timedelta(days=90)))
        trend_6m  = monthly_trend(all_claims.filter(timestamp__gte=now - datetime.timedelta(days=180)))
        trend_all = monthly_trend(all_claims)

        # Claims by category (the `claims` field) — derived from all_claims
        category_qs = (
            all_claims
            .values('claims')
            .annotate(
                total=Count('id'),
                approved=Count('id', filter=Q(status='approved')),
                declined=Count('id', filter=Q(status='declined')),
                pending=Count('id', filter=~Q(status__in=['approved', 'declined'])),
            )
            .order_by('-total')
        )
        category_labels   = [entry['claims'] or 'Unknown' for entry in category_qs]
        category_total    = [entry['total']    for entry in category_qs]
        category_approved = [entry['approved'] for entry in category_qs]
        category_declined = [entry['declined'] for entry in category_qs]

        # Recent 10 claims for the mini-list (mirrors admin_claims_list order)
        recent_claims = all_claims.order_by('-timestamp')[:10]

        # Pass statistics to the dashboard template
        context = {
            'total_users': total_users,
            'total_active_users': total_active_users,
            'total_blocked_users': total_blocked_users,
            'total_users_with_profile_picture': total_users_with_profile_picture,
            'total_announcements': total_announcements,
            'total_tickets': total_tickets,
            'total_fixed_tickets': total_fixed_tickets,
            'total_tickets_with_support_officers': total_tickets_with_support_officers,
            'total_tickets_without_support_officers': total_tickets_without_support_officers,
            'total_claims': total_claims,
            'total_approved_claims': total_approved_claims,
            'total_declined_claims': total_declined_claims,
            'total_pending_claims': total_pending_claims,
            'total_image_attachments': total_image_attachments,
            'average_ticket_response_time': average_ticket_response_time,
            'trend_3m':  json.dumps(trend_3m),
            'trend_6m':  json.dumps(trend_6m),
            'trend_all': json.dumps(trend_all),
            'category_labels':   json.dumps(category_labels),
            'category_total':    json.dumps(category_total),
            'category_approved': json.dumps(category_approved),
            'category_declined': json.dumps(category_declined),
            'recent_claims':     recent_claims,
            'total_staff_users': User.objects.filter(is_staff=True).count(),
        }

        return render(request, self.template_name, context)