# importanto as bibliotecas
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import seaborn as sns
import statsmodels.api as sm
import statsmodels.formula.api as smf
import patsy
from sklearn.model_selection import train_test_split

# configura a pagina do navegador
st.set_page_config(page_title='Análise de Crédito - Ebanker', page_icon="💰")
st.title('Análise de Crédito')

# Carregamento do banco de dados
arquivo = 'previsao_de_renda_treino.feather'

# função cache_data torna mais eficiente o carregamento
@st.cache_data()
# Carrega a base de dados previamente tratada
def load_data():
    df = pd.read_feather(arquivo)
    # fazendo uma copia do df original, por seguranca
    data = df.copy()

    return data

# carregando os dados
try:
    with st.spinner('Carregando base de dados'):   
        data = load_data()
except:
    st.error('Dados carregados incorretamente. Verficar.')

# Filtros 
tipo_renda_filter = st.sidebar.multiselect("Tipo de Renda", 
                                           data["tipo_renda"].unique(),
                                           default=data.tipo_renda.unique())

educacao_filter = st.sidebar.multiselect("Escolaridade", 
                                         data["educacao"].unique(),
                                         default=data.educacao.unique())

tipo_residencia_filter = st.sidebar.multiselect("Residência",
                                                data["tipo_residencia"].unique(),
                                                default=data["tipo_residencia"].unique())
idade_filter = st.sidebar.slider("Faixa Etária", 
                                 int(data["idade"].min()), 
                                 int(data["idade"].max()),
                                 (int(data["idade"].min()), int(data["idade"].max())))

estado_civil_filter = st.sidebar.multiselect("Estado Civil",
                                             data["estado_civil"].unique(),
                                             default=data["estado_civil"].unique())

# Aplicando os filtros
@st.cache_data()
def data_filter():
    data_filter = data[
        (data["tipo_renda"].isin(tipo_renda_filter)) &
        (data["educacao"].isin(educacao_filter)) &
        (data["tipo_residencia"].isin(tipo_residencia_filter)) &
        (data["idade"].between(idade_filter[0], idade_filter[1])) &
        (data["estado_civil"].isin(estado_civil_filter))
    ]
    return data_filter

"""
Os dados só aparecem após apertar botão de confirmação.
Por isso o resto do código está condicionado ao botão.
Ajeitar para rodar uma vez total. 
"""
if st.sidebar.button("Confirmar", use_container_width=True):
    data_filter = data_filter()
    
    # informacoes medias do bando de dados filtrado
    num_clientes = data_filter.shape[0]
    media_idade = data_filter.idade.mean().round(1)
    media_veiculo = data_filter.posse_de_veiculo.mean().round(2)
    media_imovel = data_filter.posse_de_imovel.mean().round(2)
    media_renda = data_filter.renda.mean().round(2)

    # secão dos clientes
    st.subheader("Ebankeners:")

    # definição das columnas
    num_cliente_col, media_idade_col, media_renda_col, media_imovel_col, media_veiculo_col = st.columns(5)

    # lembrando que imovel e veiculos são bool, logo aparecerá a media de Trues
    with num_cliente_col:
        st.metric("Clientes", num_clientes, help="Número Total de Clientes")
    with media_renda_col:
        st.metric("Renda (R$)", media_renda, help="Renda média")
    with media_idade_col:
        st.metric("Idade Média", media_idade)
    with media_veiculo_col:
        st.metric("Veículo (%)", media_veiculo, help="Posse de veículo")
    with media_imovel_col:
        st.metric("Imóvel (%)", media_imovel, help="Posse de imóvel")

    # colunas para os graficos
    col1, col2 = st.columns(2)

    fig_hist = px.histogram(data_filter, x="idade", nbins=10,
                       title='Idade',
                       opacity=0.8,
                       color=data_filter.sexo)
    fig_hist.update_layout(height=400, width=350)
    col1.plotly_chart(fig_hist)

   
    fig_pie = px.pie(data_filter, names="tipo_renda",
                    title="Tipo de Renda")
    fig_pie.update_layout(height=400, width=400)
    col2.plotly_chart(fig_pie)

    # titulo da seção Bens (imoveis e veiculos)
    st.subheader("Bens")
    
    # cria tabs para as categorias
    possui_imovel, possui_veiculo = st.tabs(["Imóvel", "Veículo"])
    
    with possui_imovel:
        col1_imovel, col2_imovel = st.columns(2)

        """
        Pelos dados previamente observados, mais de 6 pessoas por resisdência são poucas
        e não aparecem nos gráficos.
        """
        fig_hist_imovel = px.histogram(data_filter, x="qt_pessoas_residencia",
                       title='Pessoas por residência',
                       opacity=0.8,
                       color="posse_de_imovel",
                       range_x=(0,6))
        fig_hist_imovel.update_layout(height=400, width=350)
        col1_imovel.plotly_chart(fig_hist_imovel)

        fig_pie_imovel = px.pie(data_filter, names="tipo_residencia",
                    title="Tipo de Renda")
        fig_pie_imovel.update_layout(height=400, width=400)
        col2_imovel.plotly_chart(fig_pie_imovel)

    with possui_veiculo:
        st.header("Teste Veiculo")

