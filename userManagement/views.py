from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from auth_APIs.models import User, Category, SubCategory, Company, DoerUserData,DoerSelectedSubCategory
from django.db.models import Q
from django.urls import reverse
from django.core.paginator import Paginator
from Helpers.helper import send_email_forget_pass,s3_helper
import uuid
from chatPanel.models import Job

# Create your views here.

def adminLogin(request):
    if request.method == "GET":
        return render(request, 'userManagement/adminLogin.html')
    else:
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(email=email, password=password)
        if user is None:
            messages.warning(request, 'Incorrect username/password')
            return redirect('admin-login')
        else:
            if user.is_superuser == 1:
                login(request, user)
                return redirect('admin-dashboard')
            else:
                messages.warning(request, 'Not authenticate user')
            return redirect('admin-login')

@login_required(login_url='admin-login')
def adminDashboard(request):
    totalJobPosted = Job.objects.filter(Q(jobStatus=4) & Q(isJobShare=True)).all().count()
    context={
        "totalJobPosted":totalJobPosted
    }
    return render(request, 'userManagement/adminDashboard.html',context)

@login_required(login_url='admin-login')
def logoutAdmin(request):
    logout(request)
    return redirect('admin-login')

class CustomerUsers(ListView, LoginRequiredMixin):
    model = User
    paginate_by = 20
    template_name = 'userManagement/customerUsers.html'
    queryset = User.objects.filter(Q(userTypeId=1) & Q(
        isDeleted=False) & Q(is_superuser=False)).all().order_by('-id')
    context_object_name = 'customerUsers'
    login_url = 'admin-login'

@login_required(login_url='admin-login')
def customerViewDetail(request, userId):
    user = User.objects.filter(id=userId).first()
    context={
        "User":user,
    }
    return render(request,'userManagement/customerViewDetail.html',context)

@login_required(login_url='admin-login')
def blockUnblock(request, userId):
    user = User.objects.get(id=userId)
    if(user.isActive == True):
        user.isActive = False
        user.save()
        if user.userTypeId.id == 1:
            res = reverse('customer-users')
        else:
            res = reverse('approved-users-doer')
        if 'page' in request.GET:
            res += f"?page={request.GET['page']}"
        return redirect(res)
    else:
        user.isActive = True
        user.save()
        if user.userTypeId.id == 1:
            res = reverse('customer-users')
        else:
            res = reverse('approved-users-doer')
        if 'page' in request.GET:
            res += f"?page={request.GET['page']}"
        return redirect(res)

@login_required(login_url='admin-login')
def deleteUser(request):
    userId = request.POST.get('user_id')
    user = User.objects.filter(id=userId).first()
    if user.userTypeId.id == 1:
        user.isDeleted = True
        user.save()
        return redirect('customer-users')
    else:
        user.isDeleted = True
        user.save()
        if user.isApproved == 1:
            return redirect('doer-usr-requests')
        else:
            return redirect('approved-users-doer')

@login_required(login_url='admin-login')
def searchUserPetient(request):
    try:
        search_key = request.POST.get('q').strip()
        query1 = Q(fullName__icontains=search_key) | Q(
            email__icontains=search_key) | Q(
            mobileNo__icontains=search_key)
        users = User.objects.filter((Q(query1) & Q(userTypeId=1) & Q(
            isDeleted=False))).all().order_by('-id')
        paginator = Paginator(users, 20)
        page = request.GET.get('page')
        page_obj = paginator.get_page(page)
        context = {
            'customerUsers': users,
            'page_obj': page_obj,
            'InputText': search_key
        }
        return render(request, 'userManagement/customerUsers.html', context)
    except Exception as e:
        return redirect('customer-users')

@login_required(login_url='admin-login')
def filterByStatusActiveBlock(request):
    status = request.POST.get('filter_status_id')
    users = User.objects.filter(Q(userTypeId=1) & Q(
        isDeleted=False) & Q(isActive=status)).all().order_by('-id')
    paginator = Paginator(users, 20)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    context = {
        'customerUsers': users,
        'page_obj': page_obj,
        'SelectedType': status
    }
    return render(request, 'userManagement/customerUsers.html', context)


