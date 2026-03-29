import os

import pandas as pd
import plotly.express as px
from scipy.stats import wilcoxon
# Directory with results
result_dir = 'outputestaru'

file_path = os.path.join(result_dir, 'indicators.csv')

data = pd.read_csv(file_path)
data = data[data['alg_config'] != "Gurobi"]
# Ignore instances with no solutions
# data['Non-dominated solution rate [%]'] = data['nd_sols'] / data['all_sols'] * 100
# data = data[data['Non-dominated solution rate [%]'] != 100]

# fig = px.box(data, x='alg_config', y='time')
# fig.update_xaxes(title_text='GRASP MO strategy: Construction_LocalSearch')
# fig.update_yaxes(title_text='Time [s]')
# fig.update_layout(title_text='Execution time')
# fig.write_html('output/ex_time.html')
# fig.show()

# fig = px.histogram(data, x='HV', color='alg_config')
# fig.show()
#

# import seaborn as sns
# import matplotlib.pyplot as plt
#
# # Set a nice style
# sns.set_theme(style="whitegrid")
#
# plt.figure(figsize=(10, 6))
# ax = sns.boxplot(data=data, x='alg_config', y='HV', palette="Set2")
#
# # Customizing labels
# plt.title('Hypervolume Distribution')
# plt.xlabel('GRASP MO strategy: Construction_LocalSearch')
# plt.ylabel('HV')
#
# # Save and show
# plt.savefig('output/hypervolume.png', dpi=300)
# plt.show()
#
#
#
# fig = px.box(data, x='alg_config', y='HV')
# fig.update_xaxes(title_text='GRASP MO strategy: Construction_LocalSearch')
# fig.update_layout(title_text='Hypervolume')
# fig.write_html('output/hypervolume.html')
# fig.show()
#
# fig = px.box(data, x='alg_config', y='SC')
# fig.update_xaxes(title_text='GRASP MO strategy: Construction_LocalSearch')
# fig.update_layout(title_text='Set Coverage')
# fig.write_html('output/set_coverage.html')
# fig.show()
#
# fig = px.box(data, x='alg_config', y='eps')
# fig.update_xaxes(title_text='GRASP MO strategy: Construction_LocalSearch')
# fig.update_layout(title_text='Epsilon Indicator')
# fig.write_html('output/eps.html')
# fig.show()

# df2 = data[data['alg_config'].isin(['Alt-Btw-LC', 'Alt-Btw-3FO'])]
# df_hv = df2.pivot(index='inst', columns='alg_config', values='eps')
# df_hv = df_hv.dropna()  # remove instances missing one algorithm
# # arrays of length 30
#
# stat, p_value = wilcoxon(
#     df_hv['Alt-Btw-3FO'],
#     df_hv['Alt-Btw-LC'],
#     alternative='greater'  # or 'greater' / 'less'
# )
#
# print("Statistic:", stat)
# print("p-value:", p_value)

df_long = pd.melt(
    data,
    id_vars=['alg_config'],
    value_vars=['HV', 'SC', 'eps'],
    var_name='Metric',
    value_name='Value'
)

import seaborn as sns
import matplotlib.pyplot as plt

is_special_alg = ['NSGA2', 'SPEA2', '[2] NSGA2', '[3] SPEA2']
alg_order = sorted(
    df_long['alg_config'].unique(),
    key=lambda x: (any(s in x for s in is_special_alg), x)
)
# Set the visual style
sns.set_theme(style="whitegrid")

plt.figure(figsize=(12, 6))

# Create the boxplot
ax = sns.boxplot(
    data=df_long,
    x='alg_config',
    y='Value',
    hue='Metric',
    palette='muted',
    order=alg_order
)

# Customizing the labels
# plt.title('Performance Metrics by Algorithm Configuration', fontsize=15)
plt.xlabel('Algorithm', fontsize=12)
plt.ylabel('Value')
plt.xticks(rotation=45) # Helps if alg_config names are long

# Save and Show
plt.tight_layout()
plt.savefig('output/all_metrics_seaborn.png', dpi=300)
plt.show()


# fig = px.box(
#     df_long,
#     x='alg_config',
#     y='Value',
#     color='Metric'
# )
#
# fig.update_xaxes(title_text='GRASP MO strategy: Construction_LocalSearch')
# fig.update_layout(
#     boxgap=0.1,        # space between boxes in same group (default ~0.3)
#     boxgroupgap=0    # space between alg_config groups
# )
#
# fig.write_html('output/all_metrics_single_plot.html')
# fig.show()

# fig = px.box(data, x='alg_config', y='Non-dominated solution rate [%]')
# fig.update_xaxes(title_text='GRASP MO strategy: Construction_LocalSearch')
# fig.update_layout(title_text='Non-dominated / All solutions ratio')
# fig.write_html('output/sol_ratio.html')
# fig.show()
