from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, world.")

from example.models import Counter
def hi(request):
    record = Counter.objects.get_or_create(id=1)[0]
    record.pageviews = record.pageviews + 1
    record.save()
    return render(request, template_name="hello_world.html", context={"msg":f"Hello, world. {record.pageviews} times."})

from rest_framework import viewsets
from example.serializers import CounterSerializer
class CounterViewSet(viewsets.ModelViewSet):
    queryset = Counter.objects.all()
    serializer_class = CounterSerializer


def error(request):
    _ = Counter.objects.get(id=-1)
    return HttpResponse(_.id)