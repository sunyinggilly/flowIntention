import sys
sys.path.append('/code')
import pandas as pd
from tqdm import tqdm
from CONFIG import *
from sklearn.metrics import precision_score, recall_score, accuracy_score

def get_job_cate_funcs():
    return {'All': list(range(30)), 
            'Public Transit Staff': [1, 5, 19, 22, 24], 'Transporter': [18], 'Security': [23],
            'Blue Collar': [1, 5, 19, 22, 24, 0, 3, 4, 7, 11, 12, 17, 18, 25, 26, 29],
            'Factory Worker': [0, 3, 4, 7, 11, 12, 17, 25, 26, 29], 
            'Clerk': [8, 27], 'Merchandiser': [14], 'Salesman': [20, 28], 'Others': [6],
            'Beautician': [15],
            'Designer': [9], 'Manager': [2, 16], 'Engineer': [21], 'White Collar': [2, 9, 16, 21]}

if __name__ == "__main__":
    df = pd.read_csv("%s/jd_validation/title_topic_recall.csv" % DATA_PATH)

    df_now = df.sample(frac=2000/df.shape[0])
    df_now.to_csv('title_topic_recall_2000.csv', index=False)

    y_pred = df['name']
    y_true = df['Label']
    pr = precision_score(y_pred=y_pred, y_true=y_true, average='macro')
    re = recall_score(y_pred=y_pred, y_true=y_true, average='macro')
    acc = accuracy_score(y_pred=y_pred, y_true=y_true)
    print(pr, re, acc)