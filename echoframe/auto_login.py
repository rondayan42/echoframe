import os
import json
from flask import session, redirect, url_for, request

def setup_auto_login(app, storage_dir='user_data'):
    """
    Set up automatic login by checking for existing user data files
    
    Add this to your app.py to enable auto-login for returning users
    """
    
    @app.before_request
    def check_for_user():
        """Check if we need to automatically log the user in"""
        # Skip this check if the user is already logged in or if we're on the identify page
        if 'snaker_name' in session or request.endpoint == 'identify' or request.endpoint == 'static':
            return None
            
        # Look for user data files
        if os.path.exists(storage_dir):
            user_files = [f for f in os.listdir(storage_dir) if f.endswith('.json')]
            
            # If we have exactly one user file, auto-login that user
            if len(user_files) == 1:
                try:
                    username = os.path.splitext(user_files[0])[0]
                    with open(os.path.join(storage_dir, user_files[0]), 'r') as f:
                        user_data = json.load(f)
                    
                    # Set up the session
                    session['snaker_name'] = username
                    session['xp'] = user_data.get('xp', 0)
                    session['completed'] = user_data.get('completed', [])
                    session['snake_intro_seen'] = user_data.get('snake_intro_seen', False)
                    
                    # Log the auto-login
                    print(f"Auto-login for user: {username}")
                except Exception as e:
                    print(f"Error during auto-login: {str(e)}")
        
        # If no user is logged in at this point, redirect to the identify page
        if 'snaker_name' not in session:
            return redirect(url_for('identify'))
        
        return None