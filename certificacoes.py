import streamlit as st
import pandas as pd

# Dados iniciais
distritos = [f"Distrito {i+3}" for i in range(9)]
quadras = [f"Quadra {i+9}" for i in range(30)]

# Inicializa dados no session_state
if "empresas" not in st.session_state:
    st.session_state.empresas = []
if "lotes_ocupados" not in st.session_state:
    st.session_state.lotes_ocupados = set()

# Função para adicionar empresa
def adicionar_empresa(distrito, quadra, nome_empresa, lotes_iptu, responsavel, cnpj, endereco, telefone, email):
    lotes = [lote for lote, _ in lotes_iptu]
    lotes_conflitantes = [lote for lote in lotes if lote in st.session_state.lotes_ocupados]
    if lotes_conflitantes:
        st.error(f"Lotes já associados: {', '.join(lotes_conflitantes)}")
    else:
        st.session_state.empresas.append({
            "Distrito": distrito,
            "Quadra": quadra,
            "Empresa": nome_empresa,
            "Lotes_IPTU": lotes_iptu,
            "Responsavel": responsavel,
            "CNPJ": cnpj,
            "Endereço": endereco,
            "Telefone": telefone,
            "Email": email
        })
        st.session_state.lotes_ocupados.update(lotes)
        st.success("Empresa cadastrada com sucesso!")

# Função para excluir empresa
def excluir_empresa(index):
    empresa = st.session_state.empresas.pop(index)
    lotes = [lote for lote, _ in empresa["Lotes_IPTU"]]
    st.session_state.lotes_ocupados.difference_update(lotes)
    st.rerun()

# Interface Streamlit
st.title("Agenda de Engenharia")

# Formulário para adicionar empresa
with st.form("formulario_empresa"):
    st.subheader("Cadastrar Empresa")
    distrito = st.selectbox("Distrito", distritos)
    quadra = st.selectbox("Quadra", quadras)
    nome_empresa = st.text_input("Nome da Empresa", placeholder="Digite o nome da empresa")
    responsavel = st.text_input("Nome do Responsável", placeholder="Digite o nome do responsável")
    cnpj = st.text_input("CNPJ", placeholder="Digite o CNPJ")
    endereco = st.text_input("Endereço", placeholder="Digite o endereço")
    telefone = st.text_input("Telefone", placeholder="Digite o telefone")
    email = st.text_input("E-mail", placeholder="Digite o e-mail")
    lotes = st.text_input("Lotes (exemplo: 5a, 12b, 7)", placeholder="Digite os lotes, ex: 5a, 12b, 7")
    iptu = st.text_input("IPTU (exemplo: 12345, 67890)", placeholder="Digite os números de IPTU, ex: 12345, 67890")
    submit = st.form_submit_button("Cadastrar")

    if submit:
        campos_obrigatorios = {
            "Nome da Empresa": nome_empresa,
            "Responsável": responsavel,
            "CNPJ": cnpj,
            "Endereço": endereco,
            "Telefone": telefone,
            "E-mail": email,
            "Lotes": lotes,
            "IPTU": iptu
        }

        campos_vazios = [nome for nome, valor in campos_obrigatorios.items() if not valor.strip()]
        
        if campos_vazios:
            st.error(f"Os seguintes campos são obrigatórios e não podem estar vazios: {', '.join(campos_vazios)}")
        else:
            try:
                lotes_list = [lote.strip() for lote in lotes.split(",") if lote.strip()]
                iptu_list = [iptu.strip() for iptu in iptu.split(",") if iptu.strip()]
                if len(lotes_list) != len(iptu_list):
                    st.error("O número de lotes deve corresponder ao número de IPTUs.")
                elif not all(lote.strip() for lote in lotes_list):
                    st.error("Todos os lotes devem ter um valor válido.")
                elif not all(iptu.isdigit() for iptu in iptu_list):
                    st.error("IPTU deve conter apenas números.")
                else:
                    lotes_iptu = list(zip(lotes_list, iptu_list))
                    adicionar_empresa(distrito, quadra, nome_empresa, lotes_iptu, responsavel, cnpj, endereco, telefone, email)
            except:
                st.error("Erro no formato. Use: Lotes (5a, 12b, 7) e IPTU (12345, 67890).")

