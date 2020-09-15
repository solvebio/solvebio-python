from __future__ import absolute_import
import logging
logger = logging.getLogger('solvebio')


class NotFoundError(Exception):
    pass


class FileUploadError(Exception):
    pass


class SolveError(Exception):
    """Exceptions tailored to the kinds of errors from a SolveBio API
    request"""
    default_message = ('Unexpected error communicating with SolveBio. '
                       'If this problem persists, let us know at '
                       'support@solvebio.com.')

    def __init__(self, message=None, response=None):
        self.json_body = {}
        self.status_code = None
        self.message = message or self.default_message
        self.field_errors = []
        self.response = response

        if response is not None:
            self.status_code = response.status_code
            try:
                self.json_body = response.json()
                logger.debug(
                    'API Response (%d): %s'
                    % (self.status_code, self.json_body))
            except:
                logger.debug(
                    'API Response (%d): Response does not contain JSON.'
                    % self.status_code)

            if self.status_code == 400:
                self.message = 'Bad Request ({})'.format(response.url)
            elif response.status_code == 401:
                self.message = '401 Unauthorized ({})'.format(response.url)
            elif response.status_code == 403:
                self.message = '403 Forbidden ({})'.format(response.url)
            elif response.status_code == 404:
                self.message = '404 Not Found ({})'.format(response.url)

            # Handle other keys
            for k, v in list(self.json_body.items()):
                if k in ["non_field_errors", "detail"]:
                    self.message += '\nError: '
                else:
                    self.message += '\nError (%s): ' % k

                # can be a list, dict, string
                self.message += str(v)

    def __str__(self):
        return self.message
