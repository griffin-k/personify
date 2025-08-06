from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.conf import settings
import os
import face_recognition
import tempfile
from django.contrib.auth import logout



from .models import AddMissing

def register(request):
    if request.method == 'POST':
        # Get form data
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')
        username = email.split('@')[0]  


        try:
            EmailValidator()(email)  
            
        except ValidationError:
            messages.error(request, "Invalid email address.")
            return render(request, 'dashboard/register.html')


        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'dashboard/register.html')


        try:
            validate_password(password)  
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return render(request, 'dashboard/register.html')


        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, 'dashboard/register.html')


        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()


        messages.success(request, "Account created successfully! Please log in.")
        return redirect('login')  

    return render(request, 'dashboard/register.html')



def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

      
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None
        
        if user is not None:
     
            user = authenticate(request, username=user.username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('dashboard')  
            else:
         
                messages.error(request, "Invalid email or password.")
                return render(request, 'dashboard/login.html')
        else:

            messages.error(request, "Invalid email or password.")
            return render(request, 'dashboard/login.html')

    return render(request, 'dashboard/login.html')






def add_missing_person(request):
    if request.method == 'POST':

        full_name = request.POST.get('full_name')
        contact_info = request.POST.get('contact_info')
        reporter_address = request.POST.get('reporter_address')
        missing_place_address = request.POST.get('missing_place_address')
        identity_details = request.POST.get('identity_details')
        

        image = request.FILES.get('image')  


        if not full_name or not contact_info or not reporter_address or not missing_place_address or not identity_details:
            messages.error(request, "Please fill all required fields.")
            return redirect('add_missing')  


        try:
  
            missing_person = AddMissing(
                full_name=full_name,
                contact_info=contact_info,
                reporter_address=reporter_address,
                missing_place_address=missing_place_address,
                identity_details=identity_details,
                image=image
            )
            missing_person.save()

            messages.success(request, "Missing person case submitted successfully.")
            return redirect('success') 

        except ValidationError as e:
            messages.error(request, f"Error: {e}")
            return redirect('add_missing')
    else:
        return render(request, 'dashboard/add_missing.html')  

def success_page(request):
    return render(request, 'dashboard/index.html') 





def match_missing_person(request):
    if request.method == 'GET':
        return render(request, 'dashboard/find_missing.html')

    if request.method == 'POST' and request.FILES.get('image'):
        uploaded_image = request.FILES['image']

  
        temp_image_path = tempfile.mktemp(suffix='.jpg')
        with open(temp_image_path, 'wb+') as temp_file:
            for chunk in uploaded_image.chunks():
                temp_file.write(chunk)


        try:
            uploaded_image_data = face_recognition.load_image_file(temp_image_path)
            uploaded_encodings = face_recognition.face_encodings(uploaded_image_data)
        except Exception as e:
            return JsonResponse({'error': 'Failed to process uploaded image.'})

        if not uploaded_encodings:
            return JsonResponse({'error': 'No face found in uploaded image.'})

        uploaded_encoding = uploaded_encodings[0]


        for person in AddMissing.objects.exclude(image=''):
            db_image_path = os.path.join(settings.MEDIA_ROOT, str(person.image))

            try:
                db_image_data = face_recognition.load_image_file(db_image_path)
                db_encodings = face_recognition.face_encodings(db_image_data)

                if not db_encodings:
                    continue

                db_encoding = db_encodings[0]


                match = face_recognition.compare_faces([db_encoding], uploaded_encoding, tolerance=0.5)

                if match[0]:
                    return JsonResponse({
                        'match': {
                            'name': person.full_name,
                            'contact_info': person.contact_info,
                            'reporter_address': person.reporter_address,
                            'missing_place_address': person.missing_place_address,
                            'identity_details': person.identity_details,
                            'image_url': person.image.url,
                        }
                    })

            except Exception as e:
                continue  

        return JsonResponse({'match': None, 'message': 'No match found.'})

    return JsonResponse({'error': 'Invalid request method.'})




def logout_view(request):
    logout(request)
    return redirect('login')




def dashboard(request):
    return render(request, 'dashboard/index.html')
