import json

def make_weights():
    """
        Weights for NaI(Tl) vs PVT plastic scintillator PSD.
        Timed for gain_select = 2 (ie Z=1100 Ohms)
        Note: # In Python you can make a list from a sum of lists.
    """
    weights = [0]*5 +[-1]*3 + [0.70]*5 + [-1]*20
    weights += [0]*(1024-len(weights))  # Fill in the rest with zeros. 
    print(json.dumps(weights))
    
make_weights()