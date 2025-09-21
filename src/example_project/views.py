#
#  Copyright 2025 by Dmitry Berezovsky, MIT License
#
from django.http import HttpRequest, HttpResponse


async def home(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Hello, world. You're at the home page.")
