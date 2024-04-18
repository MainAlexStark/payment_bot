# import os

# def check_quotes(filename):
#     with open(filename, 'r') as file:
#         for line_number, line in enumerate(file, 1):
#             if "'" in line and "'''" not in line:
#                 if line.count("'") % 2 != 0:
#                     print(f"File: {filename}, Line: {line_number}, Uneven number of single quotes")
#             if '"' in line and '"""' not in line:
#                 if line.count('"') % 2 != 0:
#                     print(f"File: {filename}, Line: {line_number}, Uneven number of double quotes")

# for root, dirs, files in os.walk(".", topdown=False):
#     for name in files:
#         if name.endswith(".py"):
#             filename = os.path.join(root, name)
#             check_quotes(filename)

all_cost = 66
num_purchases = 1
num_refferals = 0

all_cost = all_cost*(1-(float(20)/100))
print(all_cost)
if num_purchases is not None:
        if num_refferals is not None:
            if num_refferals>5:num_refferals=5
            for i in range(num_refferals):all_cost = float(all_cost)*(1-(float(20))/100)
print(all_cost)
all_cost = int(round(all_cost, -1) - 1)


print(all_cost)