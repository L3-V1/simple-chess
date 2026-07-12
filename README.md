# Simple Chess

Jogo de xadrez em Python 3 com interface `pygame`, regras oficiais via `python-chess` e IA com tres niveis de dificuldade.

## Requisitos

- Python 3.11, 3.12 ou 3.13
- Windows com `pip` atualizado

## Observacao importante sobre Python 3.14

No Windows, `pygame==2.6.1` atualmente nao possui wheel oficial para Python 3.14. Quando isso acontece, o `pip` tenta compilar o pacote do zero, baixa dependencias SDL e pode falhar com erros como `Skipping Cython compilation`, `No "Setup" File Exists` e `SSL: CERTIFICATE_VERIFY_FAILED`.

Isso nao e um problema do codigo do jogo. E uma limitacao de compatibilidade da instalacao do `pygame` nesse ambiente.

## Instalacao

```powershell
py -3.11 -m venv .env
.env\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Se voce estiver usando Python 3.14 hoje, a forma mais segura de executar este projeto no Windows e criar o ambiente com Python 3.11.

## Execucao

```powershell
python main.py
```

## Estrutura

O codigo-fonte da aplicacao fica diretamente em `src`.

## Testes

```powershell
pytest
```
