# importa as bibliotecas
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import glob

"""
É suposto que os arquivos '.csv' serão padronizados com a seguinte nomenclatura: 

'SINASC_RO_2019_MES.csv'.

Logo, é possível generalizar quais arquivos são selecionados pelos seguintes segmentos: Estado, Ano e Mês.
"""

# função para o plot da pivot_table
def plota_pivot_table(df, value, index, func, y_label, x_label, opcao='nada'):
    
    if opcao == 'nada':
        pd.pivot_table(df, values=value, index=index, aggfunc=func).plot(figsize=[15, 5])
        
    elif opcao == 'unstack':
        pd.pivot_table(df, values=value, index=index, aggfunc=func).unstack().plot(figsize=[15, 5])
        
    elif opcao == 'sort':
        pd.pivot_table(df, values=value, index=index, aggfunc=func).sort_values(value).plot(figsize=[15, 5])
    
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    
    return None
        
# nome da pasta onde estão os arquivos
while True:
    try:
        input_dir = input('Qual o nome da pasta dos arquivos de entrada?\n> ')
        print(f'Pasta de Origem: {input_dir}')
        break
    except:
        print('Entrada inválida, tente novamente.')

# mudança até a pasta input
os.chdir(input_dir)

# captura o nome dos novos arquivos
csv_files = sorted(glob.glob('*.csv'))
print('Arquivos disponíveis:\n')
for index, file_name in enumerate(csv_files):
    if file_name.endswith('.csv'):
        print(f'{index+1}. {file_name}')

# o usuário seleciona os arquivos a serem carregados
print('Digite a abreviação do mês dos arquivos a serem carregados, separados por vírgula.' 
        'Aperte ENTER para concluir.')
selected_months = input('> ').split(',')
selected_indices = []
for index, file_name in enumerate(csv_files):
    if file_name.endswith('.csv'):
        # separa o arquivo por seus 'componentes principais'
        file_parts = file_name[:-4].split('_')
        # captura a abreviação do mês
        mes_abrev = file_parts[3]
        # verifica se o mês atual está entre os selecionados pelo usuário
        if mes_abrev.upper() in selected_months:
            selected_indices.append(index)


# limpa a tela
os.system('cls' if os.name == 'nt' else 'clear')

# carrega o .csv em um dataframe
dfs = [pd.read_csv(csv_files[i]) for i in selected_indices]
for df,csv in zip(dfs,csv_files):
    print(f"Arquivo: {csv}")
    print(f"Período: ({df['DTNASC'].min()} - {df['DTNASC'].max()}) \n")

    # salva a data máxima do dataset no formato string
    data_maxima = str(df['DTNASC'].max())
    # remove o dia da data
    data_maxima = data_maxima[:-3]
    # cria uma pasta output para as figuras
    os.makedirs('../output/figuras/'+data_maxima, exist_ok=True)
    output_dir = ('../output/figuras/'+data_maxima)
    print(f'Pasta de destino das imagens: {output_dir}.')
    
    # plota as imagens pedidas no exemplo
    plota_pivot_table(df, 'IDADEMAE', 'DTNASC', 'mean', 'média idade mãe por data', 'data nascimento')
    plt.savefig(os.path.join(output_dir, 'media idade mae por data.png'))

    plota_pivot_table(df, 'IDADEMAE', ['DTNASC', 'SEXO'], 'mean', 'media idade mae','data de nascimento','unstack')
    plt.savefig(os.path.join(output_dir, 'media idade mae por sexo.png'))

    plota_pivot_table(df, 'PESO', ['DTNASC', 'SEXO'], 'mean', 'media peso bebe','data de nascimento','unstack')
    plt.savefig(os.path.join(output_dir, 'media peso bebe por sexo.png'))

    plota_pivot_table(df, 'PESO', 'ESCMAE', 'median', 'PESO mediano','escolaridade mae','sort')
    plt.savefig(os.path.join(output_dir, 'PESO mediano por escolaridade mae.png'))

    plota_pivot_table(df, 'APGAR1', 'GESTACAO', 'mean', 'apgar1 medio','gestacao','sort')
    plt.savefig(os.path.join(output_dir, 'media apgar1 por gestacao.png'))


# volta a pasta original
os.chdir('..')
