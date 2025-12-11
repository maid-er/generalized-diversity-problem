import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import statsmodels.api as sm
import matplotlib.pyplot as plt
import json

def model_prediction(data):
    df = pd.DataFrame(data)

    # Scale relevant columns
    # cols_to_scale = ["MaxMin", "MaxSum", "MaxMin_pre", "MaxSum_pre"]
    # scaler = MinMaxScaler()
    # df[cols_to_scale] = scaler.fit_transform(df[cols_to_scale])

    # # Normalize MaxMin and MaxMin_pre using their global maximum
    # max_maxmin = df[["MaxMin", "MaxMin_pre"]].to_numpy().max()
    # df["MaxMin"] /= max_maxmin
    # df["MaxMin_pre"] /= max_maxmin
    #
    # # Normalize MaxSum and MaxSum_pre using their global maximum
    # max_maxsum = df[["MaxSum", "MaxSum_pre"]].to_numpy().max()
    # df["MaxSum"] /= max_maxsum
    # df["MaxSum_pre"] /= max_maxsum
    # print(df)

    # For storing all predictions for later plotting
    all_results = []

    # Loop through each algorithm type
    for algo, group_original in df.groupby("algorithm"):

        print(f"\n=== Algorithm: {algo} ===")

        # Create a copy to avoid SettingWithCopyWarning and to modify directly
        group = group_original.copy()


        for target_name in ["MaxMin", "MaxSum"]:
            print(f"\n--- Predicting {target_name} ---")

            y = group[target_name].reset_index(drop=True)
            X = group.drop(columns=["MaxMin", "MaxSum", "iteration", "algorithm"]).reset_index(drop=True)
            X = sm.add_constant(X)

            # Fit initial model
            model = sm.OLS(y, X).fit()

            # Print summary
            print(model.summary())

            # Predictions
            predictions = model.predict(X)

            # Add predictions to the 'group' DataFrame as new columns
            # The column name will be "predicted_MaxMin" or "predicted_MaxSum"
            group[f"predicted_{target_name}"] = predictions.values # Use .values to ensure proper alignment

            # Store results for plotting (if still needed for 'all_results')
            result_df = pd.DataFrame({
                "algorithm": algo,
                "target": target_name,
                "real": y,
                "predicted": predictions
            })
            all_results.append(result_df)

        # After the inner loop, 'group' now contains "predicted_MaxMin" and "predicted_MaxSum"
        print(f"\nDataFrame 'group' with predictions for algorithm {algo}:")
        print(group)

        # 2D plot with input, actual output, and prediction
        plt.figure(figsize=(6, 6))

        # Red: input space
        plt.scatter(group["MaxMin_pre"], group["MaxSum_pre"], color="red", label="Input (pre)", alpha=0.7)

        # Blue: actual target
        plt.scatter(group["MaxMin"], group["MaxSum"], color="blue", label="Actual", alpha=0.7)

        # Green: predicted target. Now using the new predicted columns from 'group'.
        # Assuming you want to plot predicted MaxMin against predicted MaxSum
        plt.scatter(group["predicted_MaxMin"], group["predicted_MaxSum"], color="green", label="Predicted", alpha=0.7)

        plt.xlabel("MaxMin or MaxMin_pre")
        plt.ylabel("MaxSum or MaxSum_pre")
        plt.title(f"2D Plot: {algo}") # Removed target_name as both are now on the plot
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.xlim(0, 200)
        plt.ylim(0, 500000)
        plt.show()

    # Optional: Return all predictions if needed
    return pd.concat(all_results, ignore_index=True)

if __name__ == '__main__':

    #
    # with open('data.txt', 'w') as f:
    #     json.dump(data_dict, f)

    with open("data.txt", "r") as f:
        data = json.load(f)

    model_prediction(data)