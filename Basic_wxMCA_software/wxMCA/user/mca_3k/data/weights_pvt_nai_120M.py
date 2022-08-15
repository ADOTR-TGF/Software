import json

# In Python you can make a list from a sum of lists.

def make_weights():
    #weights = [0]*24 + [-1]*25 + [0]*10 + [1]*24 
    # weights = [0]*7 + [1]*5 + [0]*15 + [-1]*60 
    weights = [0.5]*256
    weights += [0]*(1024-len(weights))
    print(json.dumps(weights)) 
    
make_weights()