# Exibir empresas registradas
st.subheader("Empresas Cadastradas")
empresas = st.session_state.empresas
if empresas:
    df = pd.DataFrame(empresas)
    for i, row in df[df["Distrito"] == distrito].iterrows():
        st.write(f"**Empresa:** {row['Empresa']} (Quadra: {row['Quadra']})")
        st.write(f"**Responsável:** {row['Responsavel']}")
        st.write(f"**CNPJ:** {row['CNPJ']}")
        st.write(f"**Endereço:** {row['Endereço']}")
        st.write(f"**Telefone:** {row['Telefone']}")
        st.write(f"**E-mail:** {row['Email']}")
        st.write("**Lotes e IPTU:**")
        for lote, iptu in row["Lotes_IPTU"]:
            st.write(f"- Lote: {lote}, IPTU: {iptu}")
        if st.button("Excluir", key=f"excluir_{i}"):
            excluir_empresa(i)

# Seção de busca com filtros estilo planilha
st.subheader("Busca de Empresas")
if empresas:
    df_flat = pd.DataFrame([
        {"Distrito": entry["Distrito"], "Quadra": entry["Quadra"], "Empresa": entry["Empresa"], 
         "Responsavel": entry["Responsavel"], "CNPJ": entry["CNPJ"], "Endereço": entry["Endereço"], 
         "Telefone": entry["Telefone"], "Email": entry["Email"], "Lote": lote, "IPTU": iptu}
        for entry in empresas
        for lote, iptu in entry["Lotes_IPTU"]
    ])

    # Filtros
    st.write("Filtrar Empresas")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        filtro_distrito = st.selectbox("Filtrar por Distrito", ["Todos"] + distritos)
    with col2:
        filtro_quadra = st.selectbox("Filtrar por Quadra", ["Todas"] + quadras)
    with col3:
        filtro_lote = st.text_input("Filtrar por Lote")
    with col4:
        filtro_iptu = st.text_input("Filtrar por IPTU")
    with col5:
        filtro_responsavel = st.text_input("Filtrar por Responsável")

    # Aplicar filtros
    df_filtrado = df_flat
    if filtro_distrito != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Distrito"] == filtro_distrito]
    if filtro_quadra != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Quadra"] == filtro_quadra]
    if filtro_lote:
        df_filtrado = df_filtrado[df_filtrado["Lote"].str.contains(filtro_lote, case=False, na=False)]
    if filtro_iptu:
        df_filtrado = df_filtrado[df_filtrado["IPTU"].str.contains(filtro_iptu, case=False, na=False)]
    if filtro_responsavel:
        df_filtrado = df_filtrado[df_filtrado["Responsavel"].str.contains(filtro_responsavel, case=False, na=False)]

    # Exibir resultados em tabela interativa
    if not df_filtrado.empty:
        st.dataframe(
            df_filtrado[["Distrito", "Quadra", "Empresa", "Responsavel", "CNPJ", "Endereço", "Telefone", "Email", "Lote", "IPTU"]],
            use_container_width=True,
            column_config={
                "Distrito": "Distrito",
                "Quadra": "Quadra",
                "Empresa": "Nome da Empresa",
                "Responsavel": "Responsável",
                "CNPJ": "CNPJ",
                "Endereço": "Endereço",
                "Telefone": "Telefone",
                "Email": "E-mail",
                "Lote": "Lote",
                "IPTU": "IPTU"
            }
        )
    else:
        st.write("Nenhum resultado encontrado.")
else:
    st.write("Nenhuma empresa cadastrada.")
