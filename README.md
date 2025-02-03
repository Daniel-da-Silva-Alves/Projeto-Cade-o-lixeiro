# 🚛 Cadê o Lixeiro? – Projeto Open Source

## 🌱 Sobre o Projeto  

O **"Cadê o Lixeiro?"** é uma solução inovadora para a **gestão inteligente de resíduos urbanos**. Criado no programa **InovaTech** pela primeira turma noturna de **Sistemas de Informação do CEUNI-Fametro Cachoeirinha**, o projeto tem como objetivo otimizar a coleta de lixo na cidade de **Manaus**, promovendo sustentabilidade e participação cidadã.  

Nosso aplicativo permite o **rastreamento em tempo real** dos caminhões de coleta, exibe **horários de passagem**, informa **locais de descarte consciente** e possui um sistema de **denúncias de áreas contaminadas e incêndios criminosos**. Além disso, incentiva práticas sustentáveis por meio de um **sistema de créditos e benefícios fiscais** e promove a **fiscalização colaborativa** contra descartes ilegais.  

## 🚀 Status Atual: Modularização do Front-End  

Atualmente, estamos na fase de **modularização do front-end**, com foco em:  

✅ **Componentização do código** para facilitar a manutenção e expansão.  
✅ **Refatoração da interface** para melhorar a experiência do usuário.  
✅ **Otimização da comunicação entre front-end e back-end** para melhor desempenho.  

---

## 🛠️ Funcionalidades  

- **📍 Rastreamento em tempo real** dos caminhões de coleta.  
- **🕒 Consulta de horários** de passagem dos caminhões.  
- **♻️ Locais de descarte consciente** para resíduos recicláveis e perigosos.  
- **⚠️ Denúncia de áreas contaminadas e incêndios criminosos.**  
- **🎖️ Sistema de créditos e benefícios fiscais** para incentivar boas práticas ambientais.  
- **🚯 Denúncia de descarte ilegal** para promover fiscalização colaborativa.  

---

## 🏗️ Tecnologias Utilizadas  

### 🔧 Back-End  
- **Django** – Framework web para o desenvolvimento da API.  
- **SQLite** – Banco de dados para armazenamento das informações.  

### 🎨 Front-End  
- **Bootstrap** – Framework para estilização responsiva.  
- **JavaScript (ES6+)** – Interações dinâmicas na interface.  
- **Leaflet.js** – Biblioteca para mapas e rastreamento.  
- **HTML5 e CSS3** – Estrutura e estilização da aplicação.  

---

## 🏁 Como Configurar o Projeto Localmente?  

Para testar o projeto em sua máquina, siga os passos abaixo:  

### 🔽 1. Clone o repositório  
Antes de começar, certifique-se de ter **Git**, **Python** e **pip** instalados.  

```bash
git clone https://github.com/seu-usuario/cade-o-lixeiro.git
cd cade-o-lixeiro
```

### 🏗 2. Crie e ative um ambiente virtual  
Para evitar conflitos de dependências, utilize um **ambiente virtual**:  

```bash
# No Windows (cmd)
python -m venv venv
venv\Scripts\activate

# No Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 📦 3. Instale as dependências do projeto  
```bash
pip install -r requirements.txt
```

### 🛠 4. Configure o banco de dados  
```bash
python manage.py migrate
```

### 🚀 5. Inicie o servidor localmente  
```bash
python manage.py runserver
```

Agora, acesse **http://127.0.0.1:8000/** no navegador para visualizar a aplicação!  

---

## 🤝 Como Contribuir?  

Adoraríamos contar com sua ajuda para melhorar o **"Cadê o Lixeiro?"**! Siga os passos abaixo para contribuir:  

### 📌 1. Faça um fork do repositório  
Clique no botão **Fork** no GitHub para copiar o repositório para sua conta.  

### 📌 2. Clone o repositório para sua máquina  
```bash
git clone https://github.com/seu-usuario/cade-o-lixeiro.git
cd cade-o-lixeiro
```

### 📌 3. Crie uma branch para sua contribuição  
```bash
git checkout -b minha-contribuicao
```

### 📌 4. Implemente sua melhoria e faça um commit  
```bash
git add .
git commit -m "Descrição da melhoria implementada"
```

### 📌 5. Envie para o repositório remoto  
```bash
git push origin minha-contribuicao
```

### 📌 6. Abra um Pull Request  
No GitHub, vá até a página do seu fork, clique em **"New Pull Request"** e descreva sua alteração.  

🚀 **Dica:** Se sua contribuição envolver a modularização do front-end, siga os padrões do projeto para garantir a consistência da interface!  

---
## 📬 Contato  

📧 **domhnalprofissional@gmail.com**  

Junte-se a nós para construir uma cidade mais limpa e sustentável! 🌍♻️
