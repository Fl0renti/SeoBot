from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import PasswordChangeView
from django.views import generic 
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


from .forms import SignUpForm, PasswordChangeFormCustom, UserUpdateForm

class UsersListView(LoginRequiredMixin, generic.ListView):
    model = User
    template_name = "users.html"
    context_object_name = "users"
    paginate_by = 6 

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('orders:list_of_orders')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return User.objects.all().order_by('-date_joined')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Pagination
        users_list = self.get_queryset()
        page = self.request.GET.get('page', 1)
        paginator = Paginator(users_list, self.paginate_by)

        try:
            users_list = paginator.page(page)
        except PageNotAnInteger:
            users_list = paginator.page(1)
        except EmptyPage:
            users_list = paginator.page(paginator.num_pages)
        
        context['users'] = users_list
        return context


class UserDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = User
    template_name = "delete_user.html"
    success_url = reverse_lazy("accounts:users")

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk', None)
        return get_object_or_404(User, pk=pk)
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('orders:list_of_orders') 
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, f"User&nbsp;<strong>{self.object.username}</strong>&nbsp;deleted successfully!")
        return response
    

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"User&nbsp;<strong>{self.object.username}</strong>&nbsp;deleted successfully!")
        return response


class UserUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = User
    template_name = "update_user.html"
    form_class = UserUpdateForm
    success_url = "accounts:users"

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk', None)
        return get_object_or_404(User, pk=pk)

    def get_success_url(self):
        return reverse_lazy('accounts:users')  # Redirect to the user list after successful update

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('orders:list_of_orders')  # Redirect to home if user is not staff
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"User&nbsp;<strong>{self.object.username}</strong>&nbsp;updated successfully!")
        return response


class CreateAccessUser(LoginRequiredMixin, generic.CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy("accounts:users")
    template_name = "registration/new_access_user.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('orders:list_of_orders') 
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"User&nbsp;<strong>{self.object.username}</strong>&nbsp;successfully is created!")
        return response


class PasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = PasswordChangeFormCustom
    success_url = reverse_lazy('accounts:change_password')
    template_name = "registration/change_password.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Password changed successfully!')
        return response


def password_success(request):
    return render(request, 'registration/password_success.html', {})