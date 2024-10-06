def evenOdd(n):

  # if n&1 == 0, then num is even
  if n & 1:
    return False
  # if n&1 == 1, then num is odd
  else:
    return True


# Input by geeks
num = 3
if(evenOdd(num)):
    print(num, "num is even")
else:
    print(num, "num is odd")
