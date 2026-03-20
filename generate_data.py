import os

import pandas as pd
from sklearn.datasets import load_iris


def generate_test_data():
    os.makedirs("data", exist_ok=True)
    iris = load_iris()

    # On définit explicitement les noms avec underscores
    clean_columns = ["sepal_length", "sepal_width", "petal_length", "petal_width"]
    df = pd.DataFrame(iris.data, columns=clean_columns)

    # On sauvegarde les 20 premières lignes pour le test
    df_test = df.sample(20, random_state=42)
    df_test.to_csv("data/iris_test.csv", index=False)


if __name__ == "__main__":
    generate_test_data()
