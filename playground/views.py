from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse
from django.shortcuts import render


# def say_hello(request):
#     return render(request, 'hello.html', {'name': 'Mosh'})


def multiplication_table(request):
    try:
        number = int(request.GET.get('number', 1))  # Default to 1 if 'number' parameter is not provided
    except ValueError:
        return HttpResponseBadRequest('Invalid input: number must be an integer.')
    
    if number <= 0:
        return HttpResponseBadRequest('Invalid input: number must be a positive integer.')

    multiplication_results = [f"{number} x {i} = {number*i}" for i in range(1, 11)]

    return render(request, 'hello.html', {'results': multiplication_results})

