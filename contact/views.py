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
    pujalist = models.PujaUnit.objects.all()
    return render(request, "pujalist.html", locals())


def pujaadd(request):
    if request.method == "POST":
        return redirect("/pujalist/")
    return render(request, "pujaadd.html", locals())


def pujaedit(request, pujaid=None):
    puja = models.PujaUnit.objects.get(id=pujaid)

    if request.method == "POST":
        return redirect("/pujalist/")

    return render(request, "pujaedit.html", locals())


def pujadelete(request, pujaid=None):
    puja = models.PujaUnit.objects.get(id=pujaid)
    puja.delete()
    return redirect("/pujalist/")


def personlist(request):
    personlist = models.PersonUnit.objects.all()
    return render(request, "personlist.html", locals())


def personadd(request):
    if request.method == "POST":
        return redirect("/personlist/")
    return render(request, "personadd.html", locals())


def personedit(request, personid=None):
    person = models.PersonUnit.objects.get(id=personid)

    if request.method == "POST":
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

