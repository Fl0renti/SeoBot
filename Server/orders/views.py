from django.forms import BaseModelForm
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, DeleteView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from .models import *
from django.urls import reverse_lazy
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core.serializers import serialize
import requests
import random
from django.http import HttpResponseRedirect

from django.db.models import Value
from django.db.models.functions import Coalesce


from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta

def get_location_and_timezone(ip_address):
    # Using a geolocation service API (like ipgeolocation, ipinfo, etc.)
    # Here I use 'ip-api.com' for demonstration; you should use your preferred geolocation service
    # Make sure to handle the API key and rate limiting as per your service's requirements
    response = requests.get(f'http://ip-api.com/json/{ip_address}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,query')
    
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'success':
            # Return the necessary fields
            return {
                'country': data.get('country', ''),
                'countryCode': data.get('countryCode', ''),
                'region': data.get('region', ''),
                'regionName': data.get('regionName', ''),
                'city': data.get('city', ''),
                'zip': data.get('zip', ''),
                'lat': data.get('lat', 0),
                'lon': data.get('lon', 0),
                'timezone': data.get('timezone', ''),
                'query': data.get('query', '')
            }
        else:
            raise Exception("API returned an error: " + data.get('message', 'No message'))
    else:
        response.raise_for_status()

    return None

def get_orders(request, domain_type):
    keywords = Keyword.objects.filter(keyword__active=True, keyword__domain_type=domain_type, status__in=["Waiting", "In Progress"]) 
    keywords = keywords.annotate(
    nearest_date=Coalesce('keyword__order_schedule', Value(datetime.min))
    ).order_by('nearest_date')
    clean_data = []
    for i, keyword in enumerate(keywords):
        clean_data.append({
            "id": keyword.keyword.id,
            'domain_name': f"https://{keyword.keyword.domain_name}" if not keyword.keyword.domain_name.startswith("https://") else keyword.keyword.domain_name,
            'domain_type': keyword.keyword.domain_type,
            'work_sec': keyword.keyword.work_sec,
            'max_workers': keyword.keyword.WorkerRequired(),
            'reached_users': keyword.keyword.reached_users,
            'total_users': keyword.keyword.num_users,
            "order_schedule": keyword.keyword.order_schedule,
            'action': keyword.keyword.action,
            'second_action': keyword.keyword.second_action,
            'has_sponsored': keyword.has_sponsored,
            'has_business':keyword.has_business,
            'has_sponsored_business': keyword.has_sponsored_business,
            'status': keyword.status
        })
        break
    # Return the clean data as a JsonResponse
    return clean_data

def get_orders_web(request):
    data = get_orders(request, "web")
    return JsonResponse(data, safe=False)

def get_orders_mobile(request):
    data = get_orders(request, "mobile")
    return JsonResponse(data, safe=False)


def update_reached_users(request, pk):
    """ Function to increase the reached_user number in models.py """
    order = Order.objects.get(pk=pk)
    order.increment_reached_users() 
    return JsonResponse({'success': True})
def update_reached_users_incomplete(request, pk):
    """ Function to increase the reached_user number in models.py """
    order = Order.objects.get(pk=pk)
    order.decrement_reached_users() 
    return JsonResponse({'success': True})


# Orders View
class ViewOrders(LoginRequiredMixin, TemplateView):
    template_name = "orders.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_list = Order.objects.all().order_by('-id')

        column = self.request.GET.get('column')
        query = self.request.GET.get('query')

        if column and query:
            if column == 'domain_name':
                order_list = order_list.filter(domain_name__icontains=query)
            elif column == 'proxy':
                order_list = order_list.filter(proxy__icontains=query)
            elif column == 'active':
                query_bool = query.lower() == 'true'
                order_list = order_list.filter(active=query_bool)
            elif column == 'work_sec':
                order_list = order_list.filter(work_sec__icontains=query)
            elif column == 'avg_sec':
                order_list = order_list.filter(avg_sec__icontains=query)
            elif column == 'num_users':
                order_list = order_list.filter(num_users__icontains=query)
        
        # Pagination
        page = self.request.GET.get('page', 1)
        paginator = Paginator(order_list, 5) 

        try:
            order_list = paginator.page(page)
        except PageNotAnInteger:
            order_list = paginator.page(1)
        except EmptyPage:
            order_list = paginator.page(paginator.num_pages)

        context['order_list'] = order_list
        return context
    




