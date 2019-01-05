import re
import uuid

def validate_operation_no(operation_no):
    if not re.search(r'\D{2}\d{4}', operation_no):
        print('Error')
        return False


text = 'T01-C1-KLE-KL6000'

regex_pattern = re.compile(r'(\D\d{2})-(\D\d)-(\D{3})-(\D{2}\d{4})')
print(regex_pattern.search(text).groups())

