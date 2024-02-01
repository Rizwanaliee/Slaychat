from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .models import *
from django.db.models import Q
from django.core.paginator import Paginator

# Create your views here.

class QueryList(LoginRequiredMixin, ListView):
    model = QueryTicket
    paginate_by = 20
    template_name = 'support/query_list.html'
    queryset = QueryTicket.objects.all().order_by('-createdAt')
    context_object_name = 'Queries'
    login_url = 'admin-login'


@login_required(login_url='admin-login')
def searchUserFromTickt(request):
    try:
        search_key = request.POST.get('q').strip()
        tikets = QueryTicket.objects.filter(Q(userId__fullName__icontains=search_key) | Q(userId__email__icontains=search_key) | Q(userId__mobileNo__icontains=search_key)).all().order_by('-id')
        paginator = Paginator(tikets, 20)
        page = request.GET.get('page')
        page_obj = paginator.get_page(page)
        context = {
            'Queries': tikets,
            'page_obj': page_obj,
            'InputText': search_key
        }
        return render(request, 'support/query_list.html', context)
    except Exception as e:
        return redirect('query-list')

@login_required(login_url='admin-login')
def filterByStatusTicket(request):
    status = request.POST.get('filter_status_id')
    tickets = QueryTicket.objects.filter(Q(status=status) ).all().order_by('-id')
    paginator = Paginator(tickets, 20)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    context = {
        'Queries': tickets,
        'page_obj': page_obj,
        'SelectedType': status
    }
    return render(request, 'support/query_list.html', context)