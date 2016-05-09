from __future__ import absolute_import
import logging
logger = logging.getLogger('solvebio')


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

                    if 'non_field_errors' in self.json_body:
                        self.message = '%s.' % \
                            ', '.join(self.json_body['non_field_errors'])

                    for k, v in self.json_body.items():
                        if k not in ['detail', 'non_field_errors']:
                            if isinstance(v, list):
                                v = ', '.join(v)
                            self.field_errors.append('%s (%s)' % (k, v))

                    if self.field_errors:
                        self.message += (' The following fields were missing '
                                         'or invalid: %s' %
                                         ', '.join(self.field_errors))

    def __str__(self):
        return self.message
