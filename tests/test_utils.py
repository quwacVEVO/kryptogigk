import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from kryptolib.utils import process_file, format_columns

current_dir = os.path.dirname(__file__)

alfa_26_input = os.path.join(current_dir, "alfa_26_data_set.txt")
alfa_26_output = os.path.join(current_dir, "alfa_26_cleaned_set.txt")

alfa_37_input = os.path.join(current_dir, "alfa_37_data_set.txt")
alfa_37_output = os.path.join(current_dir, "alfa_37_cleaned_set.txt")

data_set_1 = process_file(alfa_26_input, alfa_26_output, mode="alfa_26")
data_set_2 = process_file(alfa_37_input, alfa_37_output, mode="alfa_37")

#print(data_set_1)
#print(data_set_2)
print(format_columns(data_set_1))