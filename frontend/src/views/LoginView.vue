<template>
  <div class="login-container">
    <div class="card">
      <h1>Carteirinha4u</h1>

      <div class="toggle-container">
        <button 
          :class="['toggle-btn', { active: tipoLogin === 'associado' }]" 
          @click="tipoLogin = 'associado'"
        >
          Associado
        </button>
        <button 
          :class="['toggle-btn', { active: tipoLogin === 'instituicao' }]" 
          @click="tipoLogin = 'instituicao'"
        >
          Instituição
        </button>
      </div>

      <form @submit.prevent="fazerLogin">
        <div class="form-group">
          <label for="email">E-mail</label>
          <input 
            type="email" 
            id="email" 
            v-model="email" 
            placeholder="exemplo@email.com" 
            required
          >
        </div>

        <div class="form-group">
          <label for="senha">Senha</label>
          <input 
            type="password" 
            id="senha" 
            v-model="senha" 
            placeholder="••••••••" 
            required
          >
        </div>

        <button type="submit" class="btn-login" :disabled="carregando">
          {{ carregando ? 'Entrando...' : 'Log-in' }}
        </button>

        <p v-if="erro" class="error">{{ erro }}</p>

        <div class="footer-link">
          <router-link 
  :to="{ path: '/cadastro', query: { tipo: tipoLogin } }"
>
  Não possui cadastro? Cadastre-se aqui.
</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const router = useRouter();

// Estado
const email = ref('');
const senha = ref('');
const erro = ref('');
const carregando = ref(false);
const tipoLogin = ref('instituicao'); // Começa selecionado em Instituição (como na imagem)

const fazerLogin = async () => {
  carregando.value = true;
  erro.value = '';

  try {
    const resposta = await axios.post('http://127.0.0.1:5000/login', {
      email: email.value,
      senha: senha.value,
      tipo: tipoLogin.value // Envia qual botão está selecionado
    });

    localStorage.setItem('usuario_logado', JSON.stringify(resposta.data));
    
    // Redireciona dependendo de quem logou (podemos mudar isso no futuro)
    if (tipoLogin.value === 'instituicao') {
        router.push('/dashboard');
    } else {
        
        router.push('/minha-carteirinha');
    }

  } catch (error) {
    if (error.response) {
      erro.value = error.response.data.message;
    } else {
      erro.value = 'Erro de conexão com o servidor';
    }
  } finally {
    carregando.value = false;
  }
};
</script>

<style scoped>
/* Fundo Geral Escuro */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #0d1117; /* Cor de fundo bem escura */
  color: white;
  font-family: 'Arial', sans-serif;
}

/* O Cartão Central */
.card {
  background: #252932; /* Cinza azulado escuro */
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.5);
  width: 100%;
  max-width: 380px;
  text-align: center;
}

h1 {
  margin-bottom: 1.5rem;
  font-weight: 500;
  color: #ffffff;
}

/* Container dos Botões Toggle */
.toggle-container {
  display: flex;
  background-color: #161b22; /* Fundo dos botões desativados */
  border-radius: 8px;
  padding: 4px;
  margin-bottom: 1.5rem;
  border: 1px solid #3d4450;
}

.toggle-btn {
  flex: 1; /* Ocupam espaço igual */
  background: transparent;
  color: #8b949e;
  border: none;
  padding: 8px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

/* Estado Ativo do Botão (BRANCO) */
.toggle-btn.active {
  background-color: white;
  color: #0d1117;
}

/* Inputs */
.form-group {
  margin-bottom: 1rem;
  text-align: left;
}

label {
  display: none; /* Escondi as labels para ficar igual a imagem (só placeholder) ou pode manter se preferir */
}

input {
  width: 100%;
  padding: 12px;
  background-color: #0d1117;
  border: 1px solid #30363d;
  border-radius: 6px;
  color: white;
  font-size: 0.9rem;
  box-sizing: border-box;
}

input:focus {
  outline: none;
  border-color: #2f81f7; /* Azul ao clicar */
}

/* Botão de Login (AZUL) */
.btn-login {
  width: 100%;
  padding: 12px;
  background-color: #2f81f7; /* Azul bonito */
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  margin-top: 1rem;
  transition: background 0.2s;
}

.btn-login:hover {
  background-color: #236bd8;
}

.footer-link {
  margin-top: 1.5rem;
  font-size: 0.8rem;
  color: #8b949e;
}

.footer-link a {
  color: #8b949e;
  text-decoration: none;
}

.footer-link a:hover {
  text-decoration: underline;
}

.error {
  color: #ff7b72;
  margin-top: 10px;
  font-size: 0.9rem;
}
</style>