"""
YouTube API Manager with Automatic Key Rotation and Error Reporting

Features:
- Loads multiple API keys from .env
- Automatically rotates keys on quota errors
- Comprehensive error logging and reporting
- Graceful failure handling
"""

import os
import logging
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class YouTubeAPIManager:
    """Manages multiple YouTube API keys with automatic rotation"""

    def __init__(self):
        # Load environment variables
        load_dotenv()
        env_path = Path(__file__).parent.parent / '.env'
        load_dotenv(dotenv_path=env_path)

        # Load all available API keys
        self.api_keys = []
        key1 = os.getenv('YOUTUBE_API_KEY')
        key2 = os.getenv('YOUTUBE_API_KEY_2')

        if key1:
            self.api_keys.append(key1)
            logger.info(f"Loaded YOUTUBE_API_KEY: {key1[:10]}...")
        if key2:
            self.api_keys.append(key2)
            logger.info(f"Loaded YOUTUBE_API_KEY_2: {key2[:10]}...")

        if not self.api_keys:
            raise ValueError("No YouTube API keys found in .env file!")

        logger.info(f"Total API keys loaded: {len(self.api_keys)}")

        self.current_key_index = 0
        self.youtube = None
        self._build_service()

    def _build_service(self):
        """Build YouTube service with current key"""
        current_key = self.api_keys[self.current_key_index]
        logger.info(f"Building YouTube service with key #{self.current_key_index + 1}")

        try:
            self.youtube = build('youtube', 'v3', developerKey=current_key)
            logger.info(f"YouTube service built successfully with key #{self.current_key_index + 1}")
        except Exception as e:
            logger.error(f"Failed to build YouTube service: {e}")
            raise

    def _rotate_key(self):
        """Rotate to next available API key"""
        if len(self.api_keys) == 1:
            logger.error("Only 1 API key available - cannot rotate!")
            return False

        old_index = self.current_key_index
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)

        logger.warning(f"🔄 ROTATING API KEY: #{old_index + 1} -> #{self.current_key_index + 1}")

        try:
            self._build_service()
            logger.info(f"✅ Successfully rotated to key #{self.current_key_index + 1}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to rotate to key #{self.current_key_index + 1}: {e}")
            return False

    def _is_quota_error(self, error):
        """Check if error is a quota/rate limit error"""
        if isinstance(error, HttpError):
            # Quota errors are 403 with specific reasons
            if error.resp.status == 403:
                error_content = str(error.content)
                quota_indicators = [
                    'quotaExceeded',
                    'dailyLimitExceeded',
                    'userRateLimitExceeded',
                    'rateLimitExceeded'
                ]
                for indicator in quota_indicators:
                    if indicator in error_content:
                        logger.warning(f"⚠️  QUOTA ERROR DETECTED: {indicator}")
                        return True
        return False

    def search(self, **kwargs):
        """
        Execute YouTube search with automatic key rotation on quota errors

        Returns: (result, error_info)
            - result: API response or None if failed
            - error_info: dict with error details or None if successful
        """
        max_attempts = len(self.api_keys)

        for attempt in range(max_attempts):
            try:
                logger.info(f"🔍 Executing search with key #{self.current_key_index + 1} (attempt {attempt + 1}/{max_attempts})")
                result = self.youtube.search().list(**kwargs).execute()
                logger.info(f"✅ Search successful with key #{self.current_key_index + 1}")
                return result, None

            except HttpError as e:
                error_info = {
                    'status_code': e.resp.status,
                    'reason': e.reason if hasattr(e, 'reason') else 'Unknown',
                    'content': str(e.content),
                    'key_index': self.current_key_index + 1,
                    'attempt': attempt + 1
                }

                logger.error(f"❌ YouTube API Error (Key #{self.current_key_index + 1}):")
                logger.error(f"   Status: {error_info['status_code']}")
                logger.error(f"   Reason: {error_info['reason']}")

                if self._is_quota_error(e):
                    logger.warning(f"⚠️  QUOTA EXCEEDED on key #{self.current_key_index + 1}")

                    if attempt < max_attempts - 1:
                        logger.info(f"🔄 Attempting to rotate to next key...")
                        if self._rotate_key():
                            logger.info(f"✅ Rotation successful, retrying search...")
                            continue
                        else:
                            logger.error(f"❌ Rotation failed, giving up")
                            return None, error_info
                    else:
                        logger.error(f"❌ ALL API KEYS EXHAUSTED ({max_attempts} keys tried)")
                        error_info['all_keys_exhausted'] = True
                        return None, error_info
                else:
                    # Not a quota error - don't retry
                    logger.error(f"❌ Non-quota error - not retrying")
                    return None, error_info

            except Exception as e:
                error_info = {
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    'key_index': self.current_key_index + 1,
                    'attempt': attempt + 1
                }
                logger.error(f"❌ Unexpected error: {type(e).__name__}: {e}")
                return None, error_info

        # Should never reach here, but just in case
        return None, {'error': 'All attempts exhausted'}

    def get_playlists(self, **kwargs):
        """Execute YouTube playlists request with retry logic"""
        max_attempts = len(self.api_keys)

        for attempt in range(max_attempts):
            try:
                result = self.youtube.playlists().list(**kwargs).execute()
                return result, None
            except HttpError as e:
                if self._is_quota_error(e) and attempt < max_attempts - 1:
                    self._rotate_key()
                    continue
                return None, {'status': e.resp.status, 'message': str(e)}
            except Exception as e:
                return None, {'error': str(e)}

        return None, {'error': 'All keys exhausted'}

    def get_playlist_items(self, **kwargs):
        """Execute YouTube playlistItems request with retry logic"""
        max_attempts = len(self.api_keys)

        for attempt in range(max_attempts):
            try:
                result = self.youtube.playlistItems().list(**kwargs).execute()
                return result, None
            except HttpError as e:
                if self._is_quota_error(e) and attempt < max_attempts - 1:
                    self._rotate_key()
                    continue
                return None, {'status': e.resp.status, 'message': str(e)}
            except Exception as e:
                return None, {'error': str(e)}

        return None, {'error': 'All keys exhausted'}

    def get_current_key_info(self):
        """Get info about current key being used"""
        return {
            'key_number': self.current_key_index + 1,
            'total_keys': len(self.api_keys),
            'key_preview': self.api_keys[self.current_key_index][:10] + '...'
        }
