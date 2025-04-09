import os

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

dir = 'B-GRASP_IT100_b-1_Fir'
# dir = 'AltInS_Dom_cd'

# SET = 'GKD-b_n150'
# SUBSET = 'GKD-b_41_n150_b02_m15_k02'

SET = 'GKD-b_n50'
SUBSET = 'GKD-b_11_n50_b02_m5_k02'
SUBSET = 'GKD-b_11_n50_b02_m5_k03'

# SET = 'GKD-c'
# SUBSET = 'GKD-c_01_n500_b02_m50_k02'


dom_data = pd.read_csv(os.path.join('output', dir, 'GDP', SET, SUBSET, 'results_1.csv'))
ls_data = pd.read_csv(os.path.join('output', dir, 'GDP', SET, SUBSET, 'resultsAll_1.csv'))
const_data = pd.read_csv(os.path.join('output', dir, 'GDP', SET, SUBSET, 'resultsConst_1.csv'))

colors = px.colors.qualitative.Plotly

ls_data = ls_data[const_data['MaxMin'] != 0.0]
const_data = const_data[const_data['MaxSum'] != 0.0]

# Fit a linear regression line (y = mx + b)
m, b = np.polyfit(const_data['MaxSum'], ls_data['MaxSum'], 1)  # 1 for linear regression
# Generate y-values for the regression line
y_reg = m * const_data['MaxSum'] + b
fig = go.Figure()
fig.add_scatter(
    x=const_data['MaxSum'],
    y=ls_data['MaxSum'],
    mode='markers',
    showlegend=False)
fig.add_scatter(x=const_data['MaxSum'],
                y=y_reg, line_color='black',
                line_dash='dash',
                showlegend=False)
fig.update_xaxes(title_text='MaxSum values after CONSTRUCTION stage')
fig.update_yaxes(title_text='MaxSum values after LOCAL SEARCH stage')
fig.update_layout(title_text=f'Instance: {SET} - {SUBSET}')
# fig.show()
fig.write_image(f'{SET}_{SUBSET}_MaxSum_corr.png')
fig.write_html(f'{SET}_{SUBSET}_MaxSum_corr.html')

# Fit a linear regression line (y = mx + b)
m, b = np.polyfit(const_data['MaxMin'], ls_data['MaxMin'], 1)  # 1 for linear regression
# Generate y-values for the regression line
y_reg = m * const_data['MaxMin'] + b
fig = go.Figure()
fig.add_scatter(x=const_data['MaxMin'],
                y=ls_data['MaxMin'],
                mode='markers',
                showlegend=False)
fig.add_scatter(x=const_data['MaxMin'],
                y=y_reg,
                line_color='black',
                line_dash='dash',
                showlegend=False)
fig.update_xaxes(title_text='MaxMin after CONSTRUCTION stage')
fig.update_yaxes(title_text='MaxMin after LOCAL SEARCH stage')
fig.update_layout(title_text=f'Instance: {SET} - {SUBSET}')
# fig.show()
fig.write_image(f'{SET}_{SUBSET}_MaxMin_corr.png')

fig = go.Figure()
fig.add_scatter(
    x=const_data['MaxSum'],
    y=const_data['MaxMin'],
    mode='markers',
    marker_opacity=0.6,
    marker_color=colors[0],
    name='Solutions after CONSTRUCTION stage')
fig.add_scatter(
    x=ls_data['MaxSum'],
    y=ls_data['MaxMin'],
    mode='markers',
    marker_opacity=0.6,
    marker_color=colors[2],
    name='Solutions after LOCAL SEARCH stage')
fig.add_scatter(
    x=dom_data['MaxSum'],
    y=dom_data['MaxMin'],
    mode='markers',
    marker_color=colors[1],
    name='DOMINANT solutions')
fig.update_xaxes(title_text='MaxSum')
fig.update_yaxes(title_text='MaxMin')
fig.update_layout(title_text=f'Instance: {SET} - {SUBSET}')
fig.write_image(f'{SET}_{SUBSET}_solutions.png', height=400, width=1000)
# fig.show()