class ViewKeyword(LoginRequiredMixin, TemplateView):
    template_name = "result1.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        keyword_list = Keyword.objects.filter(status="Waiting")
        
        # Pagination
        page = self.request.GET.get('page', 1)
        paginator = Paginator(keyword_list, 10) 

        try:
            keyword_list = paginator.page(page)
        except PageNotAnInteger:
            keyword_list = paginator.page(1)
        except EmptyPage:
            keyword_list = paginator.page(paginator.num_pages)

        context['keyword_list'] = keyword_list
        return context








class CreateNewOrder(CreateView):
    model = Order
    template_name = "create_new_order.html"
    form_class = CreateNewOrder

    def form_valid(self, form):
        domain_name = form.cleaned_data['domain_name']
        messages.success(self.request, f"Domain for&nbsp;<strong>{domain_name}</strong>&nbsp;added successfully!")
        return super().form_valid(form)
    
class CreateNewProfile(CreateView):
    model = Profile
    template_name = "create_new_profile.html"
    form_class = CreateNewProfile
    success_url =  reverse_lazy("orders:profile")


    def form_valid(self, form):
        profile = form.save(commit=False)

        proxy_string = form.cleaned_data['proxy']
        proxy_parts = proxy_string.split(':')
        if len(proxy_parts) >= 4:
            proxy_ip, proxy_port, proxy_username, proxy_password = proxy_parts[:4]

            geo_data = get_location_and_timezone(proxy_ip)
            if geo_data:
                profile.save()  # Commit the profile to the database

                ProxyDetail.objects.update_or_create(
                    profile=profile,
                    defaults={
                        'status': 'valid',
                        'country': geo_data['country'],
                        'countryCode': geo_data['countryCode'],
                        'region': geo_data['region'],
                        'regionName': geo_data['regionName'],
                        'city': geo_data['city'],
                        'zip': geo_data['zip'],
                        'lat': geo_data['lat'],
                        'lon': geo_data['lon'],
                        'timezone': geo_data['timezone'],
                        'query': proxy_ip,
                        'proxyusername': proxy_username,
                        'proxy_password': proxy_password
                    }
                )

                messages.success(self.request, f"Profile for <strong>{proxy_ip}</strong> added successfully!")
            else:
                messages.error(self.request, "Failed to fetch geo data for the provided proxy.")

        else:
            messages.error(self.request, "Invalid proxy format.")

        return super().form_valid(form)
        

class DeleteOrder(LoginRequiredMixin, DeleteView):
    model = Order
    template_name = "delete_order.html"
    success_url = reverse_lazy("orders:list_of_orders")

    def form_valid(self, form):
        order = self.get_object()
        domain_name = order.domain_name

        response = super().form_valid(form)
        messages.success(self.request, f"Domain for&nbsp;<strong>{domain_name}</strong>&nbsp;has been deleted succesfully!")
        return response

class DeleteProfile(LoginRequiredMixin,DeleteView):
    model = Profile
    template_name = "delete_profile.html"
    success_url = reverse_lazy("orders:profile")

    def form_valid(self, form):
        profile = self.get_object()
        proxy = profile.proxy
        response = super().form_valid(form)
        messages.success(self.request, f"Profile for&nbsp;<strong>{proxy}</strong>&nbsp;has been deleted succesfully!")
        return response
    

class UpdateOrder(LoginRequiredMixin, UpdateView):
    model = Order
    template_name = "update_order.html"
    form_class = UpdateOrder

    def form_valid(self, form):
        order = self.get_object()
        domain_name = order.domain_name
        response = super().form_valid(form)
        messages.success(self.request, f"Domain for&nbsp;<strong>{domain_name}</strong>&nbsp;has been updated succesfully!")
        return response

