from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy


from .forms import UserRegistrationForm, UserLogInForm, EditUserForm
from .models import Relation, Profile


class UserRegisterView(View):
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.warning(request, f'you are now logged in as {request.user.username}')
            return redirect('pages:home')
        return super().dispatch(request, *args, **kwargs)
    

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form' : form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            User.objects.create_user(cd['username'], cd['email'], cd['password1'])
            messages.success(request, 'you registered successfully', 'success')
            return redirect('accounts:user_login')
        return render(request, self.template_name, {'form' : form})


class UserLogInView(View):
    form_class = UserLogInForm
    template_name = 'accounts/login.html'

    def setup(self, request, *args, **kwargs):
        self.next = request.GET.get('next')
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.warning(request, f'you are now logged in as {request.user.username}')
            return redirect('pages:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form':form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user is not None:
                login(request, user)
                messages.success(request, 'You are successfully logged in', 'success')
                if self.next:
                    return redirect(self.next)
                return redirect('pages:home')
            messages.error(request, 'Wrong password or username', 'danger')
        return render(request, self.template_name, {'form':form})  


class UserLogOutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.success(request, 'you are logged out successfully', 'success')
        return redirect('pages:home')


class UserProfileView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        is_following = False
        user = get_object_or_404(User, pk=user_id)
        posts = user.posts.all()
        relation = Relation.objects.filter(from_user=request.user, to_user=user)
        if relation.exists():
            is_following = True
        return render(request, 'accounts/profile.html', {'user':user, 'posts':posts, 'is_following':is_following})



class UserPasswordResetView(auth_views.PasswordResetView):
    template_name = 'accounts/password_reset_form.html'
    success_url = reverse_lazy('accounts:password_reset_done')
    email_template_name = 'accounts/password_reset_email.html'


class UserPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class UserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')


class UserPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'


class UserFollowView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        user = User.objects.get(id=user_id)
        relation = Relation.objects.filter(from_user=request.user, to_user=user)
        if relation.exists():
            messages.error(request, "you are already following this user")
        else:
            Relation(from_user=request.user, to_user=user).save()
            messages.success(request, 'you followed this user')
        return redirect('accounts:user_profile', user.id)


class UserUnfollowView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        user = User.objects.get(id=user_id)
        relation = Relation.objects.filter(from_user=request.user, to_user=user)
        if relation.exists():
            relation.delete()
            messages.success(request, "you unfollowed this user")
        else:
            messages.error(request, 'you are not following this user')
        return redirect('accounts:user_profile', user.id)


class EditUserView(LoginRequiredMixin, View):
    form_class = EditUserForm

    def get(self, request):
        form = self.form_class(instance=request.user.profile, initial={'email':request.user.email})
        return render(request, 'accounts/edit_profile.html', {'form':form})

    def post(self, request):
        form = self.form_class(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            request.user.email = form.cleaned_data['email']
            request.user.save()
            messages.success(request, 'your profile edited successfully')
        return redirect('accounts:user_profile', request.user.id)