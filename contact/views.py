from django.shortcuts import render, redirect
from django.contrib import auth
from django.http import HttpResponse
from contact import models
import csv
import random
import string
from datetime import datetime

# Create your views here.
def homepage(request):
    return redirect("/index/")


def index(request, pujaid=None):
    if not request.user.is_authenticated:
        return redirect("/login")

    if pujaid is not None:
        puja = models.PujaUnit.objects.get(id=pujaid)
        datalist = models.DataUnit.objects.filter(puja=puja).order_by("person__address")
        puja_name = "民國%d年 %s" % (puja.year, puja.name)
    else:
        puja_name = "請選擇法會"
        
    pujas = models.PujaUnit.objects.all()

    if request.method == "POST":
        puja_id = request.POST["puja_select"]
        return redirect("/index/%s" % puja_id)

    return render(request, "index.html", locals())


def downloadData(request, pujaid=None):
    if not request.user.is_authenticated:
        return redirect("/login")

    puja = models.PujaUnit.objects.get(id=pujaid)
    
    content_disposition = "attachment; filename=\"filename.csv\""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = content_disposition
    
    writer = csv.writer(response)

    title = ["姓名", "電話", "地址", "大牌/中牌"]
    writer.writerow(title)
        
    datalist = models.DataUnit.objects.filter(puja=puja).order_by("person__address")

    for data in datalist:
        info = list()
        info.append(data.person.name)
        info.append(data.person.contact)
        info.append(data.person.address)
        info.append(data.info_type)
        writer.writerow(info)

    return response


def search(request, searchquery=None):
    if not request.user.is_authenticated:
        return redirect("/login")

    if request.method == "POST":
        query = request.POST["query"]

        if query == "":
            return redirect("/search/")

        return redirect("/search/%s" % query)

    if searchquery:
        message = ""
        results = list()

        # Name -> Data
        datalist = models.DataUnit.objects.all().order_by("person__address", "person__name")
        
        for data in datalist:
            if searchquery in data.person.name:
                results.append(data)

        if len(results) > 0:
            message += "name"
            return render(request, "search.html", locals())

        # Address -> Person
        datalist = models.PersonUnit.objects.all().order_by("address", "name")
        
        for data in datalist:
            if searchquery in data.address:
                results.append(data)

        if len(results) > 0:
            message += "address"
            return render(request, "search.html", locals())

        message += "沒有找到相符項目"

    return render(request, "search.html", locals())


def pujalist(request):
    if not request.user.is_authenticated:
        return redirect("/login")

    pujas = models.PujaUnit.objects.all()
    return render(request, "pujalist.html", locals())


def pujaadd(request):
    if not request.user.is_authenticated:
        return redirect("/login")

    if request.method == "POST":
        if request.POST["name"] == "":
            return redirect("/pujalist/")

        last_puja = models.PujaUnit.objects.filter(name=Id2Puja(request.POST["name"])).order_by("year")
        last_puja = last_puja[-1] if len(last_puja) > 0 else None

        puja = models.PujaUnit.objects.create(
                year=request.POST["year"],
                name=Id2Puja(request.POST["name"]),
                puja_id="%d%s" % (request.POST["year"], request.POST["name"]),
                start=request.POST["start"],
                end=request.POST["end"]
                )
        puja.save()

        if last_puja is not None:
            datalist = models.DataUnit.objects.filter(puja=last_puja)

            for data in datalist:
                new_data = models.DataUnit.objects.create(
                        person=data.person,
                        puja=puja,
                        info_type=data.info_type
                        )
                new_data.save()

        return redirect("/pujalist/")

    return render(request, "pujaadd.html", locals())


def pujaedit(request, pujaid=None):
    if not request.user.is_authenticated:
        return redirect("/login")

    puja = models.PujaUnit.objects.get(id=pujaid)
    start_date_str = str(puja.start)
    end_date_str = str(puja.end)

    if request.method == "POST":
        puja.year = request.POST["year"]
        puja.name = Id2Puja(request.POST["name"])
        puja.start = request.POST["start"]
        puja.end = request.POST["end"]
        puja.save()
        return redirect("/pujalist/")

    return render(request, "pujaedit.html", locals())


def pujadelete(request, pujaid=None):
    if not request.user.is_authenticated:
        return redirect("/login")

    puja = models.PujaUnit.objects.get(id=pujaid)
    puja.delete()
    return redirect("/pujalist/")


def personlist(request):
    if not request.user.is_authenticated:
        return redirect("/login")

    persons = models.PersonUnit.objects.all()
    return render(request, "personlist.html", locals())


