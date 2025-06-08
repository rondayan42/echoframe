import os
import json
from flask import session
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("storage")

class PersistentStorage:
    """
    Class to handle persistent storage of user progress
    by saving data to JSON files on disk
    """
    def __init__(self, storage_dir='user_data'):
        """Initialize with a directory to store user data"""
        self.storage_dir = storage_dir
        # Create the storage directory if it doesn't exist
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
        logger.info(f"Storage initialized in directory: {storage_dir}")

    def get_user_filename(self, username):
        """Generate a filename for the user's data"""
        # Replace any characters that might cause issues in filenames
        safe_username = "".join(c for c in username if c.isalnum() or c in "._- ")
        return os.path.join(self.storage_dir, f"{safe_username}.json")

    def save_user_data(self, username, user_data_to_save): # Changed parameter name for clarity
        """Save user session data to a file"""
        if not username:
            logger.warning("Cannot save data: Empty username")
            return False

        # --- ADDED: Ensure the data being saved is a dictionary ---
        if not isinstance(user_data_to_save, dict):
            logger.error(f"Attempted to save non-dictionary data for user '{username}'. Type: {type(user_data_to_save)}")
            # Optionally, try to recover or log the problematic data
            # logger.error(f"Problematic data: {user_data_to_save}")
            return False # Prevent saving incorrect data type

        filename = self.get_user_filename(username)

        # Log what we're saving (be careful with sensitive data in real apps)
        logger.info(f"Saving data for user '{username}' to {filename}")
        # Example logging specific fields:
        # logger.info(f"Saving XP: {user_data_to_save.get('xp')}, Completed: {len(user_data_to_save.get('completed', []))}")
        # logger.info(f"Saving snake_intro_seen: {user_data_to_save.get('snake_intro_seen')}")

        try:
            # Save to file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(user_data_to_save, f, indent=2, default=str) # Added default=str for non-serializables

            logger.info("User data saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving user data: {str(e)}")
            return False

    def load_user_data(self, username):
        """Load user data from file. Returns the loaded dict or None."""
        if not username:
            logger.warning("Cannot load data: Empty username")
            return None # Return None instead of False on failure

        filename = self.get_user_filename(username)
        logger.info(f"Attempting to load user data for '{username}' from {filename}")

        if not os.path.exists(filename):
            logger.warning(f"User data file not found: {filename}")
            return None # Return None if file doesn't exist

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                user_data = json.load(f)

            # --- ADDED: Validate that loaded data is a dictionary ---
            if not isinstance(user_data, dict):
                 logger.error(f"Loaded data for '{username}' is not a dictionary (Type: {type(user_data)}). File: {filename}")
                 return None # Return None if data is malformed

            logger.info(f"Loaded user data successfully for '{username}'.")
            return user_data # Return the loaded dictionary
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON in user data file '{filename}': {str(e)}")
            return None # Return None on JSON error
        except IOError as e:
            logger.error(f"IO error reading user data file '{filename}': {str(e)}")
            return None # Return None on IO error
        except Exception as e:
            logger.error(f"Unexpected error loading user data from '{filename}': {str(e)}")
            return None # Return None on other errors

    def delete_user_data(self, username):
        """Deletes the user data file."""
        if not username:
            logger.warning("Cannot delete data: Empty username")
            return False
        filename = self.get_user_filename(username)
        if os.path.exists(filename):
            try:
                os.remove(filename)
                logger.info(f"Deleted user data file: {filename}")
                return True
            except OSError as e:
                logger.error(f"Error deleting user data file {filename}: {e}")
                return False
        else:
            logger.warning(f"Attempted to delete non-existent user data file: {filename}")
            return False


# Create a global instance to use throughout the app
storage = PersistentStorage()