def admin_forget_password(request):
    if(request.method == 'GET'):
        return render(request, 'userManagement/admin_forget_pass.html')
    else:
        email = request.POST.get('email')
        if not User.objects.filter(Q(email=email) & Q(is_superuser=True)).first():
            messages.warning(request, 'User Not Found')
            return redirect('admin-forget-password')
        user_obj = User.objects.get(email=email)
        token = str(uuid.uuid4())
        user_obj.admin_forget_password_token = token
        user_obj.save()
        send_email_forget_pass(user_obj.email, token)
        messages.success(
            request, 'An email has been sent please check your email account')
        return redirect('admin-login')


def admin_change_password(request, token):
    if(request.method == 'GET'):
        obj = User.objects.get(admin_forget_password_token=token)
        Context = {"user_id": obj.id}
        return render(request, 'userManagement/admin-change-password.html', Context)
    else:
        new_password = request.POST.get('new_pass')
        confirm_new_pass = request.POST.get('confirm_new_pass')
        user_id = User.objects.get(admin_forget_password_token=token)
        if not user_id:
            messages.warning(request, 'User not found')
            return redirect('set-new-admin-password', user_id.admin_forget_password_token)
        if new_password != confirm_new_pass:
            messages.warning(
                request, 'Password & confirm password does not match')
            return redirect('set-new-admin-password', user_id.admin_forget_password_token)
        user_obj = User.objects.get(id=user_id.id)
        user_obj.set_password(new_password)
        user_obj.save()
        messages.success(request, 'Your password successfully updated')
        return redirect('admin-login')


class DoerUserRequest(ListView, LoginRequiredMixin):
    model = User
    paginate_by = 20
    template_name = 'userManagement/doerUserRequests.html'
    queryset = User.objects.filter(Q(userTypeId=2) & Q(
        isDeleted=False) & Q(isApproved__in=[1, 3]) & Q(isVerified=True)).order_by('-id')
    context_object_name = 'doerUsers'
    login_url = 'admin-login'

@login_required(login_url='admin-login')
def viewDetail(request, userId):
    user = User.objects.filter(id=userId).first()
    doerData = DoerUserData.objects.filter(userId=user).first()
    services = DoerSelectedSubCategory.objects.filter(doerDataId=doerData).all()
    context={
        "User":user,
        "DoerData":doerData,
        "Servicess":services
    }
    return render(request,'userManagement/viewDetail.html',context)


@login_required(login_url='admin-login')
def changeRequestStatus(request, status, userId):
    user = User.objects.filter(id=userId).first()
    if not user:
        messages.warning(request, 'Incorrect userId')
        return redirect('doer-usr-requests')
    if status == 2:
        user.isApproved = status
        user.save()
    if status == 3:
        user.isApproved = status
        user.save()
    return redirect('doer-usr-requests')


@login_required(login_url='admin-login')
def searchUserRequest(request):
    try:
        search_key = request.POST.get('q').strip()
        query1 = Q(fullName__icontains=search_key) | Q(
            email__icontains=search_key) | Q(
            mobileNo__icontains=search_key)
        users = User.objects.filter((Q(query1) & Q(userTypeId=2) & Q(
            isDeleted=False) & Q(isApproved__in=[1, 3]))).all().order_by('-id')
        paginator = Paginator(users, 20)
        page = request.GET.get('page')
        page_obj = paginator.get_page(page)
        context = {
            'doerUsers': users,
            'page_obj': page_obj,
            'InputText': search_key
        }
        return render(request, 'userManagement/doerUserRequests.html', context)
    except Exception as e:
        return redirect('doer-usr-requests')


@login_required(login_url='admin-login')
def filterByStatus(request):
    status = request.POST.get('filter_status_id')
    users = User.objects.filter(Q(userTypeId=2) & Q(
        isDeleted=False) & Q(isApproved=status)).all().order_by('-id')
    paginator = Paginator(users, 20)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    context = {
        'doerUsers': users,
        'page_obj': page_obj,
        'SelectedType': status
    }
    return render(request, 'userManagement/doerUserRequests.html', context)