def personadd(request):
    if not request.user.is_authenticated:
        return redirect("/login")

    message = ""

    if request.method == "POST":
        try:
            person = models.PersonUnit.objects.get(name=request.POST["name"], address=request.POST["address"], contact=request.POST["phone"])
        except:
            person = None

        if person is None:
            person = models.PersonUnit.objects.create(
                    name=request.POST["name"],
                    person_id=PersonIdGenerator(datetime.now().timestamp()),
                    address=request.POST["address"],
                    contact=request.POST["phone"]
                    )
            person.save()
            return redirect("/personlist/")

        message = "已有名為 %s 的人員！編號為 %s ！" % (person.name, person.person_id)

    return render(request, "personadd.html", locals())


def personedit(request, personid=None):
    if not request.user.is_authenticated:
        return redirect("/login")

    person = models.PersonUnit.objects.get(person_id=personid)

    if request.method == "POST":
        person.name = request.POST["name"]
        person.address = request.POST["address"]
        person.contact = request.POST["phone"]
        person.save()
        return redirect("/personlist/")

    return render(request, "personedit.html", locals())


def persondelete(request, personid=None):
    if not request.user.is_authenticated:
        return redirect("/login")

    person = models.PersonUnit.objects.get(person_id=personid)
    person.delete()
    return redirect("/personlist/")


def participate(request, pujaid=None, participatetype=None):
    if not request.user.is_authenticated:
        return redirect("/login")

    if pujaid is None or participatetype is None:
        pujas = models.PujaUnit.objects.all()
        return render(request, "participate.html", locals())

    selection_type = ""

    if participatetype == "l":
        selection_type += "大牌"
    elif participatetype == "m":
        selection_type += "中牌"

    puja = models.PujaUnit.objects.get(id=pujaid)
    persons = models.PersonUnit.objects.all().order_by("address")
    datalist = models.DataUnit.objects.filter(puja__id=pujaid)
    participants = [data.person for data in datalist]
    datalist = models.DataUnit.objects.filter(puja__id=pujaid, info_type=selection_type)
    participants_in_type = [data.person for data in datalist]

    if request.method == "POST":
        checklist = request.POST.getlist("join")

        for person in persons:
            d_id = "%s%s" % (puja.puja_id, person.person_id)
            
            if person.person_id in checklist:
                try:
                    data = models.DataUnit.objects.get(data_id=d_id)
                    data.info_type = selection_type
                    data.save()
                except:
                    data = models.DataUnit.objects.create(
                            person=person,
                            puja=puja,
                            data_id=d_id,
                            info_type=selection_type
                            )
                    data.save()
            else:
                try:
                    data = models.DataUnit.objects.get(data_id=d_id)
                    data.delete()
                except:
                    continue

        return redirect("/participate/%d/%s" % (pujaid, participatetype))

    return render(request, "participateedit.html", locals())


def register(request):
    message = ""

    if request.method == "POST":
        username = request.POST["username"]

        try:
            user = auth.models.User.objects.get(username=username)
        except:
            user = None

        if user != None:
            message = "帳號已建立！請使用其他帳號註冊！"
            return render(request, "register.html", locals())
        else:
            if request.POST["password"] != request.POST["password_confirm"]:
                message = "密碼不相符！請再試一次！"
                return render(request, "register.html", locals())
            else:
                user = auth.models.User.objects.create_user(request.POST["username"], request.POST["email"], request.POST["password"])
                user.first_name = request.POST["first_name"]
                user.last_name = request.POST["last_name"]
                user.is_staff = False
                user.save()

        return redirect("/index/")
    return render(request, "register.html", locals())


def login(request):
    message = ""

    if request.method == "POST":
        username = request.POST["username"].strip()
        password = request.POST["password"]
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                auth.login(request, user)
                request.session["username"] = username
                request.session.set_expiry(18000)
                return redirect("/index/")
            else:
                message = "帳號不存在"
        else:
            message = "登入失敗！！"

    return render(request, "login.html", locals())


def logout(request):
    auth.logout(request)

    if "username" in request.session:
        del request.session["username"]

    return redirect("/index/")


def Id2Puja(pujaid=None):
    string = ""

    if pujaid == "01":
        string += "法華法會"
    elif pujaid == "02":
        string += "藥師光明燈"
    elif pujaid == "03":
        string += "藥師法會"
    elif pujaid == "04":
        string += "梁皇法會"
    elif pujaid == "07":
        string += "盂蘭法會"

    return string


def PersonIdGenerator(input_seed=105703009):
    random.seed(input_seed)
    candidate_letters = string.ascii_uppercase + string.digits
    letter_list = [ random.choice(candidate_letters) for _ in range(10) ]
    return "".join(letter_list)