class UpdateProfile(LoginRequiredMixin, UpdateView):
    model = Profile
    template_name = "update_profile.html"
    form_class = UpdateProfiles  # Use the correct form class
    success_url = reverse_lazy("orders:profile")
    def form_valid(self, form):
        profile = self.get_object()
        proxy_string = profile.proxy  # Assuming 'proxy' is a field in your Profiles model

        # Parse the proxy string to extract the IP address
        proxy_parts = proxy_string.split(':')
        if len(proxy_parts) >= 4:
            proxy_ip = proxy_parts[0]
            # Further processing if needed

            # Update the profile
            response = super().form_valid(form)

            # Get and update the existing ProxyDetails for the profile
            geo_data = get_location_and_timezone(proxy_ip)
            if geo_data:
                ProxyDetail.objects.update_or_create(
                    profile=profile,
                    defaults={
                        'status': 'valid',  # Or other status based on your logic
                        'country': geo_data['country'],
                        'countryCode': geo_data['countryCode'],
                        'region': geo_data['region'],
                        'regionName': geo_data['regionName'],
                        'city': geo_data['city'],
                        'zip': geo_data['zip'],
                        'lat': geo_data['lat'],
                        'lon': geo_data['lon'],
                        'timezone': geo_data['timezone'],
                        'query': proxy_ip,
                        # Include 'proxyusername' and 'proxy_password' if needed
                    }
                )

                messages.success(self.request, f"Profile for <strong>{proxy_string}</strong> has been updated successfully!")
            else:
                messages.error(self.request, "Failed to fetch geo data for the provided proxy.")
        else:
            messages.error(self.request, "Invalid proxy format.")
            return self.form_invalid(form)

        return response



class ViewProfiles(LoginRequiredMixin, TemplateView):
    template_name = "profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_list = Profile.objects.all().order_by('-id')

        column = self.request.GET.get('column')
        query = self.request.GET.get('query')

        if column and query:
            
            if column == 'proxy':
                order_list = order_list.filter(proxy__icontains=query)
            elif column == 'UserAgent':
                order_list = order_list.filter(UserAgent__icontains=query)
            elif column == 'domain_type':
                order_list = order_list.filter(domain_type__icontains=query)
            elif column == 'serverID':
                order_list = order_list.filter(serverID__icontains=query)
        
        # Pagination
        page = self.request.GET.get('page', 1)
        paginator = Paginator(order_list, 5) 

        try:
            order_list = paginator.page(page)
        except PageNotAnInteger:
            order_list = paginator.page(1)
        except EmptyPage:
            order_list = paginator.page(paginator.num_pages)

        context['order_list'] = order_list
        return context
    







def profile_creation_view(request):
    if request.method == 'POST':
        form = CreateNewProfile(request.POST)
        if form.is_valid():
            profile = form.save()
            
            # Assuming 'proxy' field contains the IP address or proxy string
            proxy_ip = form.cleaned_data['proxy'].split(':')[0]  # Adjust based on your proxy string format
            
            # Here you should call your function to validate the proxy and get additional details
            # For simplicity, I'm using placeholders for the returned data
            proxy_details = get_location_and_timezone(proxy_ip)  # This should be your actual function call
            
            if proxy_details:
                ProxyDetail.objects.create(
                    proxy=profile,
                    status='valid',  # Set the status based on your check
                    country=proxy_details['country'],
                    countryCode=proxy_details['countryCode'],
                    region=proxy_details['region'],
                    regionName=proxy_details['regionName'],
                    city=proxy_details['city'],
                    zip=proxy_details['zip'],
                    lat=proxy_details['lat'],
                    lon=proxy_details['lon'],
                    timezone=proxy_details['timezone'],
                    query=proxy_ip
                )

            return redirect('some_view_name')  # Redirect as needed

    else:
        form = CreateNewProfile()

    return render(request, 'your_template.html', {'form': form})



