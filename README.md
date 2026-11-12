# Gerador Dinâmico de DataBooks (Dynamic PDF Dossier Builder)

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![PyQt6](https://img.shields.io/badge/PyQt6-GUI-green?style=for-the-badge&logo=qt)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red?style=for-the-badge&logo=sqlalchemy)
![PyMuPDF](https://img.shields.io/badge/PyMuPDF-PDF_Processing-orange?style=for-the-badge)

Uma aplicação desktop corporativa desenvolvida em Python para automatizar a compilação, formatação e auditoria de **DataBooks** (dossiês técnicos e relatórios de controle de qualidade). 

O sistema substitui o trabalho manual de mesclagem de dezenas de PDFs por um fluxo automatizado. Através de um sistema de autenticação, a aplicação adapta a sua interface (Taxonomia Dinâmica) para exibir apenas os documentos exigidos pelo perfil de cada utilizador, garantindo a conformidade dos relatórios gerados.

## Funcionalidades Principais
* **Renderização Dinâmica de UI por Perfil (Role-Based UI):** A interface adapta-se ao operador, construindo a árvore de documentos obrigatórios e opcionais dinamicamente.
* **Processamento Avançado de PDF (`PyMuPDF`):** Mesclagem de documentos em alta velocidade e injeção automática de páginas em branco (algoritmo de paridade) para garantir a correta impressão frente e verso das divisórias.
* **Geração Inteligente de Capas:** Criação de capas automáticas utilizando coordenadas de PDF Canvas, com suporte a detecção de plural/singular para múltiplos registros de formulários.
* **Gestão de Estado e Persistência (`SQLAlchemy`):** Salvamento local de rascunhos (Drafts) e logging de métricas de uso em banco de dados SQLite/MySQL.
* **Design Moderno e Responsivo:** Interface construída com PyQt6 e Fluent UI para uma experiência limpa e profissional.

## Stack 
* **Interface Gráfica (GUI):** `PyQt6` + `PyQt6-Fluent-Widgets`
* **Manipulação de PDF:** `PyMuPDF` (fitz)
* **Banco de Dados & ORM:** `SQLAlchemy` (Configurado para SQLite no ambiente de desenvolvimento)

## Como Executar o Projeto Localmente

1. Clone o repositório:
```bash
git clone [https://github.com/SEU_USUARIO/databook-generator.git](https://github.com/SEU_USUARIO/databook-generator.git)
cd databook-generator