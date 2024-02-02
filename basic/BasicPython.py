print('Hello, world')
print('Hello, {}'.format('world'))
print('Hello, {}'.format('Sam'))
print('Hello{}'.format('Sam'))

# This is a comment and it is ignored by the Python interpreter: print('This is part of a comment')
print('Not a comment') # This part is also a comment

# Assign values to variables
x = 5
y = 10
print(x)

# Print the value of variables x and y
print('x is {} and y is {}'.format(x, y))

# Print the sum of variables x and y
print('x + y = {}'.format(x + y))

# Print the product of variables x and y
z = x*y
print('x * y = {}'.format(z))

d = x/y
print('x / y = {}'.format(d))

# Defining functions
def add(x, y):
    return x + y

print("7 plus 3 is: {}".format(add(7, 3)))

def add2(a, b):
    return x + y

print("7 plus 3 is NOT: {}".format(add2(7, 3)))

# Time formatting
minutes = 40
seconds = 9
print("Time elapsed: {:02d}:{:02d}".format(minutes, seconds))
seconds = seconds + 92
print("Time elapsed: {:02d}:{:02d}".format(minutes, seconds))
if (seconds > 60):
    seconds = seconds - 60
    minutes = minutes + 1
print("Time elapsed: {:02d}:{:02d}".format(minutes, seconds))

seconds += 153
print("Time elapsed: {:02d}:{:02d}".format(minutes, seconds))

# Use the modulus operator to get the remainder
print("The seconds hand is at {:02d}".format(seconds % 60))

# The following line would cause an error
#print("Time elapsed: {:02d}:{:02d}".format(minutes + seconds / 60, seconds % 60))

# Try removing the formatting from minutes
print("Time elapsed: {}:{:02d}".format(minutes + seconds / 60, seconds % 60))

# Typecast the result of the division to an integer to get the increase in minutes
print("Time elapsed: {:02d}:{:02d}".format(minutes + (int)(seconds / 60), seconds % 60))

# Print the values of global variables x, y, and z
print("x={}, y={}, z={}".format(x, y, z))
x = x + 2
print("x={}, y={}, z={}".format(x, y, z))

# Demonstrate order of operations
print("x+1*y-3/z is: {}".format(x+1*y-3/z))

print("(x+1)*(y-3)/z is: {}".format((x+1)*(y-3)/z))

print("z % x*2 is: {}".format(z%x*2))

print("z % (x*2) is: {}".format(z%(x*2)))

# Create a list of numbers
l = [17, 31, 5, 11, 12, 14, 24]

# Print the whole list
print(l)

# print the first item (python always counts from 0, not 1!)
print(l[0])

# The following line would cause an error
#print(l[7])

# Print the 6th item (remember the 7 items in the list are numbered 0 through 6, so item 6 is the last item)
print(l[6])

# print the number of items
print("There are {} items".format(len(l)))

# Print each item in the list 'l', one line at a time
print("----")
for amount in l:
    print(amount)

# Print items starting at 1 and stopping before 3 (so, item 1 & 2) in the list 'l', one line at a time
print("----")
for i in range(1,3):
    print(l[i])

# Print just the part of the list including item 1 & 2
print(l[1:3])

# Print the list in sorted order
l.sort()
print(l)

# Note that the first item of the list has changed
print(l[0])

# Print the list in reverse order
backwards = sorted(l, reverse=True)
print(backwards)

# Note that the list 'l' is unchanged by sorted
print(l)

# Print a string
s = "I can code."
print(s)
print("The string is: {}".format(s))

# Print the first item and the middle letters 2 through 4 of the string (remember, always count from 0!)
print("The string starts with '{}' and the middle is '{}'".format(s[0], s[2:5]))

# Try to modify the string
# The following line would cause an error
#s[0] = 'U'

# But, you can create a new string and assign it to s
s = "U" + s[1:]
print(s)
