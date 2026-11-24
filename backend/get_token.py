from supabase import create_client

from configs.settings import get_settings

settings = get_settings()

client = create_client(
        settings.database.supabase_project_url, 
        settings.database.supabase_publishable_key
        )
response = client.auth.sign_in_with_password(
    {"email": "example@gmail.com", "password": "password"}
)
print(response.session.access_token)

"""
This is a helper file that retrieves a JWT token for a user. Since our backend endpoints expects a JWT token along with data we need to request for real JWT token from supabase, authorize the fastapi docs page from where we test our endpoints
"""