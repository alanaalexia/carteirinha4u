<template>
  <div class="page-container">
    <header>
      <div class="logo">Carteirinha4u</div>
      <nav>
        <span class="active">Carteirinha</span>
        <span>Benefícios</span>
      </nav>
      <div class="user-actions">
        <button class="icon-btn">🔔</button>
        <div class="avatar-mini" v-if="usuario && usuario.dados.foto_url" :style="{ backgroundImage: `url(${usuario.dados.foto_url})` }"></div>
        <button class="btn-logout" @click="fazerLogout">Sair</button>
      </div>
    </header>

    <main>
      <div class="card-container">
        
        <div class="id-card">
          <div class="card-content">
            
            <div class="photo-section">
              <div class="photo-frame">
                <img 
                  v-if="usuario && usuario.dados.foto_url" 
                  :src="usuario.dados.foto_url" 
                  alt="Foto do Associado"
                >
                <div v-else class="placeholder-img">👤</div>
              </div>
            </div>

            <div class="info-section">
              <div class="info-row">
                <span class="label">Nome:</span>
                <span class="value">{{ usuario?.dados.nome }}</span>
              </div>
              
              <div class="info-row">
                <span class="label">Data de nascimento:</span>
                <span class="value">{{ formatarData(usuario?.dados.data_nascimento) }}</span>
              </div>

              <div class="info-row">
                <span class="label">CPF:</span>
                <span class="value">{{ usuario?.dados.cpf }}</span>
              </div>

              <div class="info-row">
                <span class="label">Instituição:</span>
                <span class="value">FACAMP - Faculdades de Campinas</span> </div>

              <div class="info-row">
                <span class="label">Associação:</span>
                <span class="value">DCE FACAMP</span>
              </div>

              <div class="info-row">
                <span class="label">Validade:</span>
                <span class="value">{{ dataValidade }}</span>
              </div>
            </div>
          </div>

          <div class="card-footer"></div>
        </div>

      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const usuario = ref(null);

onMounted(() => {
  const dadosSalvos = localStorage.getItem('usuario_logado');
  if (dadosSalvos) {
    usuario.value = JSON.parse(dadosSalvos);
    
    // Segurança: Se for instituição tentando acessar aqui, chuta pro dashboard certo
    if (usuario.value.tipo === 'instituicao') {
      router.push('/dashboard');
    }
  } else {
    router.push('/');
  }
});

// Função para deixar a data bonita (DD/MM/AAAA)
const formatarData = (dataString) => {
  if (!dataString) return '--/--/----';
  // Se vier no formato YYYY-MM-DD do input date
  const partes = dataString.split('-');
  if (partes.length === 3) return `${partes[2]}/${partes[1]}/${partes[0]}`;
  return dataString;
};

// Calcula validade (Hoje + 1 ano) para preencher o visual
const dataValidade = computed(() => {
  const hoje = new Date();
  hoje.setFullYear(hoje.getFullYear() + 1);
  return hoje.toLocaleDateString('pt-BR');
});

const fazerLogout = () => {
  localStorage.removeItem('usuario_logado');
  router.push('/');
};
</script>

<style scoped>
.page-container {
  background-color: #0d1117; /* Fundo bem escuro */
  min-height: 100vh;
  color: white;
  font-family: 'Arial', sans-serif;
  display: flex;
  flex-direction: column;
}

/* Header */
header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: #0d1117; /* Fundo igual ao corpo */
  border-bottom: 1px solid #30363d;
}

.logo { font-weight: bold; font-size: 1.3rem; }
nav span { margin: 0 15px; cursor: pointer; color: #8b949e; }
nav span.active { color: white; font-weight: bold; }

.user-actions { display: flex; align-items: center; gap: 15px; }
.icon-btn { background: none; border: none; font-size: 1.2rem; cursor: pointer; }
.btn-logout { background: transparent; border: 1px solid #30363d; color: #c9d1d9; padding: 5px 10px; border-radius: 4px; cursor: pointer; }
.avatar-mini { width: 30px; height: 30px; border-radius: 50%; background-size: cover; background-position: center; border: 1px solid #58a6ff; }

/* Main Area */
main {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center; /* Centraliza o cartão na tela */
}

/* O Cartão */
.id-card {
  background-color: #21262d; /* Cinza azulado do cartão */
  width: 600px;
  border-radius: 12px;
  overflow: hidden; /* Para cortar o footer azul arredondado */
  box-shadow: 0 20px 40px rgba(0,0,0,0.6);
}

.card-content {
  display: flex;
  padding: 30px;
  gap: 30px;
}

/* Foto */
.photo-section {
  flex-shrink: 0;
}

.photo-frame {
  width: 140px;
  height: 160px;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
}

.photo-frame img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.placeholder-img { font-size: 4rem; color: #ccc; }

/* Informações */
.info-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  font-size: 0.95rem;
  color: #c9d1d9;
  line-height: 1.8;
}

.info-row {
  display: flex;
  gap: 8px;
}

.label { color: #8b949e; font-weight: normal; }
.value { color: #ffffff; font-weight: 500; }

/* Faixa Azul */
.card-footer {
  height: 70px; /* Altura da faixa azul */
  background-color: #2f81f7; /* Azul igual da imagem */
  width: 100%;
}
</style>