def get_random_proxy(request, domain_type, no):
    # Filter Profiles with domain_type 'web' and inUsed False
    profiles = Profile.objects.filter(domain_type=domain_type, inUsed=False)

    if not profiles:
        #If there is no profile free, get one that has been used at least 4 minutes ago,
        #and make all profiles used 4 minutes ago as not used
        cutoff_time = timezone.now() - timedelta(minutes=4)
        profiles = Profile.objects.filter(last_fetched__lte=cutoff_time)
        profiles.update(inUsed=False)
        if not profiles:
            return JsonResponse({'error': 'No available profiles found'}, status=404)

    # Select a random profile from the filtered queryset
    random_profile = random.choice(profiles)

    # Get the ProxyDetails associated with the random profile
    try:
        proxy_details = ProxyDetail.objects.get(profile=random_profile)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'No proxy details found for the selected profile'}, status=404)

    # Format the proxy to only include IP and port
    proxy_ip_port = random_profile.proxy.split(':')[0:2]  # Assuming proxy format is IP:Port:Username:Password
    formatted_proxy = ':'.join(proxy_ip_port)

    # Prepare the data to be returned as JSON
    data = {
        "id": random_profile.id,
        'proxy': formatted_proxy,
        'UserAgent': random_profile.UserAgent,
        'country': proxy_details.country,
        'countryCode': proxy_details.countryCode,
        'region': proxy_details.region,
        'regionName': proxy_details.regionName,
        'city': proxy_details.city,
        'lat': proxy_details.lat,
        'long': proxy_details.lon,
        'timezone': proxy_details.timezone,
        'proxyusername': proxy_details.proxyusername,
        'proxypassword': proxy_details.proxy_password,
    }

    # Set the inUsed field of the profile to True now that it's being used
    random_profile.inUsed = True
    random_profile.serverID = ServerTable.objects.get(id=no)
    random_profile.save()
    print(random_profile)

    # Return the data as JSON
    return JsonResponse(data)

def get_random_proxy_details_web(request, no):
    print('NUMBER', no)
    data = get_random_proxy(request, 'web', no)
    return data

def get_random_proxy_details_mobile(request,no):
   data = get_random_proxy(request, 'mobile', no)
   return data

@csrf_exempt
def setProfileFree(request, pk):
    if request.method == 'POST' or request.method == 'GET':
        try:
            profile = Profile.objects.get(id=pk)
            profile.inUsed=False
            profile.save()
            return JsonResponse({'status': 'success', 'profile_id': profile.id, 'inUsed': profile.inUsed})
        except Order.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Profile not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


def get_number_of_profile_mobile(request):
    # Filter Profiles with domain_type 'web' and inUsed False
    profiles = Profile.objects.filter(domain_type='mobile', inUsed=False).count()
    print(profiles)
    return JsonResponse({"no":profiles})




def update_order_action(request):
    if request.method == 'POST':
        form = OrderActionForm(request.POST)
        if form.is_valid():
            keyword_id = form.cleaned_data['keyword_id']
            order_id = form.cleaned_data['order_id']
            action = form.cleaned_data['action']
            second_action = form.cleaned_data.get('second_action')

            order = get_object_or_404(Order, id=keyword_id)
            order.action = action
            if second_action:
                order.second_action = second_action
            order.active = True
            order.save()
            keyword = get_object_or_404(Keyword,id=order_id)
            keyword.status = "In Progress"
            keyword.save()

            url = reverse('orders:ViewKeyword')
            return HttpResponseRedirect(url)
        else:
            print(form.errors)  # Debug: print form errors
    else:
        form = OrderActionForm()

    return redirect("orders:ViewKeyword")


@csrf_exempt
def update_reached_users(request, order_id):
    if request.method == 'POST' or request.method == 'GET':
        try:
            keyword = Keyword.objects.get(keyword__id=order_id)
            order = keyword.keyword
            keyword.status = "In Progress"
            order.reached_users += 1
            if order.reached_users >= order.num_users:
                keyword.status = "Done"
                order.active = False
            order.save()
            keyword.save()
            return JsonResponse({'status': 'success', 'order_id': order.id, 'reached_users': order.reached_users, 'total_users': order.num_users})
        except Order.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Order not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)