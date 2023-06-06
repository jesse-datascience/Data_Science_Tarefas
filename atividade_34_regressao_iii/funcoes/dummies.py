import pandas as pd
"""
Função para tornas as variáveis do dataframe dummies.
Ainda retorna as variáveis mais frequentes para ordenação de acordo com a 
casela do modelo patsy,
"""

def dummies(df, colunas):

    # remove a coluna data_ref e index
    df = df.drop(['data_ref', 'index'], axis=1)
        
     # Obtém as variáveis dummy do DataFrame
    df_dummies = pd.get_dummies(data=df, columns=colunas, drop_first=True)

    # renomeia as colunas para melhor vizualização
    df_dummies = df_dummies.rename(columns=lambda x: x.replace('á', 'a')
                                   .replace('ç', 'c')
                                   .replace('ã', 'a')
                                   .replace('ó', 'o')
                                   .replace('ú', 'u')
                                   .replace(' ', '_'))
    # Calcula as frequências das colunas
    column_frequencies = df_dummies.sum().sort_values(ascending=False)

    # Reordena as colunas do DataFrame com base nas frequências
    df_dummies = df_dummies[column_frequencies.index]

    # Retorna o DataFrame com as colunas ordenadas pela frequência
    return df_dummies