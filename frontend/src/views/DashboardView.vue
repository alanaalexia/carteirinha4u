<template>
  <div class="dashboard-container">
    <header>
      <div class="logo">Carteirinha4u</div>
      <div class="user-actions">
        <div v-if="usuario" class="welcome-msg">
          Olá, {{ usuario.nome }}
        </div>
        <button class="btn-logout" @click="fazerLogout">Sair</button>
      </div>
    </header>

    <main>
      <div class="toolbar">
        <div class="search-box">
          <input type="text" v-model="termoBusca" placeholder="🔍 Buscar por nome ou CPF...">
        </div>
        <div class="actions-right">
          <input type="file" ref="fileInput" @change="processarPlanilha" hidden accept=".csv, .xlsx, .xls" />
          <button class="btn-outline" @click="$refs.fileInput.click()">
            📂 Atualizar com Planilha
          </button>
        </div>
      </div>

      <div v-if="idsParaInativar.length > 0" class="alert-bar">
        <p>⚠️ <strong>{{ idsParaInativar.length }}</strong> associados não estão na planilha e ficarão <strong>INATIVOS</strong>.</p>
        <div class="alert-actions">
          <button @click="aplicarInativacao" class="btn-danger">Aplicar</button>
          <button @click="cancelarComparacao" class="btn-secondary">Cancelar</button>
        </div>
      </div>

      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th style="width: 20%;">CPF</th>
              <th style="width: 30%;">NOME</th>
              <th style="width: 30%;">E-MAIL</th>
              <th style="width: 10%; text-align: center;">STATUS</th>
              <th style="width: 10%; text-align: center;">AÇÕES</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="usuariosFiltrados.length === 0">
              <td colspan="5" class="empty-state">Nenhum associado encontrado.</td>
            </tr>

            <tr 
              v-for="user in usuariosFiltrados" 
              :key="user._id"
              :class="{ 
                'row-inactive': user.status === 'inativo',
                'row-pending-inactive': idsParaInativar.includes(user._id) 
              }"
            >
              <template v-if="editandoId !== user._id">
                <td>{{ user.dados.cpf }}</td>
                <td>{{ user.dados.nome || user.dados.nome_fantasia }}</td>
                <td>{{ user.email }}</td>
                <td style="text-align: center;">
                  <span :class="['badge', user.status === 'inativo' ? 'bg-red' : 'bg-green']">
                    {{ user.status === 'inativo' ? 'Inativo' : 'Ativo' }}
                  </span>
                </td>
                <td style="text-align: center;">
                  <button class="icon-btn" @click="iniciarEdicao(user)" title="Editar">✏️</button>
                  <button class="icon-btn delete" @click="deletarUsuario(user._id)" title="Excluir">🗑️</button>
                </td>
              </template>

              <template v-else>
                <td><input v-model="editForm.dados.cpf" class="input-edit"></td>
                <td><input v-model="editForm.dados.nome" class="input-edit"></td>
                <td><input v-model="editForm.email" class="input-edit"></td>
                <td style="text-align: center;">
                   <select v-model="editForm.status" class="input-edit">
                     <option value="ativo">Ativo</option>
                     <option value="inativo">Inativo</option>
                   </select>
                </td>
                <td style="text-align: center;">
                  <button class="icon-btn save" @click="salvarEdicao(user._id)">💾</button>
                  <button class="icon-btn cancel" @click="cancelarEdicao">❌</button>
                </td>
              </template>
            </tr>
          </tbody>
        </table>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const router = useRouter();
const usuarios = ref([]);
const usuario = ref(null); // Usuário logado (Instituição)
const termoBusca = ref('');
const idsParaInativar = ref([]);
const editandoId = ref(null);
const editForm = reactive({});

const carregarAssociados = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:5000/associados');
    usuarios.value = res.data;
  } catch (error) {
    console.error("Erro ao buscar", error);
  }
};

onMounted(() => {
  // Recupera quem está logado
  const dadosSalvos = localStorage.getItem('usuario_logado');
  if (dadosSalvos) {
    usuario.value = JSON.parse(dadosSalvos);
  } else {
    router.push('/');
  }
  carregarAssociados();
});

const usuariosFiltrados = computed(() => {
  if (!termoBusca.value) return usuarios.value;
  return usuarios.value.filter(u => {
    const nome = u.dados?.nome?.toLowerCase() || '';
    const cpf = u.dados?.cpf || '';
    return nome.includes(termoBusca.value.toLowerCase()) || cpf.includes(termoBusca.value);
  });
});

const iniciarEdicao = (user) => {
  editandoId.value = user._id;
  Object.assign(editForm, JSON.parse(JSON.stringify(user)));
};

const cancelarEdicao = () => {
  editandoId.value = null;
};