class DoerApprovedUsers(ListView, LoginRequiredMixin):
    model = User
    paginate_by = 20
    template_name = 'userManagement/doerApprovedUsers.html'
    queryset = User.objects.filter(Q(userTypeId=2) & Q(
        isDeleted=False) & Q(isApproved=2) & Q(isVerified=True)).order_by('-id')
    context_object_name = 'approvedUsers'
    login_url = 'admin-login'

@login_required(login_url='admin-login')
def searchUserApproved(request):
    try:
        search_key = request.POST.get('q')
        query1 = Q(fullName__icontains=search_key) | Q(
            email__icontains=search_key) | Q(
            mobileNo__icontains=search_key)
        users = User.objects.filter((Q(query1) & Q(userTypeId=2) & Q(
            isDeleted=False) & Q(isApproved=2) & Q(isVerified=True))).all().order_by('-id')
        paginator = Paginator(users, 20)
        page = request.GET.get('page')
        page_obj = paginator.get_page(page)
        context = {
            'approvedUsers': users,
            'page_obj': page_obj,
            'InputText': search_key
        }
        return render(request, 'userManagement/doerApprovedUsers.html', context)
    except Exception as e:
        return redirect('approved-users-doer')


def filterByStatusApproved(request):
    status = request.POST.get('filter_status_id')
    users = User.objects.filter(Q(userTypeId=2) & Q(
        isDeleted=False) & Q(isApproved=2) & Q(isActive=status) & Q(isVerified=True)).all().order_by('-id')
    paginator = Paginator(users, 20)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    context = {
        'approvedUsers': users,
        'page_obj': page_obj,
        'SelectedType': status
    }
    return render(request, 'userManagement/doerApprovedUsers.html', context)

class AdminCategoryRequestList(ListView, LoginRequiredMixin):
    model = Category
    paginate_by = 20
    template_name = 'userManagement/adminCategoryRequest.html'
    queryset = Category.objects.filter(Q(
        isApproved=True)).order_by('-id')
    context_object_name = 'adminCatList'
    login_url = 'admin-login'

class CategoryRequestList(ListView, LoginRequiredMixin):
    model = Category
    paginate_by = 20
    template_name = 'userManagement/doerCategoryRequest.html'
    queryset = Category.objects.filter(Q(catAddedBy=2) & Q(
        isApproved=False)).order_by('-id')
    context_object_name = 'doerCatList'
    login_url = 'admin-login'

@login_required(login_url='admin-login')
def rejectDoerCategoryRequest(request,catId):
    cat = Category.objects.filter(id=catId)
    if not cat:
        messages.warning(request, 'Invalid category id')
        return redirect('doer-cat-request-list')
    Category.objects.filter(id=catId).delete()
    messages.success(request, 'Rejected successfully')
    return redirect('doer-cat-request-list')

@login_required(login_url='admin-login')
def approveDoerCategoryRequest(request,catId):
    cat = Category.objects.filter(id=catId)
    if not cat:
        messages.warning(request, 'Invalid category id')
        return redirect('doer-cat-request-list')
    Category.objects.filter(id=catId).update(isApproved=True)
    messages.success(request, 'Approved successfully')
    return redirect('doer-cat-request-list')

@login_required(login_url='admin-login')
def addCategory(request):
    if request.method=="GET":
        return render(request,'userManagement/addCategory.html')
    else:
        category = request.POST.get('category')
        # image =request.FILES.get('catImage')
        subCatNames = request.POST.getlist('subCatName[]')
        if Category.objects.filter(catName__icontains=category).exists():
            messages.warning(request, 'Category already exists')
            return redirect('add-category')
        # url = s3_helper(image)
        cat = Category.objects.create(catName=category, catAddedBy=1,isApproved=True,userId=request.user)
        for name in subCatNames:
            SubCategory.objects.create(subCatName=name, catId=cat)

        return redirect('admin-cat-list')

