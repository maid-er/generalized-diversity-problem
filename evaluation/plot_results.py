import os
import pandas as pd
import plotly.express as px


# instance = 'USCAP/Bi-objective'
# file = 'results_USCAP_5.csv'
path = 'GDP/SOM-a'
instance = 'SOM-a_20_n50_b02_m15_k03'
file = 'IT100_beta025_LSFirst/results_1.csv'

cap_table = pd.read_csv(os.path.join('output', 'USCAP', 'abbreviation_node.csv'), sep=';',
                        names=['State', 'number', 'Abbr'])

filename = os.path.join('output',
                        path,
                        instance,
                        file)

result_table = pd.read_csv(filename)

if 'USCAP' in instance:
    result_table.Solution = result_table.Solution.apply(lambda s: [int(n) for n in s.split('-')])
    results = result_table.Solution.apply(
        lambda nodes: cap_table.Abbr.loc[cap_table.number.isin(nodes)].to_list())
    results = results.apply(lambda s: ' - '.join(s))

    legend_name = 'Solution and constraint values'
    result_table[legend_name] = ('<b>' + results + '</b>' + '<br>'
                                 'Cost: ' + result_table.Cost.astype(str) +
                                 ' & Capacity: ' + result_table.Capacity.astype(str))

else:
    legend_name = 'Constraint values'
    result_table[legend_name] = ('Cost: ' + result_table.Cost.astype(str) +
                                 ' & Capacity: ' + result_table.Capacity.astype(str))

fig = px.scatter(result_table, x='MaxMin', y='MaxSum')
# fig = px.scatter(result_table, x='MaxMin', y='MaxSum', color=legend_name,
#                  color_discrete_sequence=px.colors.qualitative.Light24)
fig.update_traces(marker={'size': 8})
fig.update_layout(title_text=instance)
fig.show()
