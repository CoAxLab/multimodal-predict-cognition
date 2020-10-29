"""

Class "a la scikit-learn" to generate a classifier (for regression for now)
that stacks predictions from a list of input feature matrices to be used as 
a new features in a second level training. Only lasso is implemented as the
classifier used for estimating 1st level cross-validation predictions.

    
"""

import numpy as np
from sklearn.model_selection import (cross_val_predict, KFold)
from sklearn.linear_model import (LassoCV, Lasso)
from sklearn.pipeline import make_pipeline
from copy import deepcopy
from joblib import Parallel, delayed

def type_of_target(y): 
    if y.dtype.kind == 'f' and np.any(y != y.astype(int)):
        return 'continuous'

    if (len(np.unique(y)) > 2) or (y.ndim >= 2 and len(y[0]) > 1):
        return 'multiclass'
    else:
        return 'binary' 

def check_cv(cv, shuffle, random_state, y=None):
    """Input checker utility for building a cross-validator
    Parameters
    ----------
    cv : int, cross-validation generator or an iterable, optional
        Determines the cross-validation splitting strategy.
        Possible inputs for cv are:
        - None, to use the default 5-fold cross-validation,
        - integer, to specify the number of folds.
        - :term:`CV splitter`,
        - An iterable yielding (train, test) splits as arrays of indices.
        For integer/None inputs, if classifier is True and ``y`` is either
        binary or multiclass, :class:`StratifiedKFold` is used. In all other
        cases, :class:`KFold` is used.
        Refer :ref:`User Guide <cross_validation>` for the various
        cross-validation strategies that can be used here.
        .. versionchanged:: 0.22
            ``cv`` default value changed from 3-fold to 5-fold.
    y : array-like, optional
        The target variable for supervised learning problems.
    classifier : boolean, optional, default False
        Whether the task is a classification task, in which case
        stratified KFold will be used.
    Returns
    -------
    checked_cv : a cross-validator instance.
        The return value is a cross-validator which generates the train/test
        splits via the ``split`` method.
    """
    import numbers
    
    cv = 5 if cv is None else cv
    if isinstance(cv, numbers.Integral):
        if (y is not None) and (type_of_target(y) in ('binary', 'multiclass')):
            return StratifiedKFold(n_splits=cv, shuffle= shuffle, random_state=random_state)
        else:
            return KFold(n_splits=cv, shuffle= shuffle, random_state=random_state)

    if not hasattr(cv, 'split') or isinstance(cv, str):
        if not isinstance(cv, Iterable) or isinstance(cv, str):
            raise ValueError("Expected cv as an integer, cross-validation "
                             "object (from sklearn.model_selection) "
                             "or an iterable. Got %s." % cv)
        #return _CVIterableWrapper(cv)

    return cv  # New style cv objects are passed without any modification

def _opt_params(estimator,  X, y):
    estimator.fit(X, y)
    alpha_opt = estimator.alpha_        
    return alpha_opt    

def _set_estimators(estimator, alpha_opt):
    estimator.set_params(**{'alpha': alpha_opt})
    return estimator

def _fit_estimator(estimator, X, y):
    estimator.fit(X, y)    
    return estimator   

def _fit_transform(transformer, X, y):
    transformer.fit(X, y)    
    return transformer 

def _cv_predictions(estimator, X, y, cv):
     cv_pred = cross_val_predict(estimator, X, y, cv = cv, n_jobs = 1)   
     return cv_pred

class StackingLassoCV(object):
    #@abstractmethod
    def __init__(self, 
                 prepend_transformation = [], 
                 cv=5, #n_splits = 5, 
                 random_state=None, 
                 n_jobs=None):
        self.prepend_transformation = prepend_transformation
        self.cv  = cv
        self.random_state = random_state
        self.n_jobs = n_jobs
        
    def fit(self, X_list, y, sample_weight = None):
        
        if isinstance(X_list, list) is False:
            raise ValueError("Input data must be a list")
        
        #First set cross-validation procedure
        cv = check_cv(cv = self.cv, shuffle=True, random_state = self.random_state, y=y)
        
        # Define lassoCV
        lasso_cv = LassoCV(max_iter = 1e6, cv = cv, n_jobs = 1, 
                      random_state = self.random_state) 
        
        # Store trasnformation operations and transform data
        if self.prepend_transformation:
            steps = self.prepend_transformation
            transformer = make_pipeline(*steps)
            
            transformers_ =  Parallel(n_jobs=self.n_jobs)(delayed(_fit_transform)(deepcopy(transformer), 
                                                                                  X, y) \
                                                          for X in X_list)
            
            X_list_trans = [trans.transform(X) for (trans, X) in zip(transformers_, X_list)]
        else:
            X_list_trans = X_list
            transformers_ = []
            
        self.transformers_ = transformers_
        
        #Compute alphas                                   
        self.alphas_ = Parallel(n_jobs=self.n_jobs)(
                delayed(_opt_params)(lasso_cv, X, y) for X in X_list_trans)
        
        lasso = Lasso(max_iter = 1e6, random_state = self.random_state)
        # list of optimised classifiers
        estimators_ = [_set_estimators(deepcopy(lasso), alpha) for alpha in self.alphas_]
        # Fit lasso with these parameters
        self.estimators_ = Parallel(n_jobs=self.n_jobs)(delayed(_fit_estimator)(estimator, X, y) \
            for (estimator, X) in zip(estimators_, X_list_trans))
        
        #produce single predictions
        single_predictions = Parallel(n_jobs = self.n_jobs)(
                delayed(_cv_predictions)(estimator, X, y, cv = cv) \
                for estimator, X in zip(estimators_, X_list_trans)
                )
            
        stacked_features_ = np.column_stack(single_predictions)
        self.stacked_features_ = stacked_features_
        
        return self
    
    
    def predict(self, X_list):
        
        """
        
        This function uses the already fitted single and
        multimodal models to return the predictions.
        
        
        """
        y_pred = []
        
        if self.transformers_:
            X_list_trans = [trans.transform(X) for (trans, X) in zip(self.transformers_, X_list)]
        else:
            X_list_trans = X_list
            
        for estim, X in zip(self.estimators_, X_list_trans):
            y_pred_single = estim.predict(X)
            y_pred.append(y_pred_single)
            
        y_pred = np.column_stack(y_pred)
    
        return y_pred

