from django.shortcuts import render

# Create your views here.
def doc():
    return render("api/doc.html")