''' Python3 program to calculate Volume and 
Surface area of Sphere'''
# Importing Math library for value Of PI 
import math 
pi = math.pi 

# Function to calculate Volume of Sphere 
def volume(r): 
	vol = (4 / 3) * pi * r * r * r 
	return vol 

# Function To Calculate Surface Area of Sphere 
def surfacearea(r): 
	sur_ar = 4 * pi * r * r 
	return sur_ar 

# Driver Code 
radius = float(12) 
print( "Volume Of Sphere : ", volume(radius) ) 
print( "Surface Area Of Sphere : ", surfacearea(radius) ) 
