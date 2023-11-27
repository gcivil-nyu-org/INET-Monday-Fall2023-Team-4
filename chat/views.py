from django.shortcuts import render


def index(request):
    return render(request, "chat/index.html")


# def room(request, room_name):
#     return render(request, 'chat/room.html', {
#         'room_name': room_name
#     })


def room(request, room_name):
    return render(
        request,
        "chat/room.html",
        {"room_name": room_name, "username": request.user.username},
    )


def name(request, roomname):
    # Do any processing if needed, then pass the roomname to the template
    return render(
        request,
        "chat/name.html",
        {"roomname": roomname, "username": request.user.username},
    )
