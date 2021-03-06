# Functions for metrics calculation
import numpy as np
from sklearn.metrics import mean_squared_error, roc_auc_score


# MAPE
def mean_absolute_percentage_error(y_true, y_pred):
    """
    MAPE (Mean Absolute Percentage error) calculation
    :param y_true: array, ground truth
    :param y_pred: array, predicted values
    :return: MAPE
    """
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs(y_true - y_pred) / y_true)


def mape_lgb(preds, dtrain):
    """
    MAPE (Mean Absolute Percentage error) for LightGBM data

    :param preds: array, predicted values
    :param dtrain: lgb.Dataset, true values
    :return: MAPE
    """
    actuals = np.array(dtrain.get_label())
    return 'mape', mean_absolute_percentage_error(actuals, preds), False


# SMAPE
def symmetric_mean_absolute_percentage_error(y_true, y_pred):
    """
    Symmetric Mean Absolute Percentage Error (SMAPE)

    :param y_true: array-like, true values
    :param y_pred: array-like, predicted values
    :return: SMAPE
    """
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs(y_true - y_pred) / (y_true + y_pred + 1))


def smape_lgb(preds, dtrain):
    """
    Symmetric Mean Absolute Percentage Error (SMAPE) for LightGBM

    :param preds: array, predicted values
    :param dtrain: lgb.Dataset, true values
    :return: SMAPE
    """
    actuals = np.array(dtrain.get_label())
    return 'smape', symmetric_mean_absolute_percentage_error(actuals, preds), False


# RMSE
def rmse(y_true, y_pred):
    """
    Calculate Root Mean Squared Error (RMSE) for 2 arrays
    
    :param y_true: array, true values
    :param y_pred: array, predicted values
    :return: RMSE
    """
    return np.sqrt(mean_squared_error(y_true, y_pred))


def rmse_lgb(preds, dtrain):
    """
    Root Mean Squared Error (RMSE) for LightGBM data
    
    :param preds: array, predicted values
    :param dtrain: lgb.Dataset, true values
    :return: RMSE
    """
    actuals = np.array(dtrain.get_label()) 
    return 'rmse', rmse(actuals, preds), False


# RMSLE
def rmsle_xgb(preds, dtrain):
    """
    Root Mean Squared Logarithmic Error (RMSLE) for XGBoost

    :param preds: array, predicted values
    :param dtrain: xgb.DMatrix, true values
    :return: RMSLE
    """
    actuals = dtrain.get_label()
    temp_values = np.power(np.log1p(np.fmax(0., actuals)) - np.log1p(np.fmax(0., preds)), 2)
    return 'rmsle', np.sqrt(np.mean(temp_values)) 


# Gini
def ginic(actual, pred):
    """
    Gini calculation from https://www.kaggle.com/tezdhar/faster-gini-calculation
    """
    actual = np.asarray(actual)  # In case, someone passes Series or list
    n = len(actual)
    a_s = actual[np.argsort(pred)]
    a_c = a_s.cumsum()
    giniSum = a_c.sum() / a_s.sum() - (n + 1) / 2.0
    return giniSum / n


def gini_normalizedc(actual, pred):
    if pred.ndim == 2:  # Required for sklearn wrapper
        pred = pred[:, 1]  # If proba array contains proba for both 0 and 1 classes, just pick class 1
    return ginic(actual, pred) / ginic(actual, actual)


def gini_xgb(preds, dtrain):
    """
    Gini for XGBoost
    """
    actuals = dtrain.get_label()
    return [('gini', gini_normalizedc(actuals, preds))]


def gini_lgb(preds, dtrain):
    """
    Gini for LightGBM
    """
    actuals = np.array(dtrain.get_label()) 
    return 'gini', gini_normalizedc(actuals, preds), True 


# ROC AUC
def auc_lgb(preds, dtrain):
    actuals = np.array(dtrain.get_label()) 
    return 'auc', roc_auc_score(actuals, preds), True


# Average Precision (AP@k) and Mean Average Precision (MAP@k)
# from https://github.com/benhamner/Metrics/blob/master/Python/ml_metrics/average_precision.py


def apk(actual, predicted, k=5):
    """
    Computes the average precision at k.
    This function computes the average precision at k between two lists of
    items.
    Parameters
    ----------
    actual : list
             A list of elements that are to be predicted (order doesn't matter)
    predicted : list
                A list of predicted elements (order does matter)
    k : int, optional
        The maximum number of predicted elements
    Returns
    -------
    score : double
            The average precision at k over the input lists
    """
    if len(predicted) > k:
        predicted = predicted[:k]

    score = 0.0
    num_hits = 0.0

    for ind, pred in enumerate(predicted):
        if pred in actual and pred not in predicted[:ind]:
            num_hits += 1.0
            score += num_hits / (ind + 1.0)

    if not actual:
        return 0.0

    return score / min(len(actual), k)


def mapk(actual, predicted, k=5):
    """
    Computes the mean average precision at k.
    This function computes the mean average prescision at k between two lists
    of lists of items.
    Parameters
    ----------
    actual : list
             A list of lists of elements that are to be predicted
             (order doesn't matter in the lists)
    predicted : list
                A list of lists of predicted elements
                (order matters in the lists)
    k : int, optional
        The maximum number of predicted elements
    Returns
    -------
    score : double
            The mean average precision at k over the input lists
    """
    return np.mean([apk(act, pred, k) for act, pred in zip(actual, predicted)])
