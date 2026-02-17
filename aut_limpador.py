### IMPORTAÇÃO DE BIBLIOTECAS ####

import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from pathlib import Path
import time
import unicodedata
import warnings

warnings.filterwarnings('ignore', category=FutureWarning)

# =========================================================
# CONEXÃO
# Use variável de ambiente DATABASE_URL para conectar.
# Ex: postgresql+psycopg2://user:pass@host:5432/db
# =========================================================
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL) if DATABASE_URL else None


### FUNÇÕES E DEPARA ####

DePara_colunas = {
    'base_inativa':{
        'email':'email',
        'phone_1':'phone',
        'product':'program',
        'area':'area',
        'copy':'copy',
        'type':'type'
    },

    'base_ativa':{
        'email':'email',
        'phone':'phone',
        'program':'program',
        'area':'area',
        'copy':'copy'
    },

    'base_carrinho':{
        'Area':'area',
        'email':'email',
        'celular':'phone',
        'programa':'program',
        'copy':'copy'
    },

    'base_hubspot':{
        # deixe vazio por enquanto
    }
}

def executar_qry(query: str, nome_df: str) -> pd.DataFrame:
    """Executa query se houver engine; caso contrário, retorna DF vazio."""
    inicio = time.time()

    if engine is None:
        print(f'⚠️ Sem DATABASE_URL. Retornando DF vazio: {nome_df}')
        return pd.DataFrame()

    try:
        print(f'Executando: {nome_df}...')
        df = pd.read_sql(text(query), engine)

        tempo_total = time.time() - inicio
        minutos = int(tempo_total // 60)
        segundos = tempo_total % 60
        tempo = f'{minutos}min {segundos:.1f}s' if minutos > 0 else f'{segundos:.2f}s'

        print(f'✅ {nome_df}: {len(df)} linhas | ⏱️{tempo}')
        return df

    except Exception as e:
        print(f'❌ Erro em {nome_df} após {time.time()-inicio:.2f}s: {e}')
        return pd.DataFrame()

def filtrar_base(df, area=None, program=None, type=None):
    resultado = df.copy()

    if area is not None:
        areas = area if isinstance(area, list) else [area]
        resultado = resultado[
            resultado['area'].astype(str).str.upper().isin([a.upper() for a in areas])
        ]

    if type is not None:
        # ✅ CORRIGIDO: você estava usando "area" no lugar de "type"
        types = type if isinstance(type, list) else [type]
        resultado = resultado[
            resultado['type'].astype(str).str.upper().isin([t.upper() for t in types])
        ]

    if program is not None:
        resultado = resultado[
            resultado['program'].astype(str).str.contains(program, case=False, na=False)
        ]

    return resultado.reset_index(drop=True)

def padronizar(df, mapa_colunas):
    df_padrao = df.rename(columns=mapa_colunas)
    return df_padrao[list(mapa_colunas.values())]

def limp_min(df):
    resultado = df.copy()

    resultado = resultado[
        resultado['email'].notna() &
        resultado['phone'].notna()
    ]

    resultado = resultado[
        (resultado['email'].astype(str).str.strip() != '') &
        (resultado['phone'].astype(str).str.strip() != '')
    ]

    resultado['copy'] = resultado['email'].astype(str) + ';' + resultado['phone'].astype(str)
    return resultado.reset_index(drop=True)

def dedup_basica(df, key='copy'):
    return (
        df.drop_duplicates(subset=key, keep='first')
          .reset_index(drop=True)
    )

def remover_duplicadas(df, key='copy'):
    return (
        df.sort_values(by=key)
          .drop_duplicates(subset=key, keep='first')
          .reset_index(drop=True)
    )

def padrao_telefone(df):
    resultado = df.copy()

    resultado['email'] = resultado['email'].astype(str).str.strip().str.lower()
    resultado['phone'] = resultado['phone'].astype(str).str.replace(r'\D', '', regex=True)

    resultado['copy'] = resultado['email'] + ';' + resultado['phone']
    return resultado.reset_index(drop=True)

def val_n_movel(df):
    resultado = df.copy()

    resultado['is_movel'] = (
        resultado['phone'].astype(str).str.len().eq(11) &
        resultado['phone'].astype(str).str[2].eq('9')
    )
    return resultado

def aplicar_blacklist(df, df_blacklist):
    resultado = df.copy()
    blacklist = df_blacklist.copy()

    resultado['phone'] = resultado['phone'].astype(str).str.replace(r'\D', '', regex=True)
    blacklist['telefone'] = blacklist['telefone'].astype(str).str.replace(r'\D', '', regex=True)

    resultado['Na_blacklist'] = resultado['phone'].isin(blacklist['telefone'])
    return resultado

def rod_atual(df, df_rod_atualmente):
    resultado = df.copy()
    df_rod_atual = df_rod_atualmente.copy()

    resultado['phone'] = resultado['phone'].astype(str).str.replace(r'\D', '', regex=True)
    df_rod_atual['fone_1'] = df_rod_atual['fone_1'].astype(str).str.replace(r'\D', '', regex=True)

    resultado['rod_atual'] = resultado['phone'].isin(df_rod_atual['fone_1'])
    return resultado

def score_olos(df, ls_olos):
    resultado = df.copy()
    leadscore_olos = ls_olos.copy()

    resultado['phone'] = resultado['phone'].astype(str).str.replace(r'\D', '', regex=True)
    leadscore_olos['phone_number'] = leadscore_olos['phone_number'].astype(str).str.replace(r'\D', '', regex=True)

    resultado['No_leadScore_Olos'] = resultado['phone'].isin(leadscore_olos['phone_number'])
    return resultado

def score_blip(df, ls_blip):
    resultado = df.copy()
    leadscore_blip = ls_blip.copy()

    resultado['phone'] = resultado['phone'].astype(str).str.replace(r'\D', '', regex=True)
    leadscore_blip['phone_number'] = leadscore_blip['phone_number'].astype(str).str.replace(r'\D', '', regex=True)

    resultado['No_leadScore_blip'] = resultado['phone'].isin(leadscore_blip['phone_number'])
    return resultado

def qtdCalls(df, df_qtd, limite=10):
    resultado = df.copy()
    qtd = df_qtd.copy()

    resultado['phone'] = resultado['phone'].astype(str).str.replace(r'\D', '', regex=True)
    qtd['phone_number'] = qtd['phone_number'].astype(str).str.replace(r'\D', '', regex=True)

    resultado = resultado.merge(
        qtd[['phone_number', 'TOTAL_CALLS']],
        left_on='phone',
        right_on='phone_number',
        how='left'
    )

    resultado['acima_limite'] = (resultado['TOTAL_CALLS'].fillna(0).astype(int) > limite)
    resultado = resultado.drop(columns=['phone_number', 'TOTAL_CALLS'])
    return resultado

def ultima_compra(df, df_sispag):
    resultado = df.copy()
    sispag = df_sispag.copy()

    resultado['phone'] = resultado['phone'].astype(str).str.replace(r'\D', '', regex=True)
    sispag['celular'] = sispag['celular'].astype(str).str.replace(r'\D', '', regex=True)

    resultado['ultima_compra'] = resultado['phone'].isin(sispag['celular'])
    return resultado

def last_conct_olos(df, olos_ultimo_contato):
    resultado = df.copy()
    tab_olos = olos_ultimo_contato.copy()

    # se vier vazio, já garante as colunas mínimas
    for col in ['data_olos', 'retorno_em_dias', 'status_retorno', 'phone']:
        if col not in tab_olos.columns:
            tab_olos[col] = pd.Series(dtype='object')

    tab_olos['data_olos'] = pd.to_datetime(tab_olos['data_olos'], errors='coerce')
    tab_olos['dias_desde_tab'] = (pd.Timestamp.today() - tab_olos['data_olos']).dt.days
    tab_olos['dias_desde_tab'] = tab_olos['dias_desde_tab'].fillna(0)
    tab_olos['retorno_em_dias'] = pd.to_numeric(tab_olos['retorno_em_dias'], errors='coerce').fillna(0)

    tab_olos['last_conct_olos'] = (
        (tab_olos['dias_desde_tab'] > tab_olos['retorno_em_dias']) &
        (tab_olos['status_retorno'] == 'retornar')
    )

    resultado['phone'] = resultado['phone'].astype(str).str.replace(r'\D', '', regex=True)
    tab_olos['phone'] = tab_olos['phone'].astype(str).str.replace(r'\D', '', regex=True).str[-11:]

    resultado = resultado.merge(tab_olos[['phone', 'last_conct_olos']], on='phone', how='left')
    resultado['last_conct_olos'] = resultado['last_conct_olos'].fillna(True)
    return resultado

def last_conct_blip(df, blip_ultimo_contato):
    resultado = df.copy(deep=True)
    tab_blip = blip_ultimo_contato.copy(deep=True)

    # se vier vazio, já garante colunas mínimas
    for col in ['data_blip', 'retorno_em_dias', 'status_retorno', 'contact_id_trimmed']:
        if col not in tab_blip.columns:
            tab_blip[col] = pd.Series(dtype='object')

    tab_blip['data_blip'] = pd.to_datetime(tab_blip['data_blip'], errors='coerce')
    tab_blip['dias_desde_tab'] = (pd.Timestamp.today() - tab_blip['data_blip']).dt.days
    tab_blip['dias_desde_tab'] = tab_blip['dias_desde_tab'].fillna(0)
    tab_blip['retorno_em_dias'] = pd.to_numeric(tab_blip['retorno_em_dias'], errors='coerce').fillna(0)

    tab_blip['last_conct_blip'] = (
        (tab_blip['dias_desde_tab'] > tab_blip['retorno_em_dias']) &
        (tab_blip['status_retorno'] == 'retornar')
    )

    resultado['phone'] = resultado['phone'].astype(str).str.replace(r'\D', '', regex=True)
    tab_blip['contact_id_trimmed'] = tab_blip['contact_id_trimmed'].astype(str).str.replace(r'\D', '', regex=True)

    resultado = resultado.merge(
        tab_blip[['contact_id_trimmed', 'last_conct_blip']],
        left_on='phone',
        right_on='contact_id_trimmed',
        how='left'
    )
    resultado['last_conct_blip'] = resultado['last_conct_blip'].fillna(True)
    return resultado

def filtro_final(df):
    resultado = df.copy()

    resultado['manter_contato'] = (
        resultado['is_movel'] &
        ~resultado.get('Na_blacklist', False) &
        ~resultado.get('No_leadScore_Olos', False) &
        ~resultado.get('No_leadScore_blip', False) &
        ~resultado.get('acima_limite', False) &
        ~resultado.get('ultima_compra', False) &
        ~resultado.get('rod_atual', False) &
        resultado.get('last_conct_olos', True) &
        resultado.get('last_conct_blip', True)
    )

    resultado = resultado[resultado['manter_contato']].reset_index(drop=True)

    cols_drop = [
        'is_movel','Na_blacklist','No_leadScore_Olos','No_leadScore_blip',
        'acima_limite','ultima_compra','last_conct_olos','last_conct_blip',
        'manter_contato','rod_atual','contact_id_trimmed'
    ]
    resultado = resultado.drop(columns=[c for c in cols_drop if c in resultado.columns], errors='ignore')
    return resultado

def padrao_e_filtro(
    df,
    mapa_colunas,
    df_sispag,
    df_rod_atual=None,
    area=None,
    type=None,
    program=None,
    df_blacklist=None,
    leadScoreOlos=None,
    leadScoreBlip=None,
    qtdcalls=None,
    limite=10,
    olos_ultimo_contato=None,
    blip_ultimo_contato=None
):
    try:
        df = padronizar(df, mapa_colunas)
        df = dedup_basica(df, key='copy')
        df = filtrar_base(df, area=area, program=program, type=type)
        df = limp_min(df)
        df = padrao_telefone(df)
        df = val_n_movel(df)

        if df_rod_atual is not None:
            df = rod_atual(df, df_rod_atualmente=df_rod_atual)
        if df_blacklist is not None:
            df = aplicar_blacklist(df, df_blacklist)
        if leadScoreOlos is not None:
            df = score_olos(df, leadScoreOlos)
        if leadScoreBlip is not None:
            df = score_blip(df, leadScoreBlip)
        if qtdcalls is not None:
            df = qtdCalls(df, qtdcalls, limite=limite)

        df = remover_duplicadas(df, key='copy')
        df = ultima_compra(df, df_sispag)

        if olos_ultimo_contato is None:
            olos_ultimo_contato = pd.DataFrame(columns=['phone','data_olos','retorno_em_dias','status_retorno'])
        if blip_ultimo_contato is None:
            blip_ultimo_contato = pd.DataFrame(columns=['contact_id_trimmed','data_blip','retorno_em_dias','status_retorno'])

        df = last_conct_olos(df, olos_ultimo_contato=olos_ultimo_contato)
        df = last_conct_blip(df, blip_ultimo_contato=blip_ultimo_contato)
        df = filtro_final(df)

        return df.reset_index(drop=True)
    except Exception as e:
        return f'Erro ao processar: {e}'


# =========================================================
# QUERIES DUMMY (válidas) - definem colunas e retornam 0 linhas
# =========================================================
qry_sispag = """
SELECT
    NULL::text  AS nome_ies,
    NULL::text  AS celular,
    NULL::text  AS tipoproduto,
    NULL::date  AS dt,
    NULL::text  AS id,
    NULL::text  AS user_id,
    NULL::text  AS name,
    NULL::text  AS email,
    NULL::text  AS city,
    NULL::text  AS state,
    NULL::text  AS product_id,
    NULL::text  AS program,
    NULL::text  AS area,
    NULL::numeric AS value,
    NULL::text  AS payment_type,
    NULL::text  AS channel_id,
    NULL::text  AS channel
WHERE 1=0;
"""

qtd_calls = """
SELECT
    NULL::text AS phone_number,
    NULL::int  AS TOTAL_CALLS
WHERE 1=0;
"""

tab_olos = """
SELECT
    NULL::text AS phone,
    NULL::text AS customer_id,
    NULL::text AS disposition_nivel_1,
    NULL::text AS data_olos,
    NULL::int  AS retorno_em_dias,
    NULL::text AS status_retorno
WHERE 1=0;
"""

tab_blip = """
SELECT
    NULL::text AS contact_id_trimmed,
    NULL::date AS data_blip,
    NULL::text AS tags,
    NULL::int  AS retorno_em_dias,
    NULL::text AS status_retorno
WHERE 1=0;
"""

lead_score_olos = """
SELECT
    NULL::text AS phone_number
WHERE 1=0;
"""

lead_score_blip = """
SELECT
    NULL::text AS phone_number
WHERE 1=0;
"""

queries = {
    'sispag': qry_sispag,
    'qtd_calls': qtd_calls,
    'tab_olos': tab_olos,
    'tab_blip': tab_blip,
    'qry_leadscore_olos': lead_score_olos,
    'qry_leadscore_blip': lead_score_blip
}

dfs = {nome: executar_qry(qry, nome) for nome, qry in queries.items()}


df_blacklist = pd.DataFrame(columns=["telefone"])
df_rod_atual = pd.DataFrame(columns=["fone_1"])


# =========================================================
# BUILDER (opcional) - lê ./data/base_builder_V2.xlsm
# Se não existir, cria DFs vazios.
# =========================================================
Caminho_builder = Path("./data/base_builder_V2.xlsm")
sheets_builder = ['base_carrinho', 'base_inativa', 'base_ATIVA']

if Caminho_builder.exists():
    bases = {}
    for sheet in sheets_builder:
        df = pd.read_excel(Caminho_builder, sheet_name=sheet, dtype=str, engine='openpyxl')
        bases[sheet] = df
        print(f'Sheet "{sheet}" carregada: {df.shape}')

    df_inativa = bases['base_inativa']
    df_ativa = bases['base_ATIVA']
    df_carrinho = bases['base_carrinho']
else:
    print("⚠️ Builder não encontrado em ./data/. Criando DFs vazios.")
    df_inativa = pd.DataFrame(columns=["email","phone_1","product","area","copy","type"])
    df_ativa = pd.DataFrame(columns=["email","phone","program","area","copy"])
    df_carrinho = pd.DataFrame(columns=["Area","email","celular","programa","copy"])


# =========================================================
# TRATAMENTO EXTRA CARRINHO (Area por programa)
# Só roda se tiver coluna 'programa'
# =========================================================
def normalizar(txt):
    return (
        unicodedata.normalize('NFKD', str(txt))
        .encode('ascii', errors='ignore')
        .decode('utf-8')
        .upper()
    )

if 'programa' in df_carrinho.columns:
    p = df_carrinho['programa'].astype(str).apply(normalizar)

    condicoes = [
        p.str.contains(r'PRONEUROPSI|PROAPSI|PROCOGNITIVA|PROPSICO'),
        p.str.contains(r'PROPSICOMED|PROPSIQ'),
        p.str.contains(r'PROEMPED|PRONEUROPED|PROPED|PRORN|PROTIPED'),
        p.str.contains(r'PROENF/APS|PROENF/SMN|PROENF/TI|PROENF-URG'),
        p.str.contains(r'PROFISIO/TRAUMA|PROFISIO/TO\+|PROFISIO/TIA|PROFISIO/PED|PROFISIO/NEURO|PROFISIO/ESP|PROFISIO/CARDIO'),
        p.str.contains(r'PROPALIATIVO'),
        p.str.contains(r'PRONUTRI'),
        p.str.contains(r'PROMEVET'),
        p.str.contains(r'PROACI|PROAGO|PROAMI|PROANESTESIA|PROATO|PROCARDIOL|PROCLIM|PROENDOCRINO|PROENDOGASTRO|PROGER|PROMEDE|PROMEF|PRONEURO|PRO-ORL|PRORAD|PROTERAPEUTICA|PROURGEM')
    ]

    valores = [
        'Psicologia','Psiquiatria','Pediatria','Enfermagem','Fisioterapia',
        'Multi','Nutrição','Veterinária','Medicina'
    ]

    df_carrinho['Area'] = np.select(condicoes, valores, default='Não identificado')


# =========================================================
# EXEMPLOS DE GERAÇÃO DE BASES 
# =========================================================
psicologia_ativa = padrao_e_filtro(
    df_ativa,
    DePara_colunas['base_ativa'],
    dfs.get('sispag', pd.DataFrame(columns=['celular'])),
    area='Saúde Mental',
    df_rod_atual=df_rod_atual,
    df_blacklist=df_blacklist,
    leadScoreOlos=dfs.get('qry_leadscore_olos', pd.DataFrame(columns=['phone_number'])),
    leadScoreBlip=dfs.get('qry_leadscore_blip', pd.DataFrame(columns=['phone_number'])),
    qtdcalls=dfs.get('qtd_calls', pd.DataFrame(columns=['phone_number','TOTAL_CALLS'])),
    olos_ultimo_contato=dfs.get('tab_olos', pd.DataFrame(columns=['phone','data_olos','retorno_em_dias','status_retorno'])),
    blip_ultimo_contato=dfs.get('tab_blip', pd.DataFrame(columns=['contact_id_trimmed','data_blip','retorno_em_dias','status_retorno']))
)

# Repete o mesmo padrão para as demais... 


# =========================================================
# EXPORTAÇÃO BASES  
# =========================================================
def exportar_bases(bases_dict, pasta_saida=Path("./output")):
    pasta_saida.mkdir(parents=True, exist_ok=True)

    for nome_base, df_base in bases_dict.items():
        if isinstance(df_base, pd.DataFrame):
            caminho = pasta_saida / f"{nome_base}.xlsx"
            df_base.to_excel(caminho, index=False)
            print(f"✅ Exportado: {nome_base} -> {caminho}")
        else:
            print(f"⚠️ Ignorado (não é DataFrame): {nome_base}")


# Exemplo de dicionário final (você pode completar com todas as bases)
bases = {
    "psicologia_ativa": psicologia_ativa,
}

# exportar_bases(bases)
