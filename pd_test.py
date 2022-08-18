import pandas as pd
  
# initialize data of lists.
# data = {'Name': ['Tom', 'nick', 'krish', 'jack'],
#         'Age': [20, 21, 19, 18]}

data = {'Tom': [20],
        'nick': [21],
        'krish': [19],
        'jack': [18]}
  
# Create DataFrame
df = pd.DataFrame(data).T
df.columns = ['Name']
  
# Print the output.
print(type(df.iloc[1]))
print(df.iloc[1].array)