const salvarEdicao = async (id) => {
  try {
    await axios.put(`http://127.0.0.1:5000/associados/${id}`, editForm);
    editandoId.value = null;
    carregarAssociados();
  } catch (error) {
    alert("Erro ao salvar edição");
  }
};

const deletarUsuario = async (id) => {
  if(confirm("Tem certeza que deseja apagar permanentemente?")) {
    await axios.delete(`http://127.0.0.1:5000/associados/${id}`);
    carregarAssociados();
  }
}

const processarPlanilha = async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  const formData = new FormData();
  formData.append('arquivo', file);

  try {
    const res = await axios.post('http://127.0.0.1:5000/comparar-planilha', formData);
    idsParaInativar.value = res.data.ids_para_inativar;
    if (idsParaInativar.value.length === 0) alert("Todos os CPFs foram encontrados!");
  } catch (error) {
    alert("Erro ao ler planilha. Verifique se existe a coluna 'CPF'.");
  }
};

const aplicarInativacao = async () => {
  await axios.post('http://127.0.0.1:5000/inativar-em-massa', { ids: idsParaInativar.value });
  idsParaInativar.value = [];
  carregarAssociados();
};

const cancelarComparacao = () => {
  idsParaInativar.value = [];
};

const fazerLogout = () => {
  localStorage.removeItem('usuario_logado');
  router.push('/');
};
</script>

<style scoped>
.dashboard-container {
  width: 100%; /* Garante largura total */
  min-height: 100vh;
  background-color: #0d1117;
  color: #c9d1d9;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: #161b22; /* Levemente mais claro que o fundo */
  border-bottom: 1px solid #30363d;
}

.logo { font-weight: bold; font-size: 1.3rem; color: white; letter-spacing: -0.5px; }

.user-actions { display: flex; align-items: center; gap: 1rem; }
.welcome-msg { font-size: 0.9rem; color: #8b949e; }

.btn-logout {
  background: transparent; border: 1px solid #30363d; color: #ff7b72; 
  padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 0.9rem; transition: 0.2s;
}
.btn-logout:hover { background: rgba(255, 123, 114, 0.1); }

main { padding: 2rem; max-width: 1400px; margin: 0 auto; /* Centraliza em telas gigantes */ }

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.search-box input {
  background: #0d1117; border: 1px solid #30363d; color: white;
  padding: 10px 15px; border-radius: 6px; width: 350px; font-size: 0.95rem;
}
.search-box input:focus { outline: none; border-color: #58a6ff; }

.btn-outline {
  background: #238636; /* Verde GitHub */
  border: none; color: white;
  padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: 600;
  display: flex; align-items: center; gap: 8px;
}
.btn-outline:hover { background: #2ea043; }

/* Alerta */
.alert-bar {
  background: #240807; border: 1px solid #ff7b72; color: #ff7b72;
  padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;
  display: flex; justify-content: space-between; align-items: center;
}
.btn-danger { background: #d73a49; color: white; border: none; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-weight: bold;}

/* Tabela */
.table-container {
  border: 1px solid #30363d;
  border-radius: 6px;
  overflow: hidden; /* Arredonda os cantos da tabela */
}

table { 
  width: 100%; 
  border-collapse: collapse; 
  background-color: #0d1117;
}

th { 
  background: #161b22; 
  padding: 16px; 
  font-size: 0.85rem; 
  color: #8b949e; 
  font-weight: 600; 
  border-bottom: 1px solid #30363d;
  text-transform: uppercase;
}

td { 
  padding: 16px; 
  border-bottom: 1px solid #21262d; 
  font-size: 0.95rem;
  color: #c9d1d9;
}

tr:last-child td { border-bottom: none; }
tr:hover { background-color: #161b22; } /* Efeito hover na linha */

.empty-state { text-align: center; color: #8b949e; padding: 3rem; }

/* Status Badges */
.badge { padding: 4px 10px; border-radius: 2rem; font-size: 0.75rem; font-weight: 600; border: 1px solid transparent; }
.bg-green { background: rgba(56, 139, 253, 0.15); color: #58a6ff; border-color: rgba(56, 139, 253, 0.4); }
.bg-red { background: rgba(255, 123, 114, 0.15); color: #ff7b72; border-color: rgba(255, 123, 114, 0.4); }

/* Botões de Ação */
.icon-btn { 
  background: transparent; border: none; cursor: pointer; 
  font-size: 1.1rem; padding: 6px; border-radius: 4px; transition: 0.2s; opacity: 0.8;
}
.icon-btn:hover { opacity: 1; background: rgba(255,255,255,0.1); }
.icon-btn.delete:hover { background: rgba(255, 123, 114, 0.2); }

/* Input Edição */
.input-edit {
  background: #0d1117; border: 1px solid #30363d; color: white;
  padding: 8px; border-radius: 4px; width: 90%;
}
</style>