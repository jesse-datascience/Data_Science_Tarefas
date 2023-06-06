import pandas as pd
from sklearn.metrics import mean_squared_error

def calculate_mse(model, df):
    """
    Calcula o erro médio quadrático (MSE) entre as previsões do modelo e os valores reais.

    Parâmetros:
        - model: O modelo treinado.
        - df: O dataframe contendo as features e o target variable.

    Retorna:
        O valor do MSE.

    """

    # Separa as variáveis de entrada (features) e a variável alvo (target variable)
    X_test = df.drop(columns=['renda'])
    y_test = df['renda']

    # Faz as previsões utilizando o modelo
    y_pred = model.predict(X_test)

    # Calcula o MSE comparando os valores previstos com os valores reais
    mse = round(mean_squared_error(y_test, y_pred),2)
    return mse
