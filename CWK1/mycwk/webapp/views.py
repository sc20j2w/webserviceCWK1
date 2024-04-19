import json

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Author, Story
from django.views.decorators.http import require_http_methods
from django.views import View
from datetime import datetime


# Create your views here.
@csrf_exempt
def login(request):
    if request.method == 'POST':
        # Retrieve username and password from the request
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            # Respond with error if username or password are not provided
            return HttpResponse('Username and password are required.', status=400, content_type='text/plain')

        try:
            # Attempt to fetch the user by username
            user = Author.objects.get(username=username)
        except Author.DoesNotExist:
            # Return an error message if the user does not exist
            return HttpResponse('Login failed, author does not exist.', status=401, content_type='text/plain')

        # Check if the provided password matches the stored
        if password == user.password:
            request.session['username'] = username
            return HttpResponse('Welcome here, %s! Login success.' % username, status=200, content_type='text/plain')
        else:
            # If the password is incorrect, return an error message
            return HttpResponse('Login failed, incorrect password.', status=401, content_type='text/plain')

    else:
        # If the request method is not POST, return an error message
        return HttpResponse('Invalid request method.', status=405, content_type='text/plain')


@csrf_exempt
def logout(request):
    if request.method == 'POST':
        # Check if user is authenticated by looking for 'username' in session
        if 'username' in request.session:
            # Remove 'username' from session to log out the user
            del request.session['username']
            # Additionally clear any other session data that could be related to user's session
            request.session.flush()
            return HttpResponse('Bye! Logout success.', status=200, content_type='text/plain')
        else:
            # If no 'username' is found in session, indicate that no user was logged in
            return HttpResponse('Logout failed, no user is currently logged in.', status=400, content_type='text/plain')
    else:
        # If the request method is not POST, return an error message
        return HttpResponse('Invalid request method. Only POST is supported for this operation.', status=405,
                            content_type='text/plain')


class StoryView(View):
    @csrf_exempt
    def get(self, request):
        if request.method == "GET":
            # Get the query parameters
            data = request.GET
            story_cat = data.get('story_cat', '*')
            story_region = data.get('story_region', '*')
            story_date = data.get('story_date', '*')

            stories = Story.objects.all()

            # Filter the stories based on the query parameters
            if story_cat and story_cat != '*':
                stories = stories.filter(category=story_cat)
            if story_region and story_region != '*':
                stories = stories.filter(region=story_region)

            if story_date and story_date != '*':
                try:
                    parse_date = datetime.strptime(story_date, '%d/%m/%Y').date()
                    stories = stories.filter(date=parse_date)
                except ValueError:
                    return HttpResponse('Invalid date format. Correct: DD/MM/YYYY.', status=400,
                                        content_type='text/plain')

            if not stories.exists():
                return HttpResponse('No stories found.', status=404, content_type='text/plain')

            # Prepare the response
            stories_list = [{
                'key': story.id,
                'headline': story.headline,
                'story_cat': story.category,
                'story_region': story.region,
                'author': story.author.AuthorName,
                'story_date': story.date.strftime('%d/%m/%Y'),
                'story_details': story.details
            } for story in stories]

            return JsonResponse({'stories': stories_list}, safe=False, status=200)

    @csrf_exempt
    def post(self, request):
        if 'username' not in request.session:
            return HttpResponse('Unauthenticated author.', status=503, content_type='text/plain')

        data = json.loads(request.body.decode('utf-8'))  # ensure correct decoding
        username = request.session['username']

        try:
            author = Author.objects.get(username=username)
        except Author.DoesNotExist:
            return HttpResponse('Unauthenticated author.', status=503, content_type='text/plain')

        story = Story(headline=data['headline'], category=data['category'], region=data['region'],
                      details=data['details'], author=author)
        story.save()

        return HttpResponse('Story created success.', status=201, content_type='text/plain')


@require_http_methods(["DELETE"])
def delete(request, key):
    # Check if user is authenticated
    username = request.session.get('username')
    if not username:
        return HttpResponse('Authentication required.', status=401, content_type='text/plain')

    # Retrieve the story; return 404 if not found
    story = Story.objects.filter(pk=key).first()
    if not story:
        return HttpResponse('No story found.', status=404, content_type='text_plain')

    # Check if the logged-in user is the author of the story
    if story.author.username != username:
        return HttpResponse('Unauthorized Access.', status=403, content_type='text/plain')

    # Delete the story
    story.delete()
    return HttpResponse('Story deleted successfully.', status=200, content_type='text/plain')

