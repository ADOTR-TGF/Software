import json

def make_weights():
    weights = [1]*1024
    weights += [0]*(1024-len(weights))
    #weights = [1]*128 # [0]*10+[1]*118  # In Python you can make a list from a sum of lists.
    print(json.dumps(weights))
    
make_weights()