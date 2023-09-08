fruits = ["ask1", "answer1","ask2", "answer2","ask3", "answer3","ask4", "answer4","ask5", "answer5"]


test = []
keep = []
for i, fruit in enumerate(fruits):
    
    keep.append(fruit)
    
    if len(keep) == 2:
        test.append(keep)
        keep = []
    
    
print(test )

reversed_array = test[::-1]
    
print(reversed_array )