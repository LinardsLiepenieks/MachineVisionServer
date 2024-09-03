from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import AudioRecording, APIKey
from django.core.exceptions import ValidationError
from .utils.transcribe_audio import speech_to_text
import json

@csrf_exempt
def api_endpoint(request):
    if request.method == 'POST':
        # Get the IP address from the request
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')

        # Parse the JSON body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        # Process the data from the request body
        message = data.get('message', '')

        return JsonResponse({
            'message': f'Received message: {message}',
            'ip_address': ip_address
        })
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    
@csrf_exempt
def upload_recording(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    # Ensure user is authenticated via the middleware
    user = getattr(request, 'user', None)
    
    if user is None or user.is_anonymous:
        return JsonResponse({'error': 'User is not authenticated'}, status=401)
    
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file uploaded'}, status=400)

    file = request.FILES['file']

    try:
        print("SAVING", file)
        # Create and save the audio recording
        recording = AudioRecording.objects.create(user=user, recording=file)
        api_key = APIKey.objects.get(user=user)  # Assuming each user has an associated APIKey
        ActivityLog.objects.create(
                    user=user,
                    api_key=api_key,
                    action='record',
                    details=f"created recording, {recording.id}"
                )

        print("STARTING")
        transcribed_text = speech_to_text(file, file_name=file.name)
        print("Transcribed text:", transcribed_text)

        return JsonResponse({
            'status': 'success', 
            'recording_id': recording.id,
            'transcribed_text': transcribed_text
        }, status=201)
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def receive_text(request):
    
    if request.method == 'POST':
        user = getattr(request, 'user', None)
    
        if user is None or user.is_anonymous:
            return JsonResponse({'error': 'User is not authenticated'}, status=401)

        try:
            data = json.loads(request.body)
            text = data.get('text', '')

            if text:
                print(f"Received text: {text}")
                api_key = APIKey.objects.get(user=user)  # Assuming each user has an associated APIKey
                ActivityLog.objects.create(
                    user=user,
                    api_key=api_key,
                    action='execute',
                    details=f"Text received: {text}"
                )

                return JsonResponse({'status': 'success', 'message': 'Text received'}, status=200)
            else:
                return JsonResponse({'status': 'fail', 'message': 'No text provided'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'fail', 'message': 'Invalid JSON'}, status=400)

    return JsonResponse({'status': 'fail', 'message': 'Invalid request method'}, status=405)
