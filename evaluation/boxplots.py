import os

import pandas as pd
import plotly.express as px

# Directory with results
result_dir = 'output'

file_path = os.path.join(result_dir, 'indicators.csv')

data = pd.read_csv(file_path)
# Ignore instances with no solutions
data['Non-dominated solution rate [%]'] = data['nd_sols'] / data['all_sols'] * 100
data = data[data['Non-dominated solution rate [%]'] != 100]

fig = px.box(data, x='alg_config', y='time')
fig.update_xaxes(title_text='GRASP MO strategy: Construction_LocalSearch')
fig.update_yaxes(title_text='Time [s]')
fig.update_layout(title_text='Execution time')
fig.write_html('output/ex_time.html')
fig.show()

fig = px.box(data, x='alg_config', y='HV')
fig.update_xaxes(title_text='GRASP MO strategy: Construction_LocalSearch')
fig.update_layout(title_text='Hypervolume')
fig.write_html('output/hypervolume.html')
fig.show()

# fig = px.histogram(data, x='HV', color='alg_config')
# fig.show()

fig = px.box(data, x='alg_config', y='SC')
fig.update_xaxes(title_text='GRASP MO strategy: Construction_LocalSearch')
fig.update_layout(title_text='Set Coverage')
fig.write_html('output/set_coverage.html')
fig.show()

fig = px.box(data, x='alg_config', y='eps')
fig.update_xaxes(title_text='GRASP MO strategy: Construction_LocalSearch')
fig.update_layout(title_text='Epsilon Indicator')
fig.write_html('output/eps.html')
fig.show()

fig = px.box(data, x='alg_config', y='Non-dominated solution rate [%]')
fig.update_xaxes(title_text='GRASP MO strategy: Construction_LocalSearch')
fig.update_layout(title_text='Non-dominated / All solutions ratio')
fig.write_html('output/sol_ratio.html')
fig.show()
