# 📊 Sales Lead Preparation

Projeto de automação em Python voltado para limpeza, validação e exportação de bases de clientes para operação comercial.

O sistema aplica regras de negócio para garantir que apenas contatos elegíveis sejam enviados para a equipe de vendas, aumentando eficiência operacional e reduzindo retrabalho.

---

## 🎯 Objetivo

Automatizar o tratamento de bases comerciais aplicando:

- Padronização de dados
- Validação de telefone móvel
- Remoção de duplicidades
- Aplicação de blacklist
- Controle de tentativas de contato
- Validação de última compra
- Integração com lead score (Olos e Blip)
- Regras finais de elegibilidade

---

## ⚙️ Funcionalidades

- 📌 Padronização de colunas (DePara)
- 📧 Limpeza e normalização de e-mails
- 📱 Tratamento e validação de telefones
- 🔁 Remoção de duplicados
- 🚫 Aplicação de blacklist
- 📞 Controle de limite de tentativas de contato
- 🧠 Integração com lead scoring
- 🛒 Verificação de última compra
- 📤 Exportação das bases tratadas em Excel

---

## 🧠 Regras de Negócio Aplicadas

O pipeline considera elegível para contato apenas registros que:

- Possuam telefone móvel válido (11 dígitos e terceiro número = 9)
- Não estejam na blacklist
- Não estejam rodando atualmente na operação
- Não tenham ultrapassado o limite de tentativas
- Não tenham compra recente
- Não estejam bloqueados por lead score
- Estejam fora do período mínimo de retorno (Olos / Blip)

---

## 🗂 Estrutura do Projeto

```
sales-lead-preparation/
│
├── aut_limpador.py      # Script principal do pipeline
├── README.md            # Documentação do projeto
```

---

## 🚀 Tecnologias Utilizadas

- Python 3.x
- Pandas
- NumPy
- SQLAlchemy
- PostgreSQL
- OpenPyXL

---

## 🔒 Segurança

As queries SQL presentes no repositório são versões dummy (`WHERE 1=0`)  
utilizadas apenas para manter a estrutura das colunas.

A conexão real com banco utiliza variável de ambiente:

```
DATABASE_URL
```

Nenhuma credencial sensível está exposta no repositório.

---

## 🛠 Configuração (Opcional - Conexão com Banco)

Caso queira executar com banco real:

1. Defina a variável de ambiente:

```
export DATABASE_URL="postgresql+psycopg2://usuario:senha@host:porta/database"
```

2. Execute o script normalmente.

Se a variável não estiver definida, o sistema rodará em modo seguro (DataFrames vazios).

---

## 📦 Instalação

Clone o repositório:

```
git clone https://github.com/MrW3ll/sales-lead-preparation.git
```

Instale as dependências:

```
pip install pandas numpy sqlalchemy psycopg2 openpyxl
```

---

## 📌 Próximos Passos (Evolução do Projeto)

- Estruturação em pasta `/src`
- Criação de `requirements.txt`
- Modularização das regras de negócio
- Implementação de logs estruturados
- Automatização via agendamento (cron / scheduler)

---

## 👤 Autor

Wellington Rodrigues  
Analista focado em automação, dados e eficiência operacional.

---

