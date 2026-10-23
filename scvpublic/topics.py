"""Offline NMF evaluation helpers; not imported by Flask."""
import numpy as np


def topic_coordinates(weights, components):
    """Remove NMF factor-scale ambiguity, then normalize topic mixtures."""
    values=weights*np.linalg.norm(components,axis=1)
    norms=np.linalg.norm(values,axis=1,keepdims=True)
    return np.divide(values,norms,out=np.zeros_like(values),where=norms>0)


def ranked_cases(scores, documents):
    return [dict(documents[int(i)],score=float(scores[i]))
            for i in np.argsort(-scores,kind='stable') if scores[i]>1e-8]
