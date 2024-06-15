import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.conf import settings
from .models import UploadedFile
from .files import decrypt_file
from cryptography.fernet import Fernet
from django.http import HttpResponse

from django.http import JsonResponse
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import UploadedFile

from django.http import JsonResponse
from cryptography.fernet import Fernet
import os
from datetime import datetime

def generate_encrypted_text(request):
    if request.method == 'POST':
        file_name = request.POST.get('file_name')
        user_id = request.POST.get('user_id')
        
        # encrypt
        key_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "secret.key"
        )
        print(key_file_path)
        key = open(key_file_path, "r").read()
        f = Fernet(key)
        data_to_encrypt = f"{file_name}:{user_id}"
        print(data_to_encrypt)
        encrypted_text = str(f.encrypt(data_to_encrypt.encode()))
        
        print(encrypted_text)

        return JsonResponse({'encrypted_text': encrypted_text})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


def get_users(request):
    users = User.objects.all().values('id', 'username')
    return JsonResponse({'users': list(users)})


@login_required
def home(request):
    return render(request, "index.html")


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST or None)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect("main:home")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


def upload(request):
    return render(request, "upload.html")


@login_required
def upload_file(request):
    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]

        key = Fernet.generate_key()
        cipher_suite = Fernet(key)

        encrypted_file_content = cipher_suite.encrypt(uploaded_file.read())

        file_path = os.path.join(settings.MEDIA_ROOT, "files", uploaded_file.name)
        with open(file_path, "wb+") as destination:
            destination.write(encrypted_file_content)

        file_instance = UploadedFile(
            user=request.user, file_path=file_path, encryption_key=key.decode()
        )
        file_instance.save()
        success_message = "File uploaded and encrypted successfully!"
        return render(request, "upload.html", {"success_message": success_message})
    return render(request, "upload.html")


@login_required
def view_uploaded_files(request):
    uploaded_files = UploadedFile.objects.filter(user=request.user)
    file_names = [
        uploaded_file.file_path.split("\\")[-1] for uploaded_file in uploaded_files
    ]
    encrypted_file_paths = []
    file_paths = [uploaded_file.file_path for uploaded_file in uploaded_files]
    for uploaded_file in file_paths:

        # encrypt
        key_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "secret.key"
        )
        print(key_file_path)
        key = open(key_file_path, "r").read()
        f = Fernet(key)
        path = f.encrypt(uploaded_file.encode())

        encrypted_file_paths.append(path)

    return render(
        request, "uploaded_files.html", {"files": zip(file_names, encrypted_file_paths)}
    )


def decoder(encrypted_message):
    key_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "secret.key"
    )
    key = open(key_file_path, "r").read()
    print(key)
    f = Fernet(key)
    # Decrypt the message
    decrypted_message = f.decrypt(encrypted_message)
    return decrypted_message.decode()



from .models import Download

from django.contrib.auth.models import User
from django.shortcuts import render
from .models import Download, UploadedFile

@login_required
def download_history(request):
    uploaded_files =  UploadedFile.objects.filter(user=request.user)
    download_history = Download.objects.filter(filename__in=[uploaded_file.file_path.split("\\")[-1] for uploaded_file in uploaded_files]).order_by('-download_time')
    user_dict = {str(user.id): user.username for user in User.objects.all()}
    for download in download_history:
        download.username = user_dict.get(str(download.user_id), "Unknown")
    return render(request, 'download_history.html', {'download_history': download_history})


@login_required
def download_file(request):
    if request.method == "POST":
        user_id = str(request.user.id)
        file_path = request.POST.get("file_path")
        file_path, _id = str(decoder(file_path)).split(":")
        file_name = file_path
        file_path = decrypt_file(file_path)

        # Saving download record
        if _id:
            if _id == user_id:
                if os.path.exists(file_path):
                    # Create and save Download record
                    Download.objects.create(user_id=user_id, filename=file_name.split("\\")[0])

                    with open(file_path, "rb") as f:
                        response = HttpResponse(
                            f.read(), content_type="application/octet-stream"
                        )
                        response["Content-Disposition"] = (
                            f'attachment; filename="{os.path.basename(file_path)}"'
                        )
                        return response
                else:
                    return HttpResponse("File not found.")
            else:
                return HttpResponse("User Mismatch.")
        else:
            if os.path.exists(file_path):
                # Create and save Download record
                Download.objects.create(user_id=user_id, filename=file_name.split("\\")[0])

                with open(file_path, "rb") as f:
                    response = HttpResponse(
                        f.read(), content_type="application/octet-stream"
                    )
                    response["Content-Disposition"] = (
                        f'attachment; filename="{os.path.basename(file_path)}"'
                    )
                    return response
            else:
                return HttpResponse("File not found.")
    return render(request, "download.html")



@login_required
def generate_key_view(request):
    key = Fernet.generate_key()
    key_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "secret.key"
        )
    with open(key_file_path, "wb") as key_file:
        key_file.write(key)
    return HttpResponse("Key generated successfully")
