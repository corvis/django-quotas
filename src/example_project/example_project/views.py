from django.http import HttpResponse, HttpRequest


async def home(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Hello, world. You're at the home page.")