import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(page_title="Operação CSF - WhatsApp", layout="wide")

# Função para carregar os dados
def carregar_dados(url):
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo CSV: {e}")
        return None

# Função para aplicar os filtros de data e operação
def aplicar_filtros(df, start_date, end_date, opcao):
    df_filtered = df[(df['Data de abertura'] >= pd.to_datetime(start_date)) & 
                     (df['Data de abertura'] <= pd.to_datetime(end_date))]
    df_filtered = df_filtered[df_filtered['Papel do criador'] == opcao]
    return df_filtered

# Função para traduzir os meses para português
def traduzir_mes(mes):
    meses_portugues = {
        'Jan': 'Jan', 'Feb': 'Fev', 'Mar': 'Mar', 'Apr': 'Abr',
        'May': 'Mai', 'Jun': 'Jun', 'Jul': 'Jul', 'Aug': 'Ago',
        'Sep': 'Set', 'Oct': 'Out', 'Nov': 'Nov', 'Dec': 'Dez'
    }
    return meses_portugues.get(mes, mes)

# Função para formatar as datas no gráfico e traduzir meses para português
def formatar_datas(df):
    df.index = df.index.strftime('%b %Y')
    df.index = df.index.map(traduzir_mes)
    return df

# Função para gerar o gráfico de área com o total no período
def gerar_grafico_area(df_selected, opcao, total_periodo):
    fig_area = go.Figure()

    fig_area.add_trace(go.Scatter(
        x=df_selected.index,
        y=df_selected['Volume de Atendimentos'],
        fill='tozeroy',
        mode='none',
        name=f'{opcao}',
        fillcolor='rgba(30, 144, 255, 0.5)'
    ))

    # Adicionando o total no período dentro do gráfico
    fig_area.add_annotation(
        text=f"Total de casos: {total_periodo}",
        xref="paper", yref="paper",
        x=0.5, y=0.95, showarrow=False,
        font=dict(size=16, color="white")
    )

    fig_area.update_layout(
        title=f"Volume de Atendimentos - {opcao}",
        xaxis_title="Mês",
        yaxis_title="Volume de Atendimentos",
        plot_bgcolor='rgba(0, 0, 0, 0.1)',
        paper_bgcolor='rgba(0, 0, 0, 0.1)',
        font=dict(color="white"),
        showlegend=True,
        hovermode="x",
        xaxis=dict(showgrid=True, gridcolor='gray', gridwidth=0.5),
        yaxis=dict(showgrid=True, gridcolor='gray', gridwidth=0.5)
    )

    st.plotly_chart(fig_area, use_container_width=True)

# Função para gerar o gráfico de linha comparativo
def gerar_grafico_linha(df, start_date, end_date, opcoes_operacao):
    fig_line = go.Figure()

    for operacao in opcoes_operacao:
        df_operacao = df[(df['Papel do criador'] == operacao) & 
                         (df['Data de abertura'] >= pd.to_datetime(start_date)) & 
                         (df['Data de abertura'] <= pd.to_datetime(end_date))]

        df_operacao_grouped = df_operacao.groupby(pd.Grouper(key='Data de abertura', freq='M')).size()

        if not df_operacao_grouped.empty:
            df_operacao_grouped.index = df_operacao_grouped.index.strftime('%b %Y')
            df_operacao_grouped.index = df_operacao_grouped.index.map(traduzir_mes)
            
            fig_line.add_trace(go.Scatter(
                x=df_operacao_grouped.index,
                y=df_operacao_grouped,
                mode='lines',
                name=operacao,
            ))

    fig_line.update_layout(
        title="Comparação de Volume de Atendimentos - Operações",
        xaxis_title="Mês",
        yaxis_title="Volume de Atendimentos",
        plot_bgcolor='rgba(0, 0, 0, 0.1)',
        paper_bgcolor='rgba(0, 0, 0, 0.1)',
        font=dict(color="white"),
        showlegend=True,
        hovermode="x unified",
        xaxis=dict(showgrid=True, gridcolor='gray', gridwidth=0.5),
        yaxis=dict(showgrid=True, gridcolor='gray', gridwidth=0.5)
    )

    st.plotly_chart(fig_line, use_container_width=True)

