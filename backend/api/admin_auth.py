from django.conf import settings
from django.contrib.auth.hashers import check_password
import logging

logger = logging.getLogger(__name__)

class AdminAuthentication:
    def is_admin(self, user):
        if not user or user.is_anonymous:
            return False
        
        admin_email = settings.ADMIN_EMAIL
        if not admin_email:
            logger.warning("ADMIN_EMAIL not configured")
            return False
        
        if user.email.lower() != admin_email.lower():
            return False
        
        admin_password_hash = settings.ADMIN_PASSWORD_HASH
        if not admin_password_hash:
            logger.warning("ADMIN_PASSWORD_HASH not configured")
            return False
        
        return True
