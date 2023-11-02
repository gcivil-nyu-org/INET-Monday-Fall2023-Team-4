# from django.shortcuts import render, redirect
# from .forms import BookClubForm
# from .models import BookClub
# from libraries.models import Library

# def create_book_club(request, library_id):
#     library = Library.objects.get(id=library_id)
#     admin_user = request.user  

#     if request.method == 'POST':
#         form = BookClubForm(request.POST)
#         if form.is_valid():
#             book_club = form.save(commit=False)
#             book_club.admin = admin_user
#             book_club.libraryId = library
#             book_club.save()
           
#             book_club.members.add(admin_user)
#             book_club.save()
#             return redirect('some_view_name')  
#     else:
#         form = BookClubForm()
    
#     return render(request, 'create_book_club.html', {'form': form})