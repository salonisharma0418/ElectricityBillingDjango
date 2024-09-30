from django.shortcuts import render,redirect,HttpResponseRedirect
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import authenticate, logout, login
from django.db.models import Q
from datetime import date
from decimal import Decimal
import sweetify
from .forms import RegistrationForm
import pytesseract
import cv2
from .forms import ImageUploadForm
from datetime import date, timedelta
from .models import Connection, Unitrate, Bill
# from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist


# Create your views here.
from datetime import datetime
def get_previous_month(date):
    first_day_of_current_month = date.replace(day=1)
    last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
    return last_day_of_previous_month

def index(request):
    error = ""
    if request.method == 'POST':
        sd = request.POST['searchdata']
        connection = Connection.objects.filter(connectionid=sd).first()
        # viewbill = Bill.objects.filter(connection=connection,status='Not Paid')
        viewbill = Bill.objects.filter(connection=connection,status='Not Paid').values()
        for item in viewbill:
            bill = Bill.objects.get(id=item['id'])
            aa = Connection.objects.get(connectionid=bill.connection.connectionid)
            load = float(aa.connectionload)

            if 0 < load < 6:
                charge = 20
            elif 5 < load < 11:
                charge = 30
            else:
                charge = 40
            total_load = load * charge

            current_year = datetime.now().year
            current_date = datetime.now()
            previous_month_date = get_previous_month(current_date)

            pre_bill = Bill.objects.filter(
                connection=bill.connection,
                billformonth__month=previous_month_date.month,
                billformonth__year=current_year
            ).first()

            if not pre_bill:
                pre_bill = 0
                amou_data = 0
            else:
                amou_data = (float(pre_bill.total_bill_amt) * 9.1) / 100

            duty_amo = float(amou_data) + float(bill.total_bill_amt)
            per_amo_duty = (float(duty_amo) * 11) / 100
            bill_data = Bill_cal.objects.filter(total=item['id'])
            data = bill.total_bill_amt

            govt_amount = (float(data) + float(total_load) + float(amou_data)) / 2
            bb = Bill_cess.objects.get(cess_total=bill)
            cess_to_amou = bb.cess_amount
            other_cha= 1.9
            final = (float(data) + float(total_load) + float(amou_data) +float(per_amo_duty) + float(cess_to_amou)) - float(govt_amount)
            final-= float(other_cha)
            print(final)
            item['final']=final
            item['bp_no']=aa.connectionid
        return render(request, 'viewmybill.html', locals())
    return render(request,'index.html', locals())

def about(request):
    return  render(request, 'about.html')

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        email = request.POST.get('email')
        password1 = request.POST.get('password')
        password2 = request.POST.get('password2')

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            sweetify.error(request, 'Email already exists!')
            print('Email already exists!')
            return render(request, 'register.html', {'error': 'Email already exists!', 'Registration_Form': form})

        # Validate the form and passwords
        if form.is_valid():
            if password1 != password2:
                sweetify.error(request, 'Passwords do not match!')
                return render(request, 'register.html', {'error': 'Passwords do not match!', 'Registration_Form': form})

            user = form.save(commit=False)  # Create a new user object but don't save it yet
            user.set_password(password1)  # Set the password for the user
            user.save()  # Save the user to the database
            sweetify.success(request, 'Registration Successful')
            print('-----------------')
            return redirect('admin_login')  # Use redirect() instead of HttpResponseRedirect

        else:
            sweetify.error(request, 'Invalid form submission')
            return render(request, 'register.html', {'error': 'Invalid form submission', 'Registration_Form': form})

    else:
        form = RegistrationForm()

        return render(request, 'register.html', {'Registration_Form': form})

def admin_login(request):
    error = ""
    if request.method == 'POST':
        u = request.POST['uname']
        p = request.POST['pwd']
        user = authenticate(username=u, password=p)
        try:
            if user.is_staff:
                login(request, user)
                error = "no"
            else:
                error = "yes"
        except:
            error = "yes"
    return render(request,'admin_login.html', locals())


def admin_home(request):
    if not request.user.is_staff:
        return redirect('admin_login')
    cus = Customer.objects.all().count()
    conn = Connection.objects.all().count()
    b = Bill.objects.all().count()

    d = {'cus': cus, 'conn': conn, 'b': b}
    return render(request,'admin_home.html', d)

def add_Customer(request):
    error = ""
    if request.method == "POST":
        fn = request.POST['firstname']
        ln = request.POST['lastname']
        c = request.POST['contact']
        e = request.POST['email']
        a = request.POST['address']
        city = request.POST['city']
        s = request.POST['state']
        try:
            user = User.objects.create_user(first_name=fn, last_name=ln, username=e)
            Customer.objects.create(user=user, contact=c, address=a, city=city, state=s)
            error = "no"
        except:
            error = "yes"
    return render(request,'add_Customer.html', locals())

