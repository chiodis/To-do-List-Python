document.addEventListener('DOMContentLoaded', () => {
    const apiUrl = 'http://127.0.0.1:8000/tasks'; // Exemplo
    // Substitua com o endpoint correto da sua API

    const taskForm = document.getElementById('task-form');
    const taskList = document.getElementById('task-list');
    const newTaskInput = document.getElementById('new-task');

    // Função para buscar e listar todas as tarefas
    function fetchTasks() {
        fetch(apiUrl, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(tasks => {
            taskList.innerHTML = ''; // Limpar a lista antes de adicionar as tarefas
            tasks.forEach(task => addTaskToList(task));
        })
        .catch(error => console.error('Erro ao buscar tarefas:', error));
    }

    // Função para adicionar uma nova tarefa à API
    function addTask(taskContent) {
        fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title: taskContent })  // Envia a nova tarefa para o FastAPI
        })
        .then(response => response.json())
        .then(task => addTaskToList(task))
        .catch(error => console.error('Erro ao adicionar tarefa:', error));
    }

    // Função para marcar uma tarefa como completa (ou atualizar status)
    function completeTask(taskId) {
        fetch(`${apiUrl}/${taskId}`, {
            method: 'PUT',  // Utilizando PUT para atualização de status
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status: 'completa' })
            // Atualizando status para 'completa'
        })
        .then(() => {
            const taskItem = document.getElementById(taskId);
            taskItem.classList.add('complete');
        })
        .catch(error => console.error('Erro ao completar tarefa:', error));
    }

    // Função para remover uma tarefa da API
    function removeTask(taskId) {
        fetch(`${apiUrl}/${taskId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(() => {
            const taskItem = document.getElementById(taskId);
            taskItem.remove();
        })
        .catch(error => console.error('Erro ao remover tarefa:', error));
    }

    // Função para adicionar uma tarefa ao DOM
    function addTaskToList(task) {
        const li = document.createElement('li');
        li.id = task.id;
        li.innerHTML = `
            ${task.title}
            <div>
                <button onclick="completeTask('${task.id}')">Completar</button>
                <button onclick="removeTask('${task.id}')">Remover</button>
            </div>
        `;
        taskList.appendChild(li);
    }

    // Evento de submit do formulário de nova tarefa
    taskForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const taskContent = newTaskInput.value;
        if (taskContent) {
            addTask(taskContent);
            newTaskInput.value = '';  // Limpa o campo após adicionar
        }
    });

    // Carregar todas as tarefas ao iniciar a página
    fetchTasks();
});
