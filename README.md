# Sales Lead Preparation

Projeto de automação em Python voltado para limpeza, validação e exportação de bases de clientes.

## 🎯 Objetivo

Padronizar e automatizar o tratamento de bases comerciais, garantindo que apenas contatos elegíveis sejam enviados para operação.

## ⚙️ Funcionalidades

- Padronização de colunas
- Limpeza de dados (e-mail e telefone)
- Validação de número móvel
- Remoção de duplicados
- Aplicação de blacklist
- Integração com lead score (Olos e Blip)
- Controle de limite de tentativas de contato
- Validação de última compra
- Regras de elegibilidade final
- Exportação das bases tratadas

## 🧠 Regras de Negócio Aplicadas

O pipeline considera:

- Número válido e móvel
- Não estar em blacklist
- Não ter sido contatado recentemente
- Não ultrapassar limite de tentativas
- Não possuir compra recente
- Não estar rodando atualmente na operação

## 🗂 Estrutura

