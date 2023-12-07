import sys
sys.path.append('/code')
import pandas as pd
from tqdm import tqdm
import seaborn as sns
import matplotlib.pyplot as plt
from CONFIG import *
from Utils.tools import make_path
plt.switch_backend('agg')

def get_job_cate_funcs():
    return {'All': list(range(30)), 
            'Public Transit Staff': [1, 5, 19, 22, 24], 'Transporter': [18], 'Security': [23],
            'Blue Collar': [1, 5, 19, 22, 24, 0, 3, 4, 7, 11, 12, 17, 18, 25, 26, 29],
            'Factory Worker': [0, 3, 4, 7, 11, 12, 17, 25, 26, 29], 
            'Clerk': [8, 27], 'Merchandiser': [14], 'Salesman': [20, 28], 'Others': [6],
            'Beautician': [15],
            'Designer': [9], 'Manager': [2, 16], 'Engineer': [21], 'White Collar': [2, 9, 16, 21]}

if __name__ == "__main__":
    make_path(OUT_JD_VALID_PATH)
    df = pd.read_csv("%s/jd_validation/annotation_label.csv" % DATA_PATH)
    df = df[df['name'] != 'Others'] [['name', 'Label']]
    df_sum = df.groupby('name').agg(['count', 'sum']).reset_index()
    df_sum['Precision'] = df_sum[('Label', 'sum')] / df_sum[('Label', 'count')]
    df_sum.rename(columns={'name': 'Name'}, inplace=True)
    sns.barplot(data=df_sum, x='Name', y='Precision')
    plt.xticks(rotation=90)
    plt.savefig('%s/precision.png' % OUT_JD_VALID_PATH, bbox_inches='tight')
