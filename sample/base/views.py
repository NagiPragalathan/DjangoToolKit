from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request,'sample.html',{'items':[1,2,3]})