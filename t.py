import pandas

the_dict={ 'a': 0, 'b': "the b"}
print(f"the dict: {the_dict}")
print(f"the dict['b']: {the_dict['b']}")

the_other_dict={ 'c': 0, 'd': 'the d' }
print(f"the other dict: {the_other_dict}")
print(f"the other_dict['d']: {the_other_dict['d']}")
# print(f"the other f-string dict: {{ 'c': 0, 'd': 'the d'}['d']}")

the_df=pandas.dataframe({"colA": [1, 2, 3]})
print(f"the df: {the_df}")
# print(f"the f-string df: {pandas.dataframe({"colA": [1, 2, 3]})}")