# Função para a página Wiki
def exibir_wiki():
    st.markdown("""
    <strong>Os filtros utilizados para extrair a base de dados foram os seguintes:</strong><br>
    <ul>
        <li><strong>Unidade:</strong> Igual a "CSF".</li>
        <li><strong>Papel do criador:</strong> Igual a "Assistente CSF", "Assistente CSF CM", "Assistente CSF Ajuda Quality".</li>
        <li><strong>Origem do caso:</strong> Igual a "WhatsApp".</li>
        <li><strong>Categoria:</strong> Diferente de "Atendimento".</li>
        <li><strong>Assunto:</strong> Não contém "Atendimento".</li>
        <li><strong>Assunto:</strong> Não contém "Ativo".</li>
        <li><strong>Categorização:</strong> Não contém "Ativo".</li>
        <li><strong>Motivo:</strong> Não contém "Ativo".</li>
    </ul>

    <strong>Indicadores:</strong>
    <ul>
        <li><strong>Porcentagem de Variação:</strong> É a variação entre o primeiro e o último período selecionado, indicando a diferença percentual no volume de atendimentos.</li>
        <li><strong>Menor Volume de Atendimentos:</strong> Mostra o menor volume de atendimentos registrado no período selecionado.</li>
        <li><strong>Maior Volume de Atendimentos:</strong> Indica o maior volume de atendimentos registrado no período selecionado.</li>
    </ul>
    """, unsafe_allow_html=True)

# Função para a página de download
def exibir_download(df):
    st.title("Download da Base de Dados")
    st.markdown("Clique no botão abaixo para baixar a base de dados usada neste dashboard:")

    csv_data = df.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="Baixar o arquivo CSV",
        data=csv_data,
        file_name="Report_WhatsApp_2023_2024.csv",
        mime="text/csv"
    )

# Main
def main():
    csv_url = "https://raw.githubusercontent.com/Brunosilva-data/Atendimento_WhatsApp/main/Report_WhatsApp_2023_2024.csv"
    df = carregar_dados(csv_url)

    if df is not None:
        df['Data de abertura'] = pd.to_datetime(df['Data de abertura'], dayfirst=True)
        data_inicial = df['Data de abertura'].min()
        data_final = df['Data de abertura'].max()
        opcoes_operacao = df['Papel do criador'].unique().tolist()

        # Criação das abas
        tab1, tab2, tab3 = st.tabs(["Principal", "Wiki", "Download"])

        with tab1:
            # Organizando as colunas com largura adequada
            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                opcao = st.selectbox("Selecione a operação que deseja analisar:", opcoes_operacao)

            with col2:
                start_date = st.date_input("Selecione a Data Inicial:", value=data_inicial, min_value=data_inicial, max_value=data_final, key='start_date', format="DD/MM/YYYY")

            with col3:
                end_date = st.date_input("Selecione a Data Final:", value=data_final, min_value=data_inicial, max_value=data_final, key='end_date', format="DD/MM/YYYY")

            # Aplicar filtros
            df_filtered = aplicar_filtros(df, start_date, end_date, opcao)
            df_grouped = df_filtered.groupby(pd.Grouper(key='Data de abertura', freq='M')).size()
            df_selected = pd.DataFrame({"Volume de Atendimentos": df_grouped})

            # Calcular as métricas
            total_atendimentos = df_filtered.shape[0]
            menor_volume = df_selected["Volume de Atendimentos"].min()
            maior_volume = df_selected["Volume de Atendimentos"].max()

            # Cálculo da porcentagem de variação entre o primeiro e o último período
            primeiro_periodo = df_selected["Volume de Atendimentos"].iloc[0] if not df_selected.empty else 0
            ultimo_periodo = df_selected["Volume de Atendimentos"].iloc[-1] if not df_selected.empty else 0
            variacao_porcentual = ((ultimo_periodo - primeiro_periodo) / primeiro_periodo * 100) if primeiro_periodo != 0 else 0
            tendencia = "Subiu" if variacao_porcentual > 0 else "Caiu" if variacao_porcentual < 0 else "Estável"

            # Exibir as métricas em linha
            col4, col5, col6 = st.columns(3)
            col4.metric(label="Porcentagem de Variação", value=f"{tendencia}: {variacao_porcentual:.2f}%")
            col5.metric(label="Menor Volume de Atendimentos", value=menor_volume)
            col6.metric(label="Maior Volume de Atendimentos", value=maior_volume)

            # Aplicar tradução de meses
            df_selected = formatar_datas(df_selected)

            # Gerar gráficos
            if not df_selected.empty:
                gerar_grafico_area(df_selected, opcao, total_atendimentos)
                gerar_grafico_linha(df, start_date, end_date, opcoes_operacao)

        with tab2:
            exibir_wiki()

        with tab3:
            exibir_download(df)

    # Código para esconder botões padrão do Streamlit
    esconder_menu = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
    """
    st.markdown(esconder_menu, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
