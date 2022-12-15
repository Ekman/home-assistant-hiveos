"""All exceptions for this package"""

class HiveOsException(Exception):
    """Base exception for this package"""

class HiveOsApiException(HiveOsException):
    """An exception that occurs in the HiveOS API"""

class HiveOsAipUnauthorizedException(HiveOsApiException):
    """An exception that indicates that the API credentials are incorrect"""
