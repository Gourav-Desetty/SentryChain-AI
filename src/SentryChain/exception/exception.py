import os, sys

class CustomException(Exception):
    def __init__(self, error_message, error_detail):
        self.error_message = error_message
        self.error_detail = error_detail
        _, _, exc_tb = error_detail.exc_info()

        self.line_no = None
        self.file_name = None

        if exc_tb is not None:
            self.line_no = exc_tb.tb_lineno
            self.file_name = exc_tb.tb_frame.f_code.co_filename

    def __str__(self):
        return f"Error occured in python script {self.file_name}, line number {self.line_no}, error message {str(self.error_message)}"