def view_Customer(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    customer = Customer.objects.all()
    return render(request,'view_Customer.html', locals())

def edit_Customer(request,pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    user = User.objects.get(id=request.user.id)
    customer = Customer.objects.get(id=pid)
    error = False
    if request.method == 'POST':
        fn = request.POST['firstname']
        ln = request.POST['lastname']
        c = request.POST['contact']
        a = request.POST['address']
        city = request.POST['city']
        s = request.POST['state']

        user.first_name = fn
        user.last_name = ln
        customer.contact = c
        customer.address = a
        customer.city = city
        customer.state = s
        user.save()
        customer.save()
        error = True

    d = {'customer': customer, 'user': user, 'error': error}
    return  render(request, 'edit_Customer.html', locals())

def delete_Customer(request,pid):
    customer = Customer.objects.get(id=pid)
    customer.delete()
    return redirect('view_Customer')

def add_Connection(request):
    if not request.user.is_authenticated:
        return redirect(admin_login)
    error = ""
    customer1 = Customer.objects.all()
    if request.method == "POST":
        # cid = request.POST['connectionid']
        customerid = request.POST['customerid']
        ctype = request.POST['connectiontype']
        cdate = request.POST['connectionstartdate']
        o = request.POST['occupation']
        cload = request.POST['connectionload']
        pno = request.POST['plotno']
        c = request.POST['city']
        p = request.POST['pincode']
        a = request.POST['address']
        s = request.POST['state']
        d = request.POST['description']

        customer = Customer.objects.get(id=customerid)
        try:
            Connection.objects.create(customer=customer, connectiontype=ctype, connectionstartdate=cdate, occupation=o,
                                      connectionload=cload, plotno=pno, city=c, pincode=p, address=a, state=s, description=d)
            error = "no"
        except:
            error = "yes"
    return render(request,'add_Connection.html', locals())

def view_Connection(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    connection = Connection.objects.all()
    return render(request,'view_Connection.html', locals())

def edit_Connection(request,pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    customer = Customer.objects.all()
    connection = Connection.objects.get(connectionid=pid)
    error = False
    if request.method == 'POST':
        cid = request.POST['connectionid']
        customerid = request.POST['customerid']
        ctype = request.POST['connectiontype']
        cdate = request.POST['connectionstartdate']
        o = request.POST['occupation']
        cload = request.POST['connectionload']
        pno = request.POST['plotno']
        c = request.POST['city']
        p = request.POST['pincode']
        a = request.POST['address']
        s = request.POST['state']
        d = request.POST['description']

        customer1 = Customer.objects.get(id=customerid)

        connection.customer = customer1
        connection.connectiontype = ctype
        connection.occupation = o
        connection.connectionload = cload
        connection.plotno = pno
        connection.city = c
        connection.pincode = p
        connection.address = a
        connection.state = s
        connection.description = d
        if cdate:
            connection.connectionstartdate = cdate
        connection.save()
        error = True

    d = {'connection': connection, 'customer': customer, 'error': error}
    return  render(request, 'edit_Connection.html', locals())

def delete_Connection(request,pid):
    connection = Connection.objects.get(connectionid=pid)
    connection.delete()
    return redirect('view_Connection')

from datetime import date, timedelta
from django.shortcuts import render, redirect
from django.utils import timezone
from decimal import Decimal
import pdb 

def add_Bill(request):
    pdb.set_trace()
    current_date = date.today()
    if not request.user.is_authenticated:
        return redirect('admin_login')
    error = ""
    connection1 = Connection.objects.all()
    if request.method == "POST":
        connectionid = request.POST['connectionid']
        b = current_date
        creading = request.POST['currentreading']
        
        # Fetch the previous month's bill and get the current reading as previous reading
        try:
            previous_month = (current_date.replace(day=1) - timedelta(days=1)).month
            previous_year = (current_date.replace(day=1) - timedelta(days=1)).year
            previous_bill = Bill.objects.get(connection__connectionid=connectionid, billformonth__month=previous_month, billformonth__year=previous_year)
            preading = previous_bill.currentreading
        except Bill.DoesNotExist:
            preading = 0  # Default value if no previous reading found

        total_units = float(creading) - float(preading)
        dd = current_date + timedelta(days=10)
        connection = Connection.objects.get(connectionid=connectionid)
        
        def calculate_load_charge(load):
            if 0 < load < 6:
                charge = 20
            elif 5 < load < 11:
                charge = 30
            else:
                charge = 40
            return charge

        finalamount = 0
        l = []
        remaining_units = total_units
        for rateobj in Unitrate.objects.order_by('initialunit'):
            d = {'unit': 0, 'rate': 0, 'rate_details': "Rs/U", 'amount': 0}
            
            if remaining_units > 0:
                units_in_slab = min(remaining_units, rateobj.finalunit - rateobj.initialunit)
                d['unit'] = rateobj.unitrate
                d['rate'] = units_in_slab
                d['amount'] = units_in_slab * rateobj.unitrate
                finalamount += units_in_slab * rateobj.unitrate
                finalamount += calculate_load_charge(int(connection.connectionload))
                
                remaining_units -= units_in_slab
                l.append(d)
            else:
                break

        try:
            month = current_date.month
            year = current_date.year
            check_data = Bill.objects.filter(connection=connection, billformonth__month=month, billformonth__year=year).exists()
            if check_data:
                error = "yes"
            else:
                total_bill_amt = sum(d['amount'] for d in l)
                bill_data = Bill.objects.create(
                    connection=connection,
                    billformonth=b,
                    currentreading=creading,
                    previousreading=preading,
                    totalunit=Decimal(total_units),
                    chargeperunit=rateobj.unitrate,
                    finalamount=Decimal(finalamount),
                    duedate=dd,
                    status='Not Paid',
                    total_bill_amt=total_bill_amt
                )
                if bill_data:
                    for item in l:
                        Bill_cal.objects.create(
                            unit=item['unit'],
                            rate=item['rate'],
                            rate_details="Rs/U",
                            amount=item['amount'],
                            total=bill_data
                        )
                    Bill_load.objects.create(
                    load = float(connection.connectionload),
                    load_rate = calculate_load_charge(int(connection.connectionload)),
                    load_rate_details ='Rs/KW',
                    load_amount = float(connection.connectionload)*float(calculate_load_charge(int(connection.connectionload))),
                    load_total = bill_data,   
                    )
                    Bill_fppas.objects.create(
                    fppas = total_bill_amt ,
                    fppas_rate = "9.10",
                    fppas_rate_details = '%@(pre Month EC)',
                    fppas_amount = float(total_bill_amt)*(9.10/100),
                    fppas_total = bill_data,

                    )
                    Bill_cess.objects.create(
                    cess = total_units,
                    cess_rate = 10,
                    cess_rate_details = "Paise/U",
                    cess_amount = (total_units*10)/100,
                    cess_total = bill_data,   
                    )
                    Bill_duty.objects.create(
                    duty = "",
                    duty_rate = 11,
                    duty_rate_details = "Paise/U",
                    duty_amount = (total_units*10)/100,
                    duty_total = bill_data,   
                    )
                    print(preading)
                error = "no"

        except Exception as e:
            print(e)
            error = "yes"
    return render(request, 'add_Bill.html', locals())



def view_Bill(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    viewbill = Bill.objects.all().values()
    for item in viewbill:
            bill = Bill.objects.get(id=item['id'])
            aa = Connection.objects.get(connectionid=bill.connection.connectionid)
            load = float(aa.connectionload)

            if 0 < load < 6:
                charge = 20
            elif 5 < load < 11:
                charge = 30
            else:
                charge = 40
            total_load = load * charge

            current_year = datetime.now().year
            current_date = datetime.now()
            previous_month_date = get_previous_month(current_date)

            pre_bill = Bill.objects.filter(
                connection=bill.connection,
                billformonth__month=previous_month_date.month,
                billformonth__year=current_year
            ).first()

            if not pre_bill:
                pre_bill = 0
                amou_data = 0
            else:
                amou_data = (float(pre_bill.total_bill_amt) * 9.1) / 100

            duty_amo = float(amou_data) + float(bill.total_bill_amt)
            per_amo_duty = (float(duty_amo) * 11) / 100
            bill_data = Bill_cal.objects.filter(total=item['id'])
            data = bill.total_bill_amt

            govt_amount = (float(data) + float(total_load) + float(amou_data)) / 2
            bb = Bill_cess.objects.get(cess_total=bill)
            cess_to_amou = bb.cess_amount
            other_cha=1.9
            final = (
                float(data) + float(total_load) + float(amou_data) +
                float(per_amo_duty) + float(cess_to_amou)
            ) - float(govt_amount)
            final-=float(other_cha)
            print(final)
            item['final']=final
            item['bp_no']=aa.connectionid
    return render(request,'view_Bill.html', locals())

def delete_Bill(request,pid):
    bill = Bill.objects.get(id=pid)
    bill.delete()
    return redirect('view_Bill')

def change_password(request):
    if not request.user.is_authenticated:
        return redirect('index')
    error = ""
    user = request.user
    if request.method == "POST":
        o = request.POST['oldpassword']
        n = request.POST['newpassword']
        try:
            u = User.objects.get(id=request.user.id)
            if user.check_password(o):
                u.set_password(n)
                u.save()
                error = "no"
            else:
                error = 'not'
        except:
            error = "yes"
    return render(request,'change_password.html', locals())

def Logout(request):
    logout(request)
    return redirect('index')

def payment(request,pid):
    error = ""
    bill = Bill.objects.get(id=pid)
    if request.method == "POST":
        bill.status = "paid"
        try:
            bill.save()
            error = "no"
        except:
            error = "yes"
    return render(request,'payment.html', locals())

def viewmybill(request):
    return render(request,'viewmybill.html', locals())


def billDetialsPage(request, pid):
    from datetime import datetime

    bill = Bill.objects.get(id=pid)
    aa = Connection.objects.get(connectionid=bill.connection.connectionid)
    load = float(aa.connectionload)

    if 0 < load < 6:
        charge = 20
    elif 5 < load < 11:
        charge = 30
    else:
        charge = 40
    total_load = load * charge

    current_year = datetime.now().year
    current_date = datetime.now()
    previous_month_date = get_previous_month(current_date)

    pre_bill = Bill.objects.filter(
        connection=bill.connection,
        billformonth__month=previous_month_date.month,
        billformonth__year=current_year
    ).first()

    if not pre_bill:
        pre_bill = 0
        amou_data = 0
    else:
        amou_data = (float(pre_bill.total_bill_amt) * 9.1) / 100

    duty_amo = float(amou_data) + float(bill.total_bill_amt)
    per_amo_duty = (float(duty_amo) * 11) / 100
    bill_data = Bill_cal.objects.filter(total=pid)
    data = bill.total_bill_amt

    govt_amount = (float(data) + float(total_load) + float(amou_data)) / 2
    bb = Bill_cess.objects.get(cess_total=bill)
    cess_to_amou = bb.cess_amount
    other_cha= 1.9

    final = ((
        float(data) + float(total_load) + float(amou_data) +
        float(per_amo_duty) + float(cess_to_amou)
    ) - float(govt_amount))-float(other_cha)

    bill_load = Bill_load.objects.filter(load_total=pid)
    bill_fppas = Bill_fppas.objects.filter(fppas_total=pid)
    bill_cess = Bill_cess.objects.filter(cess_total=pid)
    bill_duty = Bill_duty.objects.filter(duty_total=pid)

    return render(request, 'BillDetails.html', locals())


def image_upload_view(request):
    extracted_text = ""
    aadhar_number = ""
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_instance = form.save()
            image_path = image_instance.image.path

            # Read image using OpenCV
            img = cv2.imread(image_path)

            # Convert image to string using Pytesseract
            extracted_text = pytesseract.image_to_string(img)

            # Extract Aadhar number
            import re
            aadhar_pattern = re.compile(r'\b\d{4}\s\d{4}\s\d{4}\b')
            match = aadhar_pattern.search(extracted_text)
            if match:
                aadhar_number = match.group()

    else:
        form = ImageUploadForm()
    return render(request, 'upload.html', {'form': form, 'extracted_text': extracted_text, 'aadhar_number': aadhar_number})

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        contactus = ContactUs(
            name=name,
            email=email,
            message=message,
        )
        contactus.save()
        return redirect('thank_you')
    return render(request, 'contact.html')

def helpme(request):
    return render(request, 'helpme.html')


def submit_feedback(request):
    if request.method == 'POST':
        satisfaction = request.POST.get('satisfaction')
        ease_of_use = request.POST.get('ease_of_use')
        features_like = request.POST.get('features_like')
        additional_features = request.POST.get('additional_features')
        customer_support = request.POST.get('customer_support')
        billing_process = request.POST.get('billing_process')
        improvement_suggestions = request.POST.get('improvement_suggestions')
        additional_comments = request.POST.get('additional_comments')

        feedback = Feedback(
            satisfaction=satisfaction,
            ease_of_use=ease_of_use,
            features_like=features_like,
            additional_features=additional_features,
            customer_support=customer_support,
            billing_process=billing_process,
            improvement_suggestions=improvement_suggestions,
            additional_comments=additional_comments
        )
        feedback.save()
        return redirect('thank_you')
    return render(request, 'feedback.html')


def reportIssues(request):
    return render(request, 'repostIssues.html')


def teamandconditions(request):
    return render(request, 'teamandconditions.html')