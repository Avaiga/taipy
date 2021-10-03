import re
reg = re.compile(r"\{(.*?)\}")

print(type(reg.findall("a = {a} and b = {b}")))

b = eval("x + 2", {}, {"x" : 10})
print(b)