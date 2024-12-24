from django.shortcuts import redirect
# from django.contrib.auth.models import User, Group

from django.http import HttpResponse
from decouple import config

class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/') and not request.user.groups.filter(name='Admin').exists():
            return redirect('permission_denied')
        if request.path.startswith('/contacts/') and not request.user.groups.filter(name__in=['Admin', 'Staff']).exists():
            return redirect('permission_denied')
        if request.path.startswith('/client-portal/') and not request.user.groups.filter(name='Contacts').exists():
            return redirect('permission_denied')

        return self.get_response(request)
    

from django.http import HttpResponse
from decouple import config

from django.http import HttpResponse
from decouple import config

def maintenance_middleware(get_response):
    def middleware(request):
        if config("MAINTENANCE_MODE", default=False, cast=bool):
            return HttpResponse("""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Maintenance</title>
                    <style>
                        body {
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            height: 100vh;
                            margin: 0;
                            font-family: Arial, sans-serif;
                            background: #f0f0f0;
                            color: #333;
                            text-align: center;
                        }
                        .container {
                            background: #ffffff;
                            padding: 2rem;
                            border-radius: 10px;
                            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                            border: 2px solid #007BFF;
                        }
                        h1 {
                            font-size: 2.5rem;
                            color: #007BFF;
                            margin-bottom: 1rem;
                        }
                        p {
                            font-size: 1.2rem;
                            color: #555;
                        }
                        a {
                            display: inline-block;
                            margin-top: 1rem;
                            padding: 0.5rem 1rem;
                            background: #007BFF;
                            color: #ffffff;
                            text-decoration: none;
                            border-radius: 5px;
                            font-weight: bold;
                        }
                        a:hover {
                            background: #0056b3;
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>We’ll Be Back Soon!</h1>
                        <p>Backend is currently under maintenance. We’re working hard to improve your experience.</p>
                        <a href="/">Go Back to Homepage</a>
                    </div>
                </body>
                </html>
            """)
        return get_response(request)

    return middleware