"""
Inicio do modelo de regressao linear.
"""
st.subheader("Regressão Linear")

# definição do modelo de regressão
@st.cache_resource()    # usado para guardar em cache um modelo de ML
def modelo_ols(formula: str, df: pd.DataFrame) -> None:

    
    # inicia o patsy dmatrices
    y, X = patsy.dmatrices(formula, data=data)
    # aqui, separando o modelo entre teste e validação em 20%/80%
    X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.20, random_state=42)
    
    # transforma em pd.Dataframe, afim de calcular o resíduo
    X_valid = pd.DataFrame(X_valid, columns=X.design_info.column_names)
    y_valid = pd.DataFrame(y_valid, columns=['renda'])

    model_ols = sm.OLS(y_train, X_train)
    result_ols = model_ols.fit()
    print(result_ols.summary())
    
    # calculando os valores previstos
    y_pred = result_ols.predict(X_valid)

    # adicionando a coluna np.log(renda)
    y_valid['log_renda'] = np.log(y_valid['renda'])
    y_res = y_valid['renda'] - y_valid['log_renda']

    # plotando o grafico para os residuos
    sns.residplot(x=y_pred, y=y_res, color='g')
    plt.title('Gráfico de Resíduos')
    plt.xlabel('y residual')
    plt.ylabel('y validação')
    plt.show()
    
    return result_ols

"""
Baseado em análises préivas, será apenas analisado as variáveis explicitados na formula definida a seguir. 
Ver atividade do módulo 13 para maiores informações.

O modelo OLS (patsy) só pode ser iniciado após a criação de variáveis dummies. Com isso, a função abaixo é criada
exclusivamente para isso.
"""
@st.cache_data()
def dummies_frequencia(columns, df=data):


    df_dummies = pd.get_dummies(data=df, columns=columns, drop_first=True)

    # conta a frequencia das colunas para usar de casela
    column_frequencies = {}
    for col in df_dummies.columns:
        counts = df_dummies[col].value_counts()
        column_frequencies[col] = counts.iloc[0] if not counts.empty else 0

    sorted_columns = sorted(column_frequencies, key=column_frequencies.get, reverse=True)
    df_dummies = df_dummies[sorted_columns]

    return df_dummies

df_dummies = dummies_frequencia(columns=['tipo_renda', 'educacao', 'estado_civil', 'tipo_residencia',
                                        'posse_de_veiculo', 'posse_de_imovel'])

# formula para regressão linear
formula = ('np.log(renda) ~'
        '+ posse_de_imovel_True + qtd_filhos'
        '+ posse_de_veiculo_True'
        '+ qt_pessoas_residencia + idade'
        '+ tempo_emprego -1')

# inicia o modelo OLS
modelo = modelo_ols(formula, df_dummies)

st.write("R² ajustado: modelo.rsquared_adj")




