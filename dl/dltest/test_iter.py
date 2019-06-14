

a=[1,2,3,4,5]
b=a

for i in a:
    if i==1:
        b.remove(1)
    if i==2:
        b.remove(2)
print(b)
print(a)