@login_required(login_url='admin-login')
def editCategory(request, catId):
    if request.method=="GET":
        cat = Category.objects.filter(id=catId).first()
        subCatList = SubCategory.objects.filter(catId=catId).all()
        context = {
            "Category":cat,
            "SubCategory":subCatList

        }
        return render(request,'userManagement/editCategory.html',context)
    else:
        category = request.POST.get('category')
        Category.objects.filter(id=catId).update(catName=category)
        if  Category.objects.filter(Q(id=catId)& Q(isApproved=True)).exists():
            return redirect('admin-cat-list')
        return redirect('doer-cat-request-list')

@login_required(login_url='admin-login')
def viewDetailsAdmin(request, catId):
    cat = Category.objects.filter(id=catId).first()
    subCatList = SubCategory.objects.filter(catId=catId).all()
    context={
        "Category":cat,
        "SubCategory":subCatList 
    }
    return render(request, 'userManagement/catDetailAdmin.html',context)

@login_required(login_url='admin-login')
def addSubCategory(request, catId):
    if request.method=="GET":
        return render(request,'userManagement/addSubCategory.html')
    else:
        cat = Category.objects.filter(id=catId).first()
        category = request.POST.get('subcategory')
        SubCategory.objects.create(subCatName=category, catId=cat)
        return redirect('edit-category',catId)

@login_required(login_url='admin-login')
def editSubCategory(request, subCatId):
    if request.method=="GET":
        subCat = SubCategory.objects.filter(id=subCatId).first()
        return render(request,'userManagement/editSubCategory.html',{"SubCategory":subCat})
    else:
        cat = SubCategory.objects.filter(id=subCatId).first()
        category = request.POST.get('subcategory')
        SubCategory.objects.filter(id=subCatId).update(subCatName=category)
        return redirect('edit-category', cat.catId.id)


class CompanyList(ListView, LoginRequiredMixin):
    model = Company
    paginate_by = 20
    template_name = 'userManagement/companyList.html'
    queryset = Company.objects.filter(Q(companyType=2) & Q(isApproved=True)).order_by('-id')
    context_object_name = 'companyList'
    login_url = 'admin-login'

class RequestCompanyList(ListView, LoginRequiredMixin):
    model = Company
    paginate_by = 20
    template_name = 'userManagement/requestCompanyList.html'
    queryset = Company.objects.filter(Q(companyType=2) & Q(isApproved=False)).order_by('-id')
    context_object_name = 'companyList'
    login_url = 'admin-login'

@login_required(login_url='admin-login')
def approveDoerCompanyRequest(request,compId):
    cap = Company.objects.filter(id=compId)
    if not cap:
        messages.warning(request, 'Invalid company id')
        return redirect('request-comp-list')
    Company.objects.filter(id=compId).update(isApproved=True)
    return redirect('request-comp-list')

@login_required(login_url='admin-login')
def rejectDoerCompanyRequest(request,compId):
    cap = Company.objects.filter(id=compId)
    if not cap:
        messages.warning(request, 'Invalid company id')
        return redirect('request-comp-list')
    Company.objects.filter(id=compId).delete()
    return redirect('request-comp-list')

@login_required(login_url='admin-login')
def addCompany(request):
    if request.method=="GET":
        return render(request,'userManagement/addCompany.html')
    else:
        name= request.POST.get('name')
        addrss = request.POST.get('address')
        logo = request.FILES.get('compImage')
        Company.objects.create(companyName=name,address=addrss,logo=s3_helper(logo),companyType=2, isApproved=True)
        return redirect('company-list')

@login_required(login_url='admin-login')
def editCompany(request, compId):
    if request.method=="GET":
        comp = Company.objects.filter(id=compId).first()
        return render(request,'userManagement/editCompany.html',{"Company":comp})
    else:
        name= request.POST.get('name')
        addrss = request.POST.get('address')
        logo = request.FILES.get('compImage')
        if logo:
            Company.objects.filter(id=compId).update(companyName=name,address=addrss,logo=s3_helper(logo))
        Company.objects.filter(id=compId).update(companyName=name,address=addrss)
        comp = Company.objects.filter(id=compId).first()
        if comp.isApproved == True:
            return redirect('company-list')
        else:
            return redirect('request-comp-list')