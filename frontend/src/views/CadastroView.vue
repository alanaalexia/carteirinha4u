<template>
  <div class="cadastro-page">
    <header class="top-bar">
      <span>Carteirinha4u</span>
    </header>

    <div class="cadastro-container">
      <div class="card">
        <h2>Cadastro de {{ tipo === 'associado' ? 'associado' : 'instituição' }}</h2>

        <form @submit.prevent="fazerCadastro">
          
          <div class="form-group">
            <input type="text" v-model="form.nome" placeholder="Nome" required>
          </div>

          <div class="form-group">
            <input 
              type="text" 
              v-model="form.cpf" 
              :placeholder="tipo === 'associado' ? 'CPF' : 'CNPJ'" 
              required
            >
          </div>

          <div class="form-group" v-if="tipo === 'associado'">
            <input 
              type="text" 
              onfocus="(this.type='date')" 
              onblur="(this.type='text')" 
              v-model="form.data_nascimento" 
              placeholder="Data de nascimento" 
              required
            >
          </div>

          <div class="form-group">
            <input type="email" v-model="form.email" placeholder="E-mail" required>
          </div>

          <div class="form-group">
            <input type="password" v-model="form.senha" placeholder="Senha" required>
          </div>

          <div class="upload-section">
            <input 
              type="file" 
              ref="fileInput" 
              @change="handleFileUpload" 
              hidden 
              accept="image/*"
            >
            
            <div class="upload-box" @click="$refs.fileInput.click()">
              <div v-if="previewUrl" class="preview-img" :style="{ backgroundImage: `url(${previewUrl})` }"></div>
              <span v-else class="upload-icon">☁️ <br> Foto</span>
            </div>
          </div>

          <button type="submit" class="btn-azul" :disabled="carregando">
            {{ carregando ? 'Cadastrando...' : 'Cadastrar-se' }}
          </button>

          <p v-if="mensagem" :class="{'error': erro, 'success': !erro}">{{ mensagem }}</p>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';

const route = useRoute();
const router = useRouter();
const tipo = ref('associado');

const form = reactive({
  nome: '',
  cpf: '',
  data_nascimento: '',
  email: '',
  senha: ''
});

const arquivoFoto = ref(null);
const previewUrl = ref(null);
const carregando = ref(false);
const mensagem = ref('');
const erro = ref(false);

onMounted(() => {
  // Pega o tipo (associado ou instituicao) que veio da tela de login
  if (route.query.tipo) {
    tipo.value = route.query.tipo;
  }
});

const handleFileUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    arquivoFoto.value = file;
    // Cria uma URL temporária para mostrar a foto no quadrado
    previewUrl.value = URL.createObjectURL(file);
  }
};

const fazerCadastro = async () => {
  carregando.value = true;
  mensagem.value = '';
  erro.value = false;

  try {
    // Para enviar arquivos, precisamos usar FormData em vez de JSON simples
    const formData = new FormData();
    formData.append('tipo', tipo.value);
    formData.append('nome', form.nome);
    formData.append('cpf', form.cpf);
    formData.append('email', form.email);
    formData.append('senha', form.senha);
    
    if (tipo.value === 'associado') {
      formData.append('data_nascimento', form.data_nascimento);
    }

    if (arquivoFoto.value) {
      formData.append('foto', arquivoFoto.value);
    }

    await axios.post('http://127.0.0.1:5000/register', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });

    mensagem.value = 'Cadastro realizado! Redirecionando...';
    setTimeout(() => router.push('/'), 2000); // Volta para o login após 2s

  } catch (error) {
    erro.value = true;
    mensagem.value = error.response?.data?.message || 'Erro ao cadastrar.';
  } finally {
    carregando.value = false;
  }
};
</script>

<style scoped>
.cadastro-page {
  background-color: #0d1117;
  min-height: 100vh;
  color: white;
  display: flex;
  flex-direction: column;
}

.top-bar {
  padding: 1rem 2rem;
  border-bottom: 1px solid #30363d;
  font-weight: bold;
  font-size: 1.2rem;
}

.cadastro-container {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
}

.card {
  background: #21262d; /* Um pouco mais claro que o fundo */
  padding: 2.5rem;
  border-radius: 8px;
  width: 100%;
  max-width: 400px;
}

h2 {
  text-align: center;
  margin-bottom: 2rem;
  font-size: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

input {
  width: 100%;
  padding: 12px;
  background-color: #0d1117; /* Input escuro */
  border: 1px solid #30363d; /* Borda sutil */
  border-radius: 20px; /* Borda bem arredondada como na imagem */
  color: #c9d1d9;
  box-sizing: border-box;
}

input:focus {
  outline: none;
  border-color: #58a6ff;
}

/* Upload Box Quadrado */
.upload-section {
  margin: 1.5rem 0;
}

.upload-box {
  width: 80px;
  height: 80px;
  background-color: #0d1117;
  border: 1px dashed #30363d;
  border-radius: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  overflow: hidden;
  transition: border 0.3s;
}

.upload-box:hover {
  border-color: #58a6ff;
}

.upload-icon {
  text-align: center;
  font-size: 0.8rem;
  color: #8b949e;
}

.preview-img {
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
}

.btn-azul {
  width: 100%;
  padding: 12px;
  background-color: #2f81f7;
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: bold;
  cursor: pointer;
  margin-top: 1rem;
}

.btn-azul:hover {
  background-color: #236bd8;
}

.error { color: #ff7b72; text-align: center; margin-top: 1rem; }
.success { color: #3fb950; text-align: center; margin-top: 1rem; }
</style>