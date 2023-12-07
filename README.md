# Data
The folders contain necessary city data (e.g., boundaries, tiers, and the generated dictionaries) and regional GDP data. 

For job postings and search queries, since the original data are large and the computation needs spark and hadoop environment, we provide the resulting data.

# Pre-processings


## Labour Flow Intention

### Flow Intention Extraction
Code stored in SparkProcess/TransitionProcess. 

Since the original data are large and the computation needs spark and hadoop environment, we provide the resulting data in data/transition.

### Make Graphs
python DataProcessing/GraphAnalysisProcess/P1_transition.py

The results are in /results/AnalysisData/[all, month, season]/graph

### Calculate Centralities
python DataProcessing/GraphAnalysisProcess/P2_centrality.py

The results are in /results/AnalysisData/[all, month, season]/centrality

### Clustering
python DataProcessing/GraphAnalysisProcess/P3_clustering.py

The results are in results/AnalysisData/{all/month/season}/clustering

## JD

### JD Clustering
Code stored in SparkProcess/LDA.

Since the original data are large and the computation needs spark and hadoop environment, we provide the resulting data in data/JDData.

### Count Each Cluster
python DataProcessing/JDProcess/J3_city_count_kmeans_time.py

The results are in /results/AnalysisData/[all, month, season]/jd

## Flow and JD with Types

### Align Educational Class
python DataProcessing/TypePreprocessing/P31_education_alignment.py

The results are in /results/Mismatch/edu

### Align Sector Class
python DataProcessing/TypePreprocessing/P32_industry_alignment.py

The results are in /results/Mismatch/industry

### Align Salary Class
python DataProcessing/TypePreprocessing/P33_salary_alignment.py

The results are in /results/Mismatch/salary

### Get Type-Aware Centrality
python DataProcessing/TypePreprocessing/P4_centrality.py

The results are in /results/Mismatch/edu


## Analysis
### Correlation with CMDS (Figure A1)
python Analysis/validate_with_real/A1_corr_with_CMDS.py

The results are in /results/Trans_valid/[Pearson, Spearman]_CMDS.png

### General Correlation with GPS-induced Mobility (Fig. A2)
python Analysis/validate_with_real/A2_generic_corr_with_beijing.py

The results are in /results/Trans_valid/[Pearson, Spearman]_GPS.png

### Temporal Correlation with GPS-induced Mobility (Fig. A3)
python Analysis/validate_with_real/A3_time_corr_with_beijing.py

The results are in /results/Trans_valid/corr_hist_GPS.png and /results/Trans_valid/lag_bar_GPS.png 

### Job Type Classification Evaluation (Table A6)
python Analysis/jd_validation/A1_average_analysis.py

The results are printed in the terminal

### Precision of Job Posting Classes (Fig. A17)
python Analysis/jd_validation/A2_precision_draw.py

The results are printed in the terminal

### Boxplot and Lineplot for Hub, Authority, Gross Flow, Net Inflow in Different Tiers (Fig. A6, Fig. 3(a), Fig. 2(a), Fig. 2(b), Fig. 2(c))
python Analysis/CentralityAnalysis/A3_hub_auth_distribution.py

Boxplot: Generate figures as results/Centrality/temporal_centrality/level_boxplot_{auth/hub}_{time}to{time}.png

Lineplot: Generate figures as results/Centrality/temporal_centrality/level_line_{auth/hub}.png


### Lineplot for Hub and Authority in Different Cities (Fig. A13)
python Analysis/CentralityAnalysis/A4_hub_auth_line.py {month/season}

Generate figures as results/Centrality/temporal_centrality/{authority/hub}_city_line_{month/season}.png


### Boxplot for Hub and Authority Change (Fig. 3(b))
python Analysis/CentralityAnalysis/A5_centrality_change.py

Generate figures as results/Centrality/level_boxplot_{authority/hub}.png and 

### Heatmap for Cross-tier Flow Intention (Fig. 3(c))
python Analysis/CentralityAnalysis/A6_tier_flow.py

Generate figures as results/Centrality/tier_graph_inc_{time}.png

### Correlation with GDP (Table A4)
python Analysis/CentralityAnalysis/wholeyear/A21_centrality_GDP_wholeyear.py

Output the correlations in terminal

### 2D Plane of Hub and Authority & Ratio Boxplot (Fig. 2(a) and Fig. A7)
python Analysis/CentralityAnalysis/wholeyear/A31_hub_auth_classify_wholeyear.py

2D plane: Generate a figure as results/Centrality/wholeyear/auth_hub_2D.png

Ratio Bxoplot: Generate a figure as results/Centrality/wholeyear/level_boxplot_ratio.png

### The Line Plot of Demand Change  (Fig. 5(c) and Fig. A18)
python Analysis/JDAnalysis/A1_demand_line_number.py

Generate figures as /results/JD/level_lineplot_{month/season}_jd_{}.png

### Blue Collar Demand Ratio in Different Tiers (Fig. A21)
python Analysis/JDAnalysis/A2_bluecollar_ratio.py

Generate a figure as /results/JD/Blue Collar_ratio.png

### Occupation Ratio of Different Blue Collar Demands (Fig. A19, Fig. A20)
python Analysis/JDAnalysis/A3_demand_occupation_tier.py

Generate figures as /results/JD/occupation/{month/season}/line_{}_Blue Collar.png

### Typical Labour Demand in Urban Agglomerations (Fig. A24, Fig. A25)
python Analysis/RegionAnalysis/region_compare.py

Generate figures as /results/Region/{month/season}/{}_change_region_compare.png and /results/Region/occupation/line_{PRD/YRD/BTH}_BlueCollar.png

### Intention of Flowing to Hihgly-paied area (Fig. A26)
python Analysis/IncomeAnalysis/P6_income_bytype.py

python Analysis/IncomeAnalysis/P7_income_tier_bytype.py

Generate figures as /results/IncomeLoss/{month/season}/centrality_with_income/city_income_diff_{}_salary_TRUE_4_t2.png 

### Sector Mismatch (Fig. 6)
python Analysis/MismatchAnalysis/P5_get_rank.py

python Analysis/MismatchAnalysis/P9_wordcloud.py

Generate figures as /results/Mismatch/{region}_{time}.png 

# Visualizations
After the processing steps, the initial intermediate results have been generated for visualization. We implemented a geographical visualization system with django framework. The code are in code/Site. To start it, run python manage.py runserver 0.0.0.0:8000. Then, browse 127.0.0.1/8000 with a browser. The urls which can be browsed are shown in the page. By setting the parameters in the bottom of the page, results in our paper can be reproduced.