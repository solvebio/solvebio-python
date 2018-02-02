from __future__ import absolute_import
import logging
logger = logging.getLogger('solvebio')


class NotFoundError(Exception):
    pass


class SolveError(Exception):
    """Exceptions tailored to the kinds of errors from a SolveBio API
    request"""
    default_message = ('Unexpected error communicating with SolveBio. '
                       'If this problem persists, let us know at '
                       'support@solvebio.com.')

    def __init__(self, message=None, response=None):
        self.json_body = None
        self.status_code = None
        self.message = message or self.default_message
        self.field_errors = []
        self.response = response  # For clients that want the full story.

        if response is not None:
            self.status_code = response.status_code
            try:
                self.json_body = response.json()
            except:
                if response.status_code == 404:
                    self.message = '404 Not Found.'
                logger.debug(
                    'API Response (%d): No content.' % self.status_code)
            else:
                logger.debug(
                    'API Response (%d): %s'
                    % (self.status_code, self.json_body))

                if self.status_code in [400, 401, 403, 404]:
                    self.message = 'Bad request.'

                    if 'detail' in self.json_body:
                        self.message = '%s' % self.json_body['detail']
                        del self.json_body['detail']

                    if 'non_field_errors' in self.json_body:
                        self.message = '%s' % \
                            ', '.join(self.json_body['non_field_errors'])
                        del self.json_body['non_field_errors']

                    if self.json_body:
                        self.message += ' %s' % self.json_body

    def __str__(self):
        return self.message
