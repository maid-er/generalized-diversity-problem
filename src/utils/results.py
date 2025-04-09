'''Class to handle result plotting and saving'''
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


class OutputHandler:
    '''Class to handle result plotting and saving'''
    def __init__(self):
        '''Initialize OutputHandler'''
        self.execution_n = -1
        # TODO add boolean input for PLOT
        self._get_execution_number()

    def pareto_front(self, table: pd.DataFrame, instance: str) -> go.Figure:
        '''
        Generates a scatter plot using data from a DataFrame and customizes the plot.

        Args:
          table (pd.DataFrame): contains solution data.
          instance (str): represents the name or path of a specific file (instance).

        Returns:
          (go.Figure): figure with solution's Pareto Front plot.
        '''
        table['Constraint values'] = ('Cost: ' + table.Cost.astype(str) +
                                      ' & Capacity: ' + table.Capacity.astype(str))
        fig = px.scatter(table, x='MaxMin', y='MaxSum', color='Constraint values')
        fig.update_layout(title_text=os.path.split(instance)[-1].split(".")[0])
        # fig.show()

        return fig

    def save(self, table: pd.DataFrame, all_sols, c_sols, add_data: dict,
             figure: go.Figure, params: str, instance: str):
        '''
        This function saves the solution DataFrame as a CSV and the Figure as an HTML file in a
        specified directory structure that contains the instance name and execution number as ID.

        Args:
          table (pd.DataFrame): contains solution data.
          figure (go.Figure): figure with solution's Pareto Front plot.
          params (str): parameter configuration used in the optimization algorithm.
          instance (str): represents the name or path of a specific file (instance).
        '''
        instance_path = instance.split(os.sep)[1:]
        instance_path = [s.replace('.txt', '') for s in instance_path]
        output_path = os.path.join('output',
                                   f'B-GRASP_{params}',
                                   *instance_path)

        os.makedirs(output_path, exist_ok=True)

        # c_sols.to_csv(os.path.join(output_path,
        #                           f'resultsConst_{self.execution_n}.csv'),
        #              index=False)

        # all_sols.to_csv(os.path.join(output_path,
        #                           f'resultsAll_{self.execution_n}.csv'),
        #              index=False)

        table.to_csv(os.path.join(output_path,
                                  f'results_{self.execution_n}.csv'),
                     index=False)

        self._save_execution_add_data(add_data, output_path)

        # figure.write_html(os.path.join(output_path,
        #                                f'solution_{self.execution_n}.html'))

    def _get_execution_number(self):
        '''
        The function reads an execution number from a file, increments it by 1, and writes the
        updated number back to the file.
        '''
        execution_file = os.path.join('temp', 'execution.txt')

        if os.path.exists(execution_file):
            with open(execution_file, 'r+') as file:
                self.execution_n = file.read()
                file.seek(0)
                file.write(str(int(self.execution_n) + 1))
                file.truncate()
        else:
            self.execution_n = 1
            os.makedirs('temp', exist_ok=True)
            with open(execution_file, 'w') as file:
                file.write(str(int(self.execution_n) + 1))

    def _save_execution_add_data(self, add_data: dict, path: str):
        '''
        The function saves algorithm's execution time `secs` in seconds in a csv file.
        '''
        time_file = os.path.join(path, 'add_data.csv')
        new_row = {'ex_number': [self.execution_n]}
        new_row.update(add_data)
        if os.path.exists(time_file):
            time_table = pd.read_csv(time_file)
            time_table = time_table.append(pd.DataFrame(new_row))
        else:
            time_table = pd.DataFrame(new_row)

        time_table.to_csv(time_file, index=False)
