"""
Sample data pipeline for chromatographic/mass spectrometric data
"""

import os
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt


class DataPipeline:
    def __init__(self, data_dir):
        self.data_dir = data_dir

    def list_data_files(self):
        """List CSV files in the data directory."""
        return [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]

    def load_data(self, filename):
        """Load a CSV data file as a pandas DataFrame."""
        file_path = os.path.join(self.data_dir, filename)
        return pd.read_csv(file_path)

    def normalize(self, df):
        """Normalize numeric columns to 0-1 range."""
        numeric = df.select_dtypes(include='number')
        norm = (numeric - numeric.min()) / (numeric.max() - numeric.min())
        df_norm = df.copy()
        df_norm[numeric.columns] = norm
        return df_norm

    def summary_statistics(self, df):
        """Return summary statistics for numeric columns."""
        return df.describe().to_dict()

    def fit_linear_regression(self, df, x_col, y_col):
        """Fit linear regression and return model, coefficients, and R^2 score."""
        X = df[[x_col]].values
        y = df[y_col].values
        model = LinearRegression()
        model.fit(X, y)
        y_pred = model.predict(X)
        r2 = r2_score(y, y_pred)
        return {
            'coef': model.coef_.tolist(),
            'intercept': model.intercept_,
            'r2_score': r2
        }

    def plot_regression(self, df, x_col, y_col, regression):
        """Plot data and regression line."""
        X = df[[x_col]].values
        y = df[y_col].values
        plt.figure(figsize=(8, 5))
        plt.scatter(X, y, color='blue', label='Data')
        y_pred = regression['coef'][0] * X + regression['intercept']
        plt.plot(X, y_pred, color='red', label='Regression line')
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.title(f'Linear Regression: {y_col} vs {x_col}')
        plt.legend()
        plt.tight_layout()
        plt.show()

    def process(self, filename, plot=False):
        """Load, normalize, summarize, fit linear regression, and optionally plot."""
        df = self.load_data(filename)
        df_norm = self.normalize(df)
        summary = self.summary_statistics(df)
        # Linear regression: predict intensity from retention_time
        if 'retention_time' in df.columns and 'intensity' in df.columns:
            regression = self.fit_linear_regression(df, 'retention_time', 'intensity')
            if plot:
                self.plot_regression(df, 'retention_time', 'intensity', regression)
        else:
            regression = None
        return {
            'filename': filename,
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'head': df.head().to_dict(),
            'normalized_head': df_norm.head().to_dict(),
            'summary_statistics': summary,
            'linear_regression': regression
        }

if __name__ == "__main__":
    data_dir = os.path.join(os.path.dirname(__file__), '../data')
    pipeline = DataPipeline(data_dir)
    files = pipeline.list_data_files()
    print(f"Found data files: {files}")
    if files:
        info = pipeline.process(files[0], plot=True)
        print(f"Sample file info: {info}")
