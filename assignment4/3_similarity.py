import numpy as np
from scipy import spatial
from math import log

def applyLog(array):
    out = []
    for i in array: 
        if i > 0:
            out.append(log(i,10))
        else:
            out.append(0)
    return out

# Load both fingerprint files
fp1 = np.load("fingerprints_ours.npy")
fp2 = np.load("fingerprints_theirs.npy")

debug = False

# Iterate over our fingerprints
for i in range(fp1.shape[0]):

    # Extract current site
    db = fp1[i]

    if np.sum(db) == 0:
        continue

    # Iterate over fingerprints from their sites
    for j in range(fp2.shape[0]):
        theirs = fp2[j]
        
        if np.sum(theirs) == 0:
            continue

        # Get receive and send packages and apply log
        db_received = applyLog(db[0])
        db_sent = applyLog(db[1])

        theirs_received = applyLog(theirs[0])
        theirs_sent = applyLog(theirs[1])

        # Calculate similarity 
        result_rec = 1 - spatial.distance.cosine(db_received, theirs_received)
        result_sen = 1 - spatial.distance.cosine(db_sent, theirs_sent)

        if debug:
            print("Similarities: sent {}, received {}".format(result_rec, result_sen))

        if result_rec > 0.5 and result_sen > 0.5:
            print("Site {} and site {} are similar".format(i, j))


