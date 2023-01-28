from django.shortcuts import render, redirect
from django.http import HttpResponse
from contact import models

# Create your views here.
def homepage(request):
    return redirect("/index/")


def index(request, pujaid=None):
    if pujaid is not None:
        datalist = models.DataUnit.objects.filter(puja__id=pujaid).order_by("id")
        
    pujas = models.PujaUnit.objects.all()

    if request.method == "POST":
        puja_id = request.POST["puja_select"]
        return redirect("/index/%d" % puja_id)

    return render(request, "index.html", locals())


def pujalist(request):
    pujas = models.PujaUnit.objects.all()
    return render(request, "pujalist.html", locals())


def pujaadd(request):
    if request.method == "POST":
        if request.POST["name"] == "":
            return redirect("/pujalist/")

        puja = models.PujaUnit.objects.create(
                year=request.POST["year"],
                name=request.POST["name"],
                start=request.POST["start"],
                end=request.POST["end"]
                )
        puja.save()
        return redirect("/pujalist/")

    return render(request, "pujaadd.html", locals())


def pujaedit(request, pujaid=None):
    puja = models.PujaUnit.objects.get(id=pujaid)
    start_date_str = str(puja.start)
    end_date_str = str(puja.end)

    if request.method == "POST":
        puja.year = request.POST["year"],
        puja.name = request.POST["name"],
        puja.start = request.POST["start"],
        puja.end = request.POST["end"]
        puja.save()
        return redirect("/pujalist/")

    return render(request, "pujaedit.html", locals())


def pujadelete(request, pujaid=None):
    puja = models.PujaUnit.objects.get(id=pujaid)
    puja.delete()
    return redirect("/pujalist/")


def personlist(request):
    persons = models.PersonUnit.objects.all()
    return render(request, "personlist.html", locals())


def personadd(request):
    if request.method == "POST":
        person = models.PersonUnit.objects.create(
                name=request.POST["name"],
                person_id=IdEncode(request.POST["personid"]),
                address=request.POST["address"],
                contact=request.POST["phone"]
                )
        person.save()
        return redirect("/personlist/")

    return render(request, "personadd.html", locals())


def personedit(request, personid=None):
    person = models.PersonUnit.objects.get(id=personid)

    if request.method == "POST":
        person.name = request.POST["name"]
        person.person_id = IdEncode(request.POST["personid"])
        person.address = request.POST["address"]
        person.contact = request.POST["phone"]
        person.save()
        return redirect("/personlist/")

    return render(request, "personedit.html", locals())


def persondelete(request, personid=None):
    person = models.PersonUnit.objects.get(id=personid)
    person.delete()
    return redirect("/personlist/")


def register(request):
    message = ""

    if request.method == "POST":
        username = request.POST["username"]

        try:
            user = User.objects.get(username=username)
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
                user = User.objects.create_user(request.POST["username"], request.POST["email"], request.POST["password"])
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
        user = authenticate(username=username, password=password)

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

    return redirect("/login/")


def IdEncode(personid=None):
    string = ""

    if ord(personid[0]) >= 65 and ord(personid[0] <= 90):
        string += str(personid[0])
        string += personid[1:]
    else:
        string += personid

    return (hex(int(string)).upper() + hex(int(string[4:])).upper())

